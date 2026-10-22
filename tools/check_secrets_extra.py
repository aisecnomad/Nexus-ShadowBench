"""Credential checks that tools/check_secrets.py does not make, run beside it.

Usage: python tools/check_secrets_extra.py FILE [FILE ...]
       git ls-files -z | xargs -0 python tools/check_secrets_extra.py

``check_secrets.py`` is bound byte for byte in MIGRATION.json and is not
amendable, so what it misses is checked here instead:

* credential families it does not know (:data:`EXTRA_PATTERNS`: AI provider
  keys, package registry and container tokens, Slack app tokens and webhooks,
  Google OAuth secrets, SendGrid), in every file;
* every family, its own and these, in what it cannot read. It decodes all
  bytes as UTF-8 and drops the rest, so a gzip member stays compressed, and in
  UTF-16 or UTF-32 text (with or without a BOM) a NUL sits beside every ASCII
  character, so neither can match. Here every gzip layer is inflated and every
  tar member read (at most :data:`MAX_GZIP_DEPTH` deep and
  :data:`MAX_DECOMPRESSED` bytes in all; a corrupt, truncated, deeper or larger
  one is reported, not skipped), and each is scanned as UTF-8 and, when it
  holds a NUL, with the NULs removed (archive padding and wide text beside
  ASCII) and as UTF-16 and UTF-32 at every alignment (wide text beside other
  characters). A match check_secrets.py
  already reports in the file as committed is not reported twice.

Reports and exit codes follow ``check_secrets.py``: each finding names the file,
line, family, first four characters and length, never the value; exit 1 on an
unapproved finding, an unreadable file or a bad approval, 2 when no file is
named. Approvals live in secret_allowlist_extra.json and bind exactly as
``check_secrets.py``'s do: normalized repository path, family, the match's
SHA-256 and a review reason, and for a private-key marker the whole file's
SHA-256 too (a marker alone cannot identify the key); an approval that matches
nothing fails closed.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import tarfile
import zlib
from collections.abc import Iterator, Sequence
from pathlib import Path, PurePosixPath

if __package__ in (None, ""):  # run as a script, as the pre-commit hook and CI do
    sys.path.insert(0, str(Path(__file__).absolute().parent.parent))

from tools import check_secrets

ALLOWLIST_PATH = Path(__file__).with_name("secret_allowlist_extra.json")
MAX_DECOMPRESSED = 256 << 20
"""The most a file's gzip layers are inflated to, all together; the repository's largest is under 5 MiB."""
MAX_GZIP_DEPTH = 8
"""The most gzip layers and tar archives a file is unwrapped through."""

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
        re.compile(
            r"https://hooks\.slack\.com/(?:services|workflows|triggers)/T[A-Z0-9]+/[A-Za-z0-9]+/[A-Za-z0-9]{20,}"
        ),
    ),
    ("Google OAuth client secret", re.compile(r"(?<![\w-])GOCSPX-[A-Za-z0-9_-]{28}" + _END)),
    ("Google OAuth access token", re.compile(r"(?<![\w-])ya29\.[0-9A-Za-z_-]{20,}")),
    ("SendGrid API key", re.compile(r"(?<![\w-])SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}" + _END)),
)
ALL_PATTERNS = check_secrets.PATTERNS + EXTRA_PATTERNS


class Unscannable(ValueError):
    """A file that cannot be decoded for scanning: a corrupt, truncated, too deep or too large gzip."""


def _inflate(contents: bytes, budget: int) -> bytes:
    """Every member of the gzip file ``contents``, inflated to at most ``budget`` bytes."""
    inflater = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = bytearray()
    data = contents
    while data:
        try:
            out += inflater.decompress(data, budget + 1 - len(out))
        except zlib.error as exc:
            raise Unscannable(f"corrupt gzip member: {exc}") from None
        if len(out) > budget:
            raise Unscannable(f"gzip layers inflate past {MAX_DECOMPRESSED} bytes")
        data = inflater.unconsumed_tail
        if inflater.eof:
            # Concatenated members are one gzip file; continue with the next.
            data = inflater.unused_data
            inflater = zlib.decompressobj(16 + zlib.MAX_WBITS) if data else inflater
    if not inflater.eof:
        # zlib returns what it could and raises nothing: a cut member would pass as scanned.
        raise Unscannable("truncated gzip member")
    return bytes(out)


def layers(contents: bytes) -> list[bytes]:
    """``contents`` and everything inside it: each gzip layer inflated and each tar member read,
    without recursion, at most :data:`MAX_GZIP_DEPTH` deep and :data:`MAX_DECOMPRESSED` bytes in all."""
    found: list[bytes] = []
    queue = [(contents, 0)]
    budget = MAX_DECOMPRESSED
    while queue:
        blob, depth = queue.pop(0)
        found.append(blob)
        inner: list[bytes] = []
        if blob[:2] == b"\x1f\x8b":
            inner = [_inflate(blob, budget)]
        elif _is_tar(blob):
            inner = _members(blob, budget)
        if inner and depth >= MAX_GZIP_DEPTH:
            raise Unscannable(f"gzip or tar nested deeper than {MAX_GZIP_DEPTH} layers")
        for item in inner:
            budget -= len(item)
            if budget < 0:
                raise Unscannable(f"gzip layers inflate past {MAX_DECOMPRESSED} bytes")
            queue.append((item, depth + 1))
    return found


def _is_tar(blob: bytes) -> bool:
    return len(blob) >= 512 and blob[257:262] == b"ustar"


def _members(blob: bytes, budget: int) -> list[bytes]:
    """The contents of every regular file in the tar archive ``blob``, at most ``budget`` bytes in all."""
    out: list[bytes] = []
    try:
        with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                budget -= member.size
                if budget < 0:
                    raise Unscannable(f"gzip layers inflate past {MAX_DECOMPRESSED} bytes")
                handle = archive.extractfile(member)
                out.append(handle.read() if handle is not None else b"")
    except (tarfile.TarError, OSError, EOFError) as exc:
        raise Unscannable(f"corrupt tar archive: {exc}") from None
    return out


_WIDE = [(codec, offset) for codec in ("utf-16-le", "utf-16-be") for offset in (0, 1)] + [
    (codec, offset) for codec in ("utf-32-le", "utf-32-be") for offset in range(4)
]


def views(contents: bytes) -> list[tuple[str, bool]]:
    """``(text, every family)`` for each way ``contents`` is read; False only for the file as
    check_secrets.py reads it, whose own families it reports itself."""
    out: list[tuple[str, bool]] = []
    for index, layer in enumerate(layers(contents)):
        out.append((layer.decode("utf-8", errors="ignore"), index > 0))
        if b"\x00" in layer:
            # Archive padding and wide text beside ASCII: the bytes themselves once the NULs go. Wide
            # text beside other characters (CJK punctuation, say) needs its own decoding, at every
            # alignment, or their bytes run into the token.
            out += [(layer[offset:].decode(codec, errors="ignore"), True) for codec, offset in _WIDE]
            out.append((layer.replace(b"\x00", b"").decode("utf-8", errors="ignore"), True))
    return out


def findings(contents: bytes) -> Iterator[tuple[int, str, str]]:
    """``(line, family, match)`` for what check_secrets.py does not report on ``contents``, each once.

    The views overlap: one token can match in several, and with a neighbour's byte run into it in
    the NUL-free one. A match that holds, or lies within, one already reported in its family is the
    same token; the decodings come first, so the clean spelling is the one reported.
    """
    read = views(contents)
    reported: dict[str, list[str]] = {}
    if len(read) > 1:  # matches in other views that check_secrets.py reports on the file itself
        for _, family, value in check_secrets.findings(read[0][0]):
            reported.setdefault(family, []).append(value)
    for text, every in read:
        for family, pattern in ALL_PATTERNS if every else EXTRA_PATTERNS:
            for match in pattern.finditer(text):
                value = match.group()
                seen = reported.setdefault(family, [])
                if any(value in known or known in value for known in seen):
                    continue
                seen.append(value)
                yield text.count("\n", 0, match.start()) + 1, family, value


def _load_approvals() -> dict[tuple[str, str, str], str | None]:
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
    approved: dict[tuple[str, str, str], str | None] = {}
    for index, entry in enumerate(manifest["entries"], 1):
        label = f"allowlist entry {index}"
        required = {"path", "family", "sha256", "reason"}
        if not isinstance(entry, dict) or not required <= set(entry) <= required | {"content_sha256"}:
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
        content = entry.get("content_sha256")
        if entry["family"] == "private key" and content is None:
            raise ValueError(f"{label}: private-key markers require a whole-file digest")
        if content is not None and not check_secrets._DIGEST.fullmatch(content):
            raise ValueError(f"{label}: invalid whole-file SHA-256")
        key = (entry["path"], entry["family"], entry["sha256"])
        if key in approved:
            raise ValueError(f"{label}: duplicate approval")
        source = check_secrets.REPOSITORY_ROOT / entry["path"]
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"{label}: approved fixture is missing or is not a regular file")
        data = source.read_bytes()
        try:
            present = {(family, check_secrets.digest(value)) for _, family, value in findings(data)}
        except Unscannable:
            present = set()
        if (entry["family"], entry["sha256"]) not in present:
            raise ValueError(f"{label}: stale approval for {check_secrets.display(entry['path'])}")
        if content is not None and hashlib.sha256(data).hexdigest() != content:
            raise ValueError(f"{label}: fixture contents changed for {check_secrets.display(entry['path'])}")
        approved[key] = content
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
            contents = Path(path).read_bytes()
            found = list(findings(contents))
        except OSError as exc:
            print(f"{where}: cannot read: {exc.strerror}", file=sys.stderr)
            failed = True
            continue
        except Unscannable as exc:
            print(f"{where}: cannot scan: {exc}", file=sys.stderr)
            failed = True
            continue
        for line, family, value in found:
            key = (check_secrets._repository_path(path), family, check_secrets.digest(value))
            if key in approved and (
                approved[key] is None or hashlib.sha256(contents).hexdigest() == approved[key]
            ):
                continue
            print(f"{where}:{line}: possible hardcoded {family}: {value[:4]}... ({len(value)} characters)")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
