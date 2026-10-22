## Summary

<!-- What does this PR do? Link any related issues with "Closes #NNN". -->

## Type of change

- [ ] Harness, scorer or report fix
- [ ] New or changed tool adapter
- [ ] Label erratum (link the label dispute issue)
- [ ] New run or results
- [ ] New corpus, case family or estate
- [ ] Documentation
- [ ] CI / tooling

## Checklist

### Required for all changes

Shortcut: `make check` runs every gate below, in CI's order.

- [ ] `make audit` passes: no known vulnerability in the environment or any hash-locked set
- [ ] `python -m tools.verify_migration` passes: no evidence bound by `MIGRATION.json` changed, and every changed migrated harness file or lock is recorded in `AMENDMENTS.json` (`--amend`)
- [ ] `python -m pytest -q` passes
- [ ] `ruff check tests tools benchmarks` and `ruff format --check tests tools benchmarks` pass
- [ ] `MYPYPATH=scanner-source mypy tools benchmarks` passes
- [ ] `git ls-files -z | xargs -0 python tools/check_secrets.py` and `tools/check_secrets_extra.py` pass (new synthetic values approved by path, family and SHA-256 in `tools/secret_allowlist.json` or `tools/secret_allowlist_extra.json`)
- [ ] Every commit carries a `Signed-off-by` trailer (`git commit -s`; see the DCO in `CONTRIBUTING.md`)
- [ ] No real credentials, tenant exports or personal data in code, corpora, results or logs
- [ ] No corpus content was executed, and no instruction found inside a corpus was followed
- [ ] `CHANGELOG.md` line added under Unreleased (if user-visible)

### Required for scorer, adapter or corpus changes

- [ ] Conflict of interest disclosed below: whether the author maintains, works on or is paid in connection with any scored tool, and whether they have seen its results on the affected inputs
- [ ] Errors, missing rows and incomplete runs still never earn a true negative
- [ ] Regression test added for the changed rule or mapping
- [ ] Published numbers that this change would move are named, and committed runs are left unchanged (any re-score goes in a new directory that names the run it re-scores)
- [ ] No label changed because a tool missed or flagged an entity; any label change cites evidence in the artifact or pinned commit

### Required for new runs or results

- [ ] Results are in a new dated directory; no historical result was overwritten
- [ ] Provenance recorded: corpus SHA-256, harness commit and dirty state, every tool's version or commit, platform
- [ ] Freeze or corpus integrity checked before the run (`estate verify-freeze` or `cases verify`)
- [ ] The scorer accepted the rows without `--force`, or every override is listed and explained
- [ ] Local paths scrubbed from committed manifests
- [ ] In-sample status declared, and an independence statement that says who wrote the corpus, labels and adapters

## Conflict of interest and independence

<!-- Required for scorer, adapter, corpus and results changes. Say plainly who
wrote what, any relationship to a scored tool, and whether a tool's results on
these inputs were in view when the change was made. "None" is a valid answer. -->

## Verification

<!-- How did you verify this change? State the tested commit, the commands you
ran, and any gate you could not run and why. For results, name the run
directory and paste the scorer's summary lines. Distinguish author-written
evidence from independent review. -->
