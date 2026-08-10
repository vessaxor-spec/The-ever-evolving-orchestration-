# Orchestration Evaluation Analyst Authority Review

**Status:** Completed research review  
**Recorded:** 2026-08-10  
**Activation decision:** Not authorized by this review

## Executive result

**PASS WITH DESIGN CORRECTION.**

The responsibility gap is real, but the initial placement under `Mission Control -> orchestration` is not the cleanest authority boundary.

The stronger allocation is:

```text
Primary team: Research
Worker: analytics
Specialist: orchestration-evaluation-analyst

Supporting teams:
- Mission Control
- Verification
- Review
- Platform & Reliability
```

Mission Control should remain the consumer and decision owner for route-policy recommendations rather than the owner of the evaluator itself.

This separation reduces the risk that the routing authority becomes its own performance judge.

## Sources inspected

The review compared the candidate against current live responsibility surfaces, including:

- `community/workers/workers.yaml`, especially the Mission Control `orchestration` worker
- `community/workers/extensions/analytics-worker.yaml`
- `community/specialists/agents-orchestrator.md`
- `community/specialists/data-analyst.md`
- `community/specialists/workflow-optimizer.md`
- `policy/routing/extensions/specialist-spawn-team-routing.yaml`
- `policy/routing/core/specialist-model-routing.yaml`
- `docs/stewardship/roadmap.md`
- `research/roadmaps/intelligence-control-plane.md`

## Duplication test

### `agents-orchestrator`

Current ownership:

- pipeline architecture
- agent activation and handoff protocols
- workflow runtime selection
- execution observability
- pipeline state and recovery
- loop and stall handling
- token budgeting
- operator gate placement

Overlap with candidate:

- consumes run evidence
- may inspect prior run logs
- understands orchestration semantics

Unowned remainder:

- cohort-level comparison across completed dispatches
- route-outcome evidence synthesis across primary, retry, fallback, verifier, final outcome, latency, usage, and cost
- statistical evidence sufficiency for routing claims
- regression detection across routing or model changes
- shadow recommendations about future routing configurations

Conclusion: **not duplicate** if the candidate remains post-run and does not redesign or operate pipelines.

### `data-analyst`

Current ownership:

- statistical inference
- experiment design
- causal reasoning
- cohort analysis
- data quality and reproducibility
- pipeline diagnostics
- model QA
- uncertainty-aware decision briefing

Overlap with candidate:

- substantial methodological overlap

Unowned remainder:

- TEO-specific route semantics
- Team -> Worker -> Specialist -> Implementation interpretation
- effective-risk and capability-eligibility constraints
- primary versus fallback-assisted outcome accounting
- verifier-independence and verifier-calibration interpretation
- routing-policy version and model-generation evidence portability
- TEO-specific shadow recommendation states and non-authority boundary

Conclusion: **specialization is justified, but ownership should reuse `Research -> analytics`.** The candidate is a narrow TEO routing-evaluation specialization of the analytics worker, not a new analytical worker.

### `workflow-optimizer`

Current ownership:

- business-process mapping
- automation ROI
- tool selection
- deterministic workflow versus bounded-agent decisions
- future-state workflow design

Overlap with candidate:

- cost and efficiency tradeoffs
- workflow measurement

Unowned remainder:

- TEO routing-policy outcome evaluation
- verifier and fallback interactions
- model-route evidence and risk invariants

Conclusion: **not duplicate**.

### Verification Team

Current ownership:

- independent output and control verification
- reproducibility and acceptance checks
- verifier calibration evidence

Overlap with candidate:

- consumes verification evidence
- requires independent result review

Unowned remainder:

- longitudinal route-quality evaluation across populations of completed dispatches
- shadow routing recommendations

Conclusion: **complementary, not duplicate**. Verification should challenge the analyst's result rather than own the route recommendation.

## Why Research ownership is stronger than Mission Control ownership

The initial hypothesis placed the candidate under Mission Control because the subject is routing.

That is understandable but creates an avoidable governance tension:

```text
Mission Control
  -> selects and governs routes
  -> owns evaluator of its own route decisions
  -> receives evaluator recommendation
```

A cleaner pattern is:

```text
Mission Control
  -> owns routing decision

Research / analytics
  -> evaluates completed route evidence
  -> produces shadow recommendation

Verification / Review
  -> challenge the evaluation

Mission Control / maintainers
  -> decide whether policy change is justified
```

This is not absolute organizational independence, because all roles remain inside TEO, but it reduces role coupling and preserves a clearer separation of duties.

## Worker fit

The existing `analytics` worker already owns:

- analytical question scoping
- data-quality validation
- statistical inference
- experiment design and analysis
- cohort analysis
- causal reasoning
- reproducible analysis
- decision briefing

Its authority boundaries already prohibit correlation-as-causation and require stated evidence, methods, samples, uncertainty, and accountable ownership.

The candidate therefore does not justify a new worker.

## Proposed model lane correction

The initial design proposed `opus_critical_reasoning`.

The better default is **`sol_deep_engineering`**, aligned with the existing `data-analyst` specialist and the quantitative/reproducible nature of the work.

Proposed future route:

- primary: GPT-5.6 Sol
- routine fallback: Claude Sonnet 5
- independent verifier: Gemini 3.1 Pro Preview

Why:

- the work is evidence-heavy and analytical rather than a binding consequential decision;
- the specialist has a high risk floor because its output may influence policy, but it has no direct policy authority;
- a binding or critical routing decision should be escalated outside the analyst rather than making the analyst itself the default high-consequence authority;
- this avoids unnecessary Opus default use while preserving independent provider-diverse verification.

A future critical policy decision may independently route to stronger governance or review reasoning as required by the owning authority.

## Authority leakage checklist

| Risk | Result | Required control |
|---|---|---|
| Candidate becomes second live router | PASS | post-run only; no route-write authority |
| Candidate applies own recommendation | PASS | shadow recommendation only |
| Mission Control grades itself | PASS WITH CORRECTION | primary ownership moved to Research |
| Analyst treats correlation as causation | PASS | explicit causal classification and comparability gate |
| Analyst optimizes against weak verifier | PASS | verifier quality is part of evidence |
| Cost lowers governance floor | PASS | hard constraints outrank economics |
| Model successor inherits old evidence | PASS | concrete-version evidence binding |
| Failures disappear from analysis | PASS | failures, retries, fallback, uncertainty retained |
| Missing price becomes zero | PASS | unknown remains unknown |
| Telemetry becomes user reconstruction | PASS | content-minimized telemetry boundary |
| Specialist self-approves activation | PASS | separate activation change required |
| Specialist forces constant optimization | PASS | `NO_CHANGE_JUSTIFIED` and `INSUFFICIENT_EVIDENCE` are first-class outputs |

## Main residual risks

### 1. Goodhart pressure

If route owners optimize directly for one published score, the metric can stop representing actual quality.

Control: preserve multi-dimensional evidence, independent fixtures, verifier calibration context, failures, and negative controls.

### 2. Selection bias

TEO intentionally routes different task classes and risks to different configurations. Raw operational success rates are therefore confounded by policy selection.

Control: stratification, controlled replay, declared experiments, or explicit descriptive-only conclusions.

### 3. Circular verification

A route can appear strong if evaluated by a permissive or correlated verifier.

Control: verifier-quality evidence, provider-diverse independent verification, and criterion-level disagreement analysis.

### 4. Model and policy drift

Historical route evidence can become stale after a model generation, reasoning policy, runtime, verifier, tool, or routing change.

Control: bind evidence to concrete configuration and classify portability before reuse.

### 5. Optimization churn

An evaluator that must always recommend a change will create policy instability.

Control: successful terminal states include `NO_CHANGE_JUSTIFIED` and `INSUFFICIENT_EVIDENCE`.

## Activation prerequisites

A future activation should not proceed until all of the following are true:

1. The role card is accepted with the Research/analytics ownership correction.
2. The active specialist allocation is added explicitly and does not create a new worker or team.
3. Specialist model policy adds the candidate through `sol_deep_engineering` unless later evidence justifies a different lane.
4. Conformance proves high-risk floor preservation and critical escalation for any live-policy mutation request.
5. Mutation tests fail if shadow-only authority, verifier independence, privacy boundaries, version-scoped evidence, or causal restrictions are weakened.
6. Route-outcome input records are sufficiently defined to make the analysis reproducible.
7. Any new cost evidence uses source-backed, effective-dated pricing.
8. The active specialist count and documentation truth are updated atomically.
9. A separate maintainer-reviewed activation change explicitly authorizes the role.

## Incidental repository truth finding

`docs/stewardship/roadmap.md` still states that TEO has 78 preserved specialist role cards, while the active repository reached 81 after the workforce expansion.

This is a documentation-truth inconsistency, not an authority defect in this candidate package. It should be corrected separately or as a tightly scoped documentation fix before relying on the roadmap count as current truth.

## Final decision

**Candidate responsibility: ACCEPT.**  
**Initial Mission Control ownership: REJECT.**  
**Corrected Research -> analytics ownership: ACCEPT.**  
**New worker: REJECT.**  
**New team: REJECT.**  
**Live activation in this research change: REJECT.**

The candidate survives the gap test only as a narrow, post-run TEO route-evaluation specialist under the existing Research analytics worker with Mission Control remaining the downstream routing decision authority.
