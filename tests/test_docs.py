"""The companion's own documentation must link only to things that exist.

Imported Markdown is excluded: MIGRATION.json binds its bytes, and some of its
links deliberately still name paths in the original ShadowScan repository.
Everything else (the README, the policy files and docs/) is checked for
relative links whose target file or heading anchor is missing.
"""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path
from urllib.parse import unquote

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]

_FENCE = re.compile(r"^\s*(```|~~~)")
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_MD_LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_HTML_LINK = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']+)["']""")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def _bound_paths() -> set[str]:
    manifest = json.loads((ROOT / "MIGRATION.json").read_text(encoding="utf-8"))
    return {entry["path"] for entry in manifest["files"]}


def _companion_docs() -> list[Path]:
    bound = _bound_paths()
    found = {
        *ROOT.glob("*.md"),
        *(ROOT / "docs").rglob("*.md"),
        *(ROOT / ".github").rglob("*.md"),
    }
    return sorted(path for path in found if path.relative_to(ROOT).as_posix() not in bound)


def _prose_lines(text: str) -> list[str]:
    """Lines outside fenced code blocks, with inline code removed."""
    lines: list[str] = []
    fenced = False
    for line in text.splitlines():
        if _FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            lines.append(_INLINE_CODE.sub("", line))
    return lines


def _slug(heading: str) -> str:
    """GitHub's heading anchor: link text kept, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"<[^>]+>", "", text).replace("`", "").lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


@cache
def _anchors(path: Path) -> frozenset[str]:
    seen: dict[str, int] = {}
    anchors: set[str] = set()
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if _FENCE.match(line):
            fenced = not fenced
            continue
        match = None if fenced else _HEADING.match(line)
        if match is None:
            continue
        base = _slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return frozenset(anchors)


def _links(path: Path) -> list[str]:
    links: list[str] = []
    for line in _prose_lines(path.read_text(encoding="utf-8")):
        links.extend(_MD_LINK.findall(line))
        links.extend(_HTML_LINK.findall(line))
    return links


def _problems(path: Path, root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for link in _links(path):
        if _EXTERNAL.match(link):
            continue
        target_part, _, anchor = link.partition("#")
        target = path if not target_part else (path.parent / unquote(target_part)).resolve()
        if not target.exists():
            problems.append(f"{link}: no such file")
            continue
        if root not in (target, *target.parents):
            problems.append(f"{link}: leaves the repository")
            continue
        if anchor and target.suffix == ".md" and unquote(anchor) not in _anchors(target):
            problems.append(f"{link}: no heading with that anchor")
    return problems


DOCS = _companion_docs()


def test_companion_documentation_is_found():
    names = {path.relative_to(ROOT).as_posix() for path in DOCS}
    assert {"README.md", "CONTRIBUTING.md", "SECURITY.md", "docs/README.md", "docs/metrics.md"} <= names
    assert not names & _bound_paths()


@pytest.mark.parametrize("path", DOCS, ids=lambda path: path.relative_to(ROOT).as_posix())
def test_relative_links_and_anchors_resolve(path: Path):
    assert _problems(path) == []


def test_slug_follows_github_rules():
    assert _slug("The Why: an open standard for discovery claims") == (
        "the-why-an-open-standard-for-discovery-claims"
    )
    assert _slug("Results: run of 2026-10-08 (before the changes)") == (
        "results-run-of-2026-10-08-before-the-changes"
    )
    assert _slug("Level 1: reproduce the `published` numbers") == "level-1-reproduce-the-published-numbers"
    assert _slug("A — B") == "a--b"


def test_broken_links_are_reported(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text(
        "# Title\n\n[ok](#title) [gone](missing.md) [anchor](#nowhere)\n"
        "```\n[ignored](inside-a-fence.md)\n```\n`[ignored](inline.md)` [web](https://example.invalid/x)\n",
        encoding="utf-8",
    )
    assert _links(doc) == ["#title", "missing.md", "#nowhere", "https://example.invalid/x"]
    assert _problems(doc, root=tmp_path.resolve()) == [
        "missing.md: no such file",
        "#nowhere: no heading with that anchor",
    ]


def test_citation_metadata_is_well_formed():
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert citation["cff-version"] == "1.2.0"
    assert {"title", "message", "authors", "repository-code", "license"} <= set(citation)
    assert citation["repository-code"] == "https://github.com/aisecnomad/Nexus-ShadowBench"
    assert all(author.get("name") for author in citation["authors"])
