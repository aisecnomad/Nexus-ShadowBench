"""Run every adapter on every case it supports, in isolation, and store normalized results.

``python -m tools.shadowbench.cases run --corpus corpus.json --tools tools.json --out results/``
(optional ``--only a,b``, ``--surfaces x,y``, ``--cases id,...``, ``--workers 4``,
``--rlimit name=value``, ``--sandbox oci --oci-image IMAGE@sha256:...``)

For each (tool, case) the runner materializes the case under a scratch
directory, asks the adapter for its invocations, and executes them through
``stage.py`` inside fresh network, PID, mount, IPC, UTS and cgroup namespaces
(``unshare``), with the case's mock services and inert processes present, the
host name set to ``stage.HOSTNAME`` and the stage's resource limits lowered
(``stage.DEFAULT_LIMITS``, changed with ``--rlimit``). The adapter then
normalizes the output into entities. One JSONL row per (tool, case) goes to
``<out>/<tool>.jsonl``; verbatim tool output goes to ``<out>/raw/<tool>/``.

Each run gets ``<scratch>/<tool>-<case>-XXXX/`` (mode 0711) holding ``work/``,
the tool's tree, which belongs to uid/gid 65534 for the run, and ``control/``
(root only), where the stage spec and the stage's result stay out of the
tool's reach. Tools run as 65534 with ``/root`` and ``/home`` hidden (see
``stage.py``), so the scratch directory, ``tool_root`` (by default the
directory holding ``tools.json``) and every path in ``tools.json`` must lie
outside those, and outside ``/var/tmp`` and ``/dev/shm``, which the stage
replaces with an empty tmpfs, and be reachable by that uid. Every run's ``work/`` belongs to
the same uid, so the scratch directory must also belong to the runner and give
group and other nothing but search (0711, as the runner creates it), or a tool
could list it and reach a concurrent run's tree. The runner refuses to start
otherwise. Before the adapter reads the tool's output as root, ``work/`` is
handed back to root with group and other write removed, so no process of the
tool's uid can change it any more. Any hard link the tool left (it may name a
file outside ``work/``) and any FIFO, socket or device node in it is removed
rather than handed to root, and then any symlink that leads out of ``work/``.

A crash, timeout or unreadable output is recorded as ``error`` and never as a
clean negative. A run that exits outside the adapter's accepted codes but still
reports entities keeps them and is flagged ``incomplete``. On a timeout the
runner kills ``unshare``'s process group; with ``--kill-child`` and ``--pid``
that takes down every process in the namespace before the work tree is
removed. ``runtime/live`` rows carry the pid map so reported pids are
translated to the corpus's ``proc:<index>`` keys before scoring.

Case and checkout ids from the corpus name directories, so they must match
``[A-Za-z0-9._-]+``. A code case may not also carry files, and no input file
is written through a symlink. A checkout is copied into a case only when it
holds its pinned commit's tree and nothing else (``fetch_code.checkout_problem``).

Before any tool runs, the runner refuses to start, with exit 2 and a message,
when it is not root, ``unshare`` is missing, a case or checkout id is unsafe,
the scratch directory or a configured path fails the checks above, or ``gcc``
cannot build the static inert binary that live-runtime cases spawn.

Sandbox backends. ``--sandbox namespaces`` (the default) is the above.
``--sandbox oci`` runs the same stage as the init of a Docker container
started from ``--oci-image``, which must be pinned by digest and present
locally (it is never pulled during a run): no network, a read-only root file
system, fresh tmpfs ``/tmp``, ``/var/tmp`` and ``/run``, a private IPC
namespace, the fixed host name, ``no-new-privileges``, Docker's default
seccomp profile, every capability dropped but the four the stage needs as
root before it drops to uid 65534 (``SETUID``, ``SETGID``, ``KILL``,
``DAC_READ_SEARCH``), and memory, CPU and process-count limits
(``--oci-memory``, ``--oci-cpus``, ``--oci-pids``). ``--oci-runtime runsc``
runs it under gVisor, which puts a user-space kernel between the tool and
the host's. Only the run directory is writable from the container; the
harness's ``tools/`` package, ``tool_root`` and every absolute path in
``tools.json`` are bound read-only at their own paths, so the image must
provide what those binaries need at run time (an interpreter for a venv, a C
library for a dynamically linked binary): build the tool tree in the same
image (``images/Containerfile``). The runner refuses an image without a
digest, one that is not present, and a rootless or user-namespace-remapped
daemon, under which uid 65534 would not be the uid that owns the work tree.

``manifest.json`` records the corpus path and SHA-256, the generator digest,
the platform, the harness commit (``harness_commit``, the checkout's ``HEAD``,
null when git cannot name it) and whether ``tools/`` differs from that commit
(``harness_dirty``, null when unknown), and per tool its version, row-status
counts and the SHA-256 of its ``<tool>.jsonl`` (``rows_sha256``). A tool's
version is the ``version`` string its ``tools.json`` entry gives, recorded as
given, or else what its adapter's ``version()`` probes. ``isolation`` records
the sandbox: backend, namespaces, host name and resource limits, and for the
OCI backend the image digest, the daemon's version and the runtime.
``tool_install`` records what ``install_tools.sh`` resolved: the runner copies
``<tool_root>/resolved/`` (frozen venvs, Go build info, the locks used and
SHA256SUMS of every binary) into ``<out>/resolved/`` and records each file's
SHA-256, or ``null`` when the tool root has no such record.
"""

from __future__ import annotations

import argparse
import errno
import gzip
import hashlib
import json
import os
import platform
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tools.shadowbench.cases.adapters.registry import load_adapters
from tools.shadowbench.cases.contract import (
    SYSTEM_PATH,
    Adapter,
    AdapterResult,
    MaterializedCase,
    RunResult,
    ToolEnv,
    supports,
)
from tools.shadowbench.cases.corpus import Case, Corpus, corpus_digest, load_corpus
from tools.shadowbench.cases.fetch_code import checkout_problem
from tools.shadowbench.cases.stage import (
    DEFAULT_LIMITS,
    HIDDEN,
    HOSTNAME,
    PRIVATE_TMP,
    build_fakeproc,
    check_limits,
)

STAGE_TIMEOUT_GRACE = 120
KILL_GRACE = 10.0
TOOL_UID = TOOL_GID = 65534
"""The identity tools and inert processes run as (``nobody``/``nogroup`` on most systems)."""
REPO = Path(__file__).resolve().parents[3]
"""The checkout the harness runs from: the stage's ``PYTHONPATH`` and the commit the manifest records."""

_SAFE_NAME = re.compile(r"[A-Za-z0-9._-]+")
_COMMIT = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
_PINNED_IMAGE = re.compile(r"[a-z0-9][a-z0-9._/:-]*@sha256:[0-9a-f]{64}")

NAMESPACES: tuple[str, ...] = ("net", "pid", "mount", "ipc", "uts", "cgroup")
"""The namespaces ``unshare`` gives the stage under the default backend."""
OCI_CAPABILITIES: tuple[str, ...] = ("SETUID", "SETGID", "KILL", "DAC_READ_SEARCH")
"""What the contained stage keeps as root: dropping to uid 65534 (``SETUID``, ``SETGID``, with
``setgroups``), stopping and killing that uid's processes (``KILL``) and entering the work tree it
owns, mode 0700, to start a tool there (``DAC_READ_SEARCH``). Tools lose all of them at the uid
change, and ``no-new-privileges`` keeps them from coming back."""
HARNESS_MOUNT = "/opt/shadowbench/harness"
"""Where the contained stage finds the harness's ``tools`` package (read-only)."""
OCI_RUNTIMES: tuple[str, ...] = ("runc", "runsc")


@dataclass(frozen=True)
class Sandbox:
    """How the stage is isolated; ``describe`` is what the manifest records."""

    backend: str = "namespaces"
    limits: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_LIMITS))
    image: str | None = None
    runtime: str = "runc"
    memory: str = "4g"
    cpus: str = "2"
    pids: int = 1024
    binds: tuple[str, ...] = ()
    """Host paths bound read-only into the container at their own paths (tool trees)."""

    def describe(self) -> dict[str, Any]:
        out: dict[str, Any] = {"backend": self.backend, "hostname": HOSTNAME, "limits": dict(self.limits)}
        if self.backend == "namespaces":
            out["namespaces"] = list(NAMESPACES)
        else:
            out.update(
                {
                    "image": self.image,
                    "runtime": self.runtime,
                    "memory": self.memory,
                    "cpus": self.cpus,
                    "pids": self.pids,
                    "capabilities": list(OCI_CAPABILITIES),
                    "read_only_root": True,
                    "network": "none",
                }
            )
        return out


DEFAULT_SANDBOX = Sandbox()


def safe_name(value: str, what: str) -> str:
    """Return a corpus-supplied identifier that is safe as a single path component."""
    if not _SAFE_NAME.fullmatch(value) or value in (".", ".."):
        raise ValueError(f"unsafe {what} {value!r}: expected [A-Za-z0-9._-]+")
    return value


def _write_input(inputs: Path, rel: str, content: str) -> None:
    """Write ``inputs/<rel>`` without following a symlink at any step of the path."""
    parts = rel.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"unsafe input path {rel!r}")
    dir_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(inputs, dir_flags)
    try:
        for part in parts[:-1]:
            try:
                os.mkdir(part, 0o755, dir_fd=fd)
            except FileExistsError:
                pass
            child = os.open(part, dir_flags, dir_fd=fd)
            os.close(fd)
            fd = child
        leaf = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o644, dir_fd=fd)
    except OSError as exc:
        if exc.errno in (errno.ELOOP, errno.ENOTDIR):
            raise ValueError(f"refusing to write input {rel!r} through a symlink or a file") from exc
        raise
    finally:
        os.close(fd)
    with os.fdopen(leaf, "w", encoding="utf-8") as fh:
        fh.write(content)


def materialize(case: Case, root: Path, checkouts: Path | None = None) -> MaterializedCase:
    inputs = root / "inputs"
    inputs.mkdir(parents=True, exist_ok=True)
    if case.checkout:
        if case.files:
            # A copied repository may hold symlinks; nothing from the corpus is written into it.
            raise ValueError(f"case {case.case_id} carries files beside its checkout")
        if checkouts is None:
            raise RuntimeError(
                "code cases need --checkouts (fetched with python -m tools.shadowbench.cases.fetch_code)"
            )
        name = safe_name(str(case.checkout["id"]), "checkout id")
        base = checkouts.resolve()
        src = (base / name).resolve()
        if src == base or not src.is_relative_to(base):
            raise ValueError(f"checkout {name} resolves to {src}, outside {base}")
        # The whole directory is copied, so it must hold the pinned commit's tree and nothing else.
        problem = checkout_problem(src, str(case.checkout["commit"]))
        if problem:
            raise RuntimeError(f"checkout {src} {problem}")
        shutil.copytree(src, inputs / "repo", symlinks=True)
    for rel, content in case.files.items():
        _write_input(inputs, rel, content)
    home = inputs / "home" if case.surface == "endpoint" else None
    if home is not None:
        home.mkdir(exist_ok=True)
    (root / "case.json").write_text(
        json.dumps({"id": case.case_id, "surface": case.surface, "modality": case.modality}), encoding="utf-8"
    )
    return MaterializedCase(
        case.case_id,
        case.surface,
        case.modality,
        case.family,
        root,
        inputs,
        home=home,
        processes=list(case.processes),
        services=list(case.services),
    )


def _chown_tree(path: Path, uid: int, gid: int) -> None:
    """Hand a tree the runner built to the tool's identity without following any symlink in it."""
    os.lchown(path, uid, gid)
    for top, dirs, files in os.walk(path):
        for name in (*dirs, *files):
            os.lchown(os.path.join(top, name), uid, gid)


def _reclaim_tree(work: Path) -> int:
    """Take the tool's tree back for the runner, so no other process can change it while it is read.

    A process of the tool's uid that runs outside the stage (any host process running as 65534) can
    hold a directory fd into ``work`` and, while ``work`` still belongs to that uid, plant a symlink
    after ``_drop_unsafe_entries`` checked the tree. Each directory is handed to the runner (root)
    and loses group and other write before it is listed, so once listed only the runner can add,
    rename or remove an entry in it; no symlink is followed, and an open fd grants no write.

    Regular files and symlinks with a single link are handed to the runner too. Anything else is
    removed rather than handed over: a hard link may name a file outside ``work`` (one the tool's
    uid could link but does not own), which a change of owner would give to root, and a FIFO,
    socket or device node is no output. Returns how many entries were removed.
    """
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    uid, gid = os.geteuid(), os.getegid()
    removed = 0

    def seal(path: str) -> None:
        fd = os.open(path, flags)
        try:
            os.fchown(fd, uid, gid)
            os.fchmod(fd, stat.S_IMODE(os.fstat(fd).st_mode) & ~0o022)
        finally:
            os.close(fd)

    seal(str(work))
    for top, dirs, files in os.walk(work):  # top-down: a directory is sealed before it is listed
        for name in [*dirs, *files]:
            path = os.path.join(top, name)
            # The parent is sealed, so ``name`` stays the entry lstat saw.
            entry = os.lstat(path)
            if stat.S_ISDIR(entry.st_mode):
                seal(path)
            elif (stat.S_ISREG(entry.st_mode) or stat.S_ISLNK(entry.st_mode)) and entry.st_nlink == 1:
                os.lchown(path, uid, gid)
            else:
                os.unlink(path)
                removed += 1
                if name in dirs:  # a hard-linked symlink to a directory
                    dirs.remove(name)
    return removed


def _drop_unsafe_entries(work: Path) -> int:
    """Remove what the tool left that the adapter, reading as root on the host, must not open.

    The tool ran as uid 65534 with ``/root`` and ``/home`` hidden, but its output is read here
    with neither restriction: a symlink it planted could lead to a host file it could never
    read itself, and a FIFO would block the read forever. Symlinks that stay inside ``work``
    are kept.
    """
    top = os.path.realpath(work)
    removed = 0
    for parent, dirs, files in os.walk(work):
        for name in [*dirs, *files]:
            path = os.path.join(parent, name)
            mode = os.lstat(path).st_mode
            if stat.S_ISDIR(mode) or stat.S_ISREG(mode):
                continue
            if stat.S_ISLNK(mode) and os.path.commonpath([top, os.path.realpath(path)]) == top:
                continue
            os.unlink(path)
            removed += 1
            if name in dirs:
                dirs.remove(name)
    return removed


def prepare_scratch(scratch: Path | None) -> Path:
    """The scratch directory, made 0711 when the runner creates it; an existing one is left as it is.

    Every run's ``work/`` belongs to the same uid 65534, so the scratch directory must not let a
    tool list it and find another run's tree; ``isolation_problems`` refuses one that does.
    """
    if scratch is None:
        path = Path(tempfile.mkdtemp(prefix="shadowbench-"))
        path.chmod(0o711)
        return path
    path = scratch.resolve()  # the stage runs from /, not from here
    if not path.exists():
        path.mkdir(parents=True)
        path.chmod(0o711)
    return path


def isolation_problems(scratch: Path, env: ToolEnv) -> list[str]:
    """Why tools running as uid 65534 with ``/root`` and ``/home`` hidden could not run from here.

    The stage also replaces ``/var/tmp`` and ``/dev/shm`` with an empty tmpfs, which hides them alike.
    """
    hidden = [Path(p).resolve() for p in (*HIDDEN, *PRIVATE_TMP)]

    def hidden_root(path: Path) -> Path | None:
        resolved = path.resolve()
        return next((h for h in hidden if resolved.is_relative_to(h)), None)

    problems: list[str] = []
    covered = hidden_root(scratch)
    if covered is not None:
        problems.append(f"scratch directory {scratch} lies under {covered}, which the stage hides from tools")
    else:
        for part in (scratch.resolve(), *scratch.resolve().parents):
            if not os.stat(part).st_mode & stat.S_IXOTH:
                problems.append(f"uid {TOOL_UID} cannot traverse {part} to reach scratch directory {scratch}")
                break
        info = os.stat(scratch)
        if info.st_uid != os.geteuid():
            problems.append(f"scratch directory {scratch} is owned by uid {info.st_uid}, not the runner's")
        if info.st_mode & 0o066:
            problems.append(
                f"scratch directory {scratch} is mode {stat.S_IMODE(info.st_mode):04o}; a tool could list"
                " it and reach another run's work tree (chmod 0711)"
            )
    # Adapters derive data paths from tool_root, which defaults to the directory holding tools.json.
    paths: list[tuple[str, str]] = [("tool_root", str(env.tool_root))]
    tools = env.config.get("tools")
    tools = tools if isinstance(tools, dict) else {}
    for name, cfg in sorted(tools.items()):
        if not isinstance(cfg, dict):
            continue
        for key, value in sorted(cfg.items()):
            if isinstance(value, str) and value.startswith("/"):
                paths.append((f"tools.{name}.{key}", value))
    for label, value in paths:
        covered = hidden_root(Path(value))
        if covered is not None:
            problems.append(f"{label} = {value} lies under {covered}, which the stage hides from tools")
    return problems


def stage_command(spec_path: Path, out_path: Path) -> list[str]:
    """The stage's command line: no network, its own PID, mount and IPC namespaces, gone when unshare dies.

    ``-P`` keeps the working directory off ``sys.path``; the stage is found through ``PYTHONPATH``.
    """
    return [
        "unshare",
        "--net",
        "--pid",
        "--fork",
        "--kill-child",
        "--mount",
        "--propagation",
        "private",
        "--mount-proc",
        "--ipc",
        "--uts",
        "--cgroup",
        "--",
        sys.executable,
        "-P",
        "-m",
        f"{__package__}.stage",
        str(spec_path),
        str(out_path),
    ]


def container_name(run_dir: Path) -> str:
    """The container's name: the run directory's (unique, ``[A-Za-z0-9._-]``) under a fixed prefix."""
    return f"shadowbench-{safe_name(run_dir.name, 'run directory')}"


def _bind(src: str, dst: str | None = None, *, readonly: bool) -> list[str]:
    for path in (src, dst or src):
        if "," in path or "=" in path:
            raise ValueError(f"cannot bind {path!r}: Docker's --mount syntax cannot quote ',' or '='")
    spec = f"type=bind,src={src},dst={dst or src}"
    return ["--mount", spec + (",readonly" if readonly else "")]


def oci_command(
    spec_path: Path, out_path: Path, run_dir: Path, fakeproc: Path, repo: Path, sandbox: Sandbox
) -> list[str]:
    """``docker run`` for the contained stage (see the module docstring); nothing is pulled."""
    if sandbox.image is None or not _PINNED_IMAGE.fullmatch(sandbox.image):
        raise ValueError(f"the OCI backend needs an image pinned by digest, not {sandbox.image!r}")
    tmpfs = "rw,nosuid,nodev"
    cmd = [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name(run_dir),
        "--pull",
        "never",
        "--network",
        "none",
        "--read-only",
        "--ipc",
        "private",
        "--hostname",
        HOSTNAME,
        "--user",
        "0:0",
        "--workdir",
        "/",
        "--cap-drop",
        "ALL",
        *[arg for cap in OCI_CAPABILITIES for arg in ("--cap-add", cap)],
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        str(sandbox.pids),
        "--memory",
        sandbox.memory,
        "--memory-swap",
        sandbox.memory,
        "--cpus",
        sandbox.cpus,
        "--tmpfs",
        f"/tmp:{tmpfs},size=1g",
        "--tmpfs",
        f"/var/tmp:{tmpfs},size=256m",
        "--tmpfs",
        f"/run:{tmpfs},size=16m",
        "--env",
        f"PATH={SYSTEM_PATH}",
        "--env",
        f"PYTHONPATH={HARNESS_MOUNT}",
        "--env",
        "LANG=C.UTF-8",
        "--env",
        "PYTHONDONTWRITEBYTECODE=1",
        *_bind(str(run_dir), readonly=False),
        *_bind(str(fakeproc), readonly=True),
        *_bind(str(repo / "tools"), f"{HARNESS_MOUNT}/tools", readonly=True),
    ]
    for path in sandbox.binds:
        cmd += _bind(path, readonly=True)
    if sandbox.runtime != "runc":
        cmd += ["--runtime", sandbox.runtime]
    return [*cmd, sandbox.image, "python3", "-P", "-m", f"{__package__}.stage", str(spec_path), str(out_path)]


def _remove_container(name: str) -> None:
    """Force-remove a container a killed ``docker run`` client left behind; errors are ignored."""
    try:
        subprocess.run(
            ["docker", "rm", "--force", name],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=60,
            check=False,
            env={"PATH": SYSTEM_PATH},
        )
    except (OSError, subprocess.SubprocessError):
        pass


def _kill_stage(proc: subprocess.Popen[bytes]) -> None:
    """Kill unshare and the stage; the stage is the namespace's init, so every tool process dies too."""
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        proc.communicate(timeout=KILL_GRACE)
    except subprocess.TimeoutExpired:
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()
        try:
            proc.wait(timeout=KILL_GRACE)
        except subprocess.TimeoutExpired:
            pass


def _stage(
    spec: dict[str, Any], control: Path, repo: Path, timeout: float, sandbox: Sandbox = DEFAULT_SANDBOX
) -> dict[str, Any]:
    """Run the stage on ``spec``; its spec and result files live in ``control``, never in the work tree.

    ``control`` is ``<run_dir>/control``; the OCI backend binds ``<run_dir>`` into the container.
    """
    spec_path = control / "stage_spec.json"
    out_path = control / "stage_out.json"
    full = {
        **spec,
        "run_as": [TOOL_UID, TOOL_GID],
        "host_mnt_ns": os.readlink("/proc/self/ns/mnt"),
        "host_uts_ns": os.readlink("/proc/self/ns/uts"),
        "limits": dict(sandbox.limits),
    }
    run_dir = control.parent
    name: str | None = None
    if sandbox.backend == "oci":
        root = os.stat("/")
        procbin = run_dir / "procbin"
        procbin.mkdir(mode=0o755, exist_ok=True)
        full.update({"contained": True, "host_root": [root.st_dev, root.st_ino], "procbin": str(procbin)})
        name = container_name(run_dir)
        command = oci_command(spec_path, out_path, run_dir, Path(spec["fakeproc"]), repo, sandbox)
    else:
        full["hostname"] = HOSTNAME
        command = stage_command(spec_path, out_path)
    spec_path.write_text(json.dumps(full), encoding="utf-8")
    env = {
        "PATH": SYSTEM_PATH,
        "PYTHONPATH": str(repo),
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    proc = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd="/",  # never a directory the stage then hides; its children would inherit it
        start_new_session=True,
    )
    try:
        _, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        _kill_stage(proc)
        if name is not None:
            _remove_container(name)  # killing the client leaves the container running
        return _stage_error(f"stage timed out after {timeout:.0f}s")
    if not out_path.exists():
        stderr = err.decode("utf-8", "replace")[-500:]
        return _stage_error(f"stage produced no output (exit {proc.returncode}): {stderr}")
    try:
        result = json.loads(out_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return _stage_error(f"stage output unreadable: {exc}")
    if not isinstance(result, dict):
        return _stage_error("stage output is not an object")
    return result


def _stage_error(message: str) -> dict[str, Any]:
    return {"error": message, "runs": [], "processes": []}


def _with_note(note: str, extra: str) -> str:
    return (note + "; " if note else "") + extra


def run_one(
    adapter: Adapter,
    case: Case,
    env: ToolEnv,
    scratch: Path,
    repo: Path,
    fakeproc: Path,
    checkouts: Path | None,
    sandbox: Sandbox = DEFAULT_SANDBOX,
) -> dict[str, Any]:
    prefix = f"{adapter.name}-{safe_name(case.case_id, 'case id')}-"
    run_dir = Path(tempfile.mkdtemp(prefix=prefix, dir=scratch))
    work = run_dir / "work"
    control = run_dir / "control"
    row: dict[str, Any] = {
        "tool": adapter.name,
        "case": case.case_id,
        "surface": case.surface,
        "modality": case.modality,
        "family": case.family,
        "label": case.label,
        "difficulty": case.difficulty,
    }
    started = time.monotonic()
    try:
        # The tool may pass through run_dir to work/, but cannot list it or enter control/.
        run_dir.chmod(0o711)
        work.mkdir(mode=0o700)
        control.mkdir(mode=0o700)
        mat = materialize(case, work / "case", checkouts)
        invocations = adapter.invocations(mat, env, work)
        spec = {
            "services": mat.services,
            "processes": mat.processes if case.modality == "live" else [],
            "fakeproc": str(fakeproc),
            "work": str(work),
            "invocations": [
                {
                    "argv": list(inv.argv),
                    "cwd": str(inv.cwd),
                    "env": inv.env,
                    "timeout": inv.timeout,
                    "stdin": inv.stdin,
                }
                for inv in invocations
            ],
        }
        total_timeout = sum(inv.timeout for inv in invocations) + STAGE_TIMEOUT_GRACE
        _chown_tree(work, TOOL_UID, TOOL_GID)
        staged = _stage(spec, control, repo, total_timeout, sandbox)
        unsafe = _reclaim_tree(work)
        unsafe += _drop_unsafe_entries(work)
        runs = [
            RunResult(
                int(r["code"]), str(r["stdout"]), str(r["stderr"]), float(r["seconds"]), bool(r["timed_out"])
            )
            for r in staged.get("runs", [])
        ]
        pid_map = {int(p["pid"]): int(p["index"]) for p in staged.get("processes", [])}
        bad_exit: int | None = None
        if staged.get("error") or len(runs) != len(invocations):
            result = AdapterResult(
                "error", note=f"stage: {staged.get('error') or 'missing invocation results'}"
            )
        elif any(r.timed_out for r in runs):
            result = AdapterResult("error", note=f"timed out after {max(r.seconds for r in runs):.0f}s")
        elif any(r.code not in inv.ok_codes for r, inv in zip(runs, invocations, strict=True)):
            bad = next(
                (r, inv) for r, inv in zip(runs, invocations, strict=True) if r.code not in inv.ok_codes
            )
            result = adapter.normalize(mat, work, runs)
            if result.status == "ok" and not result.entities:
                result = AdapterResult(
                    "error",
                    note=f"exit {bad[0].code}: {(bad[0].stderr or bad[0].stdout)[-300:].strip()}",
                    raw=result.raw,
                )
            elif result.status == "ok":
                # What a failed run printed is kept, but it may have stopped before reading everything.
                bad_exit = bad[0].code
        else:
            result = adapter.normalize(mat, work, runs)
        if case.modality == "live":
            translated = []
            harness = 0
            for e in result.entities:
                if e.key.startswith("process:"):
                    pid = int(e.key.split(":", 1)[1]) if e.key.split(":", 1)[1].isdigit() else -1
                    if pid in pid_map:
                        translated.append(type(e)(e.kind, f"proc:{pid_map[pid]}", e.label, e.attributes))
                    else:
                        harness += 1
                else:
                    translated.append(e)
            result.entities = translated
            if harness:
                result.note = _with_note(result.note, f"{harness} harness/self process reports ignored")
        if bad_exit is not None:
            result.note = _with_note(result.note, f"exit {bad_exit} is outside the accepted codes")
        if unsafe:
            result.note = _with_note(result.note, f"{unsafe} unsafe links or special files removed from work")
        row.update(result.to_json())
        row["seconds"] = round(sum(r.seconds for r in runs), 3)
        row["incomplete"] = bool(result.raw.get("incomplete")) or bad_exit is not None
        row["raw"] = {"runs": [asdict(r) for r in runs], "adapter": result.raw}
    except Exception as exc:  # noqa: BLE001 - an adapter bug is an error row, never a crash of the whole run
        row.update(
            {
                "status": "error",
                "entities": [],
                "note": f"adapter exception: {type(exc).__name__}: {exc}"[:400],
            }
        )
        row["seconds"] = round(time.monotonic() - started, 3)
        row["incomplete"] = False
        row["raw"] = {}
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
    return row


def tool_version(adapter: Adapter, env: ToolEnv) -> str:
    """The version the manifest records: the tool's ``version`` in ``tools.json``, else the adapter's probe.

    A configured version is recorded as given, for every tool alike; ``install_tools.sh`` writes the
    pinned one for each tool it installs, so a rerun records what the committed manifest does.
    """
    configured = env.tool(adapter.name).get("version")
    return configured if isinstance(configured, str) and configured else adapter.version(env)


def run_tool(
    adapter: Adapter,
    cases: list[Case],
    env: ToolEnv,
    out: Path,
    workers: int,
    scratch: Path,
    repo: Path,
    fakeproc: Path,
    checkouts: Path | None,
    sandbox: Sandbox = DEFAULT_SANDBOX,
) -> dict[str, Any]:
    for case in cases:
        safe_name(case.case_id, "case id")
    rows_path = out / f"{adapter.name}.jsonl"
    raw_dir = out / "raw" / adapter.name
    raw_dir.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    rows: dict[str, dict[str, Any]] = {}
    started = time.time()

    def task(case: Case) -> None:
        if not supports(adapter, case.surface, case.modality):
            row = {
                "tool": adapter.name,
                "case": case.case_id,
                "surface": case.surface,
                "modality": case.modality,
                "family": case.family,
                "label": case.label,
                "difficulty": case.difficulty,
                "status": "unsupported",
                "entities": [],
                "note": "",
                "seconds": 0.0,
                "incomplete": False,
            }
        else:
            row = run_one(adapter, case, env, scratch, repo, fakeproc, checkouts, sandbox)
            raw = row.pop("raw", {})
            with gzip.open(raw_dir / f"{case.case_id}.json.gz", "wt", encoding="utf-8") as fh:
                json.dump(raw, fh)
        with lock:
            rows[case.case_id] = row

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        list(pool.map(task, cases))
    with rows_path.open("w", encoding="utf-8") as fh:
        for case in cases:
            fh.write(json.dumps(rows[case.case_id], ensure_ascii=False) + "\n")
    statuses: dict[str, int] = {}
    for row in rows.values():
        statuses[str(row["status"])] = statuses.get(str(row["status"]), 0) + 1
    return {
        "tool": adapter.name,
        "version": tool_version(adapter, env),
        "seconds": round(time.time() - started, 1),
        "statuses": statuses,
        "rows_sha256": hashlib.sha256(rows_path.read_bytes()).hexdigest(),
    }


def unsafe_ids(cases: list[Case]) -> list[str]:
    """Case and checkout ids that cannot name a directory safely."""
    problems: list[str] = []
    for case in cases:
        names = [("case id", case.case_id)]
        if case.checkout:
            names.append(("checkout id", str(case.checkout.get("id"))))
        for what, value in names:
            try:
                safe_name(value, what)
            except ValueError as exc:
                problems.append(f"{case.case_id!r}: {exc}")
    return problems


def _git(repo: Path, *args: str) -> str | None:
    """``git -C repo args`` without the caller's ``GIT_*`` variables; None when it fails or cannot run."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    try:
        proc = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo), *args],
            env=env,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def harness_revision(repo: Path = REPO) -> dict[str, Any]:
    """The commit the harness runs from and whether ``tools/`` differs from it; nulls when unknown.

    Untracked files under ``tools/`` count as a difference: the registry imports every module in
    ``adapters/``, so an adapter that was never committed still runs. ``--no-optional-locks`` keeps
    git, run as root, from rewriting the operator's index.
    """
    unknown: dict[str, Any] = {"commit": None, "dirty": None}
    top = _git(repo, "rev-parse", "--show-toplevel")
    if not top or Path(top).resolve() != repo.resolve():
        return unknown
    head = _git(repo, "rev-parse", "--verify", "HEAD")
    if not head or not _COMMIT.fullmatch(head):
        return unknown
    status = _git(repo, "status", "--porcelain", "--untracked-files=normal", "--", "tools")
    return {"commit": head, "dirty": None if status is None else bool(status)}


def fakeproc_problem(exc: Exception) -> str:
    """Why ``build_fakeproc`` could not build the inert binary, in one line for the operator."""
    if isinstance(exc, FileNotFoundError) and exc.filename == "gcc":
        reason = "gcc is not on PATH"
    elif isinstance(exc, subprocess.CalledProcessError):
        stderr = exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr or ""
        reason = f"gcc exited {exc.returncode}: {' '.join(stderr.split())[-300:] or '(no output)'}"
    else:
        reason = f"{type(exc).__name__}: {exc}"
    return (
        f"cannot build the inert process binary ({reason}); the runner needs a gcc that can link a"
        " static binary (gcc and the C library's static archive, such as glibc-static or libc6-dev)"
    )


def record_install(tool_root: Path, out: Path) -> dict[str, Any]:
    """Copy ``tool_root/resolved/`` into ``out/resolved/``; the SHA-256 of each regular file copied.

    Symlinks and special files are skipped, so nothing outside the record is copied or followed.
    """
    src = tool_root / "resolved"
    if not src.is_dir() or src.is_symlink():
        return {"resolved": None}
    digests: dict[str, str] = {}
    for top, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if not os.path.islink(os.path.join(top, d)))
        for name in sorted(files):
            path = Path(top, name)
            if path.is_symlink() or not path.is_file():
                continue
            rel = path.relative_to(src).as_posix()
            data = path.read_bytes()
            dest = out / "resolved" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            digests[rel] = hashlib.sha256(data).hexdigest()
    return {"resolved": dict(sorted(digests.items()))}


def namespace_problem() -> str | None:
    """Why ``unshare`` cannot give the stage every namespace it needs on this host; None when it can."""
    command = stage_command(Path("/dev/null"), Path("/dev/null"))
    probe = [*command[: command.index("--") + 1], "true"]
    try:
        done = subprocess.run(
            probe,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            timeout=30,
            check=False,
            env={"PATH": SYSTEM_PATH},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return f"cannot run {' '.join(probe)}: {exc}"
    if done.returncode != 0:
        stderr = done.stderr.decode("utf-8", "replace").strip()[-300:]
        return f"{' '.join(probe)} exited {done.returncode}: {stderr}"
    return None


def parse_limits(values: list[str]) -> dict[str, int]:
    """``stage.DEFAULT_LIMITS`` with each ``name=value`` of ``--rlimit`` applied over it."""
    limits = dict(DEFAULT_LIMITS)
    for item in values:
        name, sep, value = item.partition("=")
        if not sep or not value.isdigit():
            raise ValueError(f"--rlimit takes name=<non-negative integer>, not {item!r}")
        limits[name] = int(value)
    return check_limits(limits)


def tool_binds(env: ToolEnv) -> tuple[str, ...]:
    """The tool trees a container needs read-only: ``tool_root`` and every absolute path in
    ``tools.json`` that exists, less those already inside another."""
    candidates = {str(env.tool_root.resolve())}
    tools = env.config.get("tools")
    for cfg in (tools if isinstance(tools, dict) else {}).values():
        if isinstance(cfg, dict):
            candidates |= {
                str(Path(v).resolve()) for v in cfg.values() if isinstance(v, str) and v.startswith("/")
            }
    existing = sorted(c for c in candidates if os.path.exists(c))
    return tuple(c for c in existing if not any(c != o and Path(c).is_relative_to(o) for o in existing))


def _docker_json(*args: str) -> Any:
    done = subprocess.run(
        ["docker", *args, "--format", "{{json .}}"],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={"PATH": SYSTEM_PATH},
    )
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip()[-300:] or f"docker {' '.join(args)} exited {done.returncode}")
    return json.loads(done.stdout)


def oci_problems(sandbox: Sandbox) -> tuple[list[str], dict[str, Any]]:
    """Why the OCI backend cannot run here, and what the manifest records about the daemon and image."""
    if sandbox.image is None or not _PINNED_IMAGE.fullmatch(sandbox.image):
        return [
            f"--oci-image must name an image pinned by digest (name@sha256:<64 hex>), not {sandbox.image!r}"
        ], {}
    if sandbox.runtime not in OCI_RUNTIMES:
        return [f"--oci-runtime must be one of {', '.join(OCI_RUNTIMES)}"], {}
    if shutil.which("docker", path=SYSTEM_PATH) is None:
        return [f"docker is not on {SYSTEM_PATH}"], {}
    problems: list[str] = []
    try:
        info = _docker_json("info")
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as exc:
        return [f"cannot reach the Docker daemon: {exc}"], {}
    options = [str(o) for o in info.get("SecurityOptions") or []]
    if any("rootless" in o or "userns" in o for o in options):
        problems.append(
            "the Docker daemon is rootless or remaps user namespaces; uid 65534 in the container would not "
            "own the work tree"
        )
    if sandbox.runtime not in (info.get("Runtimes") or {}):
        problems.append(f"the Docker daemon has no {sandbox.runtime} runtime")
    facts: dict[str, Any] = {"engine": "docker", "engine_version": info.get("ServerVersion")}
    try:
        image = _docker_json("image", "inspect", sandbox.image)
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError) as exc:
        problems.append(
            f"image {sandbox.image} is not present locally (pull it first; runs never pull): {exc}"
        )
        return problems, facts
    entry = image[0] if isinstance(image, list) and image else image
    facts["image_id"] = entry.get("Id")
    facts["image_repo_digests"] = sorted(entry.get("RepoDigests") or [])
    return problems, facts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument(
        "--tools", type=Path, required=True, help="tools.json: {tool_root, tools: {name: {bin, ...}}}"
    )
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", default="", help="comma-separated adapter names")
    ap.add_argument("--surfaces", default="", help="comma-separated surfaces to run")
    ap.add_argument("--cases", default="", help="comma-separated case ids")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--scratch", type=Path, default=None)
    ap.add_argument(
        "--checkouts", type=Path, default=None, help="directory of pinned repository checkouts for code cases"
    )
    ap.add_argument("--sandbox", choices=("namespaces", "oci"), default="namespaces")
    ap.add_argument(
        "--rlimit",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help=f"override a stage resource limit ({', '.join(f'{k}={v}' for k, v in DEFAULT_LIMITS.items())})",
    )
    ap.add_argument("--oci-image", default=None, help="image@sha256:<digest> the contained stage runs in")
    ap.add_argument("--oci-runtime", choices=OCI_RUNTIMES, default="runc", help="runsc runs under gVisor")
    ap.add_argument("--oci-memory", default="4g")
    ap.add_argument("--oci-cpus", default="2")
    ap.add_argument("--oci-pids", type=int, default=1024)
    args = ap.parse_args(argv)
    if os.geteuid() != 0:
        print(
            f"the runner needs root for unshare --net --pid --mount and to run tools as uid {TOOL_UID}",
            file=sys.stderr,
        )
        return 2
    if shutil.which("unshare", path=SYSTEM_PATH) is None:
        print(f"unshare (util-linux) is not on {SYSTEM_PATH}", file=sys.stderr)
        return 2
    corpus: Corpus = load_corpus(args.corpus)
    bad_ids = unsafe_ids(corpus.cases)
    if bad_ids:
        print("\n".join(bad_ids), file=sys.stderr)
        return 2
    env = ToolEnv.load(args.tools)
    repo = REPO
    try:
        limits = parse_limits(args.rlimit)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    sandbox = Sandbox(
        backend=args.sandbox,
        limits=limits,
        image=args.oci_image,
        runtime=args.oci_runtime,
        memory=args.oci_memory,
        cpus=args.oci_cpus,
        pids=args.oci_pids,
        binds=tool_binds(env) if args.sandbox == "oci" else (),
    )
    isolation_facts: dict[str, Any] = {}
    if sandbox.backend == "oci":
        oci, isolation_facts = oci_problems(sandbox)
        if oci:
            print("\n".join(oci), file=sys.stderr)
            return 2
    else:
        problem = namespace_problem()
        if problem:
            print(f"the stage's namespaces are not available: {problem}", file=sys.stderr)
            return 2
    adapters, problems = load_adapters()
    for name, problem in problems.items():
        print(f"adapter module {name} skipped: {problem}", file=sys.stderr)
    only = {s for s in args.only.split(",") if s}
    chosen = [a for n, a in adapters.items() if not only or n in only]
    cases = corpus.cases
    if args.surfaces:
        wanted = {s for s in args.surfaces.split(",") if s}
        cases = [c for c in cases if c.surface in wanted]
    if args.cases:
        ids = {s for s in args.cases.split(",") if s}
        cases = [c for c in cases if c.case_id in ids]
    scratch = prepare_scratch(args.scratch)
    isolation = isolation_problems(scratch, env)
    if isolation:
        print("\n".join(isolation), file=sys.stderr)
        return 2
    try:
        fakeproc = build_fakeproc(scratch / "fakeproc")
    except (OSError, subprocess.CalledProcessError) as exc:
        print(fakeproc_problem(exc), file=sys.stderr)
        return 2
    args.out.mkdir(parents=True, exist_ok=True)
    revision = harness_revision(repo)
    manifest: dict[str, Any] = {
        "started": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "harness_commit": revision["commit"],
        "harness_dirty": revision["dirty"],
        "corpus": str(args.corpus),
        "corpus_sha256": corpus_digest(args.corpus),
        "generator_digest": corpus.generator_digest,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "workers": args.workers,
        "isolation": {**sandbox.describe(), **isolation_facts},
        "tool_install": record_install(env.tool_root, args.out),
        "cases": len(cases),
        "tools": {},
        "skipped_adapters": problems,
    }
    for adapter in chosen:
        reason = adapter.unavailable_reason(env)
        if reason:
            print(f"{adapter.name}: not run ({reason})")
            manifest["tools"][adapter.name] = {"skipped": reason}
            continue
        print(f"{adapter.name}: running {len(cases)} cases ...", flush=True)
        summary = run_tool(
            adapter, cases, env, args.out, args.workers, scratch, repo, fakeproc, args.checkouts, sandbox
        )
        print(f"  {summary}")
        manifest["tools"][adapter.name] = summary
    manifest["finished"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
