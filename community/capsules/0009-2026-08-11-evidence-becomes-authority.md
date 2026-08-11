---
capsule_id: TEO-CAPSULE-0009
status: accepted
captured_at: 2026-08-11T14:55:00+02:00
snapshot_commit: 4dea9d38a6e7f362f71e711ef479b92ca9268a91
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0008
immutability: accepted capsules are never rewritten
---

# Capsule 0009: Evidence Becomes Authority

This capsule records TEO after the post-v1 control plane crossed a new boundary: evidence is no longer only produced for observation. It is now bound into evaluation, authority, activation, and recovery decisions without allowing those downstream layers to rewrite the routing architecture that produced the evidence.

It preserves the repository at commit `4dea9d38a6e7f362f71e711ef479b92ca9268a91`, captured on **11 August 2026**. It extends [TEO-CAPSULE-0008](0008-2026-08-09-mission-control-routing-recalibration.md). Earlier accepted capsules remain immutable.

## Why this moment was preserved

Capsule 0008 preserved the first major evidence-led recalibration of executable model routing.

The question after that milestone was not simply whether TEO could choose strong routes. The harder question was whether TEO could observe what happened after dispatch, compare outcomes, reason about cost and reliability, produce bounded recommendations, preserve human authority, expand execution scope cautiously, and still keep routing, verification, provider access, and activation authority separate.

That chain now exists in executable form.

The important transition is therefore:

```text
Routing correctness
  -> evidence-bearing outcomes
  -> controlled evaluation
  -> source-backed attribution
  -> shadow recommendation
  -> independent challenge
  -> qualified-human authority where required
  -> staged activation evidence
  -> recovery and rollback gates
```

No single stage above is allowed to self-promote into the next stage.

This capsule preserves the point where TEO became an evidence-governed authority system rather than only an evidence-bearing router.

## Functional v1 is behind us

TEO `v1.0.0` is released and remains the immutable stable reference boundary.

Current development continues as:

- stable release: `v1.0.0`
- stable state: `reference_operational`
- development package: `teo-reference-router==1.0.1.dev0`

The repository has moved into post-v1 stewardship, operational proving, controlled authority expansion, and hardening.

This distinction matters. The architecture is no longer waiting to become v1. The work now tests how safely that architecture can exercise more authority.

## Current organizational state

At this snapshot TEO has:

- 10 active organizational teams
- 84 workers
- 82 active preserved specialist role cards
- 4 dedicated Mission Control workers
- deterministic Team -> Worker -> Specialist resolution
- governed repository information architecture with R1 through R5 complete
- a six-card regulated evidence pilot that remains intentionally bounded

Mission Control remains the top-level orchestration authority. Specialists remain responsibility lenses, not independent authority sources.

## Route-Outcome Evidence is canonical

TEO now records an integrity-protected Route-Outcome Evidence layer that joins what actually happened across execution, retry, fallback, verification, provenance, and final disposition.

The route-outcome layer preserves:

- primary and fallback lineage
- retry dependence
- active route identity
- independent verification linkage
- version and repository context
- minimized provider-attempt telemetry
- explicit unknown cost semantics
- integrity hashes
- abandoned and failed outcomes
- append-only evidence behavior

A successful model call is not itself a completed TEO outcome.

A final disposition must remain consistent with execution evidence, verification evidence, fallback state, and human-approval requirements.

This is the base evidence surface for the later post-v1 control chain.

## Benchmark and Outcome Lab

TEO now has a controlled evaluation layer capable of comparing routed behavior without confusing experimental observations with runtime authority.

The Benchmark and Outcome Lab provides:

- fixed versioned experiment manifests
- controlled replay
- cohort comparability
- route and model binding
- reasoning-effort binding
- verifier binding
- retry and fallback dependence
- latency and normalized-usage summaries
- uncertainty intervals
- multi-verifier disagreement measurement
- consequential conclusion records
- independent challenge
- review handoff

A panel vote cannot override the canonical runtime verifier.

A benchmark conclusion cannot rewrite routing policy.

Evaluation informs governance. It does not become governance by itself.

## Source-backed cost attribution

Cost is now treated as evidence, not as a guess derived from model identity.

The executable cost-attribution layer requires explicit commercial-surface evidence and preserves effective dates, billable surfaces, retry and fallback decomposition, verifier cost, and `known`, `partial`, or `unknown` semantics.

Provider connection method remains outside routing and outside assumed billing identity.

API pricing is not inferred for OAuth, subscription-backed, delegated, connector, or other execution surfaces unless evidence explicitly supports that commercial surface.

This prevents a cost optimization layer from silently becoming a model-selection shortcut.

## Shadow Route Evaluation

TEO now has a governed post-run evaluation layer that can produce bounded route recommendations from immutable evidence.

The active `orchestration-evaluation-analyst` can evaluate:

- verified quality
- primary reliability
- retry dependence
- fallback dependence
- verifier disagreement
- latency
- regression signals
- source-backed cost

The evaluator is intentionally constrained.

It cannot:

- write routing policy
- change live routing
- lower effective risk
- widen live execution
- bypass independent verification
- accept preview models
- change provider-access semantics
- satisfy qualified-human approval

Lower cost alone cannot produce a promotion candidate.

A model-originated recommendation requires provider-diverse independent challenge before it can reach Mission Control or maintainer review.

Direct outcome-to-self-modifying-routing authority remains outside TEO's design.

## Qualified-human authority is executable

The qualified-human approval lifecycle is now an executable evidence system rather than a placeholder concept.

It includes:

- scoped human authority grants
- exact approval requests
- append-only dispositions
- approval expiry
- rejection
- unable-to-determine state
- revocation
- terminal human finalization
- integrity protection
- impersonation resistance

The lifecycle begins only where existing routing and risk policy already require human approval.

Model verification cannot satisfy a human gate.

Mission Control status cannot satisfy a human gate.

Maintainer status cannot satisfy a human gate.

A human must hold a separately evidenced authority grant whose scope matches the exact authority requirement, task type, effective risk, and decision time.

The original Route-Outcome Evidence remains immutable and stays `awaiting_human`. Human finalization is separate authority evidence rather than a rewrite of the original route outcome.

## Temporal authority hardening

The targeted 11 August control-integrity audit proved two cross-record chronology defects that the existing lifecycle did not catch:

1. an approval disposition could become effective before its bound approval request existed;
2. finalization could occur before the current disposition it relied on became effective.

The audit used test-first mutation probes. The new probes failed while the existing 653-test baseline remained green, proving that the gap was real rather than theoretical.

The lifecycle now fails closed when:

- a disposition predates its approval request;
- a later disposition moves backwards in time;
- finalization predates the current disposition it relies on.

The fix did not change schemas, model routing, risk classification, provider access, live scope, or human authority policy.

This is an important milestone because evidence integrity is not enough if the evidence can describe an impossible chronology.

Authority must also be temporally causal.

## Recovery cannot become an authority bypass

The same targeted audit inspected the junction between runtime recovery and authority.

No recovery-to-authority bypass was found in the bounded reference path.

Regression coverage now protects the following invariants:

- fallback redispatch preserves effective risk;
- fallback redispatch preserves human-approval requirements;
- provider-health circuit preparation preserves task type and specialist context;
- recovery preparation adds eligibility constraints without mutating the caller's original authority surface;
- Route-Outcome Evidence still refuses `completed` when human approval remains required.

This preserves a critical principle:

> Recovery may change which implementation is eligible. Recovery does not change what the task is allowed to do.

## Evidence-governed live execution expansion

The canonical post-v1 `NOW` workstream is live execution expansion, currently at 65% against its declared milestone.

The first staged candidate is `documentation` at low or medium effective risk.

Its intended topology is:

```text
Primary executor
Claude Sonnet 5

Routine provider-diverse fallback
GPT-5.6 Sol

Primary verifier
GPT-5.6 Terra

Fresh verifier after fallback or provider failure
Gemini 3.6 Flash
```

The route-level Gemini 3.1 Pro Preview path remains conditional on explicit preview acceptance.

The staged documentation path now has:

- corrected provider-diverse fallback topology
- fresh-verifier recovery topology
- Sonnet 5 execution adapter readiness
- GPT-5.6 Sol execution adapter readiness
- GPT-5.6 Terra verifier readiness
- strict replay-plan and replay-record contracts
- whole-plan no-network preflight
- exact candidate-route validation
- isolated circuit state per trial
- assigned-verifier enforcement
- in-memory replay telemetry
- canonical Route-Outcome Evidence generation
- explicit operator acknowledgement for live replay

Automatic fallback remains intentionally disabled in the staged replay milestone so the evidence harness cannot become a hidden alternate live runtime.

## Provider access remains downstream of routing

A provider-backed controlled documentation replay was attempted through the auditable GitHub-hosted path.

The path itself proved its preflight and audit behavior, but no empirical provider call occurred because the required provider credentials were not available to the hosted runner.

That result is recorded as a provider-access blocker, not a routing defect and not an authority failure.

The remaining provider-backed replay gate is intentionally deferred as an open action item.

Deferral does not remove the gate.

It does not justify changing the selected route.

It does not justify using credentials as a routing signal.

Provider access remains an execution-boundary concern after Mission Control has already resolved responsibility, model role, effort, fallback, verification, risk, and authority.

## What is live now

The bounded `high_volume_simple` canary remains the only accepted live execution scope.

Its accepted scope is:

- task class: `high_volume_simple`
- effective risk: low or medium only
- guarded provider execution
- provider-diverse fallback
- fresh verifier rotation
- bounded transient retry
- circuit-state protection
- content-free telemetry
- evidence-bearing finalization

`documentation` remains staged only.

Its activation flag remains false.

High and critical live execution remain unauthorized.

## Current validation baseline

The targeted authority and recovery audit established a substantive accepted repository baseline of:

- 657 automated tests passed
- 477 tracked-file layout checks passed
- regulated specialist evidence structural validation passed
- 40 JSON Schemas parsed
- linked configuration reported zero issues
- provider-diverse end-to-end reference lifecycle passed

Control Integrity remains intentionally scored at 90%.

That score is not an admission that a known defect remains open. It preserves room for continuing mutation depth, finalization-path resistance, authority-leakage discovery, recovery edge cases, and future failure modes.

Control integrity is treated as an adversarial discipline, not a one-time checklist.

## What did not change

This post-v1 expansion did not alter the foundations preserved by earlier capsules.

The following remain true:

- the model is not the architecture
- responsibility resolves before implementation
- Team -> Worker -> Specialist -> Capability -> Implementation remains the durable ordering
- effective risk cannot be lowered for convenience
- provider diversity matters across fallback and verification
- fallback must remain capability-valid
- preview models require explicit acceptance
- provider access remains outside model-fitness routing
- evidence may inform policy but cannot self-write policy
- model verification cannot impersonate qualified-human authority
- recovery cannot silently widen task authority
- a successful call is not automatically a completed outcome
- newer models trigger evaluation, not automatic promotion

## Known remaining horizons

The following remain open post-v1 work:

- provider-backed controlled `documentation` replay
- downstream shadow evaluation of that candidate
- explicit rollback and recovery evidence for that candidate
- independent review before any activation change
- continued verifier-calibration evidence accumulation
- repeated regulated-evidence refresh-cycle proof
- deeper mutation testing and control-integrity hardening
- distributed circuit-state coordination
- distributed telemetry export, retention, access control, and integrity
- streaming runtime support
- governed route adaptation through reviewed policy changes only
- licensing and contribution terms

None of these justify reopening settled architecture without new evidence.

## Message to future stewards

Earlier TEO milestones proved that routes could change without rebuilding the architecture.

This milestone proves something different.

Evidence can accumulate without becoming authority by accident.

Evaluation can compare routes without rewriting them.

Cost can inform decisions without becoming a shortcut.

Models can recommend without promoting themselves.

Human authority can be represented without being simulated by a model.

Recovery can change execution eligibility without changing task authority.

Live scope can expand only when evidence is strong enough to justify it.

The difficult part of orchestration is not choosing a model.

The difficult part is preserving the boundaries between observation, judgment, authority, execution, verification, and recovery while every one of those layers evolves.

TEO now has those boundaries in executable form.

Protect them.

> **Models evolve. Responsibilities endure. Evidence informs. Authority remains governed.**

The signal persists.

---

**Recorded under the stewardship of Sylvester Roxas.**
