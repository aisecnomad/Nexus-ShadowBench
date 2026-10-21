# Key canonicalization

How the cases-track scorer can compare a reported key with a truth key by
the entity it names rather than by its spelling. The implementation and the
normative rules are [`tools/shadowbench/keys.py`](../tools/shadowbench/keys.py);
this page restates them.

## Why

A cases-track truth entity has one key, such as `service:127.0.0.1:11434`,
`app:0672d27a-beba-c07d-f9ef-ff74e337bb52` or `artifact:.aws/amazonq/mcp.json`.
Under the `exact` scheme a tool scores a hit only when its adapter writes that
string. A tool that names the right entity as `service:localhost:11434`, an
upper-case GUID or `./.aws/amazonq/` scores a false positive **and** a false
negative for one correct finding. The committed adapters were written to emit
the corpus's spelling, but an adapter written by a vendor or a third party
should not need to know it, and a reviewer should not have to read every
adapter to know that a miss is a miss.

## Schemes

| Scheme | What is compared | Used by |
|---|---|---|
| `exact` (default) | keys as written | every committed run; `make rescore` |
| `canonical-v1` | `canonical(reported)` with `canonical(truth)` | `score --keys canonical-v1` |

`metrics.json` records `key_scheme` only for a scheme other than `exact`, so
the committed runs still re-score byte for byte, and the report then says the
keys were canonicalized. Scoring the 2026-10-11 cases run under
`canonical-v1` gives metrics identical to the committed ones
(`tests/unit/test_shadowbench_keys.py` checks it): no published number
depends on the choice.

## Rules of `canonical-v1`

A key is `<namespace>:<value>`. Folding stops at what the identifier's own
platform treats as the same; everything else keeps its case and spelling.

| Applies to | Rule | Example |
|---|---|---|
| every key | Unicode NFC; surrounding whitespace dropped; namespace lower-cased; a key with a control character or no namespace is left alone | `App :x` is `app:x` |
| any value that is one GUID | lower case, no braces, no `urn:uuid:` | `bot:{0672D27A-...}` is `bot:0672d27a-...` |
| `resource:`, `caller:` ARNs | partition, service and region lower-cased; account and resource unchanged | `arn:AWS:Bedrock:US-EAST-1:1:agent/AbC` is `arn:aws:bedrock:us-east-1:1:agent/AbC` |
| `resource:` Azure ids | the whole `/subscriptions/...` id lower-cased (Azure treats it as case-insensitive) | |
| `k8s:<ns>/<Kind>/<name>` | namespace and name lower-cased (Kubernetes requires it); built-in kinds spelled as the API spells them | `k8s:AI/deployment/Flowise` is `k8s:ai/Deployment/flowise` |
| `service:` | `host:port`, or an `http(s)`, `grpc(s)` or `ws(s)` URL whose path is dropped and whose missing port is the scheme's default; host lower-cased; `localhost` is `127.0.0.1`; IPs as Python's `ipaddress` writes them, IPv6 in brackets; port without leading zeros | `service:http://LocalHost:11434/v1` is `service:127.0.0.1:11434` |
| `client:` | an IP as `ipaddress` writes it | |
| `process:`, `proc:` | leading zeros dropped | `process:007` is `process:7` |
| `artifact:` | `\` as `/`; a leading `./`, `~/`, `$HOME/` or `${HOME}/` dropped; empty and `.` segments and a trailing `/` dropped; `..` resolved lexically; case kept | `artifact:~/.aws//amazonq/./mcp.json/` is `artifact:.aws/amazonq/mcp.json` |
| code-surface fact categories | value lower-cased; `_` and spaces written as `-` | `Framework:Lang_Graph` is `framework:lang-graph` |

Deliberately **not** folded:

- Opaque identifiers (Okta, Slack and n8n ids, IAM role and user names,
  gateway user names): their platforms distinguish case.
- An IPv4 address with leading-zero octets (`010.1.2.3`): some parsers read
  it as octal, so it is left as written and matches nothing.
- `0.0.0.0` is not loopback, and an `artifact:` path whose `..` leaves its
  root is left as written: no rewrite may turn a wrong answer into a match.
- Paths keep their case; the endpoint surface's file systems are
  case-sensitive.

## Guarantees

- **Total and idempotent.** `canonical` never raises, and
  `canonical(canonical(k)) == canonical(k)` for every string, which
  Hypothesis checks on arbitrary text. One pass can expose what an earlier
  rule would have changed, so `canonical` is the fixed point of a pass that
  only removes or folds text.
- **Never merges truth.** The scorer refuses a scheme under which two truth
  keys of one case (expected, decoy or tolerated) share a canonical form,
  `--force` or not. `python -m tools.shadowbench.keys check --corpus
  corpus.json` runs the same check and lists truth keys that are not already
  canonical. The committed cases corpus has no collision and no
  non-canonical key.
- **Matching is otherwise unchanged.** Tolerated keys, the one-way `artifact:`
  directory rule, de-duplication (now by canonical form), the code-surface
  taxonomy check and every fail-closed rule apply as in
  [metrics.md](metrics.md#matching-a-report-to-the-truth).

## Using it

```bash
python -m tools.shadowbench.keys canon 'service:http://localhost:11434/v1'
python -m tools.shadowbench.keys check --corpus benchmarks/shadowbench/cases/corpus.json
python -m tools.shadowbench.cases score --corpus benchmarks/shadowbench/cases/corpus.json \
    --results <run> --out <run>/metrics.json --keys canonical-v1
```

A new run of record should state its scheme in its README. The scheme is a
scoring rule, so changing the default is a scorer change under
[GOVERNANCE.md](../GOVERNANCE.md): proposed in the open, decided before the
run it applies to, and never chosen after seeing which scheme favours which
tool.
