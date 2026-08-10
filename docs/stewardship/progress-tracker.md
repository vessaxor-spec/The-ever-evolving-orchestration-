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

This tracker does not create runtime, routing, release, or governance authority. Normative behavior remains defined by the applicable policy, registry, schema, activation, and release artifacts. The strategic direction remains in [`roadmap.md`](roadmap.md) and longer-horizon research remains under [`research/`](../../research/).

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
| Latest validated test suite | 556 tests passed |
| Regulated evidence pilot | 6 specialists, intentionally bounded |
| Repository information architecture | R1 through R5 complete |
| Guarded live execution | bounded `high_volume_simple` canary at low or medium effective risk |
| High and critical live execution | not authorized |

The current roster counts above are expected to match the executable `ConfigBundle` composition and are protected by documentation-truth tests.

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
| Benchmark and Outcome Lab | In progress | 60% | Reproducible controlled evaluation foundation | Add controlled live replay, multi-verifier disagreement, and consequential-conclusion verification handoff |
| Source-backed cost attribution | Planned | 10% | Effective-dated pricing and cost contract | Add versioned pricing evidence and route-level cost calculation |
| Shadow route evaluation | Planned | 5% | Governed recommendation-only evaluation loop | Connect Outcome Lab evidence to specialist #82 without live policy-write authority |
| Qualified-human approval lifecycle | In progress | 40% | Explicit approval record and authority handoff | Integrate identity, role, disposition, evidence, and audit linkage into runtime flow |
| Live execution expansion | In progress | 30% | Bounded low and medium risk canary | Expand only task-class by task-class after evidence, verification, recovery, and authority gates pass |
| Distributed runtime hardening | Future | 20% | Single-process reference behavior proven | Add coordinated state, concurrency-safe export, access control, retention, integrity, and recovery |
| Licensing and contribution terms | Pending | 10% | Public repository with no reuse license selected | Select licensing and contribution terms before representing TEO as open source |

## NOW

### Benchmark and Outcome Lab

Build controlled evaluation on top of the completed route-outcome evidence contract.

The first executable foundation now provides fixed synthetic fixtures, declared harness and candidate identity, balanced repeated-trial bindings, strict comparability checks, version-scoped route-outcome joins, primary/retry/fallback separation, descriptive regression signals, uncertainty intervals, explicit missingness, integrity-protected reports, and reproducible conformance fixtures.

The remaining material gates for the current milestone are controlled live replay, multi-verifier disagreement measurement, and an explicit independent-verification handoff for consequential evaluation conclusions.

Completion criteria for the current milestone:

- define fixed benchmark fixtures with explicit task class, risk, capability, route, verifier, and version context;
- support replayable evaluation cases without silently changing task identity or authority boundaries;
- compare routes and concrete model versions only across sufficiently comparable cohorts;
- compare reasoning-effort settings where the underlying capability and task remain comparable;
- preserve primary-route outcomes separately from retry-assisted and fallback-assisted outcomes;
- measure verifier disagreement without optimizing merely for verifier pass rate;
- detect regressions across declared runtime, model, verifier, tool, registry, or policy changes;
- report uncertainty, missingness, evidence sufficiency, and practical limitations rather than forcing a winner;
- produce reproducible experiment records that can be independently checked;
- require independent verification for consequential evaluation conclusions;
- keep all analyst outputs recommendation-only and outside live policy-write authority.

The milestone is complete only when controlled benchmark and replay evidence can be reproduced from declared fixtures and route-outcome records. A dashboard or aggregate score alone is insufficient.

## NEXT

### Source-backed cost attribution

Add effective-dated price evidence and versioned calculations only after the route-outcome identity and usage contract is stable enough to bind cost correctly.

Cost optimization must remain subordinate to capability, risk, verification, provider diversity, and human-authority constraints.

### Shadow route evaluation

Connect completed outcome evidence and controlled evaluation to `orchestration-evaluation-analyst` and allow bounded outputs such as:

- `NO_CHANGE_JUSTIFIED`
- `INSUFFICIENT_EVIDENCE`
- `SHADOW_CHANGE_CANDIDATE`
- `REGRESSION_INVESTIGATION`
- `POLICY_OR_CONTROL_CONCERN`

A shadow recommendation is evidence for review. It is not routing authority.

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

### Wider live execution

Broaden live execution only after the applicable task class demonstrates reliable authority, capability, verification, telemetry, recovery, evidence, and human-approval behavior.

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

The fixed corpus, deterministic checks, empirical instrumentation, provider-diverse observations, blinded review tooling, and provisional machine-panel path exist. Additional repeatability, route-specific, disagreement, adversarial, and accumulated empirical evidence remains useful. Independent human calibration remains optional research and is not a release or routing gate.

### Regulated specialist evidence pilot, 60%

The six-card pilot has dated authoritative claims, validation, expiry behavior, authority resolution, and mutation resistance. Repeated refresh-cycle maintainability must be demonstrated before broader rollout is justified.

### Route-outcome evidence, 100%

The canonical executable route-outcome join is implemented with strict schema validation, primary/fallback lineage, retry preservation, independent-verification linkage, version context, explicit unknown cost, content minimization, provenance, integrity checks, abandoned-outcome support, append-only reference persistence, deterministic conformance tests, and reproducible analyst-ready fixtures. Reference Implementation CI run #407 validated the milestone with 546 passing tests, 414 tracked-file layout checks, regulated evidence validation, 19 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

Future distributed persistence, continuous evaluation feeds, and source-backed cost calculation are separate declared workstreams and do not keep this milestone open.

### Benchmark and Outcome Lab, 60%

The first executable controlled-evaluation foundation is implemented. It provides fixed synthetic fixtures, a versioned experiment manifest, explicit harness identity, balanced repeated trials, strict cohort comparability, executor-only isolation, route/model/reasoning/verifier/runtime/policy/registry/tool binding, primary-versus-fallback and retry dependence, descriptive regression signals, Wilson uncertainty intervals, latency and normalized-usage summaries, explicit missingness, reproducible integrity-protected reports, JSONL persistence, and deterministic conformance coverage. Reference Implementation CI run #414 validated the foundation with 556 passing tests, 424 tracked-file layout checks, regulated evidence validation, 22 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

The remaining milestone work is material: execute controlled fixtures through candidate routes under a declared live replay harness, measure disagreement using multiple independent benchmark verifier observations without Goodharting pass rate, and require an explicit independent-verification handoff before consequential evaluation conclusions can advance. Those gaps keep the workstream in progress and prevent a 100% claim.

### Source-backed cost attribution, 10%

The governance doctrine is established: pricing must be effective-dated, source-backed, versioned, and separate from raw usage telemetry. The executable attribution layer remains to be built.

### Shadow route evaluation, 5%

The analyst and recommendation states exist, canonical route-outcome evidence is available, and the first controlled evaluation foundation now exists. The continuous evidence feed, multi-verifier/independent-challenge handoff, and governed evaluation runner into specialist #82 are not yet implemented, so this workstream remains planned.

### Qualified-human approval lifecycle, 40%

Critical-risk policy already preserves qualified-human requirements, but a complete explicit runtime approval lifecycle with authority identity, disposition, evidence, and audit linkage remains incomplete.

### Live execution expansion, 30%

Guarded live execution, retry, fallback redispatch, verification, circuit state, and telemetry exist for a bounded canary. Broader task classes and high or critical execution remain evidence-gated.

### Distributed runtime hardening, 20%

The reference semantics for recovery, circuit state, telemetry, audit, and execution are proven in the current reference architecture. Distributed coordination, persistence, access control, retention, and streaming remain later work.

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
- [`../specification/benchmark-outcome-lab.md`](../specification/benchmark-outcome-lab.md): current Benchmark and Outcome Lab foundation
