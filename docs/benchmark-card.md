# ShadowBench benchmark card

A benchmark card for Nexus ShadowBench, in the spirit of model cards
(Mitchell et al., *Model Cards for Model Reporting*, FAT* 2019): what the
benchmark is for, what it is not for, what it measures and what to keep in
mind before using any number it produces. The corpora themselves are
described in the [datasheet](datasheet.md).

## Contents

- [Benchmark details](#benchmark-details)
- [Intended use](#intended-use)
- [Factors](#factors)
- [Metrics](#metrics)
- [Evaluation data](#evaluation-data)
- [Construction and labeling](#construction-and-labeling)
- [Quantitative analyses](#quantitative-analyses)
- [Ethical considerations](#ethical-considerations)
- [Caveats and recommendations](#caveats-and-recommendations)

## Benchmark details

| Field | Value |
|---|---|
| Name | Nexus ShadowBench |
| Question | Given what an operator can collect from a surface, which AI agents and which plain AI uses are present, and can a discovery tool find them without flagging the things that merely sound like AI? |
| Maintainer | [@aisecnomad](https://github.com/aisecnomad), the maintainer of [Nexus ShadowScan](https://github.com/aisecnomad/Nexus-ShadowScan), one of the tools under test |
| Development | One maintainer, with AI coding assistants. No independent human review has taken place |
| Version | Identified by repository commit. There is no release number: cite the commit and the `results/<date>/` directory you used |
| Origin | Extracted byte for byte from ShadowScan commit `0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d`; 555 files are bound by [`MIGRATION.json`](../MIGRATION.json) |
| License | [Apache-2.0](../LICENSE), with the original [NOTICE](../NOTICE) |
| Live tracks | [Cases](../benchmarks/shadowbench/cases/README.md), [Estate](../benchmarks/shadowbench/estate/README.md), [Code surface](../benchmarks/shadow-ai-discovery/README.md) |
| Runs of record | Cases 2026-10-11; Estate 2026-10-11; Code surface 2026-10-08 (all tools) and 2026-10-09 (ShadowScan alone, after changes driven by that corpus) |
| Preserved, not live | Six earlier benchmarks and the unverified ShadowBench-450 archive; see [results.md](results.md) |
| Contact | Public: issues and pull requests. Private: [security advisories](https://github.com/aisecnomad/Nexus-ShadowBench/security/advisories/new) |

## Intended use

### Primary uses

- **Regression evidence for discovery tools.** A tool author can measure
  recall and false-positive cost per surface and per input type, and catch
  regressions between versions on fixed, hashed inputs.
- **Behaviour on known inputs.** A security team can see which surfaces a
  tool reads at all, what it finds there, what it falsely flags, and how it
  fails (errors, incomplete scans), before rerunning it on its own data.
- **Method and harness reuse.** Researchers and independent evaluators can
  reuse the entity model, the fail-closed scoring rules, the isolation
  harness and the adapters to build their own corpora.
- **Checking a published number.** Anyone can re-score a committed run
  without installing any third-party tool; see
  [Level 1](../README.md#level-1-reproduce-the-published-numbers).

### Primary users

Discovery tool authors, security and platform teams evaluating tools,
researchers studying shadow AI discovery, and reviewers checking a claim
that cites ShadowBench.

### Out-of-scope uses

- **Vendor rankings, grades or tiers.** No grade is published, and the
  results tables are records of runs, not rankings. Tools are scored only on
  the surfaces they declare, through adapters the ShadowScan maintainer
  wrote.
- **Procurement decisions on these numbers alone.** The inputs are
  author-written, mostly synthetic, and small. Rerun the candidates on your
  own data.
- **Claims of field precision or recall.** No corpus here is a sample of a
  real organization; base rates, scale and record variety differ in the
  field.
- **Certification or compliance evidence.** A ShadowBench result does not
  show that an inventory is complete or that a control works.
- **Marketing claims of being "independently benchmarked".** ShadowBench is
  not independent. A claim must name the track, the run directory and the
  commit, and must say that the corpus and labels are author-written.
- **Executing corpus content.** The corpora are data; see
  [Handling the corpus safely](../README.md#handling-the-corpus-safely).

## Factors

| Factor | Values | Why it matters |
|---|---|---|
| Surface | code, identity, gateway, low-code, SaaS, cloud (including Kubernetes), endpoint, network, runtime | Tools read different subsets; coverage and in-scope accuracy are reported separately |
| Modality (cases track) | 16 input types, two per surface except endpoint (`home`) and code (`checkout`) | A tool may handle Okta exports but not Entra exports; results are reported per modality |
| Label | `agent`, `llm`, `none` (decoy) | Agent-tier metrics test whether a tool tells agents from plain AI use |
| Class (estate and code surface) | positive, control, near-miss | Near-misses carry AI vocabulary without AI technology; controls carry none |
| Difficulty | `easy`, `medium`, `hard` per case or entity | Recorded in the corpora: 257 of the 346 cases and 24 of the 137 estate entities are `hard` |
| Input format | The platforms' own export shapes (Okta and Graph exports, LiteLLM and Bedrock logs, Power Platform and n8n exports, Slack and GitHub admin exports, AWS CLI and `kubectl` JSON, Zeek logs, osquery rows), home directories, and repositories pinned by commit | No tool is handed another tool's format; conversions are documented in each adapter |
| Execution mode | Offline files, loopback mock services, inert processes | Tools that only work against live APIs or kernels cannot show their strength |
| Registry | A supplied agent registry in the estate (four registered entities) | Tests whether a tool separates registered agents from shadow ones |

## Metrics

Per entity, per fact and per case: true and false positives and negatives,
precision, recall, F1, specificity on decoys, balanced accuracy and MCC at
case level, agent-tier recall and agent false-alarm rate, estate recall
over the whole corpus, coverage out of nine surfaces, and, for the estate,
a shadow-versus-registered check. Precision, recall and specificity carry
Wilson 95% intervals; F1 carries a case-bootstrap interval; tools are
compared with an exact McNemar test. Errors, missing rows and incomplete
scans never earn a true negative.

[metrics.md](metrics.md) gives the definitions and formulas and the
differences between the three scorers; the README's
[The What](../README.md#the-what-methodology-and-metrics) summarizes them
with a worked example. Each scorer's module docstring is the normative rule.

## Evaluation data

| Track | Inputs | Ground truth | Size |
|---|---|---|---|
| Cases | 320 cases generated from written rubrics on eight surfaces, plus 26 public repositories pinned by commit | Per-case entities labeled `agent` or `llm`, tolerated keys and decoys | 346 cases, 738 expected entities, 735 decoys |
| Estate | One authored fictional organization, Adatum Logistics, across all nine surfaces at once | 137 entities (87 positive, 27 control, 23 near-miss) with facts, evidence pointers and anchors | 104 expected facts, 139 frozen files |
| Code surface | 87 public repositories (84 GitHub, 3 GitLab) pinned by commit | `<category>:<value>` facts with `kind:path[:line]` evidence | 65 positive, 10 control, 12 near-miss; 839 expected facts in 8 categories |

The [datasheet](datasheet.md) breaks these down by surface, modality,
class, label, difficulty and fact category.

## Construction and labeling

- **Cases.** Generated by `tools/shadowbench/cases/generate.py` from
  per-surface rubrics (the module docstrings under
  `tools/shadowbench/cases/families/`) at seed 20261011 with 40 cases per
  generated surface. Endpoint and passive-network cases reuse families
  pre-registered for an earlier benchmark; code cases reuse 26 repositories
  and their facts from the code-surface corpus. The committed corpus was
  built with a faulty random-stream derivation under which the seed had no
  effect and four pairs of modalities shared a stream; `verify` rebuilds it
  exactly.
- **Estate.** Authored by the maintainer in nine AI-assisted passes, one
  per surface, with each entity's artifacts and label written together from
  the vendor's semantics, then audited for label completeness after one run
  of every runnable tool, and frozen by SHA-256. Three integration errata
  are recorded in the [estate README](../benchmarks/shadowbench/estate/README.md).
- **Code surface.** Facts were extracted by
  `tools/discovery_benchmark/evidence.py` from manifests, imports, committed
  configuration paths, code constructs, infrastructure resources and
  provider hostnames, then reviewed by the session that built the benchmark.
  The labels were revised after the first run (corpus v2) by auditing every
  tool's false positives.
- **In every track** the same maintainer wrote the scanner under test, the
  labels and every other tool's adapter. Labels were not changed because a
  tool missed or flagged an entity, by the author's account; the git history
  cannot confirm the order of authoring for the cases track, whose harness,
  rubrics, corpus and results were first committed together.

## Quantitative analyses

The headline numbers of each run of record are in the README's
[Results of record](../README.md#results-of-record). [results.md](results.md)
indexes every committed run, historical result and archive with its status,
and each run's `REPORT.md` has the per-surface, per-modality and per-case
breakdowns, confidence intervals and paired tests. They are not repeated
here, so that there is one place to correct them.

Two readings matter more than any single number:

- **In scope versus estate-wide.** A narrow tool can have high in-scope
  precision and near-zero estate recall; both are true at once.
- **Disclosures beside the numbers.** Several tools' rows carry recorded
  defects of the harness of the time (an adapter that appended the answer
  key to AI-Infra-Guard's predictions, wrappers that always exited 0, exit
  codes accepted as success with no stderr kept). Read the track README's
  disclosures before using any row.

## Ethical considerations

- **Conflict of interest.** ShadowScan's maintainer wrote the corpora, the
  labels, the harness and the adapters for every competing tool, with format
  knowledge taken from ShadowScan's own documentation. The estate's input
  formats are the offline export formats ShadowScan parses. Every ShadowScan
  lead is suspect until someone without a stake reruns the benchmark.
- **In-sample tuning.** ShadowScan's detection rules were changed after the
  2026-10-11 runs with their errors in view, and after the 2026-10-08
  code-surface run with that corpus in view. Later ShadowScan runs on these
  corpora measure fit to them.
- **Fairness to other tools.** Adapters use each tool's defaults, impose no
  confidence threshold and give no tool an allowlist or inventory, and each
  adapter's docstring records the version, command and mapping. Tools that
  only work against live tenants, live cloud APIs or the kernel (power-pwn,
  Cartography, Google's k8s-aibom, AgentSight's eBPF mode, Microsoft's
  Copilot Studio Kit Agent Inventory) were listed as not run, with the
  reason, rather than scored as failures. Tool vendors can request a
  corrected adapter through an issue or a pull request.
- **Fictional organization naming.** The estate's organization was first
  named *Vantor*, which a real company adopted in 2025; it was renamed to
  *Adatum*, a widely used fictitious name. The artifacts name Adatum tenants
  on real SaaS parent domains (for example Okta, Dynamics and Azure). No
  harness contacts them, but tenants by those names may exist.
- **Synthetic credentials.** Artifacts carry fake keys and tokens, including
  synthetic JWTs, because discovery tools must handle them. Every value
  shaped like a known credential is approved by path, credential family and
  SHA-256 in `tools/secret_allowlist.json`, and CI checks every tracked file;
  anything that looks real should be reported privately through
  [SECURITY.md](../SECURITY.md).
- **Prompt-injection content.** The corpora deliberately contain
  prompt-injection text, agent instruction files such as `CLAUDE.md` and
  launcher commands. They must never be executed, and AI agents with tool
  permissions should not be pointed at them.
- **Personal data.** None is intended. Estate people and devices are
  fictional. The code-surface corpus references public repositories by URL
  and commit without redistributing them; a fetched checkout contains
  whatever its authors published, including commit metadata.

## Caveats and recommendations

- Treat every result as evidence about the listed inputs, not as field
  precision or recall, and cite the track, run directory and commit.
- Read in-scope metrics and estate recall together, and read per-surface
  tables before any headline.
- Small denominators produce extreme percentages: a 100% precision from one
  true positive has a Wilson interval of 21–100%.
- Re-score committed runs yourself before relying on them; it needs no
  third-party tool.
- To measure anything new, use a fresh corpus: generate one at another seed
  with the default `sha256` stream scheme, or better, author or label one
  independently and publish it as described in
  [submitting-results.md](submitting-results.md).
- Run third-party tools only on a disposable, externally isolated host with
  no credentials; the harness reduces what a tool can reach but is not a
  sandbox.
- Do not compare the unverified ShadowBench-450 archive with any track, and
  do not compare one tool's numbers across tracks: their tool lists,
  versions and scoring rules differ.
