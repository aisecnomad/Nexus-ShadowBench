# Historical results attestation checkpoint

Status on 2026-10-24: **three digest manifests and three genuine Sigstore
bundles verified**. Strict verification is required by `make verify`, the
required CI tests job, an independent historical-attestations job, and the
repository regression test. The historical results and manifest bytes are
unchanged. The bundles were generated after bootstrap PR #21 merged; this
checkpoint and enforcement are delivered by follow-up PR #20.

The manifests were generated with `python -m tools.attest digest` at reviewed
source commit `f875ccbf06cebadb9c267788fe58b2f3f3b69239`. Each of the 20
listed file digests was also checked against the bytes returned by
`git show <commit>:<path>`, rather than trusting only the working tree.

The initial unsigned checkpoint was recorded before the signing run below.
Its preparation checks established file identity only. The verification
record here uses actual downloaded bundles and cosign v3.1.4, with no custom
trust root or insecure verification flags.

| Preserved result directory | Files | Manifest SHA-256 |
|---|---:|---|
| `benchmarks/shadowbench/cases/results/2026-10-11` | 12 | `0b94e4b9f7cfbff5f0030be5ee463198da7543dbbc06c2a99791e246bf97f61d` |
| `benchmarks/shadowbench/estate/results/2026-10-11` | 4 | `95f0d4bbd69280baf39fd116e7c83de1e6ce42a33f46d0f8756440ded135d959` |
| `benchmarks/shadow-ai-discovery/results/2026-10-09` | 4 | `f27c5653422500ccbb5791733535f71e11a906e7e0832c7a41931c39954c088b` |

## Verified signing evidence

The successful [Attest results run](https://github.com/aisecnomad/Nexus-ShadowBench/actions/runs/40128040686)
is run **40128040686**, attempt **1**, event **push**, ref
`refs/heads/main`, source commit
`c1fd03bf4cd4e3a46a40a39804a5c5939f50f954`. GitHub's run metadata reports
`.github/workflows/attest.yml` and conclusion `success`. The run started
at 2026-10-24 20:03:01 UTC and completed at 20:03:33 UTC.

Its `attestation` artifact is **12573639685**, with archive SHA-256
`1f778c283919f206dcca21d321b79ec304b6e8c454e8f11bff7b504c437154b4`.
The downloaded archive matched that digest and contained exactly the three
manifests and their three bundles. Every manifest matched the committed bytes
in the table above before its bundle was imported.

| Bundle subject | Bundle SHA-256 | Rekor log index | Integrated time (UTC) |
|---|---|---|---|
| Cases 2026-10-11 | `a9eda343eb1dd12d19d3356734a3ca6544ca9986f605ca290cddf2fcc8799619` | `3442639241` | 2026-10-24 20:03:13 |
| Estate 2026-10-11 | `5f07929fbf546b00ed3c3657f1e0c321a8cd6d7b8e29746c32bc6c114977f413` | `3442642291` | 2026-10-24 20:03:20 |
| Code-surface 2026-10-09 | `19a4f5d7a7d969e9eb17d86eea6a7144d337e8cee2f1cb0284c0e9ff9ee92a73` | `3442643666` | 2026-10-24 20:03:23 |

All three certificates have exactly this URI SAN:
`https://github.com/aisecnomad/Nexus-ShadowBench/.github/workflows/attest.yml@refs/heads/main`.
Their issuer is `https://token.actions.githubusercontent.com`. The source,
signer and build-configuration digests equal the source commit above; the
source ref is `refs/heads/main`, trigger is `push`, and invocation is
`https://github.com/aisecnomad/Nexus-ShadowBench/actions/runs/40128040686/attempts/1`.
The repository URI and ID (`1426826719`), owner URI and ID (`193167434`),
`github-hosted` runner and public visibility match GitHub metadata. Each
bundle has one transparency entry and an inclusion proof. The
[machine-readable verification record](historical-attestation-verification.json)
preserves the observed Fulcio provenance extensions, fingerprints, validity times,
bundle hashes, log entries and command exit codes. This record documents a
check; rerunning cosign establishes trust in the bundles.

Each unmodified bundle returned `Verified OK` and exit 0 from
`cosign verify-blob` with the exact SAN and issuer above. On temporary copies,
all five negative checks returned exit 1 for **each** bundle (15 rejections):
append a space to the manifest; flip the last signature byte; supply a
different workflow identity; supply a different issuer; remove transparency
entries. Originals were not modified.

The repository-level command is:

```bash
python -m tools.attest verify --require-signatures --since c1fd03bf4cd4e3a46a40a39804a5c5939f50f954
```

Its required result is exit 0 and
`{"attestations": 3, "signed": 3, "unsigned": []}`. The pinned cosign checks
the signature, certificate chain and transparency evidence; the repository
verifier also checks every result file and preservation of committed bindings.

## Signing and import procedure

1. Merge the reviewed change to the
   [Attest results workflow](../.github/workflows/attest.yml) into `main`.
   A push that changes that workflow signs missing bundles for all three
   directories in the table, then requires strict verification before
   uploading its artifact. The trigger is restricted to `main` and that
   workflow path; it does not sign on a pull-request branch. Alternatively,
   dispatch the workflow on `main` once for each directory. Record each
   run's URL, run ID, attempt, `head_sha`, ref, event, conclusion and artifact
   ID. The workflow must be `attest.yml`, the event must match the observed
   `push` or `workflow_dispatch` run, and the ref must be `refs/heads/main`.
   Review the source at each recorded `head_sha`.
2. Download each successful run's `attestation` artifact. Compare the
   generated manifest byte for byte with the corresponding prepared
   manifest before adding its `.sigstore.json` bundle. The workflow refuses
   changed committed bindings and retains existing bundles rather than
   re-signing them. A later artifact may therefore contain signatures from
   earlier runs: record each certificate's actual signing run and source
   revision separately from the artifact's upload run. An artifact download
   or a green workflow alone is not signature verification.
3. Run `python -m tools.attest verify --require-signatures --since <base-commit>`
   with the pinned cosign version from the workflow. Require exit 0,
   `attestations: 3`, `signed: 3` and an empty `unsigned` list. This checks
   every listed file and rejects missing, added or changed result files.
   It also requires every historical subject, so removing the whole
   attestation directory cannot produce a successful empty check.
4. Verify certificate identity and provenance. The verifier constrains the
   certificate SAN to exactly
   `https://github.com/aisecnomad/Nexus-ShadowBench/.github/workflows/attest.yml@refs/heads/main`
   and the issuer to `https://token.actions.githubusercontent.com` through
   `cosign verify-blob`, which verifies the signature and transparency
   evidence. Separately inspect the bundle's Fulcio certificate extensions
   and compare its repository, source revision/ref and workflow invocation
   with the recorded Actions run and reviewed commit. Save the observed
   values and verification output in the checkpoint; do not infer them from
   filenames.
   A certificate claiming an unexpected source or workflow must be rejected.
5. Test real copies of the bundles with a changed manifest, changed
   signature, wrong workflow identity, wrong issuer and removed transparency
   evidence. All must return a
   nonzero verification result. Unit tests with a stubbed cosign process
   establish error propagation, not cryptographic verification.
6. Keep `--require-signatures` in the Companion tests workflow and
   `make verify` (used by the weekly rescore). The repository regression
   requires all three verified signatures; both Python jobs install cosign.
   Attestation verification also has its own CI job so a dependency-audit
   failure cannot skip it. Record new provenance before requesting review.

Bootstrap and enforcement were staged separately: #21 introduced the workflow
trigger; #20 imports its verified bundles and enforces them. No benchmark rerun
or historical evidence edit is needed. A bootstrap PR or mocked
workflow-routing test is not evidence that any signature exists.

## Separate dependency-audit failure

The [2026-10-24 Companion tests run](https://github.com/aisecnomad/Nexus-ShadowBench/actions/runs/40090476686)
failed in **Audit the hash-locked dependencies**. The cosign installation and
evidence/attestation verification steps were skipped. It is not evidence of
a failed attestation. Dependency remediation is reviewed separately.

A signature generated now proves that the identified workflow observed these
bytes now. It does not retroactively prove that the October 9 or October 11
benchmark runs were independently measured or signed at execution time.
