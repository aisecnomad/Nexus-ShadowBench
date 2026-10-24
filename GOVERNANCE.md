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

Recommended settings for `main` are required pull requests, passing status
checks (`tests`, `tests on Python 3.14` and CodeQL), conversation resolution,
and at least one approving review from an eligible non-author. Restrictions
should apply to administrators and other bypass actors too. Enabling these
settings requires repository administration access; verify their current
state against the repository's rules. This checklist alone does not establish
that they are enabled.

The [review and merge policy](CONTRIBUTING.md#review-and-merge-policy) remains
authoritative. Required status checks alone do not enforce its human review
requirement.

### OpenSSF Best Practices preparation

[The preparation checklist](docs/openssf-best-practices.md) links repository
controls and records gaps to investigate before a formal self-assessment at
<https://www.bestpractices.dev>. It does not claim an awarded badge or a
percentage of criteria met.

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

### Results

- **Committed results are immutable.** Every evidence byte that
  `MIGRATION.json` binds stays as imported, and a new run never overwrites an
  earlier one. A fix to a scorer or adapter reaches committed runs only as a
  documented re-score in a new directory that names the run it re-scores.
- **Harness amendments are recorded and reviewed.** Migrated harness code,
  tests and the copied CI and build locks change only through an `AMENDMENTS.json` entry that names the old and
  new SHA-256, the reason and the pull request. An amendment to a scorer, an
  adapter or a test that guards one needs the non-author approval, and must
  leave `make rescore` passing or say which committed numbers it would move
  and re-score them in a new directory. The verifier refuses amendments to
  evidence and to the code that generates or labels it.
- **Run of record.** Each track's README names its run of record (for both
  ShadowBench tracks, the 2026-10-11 run). A later run replaces it only when it
  is not in-sample and its manifest records the corpus digest, the harness
  commit and the version or commit of every tool. A regression baseline, such
  as the code-surface benchmark's 2026-10-09 run, is not thereby a run of
  record.
- **In-sample declaration.** A run is in-sample when the tool's detection rules
  were changed after seeing that corpus's results. Its README and report must
  say so. ShadowScan runs on the 2026-10-11 estate after the detection
  changes made with that run's errors in view, and ShadowScan's 2026-10-09
  code-surface run, are in-sample.
- **No independence by implication.** Results written, labeled or adapted by
  ShadowScan's maintainer are never presented as independent evaluation,
  measured field precision or recall, or a verdict on any vendor's product, in
  this repository, in ShadowScan's documentation or in any announcement.
  Green CI, AI-assisted reviews and archived review notes are not a second
  person.
- **No grades or rankings.** The project publishes per-tool measurements with
  their intervals and limits, not letter grades, tiers, recommendations or
  league tables. ShadowBench-450 stays an unverified archive.
- **Disclosure.** Every run discloses where its adapters, isolation or scoring
  differed from the current harness, as the 2026-10-11 reports do.

### Path to independent stewardship

The benchmark becomes evidence about the tools, rather than about one
author's view of them, only as these roles are filled by people without a
stake in any scored tool:

1. **Independent corpus authors** write a held-out estate or case set without
   seeing any tool's results on it, and attest to that in its README.
2. **Independent labelers** label it before any tool runs, ideally two per
   corpus with inter-annotator agreement reported and disagreements
   adjudicated in the open.
3. **Independent reviewers** with write access review scorer, adapter and
   corpus changes and give the non-author approval.
4. **Independent operators** rerun committed protocols on their own hardware
   and publish their manifests, whatever they show.

A corpus contributed under this path is accepted as its author wrote it. The
maintainer may review it for safety and format, but may not change its labels
or cases to suit any tool, ShadowScan included. Once independent reviewers
exist, decisions about labels and scoring rules that move ShadowScan's numbers
need their approval.

## Path to additional maintainers

The project welcomes reviewers and co-maintainers with experience in
detection engineering, benchmark and evaluation design, statistics, enterprise
identity, cloud and SaaS administration, endpoint and network telemetry, or
secure software maintenance. Experience maintaining a competing discovery tool
is welcome too; disclose it. Start with documentation, disputes with evidence,
reviews or a small adapter fix.

To express interest, open a
[question issue](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=question.yml)
titled `Maintainer interest` with your background, areas of focus and any
relationship to a scored tool. See [MAINTAINERS.md](MAINTAINERS.md) for the
current team.

### Reviewer role

A reviewer examines changes, records what was verified and its limits, and
gives the non-author approval the merge policy requires. This needs an
understanding of the evidence-preservation rules, care with scoring and
isolation changes, and willingness to be accountable for approvals. Write
access is granted deliberately and recorded in MAINTAINERS.md.

### Co-maintainer path

Sustained, careful contributions and constructive collaboration inform an
invitation to co-maintainer status; commit volume alone does not. Before access
is granted, the maintainer and candidate agree on scope, decision authority,
time commitment and escalation, and record the handover in a pull request that
updates this document and MAINTAINERS.md. Access is the least the role needs.
Until another maintainer is appointed there is a single-person continuity
risk.

### Offboarding

When a reviewer or maintainer steps away, revoke their access, update
MAINTAINERS.md and this document with the date, and review their recent
approvals for anything that lacked oversight.

## AI-assisted development

The project uses AI coding assistants to write and review code, corpora and
documentation. Contributors remain responsible for correctness, licensing,
security and test evidence. AI output, including an AI review of AI-produced
work, is never an independent approval and never an independent labeler. Do
not describe AI-assisted review notes as third-party audits.

## Community policies

Participation follows the [Code of conduct](CODE_OF_CONDUCT.md). Use the
[support guide](SUPPORT.md) for questions and the
[security policy](SECURITY.md#reporting) for private reports. Policy changes are
proposed in a pull request with the reason and the practical impact, and follow
the same review process as other changes.
