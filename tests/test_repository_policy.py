"""Repository policy: labels exist before anything applies them, and workflows stay pinned.

Issue forms and Dependabot apply labels that GitHub silently skips when the
label does not exist, so both may only use labels from .github/labels.yml,
which the Labels workflow syncs to the tracker. Every workflow pins each
action to a full commit SHA and each job to a named runner image, declares
its token permissions, checks out without persisting credentials and expands
no expression inside a script. `make audit` audits the locks CI audits, and
every suppressed broad `except` or security rule carries its reason.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
GITHUB = ROOT / ".github"
WORKFLOWS = sorted((GITHUB / "workflows").glob("*.yml"))
_PINNED = re.compile(r"^[\w.-]+/[\w.-]+(?:/[\w./-]+)?@[0-9a-f]{40}$")


def _yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _labels() -> list[dict[str, Any]]:
    labels = _yaml(GITHUB / "labels.yml")
    assert isinstance(labels, list)
    return labels


def _steps(workflow: dict[str, Any]) -> list[dict[str, Any]]:
    return [step for job in workflow["jobs"].values() for step in job.get("steps", [])]


def test_labels_file_is_well_formed():
    labels = _labels()
    names = [label["name"] for label in labels]
    assert len(names) == len(set(names))
    for label in labels:
        assert set(label) <= {"name", "color", "description"}, label
        assert isinstance(label["name"], str) and label["name"].strip(), label
        assert re.fullmatch(r"[0-9a-fA-F]{6}", label["color"]), label
        assert len(label.get("description", "")) <= 100, label


def test_issue_forms_and_dependabot_only_use_defined_labels():
    defined = {label["name"] for label in _labels()}
    used: dict[str, set[str]] = {}
    for form in sorted((GITHUB / "ISSUE_TEMPLATE").glob("*.yml")):
        if form.name != "config.yml":
            used[form.name] = set(_yaml(form).get("labels", []))
    for update in _yaml(GITHUB / "dependabot.yml")["updates"]:
        used.setdefault("dependabot.yml", set()).update(update.get("labels", []))
    assert used
    assert {name: sorted(labels - defined) for name, labels in used.items() if labels - defined} == {}


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_workflow_actions_are_pinned_and_least_privileged(path: Path):
    workflow = _yaml(path)
    assert "permissions" in workflow, "declare top-level token permissions"
    for step in _steps(workflow):
        uses = step.get("uses")
        if uses is None:
            continue
        assert _PINNED.match(uses), f"{uses} is not pinned to a full commit SHA"
        if uses.startswith("actions/checkout@"):
            assert step.get("with", {}).get("persist-credentials") is False, uses


# GitHub's YAML loader reads the bare key `on` as True; PyYAML does the same.
def _triggers(workflow: dict[Any, Any]) -> set[str]:
    on = workflow.get("on", workflow.get(True))
    return {on} if isinstance(on, str) else set(on or ())


# Any expression in a script, not only the contexts known to carry untrusted text: a branch name
# (github.ref_name) can hold `$(...)`, and a step output or env value can carry whatever produced it.
_INJECTABLE = re.compile(r"\$\{\{")
_OIDC_JOBS = {("attest.yml", "attest"), ("scorecard.yml", "analysis")}


def _scripts(step: dict[str, Any]) -> list[str]:
    """What a step runs as code: its shell script, or an actions/github-script script."""
    scripts = [step.get("run", "")]
    if str(step.get("uses", "")).startswith("actions/github-script@"):
        scripts.append(str(step.get("with", {}).get("script", "")))
    return scripts


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_workflows_avoid_privileged_triggers_blanket_tokens_and_script_injection(path: Path):
    """Privileged triggers run with secrets on a fork's code; an expression GitHub expands into a
    script runs whatever an issue title, branch name or input says. Values reach scripts through env.
    """
    workflow = _yaml(path)
    assert not _triggers(workflow) & {"pull_request_target", "workflow_run"}
    jobs = workflow["jobs"]
    for scope in [workflow, *jobs.values()]:
        permissions = scope.get("permissions", {})
        assert isinstance(permissions, dict), f"{path.name}: permissions must name each scope"
    assert workflow["permissions"].get("id-token") is None, "grant id-token to a job, not the workflow"
    for name, job in jobs.items():
        if job.get("uses") is not None:
            assert _PINNED.match(job["uses"]), f"{job['uses']} is not pinned to a full commit SHA"
        if job.get("permissions", {}).get("id-token") == "write":
            assert (path.name, name) in _OIDC_JOBS, f"{path.name}:{name} may not mint OIDC tokens"
    for step in _steps(workflow):
        for script in _scripts(step):
            assert not _INJECTABLE.search(script), f"{path.name}: {step.get('name')}"


def test_unpinned_actions_are_detected():
    assert _PINNED.match("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1")
    assert _PINNED.match("github/codeql-action/init@6f2ac81f5cd81fe351a197ba0b00d91d03cd2aee")
    assert not _PINNED.match("actions/checkout@v7")
    assert not _PINNED.match("actions/checkout@main")


def test_every_scanner_checkout_uses_the_makefile_pin():
    pin = re.search(r"^SCANNER_COMMIT := ([0-9a-f]{40})$", (ROOT / "Makefile").read_text(), re.M)
    assert pin is not None
    refs = [
        step["with"].get("ref")
        for path in WORKFLOWS
        for step in _steps(_yaml(path))
        if step.get("with", {}).get("repository") == "aisecnomad/Nexus-ShadowScan"
    ]
    assert refs and set(refs) == {pin.group(1)}


# The cases track's installer and the build backend it builds sdists with: they run as root in
# install_tools.sh, unlike the tools under test, whose locks pin what is measured.
TOOLCHAIN_LOCKS = {"tools/shadowbench/cases/locks/uv.txt", "tools/shadowbench/cases/locks/build.txt"}


def _audited(script: str) -> set[str]:
    """The locks a `for lock in ...; do pip-audit ...` loop audits."""
    loop = re.search(r"for lock in ([^;]+);", script)
    assert loop is not None, "no `for lock in ...` audit loop"
    return set(loop.group(1).replace("\\", " ").split())


def _ci_audit() -> str:
    scripts = [step.get("run", "") for step in _steps(_yaml(GITHUB / "workflows" / "ci.yml"))]
    return next(script for script in scripts if "pip-audit --skip-editable" in script)


def test_ci_audits_every_lock_it_installs():
    workflow = _yaml(GITHUB / "workflows" / "ci.yml")
    scripts = [step.get("run", "") for step in _steps(workflow)]
    installed = {lock for script in scripts for lock in re.findall(r"-r (requirements[\w-]*\.lock)", script)}
    audit = _ci_audit()
    audited = _audited(audit)
    assert installed and audited == installed | TOOLCHAIN_LOCKS
    assert all((ROOT / lock).is_file() for lock in audited)
    assert "--require-hashes --strict" in audit
    assert "migration/requirements.source.lock" not in audited


def test_make_audit_audits_what_ci_audits():
    """`make check` stands in for CI locally, so a lock CI audits and `make audit` skips passes there."""
    recipe = re.search(r"^audit:.*\n((?:\t.*\n)+)", (ROOT / "Makefile").read_text(encoding="utf-8"), re.M)
    assert recipe is not None, "no audit target in the Makefile"
    assert "pip-audit --skip-editable" in recipe.group(1)
    assert "--require-hashes --strict" in recipe.group(1)
    assert _audited(recipe.group(1)) == _audited(_ci_audit())


def test_historical_signature_verification_is_strict_and_independent_of_dependency_audits():
    workflow = _yaml(GITHUB / "workflows" / "ci.yml")
    job = workflow["jobs"]["attestations"]
    assert not job.get("needs"), "a dependency job failure must not skip attestation verification"
    assert "if" not in job and not job.get("continue-on-error")
    steps = job["steps"]
    scripts = [step.get("run", "") for step in steps]
    assert all("pip" not in script for script in scripts), "verification needs no Python dependencies"
    verification = [step for step in steps if "-m tools.attest verify" in step.get("run", "")]
    assert len(verification) == 1
    step = verification[0]
    assert "if" not in step and not step.get("continue-on-error")
    assert step["run"].startswith("python -m tools.attest verify --require-signatures ")
    assert '--since "$BASE_SHA"' in step["run"] and "||" not in step["run"]

    # Both explicit CI invocation and the Makefile used by weekly rescores must be strict.
    invocations = [
        line.strip()
        for step in _steps(workflow)
        for line in step.get("run", "").splitlines()
        if "-m tools.attest verify" in line
    ]
    assert len(invocations) == 2 and all("--require-signatures" in line for line in invocations)
    recipe = re.search(r"^verify:.*\n((?:\t.*\n)+)", (ROOT / "Makefile").read_text(encoding="utf-8"), re.M)
    assert recipe is not None
    assert "-m tools.attest verify --require-signatures" in recipe.group(1)


def test_every_signature_verification_job_installs_the_signing_workflows_cosign_version():
    workflow = _yaml(GITHUB / "workflows" / "ci.yml")
    signing_steps = _yaml(GITHUB / "workflows" / "attest.yml")["jobs"]["attest"]["steps"]
    signing_installer = next(
        step for step in signing_steps if step.get("uses", "").startswith("sigstore/cosign-installer@")
    )
    # The repository-level pytest regression verifies actual committed signatures on both Pythons.
    for name in ("attestations", "tests", "tests-latest-python"):
        steps = workflow["jobs"][name]["steps"]
        installers = [
            (index, step)
            for index, step in enumerate(steps)
            if step.get("uses", "").startswith("sigstore/cosign-installer@")
        ]
        assert len(installers) == 1, name
        index, installer = installers[0]
        assert "if" not in installer and not installer.get("continue-on-error"), name
        assert installer["uses"] == signing_installer["uses"], name
        assert installer["with"]["cosign-release"] == signing_installer["with"]["cosign-release"], name
        verification = next(
            i
            for i, step in enumerate(steps)
            if "-m tools.attest verify" in step.get("run", "") or "-m pytest" in step.get("run", "")
        )
        assert index < verification, name


def test_the_toolchain_locks_are_the_installers_install_tools_uses():
    script = (ROOT / "tools/shadowbench/cases/install_tools.sh").read_text(encoding="utf-8")
    smoke = (GITHUB / "workflows" / "rescore.yml").read_text(encoding="utf-8")
    assert '"$locks/build.txt"' in script and "-r tools/shadowbench/cases/locks/uv.txt" in smoke


def test_script_injection_and_privileged_triggers_are_detected():
    assert _INJECTABLE.search('echo "${{ github.event.pull_request.title }}"')
    assert _INJECTABLE.search("python -m tools.attest digest ${{inputs.results}}")
    assert _INJECTABLE.search('git push origin "${{ github.ref_name }}"')
    assert _INJECTABLE.search("echo ${{ steps.meta.outputs.tag }}")
    assert not _INJECTABLE.search('python -m tools.attest digest "$RESULTS"')
    script = {
        "uses": "actions/github-script@" + "0" * 40,
        "with": {"script": "${{ github.event.issue.title }}"},
    }
    assert any(_INJECTABLE.search(text) for text in _scripts(script))
    assert _triggers(yaml.safe_load("on: pull_request_target")) == {"pull_request_target"}
    assert _triggers(yaml.safe_load("on: {push: {}, workflow_run: {}}")) == {"push", "workflow_run"}


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_jobs_run_on_a_named_runner_image(path: Path):
    """A `-latest` label moves to a new OS image unannounced, under the byte-for-byte re-scores and
    the sandbox; moving the image is a reviewed change like moving a lock."""
    for name, job in _yaml(path)["jobs"].items():
        if "uses" in job:
            continue
        runs_on = job.get("runs-on")
        labels = [runs_on] if isinstance(runs_on, str) else list(runs_on or ())
        assert labels, f"{path.name}:{name} has no runs-on"
        assert not [label for label in labels if str(label).endswith("-latest")], f"{path.name}:{name}"


# A suppressed broad `except` or security rule is a reviewed decision, and pyproject.toml says the
# reason is written beside it (`noqa: BLE001 - <reason>`). Ruff's E, W, SIM and the other rules
# need none.
_NOQA = re.compile(r"#\s*noqa:\s*([A-Z]+[0-9]+(?:\s*,\s*[A-Z]+[0-9]+)*)(.*)")
_REVIEWED = re.compile(r"(?:BLE|S)[0-9]+")


def _unexplained_suppressions(line: str) -> list[str]:
    match = _NOQA.search(line)
    if match is None or re.match(r"\s+-\s+\S", match.group(2)):
        return []
    return [code for code in re.split(r"\s*,\s*", match.group(1)) if _REVIEWED.fullmatch(code)]


def test_broad_except_and_security_suppressions_carry_a_reason():
    artifacts = ROOT / "benchmarks" / "shadowbench" / "estate" / "artifacts"
    unexplained = []
    for top in ("tools", "tests", "benchmarks"):
        for path in sorted((ROOT / top).rglob("*.py")):
            if artifacts in path.parents:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if codes := _unexplained_suppressions(line):
                    unexplained.append(f"{path.relative_to(ROOT)}:{number}: {', '.join(codes)}")
    assert unexplained == []


def test_unexplained_suppressions_are_detected():
    noqa = "# " + "noqa"  # spelt apart, so these fixtures are not suppressions in this file
    assert _unexplained_suppressions(f"except Exception:  {noqa}: BLE001") == ["BLE001"]
    assert _unexplained_suppressions(f"run(cmd)  {noqa}: S603, E501") == ["S603"]
    assert _unexplained_suppressions(f"except Exception:  {noqa}: BLE001 - report every row") == []
    assert _unexplained_suppressions(f"x = 1  {noqa}: E501") == []
    assert _unexplained_suppressions(f"with suppress():  {noqa}: SIM105") == []
