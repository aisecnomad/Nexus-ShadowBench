# ShadowBench documentation

Start with the [README](../README.md): it gives the why, the what and the
how in one page. These documents go deeper. The track READMEs under
[`benchmarks/`](../benchmarks/README.md) are the detailed protocols and hold
each run's disclosures; they are preserved byte for byte from ShadowScan and
some of their links still point at paths in that repository.

## By question

| Question | Document |
|---|---|
| What exactly is measured, and how were the corpora built and labeled? | [methodology.md](methodology.md) |
| How is each number computed, and what happens to errors and incomplete scans? | [metrics.md](metrics.md) |
| How does the harness work, and what do its files contain? | [harness.md](harness.md) |
| How do I verify, reproduce and run the benchmark without contaminating it? | [running.md](running.md) |
| How do I add a discovery tool? | [adding-a-tool.md](adding-a-tool.md) |
| How do I publish a new run, or an independent corpus? | [submitting-results.md](submitting-results.md) |
| Which results exist, and which can I quote? | [results.md](results.md) |
| Which statements in preserved files are stale, and how should I read them? | [errata.md](errata.md) |
| What can go wrong, for the operator and for the validity of the numbers? | [threat-model.md](threat-model.md) |
| What is this benchmark for, and not for? | [benchmark-card.md](benchmark-card.md) |
| What is in the data, and where did it come from? | [datasheet.md](datasheet.md) |
| What does a term mean? | [glossary.md](glossary.md) |
| The hard questions | [faq.md](faq.md) |

## By role

| You are | Read, in order |
|---|---|
| Evaluating a discovery tool | README, [results.md](results.md), [benchmark-card.md](benchmark-card.md), [faq.md](faq.md) |
| Checking a published number | [running.md](running.md) (levels 0 and 1), [metrics.md](metrics.md), [results.md](results.md) |
| Benchmarking your own tool | [adding-a-tool.md](adding-a-tool.md), [running.md](running.md), [submitting-results.md](submitting-results.md) |
| Building an independent corpus | [methodology.md](methodology.md), [datasheet.md](datasheet.md), [submitting-results.md](submitting-results.md), [GOVERNANCE.md](../GOVERNANCE.md) |
| Reviewing security | [threat-model.md](threat-model.md), [harness.md](harness.md), [SECURITY.md](../SECURITY.md) |

## Project policies

[CONTRIBUTING.md](../CONTRIBUTING.md) · [GOVERNANCE.md](../GOVERNANCE.md) ·
[SECURITY.md](../SECURITY.md) · [SUPPORT.md](../SUPPORT.md) ·
[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) · [ROADMAP.md](../ROADMAP.md) ·
[CHANGELOG.md](../CHANGELOG.md) · [CITATION.cff](../CITATION.cff)

## Related documents in Nexus ShadowScan

- [What ShadowScan accepts as evidence](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/docs/evaluation.md)
- [Benchmarks in the product guide](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/docs/reference/product-guide.md#benchmarks)
- [The weekly code-surface regression workflow](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml)
- [AI-assisted review logs](https://github.com/aisecnomad/Nexus-ShadowScan/tree/main/archive/reviews) (not third-party reviews)
