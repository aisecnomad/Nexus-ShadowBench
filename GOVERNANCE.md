# Governance

## Current model and accountability

ShadowBench is maintained by [@aisecnomad](https://github.com/aisecnomad),
who also maintains [Nexus ShadowScan](https://github.com/aisecnomad/Nexus-ShadowScan),
one of the tools this benchmark scores. The maintainer is accountable for
project decisions, merge authority, security advisories and repository
administration. There is no foundation, governing board or independent review
team.

That conflict of interest is the central fact of this project's governance.
Every corpus, label, adapter, scorer and result committed so far was written
by the ShadowScan maintainer, with AI assistance. The rules below exist so
that the evidence stays honest about that, and so that the benchmark can pass
to independent stewardship as people without that stake join.

The [review and merge policy](CONTRIBUTING.md#review-and-merge-policy) is
authoritative for code changes: one approving review from someone with write
access who did not author the change, passing CI on the final revision, and
no AI review counted as an approval. While the maintainer is the only account
with write access, a maintainer-authored change waits for a second eligible
human reviewer.

## Repository hygiene and process maturity

### Branch protection

`main` should have branch protection enabled (Settings → Branches → Add rule):

- Require a pull request before merging
- Require status checks to pass before merging (`tests`, CodeQL, and any others)
- Require conversation resolution
- Do not allow bypassing the above settings (or document any temporary exception)
- Optionally require signed commits

While the project has a single write-access account, the [review and merge policy](CONTRIBUTING.md#review-and-merge-policy) already requires a second eligible human reviewer for maintainer-authored changes. Enabling the rule makes that policy enforceable by GitHub.

### OpenSSF Best Practices Badge

The project is pursuing the OpenSSF Best Practices Badge (https://www.bestpractices.dev). Most Passing-level criteria are already met (SECURITY.md, automated tests, CI, license, vulnerability reporting process, etc.). Progress and justifications are tracked in [docs/openssf-best-practices.md](docs/openssf-best-practices.md).

## Roles

| Role | Responsibilities | Current holders |
|---|---|---|
| Maintainer | Review and merge changes, decide direction, manage access, handle security reports and moderate project spaces | @aisecnomad |
| Reviewer | Examine changes, record what was verified and its limits, triage issues and disputes, give the non-author approval | Seeking contributors; none assigned |
| Independent corpus author or labeler | Author or label a held-out corpus without access to any scored tool's results on it, and attest to that | Seeking contributors; none so far |
| Contributor | Submit fixes, adapters, runs, disputes or documentation; take part in design and review | Open to everyone |

A role is not a claim of independent assurance. Someone who produced a change,
or who maintains a tool it affects, cannot supply its independent approval.

## Decision making

- **Small fixes and documentation:** a focused pull request that explains the
  problem, the resulting behaviour and the validation.
- **Scorer and metric changes:** open an issue first. Say which published
  numbers would move and why the new rule is fairer to every tool, not just
  one. A change that is merged is applied to committed runs only as a
  documented re-score in a new directory.
- **New tool adapters:** open a tool adapter request. The adapter must run the
  tool at a pinned version through an offline entry point and document its
  command and output-to-entity mapping.
- **New corpora and tracks:** open a corpus proposal describing the question,
  the labeling rubric, who authored it and their relationship to every tool
  under test.
- **Security changes:** use private security reporting where public details
  would expose users.

State relevant conflicts of interest in every discussion. A disputed decision
can be revisited in its issue with new evidence or a narrower proposal. Record
the rationale for accepting, rejecting or deferring significant changes.
Conduct concerns follow the [Code of conduct](CODE_OF_CONDUCT.md), not a
technical vote.

## Benchmark integrity and conflict of interest

These rules bind every maintainer and contributor, the founding maintainer
first.

### Labels

- A label changes only through a
  [label dispute](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=label_dispute.yml)
  that cites evidence in the artifact or pinned repository itself: a manifest
  entry, an import, a committed configuration path, a record in an export.
- **A label never changes because a tool missed or flagged an entity.** A
  tool's behaviour is what the benchmark measures, not evidence about the
  ground truth.
- A frozen corpus is never edited. An accepted erratum is recorded as an
  erratum (as `corpus.json` `metadata.errata` and the estate README do) and
  takes effect in a new freeze or corpus version, with its own digest. Results
  scored against the old version keep the old version's name.
- Whoever maintains a scored tool may propose label changes but may not be the
  only reviewer of one that moves that tool's numbers.

### Corpora and adapters

- An independently authored corpus or adapter is accepted only when its author
  attests that they have not seen any scored tool's results on those inputs
  and that they have no stake in any tool the benchmark scores. The attestation
  is recorded with the corpus.
- The maintainer of a scored tool may not be the sole reviewer of a corpus,
  label or adapter change that moves that tool's published numbers.

### Results

- A run of a tool whose detection rules were changed with a corpus's errors in
  view is in-sample on that corpus and must be labeled as such.
- Historical results stay historical. A re-score goes in a new directory.

## Transition to independent stewardship

The goal is that a future maintainer or governing body has no stake in any
tool the benchmark scores. Until then the rules above keep the evidence honest
about the founding conflict of interest.
