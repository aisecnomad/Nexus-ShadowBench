"""The isolated stage: what runs inside the namespaces for one adapter on one case.

``python -m tools.shadowbench.cases.stage SPEC.json OUT.json``

The runner starts this module as root under ``unshare --net --pid --fork
--kill-child --mount --mount-proc --ipc --uts --cgroup`` so the tool sees no
network, no host processes, no host System V IPC or POSIX message queues, a
private mount table, its own host name and its own cgroup root. Before
anything from the case runs, the stage checks that it is the init of that
fresh PID namespace and in neither the runner's mount nor (when the spec names
it) the runner's UTS namespace, sets ``no_new_privs``, sets the host name to
the spec's ``hostname`` and binds read-only files naming it over
``/etc/hostname`` and ``/etc/hosts`` so no tool records the operator's, brings
loopback up, joins a new, empty session keyring so no tool reaches the
runner's keys, mounts an empty tmpfs over ``/root`` and ``/home`` so the
operator's homes and credentials are out of sight and over ``/run`` and
``/tmp/.X11-unix`` so no host service's UNIX socket (the D-Bus system bus,
systemd-resolved, nscd, an X server) offers a way around the empty network
namespace, mounts a
fresh, empty, world-writable tmpfs over ``/var/tmp`` and ``/dev/shm`` so
nothing a tool leaves there outlives the case, and leaves the directory it was
started in for ``/``, so no process it starts inherits a working directory
under a hidden path. It then serves the case's mock services, spawns the
case's inert processes under their declared names and command lines, runs the
adapter's invocations in order, each under the spec's resource limits
(``limits``; see ``LIMITS``), set by ``prlimit`` in the tool's own process so
the stage and its mock services are never bound by them, and writes their
results, the pid each process got and the limits that held. The cgroup
namespace makes ``/proc/self/cgroup`` relative to the stage; ``/sys/fs/cgroup``
is not remounted.

A spec marked ``contained`` comes from the runner's OCI backend: the stage is
then the init of a container started from a digest-pinned image, with a
read-only root file system, fresh tmpfs mounts, its own host name and only the
capabilities the stage needs (see ``runner.oci_command``). The container's
root file system holds no operator home and its temporary directories are
already private, so the stage mounts nothing and leaves the host name to the
container; every other step is the same.

Tools run as the unprivileged identity the spec names (the runner passes
uid/gid 65534 with no supplementary groups) with exactly the environment
their invocation declares and nothing inherited. Inert processes run as the
same identity with a fixed minimal environment and the work directory as
their working directory, so a process scanner sees them as it would see its
own user's processes (``/proc/<pid>/exe``, ``environ``, ``cwd``) and reaches
nothing through them that it could not reach itself. Only the stage itself,
the mock services and the namespace setup keep root. After each invocation,
and on a timeout, every process in the namespace is stopped with one
``kill(-1, SIGSTOP)``, which the kernel also delivers to a child forked
meanwhile, then everything but the stage and the inert processes is killed
and reaped, including descendants that left the tool's process group with
``setsid``, and the inert processes are continued. A process still alive
after that is an error for the case, never a silent leftover.

Under ``unshare`` this is not a filesystem sandbox: a tool can still read
whatever is world-readable outside the hidden paths, and the host's ``/tmp``,
which usually holds the scratch directory, stays shared with the host and with
other cases, including any UNIX socket another host process left there. The
OCI backend closes that: the container sees only its image, its own tmpfs
mounts and the run directory, harness and tool trees the runner binds into it,
the tool trees read-only.
"""

from __future__ import annotations

import ctypes
import errno
import fcntl
import functools
import json
import os
import resource
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from tools.shadowbench.cases.contract import SYSTEM_PATH
from tools.shadowbench.cases.mockserv import Services

FAKEPROC_C = r"""
#include <signal.h>
#include <unistd.h>
int main(void) { for (;;) pause(); return 0; }
"""

HIDDEN: tuple[str, ...] = ("/root", "/home", "/run", "/tmp/.X11-unix")
"""Operator home directories, and the directories holding host services' UNIX sockets (a socket on
a path is reachable from any network namespace), that the stage covers with an empty tmpfs."""
PRIVATE_TMP: tuple[str, ...] = ("/var/tmp", "/dev/shm")
"""Shared temporary directories the stage replaces with a fresh, world-writable tmpfs for each case."""
INERT_ENV: dict[str, str] = {"PATH": SYSTEM_PATH, "LANG": "C.UTF-8"}
"""The whole environment of an inert process; nothing is inherited from the stage."""
KILL_GRACE = 3.0
"""Seconds to collect a killed invocation's output before its pipes are closed."""
SWEEP_GRACE = 5.0
"""Seconds a killed stray may take to exit before the stage reports the case as an error."""

HOSTNAME = "shadowbench"
"""The host name tools see in the stage's UTS namespace, in place of the operator's."""
LIMITS: dict[str, int] = {
    "core": resource.RLIMIT_CORE,
    "cpu": resource.RLIMIT_CPU,
    "fsize": resource.RLIMIT_FSIZE,
    "nofile": resource.RLIMIT_NOFILE,
    "nproc": resource.RLIMIT_NPROC,
    "as": resource.RLIMIT_AS,
}
"""Resource limits a spec may set, by name, applied to each tool invocation (not to the stage or the
inert processes) as soft and hard limit alike. ``nproc`` counts every process of the tools' uid on
the host, so it bounds a fork bomb rather than one case; ``as`` and ``cpu`` are off by default
because language runtimes reserve address space they never touch, and the invocation timeouts bound
time."""
MAX_LIMIT = 1 << 63
"""Limits at or above this cannot be set as a finite value (``rlim_t`` is 64 bits, and the top values
mean unlimited); leave a limit out instead of asking for unlimited."""
DEFAULT_LIMITS: dict[str, int] = {"core": 0, "fsize": 4 << 30, "nofile": 4096, "nproc": 4096}
"""No core dumps (they would copy a tool's memory into the work tree), files up to 4 GiB, 4096 open
files and 4096 processes of the tools' uid. A tool that exceeds one fails, which scores as an error."""

_MS_NOSUID, _MS_NODEV, _MS_NOEXEC = 0x2, 0x4, 0x8
_PR_SET_NO_NEW_PRIVS = 38
_SYS_KEYCTL = {"x86_64": 250, "aarch64": 219}
_KEYCTL_JOIN_SESSION_KEYRING = 1


def build_fakeproc(path: Path) -> Path:
    """Compile the inert binary once; it ignores its arguments and sleeps until killed."""
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    src = path.with_suffix(".c")
    src.write_text(FAKEPROC_C, encoding="utf-8")
    subprocess.run(["gcc", "-O2", "-static", "-o", str(path), str(src)], check=True, capture_output=True)
    return path


@functools.cache
def _libc() -> ctypes.CDLL:
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mount.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_char_p]
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
    return libc


def _check_call(rc: int, what: str) -> None:
    if rc != 0:
        err = ctypes.get_errno()
        raise OSError(err, f"{what}: {os.strerror(err)}")


def _tool_identity(spec: dict[str, Any]) -> tuple[int, int]:
    """The unprivileged (uid, gid) tools run as; a spec without one never runs a tool as root."""
    ids = spec.get("run_as")
    if (
        not isinstance(ids, list)
        or len(ids) != 2
        or not all(isinstance(i, int) and not isinstance(i, bool) and i > 0 for i in ids)
    ):
        raise ValueError(f"spec names no unprivileged identity to run tools as: {ids!r}")
    return ids[0], ids[1]


def _check_namespaces(host_mnt_ns: object, host_uts_ns: object = None) -> None:
    """Refuse to touch mounts, the host name or processes unless this is a fresh PID and mount
    namespace and, when the runner names its UTS namespace, a fresh UTS namespace too."""
    if os.getpid() != 1:
        raise RuntimeError("the stage is not the init of a fresh PID namespace")
    if not isinstance(host_mnt_ns, str) or os.readlink("/proc/self/ns/mnt") == host_mnt_ns:
        raise RuntimeError("the stage shares the runner's mount namespace; refusing to mount over host paths")
    if host_uts_ns is not None and (
        not isinstance(host_uts_ns, str) or os.readlink("/proc/self/ns/uts") == host_uts_ns
    ):
        raise RuntimeError("the stage shares the runner's UTS namespace; refusing to set the host name")


def _check_contained(host_root: object) -> None:
    """Refuse to skip the mounts unless ``/`` is not the runner's root file system.

    The runner records the device and inode of its own ``/`` in a contained spec; a stage that sees
    the same root was not started in a container, and hiding the operator's homes is then its job.
    """
    root = os.stat("/")
    if not isinstance(host_root, list) or len(host_root) != 2 or [root.st_dev, root.st_ino] == host_root:
        raise RuntimeError("a contained stage sees the runner's root file system; refusing to run unmounted")


def check_limits(limits: object) -> dict[str, int]:
    """``limits`` as ``{name: value}`` with known names and non-negative integer values, or raise."""
    if not isinstance(limits, dict):
        raise ValueError(f"limits must be an object, not {limits!r}")
    for name, value in limits.items():
        if name not in LIMITS:
            raise ValueError(f"unknown resource limit {name!r}; known: {', '.join(sorted(LIMITS))}")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"resource limit {name} must be a non-negative integer, not {value!r}")
        if value >= MAX_LIMIT:
            raise ValueError(f"resource limit {name}={value} is beyond what the kernel can set")
        if value == 0 and name in ("nofile", "nproc"):
            raise ValueError(f"resource limit {name}=0 would stop every tool from starting")
    return dict(limits)


def limit_pairs(limits: dict[str, int]) -> dict[str, list[int]]:
    """``[soft, hard]`` per limit as tools get it: both the requested value, unless this process's
    hard limit is lower, which no unprivileged process can exceed."""
    pairs: dict[str, list[int]] = {}
    for name, value in sorted(check_limits(limits).items()):
        hard = resource.getrlimit(LIMITS[name])[1]
        held = value if hard == resource.RLIM_INFINITY else min(hard, value)
        pairs[name] = [held, held]
    return pairs


def limit_prefix(pairs: dict[str, list[int]]) -> list[str]:
    """The ``prlimit`` command line that sets ``pairs`` on a tool and then executes it.

    The limits are set in the tool's own process, after the drop to its uid and before its program
    runs, so the stage, its mock services and its result file are never bound by them; ``no_new_privs``
    keeps a setuid program from raising them again. An empty ``pairs`` sets nothing.
    """
    if not pairs:
        return []
    prlimit = shutil.which("prlimit", path=SYSTEM_PATH)
    if prlimit is None:
        raise RuntimeError(f"prlimit (util-linux) is not on {SYSTEM_PATH}; tools cannot be limited")
    return [prlimit, *(f"--{name}={soft}:{hard}" for name, (soft, hard) in sorted(pairs.items())), "--"]


HOST_FILES: dict[str, str] = {
    "/etc/hostname": "{name}\n",
    "/etc/hosts": "127.0.0.1\tlocalhost\n127.0.1.1\t{name}\n::1\tlocalhost ip6-localhost ip6-loopback\n",
}
"""Files that name the host on the shared root file system, and what tools see in their place."""

_MS_RDONLY, _MS_REMOUNT, _MS_BIND = 0x1, 0x20, 0x1000


def _mask_host_files(name: str, scratch: Path) -> None:
    """Bind read-only files naming ``name`` over :data:`HOST_FILES`; only in a private mount namespace.

    ``scratch`` is the root-only control directory: tools cannot reach the sources there, only the
    read-only mounts.
    """
    for target, template in HOST_FILES.items():
        if not os.path.isfile(target):
            continue
        source = scratch / f"masked-{Path(target).name}"
        source.write_text(template.format(name=name), encoding="utf-8")
        source.chmod(0o644)
        rc = _libc().mount(os.fsencode(source), os.fsencode(target), None, _MS_BIND, None)
        _check_call(rc, f"bind {source} over {target}")
        flags = _MS_REMOUNT | _MS_BIND | _MS_RDONLY
        _check_call(
            _libc().mount(None, os.fsencode(target), None, flags, None), f"remount {target} read-only"
        )


def _set_hostname(name: object) -> None:
    """Set the host name; only call this in a fresh UTS namespace (``_check_namespaces``)."""
    if not isinstance(name, str) or not name or len(name) > 64:
        raise ValueError(f"invalid host name {name!r}")
    socket.sethostname(name)


def new_session_keyring() -> None:
    """Join a new, empty, anonymous session keyring, which every process started from here on inherits.

    A uid change keeps the session keyring, and a process possessing it keeps the possessor's rights
    to its keys, so a tool dropped to 65534 could otherwise read the keys of the session the runner
    was started in (Kerberos caches, fscrypt or network file system credentials). Without key
    support in the kernel (ENOSYS), or under a seccomp filter that refuses keyctl (EPERM, as Docker's
    default does) and binds every child too, there is no keyring for a tool to reach.
    """
    number = _SYS_KEYCTL.get(os.uname().machine)
    if number is None:
        raise RuntimeError(f"no keyctl system call number is known for {os.uname().machine}")
    join = ctypes.c_long(_KEYCTL_JOIN_SESSION_KEYRING)
    if _libc().syscall(ctypes.c_long(number), join, ctypes.c_void_p()) == -1:
        err = ctypes.get_errno()
        if err not in (errno.ENOSYS, errno.EPERM):
            raise OSError(err, f"keyctl(KEYCTL_JOIN_SESSION_KEYRING): {os.strerror(err)}")


def _no_new_privs() -> None:
    """Make setuid binaries and file capabilities inert for every process started from here on."""
    _check_call(_libc().prctl(_PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0), "prctl(PR_SET_NO_NEW_PRIVS)")


def _hide(paths: tuple[str, ...]) -> None:
    """Mount an empty, root-owned tmpfs over each path; only call this in a private mount namespace."""
    flags = _MS_NOSUID | _MS_NODEV | _MS_NOEXEC
    for path in paths:
        if not os.path.isdir(path):
            continue
        rc = _libc().mount(b"tmpfs", os.fsencode(path), b"tmpfs", flags, b"mode=0755,size=64k")
        _check_call(rc, f"mount tmpfs on {path}")
        if os.listdir(path):
            raise RuntimeError(f"{path} is still populated after mounting over it")


def _private_tmp(paths: tuple[str, ...]) -> None:
    """Mount a fresh, empty, world-writable tmpfs over each path; only in a private mount namespace."""
    for path in paths:
        if not os.path.isdir(path):
            continue
        rc = _libc().mount(b"tmpfs", os.fsencode(path), b"tmpfs", _MS_NOSUID | _MS_NODEV, b"mode=1777")
        _check_call(rc, f"mount tmpfs on {path}")


def _loopback_up() -> None:
    """Bring ``lo`` up in the fresh network namespace (iproute2 may be absent, so use ioctl).

    A container engine's empty network namespace already has it up, and the contained stage lacks
    the capability to change it, so an interface that is up is left alone.
    """
    siocgifflags, siocsifflags, iff_up, iff_running = 0x8913, 0x8914, 0x1, 0x40
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        ifr = struct.pack("16sH14s", b"lo", 0, b"\0" * 14)
        flags = struct.unpack("16sH14s", fcntl.ioctl(sock, siocgifflags, ifr))[1]
        if flags & iff_up:
            return
        fcntl.ioctl(
            sock, siocsifflags, struct.pack("16sH14s", b"lo", flags | iff_up | iff_running, b"\0" * 14)
        )


def _spawn(
    processes: list[dict[str, Any]],
    fakeproc: Path,
    bindir: Path,
    run_as: tuple[int, int] | None = None,
    cwd: Path | None = None,
) -> list[dict[str, Any]]:
    """Start one inert process per record so ``/proc`` shows its name and command line.

    Each gets ``cwd`` (``/`` when none is given), never the stage's own working directory: a
    tool running as the same uid can follow ``/proc/<pid>/cwd`` of these processes.
    """
    bindir.mkdir(parents=True, exist_ok=True)
    bindir.chmod(0o755)
    out: list[dict[str, Any]] = []
    for rec in processes:
        name = str(rec["name"]).replace("/", "_") or "proc"
        exe = bindir / name
        if not exe.exists():
            shutil.copy2(fakeproc, exe)
            exe.chmod(0o755)
        argv = [str(a) for a in rec["argv"]] or [name]
        child = subprocess.Popen(
            argv,
            executable=str(exe),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(cwd or "/"),
            env=dict(INERT_ENV),
            user=run_as[0] if run_as else None,
            group=run_as[1] if run_as else None,
            extra_groups=[] if run_as else None,
        )
        out.append({"index": int(rec["index"]), "pid": child.pid, "name": name, "cmdline": " ".join(argv)})
    time.sleep(0.2)
    return out


def _signal(pid: int, sig: int) -> None:
    try:
        os.kill(pid, sig)
    except ProcessLookupError:
        pass


def _strays(keep: set[int]) -> tuple[list[int], list[int]]:
    """Pids other than the stage and ``keep``: those still running, and the exited ones to reap.

    Only a zombie whose parent is the stage is listed for reaping, since only the stage can.
    """
    live: list[int] = []
    zombies: list[int] = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit() or int(entry) == 1 or int(entry) in keep:
            continue
        try:
            raw = Path(f"/proc/{entry}/stat").read_bytes()
            threads = len(os.listdir(f"/proc/{entry}/task"))
        except OSError:
            continue  # exited and reaped while listing
        # State and parent pid follow the command name, which is parenthesized and may hold ") ".
        state, ppid = raw[raw.rindex(b")") + 2 :].split()[:2]
        if state not in (b"Z", b"X") or threads > 1:
            live.append(int(entry))
        elif int(ppid) == os.getpid():
            zombies.append(int(entry))
    return live, zombies


def _kill_strays(keep: set[int], unreaped: frozenset[int] = frozenset()) -> None:
    """Kill every process in this PID namespace but the stage and ``keep``; a no-op outside one.

    ``kill(-1, SIGSTOP)`` from the namespace's init stops every other process in it at once, and
    the kernel delivers it to a child forked while it is sent, so nothing can start a process the
    sweep below does not list. The strays are killed and reaped, so the next invocation does not
    see them either, except ``unreaped``, which a ``Popen`` still waits for. ``keep`` is then
    continued. A stray that is still running after ``SWEEP_GRACE`` raises, which the stage records
    as an error.
    """
    if os.getpid() != 1:
        return
    _signal(-1, signal.SIGSTOP)
    try:
        deadline = time.monotonic() + SWEEP_GRACE
        while True:
            live, zombies = _strays(keep)
            for pid in zombies:
                if pid not in unreaped:
                    try:
                        os.waitpid(pid, os.WNOHANG)
                    except ChildProcessError:
                        pass
            if not live:
                break
            if time.monotonic() > deadline:
                raise RuntimeError(f"processes {live[:10]} are still running after SIGKILL")
            for pid in live:
                _signal(pid, signal.SIGKILL)
            time.sleep(0.01)
    finally:
        for pid in keep:
            _signal(pid, signal.SIGCONT)


STDOUT_KEEP = 2_000_000
STDERR_KEEP = 200_000
"""Characters of an invocation's stdout and stderr its result keeps: the tail of each."""


class _Capture:
    """Feed an invocation's stdin and read its stdout and stderr on threads, keeping only the tail
    of each (four bytes per character kept, the most UTF-8 uses).

    ``communicate`` held everything a tool printed in the stage's memory before the tail was cut,
    and the stage runs as root, with no memory cgroup under the namespaces backend: a tool could
    print until the host ran out.
    """

    def __init__(self, proc: subprocess.Popen[bytes], stdin: bytes | None) -> None:
        self._tails = {"out": bytearray(), "err": bytearray()}
        self._threads = [
            threading.Thread(target=self._pump, args=(proc.stdout, "out", 4 * STDOUT_KEEP), daemon=True),
            threading.Thread(target=self._pump, args=(proc.stderr, "err", 4 * STDERR_KEEP), daemon=True),
        ]
        self._feeder = threading.Thread(target=self._feed, args=(proc.stdin, stdin), daemon=True)
        for thread in [*self._threads, self._feeder]:
            thread.start()

    def _pump(self, stream: Any, name: str, keep: int) -> None:
        tail = self._tails[name]
        while True:
            try:
                chunk = os.read(stream.fileno(), 1 << 16)
            except (OSError, ValueError):  # the stream was closed under a reader given up on
                return
            if not chunk:
                return
            tail += chunk
            if len(tail) > 2 * keep:
                del tail[:-keep]

    @staticmethod
    def _feed(stream: Any, data: bytes | None) -> None:
        if stream is None:
            return
        try:
            if data:
                stream.write(data)
            stream.close()
        except (OSError, ValueError):  # the tool exited or closed its stdin without reading it all
            pass

    def ended(self, deadline: float) -> bool:
        """Whether both pipes reached end of file by ``deadline``: nothing holds them any more."""
        for thread in self._threads:
            thread.join(max(0.0, deadline - time.monotonic()))
        return not any(thread.is_alive() for thread in self._threads)

    def output(self) -> tuple[str, str]:
        out, err = (bytes(self._tails[name]).decode("utf-8", "replace") for name in ("out", "err"))
        return out[-STDOUT_KEEP:], err[-STDERR_KEEP:]


def _run(
    inv: dict[str, Any],
    run_as: tuple[int, int] | None = None,
    sweep: set[int] | None = None,
    prefix: list[str] | None = None,
) -> dict[str, Any]:
    """Run one invocation; with ``sweep`` (the pids to spare), kill whatever else it left running.

    Only the stage's ``main`` passes ``sweep``, once it has checked it is the init of its own
    PID namespace; without it nothing but the invocation's own process group is ever killed.
    ``prefix`` (``limit_prefix``) runs the invocation under its resource limits.
    """
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.Popen(
            [*(prefix or []), *(str(a) for a in inv["argv"])],
            cwd=str(inv["cwd"]),
            env={str(k): str(v) for k, v in dict(inv.get("env") or {}).items()},
            stdin=subprocess.PIPE if inv.get("stdin") is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            user=run_as[0] if run_as else None,
            group=run_as[1] if run_as else None,
            extra_groups=[] if run_as else None,
        )
    except OSError as exc:
        return {
            "code": 127,
            "stdout": "",
            "stderr": f"cannot start: {exc}",
            "seconds": 0.0,
            "timed_out": False,
        }
    capture = _Capture(proc, inv["stdin"].encode() if inv.get("stdin") is not None else None)
    deadline = started + float(inv.get("timeout") or 300)
    try:
        # As communicate's timeout did: the tool must exit and its pipes close within it, so a child
        # it left holding them makes the run a timeout.
        proc.wait(timeout=max(0.0, deadline - time.monotonic()))
        timed_out = not capture.ended(deadline)
    except subprocess.TimeoutExpired:
        timed_out = True
    if timed_out:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        # A descendant that called setsid() left the group and may still hold the pipes.
        if sweep is not None:
            _kill_strays(sweep, frozenset({proc.pid}))  # reaped below
        if not capture.ended(time.monotonic() + KILL_GRACE):
            for stream in (proc.stdout, proc.stderr):  # held by what no sweep reaches: give up on them
                if stream is not None:
                    stream.close()
        try:
            proc.wait(timeout=KILL_GRACE)
        except subprocess.TimeoutExpired:
            pass
    out, err = capture.output()
    if sweep is not None:
        _kill_strays(sweep)
    return {
        "code": 124 if timed_out else proc.returncode,
        "stdout": out,
        "stderr": err,
        "seconds": round(time.monotonic() - started, 3),
        "timed_out": timed_out,
    }


def main(argv: list[str]) -> int:
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out_path = Path(argv[1])
    result: dict[str, Any] = {"processes": [], "runs": [], "error": None}
    services = Services(list(spec.get("services") or []))
    children: list[dict[str, Any]] = []
    try:
        run_as = _tool_identity(spec)
        contained = spec.get("contained") is True
        _check_namespaces(spec.get("host_mnt_ns"), spec.get("host_uts_ns"))
        new_session_keyring()
        _no_new_privs()
        result["limits"] = pairs = limit_pairs(spec.get("limits", DEFAULT_LIMITS))
        prefix = limit_prefix(pairs)
        if contained:
            _check_contained(spec.get("host_root"))
        elif "hostname" in spec:
            _set_hostname(spec["hostname"])
            _mask_host_files(spec["hostname"], out_path.parent)
        _loopback_up()
        if not contained:
            _hide(HIDDEN)
            _private_tmp(PRIVATE_TMP)
        # The stage may have been started inside a now-hidden directory; children inherit the cwd.
        os.chdir("/")
        work = Path(spec["work"])
        if not work.is_dir():
            raise RuntimeError(f"work directory {work} is not visible inside the stage")
        if spec.get("services"):
            services.start()
        if spec.get("processes"):
            bindir = Path(spec["procbin"]) if spec.get("procbin") else work / "procbin"
            children = _spawn(spec["processes"], Path(spec["fakeproc"]), bindir, run_as, work)
            result["processes"] = children
        spare = {int(child["pid"]) for child in children}
        for inv in spec["invocations"]:
            result["runs"].append(_run(inv, run_as, spare, prefix))
    except Exception as exc:  # noqa: BLE001 - the stage must always report, never crash silently
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for child in children:
            try:
                os.kill(int(child["pid"]), signal.SIGKILL)
            except ProcessLookupError:
                pass
        services.stop()
        out_path.write_text(json.dumps(result), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
