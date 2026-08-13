# Task Intent & Action Authority Contract Research

**Status:** non-normative research direction  
**Recorded:** 2026-08-13  
**Authority:** research only  
**Scope:** future TEO governance of request intent, assessment-versus-action boundaries, delegated authority, and state-changing execution eligibility

## Purpose

This roadmap records a future research direction for TEO: define a machine-checkable contract that preserves the authority actually granted by the originating request before routing, execution, delegation, recovery, or host-native action occurs.

The central problem is distinct from risk classification and distinct from exact action-envelope binding.

A request can discuss the same system while granting materially different authority:

```text
analyze whether a migration is needed
  !=
prepare a migration plan or patch
  !=
execute the migration
  !=
verify a migration that another actor performed
```

TEO must not infer state-changing authority merely from task subject, available tools, host permissions, model capability, specialist eligibility, or the existence of a technically valid execution path.

The objective is to make the boundary between **assessment and action** explicit, bounded, auditable, and preserved across delegation and recovery without turning TEO into a universal permissions product or replacing host-native authorization.

## Repository diagnosis

The current canonical `Task Request` represents the task, task type, risk, domain, specialist, required capabilities, blocked implementations/providers, preview acceptance, and optional human-approval requirement. It does not currently represent a machine-readable request-authority class or permitted side-effect boundary.

The current `Dispatch Record` captures the resolved task, effective risk, Team, Worker, Specialist, capabilities, implementation, fallback, verification, and routing explanation. It likewise does not prove that a request asking only for analysis authorized a later state-changing action.

Host Integration research has separately advanced exact execution-envelope integrity. That work can bind a post-dispatch host action to exact effective risk, capability, operation, target, parameters, side-effect class, prerequisites, and attempt budget. This is necessary but not sufficient: an exact action can still be unauthorized if the originating request never granted action authority.

The resulting research gap is the boundary:

```text
request intent
  -> permitted action authority
  -> TEO routing and risk controls
  -> host/TEO authority intersection
  -> exact action envelope
  -> execution
```

This roadmap addresses the first two stages only and must compose with, not duplicate, the later authority layers.

## Core principle

Execution authority should be the restrictive intersection of independently applicable authority surfaces.

Conceptually:

```text
originating request or delegated authority
  INTERSECT TEO policy and effective-risk controls
  INTERSECT host/runtime authority
  INTERSECT capability and operation eligibility
  INTERSECT qualified-human authority where separately required
  = maximum executable authority
```

No downstream layer may widen the originating request's authority merely because it possesses broader technical permissions.

TEO may narrow authority. It must not silently widen it.

## Research questions

### 1. Intent and operating posture

Determine the smallest stable vocabulary needed to distinguish what kind of work the request actually authorizes.

Candidate postures include:

- `assess`: inspect, analyze, diagnose, or explain without state-changing action;
- `recommend`: produce a recommendation or decision proposal without applying it;
- `prepare`: create bounded drafts, plans, patches, commands, or staged artifacts without performing the consequential external action;
- `execute`: perform explicitly authorized state-changing work inside the permitted scope;
- `verify`: inspect evidence or resulting state without treating verification as execution authority.

These labels are research candidates, not a normative enum. A single posture may be insufficient unless paired with explicit side-effect and target scopes.

### 2. Side-effect authority

Research machine-readable dimensions that prevent vague labels from hiding consequential effects.

Candidate dimensions include:

- whether state mutation is allowed at all;
- permitted resource or target scope;
- local versus remote effects;
- reversible versus irreversible effects;
- persistence or publication authority;
- external communication authority;
- credential, account, or tenant scope;
- allowed tool or operation classes;
- delegated-agent write authority;
- expiry or one-shot semantics where applicable.

The contract should represent the minimum authority needed for the requested outcome rather than mirroring every permission the host happens to possess.

### 3. Authority source and provenance

Not every governed task originates from an interactive user sentence. Research how authority provenance should distinguish, where applicable:

- direct user instruction;
- maintainer or operator instruction;
- previously approved workflow policy;
- delegated parent task;
- scheduled or automated task authority;
- qualified-human approval that satisfies a separately required gate.

Standing workflow authority must be explicit and scoped. It must not be reconstructed from model memory or inferred merely because a host can technically perform the action.

### 4. Ambiguity and least-authority interpretation

When wording supports multiple materially different action scopes, the system should not choose the more consequential interpretation for convenience.

Research a fail-closed rule where material ambiguity in action authority results in one of:

- a narrower non-state-changing interpretation;
- a prepared artifact that is not applied;
- an explicit authority clarification or escalation where required.

Ambiguity about implementation details is not automatically ambiguity about action authority. The contract should distinguish the two.

### 5. Fresh authority for scope escalation

A transition from assessment or preparation into state-changing execution must require a fresh authority basis when the original request did not already grant that scope.

Research invariants should reject:

- a recommendation being treated as approval to execute;
- a prepared patch being treated as approval to merge or deploy;
- a verification request being treated as permission to repair what is being verified;
- a tool-capable model upgrading itself from read to write;
- a host's broad standing permissions being treated as user intent;
- a successful sandbox result being treated as production execution authority.

### 6. Delegation and subagent inheritance

A delegated child work unit must inherit an authority ceiling from its parent.

Research should require child authority to remain equal to or narrower than the parent across:

- action posture;
- side-effect class;
- resource targets;
- capabilities and operations;
- external effects;
- attempt and parallelism budgets;
- persistence and publication rights.

A child result, confidence score, or recommendation must not widen parent authority. Mission Control remains responsible for integration.

### 7. Retry, fallback, escalation, and recovery

Authority must survive execution-path changes.

Research should test that:

- retry preserves the same action-authority ceiling;
- fallback or redispatch cannot widen action scope;
- escalation to a stronger model does not create stronger permissions;
- recovery remains bounded by the original action and recovery authority;
- rollback cannot become an unrelated write path;
- failed execution does not create implied permission for broader remediation.

Where recovery needs action not literally described by the initial request, the contract should define when recovery was pre-authorized as part of a reversible execution transaction and when fresh authority is required.

### 8. Verification independence

Verification is evidence authority, not automatic mutation authority.

A verifier may identify a defect, failed criterion, or required correction. Unless separately authorized, that finding must not grant the verifier permission to modify the artifact or system it examined.

This keeps verification, repair, and finalization as distinct lifecycle stages.

### 9. Relationship to qualified-human authority

Qualified-human approval remains a separate authority requirement where policy independently imposes it.

The Task Intent & Action Authority Contract should not allow either direction of substitution:

- user execution intent must not satisfy a qualified-human gate that policy requires;
- qualified-human approval must not silently widen an originating request that authorized only assessment or preparation.

Both constraints may have to be satisfied for consequential execution.

## Candidate contract surface

A future research record could bind fields such as:

- request or parent-task identity;
- authority-source identity and class;
- authority issuance timestamp and optional expiry;
- requested operating posture;
- allowed state-change class;
- target/resource scope;
- allowed external effects;
- persistence/publication scope;
- delegated-work authority ceiling;
- explicit exclusions;
- ambiguity or clarification state;
- exact request or delegated-authority digest;
- integrity metadata.

The record should be content-minimized where possible. It should preserve authoritative facts about permission without becoming a persisted chain-of-thought or storing unnecessary private prompt content.

## Candidate lifecycle

```text
request or delegated work
  -> intent/action-authority interpretation
  -> authority record
  -> effective-risk and responsibility routing
  -> capability resolution
  -> host/TEO authority intersection
  -> exact action-envelope authorization
  -> execution or non-executing work
  -> independent verification
  -> evidence-bearing outcome
```

A later action must remain traceable to the authority record that permitted that class of effect.

## Relationship to existing TEO work

This research extends existing authority boundaries rather than replacing them.

It should compose with:

- Mission Control task interpretation and orchestration planning;
- non-lowerable effective risk;
- Team -> Worker -> Specialist -> Capability -> Implementation routing;
- Host Integration restrictive authority intersection;
- exact execution-envelope integrity;
- provider-neutral implementation selection;
- bounded retry and canonical fallback redispatch;
- qualified-human approval;
- independent verification and artifact binding;
- Execution Environment & Recovery Contract research;
- Route-Outcome Evidence and auditability.

The Task Intent & Action Authority layer should sit **before** exact host execution authorization. It must not become a second routing engine or a parallel host permissions system.

## Threat model

Research should explicitly test at least:

- analysis-to-execution authority escalation;
- recommendation-to-implementation escalation;
- prepared-artifact auto-application;
- verifier self-repair without write authority;
- prompt or tool output attempting to widen action scope;
- child-agent authority expansion;
- fallback or escalation permission drift;
- retry multiplication that changes external effect;
- stale or cross-task authority-record replay;
- resource-target substitution;
- host standing permissions overriding request scope;
- qualified-human approval being misused to widen user intent;
- sandbox success self-authorizing production action;
- recovery becoming an unrelated mutation channel.

## Non-goals

This roadmap does not commit TEO to:

- replacing operating-system, cloud, repository, database, or application authorization systems;
- interpreting every natural-language verb through a fixed universal enum;
- granting execution solely because risk is low;
- granting execution solely because a user has broad host permissions;
- storing private model reasoning as authority evidence;
- allowing a specialist, model, verifier, or subagent to self-authorize;
- turning qualified-human approval into universal user-intent authority;
- changing current live-execution scope;
- authorizing `documentation` live execution;
- creating a new specialist solely for this contract.

## Proposed evidence sequence

### A0. Contract and authority taxonomy

Define the request-authority model, action-posture semantics, side-effect dimensions, authority provenance, ambiguity rules, and compositional relationship to existing TEO and host authority.

**Exit condition:** the contract distinguishes at least assessment, preparation, execution, and verification cases without using task topic as a proxy for permission.

### A1. Deterministic authority harness

Build provider-independent fixtures where semantically similar tasks differ only in granted action authority.

**Exit condition:** the harness rejects analysis-to-write, recommend-to-apply, verify-to-repair, parent-to-child widening, and stale-authority reuse while accepting exact authorized positive controls.

### A2. Host Integration composition

Bind the research authority record to the existing restrictive host/TEO authority intersection and exact action-envelope research boundary.

**Exit condition:** host standing permission cannot widen request authority, and exact action tokens cannot be issued for effects above the originating authority ceiling.

### A3. Adversarial and mutation validation

Mutate action posture, side-effect scope, target, authority source, delegation inheritance, retry/fallback path, verification role, expiry, and recovery behavior.

**Exit condition:** tested authority escalation fails closed and material control mutants are killed by the evidence suite.

### A4. Architecture-diverse validation

Exercise the contract through at least two materially different host/runtime integration patterns where practical.

**Exit condition:** the same request-authority invariants survive host differences without embedding host-specific permission semantics into TEO.

### A5. Governed integration decision

Only after sufficient evidence should maintainers decide whether an authority record, schema field, or runtime gate becomes normative.

**Exit condition:** explicit Mission Control and maintainer decision based on reproducible evidence, with current routing, live scope, human authority, and release contract preserved unless separately changed.

## Specialist disposition

No new specialist is currently justified.

This research is primarily an orchestration, authority, security, and verification contract. Existing Mission Control, architecture, security, platform, and verification roles provide the necessary decision lenses. A new specialist should be considered only if implementation-backed research proves a stable responsibility gap that existing roles cannot own.

## Current disposition

**Accepted as a future non-normative TEO research direction.**

It does not alter `reference/schemas/task.schema.json`, the canonical Dispatch Record, current routing, provider/model selection, specialist roster, qualified-human authority, the deferred provider-backed `documentation` replay gate, the active `high_volume_simple` live scope, or the stable `v1.0.0` contract.