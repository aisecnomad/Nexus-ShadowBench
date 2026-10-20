"""The code-surface fetch runs only the hardened, pinned git of the cases track's fetcher."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from tools.discovery_benchmark import fetch
from tools.shadowbench.cases import fetch_code

FAKE_PASSWORD = "not-a-real-password"


def _git(*args: str, cwd: Path) -> str:
    settings = ("user.name=bench", "user.email=bench@example.invalid", "commit.gpgsign=false")
    config = [part for setting in settings for part in ("-c", setting)]
    done = subprocess.run(["git", *config, *args], cwd=cwd, capture_output=True, text=True, check=True)
    return done.stdout.strip()


def _corpus(url: str, commit: str) -> Any:
    repo = SimpleNamespace(id="demo__repo", url=url, commit=commit, default_branch="main")
    return SimpleNamespace(repos=[repo])


@pytest.fixture
def local_origin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    """A local repository with one pinned commit, reachable once file:// is allowed."""
    src = tmp_path / "src"
    src.mkdir()
    _git("init", "-q", "-b", "main", cwd=src)
    (src / "README.md").write_text("pinned\n", encoding="utf-8")
    _git("add", "README.md", cwd=src)
    _git("commit", "-q", "-m", "pinned", cwd=src)
    monkeypatch.setattr(fetch_code, "https_remote", lambda remote: remote)
    monkeypatch.setattr(fetch_code, "GIT_CONFIG", (*fetch_code.GIT_CONFIG, "protocol.file.allow=always"))
    return f"file://{src}", _git("rev-parse", "HEAD", cwd=src)


@pytest.mark.skipif(not shutil.which("git"), reason="needs git")
def test_fetch_and_verify_a_pinned_checkout(tmp_path: Path, local_origin: tuple[str, str]) -> None:
    url, pinned = local_origin
    corpus = _corpus(url, pinned)
    root = tmp_path / "checkouts"
    assert fetch.verify_all(corpus, root) == {"demo__repo": "MISSING"}
    assert fetch.fetch_all(corpus, root) == {"demo__repo": pinned}
    checkout = root / "demo__repo"
    assert _git("rev-parse", "--abbrev-ref", "HEAD", cwd=checkout) == "HEAD"  # detached
    assert (checkout / ".git" / "info" / "attributes").read_text(encoding="utf-8") == fetch_code.NO_FILTERS
    assert fetch.verify_all(corpus, root) == {"demo__repo": "OK"}
    assert fetch.fetch_all(corpus, root) == {"demo__repo": pinned}  # an untouched checkout is kept


@pytest.mark.skipif(not shutil.which("git"), reason="needs git")
def test_a_changed_checkout_fails_verification_and_is_refetched(
    tmp_path: Path, local_origin: tuple[str, str]
) -> None:
    url, pinned = local_origin
    corpus = _corpus(url, pinned)
    root = tmp_path / "checkouts"
    fetch.fetch_all(corpus, root)
    planted = root / "demo__repo" / "planted.py"
    planted.write_text("print('not part of the pinned tree')\n", encoding="utf-8")
    status = fetch.verify_all(corpus, root)["demo__repo"]
    assert status.startswith("MISMATCH: the checkout differs from")
    # The old fetcher kept any checkout whose HEAD matched; this one replaces it.
    assert fetch.fetch_all(corpus, root) == {"demo__repo": pinned}
    assert not planted.exists()
    assert fetch.verify_all(corpus, root) == {"demo__repo": "OK"}


@pytest.mark.skipif(not shutil.which("git"), reason="needs git")
def test_a_commit_the_remote_does_not_hold_is_refused(tmp_path: Path, local_origin: tuple[str, str]) -> None:
    url, _ = local_origin
    outcome = fetch.fetch_all(_corpus(url, "f" * 40), tmp_path / "checkouts")
    assert outcome["demo__repo"].startswith("ERROR: ")


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/demo/repo.git",
        "ssh://git@github.com/demo/repo.git",
        "file:///srv/demo/repo.git",
        # A fake password, joined at run time so the source holds no credential-shaped URL.
        "https://user:" + FAKE_PASSWORD + "@github.com/demo/repo.git",
    ],
)
def test_non_https_remotes_are_refused_before_git_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, url: str
) -> None:
    calls: list[list[str]] = []
    monkeypatch.setattr(subprocess, "run", lambda argv, **kwargs: calls.append(argv))
    outcome = fetch.fetch_all(_corpus(url, "a" * 40), tmp_path / "checkouts")
    assert outcome["demo__repo"].startswith("ERROR: refusing")
    assert FAKE_PASSWORD not in outcome["demo__repo"]
    assert calls == []
    assert not (tmp_path / "checkouts" / "demo__repo").exists()


def test_a_symlinked_checkout_is_never_followed(tmp_path: Path) -> None:
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    root = tmp_path / "checkouts"
    root.mkdir()
    (root / "demo__repo").symlink_to(elsewhere, target_is_directory=True)
    corpus = _corpus("https://github.com/demo/repo.git", "a" * 40)
    assert fetch.verify_all(corpus, root) == {"demo__repo": "ERROR: the checkout is a symbolic link"}
    assert fetch.fetch_all(corpus, root)["demo__repo"].startswith("ERROR: ")
    assert list(elsewhere.iterdir()) == []
