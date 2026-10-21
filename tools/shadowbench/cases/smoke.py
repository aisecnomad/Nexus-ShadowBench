"""Check a level-2 smoke run of the cases runner and report how it drifts from a committed run.

``python -m tools.shadowbench.cases.smoke --results RUN --baseline <committed run directory>``
(``--summary FILE`` appends a Markdown summary, such as ``$GITHUB_STEP_SUMMARY``)

A smoke run installs a few tools from their locks and runs them in the sandbox on a few surfaces.
It fails (exit 1) when the harness did not do its job: a tool the manifest says ran wrote no rows,
a row is an ``error`` or ``incomplete``, a case has no row, or the manifest does not record the
sandbox or the tool install. It never fails on drift: each case whose reported keys differ from
the baseline run's rows for the same tool and case is listed, since the baseline was recorded by
earlier adapters under weaker isolation, and tools resolved their dependencies at install time
then. Drift is evidence to read, not a regression gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SHOWN = 20
"""Drifting cases listed per tool in the summary."""


def _rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            rows[str(row["case"])] = row
    return rows


def _keys(row: dict[str, Any] | None) -> set[str]:
    return {str(e["key"]) for e in (row or {}).get("entities") or []}


def check(results: Path, baseline: Path) -> tuple[list[str], dict[str, Any]]:
    """Harness problems in ``results`` and, per tool, its drift from ``baseline``."""
    manifest = json.loads((results / "manifest.json").read_text(encoding="utf-8"))
    problems: list[str] = []
    if not isinstance(manifest.get("isolation"), dict):
        problems.append("the manifest records no isolation")
    if not (manifest.get("tool_install") or {}).get("resolved"):
        problems.append("the manifest records no resolved tool install (install_tools.sh's resolved/)")
    report: dict[str, Any] = {}
    ran = {name: run for name, run in (manifest.get("tools") or {}).items() if not run.get("skipped")}
    if not ran:
        problems.append("no tool ran")
    for tool, run in sorted(ran.items()):
        rows = _rows(results / f"{tool}.jsonl")
        if not rows:
            problems.append(f"{tool}: no rows")
            continue
        if len(rows) != int(manifest.get("cases") or 0):
            problems.append(f"{tool}: {len(rows)} rows for {manifest.get('cases')} cases")
        scored = {cid: row for cid, row in rows.items() if row["status"] != "unsupported"}
        for cid, row in sorted(scored.items()):
            if row["status"] != "ok":
                problems.append(f"{tool} {cid}: {row['status']}: {str(row.get('note'))[:200]}")
            elif row.get("incomplete"):
                problems.append(f"{tool} {cid}: incomplete: {str(row.get('note'))[:200]}")
        base = _rows(baseline / f"{tool}.jsonl")
        drift = [
            {
                "case": cid,
                "added": sorted(_keys(row) - _keys(base.get(cid))),
                "removed": sorted(_keys(base.get(cid)) - _keys(row)),
            }
            for cid, row in sorted(scored.items())
            if base and _keys(row) != _keys(base.get(cid))
        ]
        report[tool] = {
            "version": run.get("version"),
            "cases": len(scored),
            "with_entities": sum(1 for row in scored.values() if row.get("entities")),
            "baseline": bool(base),
            "drift": drift,
        }
    return problems, report


def summary(problems: list[str], report: dict[str, Any]) -> str:
    lines = ["## Cases smoke run", ""]
    lines.append("**Harness problems:** none" if not problems else f"**Harness problems ({len(problems)}):**")
    lines += [f"- {p}" for p in problems[:50]]
    lines += [
        "",
        "| Tool | Version | Cases | With entities | Drifting from baseline |",
        "|---|---|---|---|---|",
    ]
    for tool, entry in report.items():
        drift = len(entry["drift"]) if entry["baseline"] else "no baseline"
        lines.append(
            f"| {tool} | {entry['version']} | {entry['cases']} | {entry['with_entities']} | {drift} |"
        )
    for tool, entry in report.items():
        if not entry["drift"]:
            continue
        lines += ["", f"### {tool}: cases whose keys differ from the baseline", ""]
        for item in entry["drift"][:SHOWN]:
            added, removed = item["added"], item["removed"]
            lines.append(f"- `{item['case']}`: +{len(added)} {added[:3]} -{len(removed)} {removed[:3]}")
        if len(entry["drift"]) > SHOWN:
            lines.append(f"- ... and {len(entry['drift']) - SHOWN} more")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--baseline", type=Path, required=True)
    ap.add_argument("--summary", type=Path, default=None)
    args = ap.parse_args(argv)
    problems, report = check(args.results, args.baseline)
    text = summary(problems, report)
    print(text)
    if args.summary is not None:
        with args.summary.open("a", encoding="utf-8") as handle:
            handle.write(text)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
