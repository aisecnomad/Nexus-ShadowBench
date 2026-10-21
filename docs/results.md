# Results index

Every result set this repository holds, what it is, and how far it can be
trusted. All of them are author-written offline evidence: none is
independent review or measured field accuracy. Within a status, results are
listed by track.

| Status | Meaning |
|---|---|
| **Run of record** | The run a live track's README designates; its metrics re-score from committed rows |
| **Regression baseline** | Used to detect regressions; in-sample for ShadowScan, so it measures fit, not accuracy |
| **Historical** | An earlier benchmark with its own protocol and harness; its legacy helpers run only in the pinned `scanner-source` checkout |
| **Stale** | Its own README says not to quote it for the current code |
| **Unverified archive** | Counts supplied without the evidence needed to check them; no ranking or comparison |

## Live tracks

| Track and run | Status | Tools | Committed files | Reproduces at this commit | Read before quoting |
|---|---|---|---|---|---|
| [Cases, 2026-10-11](../benchmarks/shadowbench/cases/results/2026-10-11/REPORT.md) | Run of record | 9 run (ShadowScan, AgentDiscover, AI-Infra-Guard, SafeDep vet, Microsoft `agent-discovery`, Fleet `ai_tools`, Snyk Agent Scan, Cisco MCP Scanner, Numbat); 4 not run | `manifest.json`, `<tool>.jsonl` ×9, `metrics.json`, `REPORT.md` | `metrics.json` and `REPORT.md` byte for byte | rows recorded under weaker isolation by earlier adapters; scoring rules revised after the run; every tool `rows_unbound`; committed corpus built with the legacy stream scheme ([Integration changes](../benchmarks/shadowbench/cases/README.md#integration-changes)) |
| [Estate, 2026-10-11](../benchmarks/shadowbench/estate/results/2026-10-11/REPORT.md) | Run of record | 9 runnable (ShadowScan, Snyk Agent Scan, AgentDiscover, AI-Infra-Guard, SafeDep vet, Numbat, Agentic Radar, AgentSight, Cisco MCP Scanner); power-pwn and Cartography not runnable | `runs.json`, `metrics.json`, `tools.json`, `REPORT.md` | `metrics.json` and `REPORT.md` byte for byte | disclosures [a]–[e] ([Disclosures](../benchmarks/shadowbench/estate/README.md#disclosures-for-the-2026-10-11-run)); later ShadowScan runs are in-sample ([Bias and limits](../benchmarks/shadowbench/estate/README.md#bias-and-limits)) |
| [Code surface, 2026-10-08](../benchmarks/shadow-ai-discovery/results/2026-10-08/REPORT.md) | Multi-tool run before the benchmark-driven changes | 9 run (ShadowScan, NuGuard, Trusera ai-bom, SafeDep vet, cdxgen, AgentDiscover, SafeDep xbom, Agentic Radar, Geiger); Cisco AI BOM skipped | `runs.json`, `metrics.json`, `tools.json`, `REPORT.md` | No: scored against the labels as first published (835 facts); the current corpus has 839 | 43 of 87 ShadowScan scans incomplete; four runs of other tools did not finish ([Results 2026-10-08](../benchmarks/shadow-ai-discovery/README.md#results-run-of-2026-10-08-before-the-changes)) |
| [Code surface, 2026-10-09](../benchmarks/shadow-ai-discovery/results/2026-10-09/REPORT.md) | Regression baseline (in-sample) | ShadowScan re-run; the other tools' rows are their 2026-10-08 runs re-normalized with fixed adapters | `runs.json`, `metrics.json`, `tools.json`, `REPORT.md` | `metrics.json` byte for byte; `REPORT.md` except four cells (below) | measures fit to the corpus that drove the changes ([Results 2026-10-09](../benchmarks/shadow-ai-discovery/README.md#results-shadowscan-after-the-benchmark-driven-changes-2026-10-09)) |

**Known rendering difference.** Re-rendering the 2026-10-09 code-surface
`metrics.json` with the current `report` command prints
`no facts (incomplete)` in four cells (ShadowScan on BurntSushi/ripgrep,
JamesNK/Newtonsoft.Json, psf/requests and jenkinsci/docker-agent) where the
committed `REPORT.md` says `clean (incomplete)`. The metrics are identical;
the current wording avoids calling an incomplete negative clean. The
committed report is preserved unchanged as historical evidence.

**Regression baseline selection.** ShadowScan's weekly
[`benchmark.yml`](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml)
compares against the run its `BASELINE_RUN` names (currently `2026-10-09`),
not the newest directory under `benchmarks/shadow-ai-discovery/results/`,
since [aisecnomad/Nexus-ShadowScan#289](https://github.com/aisecnomad/Nexus-ShadowScan/pull/289).
A later directory there is reported and ignored; moving the baseline is a
reviewed change in ShadowScan. See [submitting-results.md](submitting-results.md).

## Historical benchmarks

Each has its own README, protocol and limits. Several still describe the
shared ShadowScan repository layout they were written in.

| Benchmark | Results | Status | Notes |
|---|---|---|---|
| Synthetic head-to-head (900 seeded cases across repo, endpoint and network surfaces) | [`tools/benchmark/results/`](../tools/benchmark/results/README.md) | Historical | pre-registered corpus (seed `20261006`); generator-defined labels written by ShadowScan's maintainers |
| Same corpus, ShadowScan-only rerun after fixes | [`tools/benchmark/results-post-change/`](../tools/benchmark/results-post-change/README.md) | Historical, in-sample | "a regression check, not new evidence of accuracy" |
| Real-world repositories (34), repo-surface cohort | [`tools/benchmark/results-realworld/`](../tools/benchmark/results-realworld/README.md), corpus in [`benchmarks/realworld/`](../benchmarks/realworld/README.md) | Historical | labels by the author from a rubric fixed before any tool ran |
| Same, ShadowScan post-fix rerun | [`tools/benchmark/results-realworld-post-fixes/`](../tools/benchmark/results-realworld-post-fixes/README.md) | **Stale** | measured the original experimental branch; do not quote for the merged code |
| Repo and home-view surfaces (v1 and v2 protocols) | [`tools/benchmark_realworld/`](../tools/benchmark_realworld/README.md) (`results/`, `results-v2/`, `results-v2-rerun/`) | Historical | two model-based labelers, adjudicated; not human review |
| Sampled real-world repositories (326) | [`tools/benchmark/realworld/`](../tools/benchmark/realworld/README.md) (`results/`, `results-rerun/`, `results-merged/`) | Historical | deterministic oracle plus model adjudication; `results/freeze.json` records the hashes the scored run was checked against |
| Authored real-world shapes (130) | [`benchmarks/sab_realworld/results/`](../benchmarks/sab_realworld/results/REPORT.md) | Historical | ShadowScan only, corpus version 2.0.0; regression evidence; running the harness without `--output` rewrites the committed results |
| File-dialect holdout (17) | [`benchmarks/sab-holdout/`](../benchmarks/sab-holdout/README.md) | Regression corpus | evaluated by ShadowScan's own test suite; not a comparison with other tools |

## Unverified archive

| Archive | Status | What can be checked |
|---|---|---|
| [ShadowBench-450, 2026-10-18](../benchmarks/shadowbench-450/README.md) | Unverified archive | Arithmetic and document consistency only (`python -m tools.shadowbench450_archive`). No fixtures, labels, adapter source or per-case predictions were supplied, and the submitter states vendor binaries were not run. Rankings, grades and recommendations are withdrawn. Never compare it with any result above |

## Quoting a result

When you cite a number from this repository, cite with it:

1. the track, the run directory and the repository commit;
2. whether the number is in scope or estate-wide, and the coverage;
3. its interval, when the track reports one;
4. the run's status from the tables above and its disclosures;
5. that the corpus, labels and adapters were written by the maintainer of
   one of the tools under test.

A number quoted without these is not a ShadowBench result.
