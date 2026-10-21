"""Bind a published results directory to its bytes, and check Sigstore signatures over that binding.

``python -m tools.attest digest RESULTS_DIR`` writes ``attestations/<slug>.json``: the SHA-256 of
every file in the directory, and nothing else (no time, no machine), so it can be re-made byte for
byte. The ``Attest results`` workflow (``.github/workflows/attest.yml``) signs that file with
cosign's keyless flow, through GitHub's OIDC token, into ``attestations/<slug>.sigstore.json``: a
Sigstore bundle holding the signature, a short-lived Fulcio certificate naming the workflow that
signed and the Rekor transparency-log entry. The maintainer commits both files from the workflow's
artifact.

``python -m tools.attest verify`` checks every attestation:

* the results directory holds exactly the files the digest manifest lists, with those digests (a
  file added, removed or changed after signing fails, whether or not a signature exists);
* a bundle, when present, verifies with ``cosign verify-blob`` against the manifest's bytes, issued
  to ``--identity`` (by default the ``attest.yml`` workflow on ``main`` of this repository) by
  ``--issuer`` (GitHub Actions' OIDC issuer). A bundle that cannot be checked because cosign is not
  installed fails: an unverifiable signature is never reported as a good one.

``--require-signatures`` also fails an attestation without a bundle. Without it an unsigned
manifest still binds the files it lists, as ``MIGRATION.json`` binds the migrated ones, and the
output says it is unsigned. Paths come from the repository: the subject must be a directory under
``benchmarks/`` and no symlink is followed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ATTESTATIONS = "attestations"
SCHEMA = 1
DEFAULT_IDENTITY = (
    r"^https://github\.com/aisecnomad/Nexus-ShadowBench/\.github/workflows/attest\.yml@refs/heads/main$"
)
DEFAULT_ISSUER = "https://token.actions.githubusercontent.com"
_SLUG = re.compile(r"[A-Za-z0-9._-]+")


class AttestationError(ValueError):
    """A results directory that does not match its attestation, or an attestation that is malformed."""


def slug(subject: str) -> str:
    """The attestation file stem for a repository-relative results directory."""
    stem = subject.strip("/").replace("/", "__")
    if not _SLUG.fullmatch(stem):
        raise AttestationError(f"cannot name an attestation for {subject!r}")
    return stem


def _subject_dir(root: Path, subject: str) -> Path:
    parts = Path(subject).parts
    if (
        not parts
        or parts[0] != "benchmarks"
        or any(p in ("..", ".") for p in parts)
        or Path(subject).is_absolute()
    ):
        raise AttestationError(f"subject {subject!r} must be a relative directory under benchmarks/")
    path = root / subject
    for parent in [path, *path.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise AttestationError(f"subject {subject!r} passes through a symlink at {parent}")
    if not path.is_dir():
        raise AttestationError(f"subject {subject!r} is not a directory")
    return path


def digests(directory: Path) -> dict[str, str]:
    """SHA-256 of every regular file under ``directory``, by POSIX relative path; refuses links."""
    out: dict[str, str] = {}
    for top, dirs, files in os.walk(directory):
        for name in sorted(dirs + files):
            path = Path(top, name)
            if path.is_symlink():
                raise AttestationError(f"{path} is a symlink; results directories hold regular files only")
        for name in files:
            path = Path(top, name)
            if not path.is_file():
                raise AttestationError(f"{path} is not a regular file")
            out[path.relative_to(directory).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return dict(sorted(out.items()))


def manifest(root: Path, subject: str) -> dict[str, Any]:
    return {"schema": SCHEMA, "subject": subject, "files": digests(_subject_dir(root, subject))}


def render(document: dict[str, Any]) -> bytes:
    """The canonical bytes of a digest manifest: what is signed and what is committed."""
    return (json.dumps(document, indent=1, sort_keys=True) + "\n").encode()


def write_digest(root: Path, subject: str) -> Path:
    path = root / ATTESTATIONS / f"{slug(subject)}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(render(manifest(root, subject)))
    return path


def _load(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise AttestationError(f"{path.name}: unreadable: {exc}") from exc
    if not isinstance(document, dict) or set(document) != {"schema", "subject", "files"}:
        raise AttestationError(f"{path.name}: expected exactly schema, subject and files")
    if document["schema"] != SCHEMA or not isinstance(document["subject"], str):
        raise AttestationError(f"{path.name}: unsupported schema or subject")
    if not isinstance(document["files"], dict) or not document["files"]:
        raise AttestationError(f"{path.name}: files must be a non-empty object")
    if path.read_bytes() != render(document):
        raise AttestationError(f"{path.name}: not in canonical form, so its bytes are not what was signed")
    if path.stem != slug(document["subject"]):
        raise AttestationError(f"{path.name}: names subject {document['subject']!r}, which is another file's")
    return document


def check_files(root: Path, document: dict[str, Any]) -> list[str]:
    """How the subject directory differs from the digests its manifest recorded."""
    try:
        now = digests(_subject_dir(root, document["subject"]))
    except AttestationError as exc:
        return [str(exc)]
    recorded: dict[str, str] = document["files"]
    problems = [f"{name}: missing" for name in sorted(set(recorded) - set(now))]
    problems += [f"{name}: not in the attestation" for name in sorted(set(now) - set(recorded))]
    problems += [
        f"{name}: changed" for name in sorted(set(now) & set(recorded)) if now[name] != recorded[name]
    ]
    return problems


def cosign_verify(blob: Path, bundle: Path, identity: str, issuer: str) -> str | None:
    """Why ``bundle`` does not verify ``blob`` (None when it does), with ``cosign verify-blob``."""
    cosign = shutil.which("cosign")
    if cosign is None:
        return "cosign is not installed, so the signature cannot be checked"
    command = [
        cosign,
        "verify-blob",
        "--bundle",
        str(bundle),
        "--certificate-identity-regexp",
        identity,
        "--certificate-oidc-issuer",
        issuer,
        str(blob),
    ]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=300, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"cosign failed to run: {exc}"
    if done.returncode != 0:
        return f"cosign verify-blob failed: {(done.stderr or done.stdout).strip()[-400:]}"
    return None


def verify(
    root: Path = ROOT,
    *,
    require_signatures: bool = False,
    identity: str = DEFAULT_IDENTITY,
    issuer: str = DEFAULT_ISSUER,
) -> tuple[dict[str, Any], list[str]]:
    """A summary of every attestation under ``root/attestations`` and every problem found."""
    directory = root / ATTESTATIONS
    summary: dict[str, Any] = {"attestations": 0, "signed": 0, "unsigned": []}
    problems: list[str] = []
    if not directory.is_dir():
        return summary, problems
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".sigstore.json"):
            continue
        summary["attestations"] += 1
        try:
            document = _load(path)
        except AttestationError as exc:
            problems.append(str(exc))
            continue
        problems += [f"{document['subject']}: {p}" for p in check_files(root, document)]
        bundle = path.with_name(f"{path.stem}.sigstore.json")
        if bundle.is_file():
            problem = cosign_verify(path, bundle, identity, issuer)
            if problem:
                problems.append(f"{path.name}: {problem}")
            else:
                summary["signed"] += 1
        else:
            summary["unsigned"].append(document["subject"])
            if require_signatures:
                problems.append(f"{path.name}: no Sigstore bundle ({bundle.name})")
    for bundle in sorted(directory.glob("*.sigstore.json")):
        if not bundle.with_name(bundle.name.removesuffix(".sigstore.json") + ".json").is_file():
            problems.append(f"{bundle.name}: a bundle without its digest manifest")
    return summary, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("digest", help="write attestations/<slug>.json for a results directory")
    p.add_argument("subject", help="repository-relative results directory under benchmarks/")
    p = sub.add_parser("verify", help="check every attestation's files and signature")
    p.add_argument("--require-signatures", action="store_true")
    p.add_argument("--identity", default=DEFAULT_IDENTITY, help="certificate identity regular expression")
    p.add_argument("--issuer", default=DEFAULT_ISSUER, help="certificate OIDC issuer")
    args = ap.parse_args(argv)
    try:
        if args.command == "digest":
            path = write_digest(ROOT, args.subject.rstrip("/"))
            print(path.relative_to(ROOT).as_posix())
            return 0
    except AttestationError as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    summary, problems = verify(
        ROOT, require_signatures=args.require_signatures, identity=args.identity, issuer=args.issuer
    )
    for problem in problems:
        print(problem, file=sys.stderr)
    print(json.dumps(summary))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
