"""Repository policy: labels exist before anything applies them, and workflows stay pinned.

Issue forms and Dependabot apply labels that GitHub silently skips when the
label does not exist, so both may only use labels from .github/labels.yml,
which the Labels workflow syncs to the tracker. Every workflow pins each
action to a full commit SHA, declares its token permissions and checks out
without persisting credentials.
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


def test_ci_audits_every_lock_it_installs():
    workflow = _yaml(GITHUB / "workflows" / "ci.yml")
    scripts = [step.get("run", "") for step in _steps(workflow)]
    installed = {lock for script in scripts for lock in re.findall(r"-r (requirements[\w-]*\.lock)", script)}
    audit = next(script for script in scripts if "pip-audit --skip-editable" in script)
    audited = set(re.search(r"for lock in ([^;]+);", audit).group(1).split())
    assert installed and installed == audited
    assert "--require-hashes --strict" in audit
    assert "migration/requirements.source.lock" not in audited
