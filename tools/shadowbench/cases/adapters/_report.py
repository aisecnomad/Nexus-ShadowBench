"""Bounded reads of what a tool wrote.

A tool controls the size of every file in its work tree, up to the stage's file-size limit (4 GiB by
default), and adapters parse those files as root in the runner: a ``read_text`` and ``json.loads``
of such a file could exhaust the runner's memory. :func:`read_text` reads at most
:data:`MAX_REPORT_BYTES` and raises :class:`ReportTooLarge`, an ``OSError``, for a longer file, so
every adapter's existing handling of an unreadable report turns it into an ``error`` result.
"""

from __future__ import annotations

import io
from pathlib import Path

MAX_REPORT_BYTES = 256 << 20
"""The longest report an adapter reads; the reports of the committed runs are a few MiB at most."""


class ReportTooLarge(OSError):
    """A file the tool wrote that is longer than an adapter reads."""


def read_text(path: Path, *, errors: str = "strict", limit: int | None = None) -> str:
    """``path.read_text(encoding="utf-8", errors=errors)``, reading at most ``limit`` bytes."""
    cap = MAX_REPORT_BYTES if limit is None else limit
    with path.open("rb") as handle:
        data = handle.read(cap + 1)
    if len(data) > cap:
        raise ReportTooLarge(f"{path.name} is longer than the {cap} bytes an adapter reads of a report")
    # As read_text decodes: universal newlines, so what adapters keep is unchanged.
    return io.TextIOWrapper(io.BytesIO(data), encoding="utf-8", errors=errors).read()
