# Framework mappings and the AIBOM export

Where ShadowBench's labels, surfaces and code-surface fact categories sit in
public AI-security frameworks, and how to export truth or a tool's findings
as a CycloneDX AI bill of materials. Source of record:
[`tools/shadowbench/frameworks.py`](../tools/shadowbench/frameworks.py) and
[`tools/shadowbench/aibom.py`](../tools/shadowbench/aibom.py).

## What a mapping means

A row reads: *an entity of this kind that nobody inventoried is exposure to
these risks, and is what these adversary techniques use or create.* It
explains why finding the entity matters. It is informative: written by the
benchmark's maintainer, not reviewed by OWASP or MITRE, and it changes no
label, key, match or metric. Decoys (label `none`) map to nothing, whatever
their surface.

| Reference | Version | Identifiers |
|---|---|---|
| [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026 | `ASI01`–`ASI10` |
| [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) | 2025 | `LLM01`–`LLM10` |
| [MITRE ATLAS](https://atlas.mitre.org/) | data release 2026.09 (format 6.0.0) | `AML.T....` techniques |
| [CycloneDX](https://cyclonedx.org/docs/1.6/json/) | 1.6 | component type or `services` |

Every identifier the mapping uses is checked against the module's catalogs by
`tests/unit/test_shadowbench_frameworks.py`, and every surface and fact
category must be mapped. The ATLAS names were checked against
`mitre-atlas/atlas-data` `dist/v6/ATLAS-2026.09.yaml` and the OWASP titles
against the published lists on 2026-10-21 (`MAPPING_VERSION`).

## The mapping

| Applies to | OWASP Agentic | OWASP LLM | MITRE ATLAS |
|---|---|---|---|
| label `agent` | ASI10 Rogue Agents, ASI03 Identity and Privilege Abuse | LLM06 Excessive Agency | AML.T0103 Deploy AI Agent, AML.T0108 AI Agent |
| label `llm` | | LLM02 Sensitive Information Disclosure | AML.T0040 AI Model Inference API Access, AML.T0047 AI-Enabled Product or Service |
| surface `code` | ASI04 Agentic Supply Chain Vulnerabilities | LLM03 Supply Chain | AML.T0010 AI Supply Chain Compromise |
| surface `identity` | ASI03 | LLM06 | AML.T0047 |
| surface `gateway` | | LLM02, LLM10 Unbounded Consumption | AML.T0040, AML.T0034.002 Agentic Resource Consumption |
| surface `lowcode` | ASI02 Tool Misuse and Exploitation, ASI03 | LLM06 | AML.T0053 AI Agent Tool Invocation |
| surface `saas` | | LLM02 | AML.T0047 |
| surface `cloud` | ASI03, ASI02 | LLM06 | AML.T0103, AML.T0053 |
| surface `endpoint` | ASI04, ASI03 | | AML.T0112.000 Local AI Agent, AML.T0084 Discover AI Agent Configuration, AML.T0083 Credentials from AI Agent Configuration |
| surface `network` | | LLM10 | AML.T0040 |
| surface `runtime` | ASI10, ASI05 Unexpected Code Execution | | AML.T0112.000, AML.T0108 |
| fact `framework` | ASI04 | LLM03 | AML.T0010 |
| fact `provider` | | LLM02 | AML.T0040 |
| fact `mcp` | ASI02, ASI04 | | AML.T0053, AML.T0010.005 AI Agent Tool |
| fact `mcp-client-config` | ASI04, ASI03 | | AML.T0084, AML.T0083 |
| fact `agent-config` | ASI01 Agent Goal Hijack, ASI06 Memory and Context Poisoning | | AML.T0081 Modify AI Agent Configuration, AML.T0084 |
| fact `a2a` | ASI07 Insecure Inter-Agent Communication | | AML.T0118 Autonomous AI Agent Communication |
| fact `lowcode` | ASI02, ASI03 | | AML.T0053 |
| fact `iac` | | LLM10 | AML.T0040 |

An entity's references are the union of its label's, its surface's and, on
the code surface, its fact category's. Each row's rationale is in the module;
`python -m tools.shadowbench.frameworks` prints the whole mapping as JSON.

## The AIBOM export

```bash
# corpus truth: every expected entity (add --include-decoys for the decoys, labeled none)
python -m tools.shadowbench.aibom --corpus benchmarks/shadowbench/cases/corpus.json --out truth.cdx.json
# what one tool reported on its ok rows of a run
python -m tools.shadowbench.aibom --corpus benchmarks/shadowbench/cases/corpus.json \
    --results benchmarks/shadowbench/cases/results/2026-10-11 --tool numbat --out numbat.cdx.json
```

Each entity is a component (`application`, `file`, `framework`, `library`,
`device`) or, when it is reached over a network rather than present (an
OAuth or SaaS app, a model server, a model provider), an entry of `services`.
Every entry carries `shadowbench:` properties: the key as written and in
`canonical-v1` form ([key-canonicalization.md](key-canonicalization.md)), the
case, surface, modality and label, and the `owasp-asi`, `owasp-llm` and
`mitre-atlas` references. The metadata names the corpus by SHA-256, the
mapping version and, for a tool export, the tool's recorded version and the
SHA-256 of its rows file.

The export is deterministic (no timestamp; a serial number derived from the
inputs), validates against the strict CycloneDX 1.6 schema in the tests, and
refuses a results directory recorded against another corpus. A tool export
is an inventory of what the tool said, matched to nothing: it is not a score
and says nothing about which reports were right.
