# ShadowBench datasheet

A datasheet, following the questions of Gebru et al., *Datasheets for
Datasets* (Communications of the ACM, 2021), for the three corpora behind
ShadowBench's live tracks: the cases corpus, the estate corpus with its
artifacts and freeze manifest, and the code-surface corpus. Counts were read
from the committed JSON files. Where the repository does not record an
answer, this page says so instead of guessing. The
[benchmark card](benchmark-card.md) covers intended use and metrics.

## Contents

- [The three corpora](#the-three-corpora)
- [Motivation](#motivation)
- [Composition](#composition)
- [Collection process](#collection-process)
- [Preprocessing, cleaning and labeling](#preprocessing-cleaning-and-labeling)
- [Uses](#uses)
- [Distribution](#distribution)
- [Maintenance](#maintenance)

## The three corpora

| Corpus | File | Snapshot | Described in |
|---|---|---|---|
| Cases | [`benchmarks/shadowbench/cases/corpus.json`](../benchmarks/shadowbench/cases/corpus.json) | created 2026-10-11, seed 20261011 | [cases README](../benchmarks/shadowbench/cases/README.md) |
| Estate | [`benchmarks/shadowbench/estate/corpus.json`](../benchmarks/shadowbench/estate/corpus.json), [`artifacts/`](../benchmarks/shadowbench/estate/artifacts/), [`FREEZE.json`](../benchmarks/shadowbench/estate/FREEZE.json) | snapshot date 2026-10-11 | [estate README](../benchmarks/shadowbench/estate/README.md) |
| Code surface | [`benchmarks/shadow-ai-discovery/corpus.json`](../benchmarks/shadow-ai-discovery/corpus.json) | snapshot date 2026-10-08 | [code-surface README](../benchmarks/shadow-ai-discovery/README.md) |

All three files, and every estate artifact, are bound byte for byte by
[`MIGRATION.json`](../MIGRATION.json).

## Motivation

**For what purpose were the datasets created?** To measure, on fixed and
hashed inputs, which AI agents and plain AI uses a shadow AI discovery tool
finds on each of nine surfaces, and what it falsely flags. Before them there
was no shared corpus with entity-level truth and deliberate negatives for
this problem; see [The Why](../README.md#the-why-an-open-standard-for-discovery-claims).

**Who created them, and on whose behalf?** The maintainer of Nexus
ShadowScan ([@aisecnomad](https://github.com/aisecnomad)), working with AI
coding assistants, inside ShadowScan's repository. The estate corpus calls
its nine authoring passes "the nine surface authors"; they were not nine
people. The corpora moved to this repository unchanged.

**Who funded the creation?** Not recorded.

**Conflict of interest.** The creator also maintains ShadowScan, one of the
tools under test, and wrote every other tool's adapter. This is the single
most important fact about these datasets.

## Composition

### Cases corpus

**What do the instances represent?** A case is one platform-native input a
tool is pointed at: an export, a log window, a home directory, a set of
loopback services, a process table or a repository checkout. Each case
records `id`, `surface`, `modality`, `family`, `label`, `difficulty`,
`rationale`, its `files`, and `truth` with `expected` entities, `tolerated`
keys and `decoys`.

| Surface | Modalities | Cases | Case labels (`agent` / `llm` / `none`) | Expected entities | Decoys |
|---|---|---|---|---|---|
| code | `checkout` | 26 | 16 / 0 / 10 | 109 facts | 0 |
| identity | `okta-export`, `entra-export` | 40 | 18 / 6 / 16 | 96 | 159 |
| gateway | `litellm-export`, `bedrock-export` | 40 | 18 / 22 / 0 | 124 | 0 |
| low-code | `powerplatform-export`, `n8n-export` | 40 | 18 / 6 / 16 | 78 | 118 |
| SaaS | `slack-export`, `github-export` | 40 | 18 / 6 / 16 | 88 | 110 |
| cloud | `aws-export`, `k8s-export` | 40 | 18 / 6 / 16 | 77 | 133 |
| endpoint | `home` | 40 | 18 / 6 / 16 | 24 | 0 |
| network | `passive`, `active` | 40 | 18 / 6 / 16 | 44 | 50 |
| runtime | `snapshot`, `live` | 40 | 18 / 6 / 16 | 98 | 165 |
| **Total** | 16 | **346** | **160 / 64 / 122** | **738** | **735** |

Every generated modality holds 20 cases; endpoint holds 40 in its one
modality. Expected entities split 373 `agent` and 365 `llm`. The corpus also
lists 128 tolerated keys. Case difficulty: 257 `hard`, 72 `medium`, 17
`easy`. Code and endpoint negatives carry no decoy records: there any
reported key that is not tolerated is a false positive. The gateway surface
has no decoys because every caller in a gateway log uses a model; it tests
the agent tier only.

### Estate corpus

**What do the instances represent?** A labeled entity of one fictional
organization, Adatum Logistics: an AI agent or AI use (positive), something
clearly non-AI (control), or something with AI vocabulary and no AI
technology (near-miss). Each entity records `id`, `surface`, `class`,
`difficulty`, `unit`, `registered`, `expected` facts with evidence
pointers, `tolerated` facts, `anchors`, `artifacts` and a `rationale`.

| Surface | Positive | Control | Near-miss | Total |
|---|---|---|---|---|
| code | 6 | 2 | 2 | 10 |
| identity | 12 | 4 | 3 | 19 |
| gateway | 7 | 3 | 2 | 12 |
| low-code | 10 | 3 | 3 | 16 |
| SaaS | 11 | 5 | 3 | 19 |
| cloud | 10 | 3 | 3 | 16 |
| endpoint | 19 | 3 | 3 | 25 |
| network | 6 | 2 | 2 | 10 |
| runtime | 6 | 2 | 2 | 10 |
| **Total** | **87** | **27** | **23** | **137** |

The 87 positives carry 104 expected facts in 19 categories; the largest are
`ai-client` (12), `provider` (10), `lowcode-agent` (10), `bot-app` (10) and
`cloud-ai` (10). Entity difficulty: 69 `easy`, 44 `medium`, 24 `hard`. Four
positives are registered in the supplied agent registry
(`artifacts/registry/agents.yaml`): a Bedrock agent, a Copilot Studio bot, a
GitHub App AI reviewer and Claude Code on one laptop. One corpus-level
tolerated pair exists (`ai-client:generic` with anchor `.vscode`).

Units: 108 entities are estate-wide, 19 belong to three home trees
(`dev-laptop-01`, `dev-laptop-02`, `win-laptop-03`) and 10 to ten code
repositories, one each. [`FREEZE.json`](../benchmarks/shadowbench/estate/FREEZE.json)
pins the SHA-256 of 139 files: `corpus.json` and 138 artifacts.

| Artifact area | Files | Area | Files |
|---|---|---|---|
| `code/` (ten repositories) | 71 | `saas/` | 7 |
| `home/` (three home trees) | 29 | `gateway/` | 5 |
| `lowcode/` | 7 | `identity/` | 5 |
| `cloud/` | 4 | `network/` | 4 |
| `endpoint-exports/` | 3 | `runtime/`, `registry/`, `services/` | 1 each |

### Code-surface corpus

**What do the instances represent?** A public repository pinned to a
40-character commit, with `id`, `host`, `path`, `commit`,
`default_branch`, `class`, `languages`, `size_kb`, `file_count`,
`expected` facts with `kind:path[:line]` evidence, `tolerated` facts and
`notes`.

| Class | Repositories | Meaning |
|---|---|---|
| positive | 65 | at least one expected fact |
| control | 10 | no AI integration |
| near-miss | 12 | AI or agent vocabulary without AI integration |

Hosts: 84 GitHub, 3 GitLab. The 839 expected facts by category: `provider`
488, `framework` 156, `agent-config` 102, `mcp` 60, `mcp-client-config` 12,
`a2a` 10, `iac` 8, `lowcode` 3. The corpus also lists 57 tolerated facts.

### Questions common to all three

**Is any information missing from individual instances?** The estate's
`metadata.attribution` sentence ("longest anchor wins") no longer describes
the scorer and was left as written because the corpus is frozen. The cases
corpus header predates the `per_surface` and `stream_scheme` fields, and its
recorded generator digest no longer matches the current sources (see below).

**Are there relationships between instances?** Yes. The cases track's 26
code cases reuse code-surface repositories and their facts. Its endpoint and
passive-network cases reuse 25 endpoint and 17 network families
pre-registered by the earlier head-to-head benchmark in `tools/benchmark/`.
In the estate, 12 anchors also occur in files outside their entity's
artifacts; `estate validate` lists them.

**Are there recommended splits?** No. There is no training or held-out
split, and no corpus here is held out from ShadowScan's development.

**Are there errors, noise or redundancies?** Labels are one author's. The
known corrections are listed under
[Preprocessing, cleaning and labeling](#preprocessing-cleaning-and-labeling).
In the cases corpus, the modality pairs that shared a random stream have
label sequences that match case for case.

**Is the dataset self-contained?** The cases and estate corpora are. The
code surface and the cases track's code cases depend on public repositories
fetched at pinned commits; a repository that is deleted or rewritten
upstream can no longer be fetched.

**Does it contain confidential data, offensive content or personal data?**
None is intended. Estate people (for example `dana`, `marcus` and `priya`),
devices, accounts and tenants are fictional. The artifacts deliberately
contain synthetic credentials and prompt-injection text. A fetched public
repository contains whatever its authors published, including commit
metadata.

## Collection process

**How was the data acquired?**

- **Cases:** generated by `python -m tools.shadowbench.cases generate` from
  written rubrics (the module docstrings under
  `tools/shadowbench/cases/families/`). Export-style cases draw entity
  families by quota (45% agent, 15% plain AI, 40% decoy, with at least one
  decoy slot per export except on the gateway surface) and render each
  platform's files. Code cases come from the code-surface corpus.
- **Estate:** authored by hand, with AI assistance, one surface per pass;
  agent session transcripts, the agent registry and the live-sim services
  file were added afterwards.
- **Code surface:** public repositories chosen by the author, then labeled
  from their content (below).

**What sampling strategy was used?** Purposive selection by the author for
all three. The code-surface README describes the coverage the selection
aimed for (agent frameworks, MCP servers in five languages, coding-agent
configuration surfaces, A2A cards, low-code exports, infrastructure as code,
plus controls and near-misses) but no sampling procedure; no random
sampling was used. The cases generator's draws are pseudo-random within the
author's families.

**Over what time frame?** The snapshots are dated 2026-10-08 (code
surface) and 2026-10-11 (cases and estate). How long authoring took is not
recorded.

**Were ethical review processes conducted?** Not recorded. No human
subjects are involved.

## Preprocessing, cleaning and labeling

### Cases corpus

- **Labeling** is generated: each family states the entity's label and
  evidence, and decoys are drawn from confusions real tools make.
- **Calibration.** By the author's account, the adapters were calibrated on
  probe inputs and a 4-case-per-surface smoke corpus, never on the scored
  corpus. The git history cannot confirm this: harness, rubrics, corpus and
  results were first committed together.
- **Random-stream fault.** The committed corpus was built with an older
  stream derivation, kept as the `legacy` scheme only so the corpus still
  rebuilds. Under it the seed had no effect, so every seed builds the same
  346 cases, and four pairs of modalities shared one stream (Okta and
  Entra, LiteLLM and Power Platform, Bedrock logs and Slack, AWS and
  Kubernetes). The smoke corpus therefore drew from the scored corpus's own
  streams. New corpora use the `sha256` scheme.
- **Generator digest.** The header's digest was computed before the harness
  moved and before the digest covered the code corpus, so it no longer
  matches the current sources. `verify` rebuilds every case and finds them
  identical.

### Estate corpus

- **Labeling** was done with each artifact, from the vendor's semantics.
  Artifacts were checked to parse cleanly in ShadowScan's offline loaders
  (completeness only).
- **Label-completeness audit.** Every runnable tool ran once and every
  unattributed prediction was audited. The only recorded outcome in the
  corpus is the tolerated `.vscode` pair in `metadata.errata`; no entity
  label changed.
- **Errata at integration (2026-10-12):** one artifact lost to a
  `.gitignore` rule was replaced with a minimal extension manifest; the
  fictional organization *Vantor* was renamed to the same-length *Adatum*
  everywhere, including the recorded predictions; and a wrong path in the
  services file's comment was corrected. `FREEZE.json` was recomputed for
  each.

### Code-surface corpus

- **Labeling** was extracted by `tools/discovery_benchmark/evidence.py`
  from dependency manifests, imports, committed configuration paths, code
  constructs, infrastructure resources and provider hostnames, then
  reviewed and spot-checked by the session that built the benchmark. Facts
  seen only in lock files, indirect Go requirements, test and fixture paths
  or documentation-site trees are tolerated; documentation-only mentions do
  not count.
- **Revisions.** Auditing every tool's false positives after the first run
  found three labeling gaps (an npm alias, the `portkey-ai` package, the
  `api.replicate.com` host) and the documentation-tree rule, giving corpus
  v2 with 839 expected facts. A later audit found that the labeler missed
  Rust `use rmcp::...` imports; three Rust MCP servers were labeled. Two
  repositories chosen as negatives carried coding-agent configuration and
  were moved to the positive class with exactly those facts.

**Is the raw data saved?** The estate artifacts are committed. Cases are
regenerable and committed. Code-surface checkouts are not committed; the
pins are. The tools' raw outputs for the committed runs are not committed.

## Uses

**What have the datasets been used for?** The committed runs of record:
cases 2026-10-11 (nine tools), estate 2026-10-11 (nine runnable tools),
code surface 2026-10-08 (nine tools) and 2026-10-09 (ShadowScan alone). The
code-surface corpus is also the baseline of ShadowScan's weekly
[regression workflow](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml).
ShadowScan's detection rules were changed with the 2026-10-11 errors and the
code-surface corpus in view, so these corpora are in-sample for it.

**What should they not be used for?** Estimating field precision, recall
or base rates; ranking or grading vendors; training a detector and then
reporting results on the same corpus; and anything that executes their
content. See the [benchmark card](benchmark-card.md).

**Could the composition affect future uses?** Yes. The input formats are
offline exports, which disadvantages tools built for live APIs or kernel
tracing; the rubrics encode one author's theory of what evidence suffices;
and per-modality samples of 20 give wide intervals.

## Distribution

**How is it distributed?** In this public repository under
[Apache-2.0](../LICENSE), with the original [NOTICE](../NOTICE). The
estate artifacts and the cases corpus were authored for the benchmark.
Public repositories are referenced by URL and commit and are not
redistributed; fetched checkouts remain under their own licenses.

**Is there a DOI or other identifier?** No. Cite the repository commit and
the results directory; see [`CITATION.cff`](../CITATION.cff).

**Export controls or other restrictions?** None recorded.

## Maintenance

**Who maintains the datasets?** [@aisecnomad](https://github.com/aisecnomad);
see [GOVERNANCE.md](../GOVERNANCE.md).

**How can errors be reported?** Through the label dispute form in the
[issue chooser](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new/choose),
with the corpus, the case or entity id and evidence at the pinned commit. A
real credential or personal data goes to a private advisory instead; see
[SECURITY.md](../SECURITY.md).

**Will the datasets be updated?** Not in place. The committed corpora,
freeze and results are bound by `MIGRATION.json` and stay byte-identical
(the amendment ledger, `AMENDMENTS.json`, may change harness code but never
data),
because every recorded run is scored against them. A correction or a new
version is published in a new path with its own provenance, and historical
results keep their original corpus. Labels are not changed because a tool
missed or flagged an entity.

**Will older versions remain available?** Yes, in the repository and its
history.

**How can others contribute?** By proposing families, cases or an
independently authored corpus through the corpus proposal form, and by
following [CONTRIBUTING.md](../CONTRIBUTING.md) and
[submitting-results.md](submitting-results.md). Independently authored and
labeled corpora are the contribution this benchmark most needs.
