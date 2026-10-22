# Errata for preserved documents

Statements in files that [`MIGRATION.json`](../MIGRATION.json) binds byte for
byte and that are now stale or wrong. Those files cannot be edited without
breaking the record they belong to, and documentation is not amendable, so
each correction lives here instead. An erratum changes how a sentence should
be read. It never changes a corpus, a label, a recorded prediction or a
metric.

Report a new one with the
[label dispute or bug forms](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new/choose),
quoting the file, the line and the evidence.

| Id | File | Kind |
|---|---|---|
| [E1](#e1-code-surface-2026-10-09-reportmd-wording) | `benchmarks/shadow-ai-discovery/results/2026-10-09/REPORT.md` | report rendering |
| [E2](#e2-estate-readme-cites-the-changelog-for-the-october-14-entry) | `benchmarks/shadowbench/estate/README.md` | moved reference |
| [E3](#e3-the-weekly-gate-no-longer-uses-the-newest-baseline) | `benchmarks/README.md`, `tools/discovery_benchmark/README.md`, `benchmarks/shadow-ai-discovery/README.md` | superseded behaviour |
| [E4](#e4-the-cases-reproduce-block-assumes-one-repository) | `tools/shadowbench/cases/README.md` | layout after migration |
| [E5](#e5-links-to-files-that-stayed-in-shadowscan) | several track and harness READMEs | broken relative links |
| [E6](#e6-the-cases-harness-readme-describes-unlocked-installs-and-the-older-stage) | `tools/shadowbench/cases/README.md` | superseded behaviour |
| [E7](#e7-code-surface-repository-level-detection-counts-unverified-negatives-as-unflagged) | `benchmarks/shadow-ai-discovery/results/2026-10-09/metrics.json` and `REPORT.md` | scoring rule |
| [E8](#e8-a-surplus-generic-fact-is-credited-as-a-true-positive) | `benchmarks/shadow-ai-discovery/results/2026-10-09/metrics.json` and `REPORT.md` | scoring rule |

## E1: code-surface 2026-10-09 REPORT.md wording

**Says.** The near-miss and control table shows `clean (incomplete)` for
ShadowScan on BurntSushi/ripgrep, JamesNK/Newtonsoft.Json, psf/requests and
jenkinsci/docker-agent (lines 47, 51, 54 and 64).

**Read as.** `no facts (incomplete)`. Each of those scans was incomplete
(exit 3), so reporting no facts does not establish a clean negative. The
current renderer prints that wording: `tools/discovery_benchmark/report.py`
says that "neither a partial run nor legacy metrics without a coverage flag
establish a clean negative". The committed `metrics.json` is unchanged and
re-scores byte for byte; only these four cells differ when the report is
rendered again ([results.md](results.md)).

## E2: estate README cites the changelog for the October 14 entry

**Says.** Under Bias and limits, ShadowScan's detection rules "were changed
(the changelog's October 14 detection-precision entry)" after the 2026-10-11
run (line 696).

**Read as.** ShadowScan moved its detailed history from `CHANGELOG.md` to
`docs/engineering-log.md`. The entry is
[Detection precision, ambiguous app names and scoped correlation (October 14)](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/docs/engineering-log.md#detection-precision-ambiguous-app-names-and-scoped-correlation-october-14),
which covers the changes the estate README lists, including ambiguous Gemini
names. The in-sample finding stands: later ShadowScan runs on the 2026-10-11
estate measure fit, not accuracy.

## E3: the weekly gate no longer uses the newest baseline

**Says.** ShadowScan's weekly `benchmark.yml` "fails on a regression against
the newest committed baseline in `shadow-ai-discovery/results/`"
(`benchmarks/README.md`, line 34; `tools/discovery_benchmark/README.md`,
line 37). The code-surface README asks a new baseline to be published by
copying the run "into `results/<date>/`" and describing "what changed in this
README" (`benchmarks/shadow-ai-discovery/README.md`, lines 242 to 243).

**Read as.** Since
[aisecnomad/Nexus-ShadowScan#289](https://github.com/aisecnomad/Nexus-ShadowScan/pull/289)
the workflow compares against the run its `BASELINE_RUN` names (currently
`2026-10-09`), reports a later directory without using it, and fails when the
named directory lacks `metrics.json` or `runs.json`. A new baseline is a
reviewed change to `BASELINE_RUN` in ShadowScan. Its description goes in a
`README.md` inside the new run directory, because the code-surface README is
bound ([submitting-results.md](submitting-results.md)).

## E4: the cases reproduce block assumes one repository

**Says.** The cases harness README copies "your checkout" to
`/opt/nsb/Project-Nexus` and points ShadowScan's `tools.json` entry at it:
`"repo": "/opt/nsb/Project-Nexus"` (lines 130 and 169 to 175).

**Read as.** In this companion the scanner is a separate repository. Clone
this repository outside `/root` and `/home`, and set `"repo"` to a
Nexus-ShadowScan checkout at the commit you intend to measure; the adapter
records that checkout's commit. [running.md](running.md) gives the full
block.

## E5: links to files that stayed in ShadowScan

**Says.** Several preserved READMEs link relatively to `../docs/evaluation.md`,
`archive/reviews/`, `.github/workflows/benchmark.yml` and the changelog
(for example `benchmarks/README.md`, `benchmarks/shadowbench/README.md`,
`benchmarks/shadowbench/estate/README.md`, `benchmarks/realworld/README.md`
and `tools/benchmark/README.md`).

**Read as.** Those files remain in ShadowScan:
[docs/evaluation.md](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/docs/evaluation.md),
[archive/reviews/](https://github.com/aisecnomad/Nexus-ShadowScan/tree/main/archive/reviews),
[.github/workflows/benchmark.yml](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml)
and the [engineering log](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/docs/engineering-log.md).
The repository README says the links were kept as source evidence.

## E6: the cases harness README describes unlocked installs and the older stage

**Says.** Installs "are version-pinned, not hash-locked: each PyPI tool is
pinned to one version, but its transitive dependencies resolve at install
time, and the Fleet wrapper's indirect Go modules are resolved by `go mod
tidy`. Record `uv pip freeze` for each venv and the wrapper's `go.sum` next to
any results" (lines 160 to 165). The Isolation section starts the stage under
`unshare --net --pid --fork --kill-child --mount --propagation private
--mount-proc --ipc` (lines 49 to 51).

**Read as.** Since [#8](https://github.com/aisecnomad/Nexus-ShadowBench/pull/8)
`install_tools.sh` installs PyPI tools from committed hash locks in
`tools/shadowbench/cases/locks/`, builds the Fleet wrapper against a committed
`go.mod` and `go.sum`, and records the resolved set in `resolved/`, which the
runner copies into each run and re-checks before tools run. The stage also
gets UTS and cgroup namespaces, a fixed host name with `/etc/hostname` and
`/etc/hosts` masked, and per-invocation resource limits; `--sandbox oci` runs
it in a digest-pinned container. [supply-chain.md](supply-chain.md) and
[harness.md](harness.md#isolation) describe both. The 2026-10-11 run predates
all of this.

## E7: code-surface repository-level detection counts unverified negatives as unflagged

**Says.** The headline row gives ShadowScan `0/10` controls and `0/12`
near-misses flagged (line 15), and `metrics.json` gives its repository-level
detection `fp` 0 and precision 1.0.

**Read as.** Four of those 22 negatives were incomplete scans (exit 3: the
four `no facts (incomplete)` cells of [E1](#e1-code-surface-2026-10-09-reportmd-wording)),
and `tools/discovery_benchmark/score.py` counts a control or near-miss as
unflagged whatever the run's status or incomplete flag. So the cells say
"not flagged on 22", but only 18 were scanned completely: `0/10` and `0/12`
establish no more than 0 false alarms on 18 verified negatives. Cisco AIBOM's
22 negatives all failed and are likewise counted unflagged; its
repository-level precision is undefined either way. This contradicts the rule
in [metrics.md](metrics.md#fail-closed-rules) that a run that did not
demonstrably read its input never earns credit for finding nothing. The
committed numbers re-score byte for byte and stay as they are. A corrected
scorer would report unverified negatives separately, as the cases track
does, and would publish under a new scorer version in a new results
directory.

## E8: a surplus generic fact is credited as a true positive

**Says.** ShadowScan's value-level recall is 0.9482 and F1 0.9723
(`metrics.json`, `value_level.all`; 806 TP, 2 FP, 44 FN).

**Read as.** `match_values` credits a reported `<category>:generic` as a true
positive when the category's expected facts were already matched, without
consuming an expected fact, so TP plus FN can exceed the expected facts. In
the 2026-10-09 run this happens only for ShadowScan, 11 times. Counted as
neither (as the estate scorer treats a surplus report), its recall is 0.9476
and F1 0.9719; precision is unchanged at 0.9975. The committed numbers stay as
they are.
