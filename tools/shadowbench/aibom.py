"""Export cases-track truth, or what one tool reported, as a CycloneDX 1.6 AI bill of materials.

``python -m tools.shadowbench.aibom --corpus corpus.json --out truth.cdx.json [--include-decoys]``
``python -m tools.shadowbench.aibom --corpus corpus.json --results results/ --tool NAME --out NAME.cdx.json``

Each entity becomes a component, or an entry of ``services`` when it is something reached over a
network rather than present (an OAuth or SaaS app, a model server, a model provider), placed by
``tools.shadowbench.frameworks.placement``. Every entry carries ``shadowbench:*`` properties: the
key as written and in ``canonical-v1`` form (``tools/shadowbench/keys.py``), the case, surface,
modality and label, and the OWASP Agentic, OWASP LLM and MITRE ATLAS entries the mapping assigns.
Truth exports hold the expected entities, and with ``--include-decoys`` the decoys too (label
``none``, mapped to nothing). Tool exports hold the entities of the tool's ``ok`` rows exactly as
it reported them, matched to nothing: an AIBOM is an inventory, not a score.

The output is deterministic: no timestamp, and a serial number derived from the SHA-256 of the
rest of the document, so an export can be re-made and compared byte for byte, and any change to
it (a new mapping version included) gives it a new serial number. A tool export takes only rows the
scorer would accept and the run's manifest vouches for (this corpus, the tool listed as run, its
status counts and recorded digest); anything else is refused with exit 2. The schema is CycloneDX 1.6, which
``tests/unit/test_shadowbench_frameworks.py`` validates every export against.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from pathlib import Path
from typing import Any

from tools.shadowbench import frameworks
from tools.shadowbench.cases.corpus import Case, Corpus, corpus_digest, load_corpus
from tools.shadowbench.cases.score import ResultsError, _check_row, _provenance
from tools.shadowbench.keys import canonical

SPEC_VERSION = "1.6"
TOOL_NAME = "shadowbench-aibom"


class ExportError(ValueError):
    """Inputs that would export an inventory of the wrong corpus or the wrong rows."""


def _properties(values: dict[str, str | list[str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for name, value in values.items():
        text = ",".join(value) if isinstance(value, list) else value
        if text:
            out.append({"name": f"shadowbench:{name}", "value": text})
    return out


def entry(case: Case, key: str, label: str, source: str) -> tuple[str, dict[str, Any]]:
    """``("components" | "services", object)`` for one entity of ``case``."""
    # placed and mapped by the canonical namespace (``Service:`` is ``service:``); named as reported
    namespace = canonical(key).partition(":")[0]
    value = key.partition(":")[2]
    place = frameworks.placement(namespace)
    refs = frameworks.references(label, case.surface, namespace)
    obj: dict[str, Any] = {
        "bom-ref": f"{source}/{case.case_id}/{key}",
        "group": namespace,
        "name": value or key,
        "properties": _properties(
            {
                "key": key,
                "canonical-key": canonical(key),
                "case": case.case_id,
                "surface": case.surface,
                "modality": case.modality,
                "label": label,
                "owasp-asi": refs["owasp-asi"],
                "owasp-llm": refs["owasp-llm"],
                "mitre-atlas": refs["mitre-atlas"],
            }
        ),
    }
    if "section" in place:
        return place["section"], obj
    return "components", {"type": place["type"], **obj}


def _bom(
    corpus_sha256: str, source: str, extra: dict[str, str], items: list[tuple[str, dict[str, Any]]]
) -> dict[str, Any]:
    sections: dict[str, list[dict[str, Any]]] = {"components": [], "services": []}
    seen: set[str] = set()
    for section, obj in items:
        if obj["bom-ref"] in seen:
            continue
        seen.add(obj["bom-ref"])
        sections[section].append(obj)
    for entries in sections.values():
        entries.sort(key=lambda o: str(o["bom-ref"]))
    bom: dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": SPEC_VERSION,
        "version": 1,
        "metadata": {
            "tools": {
                "components": [
                    {"type": "application", "name": TOOL_NAME, "version": frameworks.MAPPING_VERSION}
                ]
            },
            "component": {
                "type": "data",
                "bom-ref": "corpus",
                "name": "ShadowBench cases corpus",
                "hashes": [{"alg": "SHA-256", "content": corpus_sha256}],
            },
            "properties": _properties(
                {
                    "source": source,
                    "mapping-version": frameworks.MAPPING_VERSION,
                    **{
                        f"framework.{k}": f"{v['title']} {v['version']}"
                        for k, v in frameworks.SOURCES.items()
                    },
                    **extra,
                }
            ),
        },
        "components": sections["components"],
    }
    if sections["services"]:
        bom["services"] = sections["services"]
    # the serial number names this exact document: every byte but itself, metadata included
    digest = hashlib.sha256(json.dumps(bom, sort_keys=True).encode()).hexdigest()
    return {"serialNumber": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'shadowbench:' + digest)}", **bom}


def truth_bom(corpus: Corpus, corpus_sha256: str, include_decoys: bool = False) -> dict[str, Any]:
    """The corpus's expected entities (and decoys, labeled ``none``) as a BOM."""
    items = [entry(case, e.key, e.label, "truth") for case in corpus.cases for e in case.expected]
    if include_decoys:
        items += [entry(case, key, "none", "truth") for case in corpus.cases for key in case.decoys]
    return _bom(corpus_sha256, "truth", {"include-decoys": str(include_decoys).lower()}, items)


def _tool_rows(results: Path, corpus: Corpus, tool: str) -> list[dict[str, Any]]:
    """``<tool>.jsonl`` checked row by row as the scorer checks it; refused on the same grounds."""
    cases = {case.case_id: case for case in corpus.cases}
    path = results / f"{tool}.jsonl"
    rows: dict[str, dict[str, Any]] = {}
    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"{path}: {exc}") from exc
    with handle:
        for number, line in enumerate(handle, 1):  # split on newlines only, as the runner writes rows
            if not line.strip():
                continue
            where = f"{path.name}:{number}"
            try:
                row = _check_row(json.loads(line), where, cases, tool)
            except (ValueError, ResultsError) as exc:
                raise ExportError(f"{where}: {exc}") from exc
            if row["case"] in rows:
                raise ExportError(f"{where}: second row for case {row['case']}")
            rows[row["case"]] = row
    return list(rows.values())


def tool_bom(corpus: Corpus, corpus_sha256: str, results: Path, tool: str) -> dict[str, Any]:
    """What ``tool`` reported on its ``ok`` rows under ``results``, as a BOM.

    The rows must be ones the run's manifest vouches for, as the scorer requires: the manifest names
    this corpus and lists the tool as run, the row statuses add up to its counts, and the file's
    SHA-256 is the one it recorded (when it recorded one).
    """
    manifest_path = results / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ExportError(f"{manifest_path}: unreadable manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("corpus_sha256") != corpus_sha256:
        raise ExportError(f"{results}: results were not recorded against this corpus ({corpus_sha256})")
    tools = manifest.get("tools")
    run = tools.get(tool) if isinstance(tools, dict) else None
    if not isinstance(run, dict) or run.get("skipped"):
        raise ExportError(
            f"{results}: the manifest does not record {tool} as run, so no run vouches for its rows"
        )
    rows = _tool_rows(results, corpus, tool)
    try:
        _, problems, _ = _provenance({tool: {r["case"]: r for r in rows}}, {tool: run}, results)
    except ResultsError as exc:
        raise ExportError(str(exc)) from exc
    if problems:
        raise ExportError("; ".join(problems))
    cases = {case.case_id: case for case in corpus.cases}
    items = [
        entry(cases[row["case"]], str(ent["key"]), str(ent.get("label") or ""), f"tool:{tool}")
        for row in rows
        if row["status"] == "ok"
        for ent in row["entities"]
    ]
    rows_sha256 = hashlib.sha256((results / f"{tool}.jsonl").read_bytes()).hexdigest()
    extra = {"tool-version": str(run.get("version") or ""), "rows-sha256": rows_sha256}
    return _bom(corpus_sha256, f"tool:{tool}", extra, items)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--results", type=Path, help="a cases results directory; exports --tool's rows")
    ap.add_argument("--tool", help="the tool whose <tool>.jsonl to export (with --results)")
    ap.add_argument("--include-decoys", action="store_true", help="truth export: add decoys labeled none")
    args = ap.parse_args(argv)
    if bool(args.results) != bool(args.tool):
        ap.error("--results and --tool go together")
    corpus = load_corpus(args.corpus)
    digest = corpus_digest(args.corpus)
    try:
        bom = (
            tool_bom(corpus, digest, args.results, args.tool)
            if args.results
            else truth_bom(corpus, digest, args.include_decoys)
        )
    except ExportError as exc:
        print(f"refusing to export: {exc}", file=sys.stderr)
        return 2
    args.out.write_text(json.dumps(bom, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{args.out}: {len(bom['components'])} components, {len(bom.get('services', []))} services")
    return 0


if __name__ == "__main__":
    sys.exit(main())
