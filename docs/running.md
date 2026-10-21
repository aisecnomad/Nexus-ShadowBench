# Running ShadowBench accurately

The operator guide: how to set up, how to check the evidence, how to
reproduce the published numbers, how to run discovery tools against each
track without contaminating the result, and how to recognize and fix the
common failures. Each track's harness README is the complete reference for
its flags.

## Contents

- [Choose your level](#choose-your-level)
- [Set up the environment](#set-up-the-environment)
- [Level 0: verify the evidence](#level-0-verify-the-evidence)
- [Level 1: reproduce the published numbers](#level-1-reproduce-the-published-numbers)
- [Level 2: run discovery tools](#level-2-run-discovery-tools)
- [Level 3: measure without the in-sample problem](#level-3-measure-without-the-in-sample-problem)
- [Provenance to record](#provenance-to-record)
- [Accuracy rules](#accuracy-rules)
- [Troubleshooting](#troubleshooting)

## Choose your level

| Level | Goal | Runs third-party code | Time | Host |
|---|---|---|---|---|
| 0 | Confirm every byte is what the record says | no | about a minute | any Linux with Python 3.11 to 3.14 |
| 1 | Recompute committed metrics and reports from committed rows | no | minutes | same |
| 2 | Run discovery tools against a track and score them | **yes** | hours | disposable, externally isolated Linux host, no credentials |
| 3 | Measure on a corpus no tool was tuned against | yes | hours to days | same as level 2 |

Levels 0 and 1 are what a reviewer needs to check a published claim.

## Set up the environment

```bash
git clone https://github.com/aisecnomad/Nexus-ShadowBench.git
cd Nexus-ShadowBench
git clone --filter=blob:none --no-checkout https://github.com/aisecnomad/Nexus-ShadowScan.git scanner-source
git -C scanner-source checkout --detach 0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d
python -m venv .venv && . .venv/bin/activate
python -m pip install --require-hashes --only-binary=:all: \
    -r requirements.lock -r requirements-ci.lock -r requirements-build.lock
python -m pip install --no-deps --no-build-isolation -e ./scanner-source
```

`make install` does the same. The locks are hash-locked and binary-only:
`requirements.lock` is the runtime lock (it carries an aiohttp security
update), and `requirements-ci.lock` and `requirements-build.lock` add the
test and build tools. The original runtime lock is preserved at
`migration/requirements.source.lock` for provenance only; do not install it.

From a ShadowScan checkout, this repository is the `benchmark-suite`
submodule:

```bash
git submodule update --init --depth 1 -- benchmark-suite
python -m tools.benchmark_suite
cd benchmark-suite
```

Run the test suite once to confirm the environment (`make test`, or
`python -m pytest -q`). Some tests start loopback servers or synthetic
subprocesses and need a host that permits those local operations.

## Level 0: verify the evidence

```bash
python -m tools.verify_migration
python -m tools.shadowbench cases verify --corpus benchmarks/shadowbench/cases/corpus.json
python -m tools.shadowbench estate validate
python -m tools.shadowbench estate verify-freeze
python -m tools.shadowbench450_archive
```

`make verify integrity` runs the same checks. Expected results at the
current commit:

| Check | Expected output |
|---|---|
| `verify_migration` | `"files": 555`, source commit `0792106b…`, `"verification": "file identity only; no benchmark executed"` |
| `cases verify` | the stream scheme and the four modality pairs that share a stream under it; recorded and current generator digests (they differ); `regenerated cases are identical (per-surface 40)`; exit 0 |
| `estate validate` | 12 `WARN` lines for known anchor collisions, then `OK 137 entities (87 positive, 27 control, 23 near-miss), 12 anchor collision warnings`; exit 0 (`--strict` would fail on the warnings) |
| `estate verify-freeze` | `OK 139 files match the freeze manifest` |
| `shadowbench450_archive` | `"verification_status": "unverified"`, `"benchmark_executed": false`: arithmetic only |

None of these executes corpus content or any third-party tool.

## Level 1: reproduce the published numbers

Scoring reads only committed files.

```bash
out=$(mktemp -d)

# Cases track, 2026-10-11
python -m tools.shadowbench.cases score --corpus benchmarks/shadowbench/cases/corpus.json \
    --results benchmarks/shadowbench/cases/results/2026-10-11 --out "$out/cases-metrics.json"
python -m tools.shadowbench.cases report --corpus benchmarks/shadowbench/cases/corpus.json \
    --metrics "$out/cases-metrics.json" --out "$out/cases-REPORT.md"

# Estate track, 2026-10-11
python -m tools.shadowbench.estate score \
    --runs benchmarks/shadowbench/estate/results/2026-10-11/runs.json --out "$out/estate-metrics.json"
python -m tools.shadowbench.estate report --metrics "$out/estate-metrics.json" --out "$out/estate-REPORT.md"

# Code surface, 2026-10-09 (the regression baseline)
python -m tools.discovery_benchmark score --corpus benchmarks/shadow-ai-discovery/corpus.json \
    --runs benchmarks/shadow-ai-discovery/results/2026-10-09/runs.json --out "$out/code-metrics.json"
python -m tools.discovery_benchmark report --corpus benchmarks/shadow-ai-discovery/corpus.json \
    --metrics "$out/code-metrics.json" --out "$out/code-REPORT.md"
```

Then compare each output with the committed file using `cmp`. `make rescore`
does this for the cases and estate runs. At the current commit:

| File | Reproduces |
|---|---|
| cases `metrics.json`, `REPORT.md` | byte for byte |
| estate `metrics.json`, `REPORT.md` | byte for byte |
| code-surface 2026-10-09 `metrics.json` | byte for byte |
| code-surface 2026-10-09 `REPORT.md` | all but four cells: the current renderer prints `no facts (incomplete)` where the committed report says `clean (incomplete)` for four incomplete ShadowScan negatives |

The committed cases manifest predates `rows_sha256`, so the scorer lists
every tool under `rows_unbound`: those rows are bound to the run only by
their status counts. That is disclosed at the top of the report. The
code-surface 2026-10-08 metrics were scored against the labels as first
published (835 expected facts) and do not reproduce against the current
corpus (839): re-scoring its committed `runs.json` now moves ShadowScan's
in-scope value counts from 724 / 23 / 122 to 726 / 21 / 124 (TP / FP / FN),
with F1 at 90.9% either way. The 92.3% in the
[code-surface README](../benchmarks/shadow-ai-discovery/README.md) also
re-normalized the rows with the fixed adapters.

## Level 2: run discovery tools

### Prepare the host

1. Use a **disposable** Linux VM or bare-metal host that holds no
   credentials, cloud configuration, SSH keys, browser profiles or other
   sensitive files. Every tool you run executes its own code there.
2. Allow egress only while installing. Run the benchmark with egress
   disabled at the host or network level; the harness's dead-proxy
   variables do not stop direct connections.
3. For the cases track: run as root (the runner uses `unshare` for
   namespaces), install `gcc` (the runner builds the inert process binary),
   and place the repository copy, the scratch directory and every tool path
   outside `/root`, `/home`, `/var/tmp` and `/dev/shm`, where uid 65534 can
   reach them. The runner refuses to start otherwise.
4. For the estate and code-surface tracks: create an unprivileged account
   for `--as-user` and give it traverse access to the checkouts and tool
   installations. Make the code-surface checkouts read-only.

### Cases track

```bash
git clone . /opt/nsb/ShadowBench && cd /opt/nsb/ShadowBench   # a clean copy outside /root and /home
python -m tools.shadowbench.cases verify --corpus benchmarks/shadowbench/cases/corpus.json
bash tools/shadowbench/cases/install_tools.sh /opt/nsb/tools   # review it first; writes /opt/nsb/tools/tools.json
# add to "tools" in /opt/nsb/tools/tools.json:
#   "shadowscan": {"bin": "<python with the locked environment>", "repo": "<ShadowScan checkout to measure>"}
python -m tools.shadowbench.cases.fetch_code /opt/nsb/checkouts
sudo python -m tools.shadowbench.cases run --corpus benchmarks/shadowbench/cases/corpus.json \
    --tools /opt/nsb/tools/tools.json --checkouts /opt/nsb/checkouts \
    --out /opt/nsb/results/<date> --workers 3
python -m tools.shadowbench.cases score --corpus benchmarks/shadowbench/cases/corpus.json \
    --results /opt/nsb/results/<date> --out /opt/nsb/results/<date>/metrics.json
python -m tools.shadowbench.cases report --corpus benchmarks/shadowbench/cases/corpus.json \
    --metrics /opt/nsb/results/<date>/metrics.json --out /opt/nsb/results/<date>/REPORT.md
```

`run` accepts `--only a,b`, `--surfaces x,y`, `--cases id,...` and
`--scratch`; a run of some surfaces writes `unsupported` rows for the rest.
`fetch_code` uses hardened `git` calls (HTTPS only, hooks and filter
drivers off, pins checked before and after checkout), and the runner
refuses a checkout whose HEAD differs from the pin or whose `git status`
is not clean.

### Estate track

```bash
python -m tools.shadowbench.estate validate
python -m tools.shadowbench.estate verify-freeze
python -m tools.shadowbench.estate run --tools /srv/estate/tools.json \
    --out /srv/estate/runs --workers 4 --as-user bench
python -m tools.shadowbench.estate score --runs /srv/estate/runs/runs.json --out metrics.json
python -m tools.shadowbench.estate report --metrics metrics.json --out REPORT.md
```

`tools.json` maps tool ids to binaries:
`{"extra_path": "...", "tools": {"<id>": {"bin": "..."}}}`; AI-Infra-Guard
also needs its `fps` and `vul` data directories and takes an optional
`port_offset`. The committed
[`results/2026-10-11/tools.json`](../benchmarks/shadowbench/estate/results/2026-10-11/tools.json)
shows the shape with placeholder paths. `run` also takes `--timeout`
(seconds per command, default 900), `--keep-network` and `--only`. It
refuses to run when the estate differs from `FREEZE.json`, and runs each
unit in its own verified copy of the estate.

### Code-surface track

```bash
python -m tools.discovery_benchmark fetch --corpus benchmarks/shadow-ai-discovery/corpus.json --dest /srv/sadb/corpus
python -m tools.discovery_benchmark fetch --corpus benchmarks/shadow-ai-discovery/corpus.json --dest /srv/sadb/corpus --verify
python -m tools.discovery_benchmark run --corpus benchmarks/shadow-ai-discovery/corpus.json \
    --tools /srv/sadb/tools.json --checkouts /srv/sadb/corpus --out /srv/sadb/runs/full \
    --as-user bench --workers 4
python -m tools.discovery_benchmark score --corpus benchmarks/shadow-ai-discovery/corpus.json \
    --runs /srv/sadb/runs/full/runs.json --out metrics.json
python -m tools.discovery_benchmark report --corpus benchmarks/shadow-ai-discovery/corpus.json \
    --metrics metrics.json --out REPORT.md
python -m tools.discovery_benchmark compare --corpus benchmarks/shadow-ai-discovery/corpus.json \
    --baseline benchmarks/shadow-ai-discovery/results/2026-10-09/metrics.json \
    --baseline-runs benchmarks/shadow-ai-discovery/results/2026-10-09/runs.json \
    --current metrics.json --tools shadowscan
```

`compare` exits 1 when a tool's in-scope value F1 falls by more than one
point (`--f1-tolerance`), when repository-level recall falls at all, when a
negative the baseline left clean is flagged, or when a run complete in the
baseline is incomplete now. ShadowScan's weekly
[`benchmark.yml`](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml)
workflow runs this gate for ShadowScan alone.

## Level 3: measure without the in-sample problem

ShadowScan's rules were changed after the 2026-10-11 runs with their errors
in view, and after the 2026-10-08 code-surface run with that corpus in
view. A ShadowScan run on those corpora now measures fit to them. Three
ways out, in increasing order of value:

1. **Fresh cases at a new seed.**
   `python -m tools.shadowbench.cases generate --seed <seed> --per-surface 40 --output fresh.json`,
   then `verify --corpus fresh.json` must print stream scheme `sha256` and
   no shared streams. This changes the draws, not the rubrics, so it tests
   overfitting to particular cases, not to the author's view of evidence.
   Use a larger `--per-surface` for narrower intervals, and several seeds to
   see the variance the committed results cannot show.
2. **New labels on new repositories.** Pick repositories at new commits,
   label them with the evidence rules before running any tool, and score
   with the code-surface harness.
3. **An independently authored estate or corpus.** Authored by someone who
   has not seen any tool's errors on the committed corpora. This is the
   control the benchmark most needs; see
   [submitting-results.md](submitting-results.md).

## Provenance to record

Record all of these next to any result you publish:

- This repository's commit, and whether the working tree was clean.
- The ShadowScan commit you measured (`git -C <checkout> rev-parse HEAD`)
  and the scanner source commit used for tests.
- The corpus file's SHA-256 (the cases manifest records it), and for the
  estate the `FREEZE.json` digest (the runner records it).
- Every tool's version or commit (`tools.json`, the manifest's
  `tool_versions`), plus `uv pip freeze` for each tool venv and the Fleet
  wrapper's `go.sum`: tool installs are version-pinned, not hash-locked.
- The host: kernel, distribution, CPU count, worker count and timeouts.
- Which isolation you used, and anything you changed in the harness.

## Accuracy rules

1. Write every run to a new dated directory. Never overwrite a committed
   result, and never refresh a freeze to hide drift.
2. Never publish a score produced with `--force`, `--allow-freeze-mismatch`
   or `--allow-missing-services` as a run of record.
3. Never generate a new corpus with `--stream-scheme legacy`.
4. Calibrate adapters on a smoke corpus at another seed
   (`generate --seed 1 --per-surface 4 --output smoke.json`), never on the
   scored corpus, and commit adapters before the scored run.
5. Run each tool at its defaults. Give no tool an allowlist, an inventory
   or a known-agent list, and impose no threshold of your own.
6. Keep raw tool output on the run host (`raw/` in the cases output) so the
   mapping can be audited and re-applied.
7. Disclose in-sample status, isolation, incomplete and error counts,
   withheld decoys and who authored the corpus, labels and adapters.
8. Do not run the legacy `tools/benchmark` and `tools/benchmark_realworld`
   installers, freeze helpers or self-checks from this repository; run them
   in the pinned `scanner-source` checkout, where the shared-root layout
   they assume still exists.
9. Treat everything under `benchmarks/` as untrusted data. Never execute it,
   and never give an AI coding agent tool permissions over it.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `verify_migration` raises `migrated bytes or mode changed` | an imported file was edited, renormalized or lost its mode | restore it from git; check that no editor or hook rewrote line endings (`.gitattributes` marks these paths `-text`); a deliberate change to live harness code needs `--amend` (see [adding-a-tool.md](adding-a-tool.md)) |
| `verify_migration` raises `amended bytes or mode changed since the last amendment` | an amended harness file changed again without a new ledger entry | record it with `python -m tools.verify_migration --amend PATH --reason ... --reference ...` |
| `verify_migration` raises `never amendable` | `AMENDMENTS.json` names evidence or the code that generates or labels it | remove the entry; publish a correction in a new path instead |
| Cases `score` refuses the results | the manifest's corpus hash, tool list, row counts or `rows_sha256` do not match the files | score the corpus the run used; never mix files from two runs in one directory |
| Cases `run` refuses to start | scratch directory or tool paths unreachable by uid 65534, wrong permissions, or `gcc` missing | move them outside `/root`, `/home`, `/var/tmp` and `/dev/shm`; let the runner create the scratch directory (mode 0711); install `gcc` |
| Estate `run` prints `DRIFT` and exits 1 | an estate file or `corpus.json` differs from `FREEZE.json` | restore the frozen bytes; a deliberate change needs a new estate version, not a refreshed freeze |
| Estate command exits 2 with `corpus error` | a symlink or special file in the estate, a malformed manifest or services file, or a malformed run record | fix the input; these are refused by design |
| Estate `score` exits 2 naming runs that need services | `services/services.json` is missing or empty for a `sim` run or recorded scan targets | restore the file; `--allow-missing-services` only for diagnostics |
| A tool's row is `error` with nothing obviously wrong | timeout, unexpected exit code, or output the adapter could not parse | read `raw/<tool>/` on the run host; raise `--timeout` only if the tool was still working |
| Many `incomplete` ShadowScan rows | the scanner reported incomplete coverage (exit 3) | record and disclose it; incomplete rows earn no true negatives |
| A test fails on loopback or subprocess setup | the host forbids local servers or process creation | run tests on a host that permits them |
