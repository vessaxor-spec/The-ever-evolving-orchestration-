# Host Integration Contract Research

**Date:** 2026-08-12  
**Status:** research roadmap  
**Authority:** non-normative  
**Scope:** embedding TEO Mission Control into pre-existing AI agents and execution runtimes

## Purpose

TEO currently defines strong internal contracts for responsibility, routing, risk, specialist selection, capabilities, implementation eligibility, verification, recovery, evidence, and qualified-human authority. What it does not yet define is a portable boundary for embedding those contracts into a host AI system that already has its own identity, tools, planners, subagents, permissions, context management, and execution environment.

The Host Integration Contract is a research candidate for that boundary.

It is motivated by [`../runtime/2026-08-12-host-agent-integration-premortem.md`](../runtime/2026-08-12-host-agent-integration-premortem.md), which showed that an external host can misintegrate TEO by loading the entire specialist corpus, replacing host identity with specialist personas, over-applying approval gates, hallucinating generic tools, or simulating verification inside one model session.

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
capability adapters
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
HOST-NATIVE CAPABILITY EXECUTION
                |
                v
INDEPENDENT VERIFICATION / EVIDENCE
```

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
  integration_contract_version: <candidate-version>
```

The active executable `ConfigBundle` remains authoritative for active teams, workers, specialists, and routing composition.

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
  maximum_specialist_cards: 1
  semantic_retrieval_role: discovery_support_only
```

Deterministic routing metadata should narrow the candidate set before semantic retrieval is used.

### 4. Bind capabilities to host-native tools

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

### 5. Declare autonomy separately from human authority

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

### 6. Declare verification capability honestly

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

### 7. Bound recursive orchestration

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

### 8. Preserve authority boundaries

The contract should state which layer owns which decision.

| Decision | Authority |
|---|---|
| Host identity and native product constraints | Host |
| User permissions granted to the host | Host / user |
| TEO Team, Worker, Specialist, capability and model routing | TEO control plane |
| Concrete host-tool implementation for an authorized capability | Host capability adapter |
| Effective risk | TEO policy; non-lowerable |
| Qualified-human requirement | TEO policy / applicable authority contract |
| Tool/action execution permission | Intersection of TEO requirement and host authorization |
| Independent-verification requirement | TEO policy |
| Verification implementation availability | Host declaration plus TEO eligibility |
| Final claim of conformance | Evidence-bound; never inferred from intent |

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

  context_projection:
    maximum_specialist_cards: 1
    preserve_original_task: true
    preserve_user_constraints: true
    preserve_host_invariants: true

  capability_bindings:
    - capability: <teo-capability>
      implementation: <host-tool>
      available: true
      side_effect_class: <class>
      isolation_boundary: <boundary>
      rollback: <supported|unsupported|not_applicable>

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
    specialist_routing: <supported|partial|unsupported>
    capability_binding: <supported|partial|unsupported>
    non_lowerable_risk: <supported|partial|unsupported>
    independent_verification: <supported|partial|unsupported>
    route_outcome_evidence: <supported|partial|unsupported>
    qualified_human_authority: <supported|partial|unsupported>
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
- replacing the host's native safety floor with weaker integration behavior.

## Evidence required before normative promotion

The Host Integration Contract should remain research until at least the following evidence exists:

1. **Premortem replay:** demonstrate that the contract directly prevents or truthfully detects all five original failure paths.
2. **Two-host validation:** test against at least two structurally different host architectures so one agent's design does not become the universal contract by accident.
3. **Context economics:** compare bounded projection against naive corpus loading for prompt size, normalized usage, latency, and task adherence.
4. **Identity preservation:** verify that host invariants remain intact while selected specialists still retain their canonical capability definitions.
5. **Capability correctness:** prove required capabilities resolve to real host implementations and unknown capabilities fail closed.
6. **Autonomy correctness:** prove routine multi-step work can remain autonomous while explicit human-authority requirements remain blocking.
7. **Verification honesty:** prove unsupported independence is surfaced rather than simulated.
8. **Recursion resistance:** mutation-test delegation-depth and spawn-budget boundaries.
9. **Registry freshness:** prove stale or mismatched TEO version bindings are detected.
10. **Independent review:** challenge whether the integration layer creates a second routing authority or weakens existing TEO invariants.

## Relationship to existing TEO research

This work extends, rather than replaces, the existing research concepts in `research/runtime/orchestration-landscape-gap-analysis-2026-08-10.md`:

- **Specialist Execution Envelope:** now has concrete host-embedding evidence for scoped context and allowed tool/action declarations.
- **Resource Budget and Admission Contract:** delegation depth, spawn count, context/token budgets, and parallelism become directly relevant for external-host recursion control.
- **Action Authority Plane:** host tool authorization remains distinct from provider access and from TEO model routing.
- **Context and Memory Systems Engineer candidate:** this integration evidence strengthens the identified context-scoping responsibility gap, but does not by itself justify specialist activation.

No new specialist is proposed by this document.

## Current disposition

- Record the contract as non-normative research.
- Do not change current Mission Control policy, specialist cards, active roster, verifier rules, or live-execution scope.
- Validate the contract against external-host integrations before proposing schemas or reference-runtime code.
- Preserve the current Progress Tracker sequencing. This research is not promoted ahead of the provider-backed `documentation` replay gate.
