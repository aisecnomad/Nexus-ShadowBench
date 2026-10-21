# Frequently asked questions

Direct answers to the questions people should ask before using a ShadowBench
number. Where an answer is unwelcome to the benchmark's author, it is given
anyway. Terms are defined in the [glossary](glossary.md), and formulas in
[metrics.md](metrics.md).

## Contents

**Reading the results**

- [Can I cite these numbers as a tool's accuracy?](#can-i-cite-these-numbers-as-a-tools-accuracy)
- [Why does ShadowScan lead, and should I believe it?](#why-does-shadowscan-lead-and-should-i-believe-it)
- [What does "in-sample" mean for ShadowScan?](#what-does-in-sample-mean-for-shadowscan)
- [Why is a tool with 100% precision not "better"?](#why-is-a-tool-with-100-precision-not-better)
- [Why are some tools scored on only one surface?](#why-are-some-tools-scored-on-only-one-surface)
- [Why is specificity n/a for some tools?](#why-is-specificity-na-for-some-tools)
- [Why does an incomplete scan count as a false alarm?](#why-does-an-incomplete-scan-count-as-a-false-alarm)
- [Can I compare a tool's numbers across tracks?](#can-i-compare-a-tools-numbers-across-tracks)
- [Will there be letter grades or a leaderboard?](#will-there-be-letter-grades-or-a-leaderboard)
- [What is ShadowBench-450, and why can't it be compared?](#what-is-shadowbench-450-and-why-cant-it-be-compared)

**Fairness to the tools**

- [Who wrote the adapters for other vendors' tools?](#who-wrote-the-adapters-for-other-vendors-tools)
- [Why are power-pwn, Cartography, k8s-aibom and others not run?](#why-are-power-pwn-cartography-k8s-aibom-and-others-not-run)
- [Were the committed runs isolated the way the harness is now?](#were-the-committed-runs-isolated-the-way-the-harness-is-now)

**Reproducing and extending**

- [How do I check a published number myself?](#how-do-i-check-a-published-number-myself)
- [Why does the code-surface REPORT.md not reproduce byte for byte while metrics.json does?](#why-does-the-code-surface-reportmd-not-reproduce-byte-for-byte-while-metricsjson-does)
- [Why can't I just regenerate the committed corpus with my own seed?](#why-cant-i-just-regenerate-the-committed-corpus-with-my-own-seed)
- [How do I benchmark my own tool?](#how-do-i-benchmark-my-own-tool)
- [How do I dispute a label?](#how-do-i-dispute-a-label)
- [Can I run this against my real tenant data?](#can-i-run-this-against-my-real-tenant-data)

**Safety and context**

- [Is it safe to open the corpus in my IDE with an AI agent?](#is-it-safe-to-open-the-corpus-in-my-ide-with-an-ai-agent)
- [How does this relate to Nexus ShadowScan?](#how-does-this-relate-to-nexus-shadowscan)
- [Is ShadowBench a standard?](#is-shadowbench-a-standard)

## Reading the results

### Can I cite these numbers as a tool's accuracy?

No. They describe how a tool behaved on author-written, mostly synthetic
inputs, labeled and scored by the maintainer of one of the tools under
test. They are not field precision or recall and not an independent
evaluation. If you cite one, name the track, the `results/<date>/`
directory and the repository commit, and say that the corpus and labels are
author-written and not independent. "Independently benchmarked" is never an
accurate description of a ShadowBench result.

### Why does ShadowScan lead, and should I believe it?

Treat the lead as suspect. Several reasons favour ShadowScan by
construction:

- It is the only tool that declares all nine surfaces, and estate recall
  rewards coverage.
- Its maintainer wrote the rubrics that decide what counts, the labels and
  every other tool's adapter, knowing ShadowScan's documented triggers.
- The estate's input formats are the offline export formats ShadowScan
  parses; tools built for live APIs or kernel tracing cannot show their
  strength.
- Its rules were changed after the runs of record with their errors in view
  (see the next answer).

The committed results also show where it is weak, which is part of why they
are published: on the cases track its decoy specificity is 57% on identity
and 33% on SaaS, all 17 of its runtime false positives are a crypto-exchange
`gemini` CLI read as Gemini CLI, and 27 of its scans were incomplete. Only a
rerun by someone without a stake, ideally on their own corpus, can confirm
or refute the lead.

### What does "in-sample" mean for ShadowScan?

After the 2026-10-11 runs, ShadowScan's detection rules were changed with
those runs' errors in view; the
[ShadowScan changelog](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/CHANGELOG.md)
says detection was tuned using the 2026-10-11 estate errors, so later runs
on that estate are in-sample. Replayed on the frozen
estate, ShadowScan no longer makes seven of its twelve errors there. That
replay is not published as a result: it measures fit to errors the author
had seen. The same holds for the code surface, where the 2026-10-09
ShadowScan run (in-scope value F1 97.2%) followed changes driven by that
corpus. Measuring those changes needs a corpus authored without sight of
the errors.

### Why is a tool with 100% precision not "better"?

Because precision says nothing about what a tool missed, and a small
denominator makes it unstable. On the cases track, Cisco MCP Scanner and
Numbat each reported one entity, correctly: 100% precision with a Wilson
interval of 21–100%, at 4% in-scope recall. The estate README says the same
of its own table: 100% in-scope precision there means no in-scope false
positive among few predictions, not a precision estimate. Read precision
with recall, the interval and the number of predictions behind it.

### Why are some tools scored on only one surface?

Tools are scored only on the surfaces and modalities their adapters declare,
so a tool built for developer endpoints is not penalized in its in-scope
metrics for ignoring Okta exports. Estate recall then charges every tool for
the whole corpus, so the cost of narrow coverage is visible instead of
hidden. Both numbers are true at once. If you think an adapter declares too
little or too much for a tool, open an issue: the declarations were written
by the ShadowScan maintainer.

### Why is specificity n/a for some tools?

Specificity is measured on decoy records. In the cases track, the code and
endpoint surfaces have no decoy records: their negative cases are
repositories and home directories where any reported key that is not
tolerated is a false positive. A tool that ran only there has no decoy
denominator, so its decoy specificity is `n/a`. Its behaviour on negatives
still shows in its false-positive count and its case-level specificity.

### Why does an incomplete scan count as a false alarm?

Because a scan that did not read everything cannot vouch that nothing was
there. In the cases track an incomplete run (ShadowScan's exit 3, or an
exit outside the adapter's accepted codes that still reported entities)
keeps the true and false positives it reported but never earns a true
negative, and a negative case it scanned incompletely counts as a false
alarm. Without that rule a crash or a half-read repository would read as a
clean result. The estate scorer is stricter (an incomplete run earns
nothing), and the code-surface scorer is looser (it keeps the facts found
as a lower bound and marks the cells `(incomplete)`). This rule costs
ShadowScan most: its 20 live-runtime cases were all incomplete, so its
live-runtime specificity is 0%.

### Can I compare a tool's numbers across tracks?

No. The tracks were written separately and differ in tool lists, tool
versions, inputs, units and scoring rules, including how incomplete runs
are treated. Compare tools within one run of one track.

### Will there be letter grades or a leaderboard?

No grades. The vendor letter grades and PDF reports of the original cases
track were removed when it was integrated, and the ShadowBench-450 archive's
rankings were withdrawn. The tables in the README's
[Results of record](../README.md#results-of-record) are records of
specific runs with their caveats, ordered as each `REPORT.md` orders them,
not a ranking. A results index is kept in [results.md](results.md).

### What is ShadowBench-450, and why can't it be compared?

An archive of aggregate counts submitted in a pull request to ShadowScan,
preserved in [`benchmarks/shadowbench-450/`](../benchmarks/shadowbench-450/README.md).
It contains no fixtures, labels, adapter source or per-case predictions,
and the submitter states that the vendor binaries were not run. Only its
arithmetic and document consistency can be checked
(`python -m tools.shadowbench450_archive`). It supports no ranking, grade or
comparison with any track.

## Fairness to the tools

### Who wrote the adapters for other vendors' tools?

The ShadowScan maintainer, with AI assistance. Each adapter's docstring
records the tool version, the exact command, how the output maps to entity
keys and any calibration change. Adapters use each tool's defaults, impose
no confidence threshold and give no tool an allowlist, inventory or
known-agent list. Several recorded rows carry disclosed adapter defects of
their time; the estate README's disclosures [a] to [e] list them. A tool's
author who finds its adapter wrong should open an issue or a pull request;
see [adding-a-tool.md](adding-a-tool.md).

### Why are power-pwn, Cartography, k8s-aibom and others not run?

They have no offline entry point that the corpora can feed:

- **power-pwn** needs a live Microsoft 365 or Power Platform tenant with
  interactive authentication, or live internet scanning.
- **Cartography** syncs live cloud and AI provider APIs into a running Neo4j
  server, and exits without one.
- **Google's k8s-aibom** is an in-cluster controller with no manifest mode.
- **Microsoft's Copilot Studio Kit Agent Inventory** is a Power Platform
  solution.
- **AgentSight's** primary mode attaches eBPF probes to live TLS libraries;
  the estate ran its local-session reports instead, after eBPF loads failed
  on the run host.
- **Cisco AIBOM** was skipped on the code surface because it needs an LLM
  credential and the benchmark runs offline.

They are listed as not run, with the reason, rather than scored as
failures. A live replay profile (mock REST APIs behind the platforms' real
endpoints, or a kind cluster for k8s-aibom) is the designed extension; the
cases README's Known limits describe it, and it is not implemented.

### Were the committed runs isolated the way the harness is now?

No. The 2026-10-11 cases rows were recorded before the runner was hardened:
tools and inert processes ran as root, in fresh network and PID namespaces
but with the host's file system, `/root` and `/home` included, in view.
Fleet's table therefore saw the host's home directories, and its adapter
kept only rows under the case home. The current runner drops tools to uid
and gid 65534 and hides `/root` and `/home`. Each track's README says which
isolation produced its rows.

## Reproducing and extending

### How do I check a published number myself?

Re-score the committed rows. It needs no third-party tool and no network;
see [Level 1](../README.md#level-1-reproduce-the-published-numbers). The
cases, estate and code-surface `metrics.json` files reproduce byte for byte
at the current commit, and so do the cases and estate `REPORT.md` files.
[running.md](running.md) has the full procedure.

### Why does the code-surface REPORT.md not reproduce byte for byte while metrics.json does?

Re-rendering the 2026-10-09 code-surface run with the current `report`
command produces an identical `metrics.json` but a `REPORT.md` that differs
in four cells. The current renderer writes `no facts (incomplete)` where the
committed report says `clean (incomplete)`, for ShadowScan's incomplete
scans of three controls (BurntSushi/ripgrep, JamesNK/Newtonsoft.Json,
psf/requests) and one near-miss (jenkinsci/docker-agent). No number
differs. The committed report is byte-bound evidence and was not
regenerated. The current wording no longer describes an incomplete scan of
a negative repository as "clean", consistent with the code-surface README's
rule that an incomplete control is never shown as a clean negative.

### Why can't I just regenerate the committed corpus with my own seed?

Because the committed cases corpus was built with a faulty random-stream
derivation, now kept as the `legacy` scheme only so the corpus still
rebuilds. Under it the seed had no effect: every seed builds the same 346
cases, and four pairs of modalities shared one stream. New corpora use the
`sha256` scheme by default, which seeds each surface and modality from a
SHA-256 of the seed, surface and modality. To test for overfitting,
generate a fresh corpus at your own seed with the default scheme and check
that `verify` prints `stream scheme sha256` and no shared streams. Never use
`--stream-scheme legacy` for a new corpus.

### How do I benchmark my own tool?

Open a tool adapter request, then write an adapter for each track the tool
can run on, following [adding-a-tool.md](adding-a-tool.md): declare its
surfaces and modalities, pin its version, record the exact command and the
output mapping, fail closed on partial or malformed output, and calibrate on
a smoke corpus at another seed, never on the scored corpus. Run it on a
disposable host and publish the run in a new dated directory as described
in [submitting-results.md](submitting-results.md).

### How do I dispute a label?

Use the label dispute form in the
[issue chooser](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new/choose).
Give the corpus, the case or entity id, the label you believe is right and
the evidence at the pinned commit (a file and line, or an artifact path).
Labels are not changed because a tool missed or flagged something. The
committed corpora are byte-bound, so an accepted correction is published as
a new corpus version in a new path, the historical results keep their
original corpus, and the erratum is recorded beside them.

### Can I run this against my real tenant data?

Not directly, and not in this repository. The harness scores tools against
corpora with ground truth; your tenant's exports have none until someone
labels them. You can author a private corpus from your own exports in the
platform-native formats the cases and estate tracks use, label it yourself
and reuse the scorers, but never commit real tenant data, personal data or
credentials here. If you publish results from such a corpus, publish them as
an independent corpus with its provenance, without the sensitive data.

## Safety and context

### Is it safe to open the corpus in my IDE with an AI agent?

Not with an agent that has tool permissions. The corpora deliberately
contain prompt-injection text, launcher commands, synthetic credentials and
agent instruction files such as `CLAUDE.md`, `.mcp.json`,
`.claude/agents/` and Cursor rules inside the estate's artifacts. An AI
coding agent that loads instruction files from the directories it works in
can treat them as instructions. Read the files in a plain editor or a
viewer, hash them or scan them, but never execute their contents and never
start an agent inside `benchmarks/`. See
[Handling the corpus safely](../README.md#handling-the-corpus-safely).

### How does this relate to Nexus ShadowScan?

ShadowBench was extracted from ShadowScan commit `0792106b`, with every
imported file's bytes bound by `MIGRATION.json`. ShadowScan pins this
repository as its optional `benchmark-suite` submodule, and a required job in
its CI runs this repository's migration check, linters and tests against the
candidate scanner checkout. ShadowScan's weekly
[benchmark workflow](https://github.com/aisecnomad/Nexus-ShadowScan/blob/main/.github/workflows/benchmark.yml)
runs the code-surface track for ShadowScan alone against the committed run
its `BASELINE_RUN` names (currently `2026-10-09`). Both repositories have the same maintainer, which is the
conflict of interest stated at the top of every page.

### Is ShadowBench a standard?

Not yet. It is offered as a candidate open standard: its question, data,
rules, harness and results are open so that it can become one through
independent replication, not by declaration. What is missing, chiefly
independent corpus authors, labelers and reviewers, is listed in the
README's [road to independence](../README.md#limitations-and-the-road-to-independence)
and ordered in the [roadmap](../ROADMAP.md).
