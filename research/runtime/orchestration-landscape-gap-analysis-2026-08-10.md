# Orchestration Landscape Gap Analysis

**Date:** 2026-08-10  
**Status:** research  
**Authority:** non-normative  
**Scope:** post-v1 runtime and specialist-gap research  
**Reconciled against:** `docs/stewardship/progress-tracker.md` at main commit `4f6a062442748804770c4fde11926e499fad7c44`

## Purpose

This research evaluates the broader GitHub orchestration landscape for ideas that can strengthen The Ever-Evolving Orchestration without changing its core thesis or turning TEO into another agent framework, workflow product, or provider-specific runtime.

The objective is not feature accumulation. The objective is to identify proven control-plane disciplines, determine whether TEO already has an equivalent responsibility boundary, and isolate only those gaps that remain genuinely non-duplicative.

TEO remains responsibility-first and vendor-neutral. Any future implementation derived from this research must preserve Team -> Worker -> Specialist authority, non-lowerable risk, capability-aware routing, provider-diverse fallback, independent verification, evidence-backed freshness, provider-access separation, and the current stewardship sequencing defined by the canonical Progress Tracker.

## Canonical sequencing boundary

The canonical operational sequencing is maintained in `docs/stewardship/progress-tracker.md`.

This research does not create a competing roadmap or priority system.

At the current reconciliation point, the tracker defines:

```text
COMPLETED
  Route-Outcome Evidence Contract, 100%

NOW
  Benchmark and Outcome Lab, In progress / 60%

NEXT
  Source-backed cost attribution
  Shadow route evaluation

LATER
  Governed route adaptation
  Wider live execution
  Distributed runtime hardening
```

The tracker records 10 organizational teams, 84 workers, and 82 active specialists. The latest specialist activation is `orchestration-evaluation-analyst` on `Research -> analytics`.

The Benchmark and Outcome Lab foundation is executable and validated. Its remaining material gates are controlled live replay, multi-verifier disagreement measurement, and explicit independent-verification handoff for consequential evaluation conclusions.

## Executive finding

No missing foundational TEO layer was identified.

The strongest external signal remains that mature orchestration systems increasingly treat execution state, context, action authority, lineage, and operational evidence as first-class control-plane objects rather than incidental runtime details.

The repository has now absorbed part of that signal without changing TEO's architecture:

1. Route-Outcome Evidence is complete and provides canonical, version-scoped, integrity-protected post-run evidence.
2. Benchmark and Outcome Lab has an executable controlled-evaluation foundation with fixed fixtures, repeated trials, comparability gates, uncertainty, regression signals, and reproducible reports.
3. Shadow route evaluation remains separate and recommendation-only.
4. Generalized durable execution, distributed telemetry, and distributed state remain later work.

The aligned maturity path is therefore:

```text
Routing authority
  -> route-outcome evidence
  -> controlled benchmark and replay evidence
  -> shadow evaluation
  -> governed adaptation
  -> later distributed runtime hardening
```

Execution-envelope, action-authority, observability, and durable-state ideas remain valuable, but they must attach to that sequence rather than bypass it.

## Recalibrated disposition

| Research finding | Tracker alignment | Current disposition |
|---|---|---|
| Orchestration Trace and Lineage Contract | Route-Outcome Evidence, complete | Core lineage and version-scoped outcome evidence are implemented. Do not create a parallel trace authority. Distributed trace export remains later. |
| Outcome Evidence and Route Learning | Complete -> NOW -> NEXT -> LATER | Route-outcome evidence is complete. Controlled evaluation is NOW. Shadow evaluation is NEXT. Governed adaptation remains later. |
| Specialist Execution Envelope | Supporting research for NOW and later runtime work | The outcome-relevant identity/version subset is already implemented. Revisit broader context/tool/action envelope only if controlled replay or later runtime work proves a concrete need. |
| Action Authority Plane | Qualified-human approval lifecycle plus Assurance | Retain as a bounded research candidate. Do not create a new authority layer before overlap and lifecycle analysis. |
| Resource Budget and Admission Contract | NEXT cost attribution plus LATER runtime hardening | Cost fields follow source-backed attribution. General admission and concurrency controls remain later unless a current canary or replay harness proves an earlier need. |
| Durable Dispatch Lifecycle Contract | LATER: Distributed runtime hardening | Defer generalized durable orchestration semantics. Current retry, fallback, circuit, recovery, and evidence contracts remain authoritative. |

## Completed contribution: Route-Outcome Evidence Contract

The earlier version of this research identified route-outcome evidence as the highest-priority implementation need. That work is now complete.

The canonical contract now preserves or joins the decision-relevant evidence this research called for, including:

```text
dispatch identity
primary and fallback lineage
task class
effective risk
team
worker
specialist
required capabilities
selected implementation
reasoning effort
verifier assignment
attempt and retry evidence
fallback dependence
final disposition
failure evidence
latency
normalized usage
model and verifier identity
runtime version
policy version
registry version
tool-version context
provenance
integrity
```

Unknown material fields remain unknown rather than being represented as zero or inferred facts.

The contract also distinguishes primary-route success, retry-assisted success, fallback-assisted success, verification failure, verification missingness, execution failure, and abandoned outcomes.

This implementation closes the earlier research question of whether TEO needed a separate trace or route-outcome authority. It does not. The canonical route-outcome record is the evaluation substrate.

## Immediate contribution to NOW

### Benchmark and Outcome Lab

The broader orchestration landscape supports the current Benchmark and Outcome Lab through patterns such as:

- fixed fixtures;
- declared harness conditions;
- replayable cases;
- route and concrete model-version comparisons;
- reasoning-effort comparisons;
- repeated trials for nondeterministic systems;
- fallback-dependence analysis;
- verifier disagreement analysis;
- regression detection;
- reproducible experiment records;
- explicit uncertainty, missingness, and comparability gates.

The first executable foundation now implements a substantial subset of those requirements on top of the canonical Route-Outcome Evidence Contract.

Implemented and validated:

- fixed synthetic benchmark fixtures with explicit task, risk, capability, criteria, suite version, and integrity metadata;
- declared experiment manifests with study type, claim scope, candidate identity, harness identity, stopping rule, repeated-trial count, and exact trial bindings;
- strict fixture, experiment, and report JSON Schemas;
- balanced repeated trials without silent missing-trial drops;
- exact route-outcome binding to provider, model, reasoning effort, verifier, runtime, routing policy, registry, and tool-version context;
- executor-only comparability rules that reject non-executor drift;
- primary-route, retry-assisted, and fallback-assisted outcome separation;
- verified-completion and primary-completion Wilson intervals;
- pass-any-trial and pass-all-trials reliability views;
- latency and normalized-usage summaries with explicit missingness;
- descriptive regression signals without policy authority;
- integrity-protected reproducible reports and JSONL persistence;
- deterministic conformance tests.

Reference Implementation CI #417 validated the reconciled foundation with 556 passing tests, 424 tracked-file layout checks, regulated evidence validation, 22 parsed JSON Schemas, valid linked configuration, and provider-diverse end-to-end verification.

### Remaining NOW gates

The research should now be used to strengthen only the remaining declared Benchmark Lab gates:

1. **Controlled live replay.** Execute declared fixtures through candidate routes under a fixed, versioned harness while preserving task identity, authority boundaries, tool profile, budgets, and route-outcome provenance.
2. **Multi-verifier disagreement.** Join multiple independent benchmark-verifier observations without optimizing merely for verifier pass rate.
3. **Consequential-conclusion verification handoff.** Require independent challenge before a consequential evaluation conclusion can advance to Mission Control or maintainer review.

These gates should reuse the existing benchmark fixture, experiment, report, and route-outcome contracts rather than introducing a second evaluation format.

## NEXT alignment

### Source-backed cost attribution

Cost claims must be:

- source-backed;
- effective-dated;
- version-scoped;
- bound to measured usage or a declared calculation basis;
- explicit when unknown.

Cost must remain subordinate to capability, risk, verification, provider diversity, and human-authority constraints.

The broader Resource Budget and Admission Contract should not be implemented ahead of this pricing and identity foundation unless a current bounded runtime or replay use case produces a concrete need.

### Shadow route evaluation

The original research proposed an `Orchestration Evaluation Scientist` specialist. That proposal remains withdrawn.

TEO already has specialist #82, `orchestration-evaluation-analyst`, with the relevant boundary:

- cohort-level route-outcome analysis;
- evidence sufficiency;
- fallback and retry diagnostics;
- verifier disagreement;
- regression detection;
- cost-latency-quality tradeoffs;
- shadow recommendations;
- no live routing or policy-write authority.

No new orchestration-evaluation specialist should be created from this research.

The current controlled-evaluation foundation is not yet the governed Shadow Route Evaluation workstream. The remaining handoff must connect sufficient Benchmark Lab evidence to specialist #82 while retaining recommendation-only outputs such as `NO_CHANGE_JUSTIFIED`, `INSUFFICIENT_EVIDENCE`, `SHADOW_CHANGE_CANDIDATE`, `REGRESSION_INVESTIGATION`, and `POLICY_OR_CONTROL_CONCERN`.

## LATER alignment

### Governed route adaptation

The research supports the tracker sequence:

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

Direct outcome-to-self-modifying-routing authority remains outside the current TEO design.

### Distributed runtime hardening

The following research concepts belong primarily here unless an earlier workstream proves they are needed sooner:

- generalized dispatch lifecycle state;
- durable checkpoints;
- resumable long-running dispatches;
- ownership or lease semantics;
- dead-letter behavior;
- concurrency-safe state coordination;
- distributed trace export;
- retention and integrity controls;
- admission and concurrency controls.

TEO already has bounded retry, fallback redispatch, provider-family circuit state, recovery semantics, route-outcome evidence, and a controlled evaluation foundation. Those controls should not be collapsed into a generic workflow engine while distributed hardening remains a future workstream.

## Landscape signals

The following repositories and design families were useful because they expose operational disciplines rather than merely additional agent abstractions.

### HumanLayer 12-Factor Agents

Source: https://github.com/humanlayer/12-factor-agents

Useful patterns:

- own the context window;
- own control flow;
- unify execution and business state deliberately;
- expose pause and resume behavior;
- keep agent responsibilities bounded;
- treat tool calls as explicit structured actions.

TEO use: evidence for scoped context and explicit action boundaries. Not a reason to replace TEO's routing architecture.

### Conductor OSS

Source: https://github.com/conductor-oss/conductor

Useful patterns:

- durable execution;
- persisted workflow steps;
- retries and timeout semantics;
- replay and restart behavior;
- orchestration separated from worker logic.

TEO use: reference material for LATER distributed runtime hardening.

### Hatchet

Source: https://github.com/hatchet-dev/hatchet

Useful patterns:

- durable task composition;
- intermediate result persistence;
- task fan-out;
- execution history;
- composable task boundaries.

TEO use: evidence for later bounded parallelism and dependency state, not an immediate runtime dependency.

### Dapr Agents

Source: https://github.com/dapr/dapr-agents

Useful patterns:

- durable workflows;
- state management;
- scoped access controls;
- telemetry;
- event-driven coordination;
- vendor-neutral deployment posture.

TEO use: reference for later state, action scope, and telemetry boundaries while preserving provider-access separation.

### HumanLayer Agent Control Plane

Source: https://github.com/humanlayer/agentcontrolplane

Useful patterns:

- distributed scheduling;
- asynchronous outer-loop execution;
- human feedback calls;
- explicit control-plane framing.

TEO use: reference for externally blocked and long-running work during later distributed runtime hardening.

### Microsoft Conductor

Source: https://github.com/microsoft/conductor

Useful patterns:

- deterministic routing outside the model loop;
- source-controlled workflow definitions;
- repeatable multi-agent paths;
- parallel execution.

TEO use: independent reinforcement of TEO's existing choice to keep routing authority outside model self-selection.

## Candidate control-plane contracts

### Specialist Execution Envelope

Potential future structured fields:

```text
specialist_identity
worker_binding
task_instruction
intent_snapshot
effective_risk
scoped_context
context_provenance
allowed_tools_or_actions
required_capabilities
implementation_assignment
reasoning_effort
output_contract
verification_contract
policy_version
registry_version
```

Current boundary: the outcome-relevant identity and version subset is already implemented. Do not expand into a new runtime authority layer merely because the research proposed a broader envelope. Revisit only if controlled live replay or later distributed runtime work proves a concrete context, tool-scope, or handoff need that existing contracts cannot represent.

### Action Authority Plane

Provider access and action authority are different concerns.

Authentication answers whether a runtime can reach a provider or external system. Action authority answers whether a selected specialist may perform a consequential operation.

Potential action classes:

```text
read_only
local_mutation
reversible_external_mutation
financial_or_legal_commitment
credential_or_permission_change
public_release
safety_critical_action
irreversible_external_action
```

Potential controls:

- allow and deny scopes;
- side-effect classification;
- approval requirements;
- delegation depth;
- inherited authority ceiling;
- action receipts;
- before and after state references where obtainable;
- verifier visibility into executed actions.

Current boundary: analyze this alongside the existing qualified-human approval lifecycle and Assurance responsibilities before proposing a new authority plane.

### Resource Budget and Admission Contract

Potential budgets:

- maximum attempts;
- maximum wall-clock duration;
- maximum model-compute or token budget when measurable;
- maximum source-backed cost budget;
- maximum specialist spawn count;
- maximum parallel branches;
- provider concurrency constraints;
- deadline or freshness horizon.

Resource constraints may restrict or refuse execution, but must never silently lower effective risk or weaken verification.

Current boundary: cost identity belongs NEXT. A replay harness may define bounded experiment budgets as evaluation conditions, but generalized admission and concurrency control remain later unless a bounded runtime use case proves an earlier need.

### Durable Dispatch Lifecycle Contract

Potential future states:

```text
created
admitted
dispatched
running
waiting_external
waiting_approval
checkpointed
retry_pending
fallback_pending
verification_pending
completed
refused
failed_terminal
cancelled
dead_lettered
```

Current boundary: LATER distributed runtime hardening. Do not collapse retry, fallback, escalation, circuit state, human approval, and evaluation state into one generic failure mechanism.

## Specialist-gap recalibration

The canonical tracker marks Team, Worker, and Specialist architecture as Operational at 100% for its current milestone. New roles are gap-driven extensions only.

The research originally identified four possible roles. Reconciliation with current main reduces that to three inactive hypotheses.

### Withdrawn: Orchestration Evaluation Scientist

**Disposition:** do not create.

Reason: specialist #82, `orchestration-evaluation-analyst`, already owns the proposed responsibility boundary with explicit shadow-only authority and conformance coverage.

### Candidate A: Observability and Telemetry Engineer

**Confidence:** medium after implementation evidence  
**Likely primary team:** Platform and Reliability

Possible distinct responsibilities:

- distributed trace architecture;
- vendor-neutral telemetry semantics;
- correlation and causality across orchestration events;
- SLI and SLO instrumentation design;
- sampling and cardinality control;
- telemetry privacy and minimization;
- incident reconstruction;
- telemetry schema evolution.

Overlap that must be disproven before activation:

- Site Reliability Engineer;
- Performance Engineer;
- Platform Engineer;
- Distributed Systems Engineer;
- orchestration-evaluation-analyst;
- existing Mission Control orchestration ownership.

Current disposition: no activation. Route-Outcome Evidence and the first Benchmark Lab foundation were implemented cleanly using existing roles, so those milestones did not prove a distinct observability-specialist gap. Revisit if later distributed trace export, cross-process telemetry semantics, or operational SLI/SLO ownership remains unassigned after overlap analysis.

### Candidate B: Context and Memory Systems Engineer

**Confidence:** medium  
**Likely primary team:** Systems Engineering

Possible distinct responsibilities:

- runtime context scoping;
- provenance and freshness metadata;
- context compaction and loss analysis;
- session-state boundaries;
- durable memory read and write policy;
- context invalidation;
- retrieval boundaries;
- context handoff;
- stale-authority and context-contamination controls.

Current disposition: defer. The tracker does not identify context or memory systems as a current execution gap. Revisit when controlled replay, an execution-envelope proposal, or distributed-runtime work reaches an implementation gate that existing roles cannot own cleanly.

### Candidate C: Agent Authorization and Security Engineer

**Confidence:** medium-high  
**Likely primary team:** Assurance

Possible distinct responsibilities:

- tool and action authorization;
- least-privilege specialist execution;
- delegated authority boundaries;
- prompt-injection-to-action containment;
- MCP, A2A, connector, and future protocol trust boundaries;
- confused-deputy prevention;
- action provenance and receipts;
- capability-to-permission mapping;
- revocation and quarantine controls for compromised tools or integrations.

Overlap that must be disproven before activation:

- Application Security Engineer;
- DevSecOps Engineer;
- Security Engineer;
- Red Team Advisor;
- Privacy Engineer;
- existing qualified-human approval policy and runtime work.

Current disposition: retain as a research candidate tied to the qualified-human approval lifecycle and future action-authority design. Do not activate before a responsibility and authority overlap audit.

## Specialists not recommended yet

Do not add the following solely because external projects expose these concepts:

- Workflow Reliability Engineer;
- Durable Execution Engineer;
- Sandbox Engineer;
- MCP Specialist;
- A2A Specialist;
- Agent Protocol Engineer;
- generic Prompt Engineer;
- Swarm Engineer.

Their responsibilities currently fit within existing Distributed Systems, SRE, Platform Engineering, Systems Engineering, Application Security, AI Engineering, Mission Control, or orchestration workers.

## Patterns to reject

- Specialist-count competition.
- Framework absorption.
- Model-selected governance authority.
- Credential-driven routing.
- Direct outcome-to-self-modifying-routing authority.
- Premature distributed-platform expansion ahead of the tracker.

## Promotion gates

### Gate 1: NOW workstream contribution

Before adding a new evaluation or runtime contract, determine whether the requirement belongs inside one of the current Benchmark and Outcome Lab remaining gates.

For the current milestone, the relevant questions are whether the proposal is necessary for controlled live replay, multi-verifier disagreement, or independent-verification handoff.

Success means stronger controlled evidence without creating competing authority or duplicated state.

### Gate 2: Existing-role overlap analysis

Before creating a new specialist:

1. identify the exact unowned responsibility;
2. compare it against current role cards and worker ownership;
3. prove the gap cannot be addressed by clarifying an existing role or handoff;
4. define primary and supporting team ownership;
5. define risk and authority boundaries;
6. define verification requirements;
7. verify deterministic spawn compatibility.

No specialist-count target applies.

### Gate 3: Research before authority

Any execution-envelope, action-authority, resource-budget, or durable-lifecycle proposal remains non-normative until separately reviewed and promoted through the applicable TEO governance process.

### Gate 4: Tracker reconciliation

If accepted work materially changes a workstream milestone, percentage, status, NOW/NEXT/LATER sequencing, roster count, or strategic direction, update the canonical Progress Tracker only after the change is implemented, validated, and accepted through the applicable repository process.

## Revised recommendation

The orchestration landscape research should be retained, but its execution priority remains explicitly subordinate to the canonical Progress Tracker.

The current priority is:

1. use the relevant orchestration patterns to close the remaining NOW Benchmark and Outcome Lab gates without duplicating the existing fixture, experiment, route-outcome, or report contracts;
2. preserve source-backed pricing and shadow-evaluation research for their declared NEXT workstreams;
3. do not create an `Orchestration Evaluation Scientist` because specialist #82 already owns that boundary;
4. keep Observability and Telemetry Engineer, Context and Memory Systems Engineer, and Agent Authorization and Security Engineer as inactive gap hypotheses until a tracked workstream proves an unowned responsibility;
5. defer generalized durable execution and distributed orchestration machinery to the LATER distributed runtime hardening workstream unless evidence creates an earlier gate.

## Decision boundary

The question is no longer whether TEO should immediately add four specialists and several new contracts, or whether Route-Outcome Evidence still needs to be built.

The next implementation boundary is:

> Which parts of this research materially improve controlled live replay, multi-verifier disagreement measurement, or the independent-verification handoff for the current Benchmark and Outcome Lab without creating duplicate authority, duplicate evidence formats, or work outside the canonical stewardship sequence?

## Reconciliation history

This research was first reconciled against the Progress Tracker at main commit `33d7d58c6489a0a82c9c8cdc97160e2dd574d721`, when Route-Outcome Evidence was still NOW and Benchmark and Outcome Lab was NEXT.

Subsequent repository work changed that state:

- PR #110 completed the canonical Route-Outcome Evidence Contract and advanced Benchmark and Outcome Lab to NOW.
- PR #111 implemented and validated the first executable Benchmark and Outcome Lab foundation, recalibrating that workstream to In progress / 60%.
- This revision reconciles the research against main commit `4f6a062442748804770c4fde11926e499fad7c44` without changing the Progress Tracker's authority or creating a parallel roadmap.
