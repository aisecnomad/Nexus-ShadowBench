# Submitting results

The protocol for publishing a new benchmark run in this repository, whether
it comes from the maintainers or from a third party. A run is accepted for
what it can show: committed, hashed, scorable rows with their provenance and
disclosures. A run is never accepted as a ranking, a grade or evidence of
field precision or recall.

**Contents**

- [Principles](#principles)
- [Where a run goes](#where-a-run-goes)
- [What to commit, per track](#what-to-commit-per-track)
- [What never to commit](#what-never-to-commit)
- [Required disclosures](#required-disclosures)
- [Independent submissions](#independent-submissions)
- [Submitting](#submitting)
- [Reviewer checklist](#reviewer-checklist)
- [Regression baselines](#regression-baselines)

## Principles

1. **Append, never rewrite.** Every run gets a new directory. Never
   overwrite, re-score in place, regenerate or "refresh" a committed result,
   corpus, label, freeze record or recorded prediction. Every imported file
   is bound by SHA-256 in [`MIGRATION.json`](../MIGRATION.json), results can
   never be amended, and `python -m tools.verify_migration` must pass before
   and after your change.
2. **Scorable by anyone.** Commit enough that the published `metrics.json`
   and `REPORT.md` can be regenerated from the committed rows, with no
   third-party tool installed.
3. **Bound to its inputs.** The run record names the corpus digest, the
   harness commit, and each tool's version; current runners write these
   for you.
4. **Disclosed.** Who wrote what, how the tools were isolated, which runs
   were incomplete, which overrides were forced, and whether the run is
   in-sample.

## Where a run goes

| Track | New run directory | Corpus it is scored against |
|---|---|---|
| Cases | `benchmarks/shadowbench/cases/results/<YYYY-MM-DD>/` | `benchmarks/shadowbench/cases/corpus.json`, or your own corpus committed beside it |
| Estate | `benchmarks/shadowbench/estate/results/<YYYY-MM-DD>/` | `benchmarks/shadowbench/estate/corpus.json` with `FREEZE.json` |
| Code-surface discovery | `benchmarks/shadow-ai-discovery/results/<YYYY-MM-DD>/` | `benchmarks/shadow-ai-discovery/corpus.json` |

Use the run's start date. If that directory already exists, add a suffix
(`2026-11-02-b`) rather than writing into it. A run on a corpus other than
the committed one (another seed, an independently authored estate, other
labels) must say so in its directory name and report, for example
`results/2026-11-02-seed-7/`, and commit that corpus in its own path.

The code-surface `results/` directory is where ShadowScan's weekly
regression gate finds its baseline, the directory its `BASELINE_RUN` names
(see [Regression baselines](#regression-baselines)). Other runs may go there
without becoming the baseline, but keep runs on other corpora out of it.

## What to commit, per track

**Cases track** (see [harness.md](harness.md)):

- `manifest.json` as the runner wrote it: `corpus` and `corpus_sha256`,
  `generator_digest`, `harness_commit` and `harness_dirty`, `platform`,
  `python`, `workers`, and per tool its `version`, row-status counts and
  `rows_sha256`;
- one `<tool>.jsonl` per tool, unedited (the scorer checks each file's
  SHA-256 against `rows_sha256`);
- `metrics.json` from `python -m tools.shadowbench.cases score`, and
  `REPORT.md` from `report`;
- the `tools.json` shape with paths replaced by placeholders, and the
  `resolved/` directory the runner copies from the tool root (freeze lists, Go
  build info, the locks used and SHA256SUMS), whose digests the manifest
  records as `tool_install`.

**Estate track:**

- `runs.json` as the runner wrote it: `harness_commit`, `harness_dirty`,
  `freeze` (`sha256`, `files`, `drift_after`), `policy`, `workers`,
  `tool_versions`, `tools_skipped` and `results` with normalized
  predictions, argv, exit codes, timings and statuses;
- `metrics.json` from `score` and `REPORT.md` from `report`;
- `tools.json` with placeholder paths.

A run whose `freeze.drift_after` is not empty, or that could only be scored
with `--allow-freeze-mismatch` or `--allow-missing-services`, can be
committed only with that stated at the top of its report and in the pull
request.

**Code-surface discovery:**

- `runs.json` with every tool's normalized facts and mapped evidence per
  repository, `metrics.json`, `REPORT.md` and `tools.json` with placeholder
  paths;
- for a regression baseline, the `compare.json` output.

This harness does not record a corpus digest or harness commit in
`runs.json`, so state both commits (this repository's and ShadowScan's, if
ShadowScan ran) in the run's README and the pull request.

## What never to commit

- **Raw tool output.** The cases runner keeps it under `<out>/raw/<tool>/`;
  the estate and discovery runners keep stdout, stderr and reports in each
  unit's output directory. None of it is committed; the committed runs hold
  normalized rows only. `raw/` is not in `.gitignore`, so copy the run's
  files into the results directory selectively instead of copying `<out>`.
- **Local paths and identities.** Replace machine paths with placeholders
  before publishing, as the committed runs did: `<tools>`, `<run>`,
  `<estate>`, `<repo>`, `<venvs>`, `<work>` (and `<corpus>`, `<home>`,
  `<tmp>`, `<host>`). The cases runner already writes its rows with the tool
  root, scratch, output and harness paths replaced, before it records their
  digest, so **never edit a `<tool>.jsonl`**: the scorer would refuse it.
  Scrub the other records (`manifest.json`, `tools.json`, `runs.json`, notes)
  with `python -m tools.shadowbench.scrub apply --map PATH=<token> ...
  [--home] [--tmp] [--host] FILE...`, which replaces a path only where one
  starts and ends and changes nothing else, then run
  `python -m tools.shadowbench.scrub check --identity` on every file you
  publish, rows included; CI (`make paths`) checks every committed results
  directory. Estate and code-surface rows carry no recorded digest; scrub
  them the same way and say so. Say in the pull request that you ran both.
  Never rewrite any other field
  ([supply-chain.md](supply-chain.md#scrubbing-machine-paths)).
- **Credentials or credential-shaped strings.** Run
  `make secrets` (`tools/check_secrets.py` and `tools/check_secrets_extra.py`)
  before committing. Rows can echo synthetic tokens from the corpus; such a value
  may be committed only with an exact-path, exact-digest approval and a stated
  reason: in `tools/secret_allowlist.json` for what `check_secrets.py`
  reports, and in `tools/secret_allowlist_extra.json` for what only
  `check_secrets_extra.py` reports (a family the first does not know, or a
  value inside a gzip member or UTF-16 or UTF-32 text).
- **Checkouts, estate copies or tool installations.**

## Required disclosures

Every new run ships a `README.md` in its own results directory. The track
READMEs are imported files bound by `MIGRATION.json`, so a run does not edit
them. The run's README covers:

| Disclosure | What to state |
|---|---|
| Independence | Who authored the corpus, the labels, the harness and each adapter, and each person's affiliation with any tool under test. Author-written runs say so in the first paragraph. |
| In-sample status | Whether any tool, ShadowScan included, was changed with this corpus's errors in view. A run of ShadowScan on the 2026-10-11 estate after the detection changes made with that run's errors in view is in-sample. |
| Corpus | Path, SHA-256, seed and stream scheme (cases), freeze digest (estate), commit (code checkouts). |
| Harness | This repository's commit, `harness_dirty`, and any uncommitted change. |
| Tools | Each tool's version or commit, how it was installed, and tools skipped with the reason. |
| Isolation | Runner, account (`--as-user` or uid 65534), network policy (`--keep-network` or not), and anything weaker than the documented isolation. |
| Run status | Errors, timeouts, missing rows and incomplete runs per tool, and any accepted non-zero exit that hid them. |
| Overrides | Every `--force`, `--allow-freeze-mismatch` or `--allow-missing-services`, and why. |
| Post-run changes | Any scorer, adapter or label change after the run, and whether the published numbers come from the original or the revised rules (re-applied to the unchanged rows). |

Model the disclosures on the estate README's
[Disclosures for the 2026-10-11 run](../benchmarks/shadowbench/estate/README.md#disclosures-for-the-2026-10-11-run)
and the cases README's
[Integration changes](../benchmarks/shadowbench/cases/README.md#integration-changes).

## Independent submissions

A rerun by someone without a stake in any tool under test is the evidence
these benchmarks are missing. To keep it distinguishable from author-written
runs:

- **Own corpus where possible.** Generate a cases corpus at your own seed
  with the default `sha256` stream scheme (and, ideally, your own families
  and labels); author your own estate and freeze it with
  `python -m tools.shadowbench.estate freeze --out <your FREEZE.json>`; or
  label your own repository set. Commit it under a path that names it, for
  example `benchmarks/shadowbench/cases/independent/<org>-<date>/corpus.json`,
  never over the committed corpus.
- **Freeze before running.** Commit (or publish the digest of) your corpus,
  labels and adapters before any tool runs on them, so the record shows they
  were fixed in advance.
- **Results beside the corpus.** Put the run in a results directory whose
  name says it is independent, and lead its README with the independence
  statement above.
- **No relabeling to fit.** If a tool's output exposes a label error, record
  it as an erratum with the evidence, keep the original labels and results,
  and score both readings.
- **Raw output retained by you.** Keep the raw output for audit even though
  it is not committed, and say how a reviewer can request it.

An independent submission that reproduces the committed numbers from the
committed rows is also useful: say which commands you ran and that the
outputs matched byte for byte.

## Submitting

1. Open an issue describing the run you plan (track, corpus, tools,
   isolation) before running it on a scored corpus.
2. Run, score and report into a new directory.
3. Run the repository checks: `python -m tools.verify_migration`,
   `python -m pytest -q`, `ruff check tests tools benchmarks`,
   `ruff format --check tests tools benchmarks` and the secret check above.
4. Open a pull request that lists the new files, the disclosures, the exact
   commands, and both commits. Follow [CONTRIBUTING.md](../CONTRIBUTING.md).

## Reviewer checklist

- [ ] Only new paths are added; `python -m tools.verify_migration` passes;
      no historical result, corpus, freeze or prediction changed.
- [ ] Re-running `score` and `report` on the committed rows reproduces the
      committed `metrics.json` and `REPORT.md`.
- [ ] The cases manifest names the scored corpus's SHA-256 and a
      `rows_sha256` for every tool (no `rows_unbound`), unless the report
      says otherwise; the estate run records a freeze with empty
      `drift_after`.
- [ ] `metrics.json` has no `forced` entries, or each is disclosed.
- [ ] Every tool version is recorded and reproducible; skipped tools carry
      their reason.
- [ ] Errors, missing rows and incomplete runs are counted and discussed,
      and none is presented as a clean negative.
- [ ] Local paths are placeholders (`make paths` passes); no raw output,
      checkout or credential is committed; the secret check passes.
- [ ] A cases manifest records its `isolation` and its `tool_install`
      record, and `resolved/` is committed beside the rows.
- [ ] After merge, the maintainer dispatches **Attest results** for the new
      directory and commits the signed attestation
      ([supply-chain.md](supply-chain.md#signed-results)).
- [ ] The independence and in-sample statements are present and accurate.
- [ ] No ranking, grade, recommendation or field-accuracy claim appears in
      the report or the pull request.

## Regression baselines

The weekly ShadowScan-only regression workflow lives in ShadowScan:
[`.github/workflows/benchmark.yml`](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml).
It runs the code-surface discovery benchmark with read-only permissions and
no third-party tools, compares against the committed run that its
`BASELINE_RUN` names in `benchmarks/shadow-ai-discovery/results/`
(currently `2026-10-09`), and uploads its outputs as an
artifact. Publishing a new baseline is a manual step: copy the scrubbed run
into a new `results/<date>/` directory here, with a `README.md` that
describes what changed since the previous baseline. The historical
[discovery README](../benchmarks/shadow-ai-discovery/README.md) asks for that
description in itself, but it is now a bound file, so the run's own README
carries it. A baseline produced after tuning on this corpus measures fit to
it, not field accuracy, and must say so.

The workflow initializes this repository as ShadowScan's `benchmark-suite`
submodule at the commit ShadowScan pins and reads `metrics.json` and
`runs.json` from `benchmarks/shadow-ai-discovery/results/<BASELINE_RUN>/`.
Until [aisecnomad/Nexus-ShadowScan#289](https://github.com/aisecnomad/Nexus-ShadowScan/pull/289)
it took whichever directory sorted last, so a later directory silently
became the baseline. Now:

- a later directory is reported with a `::notice::` and not used;
- a missing `metrics.json` or `runs.json` in the named directory fails the
  gate with an `::error::`;
- moving the baseline is a reviewed one-line change to `BASELINE_RUN` in
  ShadowScan that says why, together with the submodule pin.

Put code-surface runs that are not meant to be ShadowScan's regression
baseline (other corpora, independent runs, multi-tool comparisons that
should not gate) outside that directory, for example under
`benchmarks/shadow-ai-discovery/independent/<name>/`, and say in the pull
request whether a new directory there is intended to become the baseline.
