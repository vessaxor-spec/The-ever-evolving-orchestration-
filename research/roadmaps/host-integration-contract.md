# Host Integration Contract Research

**Date:** 2026-08-12  
**Status:** research roadmap  
**Authority:** non-normative  
**Scope:** embedding TEO Mission Control into pre-existing AI agents and execution runtimes

## Purpose

TEO currently defines strong internal contracts for responsibility, routing, risk, specialist selection, capabilities, implementation eligibility, verification, recovery, evidence, and qualified-human authority. What it does not yet define is a portable boundary for embedding those contracts into a host AI system that already has its own identity, tools, planners, subagents, permissions, context management, and execution environment.

The Host Integration Contract is a research candidate for that boundary.

It is motivated by [`../runtime/2026-08-12-host-agent-integration-premortem.md`](../runtime/2026-08-12-host-agent-integration-premortem.md), which showed that an external host can misintegrate TEO by loading the entire specialist corpus, replacing host identity with specialist personas, over-applying approval gates, hallucinating generic tools, or simulating verification inside one model session.

The first implementation-backed validation round is recorded in [`../runtime/2026-08-12-host-integration-validation-round-1.md`](../runtime/2026-08-12-host-integration-validation-round-1.md). It validates the capability-adapter direction while exposing additional requirements around capability classification, restrictive authority intersection, dispatch-bound execution, adapter immutability, exact routing structure, and anti-fork version binding.

This document does not change current routing, runtime, specialist, verification, approval, or release authority.

## Core design principle

> The host remains the host. TEO governs orchestration within an explicit integration boundary.

The intended architecture is:

```text
HOST AGENT / RUNTIME
identity, mandate, native safety, tools, permissions, execution environment
                |
                v
HOST INTEGRATION CONTRACT
identity preservation
version binding
bounded context projection
capability classification and adapters
autonomy and authority profile
verification availability
recursion and resource limits
conformance declaration
                |
                v
TEO MISSION CONTROL
                |
                v
Team -> Worker -> Specialist -> Capability -> Implementation
                |
                v
HOST AUTHORITY GATE
TEO authorization intersected with host authorization
                |
                v
HOST-NATIVE CAPABILITY EXECUTION
                |
                v
INDEPENDENT VERIFICATION / EVIDENCE
```

Some host controls may operate before or beside Mission Control. Examples include untrusted-input screening, host runtime continuity, native credential boundaries, and system health mechanisms. The integration contract must classify those surfaces rather than forcing every host-native action behind a specialist dispatch.

The integration layer is an adapter and evidence boundary. It must not become a second routing authority.

## Design invariants

### 1. Preserve host identity

The contract must preserve the host's declared identity and non-negotiable operating invariants separately from TEO specialist context.

Examples include:

- host mission or mandate;
- native safety rules;
- quality bar;
- product-specific constraints;
- execution-environment restrictions;
- privacy and data-handling constraints;
- user-granted permissions.

TEO specialists remain canonical domain capability definitions. A host integration must not rewrite specialist cards merely to make them sound like the host.

If host invariants and a selected specialist conflict materially, the conflict must be surfaced as an explicit compatibility condition rather than silently resolving it by prompt order.

### 2. Bind to executable TEO truth

The contract must bind to versioned TEO authority rather than infer active configuration from repository files.

Candidate bindings:

```yaml
teo_binding:
  release: v1.0.0
  runtime_version: 1.0.1.dev0
  routing_policy_version: <resolved-version>
  specialist_registry_version: <resolved-version>
  capability_registry_version: <resolved-version>
  executable_composition_id: <resolved-configbundle-or-equivalent>
  integration_contract_version: <candidate-version>
```

The active executable `ConfigBundle` remains authoritative for active teams, workers, specialists, and routing composition.

A copied Mission Control file, specialist count, Markdown inventory, or base registry alone is not sufficient version binding. Hosts that vendor or cache TEO artifacts should detect stale or mismatched copies against the declared executable composition and fail closed or explicitly degrade conformance rather than silently fork TEO authority.

### 3. Project only bounded context

The contract should define a context budget and projection policy so an external host never needs to inject the entire specialist corpus into the execution prompt.

Candidate structure:

```yaml
context_projection:
  original_task: required
  user_constraints: required
  host_invariants: required
  mission_control_decision: required
  selected_team: required
  selected_worker: required
  selected_specialist: one
  specialist_source: canonical
  capability_bindings: selected_only
  supporting_evidence: task_relevant_only
  maximum_specialist_cards_per_dispatch: 1
  semantic_retrieval_role: discovery_support_only
```

`maximum_specialist_cards_per_dispatch: 1` is a context-projection boundary, not a global one-specialist limit. Mission Control may create multiple bounded specialist dispatches when a genuinely cross-disciplinary task requires them, provided each dispatch preserves responsibility, risk, capability, authority, and verification semantics.

Deterministic routing metadata should narrow the candidate set before semantic retrieval is used.

### 4. Classify host-native capabilities before binding them

Not every host-native capability belongs behind a TEO specialist dispatch. A host may contain security controls, runtime infrastructure, authority surfaces, verification mechanisms, and maintenance capabilities that operate before, beside, or beneath Mission Control.

Candidate classes:

| Class | Typical purpose | TEO relationship |
|---|---|---|
| Pre-routing safety controls | untrusted-input screening, isolation prechecks | may execute before Mission Control |
| TEO-dispatched execution capabilities | code changes, research, data processing, controlled actions | require authorized capability binding |
| Host runtime infrastructure | continuity, queues, telemetry, lifecycle state | operates beneath or beside TEO |
| Host authority infrastructure | credentials, native approval gates, environment restrictions | cannot be bypassed by TEO |
| Verification capabilities | tests, scanners, independent verifier routes | governed by verification contract |
| Host maintenance capabilities | health checks, hygiene, local upkeep | may be system-triggered under host governance |

Classification prevents two opposite failures: bypassing TEO for task execution and over-centralizing host safety or runtime machinery behind unnecessary specialist routing.

### 5. Bind capabilities to host-native tools

TEO specialists and workers should continue to express required capabilities. The host integration layer should resolve those capabilities to concrete host tools or actions.

Candidate structure:

```yaml
capability_bindings:
  - capability: sandboxed_execution
    implementation: host.tool.sandbox
    available: true
    permissions:
      - local_execute
    side_effect_class: local_mutation
    isolation_boundary: host_sandbox
    rollback: supported
    output_contract: structured_execution_result
```

The binding should be able to declare:

- concrete implementation identifier;
- current availability;
- permissions and scope;
- external/network access;
- side-effect class;
- isolation boundary;
- prerequisites;
- output contract;
- rollback or compensating action;
- fallback binding;
- evidence/receipt production.

Unknown or unavailable required capabilities should fail closed according to existing TEO semantics rather than invite hypothetical tool use.

Where a host claims executable enforcement, capability execution should be bound to an authorized dispatch rather than a capability name alone. Candidate dispatch evidence includes:

- dispatch identifier;
- selected Team and Worker;
- optional selected Specialist and source;
- effective risk;
- authorized capability set;
- host permission/approval result;
- verification requirement;
- version/integrity binding;
- expiry or replay boundary where applicable.

Capability-adapter manifests are authority surfaces. The active executor should not be able to rewrite a binding and then consume the widened binding within the same dispatch unless a separate governance change explicitly authorizes that mutation.

### 6. Declare autonomy separately from human authority

The integration contract should prevent external hosts from confusing Mission Control governance with universal human approval.

Candidate autonomy modes:

```text
AUTONOMOUS
VERIFIED_AUTONOMOUS
ESCALATED
HUMAN_GATED
```

These modes are descriptive integration behavior, not substitutes for TEO policy. The effective routing and authority decision remains governed by TEO policy and non-lowerable risk.

A multi-step task must not become human-gated merely because it is multi-step. Conversely, a host's preference for autonomy must not bypass a qualified-human requirement already imposed by policy.

### 7. Declare verification capability honestly

The host should declare which verification forms it can actually perform.

Candidate structure:

```yaml
verification_profile:
  deterministic_tests: true
  static_analysis: true
  sandbox_reexecution: true
  independent_model_verification:
    available: true
    provider_diverse: true
  qualified_human_authority:
    integration_supported: false
```

A same-session persona shift must never be represented as independent model verification.

A distinct subagent also does not automatically prove independence. When provider-diverse verification is required, the verifier must satisfy the applicable TEO independence contract.

If a required verification or authority path is unavailable, the host should record the missing condition and stop, escalate, or defer according to policy rather than fabricate conformance.

Execution success, synchronization, deployment, and independent verification are distinct evidence states and should not be collapsed into one completion claim.

### 8. Bound recursive orchestration

Hosts that already orchestrate agents need explicit recursion controls.

Candidate controls:

```yaml
orchestration_budget:
  maximum_teo_reentry_depth: 1
  maximum_specialist_spawns: <bounded>
  maximum_parallel_branches: <bounded>
  maximum_attempts: <bounded>
  deadline: <optional>
  normalized_usage_budget: <optional>
  source_backed_cost_budget: <optional>
```

Resource limits may refuse or constrain execution. They must never lower effective risk, waive required capabilities, or weaken verification.

### 9. Preserve authority boundaries

The contract should state which layer owns which decision.

| Decision | Authority |
|---|---|
| Host identity and native product constraints | Host |
| User permissions granted to the host | Host / user |
| TEO Team, Worker, Specialist, capability and model routing | TEO control plane |
| Concrete host-tool implementation for an authorized capability | Host capability adapter |
| Effective risk | TEO policy; non-lowerable |
| Qualified-human requirement | TEO policy / applicable authority contract |
| Tool/action execution permission | Restrictive intersection of TEO authorization and host authorization |
| Independent-verification requirement | TEO policy |
| Verification implementation availability | Host declaration plus TEO eligibility |
| Final claim of conformance | Evidence-bound; never inferred from intent |

Authority conflict semantics should be explicit:

- deny wins;
- the more restrictive control wins;
- host permissions cannot lower TEO risk, verification, or qualified-human requirements;
- TEO authorization cannot weaken stricter host safety, permission, environment, or operator controls;
- unresolved authority conflicts stop, escalate, or degrade conformance rather than being silently resolved by prompt order.

Neither side should silently widen the other's authority.

## Candidate contract shape

A future machine-readable contract may resemble:

```yaml
host_integration:
  version: research-0

  host:
    id: <opaque-host-id>
    architecture_class: <single-agent|multi-agent|runtime>
    identity_policy_ref: <host-owned-ref>
    safety_policy_ref: <host-owned-ref>

  teo_binding:
    release: <release>
    runtime_version: <runtime>
    routing_policy_version: <policy>
    specialist_registry_version: <registry>
    capability_registry_version: <registry>
    executable_composition_id: <configbundle-or-equivalent>

  context_projection:
    maximum_specialist_cards_per_dispatch: 1
    preserve_original_task: true
    preserve_user_constraints: true
    preserve_host_invariants: true

  capability_classes:
    pre_routing_safety: <declared-bindings>
    teo_dispatched_execution: <declared-bindings>
    host_runtime: <declared-bindings>
    host_authority: <declared-bindings>
    verification: <declared-bindings>
    maintenance: <declared-bindings>

  capability_bindings:
    - capability: <teo-capability>
      implementation: <host-tool>
      available: true
      side_effect_class: <class>
      isolation_boundary: <boundary>
      rollback: <supported|unsupported|not_applicable>

  dispatch_authorization:
    required_for_teo_dispatched_execution: true
    bind_team_worker_specialist: true
    bind_effective_risk: true
    bind_authorized_capabilities: true
    bind_host_authority_result: true
    bind_verification_requirement: true

  authority_resolution:
    mode: restrictive_intersection
    deny_wins: true
    unresolved_conflict: escalate_or_refuse

  autonomy_profile:
    routine: AUTONOMOUS
    verification_required: VERIFIED_AUTONOMOUS
    unresolved_control_failure: ESCALATED
    policy_human_requirement: HUMAN_GATED

  verification_profile:
    independent_model_verification:
      available: <bool>
      provider_diverse: <bool>
    deterministic_verification:
      available: <bool>

  orchestration_budget:
    maximum_teo_reentry_depth: 1
    maximum_specialist_spawns: <int>
    maximum_parallel_branches: <int>

  conformance:
    mission_control: <supported|partial|unsupported>
    routing_structure: <supported|partial|unsupported>
    specialist_routing: <supported|partial|unsupported>
    capability_classification: <supported|partial|unsupported>
    capability_binding: <supported|partial|unsupported>
    dispatch_bound_execution: <supported|partial|unsupported>
    non_lowerable_risk: <supported|partial|unsupported>
    authority_intersection: <supported|partial|unsupported>
    independent_verification: <supported|partial|unsupported>
    route_outcome_evidence: <supported|partial|unsupported>
    qualified_human_authority: <supported|partial|unsupported>
    upstream_freshness_binding: <supported|partial|unsupported>
```

This is illustrative only. Field names and schema are not approved.

## Integration modes for research

### Shadow

TEO receives the task and produces routing/control decisions, but the host's existing production path remains authoritative. Compare decisions and outcomes without changing host behavior.

Use for first integration and compatibility analysis.

### Governed bounded activation

TEO controls an explicitly bounded task class or capability set. Host-native execution remains behind declared capability adapters. Evidence, verification, rollback, and failure semantics are measured.

Use only after shadow evidence supports activation.

### Conformant embedded operation

A host may eventually claim a declared TEO conformance profile when all claimed surfaces have executable evidence. Unsupported surfaces remain explicit.

This research does not define a "full TEO" marketing claim or certify any host.

## Round 1 implementation refinements

The first external-host implementation validates several parts of this candidate and sharpens others.

The following refinements govern interpretation of the illustrative structures above:

1. **One specialist card means one per dispatch context.** It must not prevent Mission Control from creating several bounded specialist dispatches for a cross-disciplinary task.
2. **Authority intersection is restrictive.** Deny wins and the more restrictive control wins when TEO and host constraints differ.
3. **Capability adapters are authority surfaces.** The active executor must not self-modify a binding and consume the widened authority in the same dispatch without a separately authorized governance change.
4. **Programmatic enforcement requires dispatch binding.** A router that checks only `capability_name` demonstrates capability translation, not a hard Mission Control execution lock.
5. **Host capabilities must be classified.** Pre-routing safety, runtime infrastructure, authority controls, verification mechanisms, and maintenance functions may operate outside specialist-triggered execution while remaining governed by the host integration contract.
6. **Copied TEO files are not canonical binding.** Hosts that vendor TEO content need release, policy, registry, and executable-composition freshness checks to prevent silent forks.
7. **Exact routing fields matter.** External taxonomies may supplement but must not collapse Team, Worker, Specialist, Capability, Implementation, and Verification while claiming TEO conformance.
8. **Evidence levels must remain distinct.** Local mutation, commit, synchronization, deployment, execution, and independent verification are different claims.

See [`../runtime/2026-08-12-host-integration-validation-round-1.md`](../runtime/2026-08-12-host-integration-validation-round-1.md) for the implementation evidence and unresolved gaps.

## Anti-patterns

The following should be treated as integration failures:

- loading all active specialist cards into every task context;
- enumerating Markdown files to determine the active specialist roster;
- rewriting canonical specialist identities to match host branding;
- letting a specialist invent host commands because no capability binding exists;
- treating every complex task as human-gated;
- simulating independent verification through same-session roleplay;
- recursively re-entering Mission Control without a bounded delegation depth;
- allowing host cost/token limits to lower effective risk or waive controls;
- claiming unsupported TEO surfaces as implemented;
- replacing the host's native safety floor with weaker integration behavior;
- treating every host-native control or maintenance function as specialist-triggered execution;
- claiming a hard execution lock when a router validates only a capability name;
- letting an active executor rewrite its own capability authority surface;
- treating a copied TEO file set or specialist count as executable registry truth;
- collapsing Team, Worker, and Specialist into host-local labels while emitting a TEO dispatch record.

## Evidence required before normative promotion

The Host Integration Contract should remain research until at least the following evidence exists:

1. **Premortem replay:** demonstrate that the contract directly prevents or truthfully detects all five original failure paths.
2. **Two-host validation:** test against at least two structurally different host architectures so one agent's design does not become the universal contract by accident.
3. **Context economics:** compare bounded projection against naive corpus loading for prompt size, normalized usage, latency, and task adherence.
4. **Identity preservation:** verify that host invariants remain intact while selected specialists still retain their canonical capability definitions.
5. **Capability correctness:** prove required capabilities resolve to real host implementations and unknown capabilities fail closed.
6. **Capability classification:** prove pre-routing safety, runtime, authority, verification, maintenance, and TEO-dispatched execution surfaces are classified without creating bypasses or unnecessary orchestration loops.
7. **Dispatch authorization:** prove a governed execution router cannot invoke a TEO-dispatched capability without a valid dispatch-bound authorization record or equivalent evidence.
8. **Adapter integrity:** prove the active executor cannot widen its own capability binding inside the same dispatch without a separately authorized governance change.
9. **Autonomy correctness:** prove routine multi-step work can remain autonomous while explicit human-authority requirements remain blocking.
10. **Authority intersection:** prove host and TEO constraints resolve by deny-wins/more-restrictive-control-wins semantics.
11. **Verification honesty:** prove unsupported independence is surfaced rather than simulated.
12. **Recursion resistance:** mutation-test delegation-depth and spawn-budget boundaries.
13. **Registry freshness:** prove stale or mismatched TEO release, policy, registry, overlay, or executable-composition bindings are detected.
14. **Routing conformance:** prove host-local taxonomies cannot collapse required Team, Worker, Specialist, Capability, Implementation, or Verification fields.
15. **Independent review:** challenge whether the integration layer creates a second routing authority or weakens existing TEO invariants.

## Relationship to existing TEO research

This work extends, rather than replaces, the existing research concepts in `research/runtime/orchestration-landscape-gap-analysis-2026-08-10.md`:

- **Specialist Execution Envelope:** now has concrete host-embedding evidence for scoped context, dispatch authorization, and allowed tool/action declarations.
- **Resource Budget and Admission Contract:** delegation depth, spawn count, context/token budgets, and parallelism become directly relevant for external-host recursion control.
- **Action Authority Plane:** host tool authorization remains distinct from provider access and from TEO model routing. Round 1 strengthens the need for restrictive intersection semantics.
- **Context and Memory Systems Engineer candidate:** this integration evidence strengthens the identified context-scoping responsibility gap, but does not by itself justify specialist activation.

No new specialist is proposed by this document.

## Current disposition

- Record the contract as non-normative research.
- Treat external-host validation round 1 as implementation evidence, not normative authority.
- Do not change current Mission Control policy, specialist cards, active roster, verifier rules, or live-execution scope.
- Validate the contract against at least one structurally different external host before proposing schemas or reference-runtime code.
- Preserve the current Progress Tracker sequencing. This research is not promoted ahead of the provider-backed `documentation` replay gate.
