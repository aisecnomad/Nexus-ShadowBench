"""Regression checks for the signing workflow's trigger and command boundaries.

Command doubles exercise shell routing and failure propagation only. They do
not generate signatures or establish any historical signing evidence.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

from tools.attest import REQUIRED_SUBJECTS

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/attest.yml"


def _workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def test_signing_trigger_and_permissions_stay_narrow() -> None:
    workflow = _workflow()
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"push", "workflow_dispatch"}
    assert triggers["push"] == {"branches": ["main"], "paths": [".github/workflows/attest.yml"]}
    assert triggers["workflow_dispatch"]["inputs"]["results"]["required"] is True
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["attest"]
    assert job["if"] == "github.ref == 'refs/heads/main'"
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    assert not job.get("continue-on-error", False)
    steps = job["steps"]
    assert steps[-1]["uses"].startswith("actions/upload-artifact@")
    assert steps[-1].get("if", "success()") == "success()"
    assert steps[-1]["with"]["path"] == "attestations/"
    assert all(not step.get("continue-on-error", False) for step in steps)
    assert "tools.attest verify" in steps[-2]["run"]


_DOUBLE = """import json
import os
import sys
from pathlib import Path

name = Path(sys.argv[0]).name
args = sys.argv[1:]
log = Path(os.environ["CALLS"])
with log.open("a", encoding="utf-8") as stream:
    stream.write(json.dumps([name, *args]) + "\\n")
phase = "sign" if name == "cosign" else (
    "digest" if args[2] == "digest" else "preflight" if "--since" in args else "verify"
)
if phase == os.environ.get("FAIL_PHASE"):
    sys.exit(23)
if phase == "digest":
    count = sum(json.loads(line)[3] == "digest" for line in log.read_text().splitlines())
    print(f"attestations/manifest-{count}.json")
if phase == "sign":
    bundle = Path(args[args.index("--bundle") + 1])
    bundle.parent.mkdir(exist_ok=True)
    bundle.write_text("test fixture only", encoding="utf-8")
"""


def _run_scripts(
    tmp_path: Path,
    event: str,
    results: str = "",
    *,
    fail_phase: str = "",
    preserve_bundle: bool = False,
) -> tuple[list[list[str]], list[int]]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("python", "cosign"):
        executable = bin_dir / name
        executable.write_text(f"#!{sys.executable}\n{_DOUBLE}", encoding="utf-8")
        executable.chmod(0o755)
    if preserve_bundle:
        bundle = tmp_path / "attestations/manifest-1.sigstore.json"
        bundle.parent.mkdir()
        bundle.write_text("preserved test fixture", encoding="utf-8")
    log = tmp_path / "calls.jsonl"
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.defpath}",
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_EVENT_NAME": event,
        "GITHUB_SHA": "a" * 40,
        "RESULTS": results,
        "CALLS": str(log),
        "FAIL_PHASE": fail_phase,
    }
    codes = []
    for step in _workflow()["jobs"]["attest"]["steps"]:
        if "run" not in step:
            continue
        done = subprocess.run(
            ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", step["run"]],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        codes.append(done.returncode)
        if done.returncode:
            break
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    return calls, codes


def test_push_signs_exactly_the_three_preserved_runs_and_verifies_strictly(tmp_path: Path) -> None:
    calls, codes = _run_scripts(tmp_path, "push", results="ignored input")
    assert codes == [0, 0, 0, 0]
    assert [call[-1] for call in calls if call[:4] == ["python", "-m", "tools.attest", "digest"]] == list(
        REQUIRED_SUBJECTS
    )
    assert calls[3] == ["python", "-m", "tools.attest", "verify", "--since", "a" * 40]
    assert [call for call in calls if call[0] == "cosign"] == [
        [
            "cosign",
            "sign-blob",
            "--yes",
            "--bundle",
            f"attestations/manifest-{n}.sigstore.json",
            f"attestations/manifest-{n}.json",
        ]
        for n in (1, 2, 3)
    ]
    assert calls[-1] == ["python", "-m", "tools.attest", "verify", "--require-signatures"]


def test_dispatch_preserves_one_quoted_argument_and_single_target(tmp_path: Path) -> None:
    value = "benchmarks/a; touch injected; $(touch expanded)"
    calls, codes = _run_scripts(tmp_path, "workflow_dispatch", results=value)
    assert codes == [0, 0, 0, 0]
    assert calls[0] == ["python", "-m", "tools.attest", "digest", value]
    assert len([call for call in calls if call[0] == "cosign"]) == 1
    assert calls[-1] == ["python", "-m", "tools.attest", "verify"]
    assert not (tmp_path / "injected").exists()
    assert not (tmp_path / "expanded").exists()


def test_existing_bundles_are_retained_and_still_verified(tmp_path: Path) -> None:
    calls, codes = _run_scripts(tmp_path, "push", preserve_bundle=True)
    assert codes == [0, 0, 0, 0]
    assert len([call for call in calls if call[0] == "cosign"]) == 2
    assert (tmp_path / "attestations/manifest-1.sigstore.json").read_text() == "preserved test fixture"
    assert calls[-1][-1] == "--require-signatures"


@pytest.mark.parametrize("phase", ["digest", "preflight", "sign", "verify"])
def test_failure_in_any_phase_stops_the_workflow(tmp_path: Path, phase: str) -> None:
    calls, codes = _run_scripts(tmp_path, "push", fail_phase=phase)
    assert codes[-1] == 23
    if phase in {"digest", "preflight"}:
        assert not any(call[0] == "cosign" for call in calls)
    if phase != "verify":
        assert "--require-signatures" not in calls[-1]
