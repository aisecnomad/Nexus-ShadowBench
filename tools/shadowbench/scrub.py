"""Replace machine paths in run records with placeholders before publishing, and check that none remain.

``python -m tools.shadowbench.scrub apply --map /opt/tools=<tools> --map /srv/run=<run> FILE...``
``python -m tools.shadowbench.scrub check [--identity] PATH...``

A run's records name the operator's machine: the tool root, the scratch and output directories,
checkouts, the home directory. Published runs replace each with a placeholder; the committed runs
use ``<corpus>``, ``<estate>``, ``<repo>``, ``<run>``, ``<tools>``, ``<venvs>`` and ``<work>``, and
this module adds ``<home>``, ``<tmp>`` and ``<host>`` for what those do not cover. ``apply``
rewrites files in place, text-wise, so nothing but the replaced paths changes: a path is replaced
only where it ends at a path boundary (``/opt/tools`` is replaced in ``/opt/tools/bin`` but not in
``/opt/tools2``), longest path first, in its raw form and in the escaped form JSON writes. ``--home``
adds the operator's home directory as ``<home>`` and ``--tmp`` the temporary directory as ``<tmp>``.

``check`` reports what still looks like a machine path or identity in files (recursing into
directories): home directories (``/home/<user>``, ``/root``, ``/Users/<user>``,
``C:\\Users\\<user>``), per-run temporary paths (``/tmp/<name>``, ``/var/folders``,
``/private/var``, ``/run/user/<uid>``), and, with ``--identity``, this machine's host and user names.
It exits 1 on any finding and prints file, line and the matched text. A match that occurs
verbatim in a ``--corpus`` file or directory is the corpus's own content echoed by a tool (the
estate's fictional ``/home/dana``), not the operator's machine, and is not a finding. CI runs it
over every committed results directory of the live tracks, with their corpora. A clean check
does not prove a record names nothing private; it proves none of these patterns remain.
"""

from __future__ import annotations

import argparse
import functools
import getpass
import json
import re
import socket
import sys
import tempfile
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import NamedTuple

PLACEHOLDERS: frozenset[str] = frozenset(
    {"<corpus>", "<estate>", "<home>", "<host>", "<repo>", "<run>", "<tmp>", "<tools>", "<venvs>", "<work>"}
)
"""The tokens a published record may use in place of a machine path."""

_AFTER_ESCAPE = r"(?<=\\[ntr])|(?<=\[[0-9]m)|(?<=\[[0-9][0-9]m)|(?<=;[0-9]m)|(?<=;[0-9][0-9]m)"
"""A path may follow a JSON escape (``\\n``, ``\\t``, ``\\r``) or an ANSI colour code (``...[0m``),
whose last character is a letter."""

_START = rf"(?:(?<![>\w.~$/-])|(?<=file://)|(?<=file://localhost)|{_AFTER_ESCAPE})"
"""Where an absolute path can start. One right after a placeholder (``<estate>/home/x``), a name or
another path is relative to it, as the estate's own ``home/<device>`` trees are; one after
``file://`` is a URI's path (SARIF writes every location so)."""

PATTERNS: dict[str, re.Pattern[str]] = {
    "home directory": re.compile(
        _START
        + r"(?:/home/[A-Za-z0-9._-]+|/var/home/[A-Za-z0-9._-]+|/root(?![\w.-])"
        + r"|(?:/System/Volumes/Data|/mnt/[A-Za-z])?/Users/[A-Za-z0-9._ -]+)"
    ),
    "Windows profile": re.compile(r"[A-Za-z]:(?:\\\\|\\)Users(?:\\\\|\\)[^\\\"]+", re.IGNORECASE),
    "temporary path": re.compile(
        _START + r"(?:/tmp/[A-Za-z0-9._-]+|/var/folders/|/private/var/|/run/user/\d+)"
    ),
}
"""Patterns that mark a machine path a published record should not keep."""

TEXT_SUFFIXES: frozenset[str] = frozenset(
    {".json", ".jsonl", ".md", ".txt", ".csv", ".log", ".yml", ".yaml", ".sarif"}
)
"""Suffixes, compared in lower case, of the text records a directory walk reads."""
_BOUNDARY = r"(?=[/\\\"'\s:;,)\]}]|$)"
_DELIMITERS = frozenset(" \t\r\n\"'\\,;:)]}<>|`")
"""Characters that end a path token in a record: quotes, JSON escapes, list and shell separators."""


def parse_map(items: Iterable[str]) -> dict[str, str]:
    """``PATH=<token>`` pairs as ``{path: token}``; paths absolute, tokens from :data:`PLACEHOLDERS`."""
    out: dict[str, str] = {}
    for item in items:
        path, sep, token = item.rpartition("=")
        if not sep or not path:
            raise ValueError(f"--map takes PATH=<token>, not {item!r}")
        if token not in PLACEHOLDERS:
            raise ValueError(f"unknown placeholder {token!r}; use one of {', '.join(sorted(PLACEHOLDERS))}")
        stripped = path.rstrip("/\\") or path
        if not (stripped.startswith("/") or re.match(r"[A-Za-z]:\\", stripped)):
            raise ValueError(f"{path!r} is not an absolute path")
        if stripped in ("/", "\\"):
            raise ValueError("refusing to replace the root directory")
        out[stripped] = token
    return out


def _forms(path: str) -> list[str]:
    """``path`` as written raw and as JSON writes it inside a string (backslashes, non-ASCII escaped)."""
    forms = {path, json.dumps(path)[1:-1], json.dumps(path, ensure_ascii=False)[1:-1]}
    return sorted(forms, key=len, reverse=True)


def _token(token: str, _: re.Match[str]) -> str:
    return token


def scrub_text(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    """``text`` with each mapped path replaced where a path starts and ends, longest first; and how many.

    ``/tmp`` mapped to ``<tmp>`` replaces ``/tmp/x`` and ``"/tmp"`` but not the ``/tmp`` inside
    ``/var/tmp`` or ``https://host/tmp``.
    """
    total = 0
    for path in sorted(mapping, key=len, reverse=True):
        # a function, not a replacement string, so a token is never read as a backreference
        replace = functools.partial(_token, mapping[path])
        for form in _forms(path):
            text, count = re.subn(_START + re.escape(form) + _BOUNDARY, replace, text)
            total += count
    return text, total


def scrub_words(text: str, words: dict[str, str]) -> tuple[str, int]:
    """``text`` with each word (a host name) replaced where it stands as a whole name; and how many."""
    total = 0
    for word in sorted(words, key=len, reverse=True):
        replace = functools.partial(_token, words[word])
        text, count = re.subn(rf"(?<![A-Za-z0-9_.-]){re.escape(word)}(?![A-Za-z0-9_-])", replace, text)
        total += count
    return text, total


class Finding(NamedTuple):
    line: int
    kind: str
    match: str
    path: str
    """The whole path token the match starts, up to a quote, an escape or a separator."""


def _token_at(line: str, start: int) -> str:
    end = start
    while end < len(line) and line[end] not in _DELIMITERS:
        end += 1
    return line[start:end]


def findings(text: str, extra: Iterable[str] = ()) -> Iterator[Finding]:
    """Every machine path or identity left in ``text``."""
    words = [w for w in extra if w]
    for number, line in enumerate(text.split("\n"), 1):
        for kind, pattern in PATTERNS.items():
            for found in pattern.finditer(line):
                yield Finding(number, kind, found.group(0), _token_at(line, found.start()))
        for word in words:
            if re.search(rf"(?<![A-Za-z0-9_.-]){re.escape(word)}(?![A-Za-z0-9_-])", line):
                yield Finding(number, "machine identity", word, word)


def files(paths: Iterable[Path]) -> tuple[list[Path], list[str]]:
    """Text files under ``paths``, recursing into directories, and why any path named was unusable.

    A path named outright that does not exist, is a symlink or is not a text file is a problem, not a
    silent skip; inside a directory, symlinks and other files are passed over.
    """
    found: list[Path] = []
    problems: list[str] = []

    def walk(path: Path, named: bool) -> None:
        if path.is_symlink():
            if named:
                problems.append(f"{path}: a symlink; name the file it points to")
            return
        if path.is_dir():
            for child in sorted(path.iterdir()):
                walk(child, False)
        elif path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            found.append(path)
        elif named:
            problems.append(f"{path}: " + ("not a text record" if path.exists() else "does not exist"))

    for path in paths:
        walk(path, True)
    return found, problems


CORPUS_FILE_LIMIT = 8 << 20
"""Corpus files larger than this are not read for echoed paths."""


def echoed(token: str, corpus: set[str]) -> bool:
    """Whether a record's path token is corpus content: a corpus path or one of its ancestor
    directories, or one cut short inside its last component by a report (``/home/dana/freight/ra``).
    ``/home/ci/x`` in a corpus does not exempt ``/home/ci/y``, nor ``/home/c`` a home named ``c``."""
    if token in corpus:
        return True
    parent = token.rsplit("/", 1)[0]
    return parent in corpus and any(path.startswith(token) for path in corpus)


def corpus_matches(paths: Iterable[Path]) -> set[str]:
    """Every whole path token a pattern matches in the files under ``paths``, with each ancestor
    directory below the home or temporary root (see :func:`echoed`)."""
    found: set[str] = set()
    for path in paths:
        if path.is_symlink():
            continue
        if path.is_dir():
            found |= corpus_matches(sorted(path.iterdir()))
        elif path.is_file() and path.stat().st_size <= CORPUS_FILE_LIMIT:
            text = path.read_text(encoding="utf-8", errors="replace")
            for finding in findings(text):
                parts = finding.path.rstrip("/").split("/")
                found |= {"/".join(parts[:end]) for end in range(3, len(parts) + 1)}
    return found


def identity() -> list[str]:
    """This machine's host name and the user name, as ``check --identity`` looks for them."""
    names = {socket.gethostname()}
    try:
        names.add(getpass.getuser())
    except (KeyError, OSError):
        pass
    return sorted(n for n in names if len(n) >= 3)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("apply", help="replace machine paths with placeholders, in place")
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("--map", action="append", default=[], metavar="PATH=<token>")
    p.add_argument("--home", action="store_true", help="also replace the home directory with <home>")
    p.add_argument("--tmp", action="store_true", help="also replace the temporary directory with <tmp>")
    p.add_argument("--host", action="store_true", help="also replace this machine's host name with <host>")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("check", help="report machine paths and identities left in files or directories")
    p.add_argument("paths", nargs="+", type=Path)
    p.add_argument("--identity", action="store_true", help="also look for this host's and user's names")
    p.add_argument(
        "--corpus", action="append", default=[], type=Path, help="a corpus whose own paths are not findings"
    )
    args = ap.parse_args(argv)
    if args.command == "apply":
        try:
            mapping = parse_map(args.map)
            if args.home:
                mapping.update(parse_map([f"{Path.home()}=<home>"]))
            if args.tmp:
                mapping.update(parse_map([f"{tempfile.gettempdir()}=<tmp>"]))
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 2
        words: dict[str, str] = {}
        if args.host:
            host = socket.gethostname()
            if len(host) < 3:
                print(f"host name {host!r} is too short to replace safely; edit it by hand", file=sys.stderr)
                return 2
            words[host] = "<host>"
        if not mapping and not words:
            print("nothing to replace: give --map, --home, --tmp or --host", file=sys.stderr)
            return 2
        targets, problems = files(args.files)
        if problems or not targets:
            print("\n".join(problems) or "no text record to scrub", file=sys.stderr)
            return 2
        for path in targets:
            # newline="": line endings are bytes like any other and stay as they are
            with path.open(encoding="utf-8", newline="") as handle:
                original = handle.read()
            text, count = scrub_text(original, mapping)
            text, named = scrub_words(text, words)
            count += named
            if count and not args.dry_run:
                with path.open("w", encoding="utf-8", newline="") as handle:
                    handle.write(text)
            print(f"{path}: {count} replaced")
        return 0
    targets, problems = files(args.paths)
    if problems or not targets:
        print("\n".join(problems) or "no text record to check", file=sys.stderr)
        return 2
    extra = identity() if args.identity else []
    corpus = corpus_matches(args.corpus)
    found = skipped = 0
    for path in targets:
        for finding in findings(path.read_text(encoding="utf-8", errors="replace"), extra):
            if finding.kind != "machine identity" and echoed(finding.path, corpus):
                skipped += 1
                continue
            print(f"{path}:{finding.line}: {finding.kind}: {finding.match}")
            found += 1
    print(f"{found} finding(s); {skipped} corpus path(s) echoed by tools", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
