"""tools/check_secrets_extra.py: the families and encodings tools/check_secrets.py cannot see.

Every credential-shaped value here is assembled at run time, so this file holds none for either
scanner to report.
"""

from __future__ import annotations

import codecs
import gzip
import hashlib
import json
import tarfile
from pathlib import Path

import pytest

from tools import check_secrets, check_secrets_extra

ROOT = Path(__file__).resolve().parents[2]

SAMPLES = {
    "Anthropic OAuth token": "sk-ant-" + "oat01-" + "A" * 40,
    "OpenRouter API key": "sk-" + "or-v1-" + "0" * 64,
    "Groq API key": "gsk" + "_" + "a1" * 26,
    "xAI API key": "xai" + "-" + "B" * 80,
    "Replicate API token": "r8" + "_" + "c" * 37,
    "Perplexity API key": "pplx" + "-" + "d" * 48,
    "PyPI API token": "pypi" + "-AgEIcHlwaS5vcmc" + "e" * 60,
    "npm access token": "npm" + "_" + "F" * 36,
    "Docker personal access token": "dckr" + "_pat_" + "g" * 27,
    "Slack app token": "xapp" + "-1-A0B1C2D3E4F-1234567890123-" + "ab" * 32,
    "Slack webhook URL": "https://hooks.slack.com/" + "services/T0AAAAAAA/B0BBBBBBB/" + "h" * 24,
    "Slack webhook URL (trigger)": "https://hooks.slack.com/"
    + "triggers/T0AAAAAAA/4567890123456/"
    + "0f" * 16,
    "Google OAuth client secret": "GOCSPX" + "-" + "i" * 28,
    "Google OAuth access token": "ya29" + "." + "j" * 40,
    "SendGrid API key": "SG" + "." + "k" * 22 + "." + "m" * 43,
}
GITHUB = "ghp" + "_" + "n" * 36  # a family check_secrets.py knows


def _families(contents: bytes) -> list[str]:
    return [family for _, family, _ in check_secrets_extra.findings(contents)]


@pytest.mark.parametrize("family", sorted(SAMPLES))
def test_each_extra_family_is_found_where_check_secrets_finds_nothing(family: str) -> None:
    text = f'config = {{"token": "{SAMPLES[family]}"}}\n'
    assert _families(text.encode()) == [family.removesuffix(" (trigger)")]
    assert list(check_secrets.findings(text)) == []


def test_plain_text_is_left_to_check_secrets_for_its_own_families() -> None:
    assert _families(f"token = {GITHUB}\n".encode()) == []


@pytest.mark.parametrize(
    "encode",
    [
        lambda text: gzip.compress(text.encode()),
        lambda text: gzip.compress(text.encode()) + gzip.compress(b"second member\n"),
        lambda text: codecs.BOM_UTF16_LE + text.encode("utf-16-le"),
        lambda text: codecs.BOM_UTF16_BE + text.encode("utf-16-be"),
        lambda text: text.encode("utf-16-le"),
        lambda text: codecs.BOM_UTF32_LE + text.encode("utf-32-le"),
        lambda text: gzip.compress(codecs.BOM_UTF16_LE + text.encode("utf-16-le")),
    ],
    ids=["gzip", "gzip-members", "utf16le-bom", "utf16be-bom", "utf16le-bare", "utf32le-bom", "gzip-utf16"],
)
def test_what_check_secrets_cannot_decode_is_scanned_for_every_family(encode: object) -> None:
    """check_secrets.py read these as UTF-8 and dropped the rest: a token inside passed unseen."""
    text = f"line one\ntoken = {GITHUB}\nkey = {SAMPLES['Groq API key']}\n"
    contents = encode(text)  # type: ignore[operator]
    assert list(check_secrets.findings(contents.decode("utf-8", errors="ignore"))) == []
    found = list(check_secrets_extra.findings(contents))
    assert [(line, family) for line, family, _ in found] == [(2, "GitHub token"), (3, "Groq API key")]


def test_a_corrupt_or_oversized_gzip_member_is_reported_not_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    corrupt = tmp_path / "corrupt.jsonl.gz"
    corrupt.write_bytes(gzip.compress(b"payload\n")[:10] + b"\xff" * 16)
    truncated = tmp_path / "truncated.jsonl.gz"
    truncated.write_bytes(gzip.compress(f"key = {GITHUB}\n".encode() * 5)[:-12])
    big = tmp_path / "big.jsonl.gz"
    big.write_bytes(gzip.compress(b"x" * 4096))
    monkeypatch.setattr(check_secrets_extra, "MAX_DECOMPRESSED", 1024)
    assert check_secrets_extra.main([str(corrupt), str(truncated), str(big)]) == 1
    err = capsys.readouterr().err
    assert "corrupt.jsonl.gz: cannot scan: corrupt gzip member" in err
    assert "truncated.jsonl.gz: cannot scan: truncated gzip member" in err  # zlib itself raises nothing
    assert "big.jsonl.gz: cannot scan: gzip layers inflate past 1024 bytes" in err


def test_a_finding_reports_the_family_and_length_never_the_value(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "leak.txt"
    path.write_text(f"\n{SAMPLES['OpenRouter API key']}\n", encoding="utf-8")
    assert check_secrets_extra.main([str(path)]) == 1
    out = capsys.readouterr().out
    assert out == f"{path}:2: possible hardcoded OpenRouter API key: sk-o... (73 characters)\n"
    assert SAMPLES["OpenRouter API key"] not in out


def test_no_files_is_an_error() -> None:
    assert check_secrets_extra.main([]) == 2


def _with_allowlist(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, entries: list[dict[str, str]]) -> None:
    path = tmp_path / "allow.json"
    path.write_text(json.dumps({"version": 1, "entries": entries}), encoding="utf-8")
    monkeypatch.setattr(check_secrets_extra, "ALLOWLIST_PATH", path)


def test_an_approval_binds_path_family_and_digest_and_a_stale_one_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fixture = ROOT / "tests" / "unit" / "test_check_secrets_extra.py"  # holds no assembled value
    value = SAMPLES["Groq API key"]
    entry = {"path": "x.txt", "family": "Groq API key", "sha256": check_secrets.digest(value), "reason": "r"}
    _with_allowlist(monkeypatch, tmp_path, [entry])
    assert check_secrets_extra.main([str(fixture)]) == 1
    assert "approved fixture is missing" in capsys.readouterr().err
    _with_allowlist(monkeypatch, tmp_path, [{**entry, "path": "tests/unit/test_check_secrets_extra.py"}])
    assert check_secrets_extra.main([str(fixture)]) == 1
    assert "stale approval" in capsys.readouterr().err
    _with_allowlist(monkeypatch, tmp_path, [{**entry, "family": "Not a family"}])
    assert check_secrets_extra.main([str(fixture)]) == 1
    assert "unknown family" in capsys.readouterr().err


def test_the_allowlist_starts_empty() -> None:
    """Nothing tracked matched an extra family or a decoded file when this scanner was added; CI and
    `make secrets` scan every tracked file."""
    assert json.loads(check_secrets_extra.ALLOWLIST_PATH.read_text(encoding="utf-8")) == {
        "version": 1,
        "entries": [],
    }


def _tar(tmp_path: Path, text: str) -> bytes:
    source = tmp_path / "a.txt"
    source.write_text(text, encoding="utf-8")
    archive = tmp_path / "a.tar"
    with tarfile.open(archive, "w") as handle:
        handle.add(source, arcname="a.txt")
    return archive.read_bytes()


def test_tar_archives_are_read_through_their_nul_padding(tmp_path: Path) -> None:
    """A tar's NUL padding sent it down the UTF-16 path, where nothing matched; gzipped, neither
    scanner saw anything in it."""
    tar = _tar(tmp_path, f"token = {GITHUB}\nkey = {SAMPLES['Groq API key']}\n")
    assert _families(tar) == ["Groq API key"]  # check_secrets.py reports the GitHub token itself
    assert sorted(_families(gzip.compress(tar))) == ["GitHub token", "Groq API key"]


@pytest.mark.parametrize("encoding", ["utf-32-le", "utf-32-be", "utf-16-le", "utf-16-be"])
def test_wide_text_without_a_bom_or_with_a_non_latin_start_is_read(encoding: str) -> None:
    text = "漢字" * 3000 + f"\nkey = {SAMPLES['Groq API key']}\n"
    assert _families(text.encode(encoding)) == ["Groq API key"]


def test_deep_or_large_gzip_nesting_is_reported_not_a_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each layer recursed, so 2000 layers raised RecursionError; the size limit was per layer."""
    nested = b"x\n"
    for _ in range(check_secrets_extra.MAX_GZIP_DEPTH + 1):
        nested = gzip.compress(nested, mtime=0)
    with pytest.raises(check_secrets_extra.Unscannable, match="deeper than"):
        list(check_secrets_extra.findings(nested))
    monkeypatch.setattr(check_secrets_extra, "MAX_DECOMPRESSED", 3000)
    two = gzip.compress(gzip.compress(b"y" * 2000, mtime=0) + b"z" * 2000, mtime=0)  # 2 layers, ~4 KB in all
    with pytest.raises(check_secrets_extra.Unscannable, match="inflate past 3000"):
        list(check_secrets_extra.findings(two))


def _approved_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data: bytes, **entry: str) -> Path:
    fixture = tmp_path / "fixture.txt"
    fixture.write_bytes(data)
    monkeypatch.setattr(check_secrets, "REPOSITORY_ROOT", tmp_path)
    _with_allowlist(monkeypatch, tmp_path, [{"path": "fixture.txt", "reason": "synthetic", **entry}])
    return fixture


def test_an_approval_suppresses_exactly_its_finding(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    value = SAMPLES["Groq API key"]
    data = f"key = {value}\nother = {SAMPLES['xAI API key']}\n".encode()
    fixture = _approved_repo(
        tmp_path, monkeypatch, data, family="Groq API key", sha256=check_secrets.digest(value)
    )
    assert check_secrets_extra.main([str(fixture)]) == 1  # the xAI key is not approved
    fixture.write_bytes(f"key = {value}\n".encode())
    assert check_secrets_extra.main([str(fixture)]) == 0


def test_a_private_key_approval_binds_the_whole_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A marker is the same for every key; approving it alone would pass any key body."""
    marker = "-----BEGIN " + "PRIVATE KEY-----"
    data = gzip.compress(f"{marker}\nAAAA\n".encode())
    entry = {"family": "private key", "sha256": check_secrets.digest(marker)}
    fixture = _approved_repo(tmp_path, monkeypatch, data, **entry)
    assert check_secrets_extra.main([str(fixture)]) == 1  # no content_sha256: the approval is refused
    _with_allowlist(
        monkeypatch,
        tmp_path,
        [
            {
                "path": "fixture.txt",
                "reason": "synthetic",
                **entry,
                "content_sha256": hashlib.sha256(data).hexdigest(),
            }
        ],
    )
    assert check_secrets_extra.main([str(fixture)]) == 0
    fixture.write_bytes(gzip.compress(f"{marker}\nBBBB\n".encode()))
    assert check_secrets_extra.main([str(fixture)]) == 1  # another key body behind the same marker


@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "utf-16-be", "utf-32", "utf-32-le", "utf-32-be"])
def test_a_token_beside_cjk_punctuation_in_wide_text_is_found(encoding: str) -> None:
    """With only the NULs dropped, the bytes of 「 and 」 ran into the token and broke its boundaries."""
    text = f"鍵「{SAMPLES['Groq API key']}」。\n"
    assert _families(text.encode(encoding)) == ["Groq API key"]


def test_a_gzip_member_inside_a_tar_is_inflated(tmp_path: Path) -> None:
    inner = tmp_path / "secrets.json.gz"
    inner.write_bytes(gzip.compress(f"key = {GITHUB}\nother = {SAMPLES['xAI API key']}\n".encode()))
    archive = tmp_path / "bundle.tar"
    with tarfile.open(archive, "w") as handle:
        handle.add(inner, arcname="secrets.json.gz")
    assert sorted(_families(archive.read_bytes())) == ["GitHub token", "xAI API key"]
    assert sorted(_families(gzip.compress(archive.read_bytes()))) == ["GitHub token", "xAI API key"]
