# Glossary

The terms of art used across ShadowBench's corpora, scorers, reports and
documentation, in alphabetical order. Where a term means something slightly
different in each track, the entry says so. The scorers' module docstrings
(`tools/shadowbench/cases/score.py`, `tools/shadowbench/estate/score.py`
and `tools/discovery_benchmark/score.py`) are the normative definitions;
[metrics.md](metrics.md) gives the formulas.

[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) ·
[H](#h) · [I](#i) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) ·
[R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w)

## A

**agent.** The label for an autonomous or tool-using AI agent, or an agent
integration: a configured MCP server, a Copilot Studio agent, a Bedrock
agent, a coding-agent CLI, an agent-framework process. In the cases track it
labels expected entities; each case also carries a case label, `agent`,
`llm` or `none`, which the generator plans before composing the case.

**agent false alarm.** In the cases track, an expected `llm` entity or a
decoy that a tool labeled `agent`. The agent false-alarm rate divides those
by the agent false-alarm universe: the `llm` entities and decoys of the
tool's `ok` rows, less withheld decoys. An error row is left out of the
universe, and an incomplete run adds only the entities it did call agents.

**agent tier.** The cases-track measurements that ask whether a tool tells
agents from plain AI use. Agent-tier recall counts an expected `agent`
entity as found only when the tool reported it labeled `agent`; a tool that
reports only `ai` earns no agent-tier credit.

**amendment, AMENDMENTS.json.** A recorded change to a migrated file of
live harness code or tests (`tools/shadowbench/`, `tools/discovery_benchmark/`,
`tests/`) or to the copied `requirements-ci.lock` or
`requirements-build.lock`. Each entry names the SHA-256 the file changes from (its migrated
bytes or its previous amendment), the bytes, Git blob, mode and SHA-256 it
changes to, a reason and a reference. `python -m tools.verify_migration
--amend PATH [PATH ...]` appends one per file. Evidence, the cases generator and families, the
labeler, the taxonomies, the legacy harnesses and the original runtime
lock can never be amended.

**anchor, primary anchor.** In the estate track, a lowercase token grounded
in an entity's artifacts (an app id, an ARN, a server name, a client IP or a
`host:user:tool` composite) that ties a tool's prediction to the entity when
it occurs in the prediction's text. The first anchor is the primary anchor;
primary anchors are unique across the corpus, but 12 anchors also occur in
files outside their entity's artifacts, which `estate validate` reports as
warnings.

**attribution.** The estate scorer's rule that gives each prediction at
most one owning entity: drop corpus-level tolerated pairs, take candidates
on the prediction's surface within the run's reach, match anchors with a
fact-based preference among positives and length and id tie-breaks, fall
back to the one unit-labeled candidate that expects the fact, or, for runs
that record scan targets, map the target through `services.json`.
Unattributed in-scope predictions are false positives.

## B

**balanced accuracy.** The mean of case-level recall and case-level
specificity, computed only when a tool has both positive and negative cases
scored. It does not reward a skewed mix of positive and negative cases.

**bootstrap interval.** The cases track's 95% interval for F1: 2,000
resamples of the scored cases with replacement, under a fixed seed, taking
the 2.5th and 97.5th percentiles of the resampled F1. It is reported only
when more than 40 resamples give a defined F1.

## C

**case.** In the cases track, one platform-native input a tool is pointed
at, with its surface, modality, family, label, difficulty, files and truth
(expected entities, tolerated keys and decoys). Case ids are positional, so
the scorer requires the run manifest to name the SHA-256 of the corpus being
scored.

**category.** The first part of a fact. The code surface has eight:
`framework`, `provider`, `mcp`, `mcp-client-config`, `agent-config`, `a2a`,
`lowcode` and `iac`; the estate taxonomy adds categories for the other
surfaces, such as `oauth-app`, `bot-app`, `cloud-ai` and `agent-process`.
The code-surface scorer also reports a category level, where facts are
collapsed to their category.

**control.** A negative with no AI at all: a code repository with no AI
integration, or an estate entity that is clearly non-AI. Any attributed
in-scope finding on a control is a false positive.

**coverage.** In the cases track, the number of surfaces, out of nine, on
which a tool ran at least one case; running one modality of a surface
covers it.

## D

**decoy.** In the cases track, a record labeled `none` whose key belongs to
the true-negative universe: a service account without AI, a monitoring
*agent*, a Minecraft *Bedrock* server, an app named *copilot*. Decoys are
drawn from confusions real tools make. Reporting one is a false positive and
counts against specificity; leaving it alone is a true negative only on a
complete `ok` run.

**difficulty.** `easy`, `medium` or `hard`, recorded per case in the cases
corpus and per entity in the estate corpus.

**disposition.** The field of each [`MIGRATION.json`](../MIGRATION.json)
entry that says how the file reached this repository: `moved` (546 files
moved out of ShadowScan), `copied-support` (8 files copied because this
repository needs them to run or to carry its license, such as `LICENSE`,
the lock files and `tools/check_secrets.py`) or `copied-source-context` (1
file, ShadowScan's secret allowlist, kept as provenance).

## E

**entity.** A unit of ground truth. In the cases track, an expected entity
(a key, an `agent` or `llm` label and evidence) or a decoy. In the estate,
one of 137 labeled entities (positive, control or near-miss) with facts,
evidence pointers, anchors, artifacts and a unit.

**entity key.** A tool-neutral identifier taken from the platform's own
data: an Okta app id or Entra `appId`, a gateway key alias or principal ARN,
a Power Platform bot or flow id, an n8n workflow id, a Slack app id or
GitHub App slug, an AWS ARN or `namespace/Kind/name`, an `artifact:` path
under the home directory, a client address or `ip:port`, a process key, or,
for code, a `<category>:<value>` fact.

**error row.** A cases-track row with status `error`: a crash, a timeout or
unreadable output. It is never a correct outcome: every expected entity is
missed, its decoys stay in the specificity denominator without being true
negatives, and the case counts as missed or as a false alarm.

**estate.** (1) The estate track's corpus: one authored fictional
organization, Adatum Logistics, across all nine surfaces. (2) The `estate`
unit: a run over the whole estate at once, as ShadowScan's is, which reaches
every entity.

**estate recall.** In the cases track, true positives over all 738 expected
entities in the corpus, counting every surface and modality the tool does
not run as missed. The estate track's equivalent, *estate-wide*, is
positives detected out of all 87 and value recall over all 104 expected
facts.

## F

**fact.** A `<category>:<value>` item such as `framework:langgraph` or
`mcp-client-config:cursor`, from a tool-neutral taxonomy shared by the
labeler and every adapter. `<category>:generic` is a wildcard that matches
one expected fact of its category.

**family.** In the cases track, a rubric-defined generator of entity drafts
(for example an Okta app for an AI SaaS product, or a decoy whose name only
sounds like AI). A case's `family` names the families it was composed from.

**force (`--force`).** The scorer override that scores results the run
manifest does not vouch for: a corpus hash mismatch, a file from a tool the
manifest does not list, row counts or a digest that disagree. A forced
score lists every override in `metrics.json` and at the top of the report.
Malformed rows are refused even with `--force`.

**freeze.** The estate's [`FREEZE.json`](../benchmarks/shadowbench/estate/FREEZE.json),
which pins the SHA-256 of 139 files (`corpus.json` and 138 artifacts).
`estate verify-freeze` checks for drift. A freeze is never refreshed to hide
drift; a changed estate is a new estate.

## G

**generator digest.** A SHA-256 over the cases generator's sources, each
named by its repository-relative path, recorded in the corpus header. The
committed corpus's digest no longer matches the current sources, because it
was computed before the harness moved and before the digest covered the
code corpus; `verify` rebuilds every case regardless and finds them
identical.

## H

**harness commit, `harness_dirty`.** Fields the current runners record in
the run manifest: the harness checkout's `HEAD` (null when git cannot name
it), and whether anything under `tools/`, untracked files included, differed
from it (null when unknown). The 2026-10-11 manifests predate them.

## I

**in-sample.** Describes a result on a corpus whose errors influenced the
tool's development. ShadowScan's rules were changed after the 2026-10-11
runs with those runs' errors in view, and after the 2026-10-08 code-surface
run with that corpus in view, so later ShadowScan runs on these corpora
measure fit to them, not field accuracy.

**in scope.** Restricted to what a tool declares: surfaces and modalities
in the cases track, surfaces in the estate, categories on the code surface.
In-scope metrics do not penalize a tool for what it does not claim; estate
recall does.

**incomplete run.** A run that did not read everything. In the cases track,
an `ok` row the tool flagged as incomplete (ShadowScan's exit 3), or a run
that exited outside the adapter's accepted codes but still reported
entities; it keeps its true and false positives but never earns a true
negative, and an incompletely scanned negative case is a false alarm. In
the estate, an incomplete run leaves every entity it reaches unscored. On
the code surface, an incomplete run is scored on the facts it found and its
cells are marked `(incomplete)`.

**inert process.** A static binary, built with `gcc`, that the cases runner
spawns under a recorded process name and command line inside the tool's PID
namespace for `runtime/live` cases, so a tool that reads `/proc` sees the
processes a snapshot describes. Reported pids are translated back to the
corpus's process keys.

## L

**live-sim.** The estate's `sim` unit: AI-Infra-Guard scanning loopback mock
services that `tools/shadowbench/estate/simhost.py` serves from
`artifacts/services/services.json`, standing in for two runtime entities. A
`sim` run reaches only those two entities.

**llm.** The label for AI use without agent evidence: a chat SaaS app, a
model server, a single-completion caller, a GPT step in a flow.

## M

**manifest.** The cases track's `results/<date>/manifest.json`: corpus path
and SHA-256, generator digest, platform, and per tool its version and
row-status counts; the current runner also records `rows_sha256`, the
harness commit and `harness_dirty`. The estate's and the code surface's run
records are `runs.json`. Not to be confused with `MIGRATION.json`.

**MCC.** The Matthews correlation coefficient on case-level outcomes,
(TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN)), from −1 (always wrong)
through 0 (no better than chance) to 1 (always right). It is undefined when
a tool has no positive or no negative cases, or when the denominator is
zero.

**McNemar test.** The exact, two-sided paired test the cases track uses to
compare a tool with the reference tool (ShadowScan unless `score
--reference` names another) on case-level correctness over the cases both
ran. Only discordant cases count: those only one of the two got right.

**MIGRATION.json.** The record of the 555 files imported from ShadowScan
commit `0792106b`: each file's path, source path where it differs,
disposition, size, Git blob, mode and SHA-256. `python -m
tools.verify_migration` checks every one, against its migrated bytes or its
latest [amendment](#a).

**missing row.** A case with no result row. In the cases track it counts as
an error and is reported as missing, unless the tool does not run that
surface and modality. In the estate, a code or home unit labeled with an
entity on a tool's declared surfaces is missing when the tool has neither a
run for it nor a whole-estate run.

**mock service.** A loopback HTTP service, started by
`tools/shadowbench/cases/mockserv.py` inside the tool's network namespace
for `network/active` cases, that answers the routes a fingerprinting scanner
probes the way the real product does (Ollama, vLLM, Open WebUI, an MCP
server, an OpenClaw gateway) or the way a decoy does (Grafana, Jenkins, a
Datadog Agent Manager page, a Minecraft *Bedrock* panel). Mocks reproduce
banners and version endpoints, not full applications.

**modality.** The input type within a surface, such as `okta-export` or
`entra-export` on identity, or `passive` and `active` on network. The cases
track has 16.

## N

**near-miss.** A negative with AI-adjacent vocabulary or shape and no AI
technology: a user-agent parser, an MCP2515 CAN-bus library, the
crypto-exchange host `api.gemini.com`, a "Gemini Wallet" extension.
Flagging it is a false positive.

**none.** The label of a decoy, and of a cases-track case with no expected
entity.

## O

**out of taxonomy.** On the code surface of the cases track, a reported key
that is not a `<category>:<value>` fact, such as a file path an adapter
could not map. It is neither a true nor a false positive at entity level
and is counted per tool; at case level it earns a positive case nothing and
makes a negative case a false alarm. Adapters that drop such hits count
them in the row's `out_of_taxonomy`.

## P

**positive.** A case with at least one expected entity (cases), a
repository with at least one expected fact (code surface), or an estate
entity that is a genuine AI agent or AI use per its artifact's vendor
semantics.

## R

**reach.** In the estate, which entities a run can be scored on, decided
from its unit alone: `estate` reaches every entity; `code:<repo>` and
`home:<device>` reach that unit's entities plus estate-wide entities with an
artifact inside its tree; `sim` reaches the entities a `services.json`
service stands in for. An in-scope entity no complete run reaches is *not
reached*: a positive is missed and a negative earns no true negative.

**registry, shadow verdict.** The estate supplies an agent registry
(`artifacts/registry/agents.yaml`) naming four registered positives. For a
tool that emits a registry verdict, the shadow layer checks that detected
registered entities read registered and detected unregistered positives
read shadow.

**`rows_sha256`.** The SHA-256 of a tool's `<tool>.jsonl` that the current
cases runner records in the manifest. The scorer refuses a file whose digest
differs, unless `--force` is given.

**`rows_unbound`.** The list, in a cases `metrics.json`, of tools whose
rows the manifest binds only by their row-status counts because it records
no `rows_sha256`; an edited or swapped file with the same counts would not
be detected. All nine tools of the 2026-10-11 run are listed.

**run of record.** The committed run a track's README designates as its
published result, such as the estate's 2026-10-11 run. In-sample replays do
not replace it, and a new run is published in a new dated directory.

## S

**stream scheme.** How the cases generator seeds the random stream of each
surface and modality. `sha256`, the current default, seeds each stream from
a SHA-256 of the seed, surface and modality. `legacy`, used by the committed
2026-10-11 corpus and kept only to rebuild it, took the last 62 bits of the
text `<seed>:<surface>:<modality>`, so the seed had no effect and four pairs
of modalities shared a stream.

**surface.** One of the nine places where shadow AI agents leave evidence:
code, identity, gateway, low-code, SaaS, cloud (including Kubernetes),
endpoint, network and runtime.

## T

**tolerated key, tolerated fact.** Something a tool may report without
credit or penalty. Cases carry tolerated keys (a client's parent directory,
an agent's execution role, a pending install request). Estate entities carry
tolerated facts, and the corpus has one tolerated (fact, anchor) pair.
Code-surface facts seen only in lock files, indirect Go requirements, test
and fixture paths or documentation-site trees are tolerated.

## U

**unit.** In the estate, what one run covers: `estate`, `sim`,
`code:<repo>` or `home:<device>`. Each entity also names the unit it
belongs to; 108 of the 137 are estate-wide.

**unsupported row.** A cases-track row for a case on a surface and modality
the tool does not run. It is left out of in-scope metrics and counted as
missed in estate recall, and it may not sit beside `ok` or `error` rows of
the same tool on the same surface and modality.

## V

**value level.** Scoring of exact facts, micro-averaged, as opposed to
entity level, category level or repository level. Used by the estate and the
code-surface scorers.

## W

**Wilson interval.** The Wilson score 95% interval the cases track reports
for precision, recall and specificity. Unlike the plain normal
approximation it stays inside 0–100% and remains informative for small
counts: one true positive out of one prediction gives 100% precision with an
interval of 21–100%.

**withheld decoy.** A decoy whose record an adapter's conversion never
passes to its tool, declared by key prefix per surface and modality
(`withheld_decoys`). It is left out of that tool's specificity and agent
false-alarm denominators unless the tool reports it anyway. ShadowScan's
adapter withholds 17 AWS IAM-role decoys.
