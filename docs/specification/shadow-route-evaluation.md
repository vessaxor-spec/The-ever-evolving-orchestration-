# Shadow Route Evaluation

## Status

This specification defines TEO's version 1 governed Shadow Route Evaluation contract.

Shadow evaluation is a post-run analytical layer owned by `orchestration-evaluation-analyst`. It evaluates immutable execution and controlled-evaluation evidence and may produce a bounded recommendation for independent challenge and Mission Control or maintainer review.

It is not a router, a policy writer, an approval authority, or an automated model-selection loop.

## Core sequence

```text
Canonical evidence
  -> shadow evaluation input
  -> orchestration-evaluation-analyst
  -> bounded shadow recommendation
  -> independent challenge
  -> Mission Control or maintainer review
  -> optional later policy proposal through normal governance
```

No step in the shadow-evaluation layer can directly modify routing policy or live execution.

## Source evidence

A shadow evaluation consumes exact evidence records rather than mutable summaries.

The version 1 join supports:

- benchmark experiment manifests;
- benchmark reports;
- canonical Route-Outcome Evidence;
- source-backed route-cost attribution;
- consequential benchmark conclusions;
- independent benchmark-conclusion verification;
- benchmark-conclusion review handoffs.

Every declared source is identified by both a stable record ID and an integrity hash. The benchmark manifest is bound by its canonical SHA-256 digest. Route-cost evidence must bind the exact Route-Outcome Evidence integrity hash for the corresponding outcome.

For consequential comparisons, the evaluator requires the complete challenged conclusion chain. The benchmark conclusion must bind the exact report, its independent verification must bind the exact conclusion, and the review handoff must bind both. The conclusion must have been independently verified and advanced only to `mission_control_or_maintainer_review`.

## Analyst execution identity

A specialist name is not enough to establish independence.

Every shadow input records the concrete provider family and model operating `orchestration-evaluation-analyst`. This identity is evidence for the later independent challenge. A model-originated shadow recommendation cannot be verified by the same provider family or model that produced the recommendation.

## Evidence sufficiency gate

The evaluator checks evidence sufficiency before it can produce a change candidate.

At minimum:

- the benchmark report must bind the exact manifest;
- the report and manifest must reference the same Route-Outcome Evidence IDs;
- the supplied route-outcome set must match that declared evidence set;
- candidate and baseline must be declared benchmark candidates;
- benchmark comparability must have passed;
- benchmark evidence must not be marked insufficient;
- candidate and baseline metrics must exist;
- consequential evaluation requires measured multi-verifier disagreement;
- consequential evaluation requires the complete independently challenged benchmark-conclusion chain;
- a requested source-backed cost comparison requires cost attribution for every candidate and baseline outcome.

A failed gate produces `INSUFFICIENT_EVIDENCE` or rejects malformed evidence. Missing evidence is never converted into favorable evidence.

## Recommendation states

Every completed shadow evaluation emits exactly one specialist #82 disposition:

- `NO_CHANGE_JUSTIFIED`
- `INSUFFICIENT_EVIDENCE`
- `SHADOW_CHANGE_CANDIDATE`
- `REGRESSION_INVESTIGATION`
- `POLICY_OR_CONTROL_CONCERN`

These states are evidence classifications. None is routing authority.

## Change-candidate doctrine

`SHADOW_CHANGE_CANDIDATE` is intentionally difficult to reach.

The reference evaluator requires a controlled comparable evidence set where the candidate:

- has a higher verified completion rate than the declared baseline;
- does not have a lower primary verified completion rate;
- does not increase fallback dependence;
- does not increase retry dependence;
- has no declared candidate regression signal;
- is not blocked by unresolved human-authority or missing-verification evidence.

For consequential comparisons, the independently challenged benchmark-conclusion chain must also be present.

The result remains a shadow-only review candidate. It is not a causal superiority claim and it does not authorize deployment.

## Anti-Goodhart controls

### Final success is not enough

A route that reaches a higher final completion rate by relying more heavily on fallback is not automatically an improvement. Primary success, retry dependence, and fallback dependence remain separate signals.

### Cost cannot be routing authority

Lower source-backed cost can support a recommendation, but lower cost alone can never create `SHADOW_CHANGE_CANDIDATE`.

Cost remains subordinate to:

- verified outcome quality;
- effective risk;
- required capabilities;
- verifier independence;
- provider diversity;
- human authority;
- reliability;
- evidence sufficiency.

Unknown or partial cost remains unknown or partial. It is never treated as zero.

### Verifier pass rate is not ground truth

Measured verifier disagreement remains diagnostic evidence. Shadow evaluation cannot override the canonical runtime verifier or optimize solely for the easiest verifier to satisfy.

### Regression preempts promotion

A declared regression signal produces `REGRESSION_INVESTIGATION` before any shadow change candidate is considered.

### Human authority is preserved

Relevant `awaiting_human` or `verification_missing` outcomes produce `POLICY_OR_CONTROL_CONCERN`. Shadow evaluation cannot convert unresolved authority or missing verification into a route-improvement recommendation.

## Recommendation record

The recommendation preserves:

- candidate and baseline identity;
- verified completion delta;
- primary verified completion delta;
- fallback-assistance delta;
- retry-assistance delta;
- latency delta;
- verifier-disagreement status;
- candidate regression status;
- source-backed cost state and totals when fully known;
- supporting evidence;
- contradictory evidence;
- limitations;
- an optional shadow-only proposed-change description.

Every record is integrity protected.

## Authority denials

Every shadow recommendation explicitly records all of the following as false:

- `policy_write_authority`
- `live_routing_authority`
- `live_scope_change_authority`
- `effective_risk_lowering_authority`
- `capability_bypass_authority`
- `verifier_bypass_authority`
- `preview_acceptance_authority`
- `provider_access_change_authority`
- `qualified_human_approval_satisfied`

Changing any of these values violates the schema and fails validation.

Provider access remains outside routing. Shadow evidence cannot turn API keys, OAuth sessions, subscriptions, CLI access, connector access, or billing state into a model-fitness signal.

## Independent recommendation challenge

A shadow recommendation does not advance directly to Mission Control review.

The independent challenge evaluates:

- exact source binding;
- evidence sufficiency;
- preservation of uncertainty;
- preservation of authority boundaries;
- confirmation that cost was not treated as primary authority;
- absence of unsupported causality claims.

The challenge decision is one of:

- `verified`
- `rejected`
- `needs_human`

For a model-originated analyst recommendation, the verifier must be provider-diverse and cannot reuse the analyst model.

## Review handoff

Only an independently challenged recommendation can produce a review handoff.

The handoff destination is always:

`mission_control_or_maintainer_review`

Its status reflects the independent challenge:

- verified -> `ready_for_review`
- rejected -> `rejected`
- needs_human -> `needs_human`

The handoff explicitly records:

- independent verification performed: true;
- policy-write authority: false;
- live-routing authority: false;
- qualified-human approval satisfied: false.

A `ready_for_review` handoff is evidence for a human-governed decision process. It is not permission to edit policy.

## Persistence

The reference implementation provides append-only JSONL persistence for shadow recommendations. Persisted records are revalidated for schema, semantic, authority, and integrity correctness when read.

The reference sink is single-process evidence storage. Distributed coordination, retention policy, access control, and streaming are separate runtime-hardening concerns.

## Relationship to future route adaptation

Any future route adaptation must remain downstream of this layer and preserve the canonical sequence:

```text
Evidence
  -> evaluation
  -> shadow recommendation
  -> independent challenge and verification
  -> Mission Control and maintainer decision
  -> reviewed policy change
  -> CI
  -> deployment
  -> post-change evaluation
  -> rollback if regression
```

Direct outcome-to-self-modifying-routing authority is outside TEO's design.
