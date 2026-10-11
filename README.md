# ShadowBench

Open-source Shadow AI agent discovery benchmark. 450 labeled cases across 9 surfaces. Scores are fact-level precision, recall, and F1 on planted evidence. A tool that was not executed is `not_run`, not a zero.

| | |
|---|---|
| Cases | 450 (9 surfaces × 50) |
| Seed | `shadowbench-450-v1` |
| Corpus SHA-256 | `a874ddcf2c1bbb62746f9830798db1d3e96148ae26b71304f217bf4025392be3` |
| Provenance | synthetic-realistic |

Labels live in each case's `truth.json`. No scanner output was written back into the labels.

## Report

- [PDF](public/shadowbench-report.pdf)
- [HTML](public/shadowbench-report.html)

Direct download of the PDF from the default branch:

https://github.com/aisecnomad/ShadowBench-Grok-v1/raw/main/public/shadowbench-report.pdf

## In-scope fact F1

Primary score is fact F1 on surfaces the tool can actually read. Estate recall, which counts unscanned positives as false negatives, is in the report and is not the ranking key.

| Tool | Status | Fact F1 |
|---|---|---|
| reference-lexicon | ceiling, not a product | 0.868 |
| ShadowScan 0.1.2 | scored | 0.827 |
| NuGuard | scored | 0.745 |
| curatedmcp | scored | 0.545 |
| vet | scored | 0.440 |
| AgentDiscover | scored | 0.303 |
| ai-bom | scored | 0.230 |
| Numbat | scored | 0.000 |
| agentic-radar | scored | 0.000 |
| Snyk agent-scan | not run | — |
| AIOstack | not run | — |

`reference-lexicon` is a string-match ceiling. It is not ranked as a discovery tool.

## Reproduce

```bash
npm install
npm run dev
```

The dev server listens on port 8080. The scoreboard the UI reads is `src/data/scoreboard.json`.

Corpus and harness:

```bash
python3 benchmark/generate_corpus.py
python3 benchmark/run_benchmark.py
python3 benchmark/render_report.py
```

`generate_corpus.py` is deterministic for seed `shadowbench-450-v1`. Do not edit `truth.json` after a run.
