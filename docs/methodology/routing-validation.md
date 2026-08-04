# Routing Validation Methodology

## Purpose

This method tests whether TEO policy produces a complete, appropriate, and verifiable dispatch for representative task classes.

It evaluates routing policy. It does not claim to benchmark the quality of any provider or model implementation.

## Sources of truth

Each validation run uses:

- `policy/routing/team-routing.yaml` for team and worker dispatch
- `policy/routing/routing.yaml` for implementation resolution, fallback, risk, and verification rules
- `community/workers/workers.yaml` for worker ownership and required capabilities
- `community/teams/` for team inputs, outputs, boundaries, success criteria, and independence rules

## Required case fields

Every case records:

- case identifier
- task statement
- task type
- context
- risk level
- expected primary team
- expected primary worker
- required supporting teams or workers
- review path
- verification team
- verification method or controls
- expected dispatch record fields

## Validation checks

A case passes only when all required checks pass.

### Route coverage

The task type has an explicit route or a documented classification path.

### Team correctness

The selected team owns the primary responsibility for the task.

### Worker correctness

The selected worker matches the technical context. Default workers must be overridden when the task clearly belongs to another specialist.

### Capability sufficiency

The route can resolve every capability required by the task.

### Risk compliance

The risk level activates the required review, rollback, approval, and stopping controls.

### Verification completeness

The route names a verification team and an appropriate verification method. Every material acceptance criterion must be recorded as passed, failed, skipped, unavailable, or inconclusive.

### Independence

Consequential work must not use the same implementation as the sole planner, executor, reviewer, and verifier.

### Dispatch trace completeness

The route can populate every field required by `required_dispatch_record`.

## Verification outcomes

Each case ends with one of four outcomes:

- **accepted**: all required checks pass
- **revised**: a policy defect was found, corrected, and the case passed on rerun
- **rejected**: the route remains unsuitable after review
- **inconclusive**: required evidence or policy information is unavailable

## Validation sequence

1. Run every case against the unmodified baseline.
2. Record failures without changing the expected result to fit the policy.
3. Identify the smallest policy change that addresses each concrete failure.
4. Apply only evidence-backed corrections.
5. Rerun all cases, including cases that passed initially.
6. Record residual limitations and unresolved disagreements.

## Change rule

A routing change is justified only when a recorded case exposes a coverage, ownership, worker selection, risk, verification, independence, or traceability defect.

Newer implementations, preferences, or theoretical advantages are not sufficient reasons to change routing.
