# Changelog

One entry per change to this companion. Imported evidence is never edited:
historical corpora, labels, freezes, recorded predictions and reports keep
the bytes recorded in [MIGRATION.json](MIGRATION.json), and their own
READMEs carry their errata. New runs, corpora and harness changes are
recorded here.

## Unreleased

Documentation and project standards, then harness hardening, provenance and
interoperability. No corpus, label, freeze, recorded prediction or result
changed, no published number moved, and no published run was rerun.

### Hardening, provenance and interoperability

- **Canonical keys.** `tools/shadowbench/keys.py` maps every spelling of one
  entity its platform treats as the same to one key (GUID case, `localhost`,
  URL forms of a service, `./`, `~/` and `\` in paths, ARN partition, service
  and region, Kubernetes kind spelling, fact-category case). The cases scorer
  takes `--keys canonical-v1` (default `exact`), refuses a scheme that merges
  truth keys, and records a non-default scheme as `key_scheme`. Scored under
  `canonical-v1`, the 2026-10-11 cases run gives identical metrics
  ([docs/key-canonicalization.md](docs/key-canonicalization.md)).
- **Framework mappings and AIBOM export.** `tools/shadowbench/frameworks.py`
  maps labels, surfaces and code-surface fact categories to the OWASP Top 10
  for Agentic Applications 2026, the OWASP Top 10 for LLM Applications 2025
  and MITRE ATLAS 2026.09; `tools/shadowbench/aibom.py` exports truth or a
  tool's rows as a deterministic CycloneDX 1.6 BOM
  ([docs/framework-mappings.md](docs/framework-mappings.md)).
- **Sandbox.** The cases stage also runs in fresh UTS and cgroup namespaces,
  sets the host name `shadowbench`, and lowers its resource limits (no core
  dumps, 4 GiB files, 4096 open files and processes; `--rlimit` overrides);
  the runner probes every namespace first. `--sandbox oci` runs the stage in a
  digest-pinned Docker container (read-only root, only the run directory
  writable, four capabilities for the stage and none for tools,
  `no-new-privileges`, seccomp, memory, CPU and pids limits), with gVisor
  through `--oci-runtime runsc`. The manifest records `isolation` and the
  report states it.
- **Hash-locked tool installs.** `install_tools.sh` installs PyPI tools from
  committed universal hash locks (`--require-hashes --no-deps`), builds the
  Fleet wrapper against a committed `go.mod` and `go.sum` instead of `go mod
  tidy`, takes an optional tool list, and records the resolved set in
  `resolved/`, which the runner copies into each run (`tool_install`). A
  Containerfile builds the tool tree from digest-pinned base images.
- **Signed results.** `tools/attest.py` binds a results directory to the
  SHA-256 of every file in it; the Attest results workflow signs that binding
  keylessly with Sigstore. `make verify` and CI fail on a changed attested
  directory or a bundle that does not verify.
- **Scrubbing.** `tools/shadowbench/scrub.py` replaces machine paths with the
  committed placeholders and checks records for home, temporary and profile
  paths; `make paths` (now part of `make check`) and CI check every committed
  results directory of the live tracks.
- **Clean-room rescore.** A weekly workflow installs from scratch, verifies,
  rebuilds the cases corpus, re-scores every published run (`make rescore`
  now includes the code-surface 2026-10-09 metrics) and runs two tools from
  their locks in the sandbox on every endpoint and runtime case, failing on
  harness problems and reporting drift from the 2026-10-11 run
  ([docs/supply-chain.md](docs/supply-chain.md)).
- **Roadmap.** Added the remaining recommendations of the 2026-10-21 review:
  a third-party-held test split, a contamination policy, inter-annotator
  agreement, neutral stewardship, a pre-registered run of record, power
  analysis, vendor-authored adapters, an adversarial split, cost and
  prevalence-adjusted metrics, versioned releases with DOIs, a results page
  and a right of reply.

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

### README

- Retitled the README "ShadowBench", replaced the SVG banner with a photo
  banner (`docs/assets/shadowbench-banner.jpg`, 1600 px), and cut the README
  from 595 to 171 lines; the detail it held is in `docs/`.

## e027b98: extraction from Nexus ShadowScan

Preserved 555 original files from Nexus ShadowScan commit
[`0792106b`](https://github.com/aisecnomad/Nexus-ShadowScan/tree/0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d)
with their source path, Git blob, mode and SHA-256 in `MIGRATION.json`.
Kept the runtime lock's aiohttp advisory update separate from the retained
original lock, and added strict migration verification and the companion
CI job. No benchmark result was regenerated.
