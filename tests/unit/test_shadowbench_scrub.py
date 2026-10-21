"""Publishing scrubber (tools/shadowbench/scrub.py): placeholders in, machine paths out."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tools.shadowbench import scrub

ROOT = Path(__file__).resolve().parents[2]


def test_apply_replaces_mapped_paths_at_boundaries_only(tmp_path: Path) -> None:
    record = {
        "bin": "/opt/tools/venvs/x/bin/x",
        "sibling": "/opt/tools2/bin/y",
        "exact": "/opt/tools",
        "work": "/srv/run-17/work/case-1",
        "argv": ["--root", "/opt/tools/share", "--out=/srv/run-17/out"],
    }
    path = tmp_path / "runs.json"
    path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    mapping = scrub.parse_map(["/opt/tools=<tools>", "/srv/run-17/=<run>"])
    assert scrub.main(["apply", "--map", "/opt/tools=<tools>", "--map", "/srv/run-17/=<run>", str(path)]) == 0
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "bin": "<tools>/venvs/x/bin/x",
        "sibling": "/opt/tools2/bin/y",
        "exact": "<tools>",
        "work": "<run>/work/case-1",
        "argv": ["--root", "<tools>/share", "--out=<run>/out"],
    }
    # only the replaced paths changed: re-serializing gives the same bytes
    assert (
        path.read_text(encoding="utf-8")
        == json.dumps(json.loads(path.read_text(encoding="utf-8")), indent=1) + "\n"
    )
    assert scrub.scrub_text(path.read_text(encoding="utf-8"), mapping)[1] == 0


def test_the_longest_mapped_path_wins() -> None:
    mapping = scrub.parse_map(["/opt/tools=<tools>", "/opt/tools/venvs=<venvs>"])
    assert scrub.scrub_text("/opt/tools/venvs/a /opt/tools/bin", mapping) == ("<venvs>/a <tools>/bin", 2)


def test_json_escaped_paths_are_replaced() -> None:
    mapping = scrub.parse_map(["C:\\Users\\op\\tools=<tools>"])
    text = json.dumps({"bin": "C:\\Users\\op\\tools\\x.exe"})
    assert json.loads(scrub.scrub_text(text, mapping)[0]) == {"bin": "<tools>\\x.exe"}


@pytest.mark.parametrize(
    ("item", "message"),
    [
        ("/opt/tools", "PATH=<token>"),
        ("/opt/tools=<secret>", "unknown placeholder"),
        ("relative/path=<tools>", "not an absolute path"),
        ("/=<tools>", "root directory"),
    ],
)
def test_bad_maps_are_refused(item: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        scrub.parse_map([item])


@given(st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=200))
def test_scrubbing_text_without_the_path_changes_nothing(text: str) -> None:
    mapping = scrub.parse_map(["/opt/shadowbench-unlikely-root=<tools>"])
    if "/opt/shadowbench-unlikely-root" not in text:
        assert scrub.scrub_text(text, mapping) == (text, 0)


@pytest.mark.parametrize(
    ("line", "kind"),
    [
        ('"bin": "/home/alice/tools/x"', "home directory"),
        ('"cwd": "/root"', "home directory"),
        ('"p": "/Users/alice/x"', "home directory"),
        ('"p": "C:\\\\Users\\\\alice\\\\x"', "Windows profile"),
        ('"scratch": "/tmp/shadowbench-ab12cd/work"', "temporary path"),
        ('"p": "/var/folders/xy/T/"', "temporary path"),
        ('"p": "/run/user/1000/bus"', "temporary path"),
    ],
)
def test_check_finds_machine_paths(line: str, kind: str) -> None:
    assert [k for _, k, _ in scrub.findings(line)] == [kind]


@pytest.mark.parametrize(
    "line",
    [
        '"text": "<estate>/home/dev-laptop-01/dana/.cursor/mcp.json"',
        '"bin": "<tools>/venvs/x/bin/x"',
        '"artifact": "artifact:.config/home/x"',
        '"note": "/opt/node22/bin"',
        '"tmp": "<tmp>/x"',
    ],
)
def test_check_accepts_placeholders_and_relative_paths(line: str) -> None:
    assert list(scrub.findings(line)) == []


def test_check_skips_paths_the_corpus_itself_holds(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "mcp.json").write_text('{"command": "/home/dana/tools/server"}', encoding="utf-8")
    results = tmp_path / "results"
    results.mkdir()
    (results / "runs.json").write_text(
        '{"text": "/home/dana/tools/server", "cwd": "/home/op/run"}\n', encoding="utf-8"
    )
    assert scrub.main(["check", "--corpus", str(corpus), str(results)]) == 1
    out = capsys.readouterr()
    assert "/home/op" in out.out and "/home/dana" not in out.out
    assert "1 finding(s); 1 corpus path(s) echoed by tools" in out.err


def test_check_with_identity_finds_the_host_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scrub, "identity", lambda: ["build-host-7"])
    path = tmp_path / "manifest.json"
    path.write_text('{"node": "ci@build-host-7"}\n', encoding="utf-8")
    assert scrub.main(["check", str(path)]) == 0
    assert scrub.main(["check", "--identity", str(path)]) == 1


def test_check_never_follows_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside.json"
    outside.write_text('"/home/op/secret"', encoding="utf-8")
    results = tmp_path / "results"
    results.mkdir()
    (results / "link.json").symlink_to(outside)
    assert scrub.main(["check", str(results)]) == 0


def test_the_committed_results_are_scrubbed() -> None:
    corpora = [
        ROOT / "benchmarks/shadowbench/estate/artifacts",
        ROOT / "benchmarks/shadowbench/cases/corpus.json",
        ROOT / "benchmarks/shadow-ai-discovery/corpus.json",
    ]
    results = [
        ROOT / "benchmarks/shadow-ai-discovery/results",
        ROOT / "benchmarks/shadowbench/cases/results",
        ROOT / "benchmarks/shadowbench/estate/results",
    ]
    echoed = scrub.corpus_matches(corpora)
    left = [
        (path, match)
        for path in scrub.files(results)
        for _, _, match in scrub.findings(path.read_text(encoding="utf-8"))
        if match not in echoed
    ]
    assert left == []
