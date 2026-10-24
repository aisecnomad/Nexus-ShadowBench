# OpenSSF Best Practices preparation

This is a repository evidence checklist, not a completed assessment against
the official [OpenSSF Best Practices criteria](https://www.bestpractices.dev).
No badge, passing percentage or independently verified security status is
claimed. A maintainer must review the current official criteria and supply
the required evidence before submitting a self-assessment.

## Repository evidence

| Area | Available evidence | Remaining verification |
|---|---|---|
| Purpose and license | [README](../README.md), [Apache-2.0 license](../LICENSE) | Map to the official criteria |
| Contribution process | [CONTRIBUTING](../CONTRIBUTING.md), [governance](../GOVERNANCE.md) | Verify actual non-author human reviews and repository enforcement |
| Build and tests | [Makefile](../Makefile), [CI workflow](../.github/workflows/ci.yml) | Confirm passing checks on the revision being assessed |
| Vulnerability reporting | [Security policy](../SECURITY.md) | Confirm the advertised reporting channel is operational |
| Dependency checking | Hash locks and daily CI audits | Inspect current audit results; an audit's existence is not a clean bill of health |
| Static analysis | Ruff, mypy and [CodeQL workflow](../.github/workflows/codeql.yml) | Inspect current findings and their resolution |
| Parser properties | [Hypothesis tests](../tests/test_fuzz_parsers.py), `make fuzz` | These bounded tests cover only two parsers, not the entire attack surface |
| Coverage | `make coverage` | Local report only; no published percentage or minimum gate |
| Change history | [Changelog](../CHANGELOG.md) and Git history | Decide and document the release/versioning process |

## Local coverage

After installing the hash-locked development dependencies as described in
[the README](../README.md), run:

```sh
make coverage
```

This runs the suite with branch coverage for `tools` and `benchmarks`, writes
an HTML report to `htmlcov/`, and prints missing lines. Corpus artifacts and
the external scanner checkout are excluded. Coverage is opt-in so normal
test runs keep their existing instrumentation and execution behaviour. A
coverage percentage describes executed code, not the strength of assertions
or the security of unexecuted paths. If tests fail, investigate those failures
before treating the generated report as a successful verification run.

## Next actions

1. Verify branch protection and required human approvals using the
   [governance checklist](../GOVERNANCE.md#branch-protection).
2. Perform a criterion-by-criterion assessment on the official badge site,
   recording the exact revision and links to evidence.
3. Decide on versioned harness releases for stable citation.
4. Expand parser properties as new attack surfaces are added. Publish a real
   coverage report before presenting a measured coverage badge.

Only display a Passing badge after it has actually been awarded.
