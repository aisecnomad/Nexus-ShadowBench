# Roadmap

This roadmap is intent, not a contract. Items move only when they keep the
evidence-preservation rules in [CONTRIBUTING.md](CONTRIBUTING.md) and the
conflict-of-interest rules in [GOVERNANCE.md](GOVERNANCE.md). Each item below
answers a limit that a track's README already documents.

## Now

- Keep the companion verifiable: every migrated byte bound by
  `MIGRATION.json`, the estate freeze holding, the cases corpus rebuilding
  case for case, and the harness tests green against the pinned scanner.
- Keep community standards complete: contribution, security, support and
  governance policies, issue forms for disputes, adapters, runs and corpora,
  and an honest statement of who wrote what.
- Recruit an independent reviewer who can give the non-author approval for
  scorer, adapter and corpus changes.
- Recruit independent corpus authors and labelers with no stake in any scored
  tool (see
  [the path to independent stewardship](GOVERNANCE.md#path-to-independent-stewardship)).

## Next

- **A fresh, fully recorded ShadowScan run.** The 2026-10-11 estate run
  recorded ShadowScan only as `0.1.2`. A new run should record the harness
  commit, the scanner commit and the freeze. On the 2026-10-11 corpora it is
  in-sample, so it is published as a recorded regression run, not as a run
  of record; a new run of record needs a held-out corpus.
- **A versioned extension path for adapters.** The estate and code-surface
  adapter registries, and the cases installer and its layout test, are
  byte-bound evidence in `MIGRATION.json`, so adding a tool currently means
  proposing a change to a bound file. Define how new adapters are added
  (for example a registry outside the migrated set, or a new harness
  version) without touching preserved evidence.
- **Hash-locked tool installs.** Third-party tools are installed at pinned
  versions, but their transitive dependencies resolve at install time. Lock
  them, or record the resolved set with each run.
- **Multi-seed variance for the cases track.** The committed corpus was built
  with the legacy stream derivation, under which the seed had no effect and
  four pairs of modalities shared a stream. Generate several corpora with the
  `sha256` stream scheme at a larger `--per-surface`, run each tool on all of
  them, and report the spread across seeds alongside the per-case intervals.
- **Fix the estate's anchor collisions in a new freeze.** `validate` reports 12
  anchors that also occur outside their entity's artifacts. Fixing them needs
  a new estate version with its own freeze; the 2026-10-11 freeze stays as it
  is.
- **Scripted path scrubbing.** Local paths in committed `runs.json` and
  `tools.json` were replaced with placeholders by hand. Add a scrubber with
  tests so that every published run is scrubbed the same way.
- **Commit raw tool output where licensing allows.** Neither 2026-10-11 run
  committed stdout, stderr or raw reports, so accepted non-zero exits cannot be
  checked from the published results. Keep them, redacted and size-bounded,
  for tools whose licences permit it.

## Later, after independent review

- **An independently authored, held-out estate.** Written by someone who has
  not seen any tool's results on the current estate, labeled before any tool
  runs, frozen, and published with an attestation. It is the only way to
  measure ShadowScan's post-2026-10-11 detection changes out of sample.
- **Independent labelers and inter-annotator agreement.** Two labelers per
  corpus, agreement reported per surface, and disagreements adjudicated in the
  open.
- **A live replay profile.** Mock REST APIs behind the platforms' real
  endpoints, and a kind cluster for Google's k8s-aibom, so that tools without
  an offline entry point (Cartography, power-pwn, the Copilot Studio Kit Agent
  Inventory, k8s-aibom, AgentSight's eBPF mode) can be measured.
- **Larger samples on the weakest-powered surfaces**, so that per-surface
  intervals narrow enough to separate tools.
- **Independent operators.** Reruns of committed protocols on other people's
  hardware, published with their manifests whatever they show.

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
