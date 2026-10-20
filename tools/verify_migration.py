"""Verify migrated file bytes without importing or executing corpus artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import stat
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


def _manifest(root: Path) -> dict[str, Any]:
    """Reject ambiguous provenance before reading any declared input."""
    path = root / "MIGRATION.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
        raise ValueError("migration manifest must be a bounded regular file")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate migration JSON key")
            result[key] = value
        return result

    def finite(_: str) -> Any:
        raise ValueError("non-finite migration JSON value")

    manifest = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=finite)
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


def verify(root: Path = ROOT) -> dict[str, Any]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("migration root must be a real directory")
    manifest = _manifest(root)
    total = 0
    for entry in manifest["files"]:
        name = entry["path"]
        relative = PurePosixPath(name)
        path = root
        for part in relative.parts:
            path /= part
            if path.is_symlink():
                raise ValueError(f"migration path is a symlink: {name}")
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError(f"migration path is not a regular file: {name}")
        if path.stat().st_size != entry["bytes"]:
            raise ValueError(f"migrated bytes or mode changed: {name}")
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        executable = bool(path.stat().st_mode & 0o111)
        if (
            len(data) != entry["bytes"]
            or hashlib.sha256(data).hexdigest() != entry["sha256"]
            or blob != entry["git_blob"]
            or executable != (entry["mode"] == "100755")
        ):
            raise ValueError(f"migrated bytes or mode changed: {name}")
        total += len(data)
    return {
        "files": len(manifest["files"]),
        "bytes": total,
        "source_commit": manifest["source_commit"],
        "verification": "file identity only; no benchmark executed",
    }


def main() -> None:
    print(json.dumps(verify(), sort_keys=True))


if __name__ == "__main__":
    main()
