"""Credential checks that tools/check_secrets.py does not make, run beside it.

Usage: python tools/check_secrets_extra.py FILE [FILE ...]
       git ls-files -z | xargs -0 python tools/check_secrets_extra.py

``check_secrets.py`` is bound byte for byte in MIGRATION.json and is not
amendable, so what it misses is checked here instead:

* credential families it does not know (:data:`EXTRA_PATTERNS`: AI provider
  keys, package registry and container tokens, Slack app tokens and webhooks,
  Google OAuth secrets, SendGrid), in every file;
* every family, its own and these, in what it cannot read: it decodes all
  bytes as UTF-8 and drops the rest, so a gzip member stays compressed and
  UTF-16 or UTF-32 text keeps a NUL between characters, and neither can match.
  Such files are decoded here (gzip up to :data:`MAX_DECOMPRESSED` bytes; a
  larger member is reported, not skipped) and scanned again.

Reports and exit codes follow ``check_secrets.py``: each finding names the file,
line, family, first four characters and length, never the value; exit 1 on an
unapproved finding, an unreadable file or a bad approval, 2 when no file is
named. Approvals live in secret_allowlist_extra.json and bind exactly as
``check_secrets.py``'s do: normalized repository path, family, the match's
SHA-256 and a review reason; an approval that matches nothing fails closed.
"""

from __future__ import annotations

import codecs
import json
import os
import re
import sys
import zlib
from collections.abc import Iterator, Sequence
from pathlib import Path, PurePosixPath

if __package__ in (None, ""):  # run as a script, as the pre-commit hook and CI do
    sys.path.insert(0, str(Path(__file__).absolute().parent.parent))

from tools import check_secrets

ALLOWLIST_PATH = Path(__file__).with_name("secret_allowlist_extra.json")
MAX_DECOMPRESSED = 256 << 20
"""The most a gzip member is inflated to; the repository's largest is under 5 MiB."""

_END = r"(?![A-Za-z0-9_])"
EXTRA_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Anthropic OAuth token", re.compile(r"(?<![\w-])sk-ant-o[a-z]{2}\d{2}-[A-Za-z0-9_-]{20,}")),
    ("OpenRouter API key", re.compile(r"(?<![\w-])sk-or-v1-[A-Za-z0-9]{32,}")),
    ("Groq API key", re.compile(r"(?<![\w])gsk_[A-Za-z0-9]{40,}" + _END)),
    ("xAI API key", re.compile(r"(?<![\w-])xai-[A-Za-z0-9]{40,}" + _END)),
    ("Replicate API token", re.compile(r"(?<![\w])r8_[A-Za-z0-9]{30,}" + _END)),
    ("Perplexity API key", re.compile(r"(?<![\w-])pplx-[A-Za-z0-9]{40,}" + _END)),
    ("PyPI API token", re.compile(r"(?<![\w-])pypi-AgE[A-Za-z0-9_-]{50,}")),
    ("npm access token", re.compile(r"(?<![\w])npm_[A-Za-z0-9]{36}" + _END)),
    ("Docker personal access token", re.compile(r"(?<![\w])dckr_pat_[A-Za-z0-9_-]{20,}")),
    ("Slack app token", re.compile(r"(?<![\w-])xapp-\d-[A-Z0-9]+-\d+-[a-f0-9]{20,}")),
    (
        "Slack webhook URL",
        re.compile(r"https://hooks\.slack\.com/(?:services|workflows)/T[A-Z0-9]+/[A-Z0-9]+/[A-Za-z0-9]{20,}"),
    ),
    ("Google OAuth client secret", re.compile(r"(?<![\w-])GOCSPX-[A-Za-z0-9_-]{28}" + _END)),
    ("Google OAuth access token", re.compile(r"(?<![\w-])ya29\.[0-9A-Za-z_-]{20,}")),
    ("SendGrid API key", re.compile(r"(?<![\w-])SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}" + _END)),
)
ALL_PATTERNS = check_secrets.PATTERNS + EXTRA_PATTERNS

_BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32-le"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
)


class Unscannable(ValueError):
    """A file whose content cannot be decoded for scanning (a corrupt or oversized gzip member)."""


def _inflate(contents: bytes) -> bytes:
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = bytearray()
    data = contents
    while data:
        try:
            out += inflater.decompress(data, MAX_DECOMPRESSED + 1 - len(out))
        except zlib.error as exc:
            raise Unscannable(f"corrupt gzip member: {exc}") from None
        if len(out) > MAX_DECOMPRESSED:
            raise Unscannable(f"a gzip member inflates past {MAX_DECOMPRESSED} bytes")
        data = inflater.unconsumed_tail
        if inflater.eof:
            # Concatenated members are one gzip file; continue with the next.
            data = inflater.unused_data
            inflater = zlib.decompressobj(16 + zlib.MAX_WBITS) if data else inflater
    if not inflater.eof:
        # zlib returns what it could and raises nothing: a cut member would pass as scanned.
        raise Unscannable("truncated gzip member")
    return bytes(out)


def decoded(contents: bytes) -> tuple[str, bool]:
    """``contents`` as text, and whether check_secrets.py could not have read it as such."""
    if contents[:2] == b"\x1f\x8b":
        return decoded(_inflate(contents))[0], True
    for bom, encoding in _BOMS:
        if contents.startswith(bom):
            return contents[len(bom) :].decode(encoding, errors="ignore"), True
    head = contents[:4096]
    if len(head) >= 16 and head.count(0) * 3 >= len(head):
        # Without a BOM: UTF-16 text of mostly ASCII has a NUL in every other byte.
        odd = head[1::2].count(0) >= head[0::2].count(0)
        return contents.decode("utf-16-le" if odd else "utf-16-be", errors="ignore"), True
    return contents.decode("utf-8", errors="ignore"), False


def findings(contents: bytes) -> Iterator[tuple[int, str, str]]:
    """``(line, family, match)`` for what check_secrets.py does not report on ``contents``."""
    text, unreadable = decoded(contents)
    for family, pattern in ALL_PATTERNS if unreadable else EXTRA_PATTERNS:
        for match in pattern.finditer(text):
            yield text.count("\n", 0, match.start()) + 1, family, match.group()


def _load_approvals() -> set[tuple[str, str, str]]:
    manifest = json.loads(
        ALLOWLIST_PATH.read_text(encoding="utf-8"), object_pairs_hook=check_secrets._unique_json_fields
    )
    if not isinstance(manifest, dict) or set(manifest) != {"version", "entries"}:
        raise ValueError("allowlist must contain version and entries")
    if type(manifest["version"]) is not int or manifest["version"] != 1:
        raise ValueError("unsupported allowlist version")
    if not isinstance(manifest["entries"], list):
        raise ValueError("allowlist entries must be a list")
    families = {family for family, _ in ALL_PATTERNS}
    approved: set[tuple[str, str, str]] = set()
    for index, entry in enumerate(manifest["entries"], 1):
        label = f"allowlist entry {index}"
        if not isinstance(entry, dict) or set(entry) != {"path", "family", "sha256", "reason"}:
            raise ValueError(f"{label}: invalid fields")
        if any(not isinstance(value, str) for value in entry.values()):
            raise ValueError(f"{label}: every field must be text")
        path = PurePosixPath(entry["path"])
        if (
            not entry["path"]
            or path.is_absolute()
            or path.as_posix() != entry["path"]
            or any(part in {".", ".."} for part in path.parts)
            or "\\" in entry["path"]
            or check_secrets._CONTROL.search(entry["path"])
        ):
            raise ValueError(f"{label}: path must be a normalized repository-relative file")
        if entry["family"] not in families or not entry["reason"].strip():
            raise ValueError(f"{label}: unknown family or missing review reason")
        if not check_secrets._DIGEST.fullmatch(entry["sha256"]):
            raise ValueError(f"{label}: invalid SHA-256")
        key = (entry["path"], entry["family"], entry["sha256"])
        if key in approved:
            raise ValueError(f"{label}: duplicate approval")
        source = check_secrets.REPOSITORY_ROOT / entry["path"]
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"{label}: approved fixture is missing or is not a regular file")
        try:
            present = {
                (family, check_secrets.digest(value)) for _, family, value in findings(source.read_bytes())
            }
        except Unscannable:
            present = set()
        if (entry["family"], entry["sha256"]) not in present:
            raise ValueError(f"{label}: stale approval for {check_secrets.display(entry['path'])}")
        approved.add(key)
    return approved


def main(argv: Sequence[str] | None = None) -> int:
    paths = sys.argv[1:] if argv is None else argv
    if not paths:
        print("check_secrets_extra: no files to check", file=sys.stderr)
        return 2
    try:
        approved = _load_approvals()
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        detail = str(exc) if type(exc) is ValueError else "cannot read or parse approval manifest"
        print(f"check_secrets_extra: {detail}", file=sys.stderr)
        return 1
    failed = False
    for path in paths:
        if os.path.islink(path) or os.path.isdir(path):
            continue
        where = check_secrets.display(path)
        try:
            found = list(findings(Path(path).read_bytes()))
        except OSError as exc:
            print(f"{where}: cannot read: {exc.strerror}", file=sys.stderr)
            failed = True
            continue
        except Unscannable as exc:
            print(f"{where}: cannot scan: {exc}", file=sys.stderr)
            failed = True
            continue
        for line, family, value in found:
            if (check_secrets._repository_path(path), family, check_secrets.digest(value)) in approved:
                continue
            print(f"{where}:{line}: possible hardcoded {family}: {value[:4]}... ({len(value)} characters)")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
