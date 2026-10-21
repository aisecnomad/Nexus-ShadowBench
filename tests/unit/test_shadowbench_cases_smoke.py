"""The level-2 smoke check (tools/shadowbench/cases/smoke.py): harness failures fail, drift is reported."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools.shadowbench.cases import smoke


def _row(
    case: str, status: str = "ok", keys: tuple[str, ...] = (), incomplete: bool = False
) -> dict[str, Any]:
    return {
        "tool": "t",
        "case": case,
        "status": status,
        "entities": [{"key": k, "label": "agent"} for k in keys],
        "note": "boom" if status == "error" else "",
        "incomplete": incomplete,
    }


def _write(directory: Path, rows: list[dict[str, Any]], manifest: dict[str, Any] | None = None) -> Path:
    directory.mkdir(parents=True)
    (directory / "t.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    base = {
        "cases": len(rows),
        "isolation": {"backend": "namespaces"},
        "tool_install": {"resolved": {"SHA256SUMS": "0" * 64}},
        "tools": {"t": {"version": "1"}},
    }
    (directory / "manifest.json").write_text(json.dumps({**base, **(manifest or {})}), encoding="utf-8")
    return directory


def test_a_clean_run_passes_and_lists_its_drift(tmp_path: Path) -> None:
    baseline = _write(tmp_path / "base", [_row("a", keys=("app:1",)), _row("b"), _row("c", "unsupported")])
    run = _write(
        tmp_path / "run", [_row("a", keys=("app:1",)), _row("b", keys=("app:2",)), _row("c", "unsupported")]
    )
    problems, report = smoke.check(run, baseline)
    assert problems == []
    assert report["t"]["cases"] == 2
    assert report["t"]["drift"] == [{"case": "b", "added": ["app:2"], "removed": []}]
    summary = tmp_path / "summary.md"
    assert smoke.main(["--results", str(run), "--baseline", str(baseline), "--summary", str(summary)]) == 0
    assert "`b`: +1" in summary.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("rows", "manifest", "expected"),
    [
        ([_row("a", "error")], None, "t a: error: boom"),
        ([_row("a", incomplete=True)], None, "t a: incomplete"),
        ([_row("a")], {"isolation": None}, "the manifest records no isolation"),
        ([_row("a")], {"tool_install": {"resolved": None}}, "no resolved tool install"),
        ([_row("a")], {"cases": 2}, "t: 1 rows for 2 cases"),
        ([_row("a")], {"tools": {"t": {"skipped": "no binary"}}}, "no tool ran"),
    ],
)
def test_harness_problems_fail(
    tmp_path: Path, rows: list[dict[str, Any]], manifest: dict[str, Any] | None, expected: str
) -> None:
    run = _write(tmp_path / "run", rows, manifest)
    problems, _ = smoke.check(run, tmp_path / "missing-baseline")
    assert any(expected in p for p in problems), problems
    assert smoke.main(["--results", str(run), "--baseline", str(tmp_path)]) == 1


@pytest.mark.parametrize(
    ("manifest", "expected"),
    [
        (
            {"tools": {"t": {"version": "1"}}, "skipped_adapters": {"other": "ImportError: x"}},
            "adapter module other did not load",
        ),
        ({"tools": {"t": {"version": "1"}, "u": {"skipped": "no bin"}}}, "u: expected, but not run (no bin)"),
        ({"tools": {"t": {"version": "1"}}}, "u: expected, but the manifest does not list it"),
    ],
)
def test_an_expected_tool_that_did_not_run_fails(
    tmp_path: Path, manifest: dict[str, Any], expected: str
) -> None:
    """A skipped or unloaded tool left the smoke job green as long as another tool ran."""
    run = _write(tmp_path / "run", [_row("a")], manifest)
    problems, _ = smoke.check(run, tmp_path / "base", expect=("t", "u"))
    assert any(expected in p for p in problems), problems


def test_an_expected_tool_with_only_unsupported_rows_fails(tmp_path: Path) -> None:
    run = _write(tmp_path / "run", [_row("a", "unsupported")])
    problems, _ = smoke.check(run, tmp_path / "base", expect=("t",))
    assert "t: expected, but every row is unsupported" in problems
