"""The imported evidence must retain the exact source bytes and file modes."""

from __future__ import annotations

import hashlib
import json

import pytest

from tools.verify_migration import SOURCE_COMMIT, verify


def _tree(tmp_path):
    data = b"untrusted fixture; read as bytes only\n"
    (tmp_path / "fixture.txt").write_bytes(data)
    entry = {
        "path": "fixture.txt",
        "source_path": "fixture.txt",
        "disposition": "moved",
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
        "mode": "100644",
    }
    (tmp_path / "MIGRATION.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "source_commit": SOURCE_COMMIT,
                "source_repository": "https://github.com/aisecnomad/Nexus-ShadowScan",
                "companion_repository": "https://github.com/aisecnomad/Nexus-ShadowBench",
                "note": "Synthetic validator regression input.",
                "files": [entry],
            }
        )
    )


def test_imported_source_bytes_match_the_migration_record():
    result = verify()
    assert result["files"] == 555
    assert result["source_commit"] == "0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d"


def test_changed_evidence_is_rejected(tmp_path):
    _tree(tmp_path)
    assert verify(tmp_path)["files"] == 1
    (tmp_path / "fixture.txt").write_bytes(b"replacement\n")
    with pytest.raises(ValueError, match="bytes or mode changed"):
        verify(tmp_path)


def test_evidence_symlink_is_rejected(tmp_path):
    _tree(tmp_path)
    (tmp_path / "fixture.txt").rename(tmp_path / "target")
    (tmp_path / "fixture.txt").symlink_to("target")
    with pytest.raises(ValueError, match="symlink"):
        verify(tmp_path)


@pytest.mark.parametrize(
    "path", ["", ".", "./fixture.txt", "a//b", "a/../fixture.txt", "/fixture.txt", "a\\b"]
)
def test_noncanonical_paths_cannot_alias_verified_files(tmp_path, path):
    _tree(tmp_path)
    manifest_path = tmp_path / "MIGRATION.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"].append({**manifest["files"][0], "path": path, "source_path": "other.txt"})
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="path"):
        verify(tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("mode", "100600"),
        ("mode", "120000"),
        ("bytes", True),
        ("bytes", -1),
        ("sha256", "0" * 63),
        ("git_blob", "g" * 40),
        ("disposition", "unknown"),
        ("source_path", "./fixture.txt"),
    ],
)
def test_invalid_file_metadata_is_rejected(tmp_path, field, value):
    _tree(tmp_path)
    manifest_path = tmp_path / "MIGRATION.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"][0][field] = value
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        verify(tmp_path)


def test_duplicate_source_identity_is_not_counted_twice(tmp_path):
    _tree(tmp_path)
    (tmp_path / "other.txt").write_bytes((tmp_path / "fixture.txt").read_bytes())
    manifest_path = tmp_path / "MIGRATION.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"].append({**manifest["files"][0], "path": "other.txt"})
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="source path"):
        verify(tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("schema", True),
        ("source_commit", "b" * 40),
        ("source_repository", "https://example.invalid"),
        ("files", []),
    ],
)
def test_wrong_source_or_schema_is_rejected(tmp_path, field, value):
    _tree(tmp_path)
    manifest_path = tmp_path / "MIGRATION.json"
    manifest = json.loads(manifest_path.read_text())
    manifest[field] = value
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="schema or source"):
        verify(tmp_path)


def test_duplicate_json_keys_are_rejected(tmp_path):
    _tree(tmp_path)
    path = tmp_path / "MIGRATION.json"
    path.write_text(path.read_text().replace('"schema": 1', '"schema": 1, "schema": 1'))
    with pytest.raises(ValueError, match="duplicate"):
        verify(tmp_path)
