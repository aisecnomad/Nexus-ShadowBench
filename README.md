# Nexus ShadowBench

Benchmark corpora, harnesses, tests and historical results for
[Nexus ShadowScan](https://github.com/aisecnomad/Nexus-ShadowScan).
The [benchmark index](benchmarks/README.md) describes each track and its limits.
These are author-written or author-labeled offline benchmarks, not independent
review or measured field accuracy. The ShadowBench-450 archive remains explicitly
unverified.

This repository imports the original paths and bytes from ShadowScan commit
[`0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d`](https://github.com/aisecnomad/Nexus-ShadowScan/tree/0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d).
[MIGRATION.json](MIGRATION.json) records every imported file's original path,
Git blob, mode, byte length and SHA-256. No corpus, label, freeze record, recorded
prediction or report was regenerated during migration. Historical links and
commands in those files are retained as source evidence; some refer to paths in
the original shared repository.

## Verify and test

The main repository pins this companion as the optional `benchmark-suite`
submodule. From a ShadowScan checkout:

```bash
git submodule update --init --depth 1 -- benchmark-suite
python -m tools.benchmark_suite
cd benchmark-suite
python -m tools.verify_migration
python -m pytest -q
```

Install ShadowScan's hash-locked development environment first. The required
companion CI job runs these harness tests against the candidate ShadowScan
checkout; it does not download or execute the benchmark corpora or third-party
tools. The companion keeps the existing hermetic test fixtures. Some tests
start loopback servers or synthetic subprocesses and require a host that permits
those local operations.

For a standalone reproduction, use the exact source revision above and the
CI and build locks retained here, with the active runtime lock carrying the
aiohttp security update. The original runtime lock is preserved at
`migration/requirements.source.lock` for provenance, not recommended installation:

```bash
git clone --filter=blob:none --no-checkout https://github.com/aisecnomad/Nexus-ShadowScan.git scanner-source
git -C scanner-source checkout --detach 0792106b8d2cc09517f7f4ee2eeabf4f8eb8da2d
python -m pip install --require-hashes --only-binary=:all: -r requirements.lock -r requirements-ci.lock -r requirements-build.lock
python -m pip install --no-deps --no-build-isolation -e ./scanner-source
python -m tools.verify_migration
python -m pytest -q
```

Record both repository commits, the installed scanner version and the locks for
any new run. The source revision is the migration input, not a claim that the
historical results were produced by that revision: each run retains its original
tool and source provenance.

## Historical source and freeze semantics

The older `tools/benchmark` and `tools/benchmark_realworld` installers, freeze
helpers and self-checks assume the scanner and harness share one repository
root. Reproduce those commands in the pinned `scanner-source` checkout, where
that layout still exists. **Do not run those legacy helpers from this companion
and interpret its commit or an empty scanner-tree hash as a scanner revision.**
Their source bytes remain unchanged to preserve recorded hashes.

The ShadowBench and discovery scoring/reporting entry points retain their
relative layout and can read the recorded data here. Their existing protocols
remain authoritative. A newly generated result must use a new output directory;
never overwrite the imported historical results or refresh a historical freeze
to hide drift.

## Trust and licensing

Corpus files are untrusted data. They deliberately include prompt-injection
text, launcher commands and simulated credentials. Read, hash or scan them;
never execute their contents. Running third-party discovery tools is separate
from checking these bytes and requires the isolation described in each protocol.

The original [Apache-2.0 license](LICENSE), [notice](NOTICE), tool pins and
upstream provenance are retained. Migration and green tests do not establish
independent human review or the absence of secrets.
