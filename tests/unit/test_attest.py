"""Result attestations (tools/attest.py): digest manifests and Sigstore bundle verification."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from tools import attest

SUBJECT = "benchmarks/x/results/2026-10-21"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    results = tmp_path / SUBJECT
    (results / "raw").mkdir(parents=True)
    (results / "metrics.json").write_text('{"f1": 0.5}\n', encoding="utf-8")
    (results / "REPORT.md").write_text("# Report\n", encoding="utf-8")
    (results / "raw" / "t.jsonl").write_text("{}\n", encoding="utf-8")
    return tmp_path


def _attest(repo: Path) -> Path:
    return attest.write_digest(repo, SUBJECT)


def test_a_digest_manifest_lists_every_file_and_is_reproducible(repo: Path) -> None:
    path = _attest(repo)
    assert path == repo / "attestations" / "benchmarks__x__results__2026-10-21.json"
    first = path.read_bytes()
    document = json.loads(first)
    assert document["subject"] == SUBJECT
    assert sorted(document["files"]) == ["REPORT.md", "metrics.json", "raw/t.jsonl"]
    assert _attest(repo).read_bytes() == first


def test_an_untouched_unsigned_directory_verifies_unless_signatures_are_required(repo: Path) -> None:
    _attest(repo)
    summary, problems = attest.verify(repo)
    assert problems == []
    assert summary == {"attestations": 1, "signed": 0, "unsigned": [SUBJECT]}
    _, problems = attest.verify(repo, require_signatures=True)
    assert problems == [
        "benchmarks__x__results__2026-10-21.json: no Sigstore bundle (benchmarks__x__results__2026-10-21.sigstore.json)"
    ]


@pytest.mark.parametrize(
    ("tamper", "expected"),
    [
        (
            lambda d: (d / "metrics.json").write_text('{"f1": 0.9}\n', encoding="utf-8"),
            "metrics.json: changed",
        ),
        (lambda d: (d / "REPORT.md").unlink(), "REPORT.md: missing"),
        (
            lambda d: (d / "extra.json").write_text("{}", encoding="utf-8"),
            "extra.json: not in the attestation",
        ),
    ],
)
def test_a_changed_results_directory_fails(repo: Path, tamper: Any, expected: str) -> None:
    _attest(repo)
    tamper(repo / SUBJECT)
    _, problems = attest.verify(repo)
    assert problems == [f"{SUBJECT}: {expected}"]


def test_an_edited_manifest_is_not_what_was_signed(repo: Path) -> None:
    path = _attest(repo)
    document = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(document), encoding="utf-8")  # same content, other bytes
    _, problems = attest.verify(repo)
    assert problems and "not in canonical form" in problems[0]


def test_a_manifest_under_another_subjects_name_is_refused(repo: Path) -> None:
    path = _attest(repo)
    path.rename(path.with_name("benchmarks__y.json"))
    _, problems = attest.verify(repo)
    assert problems and "which is another file's" in problems[0]


@pytest.mark.parametrize(
    "subject", ["tools/x", "/abs/benchmarks/x", "benchmarks/../tools", "benchmarks/missing"]
)
def test_subjects_outside_benchmarks_are_refused(repo: Path, subject: str) -> None:
    with pytest.raises(attest.AttestationError):
        attest.write_digest(repo, subject)


def test_symlinks_are_refused(repo: Path, tmp_path: Path) -> None:
    os.symlink(tmp_path / "elsewhere", repo / SUBJECT / "link")
    with pytest.raises(attest.AttestationError, match="symlink"):
        _attest(repo)


def test_a_bundle_that_cannot_be_checked_fails(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _attest(repo)
    path.with_name(f"{path.stem}.sigstore.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(attest.shutil, "which", lambda name: None)
    summary, problems = attest.verify(repo)
    assert summary["signed"] == 0
    assert problems == [f"{path.name}: cosign is not installed, so the signature cannot be checked"]


def test_a_bundle_cosign_accepts_counts_as_signed(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = _attest(repo)
    bundle = path.with_name(f"{path.stem}.sigstore.json")
    bundle.write_text("{}", encoding="utf-8")
    calls: list[list[str]] = []

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "Verified OK", "")

    monkeypatch.setattr(attest.shutil, "which", lambda name: "/usr/bin/cosign")
    monkeypatch.setattr(attest.subprocess, "run", run)
    summary, problems = attest.verify(repo)
    assert (summary["signed"], problems) == (1, [])
    command = calls[0]
    assert command[:2] == ["/usr/bin/cosign", "verify-blob"]
    assert command[command.index("--certificate-identity-regexp") + 1] == attest.DEFAULT_IDENTITY
    assert command[command.index("--certificate-oidc-issuer") + 1] == attest.DEFAULT_ISSUER
    assert command[command.index("--bundle") + 1] == str(bundle) and command[-1] == str(path)


def test_an_orphan_bundle_fails(repo: Path) -> None:
    (repo / "attestations").mkdir()
    (repo / "attestations" / "benchmarks__z.sigstore.json").write_text("{}", encoding="utf-8")
    _, problems = attest.verify(repo)
    assert problems == ["benchmarks__z.sigstore.json: a bundle without its digest manifest"]


@pytest.mark.skipif(shutil.which("cosign") is None, reason="needs cosign")
def test_cosign_rejects_a_signature_from_another_identity(repo: Path, tmp_path: Path) -> None:
    """A real bundle signed with a local key carries no certificate for the workflow identity."""
    path = _attest(repo)
    bundle = path.with_name(f"{path.stem}.sigstore.json")
    env = {**os.environ, "COSIGN_PASSWORD": ""}
    keys = tmp_path / "keys"
    keys.mkdir()
    subprocess.run(["cosign", "generate-key-pair"], cwd=keys, env=env, check=True, capture_output=True)
    subprocess.run(
        [
            "cosign",
            "sign-blob",
            "--yes",
            "--use-signing-config=false",
            "--tlog-upload=false",
            "--key",
            str(keys / "cosign.key"),
            "--bundle",
            str(bundle),
            str(path),
        ],
        env=env,
        check=True,
        capture_output=True,
    )
    _, problems = attest.verify(repo)
    assert len(problems) == 1 and "cosign verify-blob failed" in problems[0]


def test_the_repository_attestations_verify() -> None:
    _, problems = attest.verify(ROOT)
    assert problems == []


@pytest.mark.parametrize(
    "subject",
    [f"{SUBJECT[:10]}./{SUBJECT[10:]}", SUBJECT.replace("/", "//", 1), "benchmarks", "benchmarks\\x/results"],
)
def test_one_directory_has_one_spelling(repo: Path, subject: str) -> None:
    """Path() dropped "." and "//", so one directory could be attested under several slugs."""
    with pytest.raises(attest.AttestationError, match="relative directory under benchmarks|cannot name"):
        attest.write_digest(repo, subject)


def _commit(repo: Path) -> None:
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "base"]):
        subprocess.run([*git, *args], cwd=repo, check=True, capture_output=True)


def test_committed_attestation_files_cannot_be_removed_or_changed_since_a_commit(repo: Path) -> None:
    """Deleting a bundle turned a signed directory into an unsigned one that still verified."""
    manifest = _attest(repo)
    bundle = manifest.with_name(f"{manifest.stem}.sigstore.json")
    bundle.write_text("{}\n", encoding="utf-8")
    _commit(repo)
    assert attest.removed_since(repo, "HEAD") == []
    bundle.unlink()
    _, problems = attest.verify(repo, since="HEAD")
    assert problems == [f"attestations/{bundle.name}: committed at HEAD and now removed"]
    bundle.write_text('{"forged": true}\n', encoding="utf-8")
    assert attest.removed_since(repo, "HEAD") == [
        f"attestations/{bundle.name}: committed at HEAD and now changed"
    ]
    manifest.unlink()
    bundle.unlink()
    assert len(attest.removed_since(repo, "HEAD")) == 2


def test_a_new_attestation_is_not_a_change_since_a_commit(repo: Path) -> None:
    _commit(repo)
    _attest(repo)
    assert attest.removed_since(repo, "HEAD") == []
    _, problems = attest.verify(repo, since="no-such-ref")
    assert problems and "not a commit" in problems[0]
