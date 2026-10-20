# Support

ShadowBench is a volunteer-maintained benchmark companion to
[Nexus ShadowScan](https://github.com/aisecnomad/Nexus-ShadowScan). Support is
best effort; there is no guaranteed response time or service-level agreement.
A green test run or a reproduced metric does not establish that any tool is
accurate in your environment.

## Choose the right route

| Need | Route |
|---|---|
| How a track works, what a metric means, how to run it | The [README](README.md), the [docs](docs/) and each track's README under [`benchmarks/`](benchmarks/README.md) |
| Question about running or interpreting a result | [Question form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=question.yml) |
| Harness, scorer or report bug | [Bug report form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=bug_report.yml) |
| A label you believe is wrong | [Label dispute form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=label_dispute.yml) |
| A tool you want benchmarked | [Tool adapter request](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=tool_adapter_request.yml) |
| A run or results you want to submit | [Result submission form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=result_submission.yml) |
| A new corpus, case family or estate | [Corpus proposal form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=corpus_proposal.yml) |
| Isolation escape, scorer bypass, or a real credential in a corpus | [Security policy](SECURITY.md#reporting); keep details private |
| ShadowScan detection behaviour outside the benchmark | [ShadowScan support](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/SUPPORT.md) |
| Participation or conduct concern | [Code of conduct](CODE_OF_CONDUCT.md#reporting-a-concern) |
| Contribute a fix, adapter, corpus or review | [Contributor guide](CONTRIBUTING.md) |

Search [existing issues](https://github.com/aisecnomad/Nexus-ShadowBench/issues)
first and add new evidence to an existing report instead of opening a
duplicate.

## Troubleshoot before reporting

1. Record the commit (`git rev-parse HEAD`), the Python version, the operating
   system and the track.
2. Run `python -m tools.verify_migration`. A failure means a migrated file
   changed in your checkout; restore it before investigating anything else.
3. For the cases track, run `python -m tools.shadowbench cases verify --corpus
   benchmarks/shadowbench/cases/corpus.json`; for the estate track,
   `python -m tools.shadowbench estate validate` and
   `python -m tools.shadowbench estate verify-freeze`.
4. Check that the scanner is the pinned checkout
   (`git -C scanner-source rev-parse HEAD` prints
   `0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d`) and that the dependencies came
   from the hash locks.
5. For a run of third-party tools, confirm each tool is at the version the
   track's README lists and that the host allows the namespaces, loopback
   servers and subprocesses the runner needs.
6. Read the scorer's refusal message before reaching for `--force`. A refusal
   usually means the rows and the manifest disagree, which is the scorer doing
   its job.

## What makes a useful report

- The revision and environment from step 1, and the exact command.
- Expected and observed behaviour, the exit code and the relevant output.
- For a scoring question, the case or entity id and the row involved.
- For a label dispute, an evidence pointer into the pinned artifact or
  repository commit.

Never attach real tenant exports, credentials, JWTs, private source trees or
environment dumps. Corpus artifacts may contain synthetic credentials and
prompt-injection text by design; quote them only as far as needed.

## Supported revisions and triage

Fixes land on `main`; older commits are not patched. Historical results are
never edited; corrections are published as errata or new runs. Maintainers
prioritize evidence integrity and security first, then reproducible harness
bugs, then new adapters and corpora. A request for more evidence is not a
promise of a fix or a date.
