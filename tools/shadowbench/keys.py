"""Canonical entity keys: one spelling per entity, so a tool is never scored on how it spells one.

``python -m tools.shadowbench.keys canon KEY...`` prints each key's canonical form;
``python -m tools.shadowbench.keys check --corpus corpus.json`` checks that the scheme is safe on a
cases corpus: every truth key is already canonical, and no two truth keys of a case share a
canonical form.

The cases scorer matches a reported key against truth keys. Under the ``exact`` scheme (the default,
under which every committed run was scored) two strings match only when they are equal, so a tool
that names the right entity as ``service:localhost:11434``, a GUID in upper case or a path as
``./.aws/amazonq/`` scores a false positive and a false negative for the same finding. The
``canonical-v1`` scheme maps reported and truth keys alike through :func:`canonical` before they
are compared. The normative rules are in ``docs/key-canonicalization.md``; in short:

* The whole key is Unicode NFC, surrounding whitespace is dropped and the namespace (the text before
  the first ``:``) is lower-cased. A key with no namespace, or with a control character, is left as
  it is apart from that, so it still matches nothing a well-formed key names.
* Only what the identifier's own platform treats as insensitive is folded. A value that is one GUID,
  bare, braced or as a ``urn:uuid:``, is lower-cased without braces or prefix in every namespace;
  other opaque identifiers (Okta, Slack or n8n ids, IAM role names, user names) keep their case.
* ``resource:`` and ``caller:`` ARNs lower-case their partition, service and region; the account
  and resource parts keep their case. An Azure resource id (``/subscriptions/...``), which Azure
  treats as case-insensitive, is lower-cased whole.
* ``k8s:<namespace>/<Kind>/<name>`` lower-cases the namespace and name (Kubernetes requires them in
  lower case) and spells a built-in kind the way the API does (``deployment`` is ``Deployment``).
* ``service:<host>:<port>`` takes ``http(s)://host:port/path`` too: the scheme's default port fills
  a missing one, the path goes, the host is lower-cased, ``localhost`` is ``127.0.0.1``, an IP is
  written the way ``ipaddress`` writes it (IPv6 in brackets) and the port loses leading zeros.
  ``client:`` IPs are written the same way.
* ``process:`` pids and ``proc:`` indexes lose leading zeros.
* ``artifact:`` paths use ``/``, lose a leading ``./``, ``~/`` or ``$HOME/``, empty and ``.``
  segments and a trailing ``/``, and resolve ``..`` lexically; a path whose ``..`` would leave the
  root is left as it is. Case is kept: the endpoint surface's file systems are case-sensitive.
* The code surface's fact namespaces (``tools.discovery_benchmark.taxonomy.CATEGORIES``) lower-case
  the value and write ``_`` and spaces as ``-``, the taxonomy's own spelling.

:func:`canonical` is total and idempotent: it never raises, and ``canonical(canonical(k))`` is
``canonical(k)`` for every string, which ``tests/unit/test_shadowbench_keys.py`` checks with
Hypothesis. A scheme is only safe on a corpus whose truth keys it never merges: :func:`collisions`
lists the keys of one case that share a canonical form, and the scorer refuses to score a corpus that
has any.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
import unicodedata
from collections.abc import Callable, Iterable
from pathlib import Path
from urllib.parse import urlsplit

from tools.discovery_benchmark.taxonomy import CATEGORIES
from tools.shadowbench.cases.corpus import Case, load_corpus

Canonicalizer = Callable[[str], str]

EXACT = "exact"
CANONICAL_V1 = "canonical-v1"

_GUID = re.compile(
    r"(?:urn:uuid:)?\{?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\}?\Z", re.IGNORECASE
)
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_DIGITS = re.compile(r"[0-9]+\Z")
_PORT = re.compile(r"[0-9]{1,5}\Z")

FACT_NAMESPACES: frozenset[str] = frozenset(CATEGORIES)
"""Code-surface fact categories, whose values the taxonomy spells in lower case with hyphens."""

K8S_KINDS: dict[str, str] = {
    kind.lower(): kind
    for kind in (
        "ConfigMap",
        "CronJob",
        "DaemonSet",
        "Deployment",
        "Ingress",
        "Job",
        "Namespace",
        "Pod",
        "ReplicaSet",
        "Secret",
        "Service",
        "ServiceAccount",
        "StatefulSet",
    )
}
"""Built-in workload and configuration kinds, spelled as the Kubernetes API spells them."""

DEFAULT_PORTS: dict[str, int] = {"http": 80, "https": 443, "grpc": 80, "grpcs": 443, "ws": 80, "wss": 443}


def exact(key: str) -> str:
    """The legacy scheme: a key is its own canonical form."""
    return key


def _guid(value: str) -> str | None:
    found = _GUID.match(value)
    return found.group(1).lower() if found else None


def _arn(value: str) -> str:
    """``arn:partition:service:region:account:resource`` with the first three fields lower-cased."""
    parts = value.split(":", 5)
    if len(parts) < 6 or parts[0].lower() != "arn":
        return value
    return ":".join(["arn", parts[1].lower(), parts[2].lower(), parts[3].lower(), parts[4], parts[5]])


def _azure(value: str) -> str:
    return value.lower() if value.lower().startswith("/subscriptions/") else value


def _ip(text: str) -> str | None:
    """``text`` as ``ipaddress`` writes it, IPv6 without brackets; None when it is no address."""
    candidate = text[1:-1] if text.startswith("[") and text.endswith("]") else text
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def _host(text: str) -> str:
    host = text.lower().rstrip(".")
    if host == "localhost":
        return "127.0.0.1"
    address = _ip(host)
    if address is None:
        return host
    return f"[{address}]" if ":" in address else address


def _service(value: str) -> str:
    """``host:port`` from a host and port or a URL; anything else is left as it is."""
    if "://" in value:
        try:
            parts = urlsplit(value)
            port = parts.port
        except ValueError:
            return value
        scheme = parts.scheme.lower()
        if parts.hostname is None:
            return value
        if port is None:
            if scheme not in DEFAULT_PORTS:
                return value
            port = DEFAULT_PORTS[scheme]
        return f"{_host(parts.hostname)}:{port}"
    host, sep, port_text = value.rpartition(":")
    if not sep or not host or not _PORT.match(port_text):
        return value
    if host.startswith("[") != host.endswith("]"):
        return value
    if ":" in host and not host.startswith("["):
        return value  # a bare IPv6 address with no port, or a malformed one
    port = int(port_text)
    if port > 65535:
        return value
    return f"{_host(host)}:{port}"


def _client(value: str) -> str:
    address = _ip(value)
    return address if address is not None else value


def _number(value: str) -> str:
    return str(int(value)) if _DIGITS.match(value) else value


def _k8s(value: str) -> str:
    parts = value.split("/")
    if len(parts) != 3 or not all(parts):
        return value
    namespace, kind, name = parts
    return f"{namespace.lower()}/{K8S_KINDS.get(kind.lower(), kind)}/{name.lower()}"


def _artifact(value: str) -> str:
    path = value.replace("\\", "/")
    for prefix in ("~/", "$HOME/", "${HOME}/"):
        if path.startswith(prefix):
            path = path[len(prefix) :]
            break
    absolute = path.startswith("/")
    out: list[str] = []
    for segment in path.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if not out:
                return value  # the path leaves its root; no rewrite can name the same file
            out.pop()
            continue
        out.append(segment)
    joined = "/".join(out)
    if absolute:
        return "/" + joined
    return joined or value


def _fact(value: str) -> str:
    return re.sub(r"[_\s]+", "-", value.strip().lower())


_RULES: dict[str, Callable[[str], str]] = {
    "artifact": _artifact,
    "caller": _arn,
    "client": _client,
    "k8s": _k8s,
    "proc": _number,
    "process": _number,
    "resource": lambda value: _azure(_arn(value)),
    "service": _service,
}


MAX_PASSES = 8
"""A rule can expose what an earlier one would have changed (a trailing ``/`` hiding a space), so
:func:`canonical` repeats one pass until nothing changes; every pass only removes or folds text."""


def canonical(key: str) -> str:
    """The ``canonical-v1`` form of ``key``: the fixed point of :func:`_pass` (see the module docstring)."""
    current = key
    for _ in range(MAX_PASSES):
        following = _pass(current)
        if following == current:
            break
        current = following
    return current


def _pass(key: str) -> str:
    text = unicodedata.normalize("NFC", key).strip()
    if _CONTROL.search(text):
        return text
    namespace, sep, value = text.partition(":")
    namespace = namespace.strip().lower()
    if not sep or not namespace:
        return text
    value = value.strip()
    guid = _guid(value)
    if guid is not None:
        return f"{namespace}:{guid}"
    rule = _RULES.get(namespace)
    if rule is not None:
        value = rule(value)
    elif namespace in FACT_NAMESPACES:
        value = _fact(value)
    return f"{namespace}:{value}"


SCHEMES: dict[str, Canonicalizer] = {EXACT: exact, CANONICAL_V1: canonical}
"""Every key scheme the scorer accepts, by the name ``metrics.json`` records."""


def scheme(name: str) -> Canonicalizer:
    try:
        return SCHEMES[name]
    except KeyError:
        raise ValueError(f"unknown key scheme {name!r}; expected one of {', '.join(SCHEMES)}") from None


def collisions(keys: Iterable[str], canon: Canonicalizer = canonical) -> dict[str, list[str]]:
    """Canonical forms that more than one distinct key in ``keys`` shares, with those keys sorted."""
    groups: dict[str, set[str]] = {}
    for key in keys:
        groups.setdefault(canon(key), set()).add(key)
    return {form: sorted(group) for form, group in sorted(groups.items()) if len(group) > 1}


def truth_keys(case: Case) -> list[str]:
    """Every key a case's truth names: expected, decoy and tolerated."""
    return [e.key for e in case.expected] + list(case.decoys) + list(case.tolerated)


def corpus_problems(cases: Iterable[Case], canon: Canonicalizer = canonical) -> list[str]:
    """Why ``canon`` is unsafe on a cases corpus: truth keys of one case it merges."""
    return [
        f"{case.case_id}: {', '.join(group)} share the canonical form {form}"
        for case in cases
        for form, group in collisions(truth_keys(case), canon).items()
    ]


def non_canonical(cases: Iterable[Case], canon: Canonicalizer = canonical) -> list[str]:
    """Truth keys not already in canonical form; they still score, but the corpus should say so."""
    return [
        f"{case.case_id}: {key} -> {canon(key)}"
        for case in cases
        for key in truth_keys(case)
        if canon(key) != key
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("canon", help="print the canonical form of each key")
    p.add_argument("keys", nargs="+")
    p.add_argument("--scheme", default=CANONICAL_V1, choices=sorted(SCHEMES))
    p = sub.add_parser("check", help="check that a scheme merges no truth keys of a cases corpus")
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--scheme", default=CANONICAL_V1, choices=sorted(SCHEMES))
    args = ap.parse_args(argv)
    canon = scheme(args.scheme)
    if args.command == "canon":
        for key in args.keys:
            print(json.dumps({"key": key, "canonical": canon(key)}, ensure_ascii=False))
        return 0
    corpus = load_corpus(args.corpus)
    problems = corpus_problems(corpus.cases, canon)
    for line in non_canonical(corpus.cases, canon):
        print(f"note: truth key not in canonical form: {line}")
    for problem in problems:
        print(f"collision: {problem}", file=sys.stderr)
    keys = sum(len(truth_keys(c)) for c in corpus.cases)
    print(
        json.dumps(
            {
                "scheme": args.scheme,
                "cases": len(corpus.cases),
                "truth_keys": keys,
                "collisions": len(problems),
            }
        )
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
