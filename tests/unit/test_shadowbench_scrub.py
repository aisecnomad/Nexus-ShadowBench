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
    assert [f.kind for f in scrub.findings(line)] == [kind]


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
    (results / "rows.jsonl").write_text("{}\n", encoding="utf-8")
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
    corpus = scrub.corpus_matches(corpora)
    targets, problems = scrub.files(results)
    assert problems == [] and targets
    left = [
        (path, finding.path)
        for path in targets
        for finding in scrub.findings(path.read_text(encoding="utf-8"))
        if not scrub.echoed(finding.path, corpus)
    ]
    assert left == []


# --- review regressions ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "/var/tmp/cache/x",
        "/private/tmp/y",
        "https://x.example/tmp/a",
        "/srv/mirror/tmp/z",
    ],
)
def test_a_mapped_path_is_never_replaced_inside_a_longer_path(text: str) -> None:
    """Only a lookahead bounded the match, so /tmp was replaced inside /var/tmp and URLs."""
    assert scrub.scrub_text(text, scrub.parse_map(["/tmp=<tmp>"])) == (text, 0)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ('{"n": "boom\\n/tmp/x"}', '{"n": "boom\\n<tmp>/x"}'),
        ("--out=/tmp/x", "--out=<tmp>/x"),
        ("PATH=/usr/bin:/tmp/x", "PATH=/usr/bin:<tmp>/x"),
        ("\x1b[0m/tmp/x", "\x1b[0m<tmp>/x"),
    ],
)
def test_a_mapped_path_after_an_escape_or_separator_is_replaced(text: str, expected: str) -> None:
    assert scrub.scrub_text(text, scrub.parse_map(["/tmp=<tmp>"]))[0] == expected


@pytest.mark.parametrize(
    "line",
    [
        '{"n": "a\\n/home/alice/x"}',
        '{"n": "x\\t/tmp/nsb-run-1234/raw"}',
        "\x1b[0m/home/alice/x",
        '"/var/home/alice/nsb/tools"',
        '"/mnt/c/Users/alice/AppData"',
        '"/System/Volumes/Data/Users/alice/x"',
        '{"note": "cannot open /root\\nTraceback"}',
        '{"PATH": "/root:/usr/bin"}',
        "stat /root, permission denied",
    ],
)
def test_check_finds_paths_after_escapes_and_under_prefixed_homes(line: str) -> None:
    assert list(scrub.findings(line)), line


def test_the_corpus_exempts_its_own_paths_not_others_under_the_same_home(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.json"
    corpus.write_text('{"cwd": "/home/jenkins/agent/tools/x"}', encoding="utf-8")
    exempt = scrub.corpus_matches([corpus])
    assert scrub.echoed("/home/jenkins/agent/tools/x", exempt)
    assert scrub.echoed("/home/jenkins", exempt)  # an ancestor directory the corpus names
    assert scrub.echoed("/home/jenkins/agent/to", exempt)  # cut short by a report
    assert not scrub.echoed("/home/jenkins/workspace/nsb/tools/bin/x", exempt)
    assert not scrub.echoed("/home/jenk", exempt)


def test_apply_keeps_line_endings(tmp_path: Path) -> None:
    path = tmp_path / "rows.csv"
    path.write_bytes(b"x,/opt/nsb/tools/bin/x\r\ny,z\r\n")
    assert scrub.main(["apply", "--map", "/opt/nsb/tools=<tools>", str(path)]) == 0
    assert path.read_bytes() == b"x,<tools>/bin/x\r\ny,z\r\n"


@pytest.mark.parametrize("command", ["check", "apply"])
def test_a_missing_or_unusable_path_fails_instead_of_passing(tmp_path: Path, command: str) -> None:
    binary = tmp_path / "blob.bin"
    binary.write_bytes(b"\0")
    extra = ["--map", "/opt/x=<tools>"] if command == "apply" else []
    assert scrub.main([command, *extra, str(tmp_path / "missing")]) == 2
    assert scrub.main([command, *extra, str(binary)]) == 2
    empty = tmp_path / "empty"
    empty.mkdir()
    assert scrub.main([command, *extra, str(empty)]) == 2


def test_apply_replaces_the_host_name(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(scrub.socket, "gethostname", lambda: "build-host-7")
    path = tmp_path / "manifest.json"
    path.write_text('{"node": "ci@build-host-7", "other": "build-host-77"}', encoding="utf-8")
    assert scrub.main(["apply", "--host", str(path)]) == 0
    assert path.read_text(encoding="utf-8") == '{"node": "ci@<host>", "other": "build-host-77"}'
    monkeypatch.setattr(scrub.socket, "gethostname", lambda: "vm")
    assert scrub.main(["apply", "--host", str(path)]) == 2


@pytest.mark.parametrize(
    "uri", ["file:///home/alice/proj/a.py", "file://localhost/home/alice/a.py", "file:///tmp/build-1/x.py"]
)
def test_a_path_in_a_file_uri_is_found_and_scrubbed(uri: str) -> None:
    """SARIF writes locations as file:// URIs, and the path after the third slash was never seen."""
    text = json.dumps({"artifactLocation": {"uri": uri}})
    assert list(scrub.findings(text))
    scrubbed, count = scrub.scrub_text(text, {"/home/alice": "<home>", "/tmp": "<tmp>"})
    assert count == 1 and not list(scrub.findings(scrubbed))


def test_urls_and_placeholder_relative_paths_are_still_not_machine_paths() -> None:
    assert not list(scrub.findings('{"a": "https://example.com/home/x", "b": "<estate>/home/dana/x"}'))


def test_a_directory_walk_reads_sarif_and_upper_case_suffixes(tmp_path: Path) -> None:
    for name in ("scan.sarif", "REPORT.JSON"):
        (tmp_path / name).write_text('{"uri": "file:///home/alice/x"}\n', encoding="utf-8")
    found, problems = scrub.files([tmp_path])
    assert sorted(p.name for p in found) == ["REPORT.JSON", "scan.sarif"] and problems == []
