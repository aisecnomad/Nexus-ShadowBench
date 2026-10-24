# Historical results attestation checkpoint

Status on 2026-10-24: **three digest manifests prepared; zero Sigstore
bundles generated or verified**. This is a signing checkpoint, not a completed
attestation. CI signature enforcement remains pending until all three real
bundles verify. The historical results and metrics are unchanged.

The manifests were generated with `python -m tools.attest digest` at reviewed
source commit `f875ccbf06cebadb9c267788fe58b2f3f3b69239`. Each of the 20
listed file digests was also checked against the bytes returned by
`git show <commit>:<path>`, rather than trusting only the working tree.

Local verification at this checkpoint: 160 attestation, documentation,
repository-policy and migration tests passed, including real cosign v3.1.4
rejection of malformed and wrong-identity bundles. Lint, formatting and type
checks passed. Cases and estate metrics/reports and code-surface metrics
re-scored byte for byte. The full suite produced 1,423 passes, 20 skips and
22 failures in ownership, process and sandbox tests; all 22 failure identities
were reproduced at the unchanged source commit above. This environment did
not establish a green full-suite result.

| Preserved result directory | Files | Manifest SHA-256 |
|---|---:|---|
| `benchmarks/shadowbench/cases/results/2026-10-11` | 12 | `0b94e4b9f7cfbff5f0030be5ee463198da7543dbbc06c2a99791e246bf97f61d` |
| `benchmarks/shadowbench/estate/results/2026-10-11` | 4 | `95f0d4bbd69280baf39fd116e7c83de1e6ce42a33f46d0f8756440ded135d959` |
| `benchmarks/shadow-ai-discovery/results/2026-10-09` | 4 | `f27c5653422500ccbb5791733535f71e11a906e7e0832c7a41931c39954c088b` |

## Complete signing

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
   values and verification output here; do not infer them from filenames.
   A certificate claiming an unexpected source or workflow must be rejected.
5. Test real copies of the bundles with a changed manifest, changed
   signature, wrong workflow identity and wrong issuer. All must return a
   nonzero verification result. Unit tests with a stubbed cosign process
   establish error propagation, not cryptographic verification.
6. Only after those checks pass, add `--require-signatures` to both the
   Companion tests workflow and `make verify` (used by the weekly rescore).
   Make the repository-level regression require all three verified
   signatures and install cosign in the Python 3.14 job as well, whose tests
   verify any committed bundles. Run attestation verification in its own CI job so a separate
   dependency-audit failure cannot skip it. Update the roadmap and this
   checkpoint with actual signing run evidence, then mark the PR ready.

The workflow change and strict-enforcement change are staged separately.
Merge the reviewed workflow change first, collect and verify its real bundles,
then add those bundles and their provenance to the enforcement change. Keep
enforcement in draft until its strict checks pass. No benchmark rerun or
historical evidence edit is needed. A bootstrap PR or mocked workflow-routing
test is not evidence that any signature exists.

## Separate dependency-audit failure

The [2026-10-24 Companion tests run](https://github.com/aisecnomad/Nexus-ShadowBench/actions/runs/40090476686)
failed in **Audit the hash-locked dependencies**. The cosign installation and
evidence/attestation verification steps were skipped. It is not evidence of
a failed attestation. Dependency remediation is reviewed separately.

A signature generated now proves that the identified workflow observed these
bytes now. It does not retroactively prove that the October 9 or October 11
benchmark runs were independently measured or signed at execution time.
