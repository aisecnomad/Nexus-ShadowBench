"""Reproducible checkouts: fetch each corpus repository at its pinned commit.

Only ``git`` runs here, and the repositories are untrusted input, so every
call goes through the ShadowBench cases track's hardened fetcher
(:mod:`tools.shadowbench.cases.fetch_code`, whose docstring lists the rules):
``https`` remotes without credentials and no other transport, none of the
operator's system or global git configuration or attributes, the caller's
``GIT_*`` variables dropped except the TLS trust anchors, hooks, submodules
and filter drivers off, TLS verification on, and no symbolic link followed.
Checkouts are detached at the pinned commit, which is checked before anything
is checked out and again afterwards, so a later push to the default branch
cannot change the benchmark input. An existing checkout is reused only when
that fetcher made it from the pinned URL and it holds exactly the pinned tree.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from tools.discovery_benchmark.corpus import Corpus, Repo
from tools.shadowbench.cases.fetch_code import FetchError, checkout_problem, fetch_pinned

__all__ = ["FetchError", "fetch_all", "fetch_repo", "verify_all"]


def fetch_repo(repo: Repo, dest: Path) -> str:
    """Fetch ``repo`` at its pinned commit into ``dest`` and return the verified HEAD.

    The pinned commit is requested directly (depth 1). Hosts that refuse an
    unadvertised commit fall back to the default branch, which succeeds only
    when that branch still points at the pinned commit.
    """
    return fetch_pinned(repo.url, repo.commit, repo.default_branch, dest)


def fetch_all(corpus: Corpus, root: Path) -> dict[str, str]:
    """Fetch every repository under ``root/<repo id>``; errors are collected, not raised."""
    outcome: dict[str, str] = {}
    for repo in corpus.repos:
        try:
            outcome[repo.id] = fetch_repo(repo, root / repo.id)
        except (FetchError, OSError, subprocess.TimeoutExpired) as exc:
            outcome[repo.id] = f"ERROR: {exc}"
    return outcome


def verify_all(corpus: Corpus, root: Path) -> dict[str, str]:
    """Report, per repository, whether an existing checkout holds exactly its pinned commit's tree."""
    outcome: dict[str, str] = {}
    for repo in corpus.repos:
        checkout = root / repo.id
        if checkout.is_symlink():
            outcome[repo.id] = "ERROR: the checkout is a symbolic link"
            continue
        if not checkout.exists():
            outcome[repo.id] = "MISSING"
            continue
        try:
            problem = checkout_problem(checkout, repo.commit)
        except (OSError, subprocess.TimeoutExpired) as exc:
            outcome[repo.id] = f"ERROR: {exc}"
            continue
        outcome[repo.id] = "OK" if problem is None else f"MISMATCH: the checkout {problem}"
    return outcome
