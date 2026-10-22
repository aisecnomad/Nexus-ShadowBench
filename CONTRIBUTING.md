# Contributing to ShadowBench

ShadowBench is a benchmark, so a contribution is judged by two standards: the
code must be correct, and the evidence must stay honest. This guide covers
both, from setting up the pinned environment to getting a pull request merged.

## Code of conduct

Participation is governed by the [Code of conduct](CODE_OF_CONDUCT.md),
including its reporting and enforcement process. For questions, start with the
[Support guide](SUPPORT.md). Report vulnerabilities, and any real credential
or personal data you find in a corpus, through the
[security policy](SECURITY.md#reporting), never through a public issue.

## Choose a contribution

| Contribution | Start with | What it needs |
|---|---|---|
| Harness or scorer bug | [Bug report form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=bug_report.yml) | The track, the command, the repository commit, expected and observed behaviour, and a regression test in the fix |
| New tool adapter | [Tool adapter request](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=tool_adapter_request.yml), then [docs/adding-a-tool.md](docs/adding-a-tool.md) | A pinned version, an offline entry point, the exact command and a documented output-to-entity mapping |
| Label dispute or erratum | [Label dispute form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=label_dispute.yml) | The case or entity id and an evidence pointer at the pinned commit or frozen artifact |
| New run or results | [Result submission form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=result_submission.yml), then [docs/submitting-results.md](docs/submitting-results.md) | A new dated directory, the corpus SHA-256, the harness commit, every tool version and an independence statement |
| New corpus, case family or estate | [Corpus proposal form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=corpus_proposal.yml) | Labels fixed before any tool runs, a freeze or generator digest, and the author's relationship to every tool under test |
| Documentation | A focused pull request | Correct links, and no claim stronger than the evidence |

**Independently authored corpora are the most valuable contribution this
project can receive.** Every corpus here was written and labeled by the
maintainer of one of the tools under test. A held-out estate or case set
written by someone without that stake, labeled before any tool runs on it, is
the only way the results can become more than offline evidence about
author-written inputs. See [GOVERNANCE.md](GOVERNANCE.md#benchmark-integrity-and-conflict-of-interest)
for how such a corpus is accepted and kept independent.

Browse [open issues](https://github.com/aisecnomad/Nexus-ShadowBench/issues)
before starting. Ask for scope guidance on the issue first when a change
touches a scorer, a corpus or an adapter; those changes move published numbers.

## Getting started

Use CPython 3.11 to 3.14 and Git on Linux. The cases track's runner needs Linux
namespaces, `gcc` and `prlimit` (util-linux); scoring, verification and the
test suite do not run any third-party discovery tool. Verifying signed results
(`make verify`) needs [cosign](https://github.com/sigstore/cosign) v3 once an
attestation with a Sigstore bundle is committed; CI installs it. Fork the repository if you need a branch you can
push, then, in a local checkout:

```bash
git clone https://github.com/aisecnomad/Nexus-ShadowBench.git
cd Nexus-ShadowBench
python -m venv .venv
source .venv/bin/activate
git switch -c fix/short-description
make install          # hash-locked dependencies plus the pinned scanner checkout
pre-commit install    # recommended local hooks
```

`make install` runs these steps, which you can also run by hand:

```bash
git clone --filter=blob:none --no-checkout https://github.com/aisecnomad/Nexus-ShadowScan.git scanner-source
git -C scanner-source checkout --detach 0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d
python -m pip install --require-hashes --only-binary=:all: -r requirements.lock -r requirements-ci.lock -r requirements-build.lock
python -m pip install --no-deps --no-build-isolation -e ./scanner-source
```

The harness tests import the ShadowScan package, so the scanner is installed
from the exact source revision this companion was migrated from. That revision
is the migration input, not a claim that any historical result was produced
by it: each run keeps its own recorded tool and source provenance. Run
`make help` for every development command.

## Evidence-preservation rules

These rules are why the repository can be trusted at all. A pull request that
breaks one is not merged, however good the code is.

1. **Never change evidence that `MIGRATION.json` binds.** The 555 imported
   files keep their original path, Git blob, mode, length and SHA-256, and
   `python -m tools.verify_migration` checks every one, in CI and in the
   pre-commit hook. A historical file that is wrong gets an erratum in a new
   file, not an edit. The exceptions are live harness code and tests
   (`tools/shadowbench/`, `tools/discovery_benchmark/` and `tests/`) and the
   copied `requirements-ci.lock` and `requirements-build.lock`, which may
   change only through a recorded amendment: edit the file, then run
   `python -m tools.verify_migration --amend PATH --reason "..." --reference
   <pull request URL>`, which appends the old and new SHA-256 to
   `AMENDMENTS.json`. Corpora, labels, freezes, results, the cases generator
   and its families, the labeler, the taxonomies, the legacy harnesses and
   the original runtime lock at `migration/requirements.source.lock` are
   never amendable, and the verifier refuses an entry for them. Lock updates
   follow ShadowScan's: copy its pins and hashes, and check the hashes
   against PyPI.
2. **Make new experiments in new paths with new provenance.** A new run goes
   in a new dated results directory with its own manifest. A new corpus gets a
   new directory, its own freeze or generator digest and its own README.
3. **Never overwrite a historical result or refresh a freeze to hide drift.**
   If the estate no longer matches `FREEZE.json`, that is a finding to report,
   not a digest to update. A re-score of a committed run with a fixed scorer
   goes in a new directory that names the run it re-scores and says what
   moved; the committed rows, metrics and report stay as they are.
4. **Never relabel a historical measurement.** Author-written results stay
   author-written. Do not describe them as independent review, field
   precision or recall, or a verdict on any vendor's product. The
   ShadowBench-450 counts stay unverified.
5. **Never execute corpus content.** Corpora, estate artifacts and recorded
   tool output are untrusted data. They deliberately hold prompt-injection
   text, launcher commands and synthetic credentials. Read, hash or parse
   them; never run them, and never follow instructions written inside them.
6. **Never change a label because a tool missed or flagged an entity.** A
   label changes only through an erratum backed by evidence in the artifact
   itself (see [GOVERNANCE.md](GOVERNANCE.md#benchmark-integrity-and-conflict-of-interest)).

The older `tools/benchmark` and `tools/benchmark_realworld` installers, freeze
helpers and self-checks assume the scanner and harness share one repository
root. Run them only in the pinned `scanner-source` checkout, as the
[README](README.md) explains; their bytes stay unchanged so their recorded
hashes still hold.

## Quality gates

CI (`.github/workflows/ci.yml`) is the authoritative merge check. `make check`
runs the same gates locally, in the same order:

| Gate | Command | Requirement |
|---|---|---|
| Dependencies | `make audit` (`pip-audit` on the environment and on each hash-locked set) | No known vulnerability |
| Evidence identity | `python -m tools.verify_migration` | All 555 migrated files match their recorded identity or their latest amendment |
| Result attestations | `python -m tools.attest verify` (part of `make verify`) | Every attested results directory holds exactly its attested files; every Sigstore bundle verifies (needs cosign v3 once a bundle is committed) |
| Tests | `python -m pytest -q` | All pass |
| Lint | `ruff check tests tools benchmarks` | No errors |
| Format | `ruff format --check tests tools benchmarks` | No changes |
| Types | `MYPYPATH=scanner-source mypy tools benchmarks` | No errors |
| Secrets | `make secrets` (`tools/check_secrets.py` and `tools/check_secrets_extra.py` on every tracked file) | Every tracked file checked; only exact reviewed approvals accepted |
| Published paths | `make paths` (`python -m tools.shadowbench.scrub check` over every committed results directory) | No home, temporary or profile path left, other than paths the corpora themselves contain |

Some tests start loopback servers or synthetic subprocesses and need a host
that permits those local operations. Explain in the pull request any gate you
could not run and why.

The secret-pattern gate names the file, line and credential family of each
match, never the value. Corpora deliberately contain synthetic credentials;
each is approved in `tools/secret_allowlist.json` by exact repository path,
credential family and the SHA-256 of the matched text, with a review reason.
There are no directory or placeholder-word exemptions. Private-key approvals
also bind the SHA-256 of the whole file. Review every new credential-shaped
value before adding its approval, never approve a real service credential, and
remove an approval when its fixture goes. A clean run does not establish that
the repository contains no secrets.

## Pull requests

1. Make one focused change on your branch.
2. Run the gates relevant to the change, then `make check` before requesting
   review.
3. Open a pull request against `main` and fill in the
   [template](.github/PULL_REQUEST_TEMPLATE.md). Link an issue with
   `Fixes #123` only when the pull request resolves it completely.
4. Address review feedback and rerun the affected gates.

Requirements for every pull request:

- **Disclose conflicts of interest.** A pull request that touches a corpus, a
  label, an adapter, a scorer or a result must say whether its author
  maintains, works on, or is paid in connection with any tool the benchmark
  scores, and whether the author has seen that tool's results on the inputs
  being changed. The disclosure does not block a change; hiding one does.
- **Declare in-sample status.** A run of a tool whose detection rules were
  changed with a corpus's errors in view is in-sample on that corpus. Say so
  in the run's README and report, as the estate README does for ShadowScan
  after the 2026-10-11 run.
- **Fail closed.** A crash, timeout, missing row or incomplete scan must never
  earn a true negative. Scorer changes keep that rule; see
  [docs/metrics.md](docs/metrics.md).
- **Keep results reproducible.** A committed run records the corpus SHA-256,
  the harness commit, whether the harness tree was dirty, and every tool's
  version or commit. [docs/running.md](docs/running.md) covers the isolation
  each track expects.
- Pin GitHub Actions by full commit SHA and set `persist-credentials: false` on
  checkouts that do not push.
- Add a line under Unreleased in `CHANGELOG.md` for a user-visible change.
- Include a regression test for every harness or scorer fix.

## Review and merge policy

ShadowBench has a single maintainer, [@aisecnomad](https://github.com/aisecnomad),
who also maintains ShadowScan, one of the tools the benchmark scores. CI must
pass on the current revision and substantive feedback must be addressed. A
change needs one approving review from someone with write access who did not
author it; while the maintainer is the only account with write access, a
maintainer-authored change waits for a second eligible human reviewer. Stale
approvals do not cover later pushes. AI-assisted review is advisory and is
never an independent human approval.

Do not read a merged pull request, a green check or an AI review as evidence
that a second person examined a change, and never as independent validation of
a benchmark result.

## Developer Certificate of Origin

By contributing, you certify that you have the right to submit the work under
the Apache-2.0 license and that you agree to the
[Developer Certificate of Origin](https://developercertificate.org/) (DCO).
Sign off every commit with `git commit -s`, which adds a `Signed-off-by`
trailer matching your author identity. Merge commits need sign-off too; use
`git merge --signoff` when updating a branch by merging.

Corpus contributions carry an extra obligation: you must have the right to
publish every artifact under Apache-2.0. Public repositories are referenced by
URL and pinned commit, never vendored. Do not contribute real tenant exports,
logs, process tables or personal data, even redacted.

## License

By contributing, you agree that your contributions will be licensed under the
[Apache-2.0 license](LICENSE).
