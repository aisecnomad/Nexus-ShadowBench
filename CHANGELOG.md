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

## e027b98: extraction from Nexus ShadowScan

Preserved 555 original files from Nexus ShadowScan commit
[`0792106b`](https://github.com/aisecnomad/Nexus-ShadowScan/tree/0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d)
with their source path, Git blob, mode and SHA-256 in `MIGRATION.json`.
Kept the runtime lock's aiohttp advisory update separate from the retained
original lock, and added strict migration verification and the companion
CI job. No benchmark result was regenerated.
