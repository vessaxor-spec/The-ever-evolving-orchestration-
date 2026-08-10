# TEO Progress Tracker

**Status:** active stewardship record  
**Last reconciled:** 2026-08-10  
**Stable release:** `v1.0.0`  
**Current development line:** `teo-reference-router==1.0.1.dev0`

This document is the canonical operational progress tracker for The Ever-Evolving Orchestration.

It answers four questions:

1. Where is TEO now?
2. Which workstreams are complete, operational, in progress, planned, or future?
3. What is the current milestone for each workstream?
4. What evidence or gate must be satisfied before the workstream advances?

This tracker does not create runtime, routing, release, or governance authority. Normative behavior remains defined by the applicable policy, registry, schema, activation, and release artifacts. Strategic direction remains in [`roadmap.md`](roadmap.md) and longer-horizon research remains under [`research/`](../../research/).

## Current system snapshot

| Surface | Current state |
|---|---|
| Stable release | `v1.0.0` in `reference_operational` state |
| Development package | `1.0.1.dev0` |
| Organizational teams | 10 |
| Workers | 84 |
| Active specialists | 82 |
| Mission Control workers | 4 |
| Latest activation milestone | `orchestration-evaluation-analyst` active on `Research -> analytics` |
| Latest validated test suite | 602 tests passed |
| Regulated evidence pilot | 6 specialists, intentionally bounded |
| Repository information architecture | R1 through R5 complete |
| Guarded live execution | bounded `high_volume_simple` canary at low or medium effective risk |
| High and critical live execution | not authorized |

The roster counts above are expected to match executable `ConfigBundle` composition and are protected by documentation-truth tests.

## Progress scoring method

Progress percentages are estimates against the **current declared milestone**, not claims that a workstream can never evolve further.

Rules:

- `100%` means the current milestone has been accepted or operationalized. It does not mean future compatible evolution is prohibited.
- A percentage must correspond to concrete completed and remaining criteria described in this tracker or linked records.
- Scope changes require the estimate and milestone criteria to be recalibrated rather than preserving a misleading historical percentage.
- Percentages are directional planning aids. Normative readiness comes from evidence, tests, policy, review, and applicable approval gates.
- A workstream may remain operational at `100%` while receiving maintenance, compatibility, evidence-refresh, or gap-driven extensions.

### Status vocabulary

| Status | Meaning |
|---|---|
| Complete | Current declared milestone accepted |
| Operational | Current capability is active and maintained |
| In progress | Material implementation or evidence work remains |
| Planned | Scope is accepted but the implementation milestone has not materially started |
| Future | Valuable later work without current execution priority |
| Pending | Decision or external stewardship action remains |

## Portfolio view

| Workstream | Status | Progress | Current milestone | Next gate |
|---|---|---:|---|---|
| Core architecture and governance | Complete | 100% | Functional v1 reference contract | Maintain invariants through compatible evolution |
| Repository information architecture | Complete | 100% | R1 through R5 | Preserve governed placement and lifecycle boundaries |
| Team, worker, and specialist architecture | Operational | 100% | 10 teams, 84 workers, 82 active specialists | Add roles only after proven responsibility-gap and authority review |
| Control integrity | Operational | 90% | Post-v1 hardening with conformance and mutation resistance | Continue closing uncovered finalization, authority, and recovery mutation gaps as discovered |
| Verifier calibration evidence | In progress | 70% | Deterministic and empirical verifier evidence | Strengthen repeatability, disagreement, adversarial, and route-specific evidence |
| Regulated specialist evidence pilot | In progress | 60% | Six-card maintainability pilot | Demonstrate repeated refresh cycles, expiry, provenance, authority resolution, and mutation resistance |
| Route-outcome evidence | Complete | 100% | Canonical executable route-outcome evidence contract | Preserve schema/version compatibility and feed controlled evaluation |
| Benchmark and Outcome Lab | Complete | 100% | Controlled evaluation, live replay, disagreement, and conclusion handoff | Preserve compatibility and feed governed downstream evaluation |
| Source-backed cost attribution | Complete | 100% | Effective-dated reproducible route-level attribution | Maintain first-party price evidence and feed governed downstream evaluation |
| Shadow route evaluation | Complete | 100% | Governed recommendation-only evidence loop | Preserve evidence and authority boundaries through later reviewed adaptation |
| Qualified-human approval lifecycle | In progress | 40% | Explicit approval record and authority handoff | Integrate identity, role, disposition, evidence, and audit linkage into runtime flow |
| Live execution expansion | In progress | 30% | Bounded low and medium risk canary | Expand only task-class by task-class after evidence, verification, recovery, and authority gates pass |
| Distributed runtime hardening | Future | 20% | Single-process reference behavior proven | Add coordinated state, concurrency-safe export, access control, retention, integrity, and recovery |
| Licensing and contribution terms | Pending | 10% | Public repository with no reuse license selected | Select licensing and contribution terms before representing TEO as open source |

## NOW

### Qualified-human approval lifecycle

Complete the explicit runtime approval lifecycle for work that already requires qualified-human authority under TEO policy.

This workstream is next because TEO now has a complete evidence chain from route outcomes through controlled evaluation, source-backed cost, shadow recommendation, independent challenge, and Mission Control or maintainer review. The remaining authority gap is not another model-evaluation layer. It is the explicit runtime record and handoff for the human authority that policy already requires.

Completion criteria for the current milestone:

- define a versioned qualified-human approval request and disposition contract;
- bind every approval request to the exact dispatch, effective risk, task identity, required authority reason, execution evidence, verification evidence, and applicable review evidence;
- record the approving human's qualified role or authority class without turning personal identity into routing authority;
- distinguish requested, approved, rejected, expired, revoked, and unable-to-determine states where applicable;
- require evidence that the approving role is authorized for the declared authority requirement;
- prevent model, specialist, verifier, Mission Control, or maintainer records from impersonating qualified-human approval;
- prevent a shadow recommendation or review handoff from satisfying qualified-human approval;
- make approval decisions integrity protected, auditable, and reproducible from declared evidence;
- preserve explicit refusal when required authority is missing, expired, ambiguous, or outside scope;
- bind finalization to the exact approval record where policy requires human authority;
- keep provider access, model selection, and billing identity outside the approval-qualification decision;
- add conformance and mutation tests that fail if qualified-human requirements can be bypassed or self-satisfied.

The milestone implements authority evidence that existing policy already requires. It does not broaden which tasks require human approval and it does not widen live execution by itself.

## NEXT

### Evidence-governed live execution expansion

After the qualified-human approval lifecycle is complete, reconsider task-class-by-task-class live-scope expansion using the now-complete route-outcome, Benchmark Lab, cost-attribution, shadow-evaluation, recovery, verification, and authority evidence chain.

High and critical live execution remains unauthorized unless and until the applicable task class independently satisfies its authority, capability, verification, recovery, evidence, and human-approval gates.

## LATER

### Governed route adaptation

Any future adaptive-routing mechanism should preserve this sequence:

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

Direct outcome-to-self-modifying-routing authority is outside the current TEO design.

### Distributed runtime hardening

Production-grade distributed persistence, coordination, streaming, telemetry export, retention, and access controls remain later runtime work. They must not be confused with missing core orchestration architecture.

## Workstream completion criteria

### Core architecture and governance, 100%

Current milestone evidence includes the released `v1.0.0` reference contract, Team -> Worker -> Specialist -> Capability -> Implementation ordering, risk controls, provider-diverse fallback, independent verification, and a runnable reference control plane.

### Repository information architecture, 100%

R1 through R5 are complete. Current authority, research, history, routing, workers, models, registries, tests, and release records have governed locations and repository-layout validation.

### Team, worker, and specialist architecture, 100%

The current target roster is active and deterministically spawnable. Future specialist additions are gap-driven extensions and do not reduce current milestone completion.

### Control integrity, 90%

The main invariants are implemented and heavily tested. The remaining ten percent represents continuing mutation depth, finalization-path resistance, authority-leakage checks, and new failure modes uncovered by future audits. It is intentionally not scored as permanently complete because control integrity is an ongoing adversarial discipline.

### Verifier calibration evidence, 70%

The fixed corpus, deterministic checks, empirical instrumentation, provider-diverse observations, blinded review tooling, and machine-panel path exist. Additional repeatability, route-specific, adversarial, and accumulated empirical evidence remains useful. Independent human calibration remains optional research and is not a release or routing gate.

Benchmark Lab measures multi-verifier disagreement for controlled evaluations, but that diagnostic capability does not by itself complete the broader verifier-calibration evidence program.

### Regulated specialist evidence pilot, 60%

The six-card pilot has dated authoritative claims, validation, expiry behavior, authority resolution, and mutation resistance. Repeated refresh-cycle maintainability must be demonstrated before broader rollout is justified.

### Route-outcome evidence, 100%

The canonical executable route-outcome join is implemented with strict schema validation, primary/fallback lineage, retry preservation, independent-verification linkage, version context, explicit unknown cost, content minimization, provenance, integrity checks, abandoned-outcome support, append-only reference persistence, deterministic conformance tests, and reproducible analyst-ready fixtures. Reference Implementation CI run #407 validated the milestone with 546 passing tests, 414 tracked-file layout checks, regulated evidence validation, 19 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

Future distributed persistence, continuous evaluation feeds, and source-backed cost calculation are separate declared workstreams and do not keep this milestone open.

### Benchmark and Outcome Lab, 100%

The current milestone is complete.

The controlled-evaluation foundation provides fixed synthetic fixtures, a versioned experiment manifest, explicit harness identity, balanced repeated trials, strict cohort comparability, offline executor-only isolation, route/model/reasoning/verifier/runtime/policy/registry/tool binding, primary-versus-fallback and retry dependence, descriptive regression signals, Wilson uncertainty intervals, latency and normalized-usage summaries, explicit missingness, reproducible integrity-protected reports, JSONL persistence, and deterministic conformance coverage.

Controlled live replay adds a schema-validated replay plan, system-to-system claim boundary, additive route-isolation constraints, no-network normal-routing preflight, exact candidate and assigned-verifier matching, active retry-budget alignment, isolated per-trial circuit state, guarded canary execution, live assigned verification, canonical route-outcome generation, replay-plan digest binding, and live capability-context comparability without rewriting source fixtures. Reference Implementation CI run #423 validated that gate with 562 passing tests, 428 tracked-file layout checks, regulated evidence validation, 23 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

Multi-verifier disagreement adds versioned provider-diverse panel plans, blinded structured observations, exact trial/output/outcome binding, explicit missing-observation insufficiency, status/criterion/human-reason disagreement measurement, and a hard rule that panel voting cannot override the canonical runtime verifier or route-outcome disposition.

Consequential conclusion control adds integrity-protected conclusion, independent-verification, and review-handoff records. Consequential comparative or regression conclusions require measured disagreement and independent challenge. Model-originated conclusions require provider-diverse verification. Review handoffs have no policy-write authority and explicitly do not satisfy qualified-human approval.

Reference Implementation CI run #429 validated the completed executable milestone with 574 passing tests, 437 tracked-file layout checks, regulated evidence validation, 28 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

Compatible maintenance, larger fixture banks, additional observational evidence, and integration into Shadow Route Evaluation may continue without reopening this completed milestone.

### Source-backed cost attribution, 100%

The current milestone is complete.

The executable contract provides strict pricing-evidence and route-cost schemas, integrity-protected first-party pricing records, explicit billable-surface identity, effective-dated price selection, overlap rejection, decimal arithmetic, primary/retry/fallback decomposition, separate verifier cost, and `known`, `partial`, or `unknown` attribution semantics.

The first-party evidence set covers the standard paid API surfaces currently relevant to the reference runtime and verifier paths for OpenAI, Anthropic, and Google. Provider-explicit effective windows are preserved where available. Current-only evidence is marked `verified_from` rather than backdated. Unsupported long-context, cache, tool, storage, regional, processing-tier, or additional-charge dimensions fail closed instead of being guessed.

Provider connection mechanism remains outside routing and is not treated as a billing identity. A subscription, OAuth-backed CLI, connector, or other surface is attributed only when evidence exists for that explicit commercial surface. API list prices are never inferred solely from provider and model identity.

Execution usage remains in canonical Route-Outcome Evidence. The live verification path preserves normalized verifier usage through an additive evidence helper while keeping the existing `VerificationResult` compatibility API unchanged. Pricing changes do not rewrite historical route outcomes.

Reference Implementation CI run #437 validated the executable milestone with 585 passing tests, 444 tracked-file layout checks, regulated evidence validation, 30 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

Future pricing refreshes, negotiated or subscription billing surfaces, additional provider-native charge dimensions, and downstream use in Shadow Route Evaluation are compatible maintenance or separate governed extensions and do not keep this milestone open.

### Shadow route evaluation, 100%

The current milestone is complete.

The governed shadow-evaluation layer binds benchmark manifests, benchmark reports, Route-Outcome Evidence, source-backed cost records, and consequential benchmark conclusion challenge records by immutable record identity and integrity hash. Consequential evaluation requires the exact conclusion, independent verification, and review handoff chain bound back to the exact benchmark report.

The evaluator records the concrete provider/model operating `orchestration-evaluation-analyst`, checks evidence sufficiency before recommendation, preserves verified quality, primary reliability, retry dependence, fallback dependence, verifier disagreement, latency, regression, and source-backed cost as separate signals, and emits only the five bounded specialist #82 states.

Anti-Goodhart controls prevent lower cost alone from creating a change candidate and prevent a final-quality gain from being promoted when retry or fallback dependence worsens. Regression signals preempt promotion. Unresolved human-authority or missing-verification outcomes surface as policy/control concerns. A `SHADOW_CHANGE_CANDIDATE` is explicitly shadow-only and is neither a causal superiority claim nor deployment authorization.

Every recommendation denies policy-write, live-routing, live-scope, risk-lowering, capability-bypass, verifier-bypass, preview-acceptance, provider-access-change, and qualified-human-approval authority. Model-originated recommendations require provider-diverse independent challenge before a handoff can advance to `mission_control_or_maintainer_review`. The handoff still has no policy-write or live-routing authority and cannot satisfy qualified-human approval.

Reference Implementation CI run #445 validated the executable milestone with 602 passing tests, 451 tracked-file layout checks, regulated evidence validation, 34 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

Future policy adaptation remains a separate governed stage requiring Mission Control and maintainer decision, reviewed policy change, CI, deployment, post-change evaluation, and rollback if regression.

### Qualified-human approval lifecycle, 40%

Critical-risk policy already preserves qualified-human requirements, but a complete explicit runtime approval lifecycle with authority identity, disposition, evidence, and audit linkage remains incomplete.

Benchmark and shadow review handoffs explicitly do not satisfy qualified-human approval. Completion of the evidence and shadow-evaluation layers therefore makes this authority lifecycle the current priority rather than reducing its remaining scope.

### Live execution expansion, 30%

Guarded live execution, retry, fallback redispatch, verification, circuit state, telemetry, controlled replay, economic evidence, and governed shadow evaluation exist for a bounded canary. Broader task classes and high or critical execution remain evidence-gated.

Benchmark Lab, cost attribution, and Shadow Route Evaluation completion do not widen live execution scope.

### Distributed runtime hardening, 20%

The reference semantics for recovery, circuit state, telemetry, audit, execution, evaluation, cost evidence, and shadow recommendation are proven in the current single-process reference architecture. Distributed coordination, persistence, access control, retention, and streaming remain later work.

### Licensing and contribution terms, 10%

The public stewardship posture exists, but no open-source reuse license has been selected. External reuse and contribution terms remain pending.

## Update protocol

Update this tracker when a merged change materially affects:

- current roster counts;
- stable or development release identity;
- completion criteria;
- workstream status or percentage;
- NOW, NEXT, or LATER ordering;
- live-execution scope;
- regulated-pilot scope;
- accepted strategic direction.

Every update should be grounded in merged repository state, executable validation, accepted research, or explicit maintainer decision. Do not update percentages merely because time passed or a model/provider release occurred.

When parallel sessions are active, reconcile against current `main` before editing this tracker so already-completed work is not reintroduced as pending.

## Related records

- [`roadmap.md`](roadmap.md): canonical stewardship roadmap
- [`research/roadmaps/intelligence-control-plane.md`](../../research/roadmaps/intelligence-control-plane.md): longer-horizon intelligence-control-plane research
- [`docs/releases/v1.0.0.md`](../releases/v1.0.0.md): immutable functional-v1 release contract
- [`docs/releases/v1-readiness.md`](../releases/v1-readiness.md): current release/readiness boundary
- [`docs/history/audits/post-v1-hard-audit-2026-08-10.md`](../history/audits/post-v1-hard-audit-2026-08-10.md): durable post-v1 hard audit
- [`community/specialists/orchestration-evaluation-analyst.md`](../../community/specialists/orchestration-evaluation-analyst.md): active post-run route evaluator
- [`../specification/route-outcome-evidence.md`](../specification/route-outcome-evidence.md): canonical route-outcome evidence contract
- [`../specification/benchmark-outcome-lab.md`](../specification/benchmark-outcome-lab.md): completed Benchmark and Outcome Lab current milestone
- [`../specification/source-backed-cost-attribution.md`](../specification/source-backed-cost-attribution.md): completed source-backed cost-attribution contract
- [`../specification/shadow-route-evaluation.md`](../specification/shadow-route-evaluation.md): completed governed Shadow Route Evaluation contract
