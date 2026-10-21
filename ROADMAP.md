# Roadmap

This roadmap is intent, not a contract. Items move only when they keep the
evidence-preservation rules in [CONTRIBUTING.md](CONTRIBUTING.md) and the
conflict-of-interest rules in [GOVERNANCE.md](GOVERNANCE.md). Each item below
answers a limit that a track's README, the [threat model](docs/threat-model.md)
or the [supply-chain notes](docs/supply-chain.md) already documents.

## Now

- Keep the companion verifiable: every migrated byte bound by
  `MIGRATION.json` or a recorded `AMENDMENTS.json` entry, the estate freeze
  holding, the cases corpus rebuilding case for case, every published run
  re-scoring byte for byte in the weekly clean-room workflow, and the harness
  tests green against the pinned scanner.
- **Sign the runs of record.** Dispatch the Attest results workflow for the
  cases and estate 2026-10-11 and code-surface 2026-10-09 directories and
  commit the bundles, then make `tools.attest verify --require-signatures`
  the CI default.
- Benchmark the next discovery tools through the amendment path: a new
  adapter module plus a recorded amendment to its track's registry (or, for
  the cases track, its installer, its lock and its layout test).
- Keep community standards complete: contribution, security, support and
  governance policies, issue forms for disputes, adapters, runs and corpora,
  and an honest statement of who wrote what.
- Recruit an independent reviewer who can give the non-author approval for
  scorer, adapter and corpus changes.
- Recruit independent corpus authors and labelers with no stake in any scored
  tool (see
  [the path to independent stewardship](GOVERNANCE.md#path-to-independent-stewardship)).

## Next

- **A fresh, fully recorded, pre-registered run.** The 2026-10-11 runs carry
  caveats a run of record should not: rows recorded under weaker isolation,
  scoring rules revised after the run, 27 incomplete ShadowScan scans, and
  ShadowScan recorded only as `0.1.2`. Freeze the scorer, the key scheme
  (`canonical-v1` is proposed as the default; see
  [key-canonicalization.md](docs/key-canonicalization.md)), the adapters, the
  locks and the image digest **before** the run, publish that freeze, then
  run every tool end to end under the OCI sandbox with the harness commit,
  scanner commit, corpus digest and `resolved/` record in the manifest, and
  sign the results. On the 2026-10-11 corpora ShadowScan is in-sample, so
  until a held-out corpus exists such a run is a recorded regression run,
  not a run of record.
- **A power analysis per surface and multi-seed corpora.** Several F1
  intervals span 20 to 40 points and cannot separate tools. Size each surface
  for a target interval half-width (about five points), generate several
  corpora with the `sha256` stream scheme at that `--per-surface` (the
  committed corpus used the legacy derivation, under which the seed had no
  effect and four pairs of modalities shared a stream), run each tool on all
  of them, and report the spread across seeds alongside the per-case
  intervals.
- **Vendor-authored, signed adapters.** A tool's numbers depend partly on how
  well its adapter was written, and every adapter here was written by the
  maintainer of a competing tool. Let each vendor write or review its own
  adapter against the cases contract, add a conformance suite every adapter
  must pass (fail-closed errors, canonical keys, declared support), and record
  each adapter's author, reviewer and version in the run manifest.
- **An adversarial and evasive split.** Agents that rename their binaries,
  proxy model traffic through generic HTTPS, use self-hosted or obfuscated
  model endpoints, run MCP servers over stdio inside containers, or hold
  low-and-slow OAuth grants. This is the case operators care about; score it
  as its own split so the existing numbers stay comparable.
- **Operational cost and prevalence-adjusted metrics.** Report runtime and
  peak memory per unit of evidence, false alarms per thousand benign
  entities, and precision recomputed at stated base rates (for example 1% and
  5%), since precision on a balanced corpus overstates what an analyst sees.
- **Fix the estate's anchor collisions in a new freeze.** `validate` reports 12
  anchors that also occur outside their entity's artifacts. Fixing them needs
  a new estate version with its own freeze; the 2026-10-11 freeze stays as it
  is.
- **Commit raw tool output where licensing allows.** Neither 2026-10-11 run
  committed stdout, stderr or raw reports, so accepted non-zero exits cannot be
  checked from the published results. Keep them, redacted with the scrubber
  and size-bounded, for tools whose licences permit it.
- **Finish the supply-chain work.** Hash-lock the estate and code-surface
  tool installs as the cases track's now are; pin the image's build-stage
  Debian packages to a `snapshot.debian.org` date; give the estate runner the
  OCI backend; and exercise gVisor (`--oci-runtime runsc`) in the smoke
  workflow.
- **Versioned releases.** Tag ShadowBench v1.0 with a frozen specification
  (corpora, scorer, key scheme, mappings), archive each release on Zenodo with
  a DOI, and publish a short methods paper, so citations name an immutable
  release rather than a commit.
- **A results page, not a leaderboard.** Per-surface coverage-by-accuracy
  matrices with their intervals and every disclosure, generated from signed
  results and ordered by nothing but tool name, plus a `shadowbench submit`
  command that packages a container image digest, the manifest and the rows
  for a submission.
- **A right of reply.** Before a run is published, give each scored vendor a
  fixed window to check its adapter and contest results, and publish their
  response beside the report, whatever it says.

## Later, after independent review

- **A held-out test set kept by a third party.** A public development split
  for building adapters, and a private test split, authored and labeled
  without sight of any tool's results, held by a custodian with no stake in
  any tool. Tools are submitted as containers pinned by digest; the custodian
  runs them under the OCI sandbox and publishes signed results. It is the
  only way to measure ShadowScan's post-2026-10-11 detection changes, or any
  tuned tool, out of sample.
- **A contamination policy.** Canary strings in every corpus file so leaks
  into training data or rule sets can be detected, a do-not-train clause on
  the test split, and the development split under a permissive data licence.
- **Independent labelers and inter-annotator agreement.** Two labelers per
  corpus, Cohen's or Krippendorff's kappa reported per surface beside every
  metric, and disagreements adjudicated in the open.
- **Neutral stewardship.** Treat ShadowScan as one ordinary entrant (its
  adapter through the same path as every other, its results never listed
  first), require non-author approval in `CODEOWNERS` for scorer, label and
  adapter changes, and move the project to a neutral home (such as the OWASP
  GenAI Security Project, CoSAI or OpenSSF) with a steering group drawn from
  at least three organizations.
- **A live replay profile.** Mock REST APIs behind the platforms' real
  endpoints, and a kind cluster for Google's k8s-aibom, so that tools without
  an offline entry point (Cartography, power-pwn, the Copilot Studio Kit Agent
  Inventory, k8s-aibom, AgentSight's eBPF mode) can be measured.
- **Independent operators.** Reruns of committed protocols on other people's
  hardware, published with their manifests and signatures whatever they show.

## Not planned

- Letter grades, tiers, vendor rankings, "winner" tables or product
  recommendations.
- Presenting author-written results as independent evaluation or field
  precision and recall.
- Rehabilitating ShadowBench-450 as a benchmark without its missing fixtures,
  labels, adapter sources and per-case predictions.
- Editing historical results, refreshing a freeze to hide drift, or changing a
  label because a tool missed or flagged an entity.
- Executing corpus content, or collecting real tenant data into a public
  corpus.
