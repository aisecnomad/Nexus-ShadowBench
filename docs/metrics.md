# Metrics

How ShadowBench turns a tool's output into numbers: the unit of truth, the
four outcomes, every reported metric with its formula, the uncertainty
estimates, the fail-closed rules, and where the three live tracks differ.
Each scorer's module docstring is normative; this page summarizes them and
says where to look when they disagree.

| Track | Scorer (normative) | Committed example |
|---|---|---|
| Cases | [`tools/shadowbench/cases/score.py`](../tools/shadowbench/cases/score.py) | [`results/2026-10-11/metrics.json`](../benchmarks/shadowbench/cases/results/2026-10-11/metrics.json) |
| Estate | [`tools/shadowbench/estate/score.py`](../tools/shadowbench/estate/score.py) | [`results/2026-10-11/metrics.json`](../benchmarks/shadowbench/estate/results/2026-10-11/metrics.json) |
| Code surface | [`tools/discovery_benchmark/score.py`](../tools/discovery_benchmark/score.py) | [`results/2026-10-09/metrics.json`](../benchmarks/shadow-ai-discovery/results/2026-10-09/metrics.json) |

## Contents

- [Units of truth](#units-of-truth)
- [Matching a report to the truth](#matching-a-report-to-the-truth)
- [The four outcomes](#the-four-outcomes)
- [Point metrics](#point-metrics)
- [Agent tier](#agent-tier)
- [Coverage and estate recall](#coverage-and-estate-recall)
- [Uncertainty and paired comparison](#uncertainty-and-paired-comparison)
- [Fail-closed rules](#fail-closed-rules)
- [How the three tracks differ](#how-the-three-tracks-differ)
- [What the scorer refuses](#what-the-scorer-refuses)
- [Worked example](#worked-example)
- [Reading the numbers](#reading-the-numbers)

## Units of truth

| Unit | Track | What it is |
|---|---|---|
| Entity | cases, estate | One thing the truth says is there: an OAuth app, a gateway caller, a bot, an AWS resource, a home-directory artifact, a client address or service, a process, or (cases code surface) a fact |
| Fact | code surface, estate value level, cases code surface | `<category>:<value>` from a tool-neutral taxonomy, for example `framework:langgraph`, `mcp-client-config:cursor`, `oauth-app:…` |
| Case | cases | One platform-native input a tool is pointed at; positive when it holds at least one expected entity |
| Repository | code surface | One checkout pinned by commit; positive, control or near-miss |
| Unit and run | estate | A run is one tool on one unit: the whole estate, one repository (`code:<name>`), one home tree (`home:<name>`) or the live-sim (`sim`) |

Every entity or fact has a label. `agent` is an autonomous or tool-using AI
agent or an agent integration; `llm` is AI use without agent evidence;
`none` is no AI (a decoy). In the estate, positives (87), controls (27) and
near-misses (23) play the same roles. **Tolerated** keys or facts are
supporting records a tool may report without credit or penalty, for example
a lock-file-only dependency, an agent's execution role, or the directory
around an expected artifact.

## Matching a report to the truth

**Cases track.** A reported key equal to a tolerated key is dropped. A
reported key matches an expected or decoy key when they are equal or, for
`artifact:` keys (home-directory paths), when the reported path lies
**inside** the expected or decoy directory: a tool that cites a file in
Claude Code's `.claude` directory has found it. Matching is one-way; a
reported ancestor directory never matches. Reported keys are de-duplicated.

**Estate track.** Predictions are free text with a fact, so the scorer
**attributes** each to at most one entity by its anchors: the candidates are
the entities on the prediction's surface that the run reaches; among those
whose anchor occurs in the prediction text, a positive that expects the fact
wins; remaining ties go to the longest anchor, then the first entity id; a
per-unit fallback handles inventory tools that print client names. Every
multi-candidate decision is recorded, and the ambiguous ones are counted. The
full rule, including harness-attributed scan targets for the live-sim, is in
the estate README's
[Attribution](../benchmarks/shadowbench/estate/README.md#attribution)
section.

**Code surface.** Facts are compared exactly at value level and by category
at category level. `<category>:generic` matches one expected fact of its
category. Tolerated facts are dropped first. Facts outside the taxonomy are
ignored, never penalized.

## The four outcomes

| Outcome | Entity or fact level | Case or repository level |
|---|---|---|
| **TP** | A report matches an expected entity or fact | A positive case with at least one TP (a false positive alone does not find it); code surface: any in-scope fact on a positive repository |
| **FP** | A report matches nothing expected or tolerated; if it hits a decoy it also counts against specificity | A negative case with any FP (cases code surface: or anything out of taxonomy); code surface: any in-scope fact on a control or near-miss |
| **FN** | An expected entity or fact not reported, including all of those on an `error` or missing row | A positive case without a TP |
| **TN** | A decoy left alone on a **complete `ok`** run; estate: an unflagged negative that a complete run reached and no incomplete or missing run reached | A negative case scanned completely with no FP |
| Neither | Tolerated keys; out-of-taxonomy code keys (counted as `out_of_taxonomy`); estate predictions outside a tool's declared surfaces (estate-wide numbers only) | Cases: a negative case whose every decoy the adapter withheld (`negatives_withheld`) |

## Point metrics

Counts are summed over every scored case or unit (micro-averaging), then the
ratios are taken. Every ratio is `null` when its denominator is zero, and the
report prints `n/a`.

| Metric | Formula | Notes |
|---|---|---|
| Precision | TP / (TP + FP) | "When it says AI, is it right?" With few predictions, 100% means no false positive, not a precise estimate |
| Recall | TP / (TP + FN) | Over the surfaces and modalities the tool declares (in scope) |
| F1 | 2·TP / (2·TP + FP + FN) | Cases and estate compute it from counts; the code-surface scorer computes 2PR/(P+R), which is the same value |
| Specificity | TN / D, where D is every decoy on scored rows (`ok` and `error`) minus withheld decoys | Decoys of error and incomplete rows stay in D and are never TN |
| Case recall | positive cases found / positive cases scored | Cases track |
| Case specificity | negative cases correct / negative cases scored | Cases track; withheld-only negatives excluded |
| Balanced accuracy | (case recall + case specificity) / 2 | Insensitive to the ratio of positive to negative cases |
| MCC | (TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN)) over case outcomes | From −1 (always wrong) through 0 (no better than chance) to 1; `null` when any margin is zero |
| Category-level P/R/F1 | as above, facts collapsed to their category | Code surface; credits a tool that names the right kind of thing but not the exact value |
| All-category value F1 | value F1 charging every tool for every expected fact | Code surface; how much of the problem the tool addresses at all |
| Repository-level detection | positives with any in-scope fact; controls and near-misses with any in-scope fact | Code surface |
| Timing | median, p90 and maximum seconds per `ok` case or unit | Indicative only; runs are parallel |

## Agent tier

Discovery is not only "is there AI here" but "is it an agent". The cases
track scores that distinction separately:

- **Agent recall** = expected `agent` entities the tool reported **with the
  label `agent`** / expected `agent` entities. A tool that reports a generic
  `ai` label earns no agent-tier credit.
- **Agent false-alarm rate** = `llm` entities and decoys the tool labeled
  `agent` / the agent false-alarm universe. An `error` row is left out of the
  universe; an incomplete run adds only the entities it did call agents;
  withheld decoys are left out.

The estate track has a related **shadow layer**: for a tool that emits a
registry verdict, each detected registered entity should read `registered`
and each detected unregistered positive should read `shadow`.

## Coverage and estate recall

A narrow tool is not penalized in scope for what it does not claim, and a
broad tool cannot hide its misses behind a narrow scope:

- **Coverage** is the number of surfaces, out of nine, on which the tool ran
  at least one case; running one modality of a surface covers it.
- **Estate recall** (cases) is TP over **all 738** expected entities in the
  corpus, so every surface and modality the tool does not run counts as
  missed.
- **Estate-wide** numbers (estate) are positives detected out of all 87 and
  value recall over all 104 expected facts.
- **All-category value F1** (code surface) charges every tool for every
  expected fact.

Report in-scope and estate-wide numbers together. Either alone misleads.

## Uncertainty and paired comparison

| Estimate | Method | Applies to |
|---|---|---|
| Proportion intervals | Wilson score interval at 95% (z = 1.959964) | Cases precision, recall and specificity, overall and per surface |
| F1 interval | Percentile bootstrap over cases, 2,000 resamples, fixed seed 7, 2.5th and 97.5th percentiles; reported only when more than 40 resamples are defined | Cases F1 |
| Paired comparison | Exact two-sided McNemar test on case-level correctness: with b cases only the reference got right and c only the other tool got right, p = min(1, 2·Σ_{i≤min(b,c)} C(b+c, i) / 2^(b+c)) | Each tool against the reference (ShadowScan unless `score --reference` names another), over the cases both ran |

Wilson intervals behave sensibly at 0% and 100% and at small n, where the
normal approximation fails. The bootstrap resamples whole cases, so entities
in one case stay together. The McNemar test uses only the discordant cases;
it says whether two tools disagree with the rubric in a balanced way, not
which tool is better in the field. Twenty cases per modality give wide
intervals; generate at a larger `--per-surface` for narrower ones.

## Fail-closed rules

The central design rule: **a run that did not demonstrably read its input
never earns credit for finding nothing.**

| Situation | Cases track | Estate track | Code surface |
|---|---|---|---|
| Crash, timeout, unreadable output | `error`: all expected entities FN; decoys in D, not TN; case missed or false alarm | Run incomplete: every entity it reaches is unscored (positive not detected, negative earns no TN) | Status recorded; counts as a miss |
| No result row | Counted as `error` and reported as `missing`, unless the tool does not run that surface and modality | A unit with labeled in-scope entities and no run is `missing`; its entities are unscored | Counts as a miss |
| Tool says it did not read everything (ShadowScan exit 3) | `ok` + incomplete: keeps TP and FP, no TN, negative case is a false alarm, counted separately | Incomplete: unscored, earns nothing | Facts kept as a lower bound, flagged `incomplete`, cells marked `(incomplete)`, never a clean negative |
| Exit code outside the adapter's accepted set | `error`, or `incomplete` when entities were still reported | Incomplete | Per adapter |
| Every command exited non-zero with no output | per adapter | Incomplete (catches tools that accept exit 1 as success) | per adapter |
| Surface or modality not declared | `unsupported`: out of in-scope metrics, missed in estate recall | Not in scope; counted estate-wide | Category out of scope; counted in all-category view |
| Adapter drops decoy records in conversion | `withheld_decoys`: out of that tool's D and agent false-alarm universe unless reported anyway | n/a | n/a |

## How the three tracks differ

The tracks were written separately and share only the code-surface taxonomy
helpers. **A tool's numbers on one track are not comparable with its numbers
on another.**

| Aspect | Cases | Estate | Code surface |
|---|---|---|---|
| Unit of truth | entity per case | entity (attributed by anchors) and fact | fact per repository |
| Truth source | rubric generator, plus 26 pinned repositories | one authored fictional organization | session-labeled public repositories |
| Negatives | decoys inside cases; negative cases | controls and near-misses | control and near-miss repositories |
| Incomplete run | keeps TP and FP, no TN | earns nothing | facts kept as a lower bound |
| `generic` facts | n/a | a surplus generic on a matched category is neither credited nor charged | a surplus generic is credited |
| Intervals and tests | Wilson, bootstrap, McNemar | point estimates | point estimates |
| Agent distinction | agent tier | shadow layer (registry) | categories (`framework`, `mcp`, `agent-config`, …) |

## What the scorer refuses

Integrity checks run before any number is computed.

| Check | Cases | Estate | Code surface |
|---|---|---|---|
| Results were recorded against this corpus | manifest corpus SHA-256 must match | freeze record checked against `FREEZE.json` | corpus loaded and validated |
| Every results file belongs to a tool the manifest ran | refused unless `--force` | one row per tool and unit | runs read from `runs.json` |
| Row-status counts match the manifest | refused unless `--force` | n/a | n/a |
| Results file digest matches `rows_sha256` | refused unless `--force`; tools without a recorded digest listed in `rows_unbound` | n/a | n/a |
| Malformed rows (unknown status, duplicate case, unknown case, mismatched tool, surface, modality, family, label or difficulty, `unsupported` beside `ok`/`error` on one pair) | refused even with `--force` | malformed records stop scoring with exit 2 | validated |

A forced score lists every override in `metrics.json` (`forced`) and at the
top of `REPORT.md`. Never publish a forced score as a run of record.

## Worked example

One tool on one modality with four cases:

| Case | Truth | Tool outcome | Entity outcomes | Case outcome |
|---|---|---|---|---|
| A, positive | expected `a1 a2 a3`; decoys `d1 d2` | `ok`, reports `a1 a3 d1` | TP `a1 a3`; FN `a2`; FP `d1`; TN `d2` | found (TP) |
| B, negative | decoys `d3 d4` | `ok`, reports nothing | TN `d3 d4` | correct (TN) |
| C, positive | expected `a4`; decoy `d5` | timeout → `error` | FN `a4`; `d5` in D, not TN | missed (FN) |
| D, negative | decoy `d6` | `ok`, flagged incomplete, reports nothing | `d6` in D, not TN | false alarm (FP) |

| Metric | Value | 95% interval |
|---|---|---|
| Precision | 2 / (2 + 1) = 66.7% | Wilson 20.8–93.9% |
| Recall | 2 / (2 + 2) = 50.0% | Wilson 15.0–85.0% |
| F1 | 4 / (4 + 1 + 2) = 57.1% | (bootstrap needs more cases) |
| Specificity | 3 / 6 = 50.0% | Wilson 18.8–81.2% |
| Case recall, specificity | 1/2, 1/2 | |
| Balanced accuracy | 50% | |
| MCC | (1·1 − 1·1) / √(2·2·2·2) = 0 | |

A scorer that read C's timeout and D's incomplete scan as clean would report
specificity 4/6 and a flawless negative record.

**Agent tier.** Suppose `a1`, `a2` and `a4` are `agent` in truth, `a3` is
`llm`, and the tool labeled every report `agent`. Agent recall counts
expected agents on scored rows (A and C): only `a1` was reported as an
agent, so 1/3 = 33%. The agent false-alarm universe is the `llm` entities
and decoys of complete `ok` rows (A: `a3 d1 d2`; B: `d3 d4`), plus, for the
incomplete row D, only the entities it did call agents (none); the error row
C adds nothing. The tool called `a3` and `d1` agents: 2/5 = 40%.

**Estate recall.** If the corpus held 10 expected entities across all
surfaces, estate recall would be 2/10 = 20%, whatever the tool's in-scope
recall.

## Reading the numbers

- Read in-scope and estate-wide figures together, and coverage beside both.
- Read precision with its denominator: 100% of 3 predictions is not 100% of
  300.
- Read every interval. Overlapping intervals on 20 cases do not separate two
  tools.
- Read the incomplete, error and withheld counts before any specificity.
- Read the disclosures and the in-sample status of the run. A ShadowScan
  number on a corpus its rules were tuned against measures fit, not accuracy.
- Never compare across tracks, and never with the
  [ShadowBench-450 archive](../benchmarks/shadowbench-450/README.md).
