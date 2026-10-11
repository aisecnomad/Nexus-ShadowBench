#!/usr/bin/env python3
"""Run ShadowBench against the ten discovery tools and a lexicon reference.

Raw tool output is kept under results/raw. Scoring is a pure function of that
output plus truth.json. Tools that cannot run are recorded as not-run; they
are not given a fake F1 of zero.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from generate_corpus import CORPUS, generate
from score import load_cases, map_strings, score_tool

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
RAW = RESULTS / "raw"
PY = Path("/tmp/bench-venv312/bin")
AIBOM = Path("/tmp/venvs/aibom/bin/ai-bom")
RADAR = Path("/tmp/venvs/radar/bin/agentic-radar")
VET = Path("/tmp/bins/vet")
NUMBAT = Path("/tmp/bins/numbat")
EMPTY_HOME = Path("/tmp/fg-empty-home")

# Declared before any score is computed. A surface is in scope only when the
# tool documents a way to read that artifact format.
SCOPE = {
    "shadowscan": {"code", "identity", "gateway", "lowcode", "saas", "cloud", "endpoint", "network", "runtime"},
    "vet": {"code", "endpoint"},
    "numbat": {"endpoint"},
    "ai-bom": {"code", "lowcode"},
    "nuguard": {"code"},
    "agentdiscover": {"code"},
    "agentic-radar": {"code", "lowcode"},
    "snyk-agent-scan": {"endpoint"},
    "aiostack": {"runtime"},
    "curatedmcp": {"endpoint"},
    "reference-lexicon": {"code", "identity", "gateway", "lowcode", "saas", "cloud", "endpoint", "network", "runtime"},
}

TEN = [
    "shadowscan",
    "vet",
    "numbat",
    "snyk-agent-scan",
    "ai-bom",
    "nuguard",
    "agentdiscover",
    "agentic-radar",
    "aiostack",
    "curatedmcp",
]


def env_for(home: Path | None = None) -> dict:
    env = os.environ.copy()
    env["HOME"] = str(home or EMPTY_HOME)
    env["NO_COLOR"] = "1"
    env.pop("OPENAI_API_KEY", None)
    env.pop("SNYK_TOKEN", None)
    env.pop("AWS_ACCESS_KEY_ID", None)
    env.pop("AWS_SECRET_ACCESS_KEY", None)
    return env


def run_cmd(cmd: list[str], cwd: Path, timeout: int, home: Path | None = None) -> dict:
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env_for(home),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "exit": proc.returncode,
            "stdout": proc.stdout[:80_000],
            "stderr": proc.stderr[:20_000],
            "ms": int((time.perf_counter() - started) * 1000),
            "error": None,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "exit": None,
            "stdout": (exc.stdout or "")[:20_000] if isinstance(exc.stdout, str) else "",
            "stderr": "timeout",
            "ms": int((time.perf_counter() - started) * 1000),
            "error": "timeout",
        }
    except OSError as exc:
        return {"exit": None, "stdout": "", "stderr": str(exc), "ms": 0, "error": "oserror"}


def iter_strings(obj, key: str = "", out: list[str] | None = None) -> list[str]:
    if out is None:
        out = []
    if len(out) > 500:
        return out
    if key in {"stderr", "stdout", "banner", "raw"}:
        return out
    if isinstance(obj, str):
        if obj and len(obj) < 500:
            out.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            iter_strings(v, k, out)
    elif isinstance(obj, list):
        for item in obj[:300]:
            iter_strings(item, key, out)
    return out


def load_json(path: Path) -> object | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("{") or line.startswith("["):
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return rows or None


def select_strings(parsed) -> list[str]:
    """Pull claim strings, not rule catalogs or tool metadata."""
    if parsed is None:
        return []
    if isinstance(parsed, list):
        strings: list[str] = []
        for item in parsed:
            strings.extend(select_strings(item))
        return strings
    if isinstance(parsed, dict):
        if "findings" in parsed and "finding_identity_schema" in parsed:
            return iter_strings(parsed.get("findings"))
        if "runs" in parsed:
            results = []
            for run in parsed.get("runs") or []:
                results.extend(run.get("results") or [])
            return iter_strings(results)
        if parsed.get("bomFormat") and "components" in parsed:
            return iter_strings(parsed.get("components"))
        if "deps" in parsed or "nodes" in parsed:
            return iter_strings({"deps": parsed.get("deps"), "nodes": parsed.get("nodes")})
        if "tables_text" in parsed:
            return [s for s in parsed["tables_text"] if isinstance(s, str)]
        return iter_strings(parsed)
    if isinstance(parsed, str):
        return [parsed[:500]]
    return []


def findings_from_result(result: dict, surface: str) -> list[dict]:
    strings = select_strings(result.get("parsed"))
    if not strings and result.get("stdout"):
        strings = [line for line in result["stdout"].splitlines() if line.strip()][:200]
    return map_strings(strings, surface)


def artifact_text(case_dir: Path) -> str:
    chunks = []
    for path in case_dir.rglob("*"):
        if not path.is_file() or path.name == "truth.json" or path.stat().st_size >= 100_000:
            continue
        rel = path.relative_to(case_dir).as_posix()
        chunks.append(rel)
        chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


def reference_scan(case: dict) -> dict:
    text = artifact_text(CORPUS / case["surface"] / case["id"])
    return {"findings": map_strings([text], case["surface"]), "error": False, "ms": 0, "exit": 0}


def shadowscan(case: dict, out: Path) -> dict:
    case_dir = CORPUS / case["surface"] / case["id"]
    binary = str(PY / "shadowscan")
    surface = case["surface"]
    if surface == "code":
        cmd = [binary, "code", str(case_dir), "-f", "json", "-o", str(out), "--no-incremental", "--connector-timeout-seconds", "20"]
    elif surface == "identity":
        cmd = [binary, "run", "identity.okta", "--input", str(case_dir / "okta-apps.json"), "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    elif surface == "gateway":
        cmd = [binary, "gateway", str(case_dir / "spend.jsonl"), "--log-format", "litellm", "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    elif surface == "lowcode":
        cmd = [binary, "run", "lowcode.n8n", "--input", str(case_dir / "workflow.json"), "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    elif surface == "saas":
        cmd = [binary, "run", "saas.slack", "--input", str(case_dir / "approved-app.json"), "--set", "team_id=T000BENCH", "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    elif surface == "cloud":
        cmd = [binary, "run", "cloud.aws", "--input", str(case_dir / "aws.jsonl"), "--set", "account_id=123456789012", "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    elif surface == "endpoint":
        cmd = [binary, "run", "endpoint.inventory", "--set", f"path={case_dir / 'home'}", "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    elif surface == "network":
        cmd = [binary, "run", "network.logs", "--input", str(case_dir / "dns.jsonl"), "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    else:
        cmd = [binary, "run", "runtime.processes", "--input", str(case_dir / "processes.json"), "-f", "json", "-o", str(out), "--connector-timeout-seconds", "20"]
    result = run_cmd(cmd, case_dir, 45)
    result["parsed"] = load_json(out)
    return result


def vet_scan(case: dict, out: Path) -> dict:
    case_dir = CORPUS / case["surface"] / case["id"]
    target = case_dir / "home" if case["surface"] == "endpoint" else case_dir
    db = out.with_suffix(".db")
    report = out.with_suffix(".discover.json")
    code = run_cmd([
        str(VET), "code", "scan", "--app", str(target), "--db", str(db), "--no-tui", "--no-banner",
    ], target, 40)
    discover = run_cmd([
        str(VET), "ai", "discover", "-D", str(target), "--scope", "project", "--report-json", str(report), "--no-banner", "--silent",
    ], target, 30, home=target if case["surface"] == "endpoint" else None)
    parsed: list = []
    if report.exists():
        parsed.append(load_json(report))
    if db.exists():
        parsed.append(sqlite_text(db))
    return {
        "exit": code["exit"] if code["exit"] not in (None, 0) else discover["exit"],
        "stdout": (code["stdout"] + "\n" + discover["stdout"])[:80_000],
        "stderr": (code["stderr"] + "\n" + discover["stderr"])[:20_000],
        "ms": code["ms"] + discover["ms"],
        "error": code["error"] or discover["error"],
        "parsed": parsed,
    }


def sqlite_text(db: Path) -> dict:
    import sqlite3

    try:
        conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        return {"sqlite_error": str(exc)}
    blobs: list[str] = []
    try:
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
            text_cols = cols[:12]
            if not text_cols:
                continue
            quoted = ", ".join(text_cols)
            try:
                for row in conn.execute(f"SELECT {quoted} FROM {table} LIMIT 200"):
                    for cell in row:
                        if isinstance(cell, str) and cell:
                            blobs.append(cell[:400])
            except sqlite3.Error:
                continue
    finally:
        conn.close()
    return {"tables_text": blobs}


def numbat_scan(case: dict, out: Path) -> dict:
    home = CORPUS / case["surface"] / case["id"] / "home"
    result = run_cmd([str(NUMBAT), "scan", "--path", str(home), "--emit", "findings"], home, 30, home=home)
    result["parsed"] = load_json(Path("/dev/null"))
    rows = []
    for line in result["stdout"].splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append(line)
    result["parsed"] = rows
    out.write_text(result["stdout"], encoding="utf-8")
    return result


def aibom_scan(case: dict, out: Path) -> dict:
    target = CORPUS / case["surface"] / case["id"]
    result = run_cmd([str(AIBOM), "scan", str(target), "-f", "json", "-o", str(out), "-q", "--no-color"], target, 40)
    result["parsed"] = load_json(out)
    return result


def nuguard_scan(case: dict, out: Path) -> dict:
    target = CORPUS / case["surface"] / case["id"]
    result = run_cmd([
        str(PY / "nuguard"), "sbom", "generate", "-s", str(target), "-o", str(out), "--no-llm",
    ], target, 60)
    result["parsed"] = load_json(out)
    return result


def agentdiscover_scan(case: dict, out: Path) -> dict:
    target = CORPUS / case["surface"] / case["id"]
    result = run_cmd([
        str(PY / "agentdiscover"), "scan", str(target), "--format", "sarif", "--output", str(out),
    ], target, 40)
    result["parsed"] = load_json(out)
    return result


def radar_scan(case: dict, out: Path) -> dict:
    target = CORPUS / case["surface"] / case["id"]
    parsed = []
    ms = 0
    errors = []
    stderr = []
    for framework in ("langgraph", "crewai", "n8n", "openai-agents", "autogen"):
        dest = out.with_name(f"{out.stem}-{framework}.json")
        result = run_cmd([
            str(RADAR), "scan", framework, "-i", str(target), "-o", str(dest), "--export-graph-json",
        ], target, 30)
        ms += result["ms"]
        if result["error"]:
            errors.append(result["error"])
        stderr.append(result["stderr"][:500])
        loaded = load_json(dest)
        if loaded is not None:
            parsed.append({framework: loaded})
    return {"exit": 0, "stdout": "", "stderr": "\n".join(stderr)[:20_000], "ms": ms, "error": None, "parsed": parsed}


def curated_scan(case: dict, out: Path) -> dict:
    home = CORPUS / case["surface"] / case["id"] / "home"
    result = run_cmd(["npx", "--yes", "curatedmcp", "audit", "--json"], home, 60, home=home)
    try:
        result["parsed"] = json.loads(result["stdout"])
    except json.JSONDecodeError:
        result["parsed"] = None
    out.write_text(result["stdout"][:80_000], encoding="utf-8")
    return result


SCANNERS = {
    "shadowscan": shadowscan,
    "vet": vet_scan,
    "numbat": numbat_scan,
    "ai-bom": aibom_scan,
    "nuguard": nuguard_scan,
    "agentdiscover": agentdiscover_scan,
    "agentic-radar": radar_scan,
    "curatedmcp": curated_scan,
}


def probe() -> dict:
    notes = {}
    notes["shadowscan"] = "run" if (PY / "shadowscan").exists() else "binary missing"
    notes["vet"] = "run" if VET.exists() else "binary missing"
    notes["numbat"] = "run" if NUMBAT.exists() else "binary missing"
    notes["ai-bom"] = "run" if AIBOM.exists() else "binary missing"
    notes["nuguard"] = "run" if (PY / "nuguard").exists() else "binary missing"
    notes["agentdiscover"] = "run" if (PY / "agentdiscover").exists() else "binary missing"
    notes["agentic-radar"] = "run" if RADAR.exists() else "binary missing"
    snyk = run_cmd(["npx", "--yes", "snyk-agent-scan", "--help"], ROOT, 45)
    if snyk["error"]:
        notes["snyk-agent-scan"] = "not run: " + (snyk["error"] or "failed")
    elif "SNYK_TOKEN" in (snyk["stdout"] + snyk["stderr"]) or "token" in (snyk["stdout"] + snyk["stderr"]).lower():
        notes["snyk-agent-scan"] = "not run: the published CLI requires a Snyk token before any scan"
    else:
        # Help succeeded. A real scan still demands a token; confirm with an empty home.
        trial = run_cmd(["npx", "--yes", "snyk-agent-scan"], EMPTY_HOME, 40, home=EMPTY_HOME)
        blob = (trial["stdout"] + trial["stderr"]).lower()
        if "token" in blob or trial["exit"] not in (0,):
            notes["snyk-agent-scan"] = "not run: scan refused without a Snyk token"
        else:
            notes["snyk-agent-scan"] = "run"
    notes["aiostack"] = "not run: AIOstack is a Kubernetes daemon with no offline fixture mode in this environment"
    probe_mcp = run_cmd(["npx", "--yes", "curatedmcp", "audit", "--help"], ROOT, 60)
    if probe_mcp["error"] or probe_mcp["exit"] not in (0,):
        notes["curatedmcp"] = "not run: auditor CLI did not start (" + (probe_mcp["error"] or f"exit {probe_mcp['exit']}") + ")"
    else:
        home_a = CORPUS / "endpoint" / "endpoint-001" / "home"
        home_b = CORPUS / "endpoint" / "endpoint-026" / "home"
        audit_a = run_cmd(["npx", "--yes", "curatedmcp", "audit"], home_a, 60, home=home_a)
        audit_b = run_cmd(["npx", "--yes", "curatedmcp", "audit"], home_b, 40, home=home_b)
        if audit_a["stdout"].strip() and audit_a["stdout"].strip() == audit_b["stdout"].strip():
            notes["curatedmcp"] = "not run: audit output did not change between two fixture homes, so the CLI is not scoring these cases"
        elif audit_a["error"] and audit_b["error"]:
            notes["curatedmcp"] = "not run: " + (audit_a["error"] or "audit failed")
        else:
            notes["curatedmcp"] = "run"
    notes["reference-lexicon"] = "run"
    return notes


def versions() -> dict:
    out = {}
    if (PY / "shadowscan").exists():
        out["shadowscan"] = run_cmd([str(PY / "shadowscan"), "--version"], ROOT, 20)["stdout"].strip()
    if VET.exists():
        out["vet"] = "1.20.0"
    if NUMBAT.exists():
        out["numbat"] = run_cmd([str(NUMBAT), "version"], ROOT, 20)["stdout"].strip()[:200]
    if AIBOM.exists():
        out["ai-bom"] = run_cmd([str(AIBOM), "version"], ROOT, 20)["stdout"].strip()
    if (PY / "nuguard").exists():
        out["nuguard"] = "0.9.15"
    if (PY / "agentdiscover").exists():
        out["agentdiscover"] = run_cmd([str(PY / "agentdiscover"), "--version"], ROOT, 20)["stdout"].strip()
    if RADAR.exists():
        out["agentic-radar"] = "0.14.1"
    return out


def main() -> None:
    smoke = "--smoke" in sys.argv
    EMPTY_HOME.mkdir(exist_ok=True)
    manifest = generate()
    cases = load_cases(CORPUS)
    assert len(cases) == 450, len(cases)
    if smoke:
        cases = [c for c in cases if c["index"] in {0, 25, 40}]
    if RAW.exists():
        shutil.rmtree(RAW)
    RAW.mkdir(parents=True, exist_ok=True)
    notes = probe() if not smoke else {name: "run" for name in list(SCANNERS) + ["reference-lexicon"]}
    if smoke:
        notes["snyk-agent-scan"] = "skipped in smoke"
        notes["aiostack"] = "skipped in smoke"
        notes["curatedmcp"] = "skipped in smoke"
    print("PROBE", json.dumps(notes), flush=True)
    predictions: dict[str, dict] = {name: {} for name in SCOPE}
    timings: dict[str, list[int]] = {name: [] for name in SCOPE}

    for case in cases:
        predictions["reference-lexicon"][case["id"]] = reference_scan(case)

    for tool, scanner in SCANNERS.items():
        if not str(notes.get(tool, "")).startswith("run"):
            continue
        tool_raw = RAW / tool
        tool_raw.mkdir(parents=True, exist_ok=True)
        applicable = [c for c in cases if c["surface"] in SCOPE[tool]]
        print(f"RUN {tool} x {len(applicable)}", flush=True)
        for i, case in enumerate(applicable):
            out = tool_raw / f"{case['id']}.json"
            result = scanner(case, out)
            failed = result["error"] in {"timeout", "oserror"} or "Traceback (most recent call last)" in (result.get("stderr") or "")
            mapped = [] if failed else findings_from_result(result, case["surface"])
            record = {
                "exit": result["exit"],
                "ms": result["ms"],
                "error": result["error"] if failed else None,
                "stderr_tail": (result.get("stderr") or "")[:400],
                "findings": mapped,
            }
            predictions[tool][case["id"]] = {"findings": mapped, "error": bool(record["error"])}
            timings[tool].append(result["ms"])
            (tool_raw / f"{case['id']}.meta.json").write_text(json.dumps(record)[:50_000], encoding="utf-8")
            if (i + 1) % 25 == 0:
                print(f"  {tool} {i+1}/{len(applicable)}", flush=True)

    tool_rows = []
    for name in TEN + ["reference-lexicon"]:
        note = notes.get(name, "not run")
        ran = str(note).startswith("run")
        row = {
            "id": name,
            "role": "reference" if name == "reference-lexicon" else "tool",
            "status": "scored" if ran else "not_run",
            "status_detail": note,
            "version": versions().get(name),
            "applicable_surfaces": sorted(SCOPE[name]),
        }
        if ran:
            summary = score_tool(cases if not smoke else load_cases(CORPUS) and cases, predictions[name], SCOPE[name])
            # score_tool with the cases we actually attempted. Errors inside predictions count.
            row["metrics"] = summary
            samples = timings[name]
            samples.sort()
            row["latency_ms"] = {
                "n": len(samples),
                "p50": samples[len(samples) // 2] if samples else None,
                "p95": samples[min(len(samples) - 1, int(len(samples) * 0.95))] if samples else None,
            }
        tool_rows.append(row)

    case_index = [
        {
            "id": case["id"],
            "surface": case["surface"],
            "polarity": case["polarity"],
            "title": case["title"],
            "facts": [{"category": f["category"], "value": f["value"], "path": f["path"], "quote": f["quote"]} for f in case["facts"]],
            "forbidden": case["forbidden"],
        }
        for case in load_cases(CORPUS)
    ]
    (RESULTS / "cases.json").write_text(json.dumps(case_index), encoding="utf-8")
    payload = {
        "benchmark": manifest,
        "smoke": smoke,
        "scored_cases": len(cases),
        "tools": tool_rows,
        "methodology": {
            "positives_per_surface": 25,
            "negatives_per_surface": 15,
            "near_misses_per_surface": 10,
            "primary_metric": "Fact-level precision, recall and F1 on surfaces the tool can read.",
            "estate_recall": "Positive facts on surfaces the tool cannot read count as misses. Unscanned negatives are not counted as true negatives.",
            "case_metric": "A positive case is detected when any planted fact is returned. Any mapped finding on a negative or near-miss case is a false positive.",
            "errors": "Timeouts and crashes are excluded from precision and recall and reported separately.",
            "reference": "reference-lexicon applies the published alias table to the artifact text. It is a string-match ceiling, not a product.",
        },
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    dest = RESULTS / ("smoke.json" if smoke else "scoreboard.json")
    dest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("WROTE", dest, flush=True)
    for row in tool_rows:
        fact = (row.get("metrics") or {}).get("quality", {}).get("fact", {})
        print(row["id"], row["status"], fact.get("f1"), "P", fact.get("precision"), "R", fact.get("recall"), "tp", fact.get("tp"), "fp", fact.get("fp"), "fn", fact.get("fn"))


if __name__ == "__main__":
    main()
