<p align="center"><img src="docs/assets/shadowbench-banner.jpg" alt="ShadowBench: an open benchmark for shadow AI agent discovery" width="100%"></p>

<h1 align="center">ShadowBench</h1>

<p align="center"><strong>An open, reproducible benchmark for tools that discover shadow AI agents.</strong><br>
Code · Identity · LLM gateways · Low-code · SaaS · Cloud · Endpoints · Network · Runtime</p>

<p align="center">
<a href="https://github.com/aisecnomad/Nexus-ShadowBench/actions/workflows/ci.yml"><img src="https://github.com/aisecnomad/Nexus-ShadowBench/actions/workflows/ci.yml/badge.svg" alt="Companion tests"></a>
<a href="https://github.com/aisecnomad/Nexus-ShadowBench/actions/workflows/codeql.yml"><img src="https://github.com/aisecnomad/Nexus-ShadowBench/actions/workflows/codeql.yml/badge.svg" alt="CodeQL"></a>
<a href="https://scorecard.dev/viewer/?uri=github.com/aisecnomad/Nexus-ShadowBench"><img src="https://api.scorecard.dev/projects/github.com/aisecnomad/Nexus-ShadowBench/badge" alt="OpenSSF Scorecard"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License: Apache-2.0"></a>
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11%E2%80%933.14-blue.svg" alt="Python 3.11-3.14"></a>
<a href="#limitations-and-the-road-to-independence"><img src="https://img.shields.io/badge/labels-author--written%2C%20not%20independent-orange.svg" alt="Labels: author-written, not independent"></a>
</p>

> [!IMPORTANT]
> **Not yet independent.** The maintainer of [Nexus ShadowScan](https://github.com/aisecnomad/Nexus-ShadowScan),
> one of the tools under test, wrote the corpora, labels, harnesses and every
> adapter, with AI assistance. Results describe tool behaviour on these
> inputs: not field precision or recall, not a vendor verdict, no grades.
> Everything needed to rerun it on your own corpus is committed and hashed.

## The Why: an open standard for discovery claims

Shadow AI agents (coding agents, MCP servers, OAuth apps, Copilot Studio
bots, Bedrock agents, model servers) leave evidence on nine surfaces, and
each discovery tool reads only some of them. Their claims cannot be compared
today:

- **No shared ground truth.** Each tool is shown on its author's data.
- **No negatives, no precision.** Monitoring *agents*, Minecraft *Bedrock*,
  the *Gemini* exchange and the MCP2515 chip all sound like AI. The recorded
  runs show the cost in every tool, ShadowScan included.
- **Coverage is confused with accuracy.** A tool precise on one surface and
  blind to the rest looks perfect or useless depending on the denominator.
- **Failures pass as clean.** A crashed or partial scan reports nothing, and
  nothing reads as a correct negative.

ShadowBench is a **candidate open standard**. It becomes one through
independent replication, not by declaration.

| A fair measurement needs | ShadowBench provides |
|---|---|
| Tool-neutral truth | Platforms' own identifiers, or a shared `<category>:<value>` fact taxonomy |
| Platform-native inputs | Okta/Graph exports, LiteLLM and Bedrock logs, Zeek, osquery, real repos pinned by commit |
| Negatives | Decoys, controls and near-misses taken from real tool confusions |
| Fail-closed scoring | Errors, timeouts, missing rows and incomplete scans never earn a true negative |
| Uncertainty | Wilson and bootstrap intervals, exact McNemar tests |
| Provenance | SHA-256 over corpora, freezes, rows and 555 migrated files; metrics re-score byte for byte |

## The What: methodology and metrics

**Question.** Given what an operator can collect from a surface, which AI
agents and plain AI uses are present, and can a tool find them without
flagging look-alikes? Labels: `agent` (autonomous or tool-using), `llm` (AI
use without agent evidence), `none` (decoy). Full rules:
[methodology](docs/methodology.md), [metrics](docs/metrics.md).

| Track | Inputs | Truth | Size |
|---|---|---|---|
| [Cases](benchmarks/shadowbench/cases/README.md) | Rubric-generated platform exports on 8 surfaces, plus 26 pinned repos | Per-case entities, tolerated keys, decoys | 346 cases, 738 entities, 735 decoys |
| [Estate](benchmarks/shadowbench/estate/README.md) | One fictional organization across all 9 surfaces | Entities with facts and anchors | 137 entities (87 positive, 50 negative), 139 frozen files |
| [Code surface](benchmarks/shadow-ai-discovery/README.md) | 87 public repos pinned by commit | `<category>:<value>` facts with file pointers | 839 facts, 22 negative repos |

| Metric | Definition |
|---|---|
| TP / FP / FN / TN | Reported key matches an expected entity / matches nothing expected or tolerated / expected but unreported / decoy left alone **on a complete run only** |
| Precision, recall, F1 | TP/(TP+FP), TP/(TP+FN), 2TP/(2TP+FP+FN) |
| Specificity | TN / all decoys in scope (decoys of failed or incomplete runs stay in the denominator) |
| Balanced accuracy, MCC | Case-level outcomes |
| Agent-tier recall | Expected agents the tool labeled `agent`; generic `ai` earns nothing |
| Estate recall, coverage | TP over every expected entity on all surfaces; surfaces run out of nine |

In-scope metrics use only the surfaces a tool declares; estate recall charges
it for all of them. Read both.

## The How: the harness and running it accurately

Each track has its own adapter, runner and scorer:
corpus → adapter → isolated runner → normalized rows + manifest (hashes) →
scorer (fails closed) → `metrics.json` → `REPORT.md`. Details:
[harness](docs/harness.md), [operator guide](docs/running.md).

```bash
git clone https://github.com/aisecnomad/Nexus-ShadowBench.git && cd Nexus-ShadowBench
make install     # hash-locked deps + ShadowScan pinned at 0792106b as scanner-source
make check       # audit, migration identity, tests, lint, types, secrets
```

### Level 0: verify the evidence

```bash
make verify integrity    # 555 files, cases corpus rebuild, estate validate and freeze
```

### Level 1: reproduce the published numbers

```bash
make rescore             # cases and estate 2026-10-11: metrics.json and REPORT.md byte for byte
```

No third-party tool runs at levels 0 and 1. **Level 2** (running tools)
needs a disposable, isolated Linux host with no credentials; **level 3**
(a fresh seed or your own corpus) is the only way past ShadowScan's in-sample
advantage. Never overwrite a result, never use `--force` for a published run,
and record every commit and tool version ([checklist](docs/running.md)).

## Results of record

Cases track, 2026-10-11 ([report](benchmarks/shadowbench/cases/results/2026-10-11/REPORT.md)).
Each tool ran only on the surfaces it declares.

| Tool | Coverage | Estate recall | In-scope P / R / F1 (F1 95% CI) | Decoy specificity |
|---|---|---|---|---|
| ShadowScan 0.1.2 | 9/9 | 84% | 78% / 88% / 82% (80–85) | 63% |
| AgentDiscover 2.9.5 | 2/9 | 4% | 96% / 20% / 32% (20–42) | n/a |
| AI-Infra-Guard v4.6.5 | 1/9 | 4% | 100% / 81% / 90% (84–96) | 100% |
| SafeDep vet v1.20.0 | 2/9 | 2% | 30% / 13% / 18% (10–27) | n/a |
| Microsoft `agent-discovery` 5.0.0 | 3/9 | 2% | 88% / 8% / 15% (8–23) | 100% |
| Fleet `ai_tools` (cf1217b) | 2/9 | 2% | 88% / 19% / 32% (18–46) | 100% |
| Snyk Agent Scan 0.6.8 | 1/9 | 1% | 100% / 29% / 45% (21–65) | n/a |
| Cisco MCP Scanner 4.8.6 | 1/9 | 0% | 100% / 4% / 8% (0–25) | n/a |
| Numbat (77ece3a) | 1/9 | 0% | 100% / 4% / 8% (0–24) | n/a |

Caveats: rows recorded under weaker isolation, scoring revised after the run,
27 ShadowScan scans incomplete, later ShadowScan runs in-sample. Estate,
code-surface and historical runs, with their status:
[docs/results.md](docs/results.md); corrections: [docs/errata.md](docs/errata.md).

## Integrity and provenance

`MIGRATION.json` binds 555 files from ShadowScan `0792106b`. Harness code,
tests and copied locks change only through the append-only
`AMENDMENTS.json`; evidence never does. `python -m tools.verify_migration`
checks both on every push, and CI audits every lock with `pip-audit`.
Results directories can be signed with Sigstore and are checked by
`make verify`; cases tools install from hash locks into a hardened sandbox
(optionally a digest-pinned container, under gVisor), and each run records
its sandbox and installed set. A weekly clean-room workflow re-scores the
cases and estate 2026-10-11 runs (metrics and reports) and the code-surface
2026-10-09 metrics from scratch; older historical results are not re-scored
([supply-chain notes](docs/supply-chain.md)).

## Handling the corpus safely

The corpus deliberately contains prompt-injection text, launcher commands and
fake credentials. Read and hash it; **never execute it** or give an AI agent
tool access over it. Report a real credential or an isolation flaw through
[SECURITY.md](SECURITY.md).

## Limitations and the road to independence

One author wrote the scanner, corpora, labels and adapters; eight surfaces and
the estate are synthetic; ShadowScan was tuned after the 2026-10-11 runs;
samples are small; only offline formats are covered. The fixes are
independent corpus authors, labelers and reviewers, larger multi-seed runs and
a live replay profile ([ROADMAP](ROADMAP.md), [GOVERNANCE](GOVERNANCE.md)).

## Documentation and community

[Docs index](docs/README.md) · [Methodology](docs/methodology.md) ·
[Metrics](docs/metrics.md) · [Running](docs/running.md) ·
[Add a tool](docs/adding-a-tool.md) · [Submit results](docs/submitting-results.md) ·
[Threat model](docs/threat-model.md) · [FAQ](docs/faq.md)

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) ·
[Support](SUPPORT.md) · [Governance](GOVERNANCE.md) ·
[Code of Conduct](CODE_OF_CONDUCT.md) · [Changelog](CHANGELOG.md) ·
[Dispute a label or request a tool](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new/choose)

## Citation and license

Cite the commit and results directory you used; metadata in
[CITATION.cff](CITATION.cff). Licensed [Apache-2.0](LICENSE) with the
original [NOTICE](NOTICE). Public repositories are referenced by URL and
commit, not redistributed. Tool names identify what was measured and imply
no endorsement.
