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


# --- the stage keeps only the tail of what a tool prints -------------------------------------------

_FLOOD = """
import json, resource, sys
from tools.shadowbench.cases import stage
code = "import sys\\nline = b'x' * 1023 + b'\\\\n'\\nfor _ in range(300_000): sys.stdout.buffer.write(line)\\nprint('END')"
inv = {"argv": [sys.executable, "-c", code], "cwd": "/", "env": {"PATH": "/usr/bin:/bin"}, "timeout": 120, "stdin": None}
result = stage._run(inv)
print(json.dumps({"rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024,
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
