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
