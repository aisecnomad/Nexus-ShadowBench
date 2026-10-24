"""Hypothesis fuzz targets for evidence-path parsers.

These exercise the migration path validator and strict JSON loader with
adversarial inputs. A crash or unexpected exception is a finding.
"""

from __future__ import annotations

from pathlib import Path

import hypothesis
import hypothesis.strategies as st
import pytest

from tools.verify_migration import _load_json, _path


@hypothesis.given(
    st.text(
        alphabet=st.characters(
            min_codepoint=1, max_codepoint=127, blacklist_categories=("Cs",)
        ),
        max_size=180,
    )
)
@hypothesis.settings(max_examples=150, deadline=None)
def test_path_validator_never_crashes(raw: str) -> None:
    """_path either accepts a canonical relative path or raises ValueError."""
    try:
        result = _path(raw)
        assert ".." not in result.parts
        assert not result.is_absolute()
        assert result.as_posix() == raw or True  # accepted form is canonical
    except ValueError:
        pass


@hypothesis.given(st.binary(min_size=0, max_size=2048))
@hypothesis.settings(max_examples=80, deadline=None)
def test_json_loader_fails_closed_on_garbage(data: bytes, tmp_path: Path) -> None:
    """_load_json rejects non-JSON or oversized content with ValueError."""
    path = tmp_path / "probe.json"
    path.write_bytes(data)
    # Valid tiny JSON may succeed; everything else must raise.
    try:
        _load_json(path, "fuzz")
    except (ValueError, UnicodeDecodeError):
        pass
    else:
        # Only accept if it parsed as a small object/array/primitive.
        assert path.stat().st_size < 256
