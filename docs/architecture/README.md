# Architecture

Reference architecture for applying TEO policy across Mission Control, teams, workers, specialists, capabilities, implementations, providers, verification, evidence, and host/runtime boundaries.

## Canonical architecture surfaces

- [`../../CONSTITUTION.md`](../../CONSTITUTION.md) defines enduring architectural principles.
- [`../specification/lexicon.md`](../specification/lexicon.md) defines stable terminology.
- [`../../community/teams/mission-control.md`](../../community/teams/mission-control.md) defines Mission Control responsibility.
- [`../../policy/routing/`](../../policy/routing/) contains current executable routing and activation authority.
- [`../../policy/runtime/`](../../policy/runtime/) contains guarded execution, retry, recovery, telemetry, and live-scope controls.
- [`../specification/`](../specification/) contains the human-readable execution, verification, evidence, provider, and finalization contracts.
- [`../stewardship/progress-tracker.md`](../stewardship/progress-tracker.md) is the canonical current-state and sequencing record.
- [`python-clean-architecture-migration.md`](python-clean-architecture-migration.md) defines the behavior-preserving internal architecture migration for the Python reference implementation.

The active responsibility chain remains:

```text
Task
  -> Effective risk
  -> Mission Control
  -> Team
  -> Worker
  -> Optional Specialist
  -> Capability
  -> Implementation
  -> Fallback / escalation as governed
  -> Independent verification
  -> Evidence-bearing outcome
```

Provider access and authentication remain outside model-fitness routing. Host-native permissions may further restrict execution, but they do not replace TEO responsibility, risk, capability, fallback, or verification decisions.

## Cross-boundary evidence

[`../specification/final-execution-provenance.md`](../specification/final-execution-provenance.md) defines the optional read-only projection from validated Route-Outcome Evidence into `FinalOutcome`. The projection identifies the route that actually completed execution; it does not create routing, action, or permission authority.

## Python reference implementation boundaries

The Python reference implementation is migrating incrementally toward explicit domain, application, port, and adapter boundaries. Existing public import paths remain compatibility surfaces during that migration. Architectural extraction must not alter routing policy, effective-risk semantics, provider diversity, verification authority, evidence requirements, live scope, or finalization behavior.

The migration is intentionally tranche-based. A file move alone does not count as architectural progress; each tranche requires behavioral regression coverage and dependency-direction checks.

## Non-normative architecture research

The following are accepted research directions and do not change current runtime or live authority:

- [`../../research/roadmaps/host-integration-contract.md`](../../research/roadmaps/host-integration-contract.md): portable embedding and restrictive host/TEO authority intersection.
- [`../../research/roadmaps/execution-environment-recovery-contract.md`](../../research/roadmaps/execution-environment-recovery-contract.md): vendor-neutral isolated execution, checkpoint, rollback, and recovery verification.
- [`../../research/roadmaps/task-intent-action-authority-contract.md`](../../research/roadmaps/task-intent-action-authority-contract.md): preservation of originating request or delegated action authority before state-changing execution.

Research roadmaps guide investigation only. A later reviewed policy, schema, runtime, or release change is required before any research candidate becomes normative architecture.
