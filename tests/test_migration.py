"""The imported evidence must retain the exact source bytes and file modes."""

from __future__ import annotations

import hashlib
import json
import subprocess

import pytest

from tools.verify_migration import ROOT, SOURCE_COMMIT, amend, amendable, check_source, verify


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


# --- AMENDMENTS.json: harness code may change only through a recorded chain ----------------------

HARNESS = "tools/shadowbench/demo.py"
EVIDENCE = "benchmarks/demo/results/metrics.json"


def _identity(data: bytes) -> dict[str, object]:
    return {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(),
    }


def _harness_tree(tmp_path):
    files = {HARNESS: b"VALUE = 1\n", EVIDENCE: b'{"f1": 0.5}\n'}
    entries = []
    for name, data in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        entries.append({"path": name, "disposition": "moved", "mode": "100644", **_identity(data)})
    (tmp_path / "MIGRATION.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "source_commit": SOURCE_COMMIT,
                "source_repository": "https://github.com/aisecnomad/Nexus-ShadowScan",
                "companion_repository": "https://github.com/aisecnomad/Nexus-ShadowBench",
                "note": "Synthetic amendment regression input.",
                "files": entries,
            }
        )
    )


def _ledger(tmp_path):
    return json.loads((tmp_path / "AMENDMENTS.json").read_text())


def test_the_real_ledger_amends_only_harness_code():
    result = verify()
    ledger = json.loads((ROOT / "AMENDMENTS.json").read_text())
    assert result["amended"] == len({entry["path"] for entry in ledger["amendments"]})
    assert all(amendable(entry["path"]) for entry in ledger["amendments"])


def test_an_amended_harness_file_verifies_only_through_its_ledger_entry(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    with pytest.raises(ValueError, match="bytes or mode changed"):
        verify(tmp_path)
    entry = amend(HARNESS, "harden the demo", "https://example.invalid/pr/1", root=tmp_path)
    assert entry["from_sha256"] == hashlib.sha256(b"VALUE = 1\n").hexdigest()
    assert verify(tmp_path)["amended"] == 1
    (tmp_path / HARNESS).write_bytes(b"VALUE = 3\n")
    with pytest.raises(ValueError, match="since the last amendment"):
        verify(tmp_path)
    second = amend(HARNESS, "again", "https://example.invalid/pr/2", root=tmp_path)
    assert second["from_sha256"] == entry["sha256"]
    assert [item["reason"] for item in _ledger(tmp_path)["amendments"]] == ["harden the demo", "again"]
    assert verify(tmp_path)["amended"] == 1


def test_evidence_is_never_amendable(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / EVIDENCE).write_bytes(b'{"f1": 0.9}\n')
    with pytest.raises(ValueError, match="never amendable"):
        amend(EVIDENCE, "better numbers", "https://example.invalid/pr/1", root=tmp_path)
    assert not (tmp_path / "AMENDMENTS.json").exists()
    forged = {"path": EVIDENCE, "from_sha256": hashlib.sha256(b'{"f1": 0.5}\n').hexdigest()}
    forged |= {"mode": "100644", "reason": "r", "reference": "x", **_identity(b'{"f1": 0.9}\n')}
    (tmp_path / "AMENDMENTS.json").write_text(json.dumps({"schema": 1, "note": "n", "amendments": [forged]}))
    with pytest.raises(ValueError, match="never amendable"):
        verify(tmp_path)


@pytest.mark.parametrize(
    "path",
    [
        "tools/shadowbench/cases/families/identity.py",
        "tools/shadowbench/cases/generate.py",
        "tools/discovery_benchmark/evidence.py",
        "tools/discovery_benchmark/taxonomy.py",
        "tools/benchmark/score.py",
        "tools/benchmark_realworld/score.py",
        "benchmarks/sab_realworld/harness.py",
        "benchmarks/shadowbench/cases/corpus.json",
        "tools/shadowbench/estate/results/runs.json",
    ],
)
def test_generators_labelers_taxonomies_legacy_code_and_data_are_not_amendable(path):
    assert not amendable(path)


def test_live_harness_code_and_tests_are_amendable():
    for path in (
        "tools/discovery_benchmark/fetch.py",
        "tools/shadowbench/cases/install_tools.sh",
        "tests/x.py",
    ):
        assert amendable(path)


def test_a_broken_or_unchanged_chain_is_rejected(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    amend(HARNESS, "r", "x", root=tmp_path)
    ledger = _ledger(tmp_path)
    ledger["amendments"][0]["from_sha256"] = "0" * 64
    (tmp_path / "AMENDMENTS.json").write_text(json.dumps(ledger))
    with pytest.raises(ValueError, match="does not start from the recorded bytes"):
        verify(tmp_path)
    ledger["amendments"][0]["from_sha256"] = ledger["amendments"][0]["sha256"]
    (tmp_path / "AMENDMENTS.json").write_text(json.dumps(ledger))
    with pytest.raises(ValueError, match="does not start from|unchanged"):
        verify(tmp_path)


def test_an_unchanged_file_or_a_missing_reason_records_nothing(tmp_path):
    _harness_tree(tmp_path)
    with pytest.raises(ValueError, match="unchanged"):
        amend(HARNESS, "r", "x", root=tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    with pytest.raises(ValueError, match="reason and a reference"):
        amend(HARNESS, " ", "x", root=tmp_path)
    assert not (tmp_path / "AMENDMENTS.json").exists()


def test_a_failed_amendment_leaves_the_ledger_as_it_was(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    (tmp_path / EVIDENCE).write_bytes(b"tampered\n")
    with pytest.raises(ValueError, match="bytes or mode changed"):
        amend(HARNESS, "r", "x", root=tmp_path)
    assert not (tmp_path / "AMENDMENTS.json").exists()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda ledger: ledger.update(schema=2),
        lambda ledger: ledger.update(extra=True),
        lambda ledger: ledger["amendments"][0].update(reason=""),
        lambda ledger: ledger["amendments"][0].update(reference=7),
        lambda ledger: ledger["amendments"][0].update(path="tools/shadowbench/other.py"),
        lambda ledger: ledger["amendments"][0].update(mode="120000"),
        lambda ledger: ledger["amendments"][0].update(unexpected="key"),
    ],
)
def test_malformed_ledgers_are_rejected(tmp_path, mutate):
    _harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    amend(HARNESS, "r", "x", root=tmp_path)
    ledger = _ledger(tmp_path)
    mutate(ledger)
    (tmp_path / "AMENDMENTS.json").write_text(json.dumps(ledger))
    with pytest.raises(ValueError):
        verify(tmp_path)


def test_removing_the_ledger_fails_closed(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    amend(HARNESS, "r", "x", root=tmp_path)
    (tmp_path / "AMENDMENTS.json").unlink()
    with pytest.raises(ValueError, match="bytes or mode changed"):
        verify(tmp_path)


def test_copied_ci_and_build_locks_are_amendable_but_the_original_lock_is_not():
    assert amendable("requirements-ci.lock")
    assert amendable("requirements-build.lock")
    assert not amendable("migration/requirements.source.lock")
    assert not amendable("requirements-docs.lock")
    assert not amendable("tools/requirements-ci.lock")


# --- Anchors: the source commit and the previous commit -------------------------------------------


def _manifest_of(tmp_path):
    return json.loads((tmp_path / "MIGRATION.json").read_text())


def test_records_must_name_the_blob_and_mode_of_the_source_commit(tmp_path):
    _tree(tmp_path)
    manifest = _manifest_of(tmp_path)
    entry = manifest["files"][0]
    check_source(manifest, {"fixture.txt": ("100644", entry["git_blob"])})
    for tree in (
        {},
        {"fixture.txt": ("100755", entry["git_blob"])},
        {"fixture.txt": ("100644", "0" * 40)},
        {"elsewhere.txt": ("100644", entry["git_blob"])},
    ):
        with pytest.raises(ValueError, match="does not match the source commit"):
            check_source(manifest, tree)


@pytest.mark.skipif(not (ROOT / "scanner-source" / ".git").exists(), reason="no pinned scanner checkout")
def test_the_real_records_match_the_pinned_scanner_checkout():
    assert verify(source=ROOT / "scanner-source")["source_tree_checked"] is True


def _git(tmp_path, *args):
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )


def _committed_harness_tree(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    amend(HARNESS, "first", "https://example.invalid/pr/1", root=tmp_path)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")


def test_a_ledger_that_only_grows_verifies_since_its_base(tmp_path):
    _committed_harness_tree(tmp_path)
    assert verify(tmp_path, since="HEAD")["since"] == "HEAD"
    (tmp_path / HARNESS).write_bytes(b"VALUE = 3\n")
    amend(HARNESS, "second", "https://example.invalid/pr/2", root=tmp_path)
    assert verify(tmp_path, since="HEAD")["amended"] == 1


@pytest.mark.parametrize(
    "rewrite",
    [
        lambda ledger: ledger["amendments"][0].update(reason="a better story"),
        lambda ledger: ledger["amendments"][0].update(reference="https://example.invalid/pr/9"),
        lambda ledger: ledger.update(note="Edited."),
    ],
)
def test_rewriting_a_recorded_amendment_is_rejected(tmp_path, rewrite):
    _committed_harness_tree(tmp_path)
    ledger = _ledger(tmp_path)
    rewrite(ledger)
    (tmp_path / "AMENDMENTS.json").write_text(json.dumps(ledger))
    verify(tmp_path)
    with pytest.raises(ValueError, match="rewrote, reordered or dropped"):
        verify(tmp_path, since="HEAD")


def test_collapsing_a_chain_is_rejected(tmp_path):
    _committed_harness_tree(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 3\n")
    amend(HARNESS, "second", "https://example.invalid/pr/2", root=tmp_path)
    _git(tmp_path, "commit", "-q", "-am", "second")
    ledger = _ledger(tmp_path)
    first, second = ledger["amendments"]
    ledger["amendments"] = [{**second, "from_sha256": first["from_sha256"]}]
    (tmp_path / "AMENDMENTS.json").write_text(json.dumps(ledger))
    verify(tmp_path)
    with pytest.raises(ValueError, match="rewrote, reordered or dropped"):
        verify(tmp_path, since="HEAD")


def test_unbinding_a_file_from_the_migration_record_is_rejected(tmp_path):
    _committed_harness_tree(tmp_path)
    manifest = _manifest_of(tmp_path)
    manifest["files"] = [entry for entry in manifest["files"] if entry["path"] != EVIDENCE]
    (tmp_path / "MIGRATION.json").write_text(json.dumps(manifest))
    (tmp_path / EVIDENCE).write_bytes(b'{"f1": 0.9}\n')
    verify(tmp_path)
    with pytest.raises(ValueError, match="MIGRATION.json changed since HEAD"):
        verify(tmp_path, since="HEAD")


def test_removing_a_committed_ledger_is_rejected(tmp_path):
    _committed_harness_tree(tmp_path)
    (tmp_path / "AMENDMENTS.json").unlink()
    with pytest.raises(ValueError):
        verify(tmp_path, since="HEAD")
    with pytest.raises(ValueError, match="removed since HEAD"):
        from tools.verify_migration import check_since

        check_since(tmp_path, "HEAD")


@pytest.mark.parametrize("ref", ["-c", "--upload-pack=x", "HEAD:MIGRATION.json", "no-such-commit"])
def test_since_takes_only_a_commit_that_exists(tmp_path, ref):
    _committed_harness_tree(tmp_path)
    with pytest.raises(ValueError, match="revision|not a commit"):
        verify(tmp_path, since=ref)


def test_a_missing_migrated_file_fails_closed_and_amend_leaves_the_ledger(tmp_path):
    _harness_tree(tmp_path)
    (tmp_path / EVIDENCE).unlink()
    with pytest.raises(ValueError, match="missing"):
        verify(tmp_path)
    (tmp_path / HARNESS).write_bytes(b"VALUE = 2\n")
    with pytest.raises(ValueError, match="missing"):
        amend(HARNESS, "r", "x", root=tmp_path)
    assert not (tmp_path / "AMENDMENTS.json").exists()
