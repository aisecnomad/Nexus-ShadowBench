# Methodology

What ShadowBench measures, how each corpus was built and labeled, which
tools are run and how, and which controls stand against bias. The track
READMEs are the detailed protocols; this page states the shared design and
points to them. For the metrics themselves see [metrics.md](metrics.md).

## Contents

- [The question](#the-question)
- [Design principles](#design-principles)
- [Scope: nine surfaces](#scope-nine-surfaces)
- [What counts as an agent](#what-counts-as-an-agent)
- [Corpus construction](#corpus-construction)
- [Tool selection and execution](#tool-selection-and-execution)
- [Bias controls](#bias-controls)
- [What is and is not pre-registered](#what-is-and-is-not-pre-registered)
- [Known limits](#known-limits)

## The question

> Given what an operator can actually collect from a surface, which AI
> agents and which plain AI uses are present, and can a discovery tool find
> them without flagging the things that merely sound like AI?

Three live tracks ask it from different directions:

| Track | Holds constant | Varies | Detailed protocol |
|---|---|---|---|
| Cases | one platform-native input at a time | surface, input format, entity mix | [cases README](../benchmarks/shadowbench/cases/README.md) |
| Estate | one whole organization at once | which tool, which unit | [estate README](../benchmarks/shadowbench/estate/README.md) |
| Code surface | one repository checkout at a time | repository, language, framework | [code-surface README](../benchmarks/shadow-ai-discovery/README.md) |

[`benchmarks/shadowbench/README.md`](../benchmarks/shadowbench/README.md)
explains how the cases and estate tracks relate.

## Design principles

1. **Tool-neutral truth.** Ground truth is expressed in the platforms' own
   identifiers or in a shared fact taxonomy, never in any tool's finding
   schema. The alias tables that map package names, imports, hostnames and
   names onto facts are shared by the labeler and every adapter, and are
   independent of every tool's signatures, ShadowScan's included.
2. **Platform-native inputs.** A tool is pointed at what an operator can
   export or collect: an Okta app list, Graph objects, a LiteLLM spend log, a
   Power Platform export, a Zeek window, an osquery table, a home directory, a
   checkout. Where a tool reads its own offline format, its adapter converts
   and the conversion is documented in the adapter's docstring.
3. **Negatives that bite.** Decoys, controls and near-misses come from the
   confusions real tools make: infrastructure *agents*, *Bedrock* game
   servers, *MCP* as Minecraft Coder Pack or Microsoft Cloud Partner,
   *copilot* seat reports, *Gemini* exchange clients, embedding batches that
   look like agent loops, classic chatbots, flows whose names mention AI.
4. **Evidence for every label.** Every expected entity carries the evidence
   that justifies it; supporting records a tool may also report are listed
   as tolerated instead of being left ambiguous.
5. **Fail closed.** No crash, timeout, missing row or incomplete scan earns a
   true negative.
6. **A tool's own defaults.** No confidence threshold is imposed on top of
   what a tool reports, and no tool is given an allowlist, an inventory or a
   known-agent list.
7. **Scored only where declared, charged for everything.** In-scope metrics
   use only the surfaces and modalities a tool declares; estate-wide metrics
   charge every tool for the whole corpus.
8. **Everything hashed, everything committed.** Corpora, frozen artifacts,
   normalized rows, manifests, metrics and reports are committed; digests
   bind them; scoring a committed run needs no third-party tool.
9. **Disclose before claiming.** Every result sits beside its conflicts of
   interest, errata, in-sample status and run-specific disclosures.

## Scope: nine surfaces

| Surface | Where agents leave evidence | Cases modalities | Estate artifacts | Code track |
|---|---|---|---|---|
| code | dependencies, imports, MCP and agent configs, A2A cards, low-code exports, IaC | `checkout` (26 pinned repositories) | 11 authored repositories | 87 pinned repositories |
| identity | OAuth apps, service principals, grants, tokens | `okta-export`, `entra-export` | IdP exports | — |
| gateway | per-caller model traffic | `litellm-export`, `bedrock-export` | gateway and egress logs | — |
| low-code | bots, flows, AI steps | `powerplatform-export`, `n8n-export` | low-code exports | — |
| SaaS | installed and requested AI apps | `slack-export`, `github-export` | app inventories | — |
| cloud | managed agents, model endpoints, workloads | `aws-export`, `k8s-export` | cloud inventories | — |
| endpoint | coding agents, MCP clients and servers, extensions, session transcripts | `home` (40 home directories) | home trees and offline endpoint exports | — |
| network | AI service contacts and listening AI services | `passive` (Zeek), `active` (loopback mocks) | network logs | — |
| runtime | agent and model-server processes | `snapshot` (osquery), `live` (inert processes) | runtime process exports and a loopback live-sim | — |

The estate column summarizes the artifact groups under
[`benchmarks/shadowbench/estate/artifacts/`](../benchmarks/shadowbench/estate/artifacts/);
the estate README's Corpus section lists them.

## What counts as an agent

| Label | Rule | In |
|---|---|---|
| `agent` | an autonomous or tool-using AI agent, or an agent integration: a configured MCP server, a Copilot Studio agent, a Bedrock agent, a coding-agent CLI, an agent-framework process | cases; estate facts such as `lowcode-agent`, `agent-process` |
| `llm` | AI use without agent evidence: a chat SaaS app, a model server, a single-completion caller, a GPT step in a flow | cases; estate facts such as `gateway-caller`, `ai-service-contact` |
| `none` | no AI | cases decoys; estate controls and near-misses |
| facts | `framework`, `provider`, `mcp`, `mcp-client-config`, `agent-config`, `a2a`, `lowcode`, `iac` | code surface; cases code surface (`provider:*` facts are `llm`, all others `agent`) |

The exact per-surface rubrics are the module docstrings under
[`tools/shadowbench/cases/families/`](../tools/shadowbench/cases/families/);
the estate taxonomy is
[`tools/shadowbench/estate/taxonomy.py`](../tools/shadowbench/estate/taxonomy.py);
the code taxonomy and alias tables are
[`tools/discovery_benchmark/taxonomy.py`](../tools/discovery_benchmark/taxonomy.py).

A **shadow** agent is one not in the organization's approved inventory. The
estate supplies an agent registry
([`artifacts/registry/agents.yaml`](../benchmarks/shadowbench/estate/artifacts/registry/agents.yaml))
naming four registered positives: discovering them is still expected,
classifying them as shadow is not.

## Corpus construction

### Cases track

- **Generated export cases.** For each export-style surface and modality,
  the generator draws entity families by quota (45% agent, 15% plain AI, 40%
  decoy, with at least one decoy slot per export except on the gateway
  surface, which has no decoys), redraws collisions, and renders the
  platform's own files.
- **Endpoint and passive-network cases** reuse the 25 endpoint and 17
  network families that the earlier synthetic head-to-head benchmark
  pre-registered under `tools/benchmark/`, adding the artifact or client key
  each family plants.
- **Code cases** are 26 repositories of the code-surface corpus (16
  positive, 4 control, 6 near-miss), with their facts and tolerated facts.
- **Seed and streams.** Each surface and modality draws from its own random
  stream. New corpora seed each stream from a SHA-256 of the seed, surface
  and modality (`stream_scheme: sha256`). The committed 2026-10-11 corpus
  was built with a faulty legacy derivation under which the seed had no
  effect and four pairs of modalities shared a stream; `verify` prints this,
  and the cases README's Random streams section explains it.
- **Integrity.** The header records the seed and a SHA-256 over the
  generator sources; `verify` always rebuilds the cases and compares them,
  because a matching digest says only that the sources are unchanged.

### Estate track

- **Authoring.** One maintainer wrote each surface's artifacts and labels
  together from vendor semantics, in nine AI-assisted authoring passes, one
  per surface (not nine people). Artifacts were checked only to parse in
  ShadowScan's offline loaders; labels were never changed because a tool
  missed or flagged an entity.
- **Additions.** Agent session transcripts in two home trees, the agent
  registry and the live-sim services file.
- **Label-completeness audit.** Every runnable tool ran once and every
  unattributed prediction was audited; no entity label changed.
- **Freeze and errata.** `FREEZE.json` pins 139 files. Three integration
  errata (a lost `.vscode` file replaced, the fictional organization renamed
  from *Vantor* to *Adatum*, a services-file comment corrected) changed
  digests and are documented in the estate README.
- **Hard cases in both directions.** Positives that may exceed documented
  detection, and negatives that discovery tools, ShadowScan included, are
  known to over-flag.

### Code-surface track

- **Selection.** 87 public repositories pinned to a 40-character commit,
  spanning agent frameworks in several languages, MCP servers in five
  languages, committed MCP client configurations, coding-agent configuration
  surfaces, A2A cards, low-code exports and IaC; controls with no AI; and
  near-misses that use the vocabulary without the technology.
- **Labeling.** An evidence extractor
  ([`tools/discovery_benchmark/evidence.py`](../tools/discovery_benchmark/evidence.py))
  reads manifests, imports, committed configuration paths, code constructs,
  IaC resources and provider hostnames, with file and line pointers. Facts
  seen only in lock files, indirect Go requirements, test and fixture paths
  or documentation trees are tolerated; documentation-only mentions do not
  count. The output was reviewed by the benchmark author (a Claude session)
  and spot-checked.
- **Revisions.** Auditing every tool's false positives found labeling gaps
  and adapter bugs; labels moved to corpus v2 (839 expected facts) and two
  repositories chosen as negatives moved to the positive class with exactly
  the facts found.

## Tool selection and execution

Every open-source discovery tool that could be installed and run offline on
a surface was included; tools with no offline entry point are listed as not
run, with the reason observed. Examples from the track READMEs:

| Not run | Reason recorded |
|---|---|
| Cartography | needs Neo4j and live cloud APIs |
| power-pwn | needs a live Microsoft 365 / Power Platform tenant |
| Microsoft Copilot Studio Kit Agent Inventory | a Power Platform solution |
| Google k8s-aibom | an in-cluster controller with no manifest mode |
| AgentSight (eBPF mode) | eBPF uprobes on live TLS libraries; blocked on the run host |
| Cisco AI BOM | refuses to run without an LLM credential; the benchmark is offline |

Each adapter's docstring records the tool version, the exact command and the
output-to-entity mapping. Cases-track tool installs are hash-locked
([supply-chain.md](supply-chain.md#hash-locked-tool-installs)); estate and
code-surface installs are version-pinned, not hash-locked, and the 2026-10-11
runs predate the locks.
How each runner isolates a tool is described in the README's
[architecture section](../README.md#the-how-the-harness-and-running-it-accurately)
and in [harness.md](harness.md).

## Bias controls

| Risk | Control | Residual |
|---|---|---|
| Labels shaped to a tool | labels never changed because a tool missed or flagged; label audits run against every tool's false positives in both directions | one labeler, who knows ShadowScan's triggers |
| Format selection | platform-native inputs; conversions documented per adapter | offline formats are the ones ShadowScan parses; live-API and kernel tools cannot show their strength |
| Calibration on the test set | adapters calibrated on probe inputs and a small smoke corpus, by the author's account | git history cannot confirm it; the smoke corpus drew from the scored corpus's streams |
| Scorer tuned to results | revised rules re-applied to unchanged rows, with every change documented | rules were revised after the runs with their results in view |
| In-sample tuning | runs after rule changes are declared in-sample and never published as runs of record | only a newly authored held-out corpus can measure the changes |
| Answer-key leakage | disclosed where found (AI-Infra-Guard anchors appended by an earlier adapter) and re-scored | the harness, not the tool, attributes loopback scan targets |
| Silent failures | fail-closed scoring; wrapper exits and normalizers now fail on missing output | rows recorded before the fixes are disclosed |

## What is and is not pre-registered

- The endpoint and network families reused by the cases track were
  pre-registered in the earlier head-to-head benchmark.
- The real-world repositories benchmark (34) fixed its labeling rubric
  before any tool ran on it.
- For the cases track, the author states that rubrics, families, generator,
  adapters and original scorer were written before the scored run; the
  harness, rubrics, corpus and results were first committed together, so the
  history cannot confirm the order.
- Scoring rules for the cases and estate tracks were revised after their
  runs, with the results in view, and re-applied to unchanged rows.

## Known limits

See the README's
[limitations table](../README.md#limitations-and-the-road-to-independence)
and each track's limits section. In short: author-written synthetic data on
eight cases surfaces and the whole estate; one labeler; small per-surface
samples; offline formats only; mock services that approximate real
responses; one estate on one date; and a conflict of interest that only
independent replication can remove.
