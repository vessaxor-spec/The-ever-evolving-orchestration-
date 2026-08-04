# Benchmark Registry

Public benchmark definitions, results, limitations, and relevance to routing decisions.

TEO uses evidence to improve routing rather than maintain a permanent model leaderboard.

## Registry

- [`evidence.yaml`](evidence.yaml) is the machine-readable evidence register.
- [`methodology.md`](methodology.md) defines evidence grades, comparison rules, failure recording, and refresh requirements.
- [`result-template.yaml`](result-template.yaml) is the required structure for new reproducible benchmark entries.

## Evidence grades

- **A:** reproducible TEO-observed result
- **B:** reproducible independent external benchmark
- **C:** current provider-reported claim
- **D:** unverified or non-reproducible assertion

Only evidence relevant to a specific routing decision belongs in this registry.

The initial Grade A entry is the Phase 3 routing-policy conformance run. Current provider model catalogs are recorded as Grade C evidence. Live model quality, cost, and latency comparisons remain explicitly unrecorded until controlled runs exist.
