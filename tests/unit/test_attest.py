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
    assert any("no Sigstore bundle" in problem for problem in problems)
    assert all(any(subject in problem for problem in problems) for subject in attest.REQUIRED_SUBJECTS)


@pytest.mark.parametrize("empty_directory", [False, True])
def test_strict_verification_requires_historical_manifests_even_without_attestations(
    repo: Path, empty_directory: bool
) -> None:
    if empty_directory:
        (repo / attest.ATTESTATIONS).mkdir()
    summary, problems = attest.verify(repo, require_signatures=True)
    assert summary["signed"] == 0
    assert problems == [
        f"{subject}: required historical results attestation is missing"
        for subject in attest.REQUIRED_SUBJECTS
    ]
    # Existing one-at-a-time signing remains available until all runs are signed.
    assert attest.verify(repo)[1] == []


def test_cli_strict_verification_fails_without_manifests(
    repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(attest, "ROOT", repo)
    assert attest.main(["verify", "--require-signatures"]) == 1
    captured = capsys.readouterr()
    assert all(subject in captured.err for subject in attest.REQUIRED_SUBJECTS)
    assert json.loads(captured.out)["signed"] == 0


def _historical_manifests(repo: Path, monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    """Synthetic manifests and a stub verifier, never historical signing evidence."""
    manifests = []
    for subject in attest.REQUIRED_SUBJECTS:
        directory = repo / subject
        directory.mkdir(parents=True)
        (directory / "metrics.json").write_text('{"fixture": true}\n', encoding="utf-8")
        path = attest.write_digest(repo, subject)
        path.with_name(f"{path.stem}.sigstore.json").write_text("{}\n", encoding="utf-8")
        manifests.append(path)
    monkeypatch.setattr(attest, "cosign_verify", lambda *args: None)
    return manifests


@pytest.mark.parametrize("missing", attest.REQUIRED_SUBJECTS)
def test_strict_verification_requires_every_historical_subject(
    repo: Path, monkeypatch: pytest.MonkeyPatch, missing: str
) -> None:
    manifests = _historical_manifests(repo, monkeypatch)
    assert attest.verify(repo, require_signatures=True) == (
        {"attestations": 3, "signed": 3, "unsigned": []},
        [],
    )
    path = next(path for path in manifests if path.stem == attest.slug(missing))
    path.unlink()
    path.with_name(f"{path.stem}.sigstore.json").unlink()
    _, problems = attest.verify(repo, require_signatures=True)
    assert problems == [f"{missing}: required historical results attestation is missing"]


def test_strict_verification_rejects_a_missing_historical_bundle(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = _historical_manifests(repo, monkeypatch)[0]
    path.with_name(f"{path.stem}.sigstore.json").unlink()
    summary, problems = attest.verify(repo, require_signatures=True)
    assert summary["signed"] == 2
    assert len(problems) == 1 and "no Sigstore bundle" in problems[0]


def test_strict_verification_rejects_changed_evidence_even_when_the_signature_verifies(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _historical_manifests(repo, monkeypatch)
    subject = attest.REQUIRED_SUBJECTS[0]
    (repo / subject / "metrics.json").write_text('{"fixture": "changed"}\n', encoding="utf-8")
    _, problems = attest.verify(repo, require_signatures=True)
    assert problems == [f"{subject}: metrics.json: changed"]


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


@pytest.mark.parametrize("entry", ["directory", "manifest", "bundle"])
def test_attestation_symlinks_are_refused(repo: Path, tmp_path: Path, entry: str) -> None:
    path = _attest(repo)
    bundle = path.with_name(f"{path.stem}.sigstore.json")
    bundle.write_text("{}\n", encoding="utf-8")
    original = path.parent if entry == "directory" else path if entry == "manifest" else bundle
    external = tmp_path / "outside"
    original.rename(external)
    original.symlink_to(external, target_is_directory=entry == "directory")
    _, problems = attest.verify(repo)
    assert any("symlink" in problem for problem in problems)
    if entry in {"directory", "manifest"}:
        with pytest.raises(attest.AttestationError, match="symlink"):
            _attest(repo)


def test_unreadable_attestation_directory_fails(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _attest(repo)
    original = Path.iterdir

    def iterdir(path: Path) -> Any:
        if path == repo / attest.ATTESTATIONS:
            raise PermissionError("fixture read denied")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", iterdir)
    _, problems = attest.verify(repo)
    assert len(problems) == 1 and "cannot read directory" in problems[0]


def test_unreadable_manifest_fails(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manifest = _attest(repo)
    original = Path.read_bytes

    def read_bytes(path: Path) -> bytes:
        if path == manifest:
            raise PermissionError("fixture read denied")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes)
    _, problems = attest.verify(repo)
    assert len(problems) == 1 and "unreadable" in problems[0]


def test_invalid_utf8_manifest_fails(repo: Path) -> None:
    _attest(repo).write_bytes(b"\xff")
    _, problems = attest.verify(repo)
    assert len(problems) == 1 and "unreadable" in problems[0]


def test_a_nonregular_bundle_fails_even_without_strict_mode(repo: Path) -> None:
    path = _attest(repo)
    path.with_name(f"{path.stem}.sigstore.json").mkdir()
    _, problems = attest.verify(repo)
    assert len(problems) == 1 and "bundle must be a regular file" in problems[0]


def test_unreadable_result_subdirectory_fails(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _attest(repo)

    def walk(path: Path, *, onerror: Any) -> list[Any]:
        onerror(PermissionError(13, "fixture read denied", str(path / "raw")))
        return []

    monkeypatch.setattr(attest.os, "walk", walk)
    _, problems = attest.verify(repo)
    assert len(problems) == 1 and "cannot read results directory" in problems[0]


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


@pytest.mark.parametrize(
    "failure",
    ["invalid signature", "certificate identity does not match", "certificate OIDC issuer does not match"],
)
def test_cosign_rejections_fail_closed(repo: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> None:
    path = _attest(repo)
    path.with_name(f"{path.stem}.sigstore.json").write_text("{}\n", encoding="utf-8")

    def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        # The verifier must always constrain both the workflow and the issuer.
        assert command[command.index("--certificate-identity-regexp") + 1] == attest.DEFAULT_IDENTITY
        assert command[command.index("--certificate-oidc-issuer") + 1] == attest.DEFAULT_ISSUER
        return subprocess.CompletedProcess(command, 1, "", failure)

    monkeypatch.setattr(attest.shutil, "which", lambda name: "/usr/bin/cosign")
    monkeypatch.setattr(attest.subprocess, "run", run)
    summary, problems = attest.verify(repo)
    assert summary["signed"] == 0
    assert problems == [f"{path.name}: cosign verify-blob failed: {failure}"]


@pytest.mark.parametrize(
    "failure", [OSError("fixture cannot start"), subprocess.TimeoutExpired("cosign", 300)]
)
def test_cosign_execution_errors_fail_closed(
    repo: Path, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    path = _attest(repo)
    path.with_name(f"{path.stem}.sigstore.json").write_text("{}\n", encoding="utf-8")

    def run(command: list[str], **kwargs: Any) -> None:
        raise failure

    monkeypatch.setattr(attest.shutil, "which", lambda name: "/usr/bin/cosign")
    monkeypatch.setattr(attest.subprocess, "run", run)
    summary, problems = attest.verify(repo)
    assert summary["signed"] == 0
    assert len(problems) == 1 and "cosign failed to run" in problems[0]


@pytest.mark.skipif(shutil.which("cosign") is None, reason="needs cosign")
def test_cosign_rejects_a_malformed_bundle(repo: Path) -> None:
    path = _attest(repo)
    path.with_name(f"{path.stem}.sigstore.json").write_text("{}\n", encoding="utf-8")
    summary, problems = attest.verify(repo)
    assert summary["signed"] == 0
    assert len(problems) == 1 and "cosign verify-blob failed" in problems[0]


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


def test_the_repository_attestations_require_all_historical_signatures() -> None:
    summary, problems = attest.verify(ROOT, require_signatures=True)
    assert problems == []
    assert summary == {
        "attestations": len(attest.REQUIRED_SUBJECTS),
        "signed": len(attest.REQUIRED_SUBJECTS),
        "unsigned": [],
    }
    subjects = {
        json.loads(path.read_bytes())["subject"]
        for path in (ROOT / attest.ATTESTATIONS).glob("*.json")
        if not path.name.endswith(".sigstore.json")
    }
    assert subjects == set(attest.REQUIRED_SUBJECTS)


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
