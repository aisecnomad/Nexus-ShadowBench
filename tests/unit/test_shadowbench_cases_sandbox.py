"""Sandbox hardening of the cases runner: resource limits, UTS and cgroup namespaces, the OCI backend.

The tests that run the real stage need root and ``unshare`` (as in test_shadowbench_cases_runner.py);
the end-to-end OCI test also needs a reachable Docker daemon and ``SHADOWBENCH_OCI_IMAGE``, an image
pinned by digest and present locally that has ``python3`` (for example the ``python:3.13-slim``
image by digest).
"""

from __future__ import annotations

import ctypes
import errno
import functools
import json
import os
import resource
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import types
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

from tools.shadowbench.cases import mockserv, runner, stage
from tools.shadowbench.cases.adapters import _probe
from tools.shadowbench.cases.contract import ToolEnv
from tools.shadowbench.cases.corpus import load_corpus

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


def test_limit_pairs_hold_the_request_unless_the_host_hard_limit_is_lower(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    current = {
        resource.RLIMIT_NOFILE: (1024, 1 << 20),
        resource.RLIMIT_CORE: (resource.RLIM_INFINITY,) * 2,
        resource.RLIMIT_NPROC: (100, 100),
    }
    monkeypatch.setattr(stage.resource, "getrlimit", lambda which: current[which])
    monkeypatch.setattr(
        stage.resource, "setrlimit", lambda *a: pytest.fail("the stage must not limit itself")
    )
    pairs = stage.limit_pairs({"nofile": 4096, "core": 0, "nproc": 4096})
    # soft and hard alike: the manifest's requested value is what the tool runs with...
    assert pairs["nofile"] == [4096, 4096] and pairs["core"] == [0, 0]
    # ...unless the host's hard limit is lower, which the stage then reports
    assert pairs["nproc"] == [100, 100]


def test_limit_prefix_runs_prlimit_then_the_tool() -> None:
    prefix = stage.limit_prefix({"core": [0, 0], "nofile": [4096, 4096]})
    assert Path(prefix[0]).name == "prlimit"
    assert prefix[1:] == ["--core=0:0", "--nofile=4096:4096", "--"]
    assert stage.limit_prefix({}) == []


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
    sandbox = runner.Sandbox(backend="oci", image=IMAGE, binds=(("/data/tools", "/opt/tools"),), **overrides)
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
    assert "type=bind,src=/data/tools,dst=/opt/tools,readonly" in mounts
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
    sandbox = runner.Sandbox(backend="oci", image=IMAGE, binds=(("/opt/a,b", "/opt/a,b"),))
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
        expected = sorted([str(tmp_path), str(other)])
        assert runner.tool_binds(env) == tuple((os.path.realpath(p), p) for p in expected)
    finally:
        shutil.rmtree(other)


def test_tool_binds_show_a_symlinked_tool_root_at_its_configured_path(tmp_path: Path) -> None:
    """Binding only the resolved path left the configured paths the invocations use missing."""
    (tmp_path / "data" / "tools" / "bin").mkdir(parents=True)
    (tmp_path / "data" / "tools" / "bin" / "numbat").write_text("", encoding="utf-8")
    (tmp_path / "opt").symlink_to(tmp_path / "data")
    root = tmp_path / "opt" / "tools"
    env = ToolEnv(root, {"tools": {"numbat": {"bin": str(root / "bin" / "numbat")}}})
    real = os.path.realpath(root)
    # one bind: the binary sits where the tool root's bind already shows it
    assert runner.tool_binds(env) == ((real, str(root)),)


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


@pytest.mark.skipif(not _namespaces_available(), reason="needs root and unshare with every stage namespace")
def test_the_stage_writes_large_output_whatever_the_tools_file_size_limit(
    run_dirs: tuple[Path, Path],
) -> None:
    """The limits bound the stage itself, so a tool printing more than fsize turned into a stage error."""
    work, control = run_dirs
    sandbox = runner.Sandbox(limits={**stage.DEFAULT_LIMITS, "fsize": 1 << 20})
    script = "head -c 1572864 /dev/zero | tr '\\0' x"
    spec = {"services": [], "processes": [], "fakeproc": "/nonexistent", "work": str(work)}
    staged = runner._stage({**spec, "invocations": [_inv(work, script)]}, control, ROOT, 60, sandbox)
    assert staged["error"] is None, staged
    assert len(staged["runs"][0]["stdout"]) == 1572864
    assert staged["limits"]["fsize"] == [1 << 20, 1 << 20]


@pytest.mark.skipif(not _namespaces_available(), reason="needs root and unshare with every stage namespace")
def test_the_stage_masks_the_host_name_files(run_dirs: tuple[Path, Path]) -> None:
    """Setting the UTS name left /etc/hostname and /etc/hosts naming the operator's machine."""
    work, control = run_dirs
    script = (
        "cat /etc/hostname; grep -c shadowbench /etc/hosts; echo x > /etc/hostname 2>/dev/null || echo ro"
    )
    spec = {"services": [], "processes": [], "fakeproc": "/nonexistent", "work": str(work)}
    staged = runner._stage({**spec, "invocations": [_inv(work, script)]}, control, ROOT, 60)
    assert staged["error"] is None, staged
    lines = staged["runs"][0]["stdout"].split()
    if os.path.isfile("/etc/hostname"):
        assert lines[0] == stage.HOSTNAME
    assert "ro" in lines
    host = socket.gethostname()
    if host != stage.HOSTNAME and len(host) > 2:
        assert host not in staged["runs"][0]["stdout"]
    # the host's own files are untouched
    assert stage.HOSTNAME not in Path("/etc/hostname").read_text(encoding="utf-8") or host == stage.HOSTNAME


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
    assert "requested resource limits core=0" in report.harness(manifest)
    manifest["isolation"] = runner.Sandbox(backend="oci", image=IMAGE, runtime="runsc").describe()
    sentence = report.harness(manifest)
    assert "gVisor" in sentence and IMAGE in sentence and "read-only root" in sentence


def test_the_runner_refuses_a_host_without_every_stage_namespace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from tools.shadowbench.cases.corpus import Corpus, dump_corpus

    def refused(argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        assert "--uts" in argv and "--cgroup" in argv and kwargs["env"] == {"PATH": runner.SYSTEM_PATH}
        return subprocess.CompletedProcess(argv, 1, b"", b"unshare: unshare failed: Operation not permitted")

    monkeypatch.setattr(runner.subprocess, "run", refused)
    assert "Operation not permitted" in (runner.namespace_problem() or "")
    monkeypatch.setattr(runner.os, "geteuid", lambda: 0)
    monkeypatch.setattr(runner.shutil, "which", lambda name, path=None: f"/usr/bin/{name}")
    corpus = tmp_path / "corpus.json"
    dump_corpus(Corpus([], 1, "generator", "2026-10-11T00:00:00Z"), corpus)
    tools_json = tmp_path / "tools.json"
    tools_json.write_text(json.dumps({"tool_root": str(tmp_path), "tools": {}}), encoding="utf-8")
    argv = ["--corpus", str(corpus), "--tools", str(tools_json), "--out", str(tmp_path / "out")]
    assert runner.main(argv) == 2
    assert "the stage's namespaces are not available" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    ("item", "message"),
    [
        (f"fsize={1 << 64}", "beyond what the kernel can set"),
        (f"fsize={(1 << 64) - 1}", "beyond what the kernel can set"),
        ("nofile=0", "would stop every tool"),
        ("nproc=0", "would stop every tool"),
    ],
)
def test_limits_no_tool_could_run_under_are_refused_up_front(item: str, message: str) -> None:
    """An impossible --rlimit passed the preflight and then failed every case."""
    with pytest.raises(ValueError, match=message):
        runner.parse_limits([item])


# --- session keyring, host sockets, reclaimed files, mock services ---------------------------------


class _Libc:
    def __init__(self, rc: int, err: int = 0) -> None:
        self.rc, self.err, self.calls = rc, err, []

    def syscall(self, *args: Any) -> int:
        self.calls.append(tuple(getattr(a, "value", a) for a in args))
        ctypes.set_errno(self.err)
        return self.rc


@pytest.mark.parametrize(("rc", "err"), [(7, 0), (-1, errno.ENOSYS), (-1, errno.EPERM)])
def test_the_stage_leaves_the_session_keyring_or_finds_none_to_leave(
    monkeypatch: pytest.MonkeyPatch, rc: int, err: int
) -> None:
    fake = _Libc(rc, err)
    monkeypatch.setattr(stage, "_libc", lambda: fake)
    monkeypatch.setattr(stage.os, "uname", lambda: types.SimpleNamespace(machine="x86_64"))
    stage.new_session_keyring()
    assert fake.calls == [(250, 1, None)]


def test_a_keyring_the_stage_cannot_leave_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(stage, "_libc", lambda: _Libc(-1, errno.EDQUOT))
    with pytest.raises(OSError, match="KEYCTL_JOIN_SESSION_KEYRING"):
        stage.new_session_keyring()
    monkeypatch.setattr(stage.os, "uname", lambda: types.SimpleNamespace(machine="mips"))
    with pytest.raises(RuntimeError, match="no keyctl system call number"):
        stage.new_session_keyring()


_KEYRING_PROBE = """
import ctypes, os, sys
from tools.shadowbench.cases import stage
libc = ctypes.CDLL(None, use_errno=True)
nr = ctypes.c_long(stage._SYS_KEYCTL[os.uname().machine])
def keyctl(*args):
    return libc.syscall(nr, *(ctypes.c_long(a) for a in args))
before = keyctl(0, -3, 1)  # KEYCTL_GET_KEYRING_ID of the session keyring, created if absent
if before == -1:
    sys.exit(77)
stage.new_session_keyring()
after = keyctl(0, -3, 0)
print(before, after, keyctl(11, after, 0, 0))  # KEYCTL_READ with no buffer: the payload size
"""


def test_a_new_session_keyring_is_another_and_empty() -> None:
    done = subprocess.run(
        [sys.executable, "-c", _KEYRING_PROBE], cwd=ROOT, capture_output=True, text=True, check=False
    )
    if done.returncode == 77:
        pytest.skip("keyctl is not available here")
    assert done.returncode == 0, done.stderr
    before, after, size = (int(x) for x in done.stdout.split())
    assert after != before and size == 0


def test_the_stage_hides_host_service_sockets() -> None:
    """A UNIX socket on a path is reachable from any network namespace; these hold the host's."""
    assert {"/root", "/home", "/run", "/tmp/.X11-unix"} <= set(stage.HIDDEN)


@pytest.mark.skipif(not _namespaces_available(), reason="needs root and unshare with every stage namespace")
def test_the_stage_shows_tools_an_empty_run_directory(run_dirs: tuple[Path, Path]) -> None:
    work, control = run_dirs
    script = "ls -A /run /var/run | wc -w; cat /proc/self/stat > /dev/null && echo ok"
    spec = {"services": [], "processes": [], "fakeproc": "/nonexistent", "work": str(work)}
    staged = runner._stage({**spec, "invocations": [_inv(work, script)]}, control, ROOT, 60)
    assert staged["error"] is None, staged
    assert staged["runs"][0]["stdout"].split() == ["2", "ok"]  # the two "dir:" headers, no entries


def test_reclaimed_files_lose_group_and_other_write(tmp_path: Path) -> None:
    (tmp_path / "sub").mkdir()
    for path, mode in ((tmp_path / "report.json", 0o666), (tmp_path / "sub" / "tool", 0o4777)):
        path.write_text("{}")
        path.chmod(mode)
    assert runner._reclaim_tree(tmp_path) == 0
    assert stat.S_IMODE((tmp_path / "report.json").stat().st_mode) == 0o644
    assert stat.S_IMODE((tmp_path / "sub" / "tool").stat().st_mode) == 0o755


def _raw_request(port: int, head: bytes) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as conn:
        conn.sendall(head)
        conn.shutdown(socket.SHUT_WR)
        return conn.recv(4096)


@pytest.mark.parametrize(
    ("length", "status"),
    [
        (b"zz", b"400"),
        (b"-5", b"400"),
        (b"99999999999", b"400"),
        (str(mockserv.MAX_BODY + 1).encode(), b"413"),
    ],
)
def test_mock_services_refuse_bad_lengths_quietly(
    capfd: pytest.CaptureFixture[str], length: bytes, status: bytes
) -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    services = mockserv.Services([{"ip": "127.0.0.1", "port": port, "product": "ollama"}])
    try:
        services.start(timeout=5)
        reply = _raw_request(port, b"POST /api/generate HTTP/1.1\r\nContent-Length: " + length + b"\r\n\r\n")
    finally:
        services.stop()
    assert reply.split(b" ", 2)[1] == status
    assert capfd.readouterr().err == ""


# --- the answer key out of the tools' reach -------------------------------------------------------


def test_the_stage_tree_holds_exactly_what_the_stage_imports_and_only_root_reads_it(tmp_path: Path) -> None:
    """The stage ran with the whole checkout on PYTHONPATH (and the OCI backend bound all of tools/),
    so the generator and families that rebuild every label were in a tool's reach."""
    tree = runner.build_stage_tree(tmp_path)
    assert stat.S_IMODE(tree.stat().st_mode) == 0o700
    copied = sorted(p.relative_to(tree).as_posix() for p in tree.rglob("*") if p.is_file())
    assert copied == sorted(runner.STAGE_MODULES)
    probe = (
        "import json, sys; sys.path.insert(0, sys.argv[1]); import tools.shadowbench.cases.stage;"
        "print(json.dumps(sorted(m.__file__ for n, m in sys.modules.items() if n.split('.')[0] == 'tools')))"
    )
    done = subprocess.run(
        [sys.executable, "-I", "-c", probe, str(tree)], capture_output=True, text=True, check=True
    )
    loaded = sorted(Path(f).relative_to(tree).as_posix() for f in json.loads(done.stdout))
    assert loaded == sorted(runner.STAGE_MODULES)


def test_the_stage_tree_is_rebuilt_afresh(tmp_path: Path) -> None:
    tree = runner.build_stage_tree(tmp_path)
    (tree / "tools" / "stale.py").write_text("x = 1\n", encoding="utf-8")
    assert not (runner.build_stage_tree(tmp_path) / "tools" / "stale.py").exists()


def test_the_manifest_names_what_is_hidden_but_not_where() -> None:
    sandbox = runner.Sandbox(
        stage_tree="/scratch/harness", hide=(("checkout", "/home/u/repo"), ("corpus", "/c.json"))
    )
    described = sandbox.describe()
    assert described["hidden"] == ["checkout", "corpus"]
    assert described["stage_modules"] == list(runner.STAGE_MODULES)
    assert "/home/u/repo" not in json.dumps(described)


def test_a_scratch_directory_under_a_hidden_path_is_refused(tmp_path: Path) -> None:
    scratch = tmp_path / "out" / "scratch"
    scratch.mkdir(parents=True)
    problems = runner.isolation_problems(scratch, ToolEnv(Path("/opt/nsb"), {}), [str(tmp_path / "out")])
    assert any("which the stage hides from tools" in p for p in problems)


@pytest.mark.parametrize("hide", [["relative/path"], "/not/a/list", [7]])
def test_the_stage_covers_only_absolute_paths(tmp_path: Path, hide: Any) -> None:
    with pytest.raises(ValueError, match="absolute paths"):
        stage._cover(hide, tmp_path)


def test_case_json_and_the_run_directory_name_no_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = next(
        c for c in load_corpus(ROOT / "benchmarks/shadowbench/cases/corpus.json").cases if not c.checkout
    )
    mat = runner.materialize(case, tmp_path / "case")
    assert "id" not in json.loads((mat.root / "case.json").read_text(encoding="utf-8"))
    names: list[str] = []
    real = runner.tempfile.mkdtemp

    def spy(*args: Any, **kwargs: Any) -> str:
        path = real(*args, **kwargs)
        names.append(Path(path).name)
        return path

    def broken(*_: Any) -> Any:
        raise RuntimeError("no invocations")

    monkeypatch.setattr(runner.tempfile, "mkdtemp", spy)
    adapter = types.SimpleNamespace(name="t", invocations=broken)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    row = runner.run_one(adapter, case, ToolEnv(tmp_path, {}), scratch, ROOT, tmp_path / "fakeproc", None)
    assert row["status"] == "error" and len(names) == 1
    assert names[0].startswith("run-") and case.case_id not in names[0] and "t-" not in names[0]


@pytest.mark.skipif(not _namespaces_available(), reason="needs root and unshare with every stage namespace")
def test_tools_see_neither_the_checkout_nor_the_results_nor_the_corpus(run_dirs: tuple[Path, Path]) -> None:
    """A checkout under /home was hidden already; one under /opt or /srv showed tools the corpus,
    and the results and a corpus kept elsewhere were readable wherever they were."""
    work, control = run_dirs
    scratch = work.parents[1]
    tree = runner.build_stage_tree(scratch)
    outside = Path(tempfile.mkdtemp(prefix="shadowbench-answers-"))
    try:
        outside.chmod(0o755)
        checkout, results, corpus = outside / "checkout", outside / "results", outside / "corpus.json"
        for directory in (checkout, results):
            directory.mkdir(mode=0o755)
        files = {
            checkout / "corpus.json": '{"cases": []}\n',
            results / "t.jsonl": '{"label": "agent"}\n',
            corpus: '{"cases": []}\n',
            outside / "visible.txt": "seen\n",
        }
        for path, text in files.items():
            path.write_text(text, encoding="utf-8")
            path.chmod(0o644)
        hide = (("checkout", str(checkout)), ("results", str(results)), ("corpus", str(corpus)))
        sandbox = runner.Sandbox(stage_tree=str(tree), hide=(("checkout", str(ROOT)), *hide))
        script = (
            f"cat {outside}/visible.txt; ls -A {checkout} | wc -l; ls -A {results} | wc -l; wc -c < {corpus};"
            f" ls -A {ROOT} | wc -l;"
            f" cat {tree}/tools/shadowbench/cases/stage.py >/dev/null 2>&1 && echo tree-readable || echo tree-private"
        )
        spec = {"services": [], "processes": [], "fakeproc": "/nonexistent", "work": str(work)}
        staged = runner._stage({**spec, "invocations": [_inv(work, script)]}, control, ROOT, 60, sandbox)
    finally:
        shutil.rmtree(outside, ignore_errors=True)
    assert staged["error"] is None, staged  # and it ran from the tree: PYTHONPATH named nothing else
    assert staged["runs"][0]["stdout"].split() == ["seen", "0", "0", "0", "0", "tree-private"]


def test_the_container_gets_the_stage_tree_not_the_harness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[list[str]] = []

    class Popen:
        pid = 0
        returncode = 1

        def __init__(self, command: list[str], **_: Any) -> None:
            seen.append(command)

        def communicate(self, timeout: float | None = None) -> tuple[bytes, bytes]:
            return b"", b""

    monkeypatch.setattr(runner.subprocess, "Popen", Popen)
    tree = runner.build_stage_tree(tmp_path)
    run_dir = tmp_path / "run-x"
    (run_dir / "control").mkdir(parents=True)
    sandbox = runner.Sandbox(backend="oci", image=IMAGE, stage_tree=str(tree))
    spec = {
        "services": [],
        "processes": [],
        "fakeproc": str(tmp_path / "fakeproc"),
        "work": str(run_dir / "work"),
    }
    runner._stage({**spec, "invocations": []}, run_dir / "control", ROOT, 5, sandbox)
    mounts = [arg for arg in seen[0] if arg.startswith("type=bind")]
    assert f"type=bind,src={tree / 'tools'},dst={runner.HARNESS_MOUNT}/tools,readonly" in mounts
    assert not any(f"src={ROOT}" in arg for arg in mounts)


# --- review fixes: a ShadowScan checkout, probes, symlinked tool paths, main's wiring ---------------


def _shadowscan_checkout(tmp_path: Path) -> tuple[Path, Path]:
    checkout = tmp_path / "Project-Nexus"
    for entry in ("shadowscan", "benchmarks/shadowbench/cases", "tools", ".git", ".venv/bin"):
        (checkout / entry).mkdir(parents=True)
    (checkout / "benchmarks/shadowbench/cases/corpus.json").write_text("{}\n", encoding="utf-8")
    (checkout / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    python = checkout / ".venv/bin/python"
    python.write_text("", encoding="utf-8")
    return checkout, python


def test_a_shadowscan_checkout_shows_tools_only_its_package_and_the_paths_tools_json_names(
    tmp_path: Path,
) -> None:
    """The checkout ShadowScan runs from is the repository this benchmark came from: its benchmarks/
    and tools/ hold the corpus and generator, on ShadowScan's PYTHONPATH and in every tool's reach."""
    checkout, python = _shadowscan_checkout(tmp_path)
    env = ToolEnv(tmp_path / "tools", {"tools": {"shadowscan": {"bin": str(python), "repo": str(checkout)}}})
    hidden = runner.checkout_answer_keys(env)
    assert sorted(Path(p).name for p in hidden) == [".git", "benchmarks", "pyproject.toml", "tools"]
    binds = {dst: src for src, dst in runner.tool_binds(env)}
    assert str(checkout / "shadowscan") in binds and str(checkout) not in binds  # OCI: the package only
    assert (
        runner.checkout_answer_keys(ToolEnv(tmp_path, {"tools": {"shadowscan": {"repo": "relative"}}})) == ()
    )


def test_a_tool_path_that_only_resolves_out_of_a_hidden_tree_is_refused(tmp_path: Path) -> None:
    """A venv's python is a symlink out of the checkout; the stage still runs it at its configured path."""
    hidden_tree = tmp_path / "checkout"
    (hidden_tree / ".venv/bin").mkdir(parents=True)
    python = hidden_tree / ".venv/bin/python"
    python.symlink_to(sys.executable)
    env = ToolEnv(tmp_path / "tools", {"tools": {"x": {"bin": str(python)}}})
    scratch = tmp_path / "scratch"
    scratch.mkdir(mode=0o711)
    problems = runner.isolation_problems(scratch, env, [str(hidden_tree)])
    assert any(f"tools.x.bin = {python}" in p and "which the stage hides" in p for p in problems)


@pytest.mark.skipif(os.geteuid() != 0 or shutil.which("unshare") is None, reason="needs root and unshare")
def test_probes_hide_what_the_stage_hides(monkeypatch: pytest.MonkeyPatch) -> None:
    """A version probe runs the tool's code outside the stage: it read the corpus the stage now hides."""
    top = Path(tempfile.mkdtemp(prefix="shadowbench-probe-hide-"))  # uid 65534 cannot reach tmp_path
    try:
        top.chmod(0o755)
        secret_dir, secret_file = top / "checkout", top / "corpus.json"
        secret_dir.mkdir(mode=0o755)
        (secret_dir / "labels.json").write_text("{}\n", encoding="utf-8")
        secret_file.write_text('{"cases": []}\n', encoding="utf-8")
        for path in (secret_dir / "labels.json", secret_file):
            path.chmod(0o644)
        script = f"ls -A {secret_dir} | wc -l; wc -c < {secret_file}"
        monkeypatch.setattr(_probe, "HIDE", ())
        seen = _probe.run_probe(["sh", "-c", script])
        assert seen is not None and seen.stdout.split() == ["1", "14"], seen
        monkeypatch.setattr(_probe, "HIDE", (str(secret_dir), str(secret_file), str(top / "missing")))
        hidden = _probe.run_probe(["sh", "-c", script])
        assert hidden is not None and hidden.stdout.split() == ["0", "0"], hidden
    finally:
        shutil.rmtree(top, ignore_errors=True)


def test_main_hides_the_checkout_results_corpus_and_shadowscan_checkout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The real-stage tests built their own Sandbox, so main() could drop the hide list unnoticed."""
    checkout, python = _shadowscan_checkout(tmp_path)
    seen: dict[str, Any] = {}

    def isolation(scratch: Path, env: ToolEnv, hide: Any = ()) -> list[str]:
        seen["hide"] = list(hide)
        return []

    def run_tool(*args: Any) -> dict[str, Any]:
        seen["sandbox"] = args[-1]
        return {"statuses": {}}

    monkeypatch.setattr(runner.os, "geteuid", lambda: 0)
    monkeypatch.setattr(runner.shutil, "which", lambda name, path=None: f"/usr/bin/{name}")
    monkeypatch.setattr(runner, "namespace_problem", lambda: None)
    monkeypatch.setattr(runner, "new_session_keyring", lambda: None)
    monkeypatch.setattr(runner, "build_fakeproc", lambda path: path)
    monkeypatch.setattr(runner, "isolation_problems", isolation)
    monkeypatch.setattr(runner, "run_tool", run_tool)
    monkeypatch.setattr(runner, "tool_version", lambda adapter, env: "test")
    monkeypatch.setattr(_probe, "HIDE", ())
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        (ROOT / "benchmarks/shadowbench/cases/corpus.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    tools_json = tmp_path / "tools.json"
    config = {
        "tool_root": str(tmp_path / "tools"),
        "tools": {"shadowscan": {"bin": str(python), "repo": str(checkout)}},
    }
    tools_json.write_text(json.dumps(config), encoding="utf-8")
    out = tmp_path / "out"
    argv = ["--corpus", str(corpus), "--tools", str(tools_json), "--out", str(out), "--only", "shadowscan"]
    assert runner.main([*argv, "--cases", "none", "--scratch", str(tmp_path / "scratch")]) == 0
    isolation_record = json.loads((out / "manifest.json").read_text(encoding="utf-8"))["isolation"]
    assert isolation_record["hidden"] == ["checkout", "results", "corpus", "ShadowScan checkout"]
    assert isolation_record["stage_modules"] == list(runner.STAGE_MODULES)
    expected = [
        str(ROOT),
        str(out.resolve()),
        str(corpus.resolve()),
        *runner.checkout_answer_keys(runner.ToolEnv.load(tools_json)),
    ]
    assert seen["hide"] == expected and list(_probe.HIDE) == expected
    assert str(checkout / "benchmarks") in expected and str(checkout / ".venv") not in expected
    assert seen["sandbox"].stage_tree is not None


def test_a_container_bind_that_holds_the_answer_key_is_refused(tmp_path: Path) -> None:
    checkout = tmp_path / "checkout"
    (checkout / "benchmarks").mkdir(parents=True)
    binds = ((str(tmp_path), "/opt/tools"), (str(tmp_path / "elsewhere"), "/opt/x"))
    problems = runner.exposed_answer_keys(binds, [str(checkout / "benchmarks")])
    assert problems == [
        f"/opt/tools would show tools {checkout / 'benchmarks'} in the container; keep tool paths outside it"
    ]
    assert runner.exposed_answer_keys(binds[1:], [str(checkout)]) == []


@pytest.mark.skipif(os.geteuid() != 0 or shutil.which("unshare") is None, reason="needs root and unshare")
def test_a_probe_skips_hidden_paths_already_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    """A path nested in an earlier one, or under /home, had no mount point left: the mount failed and
    every probed version read unknown."""
    top = Path(tempfile.mkdtemp(prefix="shadowbench-probe-nested-"))
    try:
        top.chmod(0o755)
        (top / "repo/results").mkdir(parents=True)
        (top / "repo/corpus.json").write_text("{}\n", encoding="utf-8")
        hide = (
            str(top / "repo"),
            str(top / "repo/results"),
            str(top / "repo/corpus.json"),
            str(ROOT),
            "/home/x/y",
        )
        monkeypatch.setattr(_probe, "HIDE", hide)
        done = _probe.run_probe(["sh", "-c", f"echo ok; ls -A {top / 'repo'} | wc -l"])
        assert done is not None and done.returncode == 0 and done.stdout.split() == ["ok", "0"], done
    finally:
        shutil.rmtree(top, ignore_errors=True)


@pytest.mark.skipif(os.geteuid() != 0 or shutil.which("unshare") is None, reason="needs root and unshare")
def test_a_probe_hands_the_runner_only_the_head_of_what_it_prints(monkeypatch: pytest.MonkeyPatch) -> None:
    """capture_output held all of a probing binary's output in the root runner."""
    monkeypatch.setattr(_probe, "HIDE", ())
    flood = "import sys\nfor _ in range(4096): sys.stdout.write('v1.2.3 ' * 2000)\nsys.stderr.write('warn')"
    python = shutil.which("python3", path="/usr/bin:/bin")  # the venv's lies under the hidden /home
    if python is None:
        pytest.skip("no system python3")
    done = _probe.run_probe([python, "-c", flood])
    assert done is not None and done.returncode != 0  # the 2 MiB tmpfs filled
    assert len(done.stdout) == _probe.PROBE_OUTPUT_KEEP and done.stdout.startswith("v1.2.3 ")
    ok = _probe.run_probe(["sh", "-c", "echo v9.9.9; echo note >&2; exit 3"])
    assert ok is not None and (ok.returncode, ok.stdout, ok.stderr) == (3, "v9.9.9\n", "note\n")


def test_a_tool_path_through_a_symlinked_parent_into_a_hidden_tree_is_refused(tmp_path: Path) -> None:
    hidden_tree = tmp_path / "checkout"
    (hidden_tree / "venv/bin").mkdir(parents=True)
    (hidden_tree / "venv/bin/tool").write_text("", encoding="utf-8")
    (tmp_path / "opt").symlink_to(hidden_tree / "venv")
    env = ToolEnv(tmp_path / "tools", {"tools": {"x": {"bin": str(tmp_path / "opt/bin/tool")}}})
    scratch = tmp_path / "scratch"
    scratch.mkdir(mode=0o711)
    problems = runner.isolation_problems(scratch, env, [str(hidden_tree)])
    assert any("tools.x.bin" in p and "which the stage hides" in p for p in problems)


def test_a_shadowscan_checkout_inside_a_bound_tool_root_is_refused_for_the_container(tmp_path: Path) -> None:
    """tool_binds bound the package alone, but tool_root, which holds the checkout, whole."""
    root = tmp_path / "tools"
    checkout = root / "Project-Nexus"
    for entry in ("shadowscan", "benchmarks"):
        (checkout / entry).mkdir(parents=True)
    env = ToolEnv(root, {"tool_root": str(root), "tools": {"shadowscan": {"repo": str(checkout)}}})
    problems = runner.exposed_answer_keys(runner.tool_binds(env), runner.checkout_answer_keys(env))
    assert any(str(checkout / "benchmarks") in p for p in problems)


# --- the stage keeps only the tail of what a tool prints -------------------------------------------

_FLOOD = """
import json, sys
from tools.shadowbench.cases import stage
code = "import sys\\nline = b'x' * 1023 + b'\\\\n'\\nfor _ in range(300_000): sys.stdout.buffer.write(line)\\nprint('END')"
inv = {"argv": [sys.executable, "-c", code], "cwd": "/", "env": {"PATH": "/usr/bin:/bin"}, "timeout": 120, "stdin": None}
result = stage._run(inv)
# VmHWM, not ru_maxrss: Linux carries ru_maxrss across execve, so it would report the test runner's peak
hwm = next(int(line.split()[1]) for line in open("/proc/self/status") if line.startswith("VmHWM:"))
print(json.dumps({"rss_mib": hwm // 1024,
                  "len": len(result["stdout"]), "end": result["stdout"][-4:], "code": result["code"]}))
"""


def test_a_flood_of_output_is_kept_as_its_tail_in_bounded_memory() -> None:
    """communicate() held all 300 MB a tool printed in the root stage's memory before cutting it."""
    done = subprocess.run(
        [sys.executable, "-c", _FLOOD], cwd=ROOT, capture_output=True, text=True, timeout=300
    )
    assert done.returncode == 0, done.stderr
    result = json.loads(done.stdout)
    assert result["code"] == 0 and result["end"] == "END\n" and result["len"] == stage.STDOUT_KEEP
    assert result["rss_mib"] < 150, result  # the tail is at most 16 MB; 300 MB arrived


def test_stdin_is_fed_and_both_streams_are_kept(tmp_path: Path) -> None:
    inv = {"argv": ["sh", "-c", "cat; echo oops >&2"], "cwd": str(tmp_path), "env": {"PATH": TOOL_PATH}}
    result = stage._run({**inv, "timeout": 30, "stdin": "hello\n"})
    assert (result["code"], result["stdout"], result["stderr"], result["timed_out"]) == (
        0,
        "hello\n",
        "oops\n",
        False,
    )


def test_a_child_left_holding_the_pipes_still_makes_the_run_a_timeout(tmp_path: Path) -> None:
    """As with communicate's timeout: the tool exited at once, but its child kept stdout open."""
    inv = {"argv": ["sh", "-c", "sleep 30 & echo started"], "cwd": str(tmp_path), "env": {"PATH": TOOL_PATH}}
    result = stage._run({**inv, "timeout": 1, "stdin": None})
    assert (result["code"], result["timed_out"], result["stdout"]) == (124, True, "started\n")
    assert result["seconds"] < 1 + 2 * stage.KILL_GRACE
