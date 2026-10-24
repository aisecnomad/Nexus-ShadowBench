# OpenSSF Best Practices Badge — Progress

This document tracks self-assessment against the OpenSSF Best Practices Badge (Passing level) criteria. Register the project at https://www.bestpractices.dev to obtain the official badge.

Most criteria are already met. Items marked **TODO** need maintainer action on the badge site or a small repository change.

## Basics

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Description | Met | README.md |
| Project website / documentation | Met | README + docs/ |
| FLOSS license | Met | LICENSE (Apache-2.0) |
| Documentation of how to contribute | Met | CONTRIBUTING.md |
| Build instructions | Met | README + Makefile |
| Installation instructions | Met | README + `make install` |
| Automated test suite | Met | pytest + CI |
| New functionality includes tests | Met | CONTRIBUTING.md quality gates |
| Warnings as errors (or documented) | Met | ruff + mypy strict in CI |
| Static analysis | Met | CodeQL + ruff (Bandit) |
| Vulnerability reporting process | Met | SECURITY.md (private advisories) |
| Publicly known vulnerabilities fixed | Met | pip-audit daily; no open advisories |

## Change Control

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Public version-controlled source repository | Met | GitHub |
| Unique version numbers | Partial | Harness is not packaged; commits + tags recommended |
| Release notes | Met | CHANGELOG.md |
| Code review for changes | Partial | Policy exists; enable branch protection to enforce |
| Two-person review for security-sensitive changes | Documented | GOVERNANCE.md + CONTRIBUTING.md |

## Reporting

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Bug reporting process | Met | Issue templates |
| Vulnerability reporting process | Met | SECURITY.md |
| Response process for vulnerabilities | Met | SECURITY.md |

## Quality

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Working build system | Met | Makefile + CI |
| Automated test suite that is typically invoked | Met | `make test` / CI |
| New functionality added with tests | Met | CONTRIBUTING.md |
| Regression tests for fixed bugs | Met | CONTRIBUTING.md |
| Continuous integration | Met | .github/workflows/ci.yml |
| Code coverage tracked | Met | pytest-cov (see `make coverage`) |

## Security

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Secure development knowledge | Met | Threat model, isolation design |
| Use of basic good cryptographic practices | Met | SHA-256 binding, Sigstore, hash locks |
| Software released only after security evaluation | N/A | Not a released package; harness changes go through review |
| Dependency updates | Met | Dependabot (Actions) + daily pip-audit |
| No known critical vulnerabilities | Met | pip-audit clean |

## Analysis

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Static analysis | Met | CodeQL + ruff |
| Dynamic analysis (fuzzing) | Partial | Hypothesis targets added (`make fuzz`); expand over time |

## Next actions

1. Enable branch protection on `main` (see GOVERNANCE.md).
2. Register at https://www.bestpractices.dev and mark criteria with justifications linking here.
3. Tag a harness release (e.g., `v0.1.0-harness`) for citation stability.
4. Expand fuzz targets as new parsers are added.

Once the Passing badge is earned, add the badge to README.md.
