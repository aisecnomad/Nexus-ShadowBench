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

The output is deterministic: no timestamp, and a serial number derived from the inputs' SHA-256, so
an export can be re-made and compared byte for byte. A results directory whose manifest names
another corpus is refused, as the scorer refuses it. The schema is CycloneDX 1.6, which
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
    namespace, _, value = key.partition(":")
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
    digest = hashlib.sha256(
        json.dumps(
            {"corpus": corpus_sha256, "source": source, **extra, "items": sections}, sort_keys=True
        ).encode()
    ).hexdigest()
    bom: dict[str, Any] = {
        "bomFormat": "CycloneDX",
        "specVersion": SPEC_VERSION,
        "serialNumber": f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'shadowbench:' + digest)}",
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
    return bom


def truth_bom(corpus: Corpus, corpus_sha256: str, include_decoys: bool = False) -> dict[str, Any]:
    """The corpus's expected entities (and decoys, labeled ``none``) as a BOM."""
    items = [entry(case, e.key, e.label, "truth") for case in corpus.cases for e in case.expected]
    if include_decoys:
        items += [entry(case, key, "none", "truth") for case in corpus.cases for key in case.decoys]
    return _bom(corpus_sha256, "truth", {"include-decoys": str(include_decoys).lower()}, items)


def tool_bom(corpus: Corpus, corpus_sha256: str, results: Path, tool: str) -> dict[str, Any]:
    """What ``tool`` reported on its ``ok`` rows under ``results``, as a BOM."""
    manifest_path = results / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ExportError(f"{manifest_path}: unreadable manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("corpus_sha256") != corpus_sha256:
        raise ExportError(f"{results}: results were not recorded against this corpus ({corpus_sha256})")
    rows_path = results / f"{tool}.jsonl"
    try:
        lines = rows_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ExportError(f"{rows_path}: {exc}") from exc
    cases = {case.case_id: case for case in corpus.cases}
    items: list[tuple[str, dict[str, Any]]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        row = json.loads(line)
        case = cases.get(str(row.get("case")))
        if case is None:
            raise ExportError(f"{rows_path}:{number}: row for a case the corpus does not have")
        if row.get("status") != "ok":
            continue
        for ent in row.get("entities") or []:
            items.append(entry(case, str(ent["key"]), str(ent.get("label") or ""), f"tool:{tool}"))
    run = (manifest.get("tools") or {}).get(tool) or {}
    extra = {
        "tool-version": str(run.get("version") or ""),
        "rows-sha256": hashlib.sha256(rows_path.read_bytes()).hexdigest(),
    }
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
