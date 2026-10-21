"""Sandbox hardening of the cases runner: resource limits, UTS and cgroup namespaces, the OCI backend.

The tests that run the real stage need root and ``unshare`` (as in test_shadowbench_cases_runner.py);
the end-to-end OCI test also needs a reachable Docker daemon and ``SHADOWBENCH_OCI_IMAGE``, an image
pinned by digest and present locally that has ``python3`` (for example the ``python:3.13-slim``
image by digest).
"""

from __future__ import annotations

import functools
import json
import os
import resource
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from tools.shadowbench.cases import runner, stage
from tools.shadowbench.cases.contract import ToolEnv

ROOT = Path(__file__).resolve().parents[2]
TOOL_PATH = "/usr/local/bin:/usr/bin:/bin"
DIGEST = "sha256:" + "a" * 64
IMAGE = f"python@{DIGEST}"

# --- limits ---------------------------------------------------------------------------------------


def test_default_limits_disable_core_dumps_and_bound_files_and_processes() -> None:
    assert stage.DEFAULT_LIMITS["core"] == 0
    assert set(stage.DEFAULT_LIMITS) <= set(stage.LIMITS)
    assert stage.check_limits(stage.DEFAULT_LIMITS) == stage.DEFAULT_LIMITS


@pytest.mark.parametrize(
    ("limits", "message"),
    [
        ({"stack": 1}, "unknown resource limit"),
        ({"core": -1}, "non-negative integer"),
        ({"core": True}, "non-negative integer"),
        ({"core": "0"}, "non-negative integer"),
        ([], "must be an object"),
    ],
)
def test_malformed_limits_are_refused(limits: Any, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        stage.check_limits(limits)


def test_parse_limits_overrides_defaults() -> None:
    assert runner.parse_limits(["nofile=1024", "as=8589934592"]) == {
        **stage.DEFAULT_LIMITS,
        "nofile": 1024,
        "as": 8589934592,
    }
    for bad in (["nofile"], ["nofile=-1"], ["nofile=1k"], ["stack=1"]):
        with pytest.raises(ValueError):
            runner.parse_limits(bad)


def test_apply_limits_only_lowers(monkeypatch: pytest.MonkeyPatch) -> None:
    current = {resource.RLIMIT_NOFILE: (1024, 1 << 20), resource.RLIMIT_CORE: (resource.RLIM_INFINITY,) * 2}
    set_to: dict[int, tuple[int, int]] = {}
    monkeypatch.setattr(stage.resource, "getrlimit", lambda which: current[which])
    monkeypatch.setattr(stage.resource, "setrlimit", lambda which, pair: set_to.__setitem__(which, pair))
    applied = stage._apply_limits({"nofile": 4096, "core": 0})
    # the soft limit is never raised, only capped by the new hard limit
    assert set_to[resource.RLIMIT_NOFILE] == (1024, 4096)
    assert set_to[resource.RLIMIT_CORE] == (0, 0)
    assert applied == {"core": [0, 0], "nofile": [1024, 4096]}


# --- namespaces and containment checks ------------------------------------------------------------


def test_the_stage_command_adds_uts_and_cgroup_namespaces() -> None:
    command = runner.stage_command(Path("/spec"), Path("/out"))
    flags = command[: command.index("--")]
    for flag in ("--net", "--pid", "--mount", "--ipc", "--uts", "--cgroup", "--kill-child"):
        assert flag in flags


def test_the_stage_refuses_to_set_a_host_name_in_the_runners_uts_namespace() -> None:
    if os.getpid() == 1:
        pytest.skip("this test process is a PID namespace init")
    with pytest.raises(RuntimeError, match="PID namespace"):
        stage._check_namespaces("mnt:[1]", os.readlink("/proc/self/ns/uts"))


def test_a_contained_stage_refuses_the_runners_root_file_system() -> None:
    root = os.stat("/")
    with pytest.raises(RuntimeError, match="runner's root file system"):
        stage._check_contained([root.st_dev, root.st_ino])
    with pytest.raises(RuntimeError):
        stage._check_contained(None)
    stage._check_contained([root.st_dev, root.st_ino + 1])  # another root passes


@pytest.mark.parametrize("name", ["", "x" * 65, None, 3])
def test_invalid_host_names_are_refused(name: Any) -> None:
    with pytest.raises(ValueError, match="invalid host name"):
        stage._set_hostname(name)


# --- the OCI backend's command line ---------------------------------------------------------------


def _oci(tmp_path: Path, **overrides: Any) -> list[str]:
    sandbox = runner.Sandbox(backend="oci", image=IMAGE, binds=("/opt/tools",), **overrides)
    run_dir = tmp_path / "fake-case-abc123"
    return runner.oci_command(
        run_dir / "control" / "spec.json",
        run_dir / "control" / "out.json",
        run_dir,
        tmp_path / "fakeproc",
        ROOT,
        sandbox,
    )


def _pairs(command: list[str], flag: str) -> list[str]:
    return [command[i + 1] for i, arg in enumerate(command) if arg == flag]


def test_the_container_is_locked_down(tmp_path: Path) -> None:
    command = _oci(tmp_path)
    assert command[:2] == ["docker", "run"]
    for flag in ("--rm", "--read-only"):
        assert flag in command
    assert _pairs(command, "--network") == ["none"]
    assert _pairs(command, "--pull") == ["never"]
    assert _pairs(command, "--cap-drop") == ["ALL"]
    assert _pairs(command, "--cap-add") == list(runner.OCI_CAPABILITIES)
    assert _pairs(command, "--security-opt") == ["no-new-privileges"]
    assert _pairs(command, "--hostname") == [stage.HOSTNAME]
    assert _pairs(command, "--memory") == _pairs(command, "--memory-swap") == ["4g"]
    assert _pairs(command, "--pids-limit") == ["1024"]
    assert {t.split(":", 1)[0] for t in _pairs(command, "--tmpfs")} == {"/tmp", "/var/tmp", "/run"}
    assert "--privileged" not in command and "--runtime" not in command
    assert command[command.index(IMAGE) + 1 :][:4] == ["python3", "-P", "-m", "tools.shadowbench.cases.stage"]


def test_only_the_run_directory_is_bound_writable(tmp_path: Path) -> None:
    mounts = _pairs(_oci(tmp_path), "--mount")
    writable = [m for m in mounts if not m.endswith(",readonly")]
    assert writable == [f"type=bind,src={tmp_path / 'fake-case-abc123'},dst={tmp_path / 'fake-case-abc123'}"]
    assert "type=bind,src=/opt/tools,dst=/opt/tools,readonly" in mounts
    assert f"type=bind,src={ROOT / 'tools'},dst={runner.HARNESS_MOUNT}/tools,readonly" in mounts


def test_gvisor_is_a_runtime_flag(tmp_path: Path) -> None:
    assert _pairs(_oci(tmp_path, runtime="runsc"), "--runtime") == ["runsc"]


@pytest.mark.parametrize("image", [None, "python:3.13-slim", "python@sha256:abc", f"python:3.13@{DIGEST}x"])
def test_an_image_not_pinned_by_digest_is_refused(tmp_path: Path, image: str | None) -> None:
    sandbox = runner.Sandbox(backend="oci", image=image)
    with pytest.raises(ValueError, match="pinned by digest"):
        runner.oci_command(tmp_path / "s", tmp_path / "o", tmp_path / "run", tmp_path / "f", ROOT, sandbox)
    problems, _ = runner.oci_problems(sandbox)
    assert problems and "pinned by digest" in problems[0]


def test_a_bind_path_docker_cannot_quote_is_refused(tmp_path: Path) -> None:
    sandbox = runner.Sandbox(backend="oci", image=IMAGE, binds=("/opt/a,b",))
    with pytest.raises(ValueError, match="cannot bind"):
        runner.oci_command(tmp_path / "s", tmp_path / "o", tmp_path / "run", tmp_path / "f", ROOT, sandbox)


def test_tool_binds_keep_existing_outermost_paths(tmp_path: Path) -> None:
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin" / "tool").write_text("", encoding="utf-8")
    other = Path(tempfile.mkdtemp())
    try:
        config = {
            "tools": {"a": {"bin": str(tmp_path / "bin" / "tool")}, "b": {"bin": str(other), "x": "/no/such"}}
        }
        env = ToolEnv(tmp_path, config)
        assert runner.tool_binds(env) == tuple(sorted([str(tmp_path.resolve()), str(other.resolve())]))
    finally:
        shutil.rmtree(other)


def test_describe_records_the_sandbox() -> None:
    assert runner.Sandbox().describe() == {
        "backend": "namespaces",
        "hostname": stage.HOSTNAME,
        "limits": stage.DEFAULT_LIMITS,
        "namespaces": list(runner.NAMESPACES),
    }
    oci = runner.Sandbox(backend="oci", image=IMAGE, runtime="runsc").describe()
    assert (oci["image"], oci["runtime"], oci["read_only_root"], oci["network"]) == (
        IMAGE,
        "runsc",
        True,
        "none",
    )


def test_a_timed_out_container_is_removed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    removed: list[str] = []

    class Hung:
        pid = os.getpid()

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
            raise subprocess.TimeoutExpired("docker", timeout or 0)

    monkeypatch.setattr(runner.subprocess, "Popen", Hung)
    monkeypatch.setattr(runner, "_kill_stage", lambda proc: None)
    monkeypatch.setattr(runner, "_remove_container", removed.append)
    run_dir = tmp_path / "fake-case-xyz"
    control = run_dir / "control"
    control.mkdir(parents=True)
    sandbox = runner.Sandbox(backend="oci", image=IMAGE)
    staged = runner._stage({"work": str(run_dir / "work"), "fakeproc": "/f"}, control, ROOT, 1, sandbox)
    assert "timed out" in staged["error"]
    assert removed == ["shadowbench-fake-case-xyz"]
    spec = json.loads((control / "stage_spec.json").read_text(encoding="utf-8"))
    assert spec["contained"] is True and spec["procbin"] == str(run_dir / "procbin")
    assert spec["limits"] == stage.DEFAULT_LIMITS and "hostname" not in spec


# --- the real stage -------------------------------------------------------------------------------


@functools.cache
def _namespaces_available() -> bool:
    if os.geteuid() != 0 or shutil.which("unshare") is None:
        return False
    return runner.namespace_problem() is None


@pytest.fixture
def run_dirs() -> Iterator[tuple[Path, Path]]:
    if not os.stat(tempfile.gettempdir()).st_mode & 0o001:
        pytest.skip("uid 65534 cannot traverse the temporary directory")
    scratch = Path(tempfile.mkdtemp(prefix="shadowbench-sandbox-"))
    scratch.chmod(0o711)
    run_dir = scratch / "fake-case-run"
    run_dir.mkdir(mode=0o711)
    run_dir.chmod(0o711)
    work, control = run_dir / "work", run_dir / "control"
    work.mkdir(mode=0o700)
    control.mkdir(mode=0o700)
    os.chown(work, 65534, 65534)
    try:
        yield work, control
    finally:
        subprocess.run(
            ["docker", "rm", "--force", runner.container_name(run_dir)], capture_output=True, check=False
        )
        shutil.rmtree(scratch, ignore_errors=True)


def _inv(work: Path, script: str) -> dict[str, Any]:
    env = {"PATH": TOOL_PATH, "HOME": str(work), "LANG": "C.UTF-8"}
    return {"argv": ["sh", "-c", script], "cwd": str(work), "env": env, "timeout": 30, "stdin": None}


PROBE = (
    "hostname; ulimit -c; ulimit -n; grep NoNewPrivs /proc/self/status | tr -d '\\t';"
    " grep CapEff /proc/self/status | tr -d '\\t'; cut -d: -f3 /proc/self/cgroup | sort -u | head -1"
)


@pytest.mark.skipif(not _namespaces_available(), reason="needs root and unshare with every stage namespace")
def test_the_stage_hides_the_host_name_and_lowers_limits(run_dirs: tuple[Path, Path]) -> None:
    work, control = run_dirs
    spec = {"services": [], "processes": [], "fakeproc": "/nonexistent", "work": str(work)}
    staged = runner._stage({**spec, "invocations": [_inv(work, PROBE)]}, control, ROOT, 60)
    assert staged["error"] is None, staged
    lines = staged["runs"][0]["stdout"].split()
    assert lines[:5] == [stage.HOSTNAME, "0", "4096", "NoNewPrivs:1", "CapEff:0000000000000000"]
    assert lines[5] == "/"  # the cgroup namespace's root, not the host's path
    assert staged["limits"]["core"] == [0, 0]


@pytest.mark.skipif(not _namespaces_available(), reason="needs root and unshare with every stage namespace")
def test_a_tool_that_writes_past_the_file_size_limit_fails(run_dirs: tuple[Path, Path]) -> None:
    work, control = run_dirs
    sandbox = runner.Sandbox(limits={**stage.DEFAULT_LIMITS, "fsize": 1 << 20})
    script = "head -c 2097152 /dev/zero > big; echo exit=$?"
    spec = {"services": [], "processes": [], "fakeproc": "/nonexistent", "work": str(work)}
    staged = runner._stage({**spec, "invocations": [_inv(work, script)]}, control, ROOT, 60, sandbox)
    assert staged["error"] is None, staged
    assert (work / "big").stat().st_size <= 1 << 20
    assert "exit=0" not in staged["runs"][0]["stdout"]


def _oci_image() -> str | None:
    image = os.environ.get("SHADOWBENCH_OCI_IMAGE")
    if not image or os.geteuid() != 0 or shutil.which("docker") is None:
        return None
    problems, _ = runner.oci_problems(runner.Sandbox(backend="oci", image=image))
    return None if problems else image


@pytest.mark.skipif(
    _oci_image() is None, reason="needs root, Docker and SHADOWBENCH_OCI_IMAGE (pinned, present)"
)
def test_the_contained_stage_runs_tools_unprivileged_on_a_read_only_root(
    run_dirs: tuple[Path, Path], tmp_path: Path
) -> None:
    work, control = run_dirs
    fakeproc = stage.build_fakeproc(work.parent.parent / "fakeproc")
    sandbox = runner.Sandbox(backend="oci", image=_oci_image())
    script = (
        "id -u; " + PROBE + "; touch /etc/x 2>/dev/null && echo root-rw || echo root-ro;"
        " ls /sys/class/net | tr '\\n' ' '; echo; touch made; grep -l ollama /proc/[0-9]*/cmdline | wc -l"
    )
    spec = {
        "services": [],
        "processes": [{"index": 0, "name": "ollama", "argv": ["ollama", "serve"]}],
        "fakeproc": str(fakeproc),
        "work": str(work),
        "invocations": [_inv(work, script)],
    }
    staged = runner._stage(spec, control, ROOT, 120, sandbox)
    assert staged["error"] is None, staged
    lines = staged["runs"][0]["stdout"].splitlines()
    assert lines[:6] == ["65534", stage.HOSTNAME, "0", "4096", "NoNewPrivs:1", "CapEff:0000000000000000"]
    assert lines[7] == "root-ro"
    assert lines[8].split() == ["lo"]
    assert int(lines[9]) >= 1  # the inert process is visible to the tool
    assert (work / "made").stat().st_uid == 65534
    assert staged["processes"][0]["name"] == "ollama"


def test_the_report_names_the_sandbox() -> None:
    from tools.shadowbench.cases import report

    manifest: dict[str, Any] = {"harness_commit": "a" * 40, "harness_dirty": False}
    assert "Tools ran" not in report.harness(manifest)
    manifest["isolation"] = runner.Sandbox().describe()
    assert "fresh namespaces (net, pid, mount, ipc, uts, cgroup)" in report.harness(manifest)
    manifest["isolation"] = runner.Sandbox(backend="oci", image=IMAGE, runtime="runsc").describe()
    sentence = report.harness(manifest)
    assert "gVisor" in sentence and IMAGE in sentence and "read-only root" in sentence
