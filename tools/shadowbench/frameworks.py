"""Where ShadowBench's labels, surfaces and code facts sit in public AI-security frameworks.

The benchmark's own taxonomy (``agent``/``llm``/``none`` labels, nine surfaces, the code surface's
``<category>:<value>`` facts) says what a tool must find. This module says why an operator would
care that it was found, in the vocabulary of four public references:

* OWASP Top 10 for Agentic Applications 2026 (``ASI01``..``ASI10``),
* OWASP Top 10 for LLM Applications 2025 (``LLM01``..``LLM10``),
* MITRE ATLAS techniques (data release 2026.09, format 6.0.0),
* CycloneDX 1.6, for where an entity goes in an AI bill of materials (``tools/shadowbench/aibom.py``).

A mapping reads "an entity of this kind that nobody inventoried is exposure to these risks, and is
what these adversary techniques use or create". It is informative, written by the benchmark's
maintainer and not reviewed by OWASP or MITRE; it changes no label, key or metric. Every identifier
used is checked against the catalogs below by ``tests/unit/test_shadowbench_frameworks.py``, and the
catalogs were checked against the publishers' own data when :data:`MAPPING_VERSION` was set: ATLAS
names from ``mitre-atlas/atlas-data`` ``dist/v6/ATLAS-2026.09.yaml``, OWASP titles from the
published lists. ``python -m tools.shadowbench.frameworks`` prints the whole mapping as JSON.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from typing import get_args

from tools.discovery_benchmark.taxonomy import CATEGORIES
from tools.shadowbench.cases.contract import SURFACES, Label, Reported

MAPPING_VERSION = "2026-10-21"
"""Date the mapping and its catalogs were last checked against their sources."""

SOURCES: dict[str, dict[str, str]] = {
    "owasp-asi": {
        "title": "OWASP Top 10 for Agentic Applications",
        "version": "2026",
        "url": "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/",
    },
    "owasp-llm": {
        "title": "OWASP Top 10 for LLM Applications",
        "version": "2025",
        "url": "https://genai.owasp.org/llm-top-10/",
    },
    "mitre-atlas": {
        "title": "MITRE ATLAS",
        "version": "2026.09",
        "url": "https://atlas.mitre.org/",
    },
    "cyclonedx": {
        "title": "CycloneDX",
        "version": "1.6",
        "url": "https://cyclonedx.org/docs/1.6/json/",
    },
}

OWASP_ASI: dict[str, str] = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Tool Misuse and Exploitation",
    "ASI03": "Identity and Privilege Abuse",
    "ASI04": "Agentic Supply Chain Vulnerabilities",
    "ASI05": "Unexpected Code Execution",
    "ASI06": "Memory and Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "ASI10": "Rogue Agents",
}

OWASP_LLM: dict[str, str] = {
    "LLM01": "Prompt Injection",
    "LLM02": "Sensitive Information Disclosure",
    "LLM03": "Supply Chain",
    "LLM04": "Data and Model Poisoning",
    "LLM05": "Improper Output Handling",
    "LLM06": "Excessive Agency",
    "LLM07": "System Prompt Leakage",
    "LLM08": "Vector and Embedding Weaknesses",
    "LLM09": "Misinformation",
    "LLM10": "Unbounded Consumption",
}

MITRE_ATLAS: dict[str, str] = {
    "AML.T0010": "AI Supply Chain Compromise",
    "AML.T0010.005": "AI Agent Tool",
    "AML.T0034.002": "Agentic Resource Consumption",
    "AML.T0040": "AI Model Inference API Access",
    "AML.T0047": "AI-Enabled Product or Service",
    "AML.T0053": "AI Agent Tool Invocation",
    "AML.T0055": "Unsecured Credentials",
    "AML.T0081": "Modify AI Agent Configuration",
    "AML.T0083": "Credentials from AI Agent Configuration",
    "AML.T0084": "Discover AI Agent Configuration",
    "AML.T0103": "Deploy AI Agent",
    "AML.T0108": "AI Agent",
    "AML.T0112.000": "Local AI Agent",
    "AML.T0118": "Autonomous AI Agent Communication",
}
"""The ATLAS techniques this mapping uses, named as ATLAS 2026.09 names them."""


@dataclass(frozen=True)
class Mapping:
    """One row of the mapping: the framework entries an entity kind bears on, and why."""

    owasp_asi: tuple[str, ...] = ()
    owasp_llm: tuple[str, ...] = ()
    mitre_atlas: tuple[str, ...] = ()
    rationale: str = ""
    cyclonedx: dict[str, str] = field(default_factory=dict)


LABELS: dict[str, Mapping] = {
    "agent": Mapping(
        owasp_asi=("ASI10", "ASI03"),
        owasp_llm=("LLM06",),
        mitre_atlas=("AML.T0103", "AML.T0108"),
        rationale="An agent nobody inventoried acts with delegated authority no one reviews; an "
        "adversary-deployed agent and a sanctioned one an adversary steers look the same until found.",
    ),
    "llm": Mapping(
        owasp_llm=("LLM02",),
        mitre_atlas=("AML.T0040", "AML.T0047"),
        rationale="Unsanctioned model use sends data to an inference API or AI product outside review.",
    ),
}
LABELS["ai"] = Mapping(
    owasp_llm=LABELS["llm"].owasp_llm,
    mitre_atlas=LABELS["llm"].mitre_atlas,
    rationale="A report the tool could not tier: at least AI use, so it bears on what llm does.",
)
"""Per label, truth or reported. ``ai`` is a report a tool could not tier and maps as ``llm``, its
lower bound; ``none`` (a decoy) maps to nothing: it is not AI."""

SURFACE_MAP: dict[str, Mapping] = {
    "code": Mapping(
        owasp_asi=("ASI04",),
        owasp_llm=("LLM03",),
        mitre_atlas=("AML.T0010",),
        rationale="Frameworks, SDKs and agent configuration committed to a repository are AI supply chain.",
    ),
    "identity": Mapping(
        owasp_asi=("ASI03",),
        owasp_llm=("LLM06",),
        mitre_atlas=("AML.T0047",),
        rationale="OAuth clients and service principals hold delegated scopes an AI product or agent uses.",
    ),
    "gateway": Mapping(
        owasp_llm=("LLM02", "LLM10"),
        mitre_atlas=("AML.T0040", "AML.T0034.002"),
        rationale="Gateway callers are direct inference API use, with its data exposure and spend.",
    ),
    "lowcode": Mapping(
        owasp_asi=("ASI02", "ASI03"),
        owasp_llm=("LLM06",),
        mitre_atlas=("AML.T0053",),
        rationale="Copilot Studio bots, flows and n8n workflows invoke connectors as tools under their "
        "maker's identity.",
    ),
    "saas": Mapping(
        owasp_llm=("LLM02",),
        mitre_atlas=("AML.T0047",),
        rationale="Marketplace AI apps receive tenant data through granted scopes.",
    ),
    "cloud": Mapping(
        owasp_asi=("ASI03", "ASI02"),
        owasp_llm=("LLM06",),
        mitre_atlas=("AML.T0103", "AML.T0053"),
        rationale="Managed agents and agent workloads run with execution roles and tool gateways.",
    ),
    "endpoint": Mapping(
        owasp_asi=("ASI04", "ASI03"),
        mitre_atlas=("AML.T0112.000", "AML.T0084", "AML.T0083"),
        rationale="Local agent configuration names the agent's tools and often the credentials they use.",
    ),
    "network": Mapping(
        owasp_llm=("LLM10",),
        mitre_atlas=("AML.T0040",),
        rationale="A model server reachable on the network is an inference API nobody gates.",
    ),
    "runtime": Mapping(
        owasp_asi=("ASI10", "ASI05"),
        mitre_atlas=("AML.T0112.000", "AML.T0108"),
        rationale="A running agent process is a local AI agent with the host user's permissions.",
    ),
}
"""Per surface (``tools.shadowbench.cases.contract.SURFACES``)."""

FACTS: dict[str, Mapping] = {
    "framework": Mapping(
        owasp_asi=("ASI04",),
        owasp_llm=("LLM03",),
        mitre_atlas=("AML.T0010",),
        rationale="An agent framework is a dependency whose compromise reaches every agent built on it.",
        cyclonedx={"type": "framework"},
    ),
    "provider": Mapping(
        owasp_llm=("LLM02",),
        mitre_atlas=("AML.T0040",),
        rationale="A model provider receives prompts and data over its inference API.",
        cyclonedx={"section": "services"},
    ),
    "mcp": Mapping(
        owasp_asi=("ASI02", "ASI04"),
        mitre_atlas=("AML.T0053", "AML.T0010.005"),
        rationale="MCP servers and SDKs are agent tools, invoked by agents and acquired as supply chain.",
        cyclonedx={"type": "library"},
    ),
    "mcp-client-config": Mapping(
        owasp_asi=("ASI04", "ASI03"),
        mitre_atlas=("AML.T0084", "AML.T0083"),
        rationale="A client's MCP configuration lists the tools an agent may call, and often their "
        "credentials.",
        cyclonedx={"type": "file"},
    ),
    "agent-config": Mapping(
        owasp_asi=("ASI01", "ASI06"),
        mitre_atlas=("AML.T0081", "AML.T0084"),
        rationale="Instruction files (AGENTS.md, CLAUDE.md, rules) set an agent's goals and persistent "
        "context.",
        cyclonedx={"type": "file"},
    ),
    "a2a": Mapping(
        owasp_asi=("ASI07",),
        mitre_atlas=("AML.T0118",),
        rationale="Agent cards and A2A SDKs are agent-to-agent communication channels.",
        cyclonedx={"type": "library"},
    ),
    "lowcode": Mapping(
        owasp_asi=("ASI02", "ASI03"),
        mitre_atlas=("AML.T0053",),
        rationale="A low-code AI workflow definition calls tools under its owner's connections.",
        cyclonedx={"type": "application"},
    ),
    "iac": Mapping(
        owasp_llm=("LLM10",),
        mitre_atlas=("AML.T0040",),
        rationale="Infrastructure code that provisions managed model endpoints creates inference APIs "
        "and spend.",
        cyclonedx={"type": "file"},
    ),
}
"""Per code-surface fact category (``tools.discovery_benchmark.taxonomy.CATEGORIES``)."""

NAMESPACES: dict[str, dict[str, str]] = {
    "app": {"section": "services"},
    "artifact": {"type": "file"},
    "bot": {"type": "application"},
    "caller": {"type": "application"},
    "client": {"type": "device"},
    "flow": {"type": "application"},
    "k8s": {"type": "application"},
    "proc": {"type": "application"},
    "process": {"type": "application"},
    "resource": {"type": "application"},
    "service": {"section": "services"},
    "workflow": {"type": "application"},
}
"""Where an entity of each cases-track key namespace goes in a CycloneDX BOM: a component of
``type``, or an entry of ``services`` (something reached over a network, not shipped)."""


def placement(namespace: str) -> dict[str, str]:
    """The CycloneDX placement of a key namespace; unknown namespaces are generic applications."""
    if namespace in FACTS:
        return FACTS[namespace].cyclonedx
    return NAMESPACES.get(namespace, {"type": "application"})


def references(label: str | None, surface: str | None, namespace: str | None) -> dict[str, list[str]]:
    """The framework entries an entity bears on, merged from its label, surface and fact category.

    A decoy (label ``none``) is not AI and bears on nothing, whatever its surface.
    """
    if label == "none":
        return {"owasp-asi": [], "owasp-llm": [], "mitre-atlas": []}
    rows = [
        LABELS.get(label or ""),
        SURFACE_MAP.get(surface or ""),
        FACTS.get(namespace or "") if surface == "code" else None,  # fact categories are code-surface truth
    ]
    out: dict[str, list[str]] = {"owasp-asi": [], "owasp-llm": [], "mitre-atlas": []}
    for row in rows:
        if row is None:
            continue
        for name, ids in (
            ("owasp-asi", row.owasp_asi),
            ("owasp-llm", row.owasp_llm),
            ("mitre-atlas", row.mitre_atlas),
        ):
            out[name].extend(i for i in ids if i not in out[name])
    return {name: sorted(ids) for name, ids in out.items()}


def problems() -> list[str]:
    """Identifiers used but missing from their catalog, and surfaces or categories left unmapped."""
    found: list[str] = []
    tables = {"labels": LABELS, "surfaces": SURFACE_MAP, "facts": FACTS}
    for table, rows in tables.items():
        for name, row in rows.items():
            for catalog, ids in (
                (OWASP_ASI, row.owasp_asi),
                (OWASP_LLM, row.owasp_llm),
                (MITRE_ATLAS, row.mitre_atlas),
            ):
                found.extend(f"{table}.{name}: {i} is not in its catalog" for i in ids if i not in catalog)
            if not row.rationale:
                found.append(f"{table}.{name}: no rationale")
    found.extend(f"surface {s} is not mapped" for s in SURFACES if s not in SURFACE_MAP)
    labels = {*get_args(Label), *get_args(Reported)} - {"none"}
    found.extend(f"label {label} is not mapped" for label in sorted(labels) if label not in LABELS)
    found.extend(f"fact category {c} is not mapped" for c in CATEGORIES if c not in FACTS)
    return found


def as_json() -> dict[str, object]:
    return {
        "mapping_version": MAPPING_VERSION,
        "sources": SOURCES,
        "catalogs": {"owasp-asi": OWASP_ASI, "owasp-llm": OWASP_LLM, "mitre-atlas": MITRE_ATLAS},
        "labels": {k: asdict(v) for k, v in LABELS.items()},
        "surfaces": {k: asdict(v) for k, v in SURFACE_MAP.items()},
        "facts": {k: asdict(v) for k, v in FACTS.items()},
        "namespaces": NAMESPACES,
    }


def main(argv: list[str] | None = None) -> int:
    del argv
    print(json.dumps(as_json(), indent=1))
    return 1 if problems() else 0


if __name__ == "__main__":
    sys.exit(main())
