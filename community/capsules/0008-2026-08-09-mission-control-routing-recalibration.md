---
capsule_id: TEO-CAPSULE-0008
status: accepted
captured_at: 2026-08-09T20:08:00+02:00
snapshot_commit: ea47cc3ba348d1f222330ec3f4f483838a818d93
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0007
immutability: accepted capsules are never rewritten
---

# Capsule 0008: Mission Control Recalibrates the Routes

This capsule records TEO after Mission Control completed its first full evidence-led recalibration of executable model routing and the repository README was reconciled to that resulting policy.

It preserves the repository at commit `ea47cc3ba348d1f222330ec3f4f483838a818d93`, captured on **9 August 2026**. It extends [TEO-CAPSULE-0007](0007-2026-08-09-routing-not-access.md). Earlier accepted capsules remain immutable.

## Why this moment was preserved

Capsule 0007 established a boundary: routing is architecture; provider access is not.

The next question was harder: once access had been removed from the routing decision, were the actual primary, fallback, escalation, and verifier assignments still the best fit for the current provider landscape and TEO's own responsibility model?

Mission Control put those assignments under review.

The result was not a broad model churn event. It was a targeted recalibration of executable routing roles based on workload shape, capability fit, failure behavior, provider diversity, verifier independence, model lifecycle state, and TEO's existing authority boundaries.

This capsule preserves the moment when that review stopped being documentation and became executable policy.

## Mission Control routing decision

### Bounded engineering execution

- primary: `gpt-5.6-terra`
- routine cross-provider coding fallback: `gemini-3.6-flash`
- planning and difficult cross-component reasoning support: `gpt-5.6-sol`
- semantic review: `claude-sonnet-5`

Terra remains the implementation lane for inspect, edit, test, debug, and verify work where the dominant problem is bounded execution.

The key change is that routine coding fallback no longer depends on a preview research model. Stable Gemini 3.6 Flash now provides the ordinary cross-provider coding fallback.

### Difficult engineering reasoning

- primary reasoning lane: `gpt-5.6-sol`
- cross-provider reasoning fallback and challenge: `claude-sonnet-5`
- preview Gemini Pro remains conditional where explicit preview acceptance and research-heavy context justify it

Sol remains distinct from Terra. It is used when the dominant work is root-cause synthesis, hidden-invariant discovery, cross-system reasoning, or implementation-aware planning.

### Economical bounded throughput

The active `high_volume_simple` route became:

```text
Gemini 3.5 Flash-Lite
  -> Claude Haiku 4.5 fallback
  -> GPT-5.6 Luna independent alternative
```

This was the largest direct route promotion in the recalibration.

Gemini 3.5 Flash-Lite moved from evaluated candidate status to the primary bounded-throughput implementation because current provider evidence positioned it specifically for stable, low-cost, high-throughput work.

Haiku 4.5 became the first cross-provider fallback rather than the primary.

Luna remains an independent economical alternative.

Gemini 3.6 Flash remains available when the task requires stronger bounded agentic or multimodal capability rather than pure throughput optimization.

## Fresh verifier topology

The throughput route was not changed in isolation. Mission Control also recalibrated verifier assignment so fallback and provider-failure paths do not inherit stale verification assumptions.

The resulting topology is:

### Normal Flash-Lite execution

```text
Executor: Gemini 3.5 Flash-Lite
Verifier: Claude Sonnet 5
```

### Model-specific fallback to Haiku

```text
Executor: Claude Haiku 4.5
Verifier: Gemini 3.6 Flash
```

### Google provider-level unavailability

```text
Executor: Claude Haiku 4.5
Verifier: GPT-5.6 Sol
```

The verifier is therefore reassigned as part of canonical redispatch rather than treated as a fixed companion to the task type.

This preserves two principles simultaneously:

- the verifier must remain independent from the executor
- provider diversity must survive fallback and recovery, not only the happy path

## Frontier reasoning without global promotion

Claude Fable 5 was not made a universal replacement for Opus 5.

Mission Control instead assigned it a narrow frontier-escalation role for unusually difficult unresolved reasoning, long-horizon orchestration, or cross-system authority conflicts after established Opus/Sol paths remain inconclusive.

The established high-consequence route remains:

- Claude Opus 5 for selected high-consequence specialist reasoning
- GPT-5.6 Sol as cross-provider fallback
- independent Gemini verification where applicable and explicitly allowed
- qualified human authority where critical effective risk requires it

The lesson is intentional:

> A model can be more capable in aggregate without becoming the correct default for every governed responsibility.

## Runtime reconciliation

The routing update was not accepted until the reference runtime and its tests represented the same topology.

The migration therefore included:

- `high_volume_simple` route policy
- active runtime worker eligibility
- guarded Gemini canary support for `gemini-3.5-flash-lite`
- model-specific fallback behavior
- provider-scoped fallback behavior
- verifier rotation
- bounded retry fixtures
- provider circuit-breaker fixtures
- runtime telemetry fixtures
- live independent-verification fixtures
- documentation truth

One important control was preserved during this work: Google `UNAVAILABLE` remains a transient failure class for bounded retry under the same dispatch. The circuit-breaker tests were corrected to reflect that policy rather than weakening the retry contract merely to make the new topology pass.

The recalibration was accepted only after the complete reference gate returned green.

## What did not change

This milestone did **not** redefine TEO's architecture around model brands.

The following remain unchanged:

- Mission Control resolves responsibility before implementation
- teams, workers, and specialists remain the durable organizational layer
- effective risk remains non-lowerable
- fallback must remain capability-valid
- preview models require explicit acceptance
- critical-risk human authority is not removed by model capability
- provider access remains outside routing
- API, OAuth, subscription-backed access, delegated identity, connectors, and other legitimate access mechanisms remain execution-boundary concerns
- a newer model triggers evaluation, not automatic promotion

The model assignments changed because the evidence and workload fit justified them. The architecture did not need to change in order to absorb those assignments.

## README reconciliation

After the executable policy was merged, the root README was put under a second Mission Control review.

That pass removed a contradiction in which Gemini 3.5 Flash-Lite was simultaneously described as the active primary route and as a candidate awaiting promotion.

The README now distinguishes clearly between:

- active primary routes
- routine fallbacks
- independent alternatives
- conditional escalation
- route-specific verification
- preview-only routes
- evidence-gated frontier capacity

The README remains explanatory. Canonical authority continues to live in policy, registries, model evidence, and executable conformance.

## Operational state at this snapshot

At this point TEO is at the reference-operational functional-v1 boundary with:

- ten active organizational teams
- 84 workers
- 78 preserved specialist role cards
- deterministic Team -> Worker -> Specialist routing
- current model and reasoning-effort assignments
- provider-diverse fallback
- provider-diverse independent verification
- guarded live execution for the bounded canary
- bounded transient retry
- model and provider scoped canonical redispatch
- persistent provider-family circuit state
- abandoned half-open probe recovery
- content-free runtime telemetry
- strict external schemas
- model-freshness governance
- provider-access separation governance
- regulated evidence controls
- provisional operational-evidence tooling
- community human-calibration stewardship path
- reproducible reference CI

The system is not a production distributed orchestration platform. It is a runnable, governed reference control plane whose routing decisions can evolve without replacing the architecture that produces them.

## Known remaining horizons

The following remain post-v1 stewardship, evidence-strengthening, or production-hardening work:

- independent blinded human calibration through the GitHub community
- human-ground-truth verifier-quality evidence
- evidence-governed expansion of live execution scope
- distributed circuit-state coordination
- distributed telemetry export and retention
- streaming execution
- source-backed historical cost attribution
- route-outcome learning
- qualified-human approval integration
- continued regulated-evidence expansion after the pilot proves maintainability
- future model-route recalibration as provider catalogs evolve

None of these justify weakening the current control plane or confusing missing production infrastructure with missing routing architecture.

## Message to future stewards

This capsule records a practical test of TEO's founding claim.

The models changed.

The route assignments changed.

The fallback topology changed.

The verifier topology changed.

The architecture did not need to be rebuilt.

That is the point.

Do not preserve a route because it is familiar.

Do not replace a route because a model is fashionable.

Use Mission Control. Establish the responsibility. Check current provider reality. Evaluate capability and failure behavior. Preserve fallback validity and verifier independence. Then change the route if the evidence justifies it.

> **Models evolve. Responsibilities endure.**

The signal persists.

---

**Recorded under the stewardship of Sylvester Roxas.**
