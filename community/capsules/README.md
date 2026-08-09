# Capsules

Immutable historical snapshots of TEO and the wider AI ecosystem.

## Immutability rule

Once a capsule is accepted into `main`, its contents are never rewritten, corrected, reformatted, or retroactively updated.

When later evidence changes the interpretation of an earlier capsule, create a new capsule that references the earlier record. Do not modify history to make the past appear cleaner, more complete, or more accurate than it was at the time.

The capsule index in this README may evolve. Accepted capsule files may not.

## Naming convention

```text
NNNN-YYYY-MM-DD-short-description.md
```

Each capsule should record:

- a stable capsule ID
- capture date and time
- the repository commit being preserved
- the project and ecosystem assumptions in effect
- completed capabilities and routes
- known limitations and unresolved work
- the next expected horizon
- a message to future stewards

## Accepted capsules

| Capsule | Captured state | Snapshot commit |
|---|---|---|
| [TEO-CAPSULE-0001](0001-2026-08-05-reference-control-plane.md) | The reference control plane exists; Phases 1–5 complete | `1aec5f651e4b448b5cb2cf0d7e0b1e3d099ee938` |
| [TEO-CAPSULE-0002](0002-2026-08-05-specialist-freshness-architecture.md) | Specialist depth is preserved through freshness, source-authority, applicability, and regression controls | `21a4b5281eab025fa5f3b76c84e823a4d202a1ea` |
| [TEO-CAPSULE-0003](0003-2026-08-06-user-research-route.md) | Qualitative user evidence receives a dedicated worker, route, provider-diverse fallback, and independent verification | `ac15871037df63e1e69bfce80a0e9e549c43a292` |
| [TEO-CAPSULE-0004](0004-2026-08-06-compliance-review-route.md) | Critical compliance becomes a dedicated, provider-diverse, human-gated Review Team responsibility | `09e46863d481b673790f646099087133e06d1e9d` |
| [TEO-CAPSULE-0005](0005-2026-08-06-principal-engineering-control-plane.md) | Principal engineering becomes an active 10-team, 78-specialist, provider-diverse, independently verified control plane | `003f71ac1bf27e96a1be5b0f66c58ba33fc5b75f` |
| [TEO-CAPSULE-0006](0006-2026-08-07-evidence-bearing-live-runtime.md) | TEO becomes an evidence-bearing live runtime with guarded provider execution, recovery, telemetry, and provider-diverse independent verification | `37e1d86b4a637834774b95bbe742795783063cf9` |
| [TEO-CAPSULE-0007](0007-2026-08-09-routing-not-access.md) | TEO reaches the reference-operational functional-v1 boundary with control-integrity remediation, freshness governance, provisional evidence tooling, and explicit separation of model routing from provider access | `f3eda8289e3d5c85ab59f477e3fdbefdcb5a834d` |
| [TEO-CAPSULE-0008](0008-2026-08-09-mission-control-routing-recalibration.md) | Mission Control completes the first evidence-led executable routing recalibration, including active Flash-Lite throughput routing, fallback and verifier rotation, stable coding fallback, frontier escalation, and README truth reconciliation | `ea47cc3ba348d1f222330ec3f4f483838a818d93` |
