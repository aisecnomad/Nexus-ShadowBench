# Changelog

One entry per change to this companion. Imported evidence is never edited:
historical corpora, labels, freezes, recorded predictions and reports keep
the bytes recorded in [MIGRATION.json](MIGRATION.json), and their own
READMEs carry their errata. New runs, corpora and harness changes are
recorded here.

## Unreleased

### Parser property tests and local coverage

- Add Hypothesis properties for canonical migration paths and strict JSON
  parsing, available through `make fuzz` and the normal test suite.
- Reject JSON numeric overflow such as `1e999` in provenance inputs, including
  nested values; previously only the `NaN` and `Infinity` spellings were
  rejected. Finite float decoding remains supported.
- Add opt-in branch coverage reports through `make coverage`; coverage is a
  local diagnostic, with no published percentage or minimum gate yet.
- Add an independence invitation and a checklist for branch protection and
  OpenSSF Best Practices preparation. Existing governance, evidence rules,
  historical changelog entries and lint exceptions remain intact.

Documentation and project standards, then harness hardening, provenance and
interoperability. No corpus, label, freeze, recorded prediction or result
changed, no published number moved, and no published run was rerun.

### Hardening, provenance and interoperability

- **Historical signing bootstrap.** A protected merge changing `attest.yml`
  now triggers the existing main-only signing job for the three fixed
  historical result directories. It checks committed bindings before signing,
  preserves existing bundles, and requires all signatures to verify before
  uploading the artifact. Manual dispatch still selects one requested directory.
  This adds a way to produce real workflow artifacts; it does not itself
  supply signature bundles or claim historical signing is complete.
- **Historical signing preparation.** Add reproducible digest manifests for
  the three preserved result sets and a signing checkpoint. Strict attestation
  verification now rejects missing historical manifests, even with an empty
  attestation directory, and refuses attestation symlinks and unreadable
  inputs. Signature bundles and CI enforcement remain pending real signing
  and verification; no historical result or metric changed.
- **Dependency audit hygiene.** Refresh active CI/build lock pins for
  filelock, virtualenv and setuptools with registry-verified hashes and
  recorded amendments. Align `make audit` with CI's installer-toolchain
  locks. Historical tool locks and evidence remain unchanged.
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
  rebuilds the cases corpus, re-scores the cases and estate 2026-10-11 runs
  and the code-surface 2026-10-09 metrics (`make rescore` now includes the
  latter; older historical results are not re-scored) and runs two tools from
  their locks in the sandbox on every endpoint and runtime case, failing on
  harness problems and reporting drift from the 2026-10-11 run
  ([docs/supply-chain.md](docs/supply-chain.md)).
- **Fixes from an adversarial review of this change** (41 findings, each
  reproduced and upheld by independent verifiers): `canonical-v1` strips a
  home prefix once, keeps a climb out of a relative path, never raises on
  long pids and is idempotent on adversarial paths; a reported `artifact:`
  path with `..` is inside no truth directory, and a key reported more than
  once is labeled `agent` when any report is, in both schemes (no committed
  row is affected); limits are set by `prlimit` in each tool's process, not
  the stage, and the limits that held are recorded; `/etc/hostname` and
  `/etc/hosts` are masked; OCI tool binds keep their configured paths; the
  installer creates venvs afresh, builds sdists with hash-locked setuptools,
  is `CDPATH`-safe, and Go adapters skip a missing binary; the runner refuses
  tools whose binaries changed since install, empties `resolved/` before
  copying, refuses impossible `--rlimit` values and writes rows with
  placeholders before their digest; the scrubber bounds both ends of a path,
  sees paths after JSON escapes and under `/var/home` or WSL profiles, exempts
  only whole corpus paths, keeps line endings, refuses missing inputs and
  gains `--host`; the AIBOM export refuses rows the manifest does not vouch
  for and malformed rows, splits rows on newlines only, maps the `ai` label,
  applies fact categories on the code surface only, places by canonical
  namespace and derives its serial number from the whole document; the smoke
  check fails on an expected tool that did not run; and the docs no longer
  overstate what is re-scored, hash-locked or verified (erratum E6).
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

### The answer key out of the tools' reach

A tool under test could read what it is scored against. Under
`--sandbox namespaces` a checkout outside `/root` and `/home`, the results
directory and a corpus kept elsewhere were world-readable; `--sandbox oci`
bound the whole `tools/` package, whose generator rebuilds every label of the
committed corpus; and every tool saw its case id, in its run directory's name
and in `case.json`. A discovery tool scanning the file system could also pick
up the benchmark's own fixtures. No committed metric changes.

- The stage runs from `<scratch>/harness`, a root-only copy of the six
  modules it imports (`runner.STAGE_MODULES`; a test holds the set to what the
  stage actually loads), under both backends; the container binds that, not
  `tools/`.
- Under `--sandbox namespaces` the stage covers the checkout and `--out` with
  an empty tmpfs and `--corpus` with an empty read-only file before anything
  from the case runs; the runner refuses a scratch directory or tool path that
  lies under one of them. The manifest's `isolation` names what was hidden,
  not where.
- A configured ShadowScan checkout is the repository this benchmark was
  migrated from, so it too holds the corpus, generator and results (and it is
  on ShadowScan's own `PYTHONPATH`): the namespaced stage hides every entry of
  it but its `shadowscan/` package and the paths `tools.json` names (a virtual
  environment, say), and `--sandbox oci` binds only the package.
- Version probes, which run tool code outside the stage, hide the same paths
  (each tested inside the probe's namespace, so one under `/home` or inside an
  earlier one is skipped rather than failing the probe), and a root probe hands
  the runner only the first 64 KiB of each stream, through a 2 MiB tmpfs, where
  `capture_output` kept everything the binary printed.
- The runner checks a tool path against what is hidden by its configured
  spelling as well as what it resolves to: a venv's `python` resolves out of a
  hidden checkout while the stage still runs it at its configured path.
- Run directories are `run-XXXX`, and `case.json` keeps the surface and
  modality but not the case id.
- The stage's private `/var/tmp` and `/dev/shm` are capped at 256 MiB each (a
  tmpfs defaults to half the host's memory), as the OCI backend caps its
  `/var/tmp`.
- The threat model keeps one residual: the corpus is public, so a tool could
  ship answers keyed by its inputs' content.

### Sandbox and scorer review fixes

No committed metric or report changes: the cases and estate 2026-10-11 runs
and the code-surface 2026-10-09 metrics still re-score byte for byte, and
`canonical-v1` still scores the cases run identically.

- **Session keyring.** A uid change keeps the session keyring, and a process
  possessing it can read its keys, so tools dropped to 65534 could read the
  keys of the session the runner was started in. The runner (before any
  probe) and the stage (before anything from the case) join a new, empty
  anonymous session keyring.
- **Host sockets.** The stage also covers `/run` and `/tmp/.X11-unix`: a
  UNIX socket on a path is reachable from any network namespace, so the
  D-Bus system bus (systemd-resolved resolves names over it), nscd or an X
  server bridged the empty network namespace.
- **Reclaimed files** lose group and other write, as the estate runner's do,
  so a 0666 report stays no longer writable to the tools' uid.
- **Mock services** answer a malformed, negative or over-1 MiB
  `Content-Length` with 400 or 413 instead of raising (a traceback on the
  root stage's stderr per request, which the runner holds in memory),
  blocking a thread or allocating the declared size.
- **`install_tools.sh`** sets `umask 022`, clears the operator's `GOFLAGS`,
  `GOSUMDB`, `GONOSUMDB`, `GONOSUMCHECK`, `GOPRIVATE`, `GONOPROXY` and
  `GOINSECURE` and ignores the go env file, resets and cleans a reused
  checkout to exactly its pin (checkout kept local edits and untracked
  files), and copies AI-Infra-Guard's data afresh.
- **Cases scorer.** A case listing a decoy, tolerated or expected key twice
  is refused (a reported repeated decoy still earned a true negative); a
  row's `seconds` must be a finite, non-negative number; the McNemar test
  divides by an integer, since `2.0**n` overflowed from 1024 discordant
  cases on.
- **Code-surface scorer.** A second run of a tool on one repository is
  refused (the last row won, so an appended row could replace a failed
  scan), and `seconds` is validated; both exit 2 with `runs error:`.
- **AIBOM export** refuses unsupported rows mixed with scored ones on a
  surface and modality, as the scorer does (the check is now shared,
  `score.mixed_support`), refuses a key that is not valid Unicode, and
  writes `--out` atomically, so a refused export leaves it as it was.
- **`canonical-v1`** no longer folds an `artifact:` path that happens to be
  a GUID: paths keep their case.
- **Errata** [E7 and E8](docs/errata.md) record two code-surface scoring
  rules that flatter the committed 2026-10-09 numbers: repository-level
  detection counts ShadowScan's 4 incomplete negatives as unflagged, and 11
  surplus `<category>:generic` facts are credited as true positives (recall
  0.9482 instead of 0.9476). The threat model now lists the answer key's
  reachability from inside the cases sandbox as a residual risk.

### Secret checks beside `check_secrets.py`

`tools/check_secrets.py` is bound in `MIGRATION.json` and not amendable, and
it missed whole families and encodings, so `tools/check_secrets_extra.py`
runs beside it in CI, `make secrets` and pre-commit:

- families it does not know: Anthropic OAuth (`sk-ant-oat01-`), OpenRouter
  (`sk-or-v1-`, which the OpenAI rule does not reach), Groq, xAI, Replicate
  and Perplexity keys, PyPI, npm and Docker tokens, Slack app tokens and
  webhook URLs, Google OAuth client secrets and access tokens, SendGrid keys;
- every family in what it cannot read: it decodes all bytes as UTF-8 and drops
  the rest, so a token in a gzip member, or in UTF-16 or UTF-32 text, with or
  without a BOM, passed unseen. Each gzip layer is inflated and each tar
  member read (at most 8 deep and 256 MiB in all; a corrupt, truncated, deeper
  or larger one is reported, not skipped; zlib itself raises nothing for a
  truncated member), and each is read as UTF-8 and, when it holds a NUL, as
  UTF-16 and UTF-32 at every alignment (wide text beside non-ASCII characters
  such as CJK punctuation) and with the NULs removed (archive padding, wide
  text beside ASCII). One token matched in several views is reported once, a
  match `check_secrets.py` already reports is not reported twice, and a
  private-key approval must bind the whole file, as there.

Reports, exit codes and approvals (`tools/secret_allowlist_extra.json`, by
path, family and SHA-256, stale entries failing closed) follow
`check_secrets.py`. Nothing tracked matched, including the two committed
`.jsonl.gz` result files, so the allowlist starts empty.

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
- Updated virtualenv from 21.14.8 to 21.14.9 in `requirements-ci.lock` for
  GHSA-c978-59m8-c77v, which that audit caught on `main`. The two releases
  declare the same dependencies, and both hashes were checked against PyPI.
- Updated uv, the cases track's tool installer, from 0.9.5 to 0.13.4 in
  `tools/shadowbench/cases/locks/uv.txt` (recompiled with the command in its
  header; its 19 hashes are every artifact PyPI publishes for 0.13.4) and in
  the tool image's digest-pinned `UV_IMAGE`. 0.9.5 is affected by
  GHSA-pjjw-68hj-v9mw and GHSA-4gg8-gxpx-9rph (a wheel's RECORD entries or
  entry-point names written outside the install prefix, by a process that
  runs as root here), GHSA-pqhf-p39g-3x64 (ZIP parsing differentials) and
  GHSA-hq85-5cpj-mr62 (an untrusted root in the vendored TLS bundle). CI now
  audits `locks/uv.txt` and `locks/build.txt` with the repository's own
  locks.

### Bounded reads of tool output

A hostile tool could exhaust memory as root in two places. Cases-track
adapters read the files a tool wrote, whose size the tool controls up to the
stage's 4 GiB file-size limit, whole with `read_text` and `json.loads` in the
runner; and the stage held everything a tool printed (`communicate`) before
keeping the last 2,000,000 characters. No committed metric changes.

- `adapters/_report.read_text` reads at most `MAX_REPORT_BYTES` (8 MiB;
  `json.loads` of 8 MiB of empty objects or lists peaks near 220 MiB, the worst
  shape) in 1 MiB chunks, not
  one allocation of the whole cap, and raises `ReportTooLarge`, an `OSError`
  every adapter already turns into an `error` result. Under the limit it
  returns exactly what `read_text` did. AgentDiscover, AI-Infra-Guard,
  ShadowScan and vet use it; ShadowScan's code surface, which hands
  `report.json` to the code-surface adapter, refuses a longer one first; and
  AgentDiscover parses each client configuration once per file however many
  reported servers send its lookup there. The adapter rules in
  `adapters/__init__.py` and [adding-a-tool.md](docs/adding-a-tool.md) require
  it ([erratum E9](docs/errata.md) for the cases README).
- The stage reads each invocation's stdout and stderr on threads and keeps only
  their tails (a 300 MB flood now peaks under 150 MiB, against 902 MiB), with
  the same deadline: the tool must exit and its pipes close within its timeout.

### Errata

- Added `docs/errata.md` for stale statements in byte-bound files: the four
  `clean (incomplete)` cells of the code-surface 2026-10-09 report, the
  estate README's pointer to an October 14 changelog entry that now lives in
  ShadowScan's engineering log, the "newest baseline" wording superseded by
  Nexus-ShadowScan#289, the cases reproduce block's single-repository
  layout, and relative links to files that stayed in ShadowScan. The
  companion docs that described the old baseline selection now describe
  `BASELINE_RUN`.

### Continuous integration

- **Companion tests** also runs daily on `main` and on demand, so an
  advisory published after a merge fails `main`'s status within a day
  rather than on the next pull request, and a newer push to a pull request
  cancels its superseded run.
- A `tests on Python 3.14` job installs the same binary-only locks on the
  newest supported CPython and runs the harness tests; the required `tests`
  job keeps gating on 3.11 under its existing name.
- CodeQL also analyses the workflows (`actions`), which hold the OIDC
  identity that signs results.
- `tests/test_repository_policy.py` checks that every workflow checkout of
  ShadowScan uses the Makefile's `SCANNER_COMMIT`.
- **Named runner image.** Every job runs on `ubuntu-24.04` instead of
  `ubuntu-latest`, which GitHub began moving to Ubuntu 26 on 2026-10-19,
  under the byte-for-byte re-scores and the sandbox. Moving the image is now
  a reviewed change, and the policy tests reject a `-latest` label.
- **Security lint that applies.** `pyproject.toml` selected bandit (`S`)
  but turned it off for `tests/**`, `tools/**` and `benchmarks/**`, which
  hold every Python file here, so it checked nothing. It now applies to the
  live harness, which runs as root and parses what tools write. Its
  by-design exceptions are scoped per file with their reasons: starting
  fixed programs without a shell, the sandbox's fixed mount points, and the
  seeded bootstrap. Frozen files stay exempt, since a finding there could
  never be fixed. The one finding, Git's SHA-1 blob id in
  `tools/verify_migration.py`, now says `usedforsecurity=False`. Stale
  references to ShadowScan's files in its comments are corrected.
- The policy tests also check that `make audit` audits exactly the locks
  CI audits, that every `noqa` for a broad `except` or a bandit rule
  carries its reason (as `pyproject.toml` has always said), and that no
  workflow script expands any `${{ }}` expression, where they previously
  caught only `github.event.*`, `github.head_ref` and `inputs.*`. A branch
  name (`github.ref_name`) or a step output can carry shell syntax too.
  `actions/github-script` scripts are checked as well.
- `python -m tools.verify_migration --amend` takes several paths and
  verifies the tree once all are recorded. Amending one at a time failed
  whenever a change edited two bound files, such as both locks or an
  adapter and its test, because each saw the other as unrecorded. A
  refused file records none of the others.

### Anchoring the provenance records

The default checks took `MIGRATION.json`, the ledger and the attestation
files as given, so an edit to evidence that also rewrote its record, a
rewritten ledger entry or a deleted Sigstore bundle all verified.

- `python -m tools.verify_migration --source DIR` checks every record's Git
  blob and mode against the pinned source commit in the ShadowScan checkout
  at DIR (all 555 match); `--since REF` requires `MIGRATION.json` to be
  byte-identical to REF's and REF's ledger to be a prefix of today's. A
  migrated file that went missing is now reported as such, and leaves the
  ledger untouched when `--amend` fails.
- `python -m tools.attest verify --since REF` fails when a manifest or bundle
  committed at REF is gone or changed. Subjects must be spelled canonically
  (`benchmarks/x/./r` and `benchmarks//x/r` named one directory under three
  slugs).
- CI passes `--source scanner-source` and, on pull requests and pushes to
  `main`, `--since` the commit the change builds on; `make verify` does the
  same with a scanner checkout present and `SINCE=<commit>`.
- `scrub` finds and replaces paths inside `file://` URIs (SARIF writes every
  location so) and reads `.sarif` and upper-case suffixes in a directory.
- `tests/test_repository_policy.py` also refuses `pull_request_target` and
  `workflow_run` triggers, blanket `permissions` strings, a workflow-level or
  unexpected `id-token: write`, unpinned reusable workflows, and
  `${{ github.event.* }}`, `${{ github.head_ref }}` or `${{ inputs.* }}`
  expanded inside a `run:` script.

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
