"""Bounded property tests for evidence-path and strict JSON parsers.

Only generated strings and bytes are parsed; no corpus artifact is executed.
Each JSON example owns its temporary directory so examples cannot share state.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import hypothesis.strategies as st
import pytest
from hypothesis import example, given, settings

from tools.verify_migration import _load_json, _path


@given(raw=st.text(max_size=180))
@example(raw="a/../b")
@example(raw="a//b")
@example(raw="a/./b")
@example(raw=".git/config")
@example(raw="a\\b")
@example(raw="a\0b")
@settings(max_examples=150, deadline=None)
def test_path_validator_accepts_only_canonical_relative_paths(raw: str) -> None:
    try:
        path = _path(raw)
    except ValueError:
        return
    assert path.as_posix() == raw
    assert path.parts and not path.is_absolute()
    assert not {"..", ".git"}.intersection(path.parts)
    assert "\\" not in raw and "\0" not in raw
    assert _path(path.as_posix()) == path


@given(parts=st.lists(st.from_regex(r"[A-Za-z][A-Za-z0-9_-]{0,20}", fullmatch=True), min_size=1, max_size=8))
@settings(max_examples=80, deadline=None)
def test_path_validator_accepts_generated_canonical_paths(parts: list[str]) -> None:
    assert _path("/".join(parts)).parts == tuple(parts)


@given(data=st.binary(max_size=2048))
@example(data=b'{"duplicate": 1, "duplicate": 2}')
@example(data=b"NaN")
@example(data=b"\xff")
@example(data=b"[" + b"0," * 300 + b"0]")
@settings(max_examples=80, deadline=None)
def test_json_loader_rejects_invalid_bytes_and_matches_valid_json(data: bytes) -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_bytes(data)
        try:
            result = _load_json(path, "fuzz")
        except (ValueError, UnicodeDecodeError):
            return
        # Successful decoding must agree with JSON's value, without the
        # original test's arbitrary 256-byte ceiling on legitimate input.
        assert result == json.loads(data.decode("utf-8"))


_JSON = st.recursive(
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats(allow_nan=False, allow_infinity=False)
    | st.text(max_size=50),
    lambda values: st.lists(values, max_size=8) | st.dictionaries(st.text(max_size=20), values, max_size=8),
    max_leaves=20,
)


@given(value=_JSON)
@example(value={"nested": [1.5, -1e308, 1e-308]})
@settings(max_examples=80, deadline=None)
def test_json_loader_round_trips_valid_json(value: object) -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        assert _load_json(path, "fuzz") == value


@given(key=st.text(max_size=50), first=st.integers(), second=st.integers())
@settings(max_examples=80, deadline=None)
def test_json_loader_rejects_duplicate_keys(key: str, first: int, second: int) -> None:
    encoded_key = json.dumps(key)
    with TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_text(f"{{{encoded_key}: {first}, {encoded_key}: {second}}}", encoding="utf-8")
        with pytest.raises(ValueError, match="duplicate"):
            _load_json(path, "fuzz")


@given(token=st.sampled_from(["NaN", "Infinity", "-Infinity", "1e999", "-1e999"]), key=st.text(max_size=50))
@example(token="1e999", key="nested")
@example(token="-1e999", key="nested")
@settings(max_examples=80, deadline=None)
def test_json_loader_rejects_nonfinite_numbers(token: str, key: str) -> None:
    with TemporaryDirectory() as directory:
        path = Path(directory) / "probe.json"
        path.write_text(f"{{{json.dumps(key)}: [{token}]}}", encoding="utf-8")
        with pytest.raises(ValueError, match="non-finite"):
            _load_json(path, "fuzz")
