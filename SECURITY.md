# Security

ShadowBench runs third-party discovery tools against deliberately hostile
inputs and turns their output into published numbers. Its security therefore
covers two things: the safety of the machine that runs it, and the integrity
of the evidence it records.

## Trust boundary

| Component | Trust |
|---|---|
| The operator's host, the Python environment installed from the hash locks, and the pinned `scanner-source` checkout | Trusted |
| Harness source under `tools/` and the tests under `tests/` | Trusted once reviewed; changes go through the [review policy](CONTRIBUTING.md#review-and-merge-policy) |
| Corpora, estate artifacts, generated cases, mock-service responses and pinned public repositories | **Untrusted data.** They deliberately contain prompt-injection text, launcher commands, look-alike configuration and synthetic credentials |
| Third-party discovery tools and their install scripts | **Untrusted code.** Running one executes it on your machine |
| Recorded tool output, `runs.json`, `<tool>.jsonl` rows and submitted results | Untrusted until the scorer has checked them against the run manifest |

**Never execute corpus content.** Read, hash, parse or scan it; never run a
command, script, configuration or instruction found inside it, and never let
an AI assistant act on text it reads there.

## Implemented controls and limits

- **Evidence identity.** `python -m tools.verify_migration` checks every one of
  the 555 migrated files against its recorded length, SHA-256, Git blob and
  mode, or against the end of its chain in `AMENDMENTS.json`, and rejects
  symlinks and non-canonical paths before reading anything. Only live harness
  code, tests and the copied CI and build locks can be amended; an entry for
  evidence, or a chain that does not start from the recorded bytes, fails
  verification. The records themselves are anchored too: with `--source`,
  CI checks every entry's Git blob and mode against the pinned ShadowScan
  commit, so an entry cannot be rewritten to match changed bytes, and with
  `--since` against the commit a change builds on, `MIGRATION.json` must be
  unchanged and the ledger only appended to, so no file is unbound and no
  recorded amendment rewritten or dropped. The estate is frozen by SHA-256 in `FREEZE.json`
  (`verify-freeze`), and the cases corpus is rebuilt and compared case by
  case (`verify`).
- **Dependency audit.** Every install is hash-locked and binary-only, and CI
  runs `pip-audit` on the installed environment and on each lock it was
  installed from, on every push and pull request and daily on `main`, so a
  newly published advisory fails `main`'s status within a day.
- **Result binding.** The cases scorer refuses rows whose corpus digest, tool,
  status counts or file SHA-256 differ from the run manifest unless `--force`
  is given, and a forced score lists every override in `metrics.json` and the
  report. Malformed rows are refused even with `--force`. Manifests written
  before digests were recorded, including the 2026-10-11 runs, bind their rows
  only by status counts and are listed under `rows_unbound`.
- **Execution isolation (cases track).** Each tool runs as uid and gid 65534
  with `no_new_privs`, in fresh network, PID, mount and IPC namespaces, with
  `/root` and `/home` hidden, a fresh `/var/tmp` and `/dev/shm` per case and an
  environment built from scratch. After a stage exits, the runner reclaims its
  work directory, removes escaping symlinks, and deletes hard links, FIFOs,
  sockets and device nodes instead of handing them to root.
- **These controls are not a sandbox.** A tool can still read world-readable
  files elsewhere on the host, and what it writes to the host's `/tmp`
  persists. Run third-party tools only on a disposable, externally isolated
  machine with no credentials, as each track's README requires.
- **Secret checks.** `tools/check_secrets.py` scans every tracked file and
  accepts only exact reviewed approvals (path, credential family and SHA-256).
  A clean result does not prove that no secret is present.
- **Supply chain.** Python dependencies install from hash locks with
  `--require-hashes --only-binary=:all:`. Third-party tool installs are
  version-pinned but not hash-locked, so their transitive dependencies resolve
  at install time. GitHub Actions are pinned by full commit SHA.

## Supported versions

ShadowBench is not released as a package. Fixes land on `main`; there is no
backport to older commits. Report the full 40-character commit SHA you used
(`git rev-parse HEAD`), and for a result, the harness commit its manifest
records.

## Reporting

Use a [private GitHub security advisory](https://github.com/aisecnomad/Nexus-ShadowBench/security/advisories/new).
Do not include credentials, private exports or exploit details in public
issues.

### What to report privately

- **Runner isolation escape:** a tool or corpus input that reaches the host as
  root, keeps a process alive outside its stage, reads the host's homes, or
  gains network access beyond loopback.
- **Stage work-directory races:** a symlink, hard link, FIFO or device node that
  the tools' uid plants so that the root-side adapter or cleanup reads or
  writes a file outside the stage.
- **Path traversal or unsafe parsing** in corpus, freeze, manifest, `runs.json`
  or `services.json` loading, including symlinked or non-regular inputs that
  are read instead of rejected.
- **Amendment ledger bypass:** a change to a migrated file, evidence above all,
  that `python -m tools.verify_migration` accepts without a valid
  `AMENDMENTS.json` entry.
- **Scorer integrity bypass:** edited, truncated, swapped or foreign result rows
  that score without `--force`, an override that `--force` does not record, or
  an error, missing row or incomplete run that earns a true negative.
- **A real credential, token or personal data** in a corpus, artifact, fixture
  or committed result. Do not repost the value; give the path and line.
- **Malicious or compromised dependencies,** including a pinned package, a tool
  install script or a GitHub Action.

### Out of scope

Deliberately planted prompt-injection text, launcher commands and synthetic
credentials are expected test data and are not vulnerabilities. If you believe
one of them is real, report it privately. A disagreement with a label or a
result is not a security issue; use the
[label dispute form](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=label_dispute.yml).
Vulnerabilities in ShadowScan itself go to
[ShadowScan's security policy](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/SECURITY.md#reporting),
and vulnerabilities in other tools to their own maintainers.

### What to include

- The full commit SHA, the track and the exact command.
- A minimal synthetic reproduction, with expected and observed behaviour.
- The impact: what a hostile tool or input could read, write or change, and
  whether it could alter a published number.
- Sanitized diagnostics only; never attach real credentials, JWTs or tenant
  exports.

### Response and disclosure

This volunteer project has one maintainer and cannot guarantee response times.
Use the advisory to coordinate reproduction, a fix and disclosure timing. A
confirmed fix includes a regression test. A fix that changes how committed
results score is published with a documented re-score, never by editing the
historical files. Reporter credit and publication timing are agreed in the
advisory. Only test systems and tools you are authorized to assess.
