# Reference Implementations

Readable, non-normative implementations used to demonstrate TEO behavior. Machine-readable policy and canonical schemas remain authoritative when prose or example code disagrees.

## Python reference control plane

[`python/README.md`](python/README.md) documents the runnable Python router, provider-adapter boundary, retry/fallback behavior, live verification, finalization, controlled documentation replay, executable regulated-evidence stability qualification, and the non-production Host Integration Protocol 0.1 reference candidate.

The regulated-evidence harness is implemented in `teo_reference.evidence_stability` and is governed by `policy/specialists/evidence-stability-qualification.yaml`. Deterministic replay and mutation evidence demonstrate conformance; external-network authority resolution remains separately evidenced and continuous seven-day monitoring remains active.
