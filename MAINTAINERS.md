# Maintainers

## Current maintainers

| Name | GitHub | Role |
|------|--------|------|
| AISecNomad | [@aisecnomad](https://github.com/aisecnomad) | Founding maintainer; also maintains Nexus ShadowScan, a tool this benchmark scores |

There is currently a single maintainer. Review, merge and security decisions
are made by that account. See [GOVERNANCE.md](GOVERNANCE.md) for how that
changes when reviewers and further maintainers join, and for the
conflict-of-interest rules that bind the maintainer.

## What maintainers do

- Triage issues, label disputes and security advisories
- Review pull requests against the quality gates in
  [CONTRIBUTING.md](CONTRIBUTING.md)
- Keep every migrated byte, freeze and committed result unchanged
- Keep scoring fail-closed: errors, missing rows and incomplete runs never
  earn a true negative
- Keep every published claim within its evidence, and disclose in-sample runs
- Enforce the [code of conduct](CODE_OF_CONDUCT.md)

## Becoming a reviewer or maintainer

The project is looking for reviewers, independent corpus authors and
independent labelers with experience in:

- Benchmark and evaluation design, and the statistics of small samples
- Detection engineering for agent frameworks, MCP and coding agents
- Enterprise identity, LLM gateways, low-code and SaaS administration
- Cloud, Kubernetes, endpoint, network and process telemetry
- Sandboxing and isolation on Linux

People without a stake in any scored tool are especially needed; see
[GOVERNANCE.md](GOVERNANCE.md#path-to-independent-stewardship). Start with a
documentation fix, a label dispute backed by evidence, a review, or an adapter
fix.

Open a [question issue](https://github.com/aisecnomad/Nexus-ShadowBench/issues/new?template=question.yml)
titled `Maintainer interest` if you want to help, and state any relationship
to a scored tool.

## Contact

- Public: GitHub issues and pull requests
- Private / security / code of conduct:
  [security advisories](https://github.com/aisecnomad/Nexus-ShadowBench/security/advisories/new)
