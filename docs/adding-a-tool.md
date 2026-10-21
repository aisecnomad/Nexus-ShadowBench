# Adding a discovery tool

How to write an adapter that lets ShadowBench run another shadow AI agent
discovery tool and score its output, on each of the three live harnesses.
The interfaces below are copied from the code; the fairness rules and the
review checklist are what make the resulting numbers mean something.

**Contents**

- [Before you start](#before-you-start)
- [What an adapter does, and must not do](#what-an-adapter-does-and-must-not-do)
- [Cases track adapter](#cases-track-adapter)
- [Estate track adapter](#estate-track-adapter)
- [Code-surface discovery adapter](#code-surface-discovery-adapter)
- [Fairness rules](#fairness-rules)
- [Amending byte-locked harness files](#amending-byte-locked-harness-files)
- [Adapter pull request checklist](#adapter-pull-request-checklist)

## Before you start

- Read [harness.md](harness.md) for the pipeline and
  [metrics.md](metrics.md) for how rows are scored.
- Read an existing adapter for a tool like yours. Every adapter's module
  docstring states the version it was measured against, the exact command
  line, the output format and the mapping from output to keys or facts.
- Decide which track measures what your tool does. A tool that reads
  exports, logs, home directories, process tables or loopback services
  belongs in the cases track; one that scans a whole estate or per-repository
  and per-home units belongs in the estate track; a repository scanner can
  also join the code-surface discovery benchmark. Numbers from different
  tracks are not comparable.
- Running third-party tools executes their code. Develop and run on a
  disposable machine with no credentials ([threat-model.md](threat-model.md)).

## What an adapter does, and must not do

An adapter:

1. declares what the tool handles (surfaces and modalities, or categories);
2. reports why the tool cannot run (`unavailable_reason`) and what version
   is installed (`version`);
3. returns the processes to run, as data; the runner executes them;
4. maps the tool's own output onto the corpus's keys or facts.

It must not:

- execute the tool itself or run anything outside the runner;
- interpret findings beyond what the tool reported (no extra heuristics, no
  confidence threshold of its own);
- read the corpus's truth, labels, decoys or anchors;
- turn a crash, timeout, missing report, empty output or unparsable output
  into an empty clean result.

## Cases track adapter

### Interface

The contract is [`tools/shadowbench/cases/contract.py`](../tools/shadowbench/cases/contract.py)
(`Adapter` protocol) plus the rules in
[`adapters/__init__.py`](../tools/shadowbench/cases/adapters/__init__.py).
[`adapters/registry.py`](../tools/shadowbench/cases/adapters/registry.py)
imports every module in `adapters/` whose name does not start with `_` and
is not `registry`, and takes its module-level `ADAPTER`; an import failure is
recorded, not fatal.

| Member | Type | Meaning |
|---|---|---|
| `name` | `str` | Adapter id; names `<tool>.jsonl` and the `tools.json` entry |
| `display` | `str` | Human-readable name for the report |
| `surfaces` | `Mapping[str, frozenset[str]]` | Surface to the modalities the tool handles, from `contract.MODALITIES` |
| `withheld_decoys` (optional) | `Mapping[tuple[str, str], tuple[str, ...]]` | Per (surface, modality), key prefixes of decoys whose records your input conversion never passes to the tool |
| `unavailable_reason(env)` | `str \| None` | Why the tool cannot run (no `bin`, missing file), or `None` |
| `version(env)` | `str` | A `version` in the `tools.json` entry if present; otherwise a probe through `_probe` |
| `invocations(case, env, work)` | `list[Invocation]` | The processes to run, in order |
| `normalize(case, work, runs)` | `AdapterResult` | Map the stored output onto entities |

`Invocation(argv, cwd, env={}, timeout=300, ok_codes=frozenset({0}), stdin=None)`:
`env` is the process's whole environment (start from `base_env(home, work)`),
and `ok_codes` lists the exit codes that mean the tool finished.

`AdapterResult(status, entities=[], note="", raw={}, out_of_taxonomy=0)`:
`status` is `ok` or `error`; `entities` are `Entity(kind, key, label,
attributes)` with `label` one of `agent`, `llm` or `ai` (a tool that cannot
tell agents from plain AI use reports `ai`); `raw` is kept beside the rows
and never scored; `raw["incomplete"] = True` flags a scan the tool says did
not read everything.

Entity keys must use the contract's tool-neutral forms: `app:<id>`,
`caller:<alias>`, `bot:<id>`, `flow:<id>`, `workflow:<id>`, `resource:<ARN>`,
`k8s:<namespace>/<Kind>/<name>`, `artifact:<path relative to home>` (use
`relative_artifact`), `client:<ip>`, `service:<ip>:<port>`, `process:<pid>`
(the runner translates pids to `proc:<index>`), and on the code surface only
`<category>:<value>` facts from
[`tools/discovery_benchmark/taxonomy.py`](../tools/discovery_benchmark/taxonomy.py).

### Rules from `adapters/__init__.py`

- **Fail closed.** A crash, timeout, missing report, empty output or output
  that does not parse is an `error` result, never an `ok` result with no
  entities; so is an inventory entry that is not an object, and a per-target
  scan that prints no result for one of its targets.
- **Incomplete scans.** A tool that says it did not read everything is
  normalized and flagged with `raw["incomplete"]`. The runner also flags a
  run that exits outside `ok_codes` but still reported entities.
- **Code surface.** Emit only taxonomy facts. A hit that maps to no fact is
  dropped and counted in `AdapterResult.out_of_taxonomy`, never emitted under
  another key; the scorer treats it as an alarm on a negative case.
- **Version probes** run the tool's binary only through
  `_probe.run_probe` (or its helpers `cli_version` and
  `distribution_version`), which scrub the environment and, as root, drop to
  the stage's identity in fresh namespaces.
- **Withheld decoys.** When your conversion drops records a decoy comes from,
  declare the prefixes in `withheld_decoys` (the ShadowScan adapter does so
  for AWS IAM roles). The scorer then leaves those decoys out of the tool's
  specificity unless it reports one anyway. The scorer reads this attribute
  from the loaded adapter, and refuses to score (without `--force`) when an
  adapter module does not load.

### Skeleton

Documentation only; the names match the real interface. Replace `mytool`,
the command line and the parsing with your tool's.

```python
"""MyTool on the endpoint/home surface.

CLI (measured against mytool 1.2.3, PyPI ``mytool``)::

    mytool inventory --json --output <work>/mytool.json

run with ``HOME=<case home>`` and the contract's minimal environment.
Exit 0 is a completed inventory; exit 4 means some paths were unreadable
(normalized and flagged incomplete). Report: a JSON array of objects with
``path`` and ``kind``.

Mapping: each ``path`` under the case home becomes
``artifact:<path relative to home>``; ``kind == "mcp"`` or ``"agent"`` is
labelled ``agent``, ``kind == "assistant"`` ``llm``, anything else ``ai``.
Paths outside the home are dropped and counted in the note.

Fail closed: a missing, empty or unparsable report, or an entry that is not
an object, is an error. Calibration: none yet (record each calibration
change here, with the probe or smoke input that forced it).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from tools.shadowbench.cases.adapters._probe import cli_version
from tools.shadowbench.cases.contract import (
    AdapterResult,
    Entity,
    Invocation,
    MaterializedCase,
    RunResult,
    ToolEnv,
    base_env,
    relative_artifact,
    tail,
)

BIN = "mytool"
LABELS = {"mcp": "agent", "agent": "agent", "assistant": "llm"}


class MyTool:
    name = "mytool"
    display = "MyTool"
    surfaces: Mapping[str, frozenset[str]] = {"endpoint": frozenset({"home"})}

    def unavailable_reason(self, env: ToolEnv) -> str | None:
        binary = env.binary(BIN)
        if not binary:
            return f"no 'bin' configured for {BIN} in tools.json"
        if not Path(binary).exists():
            return f"{binary} does not exist"
        return None

    def version(self, env: ToolEnv) -> str:
        pinned = env.tool(BIN).get("version")
        if isinstance(pinned, str) and pinned:
            return pinned
        binary = env.binary(BIN)
        return cli_version(binary) if binary else "unknown"

    def invocations(self, case: MaterializedCase, env: ToolEnv, work: Path) -> list[Invocation]:
        if case.home is None:
            return []
        argv = (env.binary(BIN) or BIN, "inventory", "--json", "--output", str(work / "mytool.json"))
        return [
            Invocation(
                argv=argv,
                cwd=work,
                env=base_env(case.home, work),
                timeout=300,
                ok_codes=frozenset({0, 4}),
                stdin="",
            )
        ]

    def normalize(self, case: MaterializedCase, work: Path, runs: list[RunResult]) -> AdapterResult:
        if case.home is None or not runs:
            return AdapterResult("error", note="tool was not run")
        run = runs[0]
        raw = {"stderr": tail(run.stderr, 2000), "incomplete": run.code == 4}
        if run.timed_out:
            return AdapterResult("error", note=f"timeout after {run.seconds:.0f}s", raw=raw)
        report = work / "mytool.json"
        try:
            items = json.loads(report.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return AdapterResult("error", note=f"exit {run.code}: no readable report", raw=raw)
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            return AdapterResult("error", note="report is not a list of objects", raw=raw)
        found: dict[str, Entity] = {}
        outside = 0
        for item in items:
            key = relative_artifact(str(item.get("path") or ""), case.home)
            if key is None:
                outside += 1
                continue
            label = LABELS.get(str(item.get("kind")), "ai")
            found.setdefault(key, Entity("artifact", key, label))
        note = f"items={len(items)} outside_home={outside}"
        return AdapterResult("ok", entities=list(found.values()), note=note, raw=raw)


ADAPTER = MyTool()
```

An explicitly empty report (`[]`) from a completed run is a clean negative;
a missing or unparsable one is an error. Decide which your tool prints when it
finds nothing, and test both.

### Tool configuration and versions

The runner reads `tools.json` (`{"tool_root": ..., "tools": {"<name>":
{"bin": ..., "version": ...}}}`). A `version` string there is recorded in
the manifest as given, for every tool, without a probe; otherwise the runner
calls `version()` once per tool. Every path in `tools.json` must lie outside
`/root`, `/home`, `/var/tmp` and `/dev/shm`, and be readable and executable by
uid 65534, or the runner refuses to start. Record how you installed the tool
(exact version or commit, and a `uv pip freeze` or `go.sum` for transitive
dependencies): [`install_tools.sh`](../tools/shadowbench/cases/install_tools.sh)
pins versions, not hashes. See the cases harness README's
[Tool configuration](../tools/shadowbench/cases/README.md#tool-configuration).

### Calibrating without touching the scored corpus

Calibrate on a different seed with the default stream scheme, never on the
scored corpus:

```bash
python -m tools.shadowbench.cases generate --seed 1 --per-surface 4 --output smoke.json
python -m tools.shadowbench.cases verify --corpus smoke.json   # expect "stream scheme sha256" and no shared streams
```

The committed adapters were calibrated on a smoke corpus that, because of the
legacy stream bug, drew from the scored corpus's own streams; see the cases
README's [Random streams](../benchmarks/shadowbench/cases/README.md#random-streams).

## Estate track adapter

The contract is [`tools/shadowbench/estate/adapters/__init__.py`](../tools/shadowbench/estate/adapters/__init__.py):

| Member | Type | Meaning |
|---|---|---|
| `spec` | `ToolSpec(id, name, vendor, surfaces, categories, notes="")` | `id` is the `tools.json` key; `surfaces` and `categories` declare scope |
| `unavailable_reason(cfg)` | `str \| None` | Why the tool cannot run, recorded in `tools_skipped` |
| `version(cfg)` | `str` | Probed from the binary (`run_version`, `python_package_version`) |
| `units(cfg, estate, corpus)` | `list[str]` | `estate`, `code:<repo>` (`code_units`), `home:<device>` (`home_units`), or `sim` |
| `commands(cfg, unit, estate, out_dir)` | `list[Command]` | `Command(argv, ok_exit_codes=frozenset({0}), env={}, timeout=None, stdout_name=None)`; cwd is the unit's output directory |
| `normalize(unit, out_dir)` | `Normalized` | `Normalized(predictions=[], raw_count=0, detail={}, error=None, incomplete=False)` |

A `Prediction(fact, text, surface, shadow=None)` carries one
`<category>:<value>` fact from
[`tools/shadowbench/estate/taxonomy.py`](../tools/shadowbench/estate/taxonomy.py),
the tool's own identifiers in `text` (resource ids, paths, names; the scorer
matches entity anchors against it case-insensitively), the adapter's surface
placement, and a registry verdict when the tool makes one. Facts outside the
taxonomy are dropped, so they are never penalized. Set `error` or
`incomplete` rather than returning an empty list when the output is missing
or partial; the scorer gives an incomplete unit nothing (its expected facts
are missed and its negatives earn no true negative).

Helpers in [`adapters/common.py`](../tools/shadowbench/estate/adapters/common.py)
map client names a tool prints onto `ai-client:` values (`client_slug`) and
write wrapper scripts. Tools that launch MCP servers to enumerate them should
use the refusing launcher shims (`common.LAUNCHERS`) so no corpus
configuration is executed. A tool with no offline entry point belongs in
[`not_runnable.py`](../tools/shadowbench/estate/adapters/not_runnable.py),
which always reports its blocker so the report names it instead of omitting
it. Adapters are listed explicitly in
[`registry.py`](../tools/shadowbench/estate/adapters/registry.py), in report
order.

## Code-surface discovery adapter

The contract is [`tools/discovery_benchmark/adapters/__init__.py`](../tools/discovery_benchmark/adapters/__init__.py):

| Member | Type | Meaning |
|---|---|---|
| `spec` | `ToolSpec(id, name, vendor, categories, notes="")` | `categories` are the taxonomy categories the tool declares; in-scope metrics count only these |
| `unavailable_reason(cfg)` | `str \| None` | |
| `version(cfg)` | `str` | |
| `commands(cfg, repo_dir, out_dir)` | `list[Command]` | `Command(argv, cwd="out" or "repo", ok_exit_codes=frozenset({0}), env={})` |
| `normalize(out_dir)` | `Normalized` | `Normalized(facts=set(), raw_count=0, detail={}, error=None)`; set `detail["incomplete"]` for a partial scan |

Map package URLs, imports, paths and hostnames onto facts through the alias
tables in [`taxonomy.py`](../tools/discovery_benchmark/taxonomy.py) (for
example `facts_from_purl`), so no tool is scored against a vocabulary it
cannot express. Output outside the taxonomy is ignored rather than
penalized. Adapters are listed explicitly in
[`adapters/registry.py`](../tools/discovery_benchmark/adapters/registry.py).
`renormalize` re-reads stored output with the current adapters, so a mapping
fix can be applied to a run without re-running the tools; disclose any such
re-normalization with the results.

## Fairness rules

These come from the tracks' bias controls and apply to every adapter,
ShadowScan's included:

1. **The tool's own defaults and its own notion of a finding.** No
   confidence threshold, filter or post-processing beyond mapping names
   onto keys. Document every non-default flag and why it is needed to run
   offline (for example declining consent prompts so no server starts).
2. **No allowlists, inventories or known-agent lists.** In the cases track no
   tool is given one. In the estate track the agent registry is part of the
   corpus artifacts, so any tool that reads a registry can use it, and only
   its shadow-versus-registered verdict is scored in the shadow layer.
3. **Never calibrate on the scored corpus.** Use probe inputs and a smoke
   corpus at another seed. Commit the adapter before running it on the
   scored corpus, and record calibration changes in the docstring.
4. **Record every conversion.** When the tool reads its own offline format,
   document the conversion in the docstring, and declare the decoys it
   withholds (cases track) so the scorer does not credit unseen records.
5. **Fail closed.** Partial, truncated or malformed output is an error or an
   incomplete scan, never a clean negative. Do not accept a non-zero exit as
   success unless the tool documents it as a completed scan, and say so.
6. **Never execute corpus content.** No launching configured MCP servers,
   running repository scripts, installing dependencies or following
   prompt-injection text in the inputs.
7. **Declare only what the tool does.** Scope (surfaces, modalities,
   categories) is the tool's documented scope, not where it happens to score
   well. Estate-wide recall charges every tool for what it does not cover.
8. **Disclose the conflict of interest.** State who wrote the adapter, and
   whether that person is affiliated with this tool or any other tool under
   test.

## Amending byte-locked harness files

Every file imported from ShadowScan is bound by SHA-256 in
[`MIGRATION.json`](../MIGRATION.json). That includes the files a new adapter
normally touches:

| Track | What a new adapter needs | Bound file(s) to amend |
|---|---|---|
| Cases | A new module in `adapters/` is discovered automatically. But `test_install_script_layout_satisfies_every_adapter` in `tests/unit/test_shadowbench_cases_adapters.py` requires every loaded adapter except ShadowScan to be satisfied by the `tools.json` that `install_tools.sh` writes, so the installer must configure it | `tools/shadowbench/cases/install_tools.sh` |
| Estate | An entry in the explicit adapter list | `tools/shadowbench/estate/adapters/registry.py` |
| Code-surface discovery | An entry in the explicit adapter list | `tools/discovery_benchmark/adapters/registry.py` |

Live harness code and tests may change only through a recorded amendment.
Add the new adapter module (a new file, so nothing to amend), edit the bound
file, then record it:

```bash
python -m tools.verify_migration --amend tools/discovery_benchmark/adapters/registry.py \
    --reason "Register the <tool> adapter" \
    --reference https://github.com/aisecnomad/Nexus-ShadowBench/pull/<number>
python -m tools.verify_migration    # now reports "amended": <n>
```

`--amend` appends an entry to [`AMENDMENTS.json`](../AMENDMENTS.json) with the
SHA-256 the file changes from (its migrated bytes or its previous amendment)
and the bytes, Git blob, mode and SHA-256 it changes to. Commit the edit and
the ledger together; if the file changes again in review, amend it again
(the chain is append-only) or, before merge, drop the entry and record it
once more. The verifier refuses entries for evidence and for the code that
produces it: corpora, labels, freezes, results, the cases generator, its
case model and families, the ground-truth labeler, the taxonomies, and the
legacy `tools/benchmark` and `tools/benchmark_realworld` harnesses, whose
sources are hashed into recorded freezes. Never amend a file to make a
failing test pass without saying why in the reason.

## Adapter pull request checklist

- [ ] The module docstring names the tool, the exact version or commit it was
      measured against, the exact command line, the output format, the
      output-to-key or output-to-fact mapping, accepted non-zero exits and
      what they mean, and every calibration change.
- [ ] The version is pinned and reproducible: an installer step or written
      instructions, plus transitive dependency records.
- [ ] Unit tests under `tests/unit/` feed recorded-shape output (no
      third-party tool runs in the tests) and cover: a normal report; an
      explicitly empty report; empty output; unparsable output; an entry
      that is not an object; an incomplete scan; and, on the code surface,
      out-of-taxonomy hits counted rather than emitted.
- [ ] `unavailable_reason` names what is missing; `version` uses the probe
      helpers and never the caller's environment.
- [ ] Scope is the tool's documented scope; `withheld_decoys` declares every
      decoy a conversion drops.
- [ ] No corpus content is executed; no network is needed.
- [ ] The adapter was committed before any run on the scored corpus, and no
      scored result was used to change it.
- [ ] Every bound file the change touches is recorded in `AMENDMENTS.json`
      with `python -m tools.verify_migration --amend`, and
      `python -m tools.verify_migration` passes.
- [ ] The author's affiliation with any tool under test is disclosed.
- [ ] `ruff check`, `ruff format --check`, `mypy tools benchmarks` and
      `python -m pytest -q` pass.
