"""Canonical entity keys (tools/shadowbench/keys.py) and the cases scorer's ``--keys`` scheme."""

from __future__ import annotations

import json
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from tools.discovery_benchmark.taxonomy import CATEGORIES
from tools.shadowbench import keys
from tools.shadowbench.cases import report, score
from tools.shadowbench.cases.contract import TruthEntity
from tools.shadowbench.cases.corpus import Case, Corpus, dump_corpus, load_corpus

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "benchmarks" / "shadowbench" / "cases"
RUN = CASES / "results" / "2026-10-11"

NAMESPACES = sorted(
    {"app", "artifact", "bot", "caller", "client", "flow", "k8s", "proc", "process"}
    | {
        "resource",
        "service",
        "workflow",
        *CATEGORIES,
    }
)

# --- properties -----------------------------------------------------------------------------------


@settings(max_examples=2000)
@given(st.text())
def test_canonical_is_total_and_idempotent_on_any_text(text: str) -> None:
    once = keys.canonical(text)
    assert keys.canonical(once) == once


@settings(max_examples=1000)
@given(st.sampled_from(NAMESPACES), st.text())
def test_canonical_is_idempotent_and_keeps_the_namespace(namespace: str, value: str) -> None:
    once = keys.canonical(f"{namespace}:{value}")
    assert keys.canonical(once) == once
    if not keys._CONTROL.search(value):
        assert once.startswith(f"{namespace}:")


@given(st.uuids(), st.sampled_from(["app", "bot", "flow"]), st.sampled_from(["{%s}", "urn:uuid:%s", "%s"]))
def test_a_guid_matches_whatever_its_case_and_wrapping(guid: Any, namespace: str, wrap: str) -> None:
    truth = f"{namespace}:{guid}"
    assert keys.canonical(f"{namespace}:{wrap % str(guid).upper()}") == truth


_SEGMENT = st.text(
    alphabet=st.characters(blacklist_characters="/\\\x00", blacklist_categories=("Cc", "Zs")), min_size=1
).filter(lambda s: s not in (".", "..") and s.strip() == s)


@given(st.lists(_SEGMENT, min_size=1, max_size=6), st.sampled_from(["", "./", "~/", "$HOME/"]), st.booleans())
def test_equivalent_spellings_of_a_relative_path_match(segments: list[str], prefix: str, slash: bool) -> None:
    truth = keys.canonical("artifact:" + "/".join(segments))
    spelled = prefix + "/./".join(segments) + ("/" if slash else "")
    assert keys.canonical("artifact:" + spelled) == truth
    assert keys.canonical("artifact:" + spelled.replace("/", "\\")) == truth


@given(st.lists(_SEGMENT, min_size=1, max_size=4))
def test_a_path_keeps_its_case(segments: list[str]) -> None:
    path = unicodedata.normalize("NFC", "/".join(segments))  # NFC may fold compatibility characters
    assert keys.canonical(f"artifact:{path}") == f"artifact:{path}"


_PATH_PART = st.sampled_from(["~", "$HOME", "${HOME}", "..", ".", "", " ", "a", "B", ".claude", "x y"])


@settings(max_examples=3000)
@given(st.lists(_PATH_PART, max_size=24), st.sampled_from(["", "/", "./", "~/", "$HOME/", "\\"]))
def test_canonical_is_idempotent_on_adversarial_paths(parts: list[str], lead: str) -> None:
    """Repeated home prefixes, escapes and whitespace segments once needed more passes than allowed."""
    once = keys.canonical("artifact:" + lead + "/".join(parts))
    assert keys.canonical(once) == once


@given(st.lists(st.sampled_from(["~", "$HOME", "a", "..", "b"]), min_size=1, max_size=8))
def test_a_canonical_path_never_merges_a_directory_named_like_home(parts: list[str]) -> None:
    """``./~/x`` (a directory named ~) and ``x`` are different files and must stay apart."""
    value = keys.canonical("artifact:./" + "/".join(parts)).removeprefix("artifact:")
    # whatever ``..`` resolved away, a path that still starts in a directory named like home says so
    if value.removeprefix("./").split("/")[0] in keys.HOME_TOKENS:
        assert value.startswith("./")


@given(st.ip_addresses(v=4), st.integers(min_value=1, max_value=65535))
def test_service_spellings_of_one_ipv4_endpoint_match(ip: Any, port: int) -> None:
    truth = f"service:{ip}:{port}"
    assert keys.canonical(truth) == truth
    assert keys.canonical(f"service:http://{ip}:{port}/v1/models") == truth
    assert keys.canonical(f"service:{ip}:{port:05d}") == truth


@given(st.ip_addresses(v=6), st.integers(min_value=1, max_value=65535))
def test_ipv6_services_are_bracketed_and_compressed(ip: Any, port: int) -> None:
    exploded = f"service:[{ip.exploded.upper()}]:{port}"
    assert keys.canonical(exploded) == f"service:[{ip.compressed}]:{port}"


# --- rules ----------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("service:localhost:11434", "service:127.0.0.1:11434"),
        ("service:LOCALHOST.:11434", "service:127.0.0.1:11434"),
        ("service:https://localhost/v1", "service:127.0.0.1:443"),
        ("service:http://127.0.0.1", "service:127.0.0.1:80"),
        ("service:ftp://127.0.0.1", "service:ftp://127.0.0.1"),  # no default port to fill in
        ("service:127.0.0.1:70000", "service:127.0.0.1:70000"),  # no such port: left as written
        ("service:0.0.0.0:11434", "service:0.0.0.0:11434"),  # all interfaces is not loopback
        ("client:10.014.103.19", "client:10.014.103.19"),  # leading zeros may mean octal: never folded
        ("client:10.14.103.19 ", "client:10.14.103.19"),
        ("process:007", "process:7"),
        ("proc:0", "proc:0"),
        (
            "resource:ARN:AWS:Bedrock:US-EAST-1:123456789012:agent/AbC",
            "resource:arn:aws:bedrock:us-east-1:123456789012:agent/AbC",
        ),
        (
            "caller:arn:aws:sts::123456789012:assumed-role/BatchRole/x",
            "caller:arn:aws:sts::123456789012:assumed-role/BatchRole/x",
        ),
        ("caller:Alice-Dev", "caller:Alice-Dev"),  # a gateway user name keeps its case
        (
            "resource:/subscriptions/ABC/resourceGroups/RG/providers/Microsoft.CognitiveServices/accounts/Foo",
            "resource:/subscriptions/abc/resourcegroups/rg/providers/microsoft.cognitiveservices/accounts/foo",
        ),
        ("k8s:AI/deployment/Flowise-2a", "k8s:ai/Deployment/flowise-2a"),
        ("k8s:ai/MyCustomKind/x", "k8s:ai/MyCustomKind/x"),
        ("k8s:ai/Deployment", "k8s:ai/Deployment"),
        ("app:0oa7jf08kbsdan7lysvw", "app:0oa7jf08kbsdan7lysvw"),
        ("app:A0123ABCDEF", "app:A0123ABCDEF"),  # an opaque id keeps its case
        ("workflow:02ac1b64b04cfe83", "workflow:02ac1b64b04cfe83"),
        ("Framework:Lang_Graph", "framework:lang-graph"),
        ("provider:Azure OpenAI", "provider:azure-openai"),
        ("artifact:../outside", "artifact:../outside"),  # leaves the root: never rewritten into a match
        ("artifact:a/../../b", "artifact:../b"),  # the climb out is kept, so it lies inside nothing
        ("artifact:.openclaw/../../.cursor/mcp.json", "artifact:../.cursor/mcp.json"),
        ("artifact:./~/.openclaw/x", "artifact:./~/.openclaw/x"),  # a directory named ~, not home
        ("artifact:~/~/x", "artifact:./~/x"),
        ("artifact:~/$HOME/.openclaw/config.json", "artifact:./$HOME/.openclaw/config.json"),
        ("artifact:~//.aws/amazonq/mcp.json", "artifact:.aws/amazonq/mcp.json"),  # home-relative
        ("artifact:/../etc/x", "artifact:/etc/x"),
        ("artifact:x/ / / / / / / / / / ", "artifact:x"),
        ("process:" + "1" * 5000, "process:" + "1" * 5000),  # beyond int()'s digit limit
        ("process:000", "process:0"),
        ("artifact:.claude/../.cursor/mcp.json", "artifact:.cursor/mcp.json"),
        ("artifact:/abs/path/", "artifact:/abs/path"),
        ("no-namespace", "no-namespace"),
        (":empty", ":empty"),
        ("app:\x00weird", "app:\x00weird"),
        ("artifact:café", "artifact:café"),  # NFC
    ],
)
def test_rules(key: str, expected: str) -> None:
    assert keys.canonical(key) == expected


def test_exact_is_the_identity() -> None:
    assert keys.scheme("exact")("service:localhost:1") == "service:localhost:1"
    with pytest.raises(ValueError, match="unknown key scheme"):
        keys.scheme("fuzzy")


def test_collisions_name_every_merged_key() -> None:
    assert keys.collisions(["app:A", "app:a", "service:localhost:1", "service:127.0.0.1:1"]) == {
        "service:127.0.0.1:1": ["service:127.0.0.1:1", "service:localhost:1"]
    }


def test_the_committed_corpus_is_canonical_and_merges_nothing() -> None:
    corpus = load_corpus(CASES / "corpus.json")
    assert keys.corpus_problems(corpus.cases) == []
    assert keys.non_canonical(corpus.cases) == []


def test_check_cli_reports_collisions(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "corpus.json"
    dump_corpus(
        Corpus([_case("c1", decoys=["service:localhost:1", "service:127.0.0.1:1"])], 1, "g", "t"), path
    )
    assert keys.main(["check", "--corpus", str(path)]) == 1
    captured = capsys.readouterr()
    assert "c1: service:127.0.0.1:1, service:localhost:1 share the canonical form" in captured.err
    assert "note: truth key not in canonical form: c1: service:localhost:1" in captured.out


# --- scorer integration ---------------------------------------------------------------------------


def _case(cid: str, expected: tuple[tuple[str, str], ...] = (), decoys: list[str] | None = None) -> Case:
    return Case(
        cid,
        "identity",
        "okta-export",
        "test-family",
        "easy",
        "unit test",
        expected=[TruthEntity(k.split(":", 1)[0], k, label, {}, "planted") for k, label in expected],
        tolerated=[],
        decoys=decoys or [],
    )


def _results(tmp_path: Path, cases: list[Case], entities: dict[str, list[str]]) -> tuple[Path, Path]:
    corpus_path = tmp_path / "corpus.json"
    digest = dump_corpus(Corpus(cases, 1, "generator", "2026-10-11T00:00:00Z"), corpus_path)
    results = tmp_path / "results"
    results.mkdir()
    rows = [
        {
            "tool": "t",
            "case": c.case_id,
            "surface": c.surface,
            "modality": c.modality,
            "family": c.family,
            "label": c.label,
            "difficulty": c.difficulty,
            "status": "ok",
            "entities": [
                {"kind": "service", "key": k, "label": "agent"} for k in entities.get(c.case_id, [])
            ],
            "note": "",
            "seconds": 0.1,
            "incomplete": False,
        }
        for c in cases
    ]
    (results / "t.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    manifest = {
        "corpus_sha256": digest,
        "tools": {"t": {"version": "1", "statuses": dict(Counter(r["status"] for r in rows))}},
    }
    (results / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return corpus_path, results


def _metrics(tmp_path: Path, corpus_path: Path, results: Path, *extra: str) -> dict[str, Any]:
    out = tmp_path / f"metrics{len(extra)}.json"
    assert (
        score.main(["--corpus", str(corpus_path), "--results", str(results), "--out", str(out), *extra]) == 0
    )
    loaded: dict[str, Any] = json.loads(out.read_text(encoding="utf-8"))
    return loaded


def test_canonical_keys_credit_a_finding_exact_keys_score_twice_against(tmp_path: Path) -> None:
    pos = _case("p1", expected=(("service:127.0.0.1:11434", "agent"),), decoys=["service:127.0.0.1:8080"])
    corpus_path, results = _results(
        tmp_path, [pos], {"p1": ["service:localhost:11434", "service:LOCALHOST:11434"]}
    )
    exact = _metrics(tmp_path, corpus_path, results)["tools"]["t"]["in_scope"]
    assert (exact["tp"], exact["fp"], exact["fn"]) == (0, 2, 1)
    canonical = _metrics(tmp_path, corpus_path, results, "--keys", "canonical-v1")
    assert canonical["key_scheme"] == "canonical-v1"
    i = canonical["tools"]["t"]["in_scope"]
    # both spellings are one entity, found once
    assert (i["tp"], i["fp"], i["fn"]) == (1, 0, 0)


def test_a_canonical_decoy_hit_counts_against_specificity(tmp_path: Path) -> None:
    neg = _case("n1", decoys=["service:127.0.0.1:8080"])
    corpus_path, results = _results(tmp_path, [neg], {"n1": ["service:http://localhost:8080/"]})
    i = _metrics(tmp_path, corpus_path, results, "--keys", "canonical-v1")["tools"]["t"]["in_scope"]
    assert (i["fp"], i["tn"], i["decoys"]) == (1, 0, 1)


def test_a_scheme_that_merges_truth_keys_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    neg = _case("n1", decoys=["service:localhost:1", "service:127.0.0.1:1"])
    corpus_path, results = _results(tmp_path, [neg], {})
    out = tmp_path / "m.json"
    args = [
        "--corpus",
        str(corpus_path),
        "--results",
        str(results),
        "--out",
        str(out),
        "--keys",
        "canonical-v1",
    ]
    assert score.main(args) == 2
    assert "merges truth keys" in capsys.readouterr().err
    assert not out.exists()
    # the exact scheme compares them as written and scores
    assert score.main(args[:-2]) == 0


@pytest.mark.parametrize("scheme", [(), ("--keys", "canonical-v1")])
def test_a_path_that_climbs_out_of_a_truth_directory_is_not_inside_it(
    tmp_path: Path, scheme: tuple[str, ...]
) -> None:
    pos = Case(
        "e1",
        "endpoint",
        "home",
        "test-family",
        "easy",
        "unit test",
        expected=[TruthEntity("artifact", "artifact:.openclaw", "agent", {}, "planted")],
        tolerated=[],
        decoys=[],
        files={"home/.openclaw/x": "{}"},
    )
    corpus_path, results = _results(tmp_path, [pos], {"e1": ["artifact:.openclaw/../../.cursor/mcp.json"]})
    i = _metrics(tmp_path, corpus_path, results, *scheme)["tools"]["t"]["in_scope"]
    assert (i["tp"], i["fp"], i["fn"]) == (0, 1, 1)


@pytest.mark.parametrize("scheme", [(), ("--keys", "canonical-v1")])
@pytest.mark.parametrize("order", [("llm", "agent"), ("agent", "llm")])
def test_the_agent_tier_does_not_depend_on_report_order(
    tmp_path: Path, scheme: tuple[str, ...], order: tuple[str, str]
) -> None:
    """De-duplicating by first report let report order decide agent credit and agent false alarms."""
    pos = _case("p1", expected=(("service:127.0.0.1:11434", "agent"), ("service:127.0.0.1:8080", "llm")))
    spellings = (
        [
            "service:127.0.0.1:11434",
            "service:127.0.0.1:11434",
            "service:127.0.0.1:8080",
            "service:127.0.0.1:8080",
        ]
        if not scheme
        else [
            "service:localhost:11434",
            "service:127.0.0.1:11434",
            "service:localhost:8080",
            "service:127.0.0.1:8080",
        ]
    )
    corpus_path, results = _results(tmp_path, [pos], {})
    rows = [json.loads(line) for line in (results / "t.jsonl").read_text(encoding="utf-8").splitlines()]
    labels = [order[0], order[1], order[0], order[1]]
    rows[0]["entities"] = [
        {"kind": "service", "key": k, "label": lab} for k, lab in zip(spellings, labels, strict=True)
    ]
    (results / "t.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    i = _metrics(tmp_path, corpus_path, results, *scheme)["tools"]["t"]["in_scope"]
    assert i["agent_recall"] == 1.0
    assert i["agent_false_alarm_rate"] == 1.0  # the llm entity was called an agent by one report


def test_the_committed_run_scores_the_same_under_canonical_keys(tmp_path: Path) -> None:
    """canonical-v1 changes no published number: the 2026-10-11 adapters already wrote canonical keys."""
    metrics = _metrics(tmp_path, CASES / "corpus.json", RUN, "--keys", "canonical-v1")
    assert metrics.pop("key_scheme") == "canonical-v1"
    assert metrics == json.loads((RUN / "metrics.json").read_text(encoding="utf-8"))


def test_the_report_names_a_non_default_scheme(tmp_path: Path) -> None:
    pos = _case("p1", expected=(("service:127.0.0.1:1", "agent"),))
    corpus_path, results = _results(tmp_path, [pos], {"p1": ["service:localhost:1"]})
    metrics = _metrics(tmp_path, corpus_path, results, "--keys", "canonical-v1")
    assert "`canonical-v1` scheme" in report.render(metrics, corpus_path)
    assert "scheme" not in report.render(_metrics(tmp_path, corpus_path, results), corpus_path)
