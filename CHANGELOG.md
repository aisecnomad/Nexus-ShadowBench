# Changelog

One entry per change to this companion. Imported evidence is never edited:
historical corpora, labels, freezes, recorded predictions and reports keep
the bytes recorded in [MIGRATION.json](MIGRATION.json), and their own
READMEs carry their errata. New runs, corpora and harness changes are
recorded here.

## Unreleased

Documentation and project standards. No corpus, label, freeze, recorded
prediction, result or harness behaviour changed, and no benchmark was rerun.

- Rewrote the README around the case for an open standard (why), the
  methodology and metrics (what) and the harness and how to run it
  accurately (how), with the results of record and their caveats.
- Added `docs/`: methodology, metrics, harness, running, adding a tool,
  submitting results, results index, threat model, benchmark card,
  datasheet, glossary and FAQ.
- Added community and governance files: contributing guide, code of
  conduct, security policy, support, governance with a benchmark integrity
  and conflict-of-interest policy, maintainers, roadmap and code owners.
- Added issue forms (harness bug, label dispute, tool adapter request,
  result submission, corpus proposal, question), a pull request template,
  Dependabot for GitHub Actions, OpenSSF Scorecard and CodeQL workflows,
  `.editorconfig`, a pre-commit configuration and a `Makefile`.
- Added `.github/labels.yml` and a Labels workflow that creates or updates
  those labels on `main`, and `tests/test_repository_policy.py`, which fails
  when an issue form or Dependabot applies a label the file does not define,
  or when a workflow leaves an action unpinned, omits token permissions or
  persists checkout credentials.
- Added `tests/test_docs.py`, which checks that the companion's own
  Markdown links and anchors resolve and that `CITATION.cff` is well formed.
- Recorded what re-scoring shows at this commit: the cases and estate
  2026-10-11 metrics and reports, and the code-surface 2026-10-09 metrics,
  reproduce byte for byte; the code-surface 2026-10-09 report differs in
  four cells because the current renderer no longer calls an incomplete
  negative clean ([docs/results.md](docs/results.md)).

### Harness amendments

- Added `AMENDMENTS.json`, an append-only ledger for changes to migrated
  harness code and tests, and taught `tools/verify_migration.py` to accept a
  migrated file only at its migrated bytes or at the end of its recorded
  chain. Evidence (corpora, labels, freezes, results), the cases generator,
  case model and families, the ground-truth labeler, the taxonomies and the
  legacy `tools/benchmark` and `tools/benchmark_realworld` harnesses are not
  amendable. `python -m tools.verify_migration --amend PATH --reason TEXT
  --reference URL` records an entry; its output gains an `amended` count.
- First amendment: the code-surface `fetch` now delegates to the cases
  track's hardened `fetch_pinned` and `checkout_problem` (https only, no
  operator git configuration, hooks, submodules or filter drivers, `GIT_*`
  dropped, pin checked before checkout, and a checkout reused only when it
  holds exactly the pinned tree). Checkouts made by the earlier fetcher
  should be fetched again. `tests/unit/test_discovery_fetch.py` covers it.

### Dependency security

- Updated certifi from 2026.7.22 to 2026.10.19 in `requirements.lock` and
  `requirements-ci.lock` for GHSA-6q48-6c7w-9gw2, with the same pins and
  hashes as Nexus-ShadowScan#290 and both hashes checked against PyPI. The
  ledger now also covers the copied `requirements-ci.lock` and
  `requirements-build.lock`, so they can follow ShadowScan's security
  updates; `migration/requirements.source.lock` stays as the original
  record.
- CI and `make audit` (now part of `make check`) run `pip-audit` on the
  installed environment and on each hash-locked set, so a new advisory
  fails the next run instead of going unnoticed.

### Errata

- Added `docs/errata.md` for stale statements in byte-bound files: the four
  `clean (incomplete)` cells of the code-surface 2026-10-09 report, the
  estate README's pointer to an October 14 changelog entry that now lives in
  ShadowScan's engineering log, the "newest baseline" wording superseded by
  Nexus-ShadowScan#289, the cases reproduce block's single-repository
  layout, and relative links to files that stayed in ShadowScan. The
  companion docs that described the old baseline selection now describe
  `BASELINE_RUN`.

## e027b98: extraction from Nexus ShadowScan

Preserved 555 original files from Nexus ShadowScan commit
[`0792106b`](https://github.com/aisecnomad/Nexus-ShadowScan/tree/0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d)
with their source path, Git blob, mode and SHA-256 in `MIGRATION.json`.
Kept the runtime lock's aiohttp advisory update separate from the retained
original lock, and added strict migration verification and the companion
CI job. No benchmark result was regenerated.
