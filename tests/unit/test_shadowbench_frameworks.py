"""Framework mappings (tools/shadowbench/frameworks.py) and the CycloneDX AIBOM export (aibom.py)."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest
from cyclonedx.schema import SchemaVersion
from cyclonedx.validation.json import JsonStrictValidator

from tools.discovery_benchmark.taxonomy import CATEGORIES
from tools.shadowbench import aibom, frameworks
from tools.shadowbench.cases.contract import SURFACES
from tools.shadowbench.cases.corpus import corpus_digest, load_corpus

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "benchmarks" / "shadowbench" / "cases"
CORPUS = CASES / "corpus.json"
RUN = CASES / "results" / "2026-10-11"

VALIDATOR = JsonStrictValidator(SchemaVersion.V1_6)


def _valid(bom: dict[str, Any]) -> None:
    error = VALIDATOR.validate_str(json.dumps(bom))
    assert error is None, error


def test_every_identifier_is_in_its_catalog_and_every_surface_and_category_is_mapped() -> None:
    assert frameworks.problems() == []
    assert set(frameworks.SURFACE_MAP) == set(SURFACES)
    assert set(frameworks.FACTS) == set(CATEGORIES)


def test_catalog_identifiers_are_well_formed() -> None:
    assert list(frameworks.OWASP_ASI) == [f"ASI{n:02d}" for n in range(1, 11)]
    assert list(frameworks.OWASP_LLM) == [f"LLM{n:02d}" for n in range(1, 11)]
    assert all(re.fullmatch(r"AML\.T\d{4}(\.\d{3})?", i) for i in frameworks.MITRE_ATLAS)


def test_problems_names_an_unknown_identifier(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(frameworks.LABELS, "agent", frameworks.Mapping(owasp_asi=("ASI11",), rationale="x"))
    assert frameworks.problems() == ["labels.agent: ASI11 is not in its catalog"]


def test_references_merge_label_surface_and_category() -> None:
    refs = frameworks.references("agent", "code", "mcp")
    assert refs["owasp-asi"] == ["ASI02", "ASI03", "ASI04", "ASI10"]
    assert "AML.T0053" in refs["mitre-atlas"] and "AML.T0010" in refs["mitre-atlas"]
    assert frameworks.references("none", "cloud", "resource") == {
        "owasp-asi": [],
        "owasp-llm": [],
        "mitre-atlas": [],
    }


def test_the_cli_prints_the_mapping() -> None:
    assert frameworks.main([]) == 0


def test_the_truth_export_is_valid_cyclonedx_and_deterministic(tmp_path: Path) -> None:
    out = tmp_path / "truth.cdx.json"
    assert aibom.main(["--corpus", str(CORPUS), "--out", str(out)]) == 0
    first = out.read_bytes()
    bom = json.loads(first)
    _valid(bom)
    corpus = load_corpus(CORPUS)
    expected = {(c.case_id, e.key) for c in corpus.cases for e in c.expected}
    entries = bom["components"] + bom.get("services", [])
    assert len(entries) == len(expected)
    props = {p["name"]: p["value"] for p in entries[0]["properties"]}
    assert props["shadowbench:label"] in ("agent", "llm")
    assert bom["metadata"]["component"]["hashes"][0]["content"] == corpus_digest(CORPUS)
    assert "timestamp" not in bom["metadata"]
    assert aibom.main(["--corpus", str(CORPUS), "--out", str(out)]) == 0
    assert out.read_bytes() == first


def test_decoys_are_labeled_none_and_map_to_nothing(tmp_path: Path) -> None:
    corpus = load_corpus(CORPUS)
    bom = aibom.truth_bom(corpus, corpus_digest(CORPUS), include_decoys=True)
    _valid(bom)
    decoys = [
        e
        for e in bom["components"] + bom["services"]
        if {"name": "shadowbench:label", "value": "none"} in e["properties"]
    ]
    assert len(decoys) == len({(c.case_id, k) for c in corpus.cases for k in c.decoys})
    assert all(
        not p["name"].startswith(("shadowbench:owasp", "shadowbench:mitre"))
        for d in decoys
        for p in d["properties"]
    )


def test_placement_puts_network_entities_in_services() -> None:
    corpus = load_corpus(CORPUS)
    bom = aibom.truth_bom(corpus, corpus_digest(CORPUS))
    groups = {s["group"] for s in bom["services"]}
    assert groups <= {"app", "service", "provider"}
    assert {c["type"] for c in bom["components"] if c["group"] == "artifact"} == {"file"}
    assert {c["type"] for c in bom["components"] if c["group"] == "framework"} == {"framework"}


def test_a_tool_export_holds_its_ok_rows_as_reported(tmp_path: Path) -> None:
    out = tmp_path / "t.cdx.json"
    args = ["--corpus", str(CORPUS), "--results", str(RUN), "--tool", "numbat", "--out", str(out)]
    assert aibom.main(args) == 0
    bom = json.loads(out.read_text(encoding="utf-8"))
    _valid(bom)
    reported = set()
    for line in (RUN / "numbat.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["status"] == "ok":
            reported |= {(row["case"], e["key"]) for e in row["entities"]}
    entries = bom["components"] + bom.get("services", [])
    assert {(e["bom-ref"].split("/", 2)[1], e["bom-ref"].split("/", 2)[2]) for e in entries} == reported
    meta = {p["name"]: p["value"] for p in bom["metadata"]["properties"]}
    assert meta["shadowbench:source"] == "tool:numbat"


def test_a_results_directory_of_another_corpus_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    results = tmp_path / "results"
    shutil.copytree(RUN, results)
    manifest = json.loads((results / "manifest.json").read_text(encoding="utf-8"))
    manifest["corpus_sha256"] = "0" * 64
    (results / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    out = tmp_path / "t.cdx.json"
    args = ["--corpus", str(CORPUS), "--results", str(results), "--tool", "numbat", "--out", str(out)]
    assert aibom.main(args) == 2
    assert "not recorded against this corpus" in capsys.readouterr().err
    assert not out.exists()


# --- review regressions ---------------------------------------------------------------------------


def _copy_run(tmp_path: Path) -> Path:
    results = tmp_path / "results"
    shutil.copytree(RUN, results)
    return results


def _export(tmp_path: Path, results: Path, tool: str = "numbat") -> int:
    out = tmp_path / "t.cdx.json"
    return aibom.main(["--corpus", str(CORPUS), "--results", str(results), "--tool", tool, "--out", str(out)])


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda m: m["tools"].pop("numbat"), "does not record numbat as run"),
        (
            lambda m: m["tools"].__setitem__("numbat", {"skipped": "no binary"}),
            "does not record numbat as run",
        ),
        (lambda m: m["tools"]["numbat"].__setitem__("statuses", {"ok": 1}), "row statuses"),
        (lambda m: m["tools"]["numbat"].__setitem__("rows_sha256", "0" * 64), "SHA-256"),
    ],
)
def test_a_tool_export_needs_rows_the_manifest_vouches_for(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], edit: Any, message: str
) -> None:
    """Only the corpus digest was checked, so stale or edited rows were exported as this corpus's."""
    results = _copy_run(tmp_path)
    manifest = json.loads((results / "manifest.json").read_text(encoding="utf-8"))
    edit(manifest)
    (results / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert _export(tmp_path, results) == 2
    assert message in capsys.readouterr().err


@pytest.mark.parametrize(
    "line",
    ["[1, 2]", '{"case": ', '{"case": "x"}'],
)
def test_a_malformed_row_is_refused_not_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], line: str
) -> None:
    results = _copy_run(tmp_path)
    with (results / "numbat.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    assert _export(tmp_path, results) == 2
    assert "refusing to export" in capsys.readouterr().err


def test_rows_with_unicode_line_separators_export(tmp_path: Path) -> None:
    """splitlines() cut a valid row at U+2028 and the export crashed."""
    results = _copy_run(tmp_path)
    rows = (results / "numbat.jsonl").read_text(encoding="utf-8").splitlines()
    first = json.loads(rows[0])
    first["note"] = "caf e\u0085"
    rows[0] = json.dumps(first, ensure_ascii=False)
    (results / "numbat.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")
    manifest = json.loads((results / "manifest.json").read_text(encoding="utf-8"))
    manifest["tools"]["numbat"].pop("rows_sha256", None)
    (results / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    assert _export(tmp_path, results) == 0


def test_an_untiered_ai_report_maps_as_llm_and_facts_only_on_the_code_surface() -> None:
    assert frameworks.references("ai", "saas", "app") == frameworks.references("llm", "saas", "app")
    on_endpoint = frameworks.references("agent", "endpoint", "mcp")
    assert on_endpoint == frameworks.references("agent", "endpoint", "artifact")
    assert "AML.T0010.005" in frameworks.references("agent", "code", "mcp")["mitre-atlas"]


def test_placement_follows_the_canonical_namespace() -> None:
    case = load_corpus(CORPUS).cases[0]
    section, obj = aibom.entry(case, "Service:127.0.0.1:11434", "agent", "tool:t")
    assert section == "services" and obj["group"] == "service"


def test_the_serial_number_changes_with_the_mapping_version(monkeypatch: pytest.MonkeyPatch) -> None:
    corpus = load_corpus(CORPUS)
    before = aibom.truth_bom(corpus, corpus_digest(CORPUS))
    monkeypatch.setattr(frameworks, "MAPPING_VERSION", "2099-01-01")
    after = aibom.truth_bom(corpus, corpus_digest(CORPUS))
    assert before["serialNumber"] != after["serialNumber"]
    _valid(after)
