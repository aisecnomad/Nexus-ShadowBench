"""Hash-locked tool installs, the digest-pinned build image and the runner's install record."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from tools.shadowbench.cases import runner

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "tools" / "shadowbench" / "cases"
LOCKS = CASES / "locks"
INSTALL = CASES / "install_tools.sh"
CONTAINERFILE = CASES / "images" / "Containerfile"

PYPI_VENVS = ("snyk-agent-scan", "mcp-scanner", "agentmesh-discovery", "agentdiscover")
_REQUIREMENT = re.compile(r"^([A-Za-z0-9._-]+)==([^ ;\\]+)")
_DIGEST_IMAGE = re.compile(r"[a-z0-9][a-z0-9._/:-]*@sha256:[0-9a-f]{64}")


def _requirements(lock: Path) -> dict[str, list[str]]:
    """Each pinned requirement of a hashed lock with the hashes listed under it."""
    out: dict[str, list[str]] = {}
    current: str | None = None
    for line in lock.read_text(encoding="utf-8").splitlines():
        found = _REQUIREMENT.match(line)
        if found:
            current = f"{found.group(1).lower()}=={found.group(2)}"
            out[current] = []
        elif current and line.strip().startswith("--hash=sha256:"):
            out[current].append(line.strip().removeprefix("--hash=sha256:").rstrip(" \\"))
    return out


@pytest.mark.parametrize("venv", PYPI_VENVS)
def test_every_pypi_lock_pins_its_tool_and_hashes_every_distribution(venv: str) -> None:
    pin = (LOCKS / f"{venv}.in").read_text(encoding="utf-8").strip().lower()
    requirements = _requirements(LOCKS / f"{venv}.txt")
    assert pin in requirements, f"{venv}.txt does not pin {pin}"
    for requirement, hashes in requirements.items():
        assert hashes, f"{venv}.txt: {requirement} has no hash"
        assert all(re.fullmatch(r"[0-9a-f]{64}", h) for h in hashes), requirement


def test_locks_name_no_local_path() -> None:
    for lock in LOCKS.iterdir():
        text = lock.read_text(encoding="utf-8")
        assert not re.search(r"(?:/tmp/|/root/|/home/|/Users/)", text), lock.name


def test_the_fleet_wrapper_go_sum_covers_its_go_mod() -> None:
    mod = (LOCKS / "fleet-ai-tools.go.mod").read_text(encoding="utf-8")
    required = re.findall(r"^\s+(\S+) (v\S+)", mod, flags=re.MULTILINE)
    assert required, "go.mod lists no requirements"
    sums = {tuple(line.split()[:2]) for line in (LOCKS / "fleet-ai-tools.go.sum").read_text().splitlines()}
    for module, version in required:
        assert (module, f"{version}/go.mod") in sums, f"go.sum lacks {module} {version}"


def test_the_installer_installs_only_from_locks() -> None:
    script = INSTALL.read_text(encoding="utf-8")
    code = "\n".join(line for line in script.splitlines() if not line.lstrip().startswith("#"))
    assert "--require-hashes --no-deps" in code
    assert "go mod tidy" not in code
    assert re.search(r"uv pip install [^\n]*==", code) is None, "a PyPI install outside the locks"
    for venv in PYPI_VENVS:
        assert f"venv {venv}" in code


@pytest.mark.skipif(shutil.which("bash") is None, reason="needs bash")
def test_the_installer_parses_and_refuses_unknown_tools(tmp_path: Path) -> None:
    assert subprocess.run(["bash", "-n", str(INSTALL)], check=False).returncode == 0
    root = tmp_path / "root"
    done = subprocess.run(
        ["bash", str(INSTALL), str(root), "bogus"], capture_output=True, text=True, check=False
    )
    assert done.returncode == 2
    assert "unknown tool bogus" in done.stderr
    assert not root.exists()


def test_every_base_image_is_pinned_by_digest() -> None:
    text = CONTAINERFILE.read_text(encoding="utf-8")
    images = dict(re.findall(r"^ARG (\w+_IMAGE)=(\S+)$", text, flags=re.MULTILINE))
    assert set(images) == {"PYTHON_IMAGE", "GO_IMAGE", "UV_IMAGE"}
    for name, image in images.items():
        assert _DIGEST_IMAGE.fullmatch(image), f"{name} is not pinned by digest: {image}"
    stages: set[str] = set()
    for source, stage in re.findall(r"^FROM (\S+)(?: AS (\w+))?$", text, flags=re.MULTILINE):
        variable = re.fullmatch(r"\$\{(\w+)\}", source)
        assert source == "scratch" or source in stages or (variable and variable.group(1) in images), source
        if stage:
            stages.add(stage)


def test_record_install_copies_the_resolved_record_and_its_digests(tmp_path: Path) -> None:
    root = tmp_path / "tools"
    (root / "resolved" / "locks").mkdir(parents=True)
    (root / "resolved" / "SHA256SUMS").write_text("abc  bin/x\n", encoding="utf-8")
    (root / "resolved" / "locks" / "x.txt").write_text("x==1\n", encoding="utf-8")
    secret = tmp_path / "secret"
    secret.write_text("not part of the record", encoding="utf-8")
    os.symlink(secret, root / "resolved" / "link")
    os.symlink(tmp_path, root / "resolved" / "dirlink")
    out = tmp_path / "out"
    record = runner.record_install(root, out)
    assert record == {
        "resolved": {
            "SHA256SUMS": hashlib.sha256(b"abc  bin/x\n").hexdigest(),
            "locks/x.txt": hashlib.sha256(b"x==1\n").hexdigest(),
        }
    }
    assert (out / "resolved" / "locks" / "x.txt").read_text(encoding="utf-8") == "x==1\n"
    assert not (out / "resolved" / "link").exists() and not (out / "resolved" / "dirlink").exists()


def test_record_install_without_a_record_says_so(tmp_path: Path) -> None:
    assert runner.record_install(tmp_path, tmp_path / "out") == {"resolved": None}
    assert not (tmp_path / "out").exists()
