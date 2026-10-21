# Supply chain and provenance of runs

How a ShadowBench run is tied to exactly what produced it: the sandbox the
tools ran in, the bytes of every installed tool, the published files, and the
machine paths taken out of them before publishing. Each mechanism names the
module whose docstring is normative.

**Contents**

- [Sandbox backends](#sandbox-backends)
- [Hash-locked tool installs](#hash-locked-tool-installs)
- [The tool image](#the-tool-image)
- [Signed results](#signed-results)
- [Scrubbing machine paths](#scrubbing-machine-paths)
- [The clean-room rescore](#the-clean-room-rescore)
- [What this does not establish](#what-this-does-not-establish)

## Sandbox backends

The cases runner ([`runner.py`](../tools/shadowbench/cases/runner.py),
[`stage.py`](../tools/shadowbench/cases/stage.py)) has two backends; the
manifest records which, with every limit, as `isolation`, and the report
states it.

| | `--sandbox namespaces` (default) | `--sandbox oci` |
|---|---|---|
| Namespaces | network, PID, mount, IPC, UTS, cgroup (`unshare`) | the container's own, under Docker |
| Kernel boundary | the host kernel | the host kernel; `--oci-runtime runsc` puts gVisor's user-space kernel in between |
| Tool identity | uid/gid 65534, no supplementary groups, `no_new_privs` | the same, inside the container |
| Capabilities | none for tools (dropped at the uid change) | container keeps only `SETUID`, `SETGID`, `KILL`, `DAC_READ_SEARCH` for the stage; tools get none; `no-new-privileges` |
| File system | host's, with `/root` and `/home` hidden and fresh `/var/tmp` and `/dev/shm` | the image's, read-only; fresh `/tmp`, `/var/tmp`, `/run`; only the run directory writable; tool trees and harness bound read-only |
| Host name | `shadowbench` | `shadowbench` |
| Resource limits | `RLIMIT_CORE` 0, `FSIZE` 4 GiB, `NOFILE` 4096, `NPROC` 4096 (`--rlimit` changes them; `as` and `cpu` available) | the same, plus `--oci-memory` (4g, no swap), `--oci-cpus` (2) and `--oci-pids` (1024) |
| Network | empty namespace, loopback mock services | `--network none`, loopback mock services |
| System calls | unrestricted | Docker's default seccomp profile (gVisor: its own) |

The OCI image must be pinned by digest and present locally; a run never
pulls. The runner refuses a rootless or user-namespace-remapped daemon, under
which uid 65534 in the container would not own the work tree, and a
contained stage refuses to skip its mounts unless its root file system is not
the runner's. A timed-out container is force-removed. Both backends were run
on the endpoint and runtime cases with Fleet `ai_tools` and reproduce the
2026-10-11 run's keys on every case.

## Hash-locked tool installs

[`install_tools.sh`](../tools/shadowbench/cases/install_tools.sh) installs the
cases track's third-party tools, all of them or the ones named
(`install_tools.sh ROOT agentdiscover numbat`).

- **PyPI tools** install exactly the distributions of
  [`locks/<venv>.txt`](../tools/shadowbench/cases/locks/), universal locks
  compiled with `uv pip compile --generate-hashes` from the one-line
  `locks/<venv>.in`, with `--require-hashes --no-deps`. Nothing resolves at
  install time, a distribution whose hash differs fails the install, and
  `uv pip check` fails an incomplete lock.
- **Go tools** build from pinned commits against their own `go.sum`. The
  Fleet wrapper builds against a committed
  [`go.mod` and `go.sum`](../tools/shadowbench/cases/locks/) in `-mod=readonly`
  mode; it used to run `go mod tidy` at install time, which resolved an
  unpinned indirect module at its latest version.
- **The record.** `TOOL_ROOT/resolved/` holds `uv pip freeze` per venv,
  `go version -m` per binary (every module and its `h1:` hash), the locks
  used, and `SHA256SUMS` of every binary and entry point. The runner copies
  it into each run's `resolved/` and records each file's SHA-256 as
  `tool_install` in the manifest.

The 2026-10-11 run predates the locks: its tools resolved their transitive
dependencies at install time and nothing recorded them. To refresh a lock,
change the `.in` file, recompile with the command in the lock's header, and
say in the pull request what moved.

## The tool image

[`images/Containerfile`](../tools/shadowbench/cases/images/Containerfile)
builds the tool tree from digest-pinned `python`, `golang` and `uv` images and
exports it:

```bash
docker buildx build -f tools/shadowbench/cases/images/Containerfile --target tools \
    --output type=local,dest=/opt/shadowbench/tools .
sudo python -m tools.shadowbench.cases run --tools /opt/shadowbench/tools/tools.json ... \
    --sandbox oci --oci-image python:3.13-slim-bookworm@sha256:<the Containerfile's PYTHON_IMAGE digest>
```

The tree's venvs point at the runtime image's interpreter and its
dynamically linked binaries at that image's C library, so it runs in the
container, not on the host. The build stage's Debian packages (`gcc`, `git`)
come from the archive at build time; they are build tools and not part of
the exported tree.

## Signed results

[`tools/attest.py`](../tools/attest.py) binds a published results directory
to its bytes, and the **Attest results** workflow
([`attest.yml`](../.github/workflows/attest.yml)) signs that binding with
Sigstore.

1. `python -m tools.attest digest <results dir>` writes
   `attestations/<slug>.json`: the SHA-256 of every file in the directory,
   canonical JSON, no time and no machine, so it can be re-made byte for
   byte.
2. The workflow, dispatched on `main` with the directory, signs that file
   with `cosign sign-blob` through its GitHub OIDC identity (`id-token: write`
   on that job only). The bundle `attestations/<slug>.sigstore.json` holds the
   signature, a Fulcio certificate naming the workflow, and the Rekor
   transparency-log entry. The workflow verifies it and uploads both files;
   the maintainer commits them.
3. `python -m tools.attest verify`, part of `make verify` and CI, fails when
   an attested directory gained, lost or changed a file, when a bundle does
   not verify for the `attest.yml` workflow on `main` of this repository
   issued by GitHub Actions' OIDC issuer, or when cosign is missing for a
   bundle that is present. `--require-signatures` also fails an unsigned
   attestation.

Anyone can check a signed run without trusting this repository's CI:

```bash
cosign verify-blob --bundle attestations/<slug>.sigstore.json \
    --certificate-identity-regexp '^https://github\.com/aisecnomad/Nexus-ShadowBench/\.github/workflows/attest\.yml@refs/heads/main$' \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com attestations/<slug>.json
python -m tools.attest verify
```

A signature says which workflow run, on which commit of `main`, saw these
bytes, and the transparency log says when. It does not say the run was
honest, independent or correct.

## Scrubbing machine paths

[`tools/shadowbench/scrub.py`](../tools/shadowbench/scrub.py) prepares a run's
records for publication ([submitting-results.md](submitting-results.md#what-never-to-commit)):

```bash
python -m tools.shadowbench.scrub apply --map /opt/nsb/tools=\<tools\> --map /opt/nsb/results/2026-11-02=\<run\> \
    --home --tmp <published files>
python -m tools.shadowbench.scrub check --identity <published files>
```

`apply` replaces each mapped path with its placeholder (`<corpus>`,
`<estate>`, `<home>`, `<host>`, `<repo>`, `<run>`, `<tmp>`, `<tools>`,
`<venvs>`, `<work>`) at path boundaries only, longest first, in its raw and
JSON-escaped forms, and changes nothing else. `check` reports home,
temporary and Windows profile paths left, and with `--identity` this
machine's host and user names; a path that occurs verbatim in a `--corpus`
(the estate's fictional `/home/dana`, echoed by tools) is the corpus's, not
the machine's. `make paths` and CI check every committed results directory
of the live tracks with their corpora.

## The clean-room rescore

The **Clean-room rescore** workflow
([`rescore.yml`](../.github/workflows/rescore.yml)) runs weekly and on
demand, on a fresh runner with nothing cached.

- **Verify and re-score:** `make install`, then `make verify` (migrated bytes,
  amendments, attestations), `make integrity` (the cases corpus rebuilt case
  for case, the estate validated against its freeze), `make rescore` (cases
  and estate 2026-10-11 metrics and reports, and the code-surface 2026-10-09
  metrics, byte for byte) and `make paths`.
- **Level-2 smoke run:** Fleet `ai_tools` and Microsoft `agent-discovery`
  installed from their locks and run in the sandbox on every endpoint and
  runtime case.
  [`smoke.py`](../tools/shadowbench/cases/smoke.py) fails the job on an
  `error` or `incomplete` row, a missing row, or a manifest without its
  isolation or install record, and reports, without failing, every case whose
  keys drift from the 2026-10-11 run. The records are then scrubbed and
  checked as for publication.

## What this does not establish

None of this makes the results independent. The corpora, labels, adapters,
locks, image and workflows were written by the maintainer of one of the
tools under test, and a signature from this repository's workflow is a
signature by that maintainer's automation. What it does provide is that a
third party can tell exactly which bytes ran, in what sandbox, and which
bytes were published, and can rerun all of it. The
[roadmap](../ROADMAP.md) lists what independence needs.
