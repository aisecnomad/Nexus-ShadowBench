"""Verify migrated file bytes without importing or executing corpus artifacts.

Every imported file must keep the bytes, mode and Git blob that MIGRATION.json
records. Harness code, tests and the copied CI and build dependency locks may
change only through AMENDMENTS.json, an append-only ledger in which each entry
names a migrated file, the SHA-256 it changes from (the migrated bytes or the
previous entry for that file), the bytes it changes to, a reason and a
reference. Evidence never changes: corpora, labels, freezes, recorded
predictions, results, the original runtime lock kept for provenance and the
code that generates cases, labels ground truth or defines the taxonomies are
not amendable.

``python -m tools.verify_migration`` verifies; ``python -m tools.verify_migration
--amend PATH --reason TEXT --reference URL`` appends an entry for a changed file.

Two checks anchor the records themselves, which the default check takes as
given. ``--source DIR`` requires every manifest entry to name the Git blob and
mode its source path has in the source commit of the ShadowScan checkout at
DIR, so an entry cannot be rewritten to match changed bytes. ``--since REF``
requires MIGRATION.json to be byte-identical to its copy at REF and the ledger
at REF to be a prefix of the current one, so no file is unbound and no
recorded amendment is rewritten, reordered or dropped. CI passes both.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d"
_TOP_KEYS = {
    "companion_repository",
    "files",
    "note",
    "schema",
    "source_commit",
    "source_repository",
}
_ENTRY_KEYS = {"bytes", "disposition", "git_blob", "mode", "path", "sha256"}
_LEDGER_KEYS = {"amendments", "note", "schema"}
_AMENDMENT_KEYS = {"bytes", "from_sha256", "git_blob", "mode", "path", "reason", "reference", "sha256"}
# Harness code and tests of the live tracks, and the CI and build locks copied
# from ShadowScan, which must follow its security updates. The legacy harnesses
# under tools/benchmark and tools/benchmark_realworld hash their own sources
# into recorded freezes, and migration/requirements.source.lock records the
# original runtime lock, so they stay as migrated.
_AMENDABLE = re.compile(
    r"(?:tools/(?:shadowbench|discovery_benchmark)/[^/].*\.(?:py|sh)"
    r"|tests/[^/].*\.py"
    r"|requirements-(?:ci|build)\.lock)"
)
# Code whose output is evidence: the cases generator, its families and case
# model, the ground-truth labeler and the taxonomies the labels are written in.
_NEVER_AMENDABLE = re.compile(
    r"(?:.*/families/.*"
    r"|tools/shadowbench/cases/(?:generate|corpus|contract)\.py"
    r"|tools/shadowbench/estate/taxonomy\.py"
    r"|tools/discovery_benchmark/(?:evidence|taxonomy)\.py)"
)


def _path(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise ValueError("invalid migration path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or ".." in path.parts
        or ".git" in path.parts
        or path.as_posix() != value
    ):
        raise ValueError("migration path must be canonical and relative")
    return path


def _load_json(path: Path, what: str) -> Any:
    """Read bounded, strict JSON: no duplicate keys and no non-finite numbers."""
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError(f"{what} must be a bounded regular file")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate {what} JSON key")
            result[key] = value
        return result

    def finite(_: str) -> Any:
        raise ValueError(f"non-finite {what} JSON value")

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=finite)


def _manifest(root: Path) -> dict[str, Any]:
    """Reject ambiguous provenance before reading any declared input."""
    manifest = _load_json(root / "MIGRATION.json", "migration")
    if (
        not isinstance(manifest, dict)
        or set(manifest) != _TOP_KEYS
        or type(manifest["schema"]) is not int
        or manifest["schema"] != 1
        or manifest["source_commit"] != SOURCE_COMMIT
        or manifest["source_repository"] != "https://github.com/aisecnomad/Nexus-ShadowScan"
        or manifest["companion_repository"] != "https://github.com/aisecnomad/Nexus-ShadowBench"
        or not isinstance(manifest["note"], str)
        or not manifest["note"].strip()
        or not isinstance(manifest["files"], list)
        or not manifest["files"]
    ):
        raise ValueError("invalid migration schema or source identity")
    paths: set[str] = set()
    source_paths: set[str] = set()
    for entry in manifest["files"]:
        if not isinstance(entry, dict) or set(entry) not in (_ENTRY_KEYS, _ENTRY_KEYS | {"source_path"}):
            raise ValueError("invalid migration file schema")
        _path(entry["path"])
        source_path = _path(entry.get("source_path", entry["path"])).as_posix()
        if entry["path"] in paths or source_path in source_paths:
            raise ValueError("duplicate migration path or source path")
        paths.add(entry["path"])
        source_paths.add(source_path)
        if (
            type(entry["bytes"]) is not int
            or entry["bytes"] < 0
            or entry["mode"] not in ("100644", "100755")
            or entry["disposition"] not in ("moved", "copied-support", "copied-source-context")
            or not isinstance(entry["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None
            or not isinstance(entry["git_blob"], str)
            or re.fullmatch(r"[0-9a-f]{40}", entry["git_blob"]) is None
        ):
            raise ValueError("invalid migration size, mode, disposition or digest")
    return manifest


def amendable(path: str) -> bool:
    """Whether a migrated file is harness code, a test or a copied lock that AMENDMENTS.json may change."""
    return _AMENDABLE.fullmatch(path) is not None and _NEVER_AMENDABLE.fullmatch(path) is None


def _ledger(root: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """The identity each amended file must now have, after checking every chain of amendments.

    The ledger is optional. When present it must be well formed, every entry must
    change an amendable migrated file from exactly the bytes the previous record
    gives it, and no entry may leave a file as it was.
    """
    path = root / "AMENDMENTS.json"
    if not path.exists() and not path.is_symlink():
        return {}
    ledger = _load_json(path, "amendment")
    if (
        not isinstance(ledger, dict)
        or set(ledger) != _LEDGER_KEYS
        or type(ledger["schema"]) is not int
        or ledger["schema"] != 1
        or not isinstance(ledger["note"], str)
        or not ledger["note"].strip()
        or not isinstance(ledger["amendments"], list)
    ):
        raise ValueError("invalid amendment ledger schema")
    current = {entry["path"]: entry for entry in manifest["files"]}
    amended: dict[str, dict[str, Any]] = {}
    for entry in ledger["amendments"]:
        if not isinstance(entry, dict) or set(entry) != _AMENDMENT_KEYS:
            raise ValueError("invalid amendment entry schema")
        name = _path(entry["path"]).as_posix()
        if name not in current:
            raise ValueError(f"amendment names a file the migration does not record: {name}")
        if not amendable(name):
            raise ValueError(f"amendment changes evidence, which is never amendable: {name}")
        if (
            type(entry["bytes"]) is not int
            or entry["bytes"] < 0
            or entry["mode"] not in ("100644", "100755")
            or any(
                not isinstance(entry[key], str) or re.fullmatch(r"[0-9a-f]{64}", entry[key]) is None
                for key in ("from_sha256", "sha256")
            )
            or not isinstance(entry["git_blob"], str)
            or re.fullmatch(r"[0-9a-f]{40}", entry["git_blob"]) is None
            or not isinstance(entry["reason"], str)
            or not entry["reason"].strip()
            or not isinstance(entry["reference"], str)
            or not entry["reference"].strip()
        ):
            raise ValueError(f"invalid amendment size, mode, digest, reason or reference: {name}")
        if entry["from_sha256"] != current[name]["sha256"]:
            raise ValueError(f"amendment does not start from the recorded bytes: {name}")
        if entry["sha256"] == entry["from_sha256"]:
            raise ValueError(f"amendment leaves the file unchanged: {name}")
        current[name] = entry
        amended[name] = entry
    return amended


def _identity(path: Path) -> tuple[int, str, str, bool]:
    """Size, SHA-256, Git blob and executable bit of a regular file."""
    data = path.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    return len(data), hashlib.sha256(data).hexdigest(), blob, bool(path.stat().st_mode & 0o111)


def _regular(root: Path, name: str) -> Path:
    path = root
    for part in PurePosixPath(name).parts:
        path /= part
        if path.is_symlink():
            raise ValueError(f"migration path is a symlink: {name}")
    try:
        mode = path.stat().st_mode
    except FileNotFoundError:
        raise ValueError(f"migrated file is missing: {name}") from None
    if not stat.S_ISREG(mode):
        raise ValueError(f"migration path is not a regular file: {name}")
    return path


_REF = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/@^~-]*")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        timeout=120,
        check=False,
    )


def _revision(repo: Path, ref: str) -> None:
    if not _REF.fullmatch(ref):
        raise ValueError(f"not a plain Git revision: {ref!r}")
    if _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode != 0:
        raise ValueError(f"{ref} is not a commit in {repo}; fetch it first")


def committed(repo: Path, ref: str, name: str) -> bytes | None:
    """The bytes of ``name`` at ``ref`` in the Git repository at ``repo``; None when it has no such file."""
    _revision(repo, ref)
    done = _git(repo, "cat-file", "blob", f"{ref}:{_path(name).as_posix()}")
    return done.stdout if done.returncode == 0 else None


def committed_names(repo: Path, ref: str, directory: str) -> list[str]:
    """Every file path under ``directory`` at ``ref``, repository-relative."""
    _revision(repo, ref)
    where = _path(directory).as_posix()
    done = _git(repo, "ls-tree", "-r", "-z", "--name-only", "--full-tree", ref, "--", where)
    if done.returncode != 0:
        raise ValueError(f"cannot list {directory} at {ref}: {done.stderr.decode(errors='replace').strip()}")
    return sorted(name for name in done.stdout.decode().split("\0") if name)


def _source_tree(source: Path, commit: str) -> dict[str, tuple[str, str]]:
    """Mode and Git blob of every file in ``commit`` of the checkout at ``source``."""
    done = _git(source, "ls-tree", "-r", "-z", "--full-tree", commit)
    if done.returncode != 0:
        raise ValueError(f"the source checkout at {source} does not hold commit {commit}")
    tree: dict[str, tuple[str, str]] = {}
    for record in done.stdout.decode().split("\0"):
        if record:
            meta, name = record.split("\t", 1)
            mode, kind, blob = meta.split()
            if kind == "blob":
                tree[name] = (mode, blob)
    return tree


def check_source(manifest: dict[str, Any], tree: dict[str, tuple[str, str]]) -> None:
    """Every manifest entry must name the mode and Git blob its source path has in the source tree."""
    for entry in manifest["files"]:
        source_path = entry.get("source_path", entry["path"])
        if tree.get(source_path) != (entry["mode"], entry["git_blob"]):
            raise ValueError(f"migration record does not match the source commit: {entry['path']}")


def check_since(root: Path, ref: str) -> None:
    """MIGRATION.json must be unchanged since ``ref`` and the ledger at ``ref`` a prefix of today's."""
    if committed(root, ref, "MIGRATION.json") != (root / "MIGRATION.json").read_bytes():
        raise ValueError(f"MIGRATION.json changed since {ref}; the migration record never changes")
    before = committed(root, ref, "AMENDMENTS.json")
    if before is None:
        return
    path = root / "AMENDMENTS.json"
    if not path.is_file():
        raise ValueError(f"AMENDMENTS.json was removed since {ref}")
    # Today's ledger has passed _ledger; the one at ref is only compared with it.
    base = json.loads(before)
    now = _load_json(path, "amendment")
    if (
        not isinstance(base, dict)
        or not isinstance(base.get("amendments"), list)
        or {key: value for key, value in now.items() if key != "amendments"}
        != {key: value for key, value in base.items() if key != "amendments"}
        or now["amendments"][: len(base["amendments"])] != base["amendments"]
    ):
        raise ValueError(f"AMENDMENTS.json rewrote, reordered or dropped entries recorded at {ref}")


def verify(root: Path = ROOT, *, source: Path | None = None, since: str | None = None) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("migration root must be a real directory")
    manifest = _manifest(root)
    if source is not None:
        check_source(manifest, _source_tree(source, manifest["source_commit"]))
    amended = _ledger(root, manifest)
    if since is not None:
        check_since(root, since)
    total = 0
    for migrated in manifest["files"]:
        name = migrated["path"]
        entry = amended.get(name, migrated)
        path = _regular(root, name)
        if path.stat().st_size != entry["bytes"]:
            raise ValueError(f"migrated bytes or mode changed: {name}")
        size, sha256, blob, executable = _identity(path)
        if (
            size != entry["bytes"]
            or sha256 != entry["sha256"]
            or blob != entry["git_blob"]
            or executable != (entry["mode"] == "100755")
        ):
            if name in amended:
                raise ValueError(f"amended bytes or mode changed since the last amendment: {name}")
            raise ValueError(f"migrated bytes or mode changed: {name}")
        total += size
    return {
        "amended": len(amended),
        "files": len(manifest["files"]),
        "bytes": total,
        "source_commit": manifest["source_commit"],
        "source_tree_checked": source is not None,
        "since": since,
        "verification": "file identity only; no benchmark executed",
    }


def amend(name: str, reason: str, reference: str, root: Path = ROOT) -> dict[str, Any]:
    """Append an AMENDMENTS.json entry recording the current bytes of an amendable migrated file."""
    if not reason.strip() or not reference.strip():
        raise ValueError("an amendment needs a reason and a reference")
    manifest = _manifest(root)
    amended = _ledger(root, manifest)
    migrated = {entry["path"]: entry for entry in manifest["files"]}
    name = _path(name).as_posix()
    if name not in migrated:
        raise ValueError(f"not a migrated file: {name}")
    if not amendable(name):
        raise ValueError(f"evidence is never amendable: {name}")
    previous = amended.get(name, migrated[name])
    size, sha256, blob, executable = _identity(_regular(root, name))
    if sha256 == previous["sha256"]:
        raise ValueError(f"unchanged since its last recorded bytes: {name}")
    entry = {
        "bytes": size,
        "from_sha256": previous["sha256"],
        "git_blob": blob,
        "mode": "100755" if executable else "100644",
        "path": name,
        "reason": reason.strip(),
        "reference": reference.strip(),
        "sha256": sha256,
    }
    ledger_path = root / "AMENDMENTS.json"
    before = ledger_path.read_bytes() if amended or ledger_path.exists() else None
    if before is not None:
        ledger = _load_json(ledger_path, "amendment")
    else:
        ledger = {
            "schema": 1,
            "note": (
                "Append-only record of changes to migrated harness code and tests. "
                "Evidence is never amended; see tools/verify_migration.py."
            ),
            "amendments": [],
        }
    ledger["amendments"].append(entry)
    ledger_path.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        verify(root)
    except ValueError:
        # Another file fails verification: leave the ledger exactly as it was.
        if before is None:
            ledger_path.unlink()
        else:
            ledger_path.write_bytes(before)
        raise
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.verify_migration",
        description="Verify migrated files against MIGRATION.json and AMENDMENTS.json, or amend one.",
    )
    parser.add_argument("--amend", metavar="PATH", help="record the current bytes of a changed harness file")
    parser.add_argument("--reason", default="", help="why the file changed (with --amend)")
    parser.add_argument("--reference", default="", help="pull request or issue URL (with --amend)")
    parser.add_argument(
        "--source",
        metavar="DIR",
        type=Path,
        help="also check every record against the source commit in the ShadowScan checkout at DIR",
    )
    parser.add_argument(
        "--since",
        metavar="REF",
        help="also require MIGRATION.json unchanged and the ledger only appended to since REF",
    )
    args = parser.parse_args(argv)
    if args.amend:
        try:
            print(json.dumps(amend(args.amend, args.reason, args.reference), sort_keys=True))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0
    try:
        print(json.dumps(verify(source=args.source, since=args.since), sort_keys=True))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
