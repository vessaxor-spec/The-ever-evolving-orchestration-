# Host Integration Contract Research

**Date:** 2026-08-12  
**Last reconciled:** 2026-08-14  
**Status:** research roadmap  
**Authority:** non-normative  
**Scope:** embedding TEO Mission Control into pre-existing AI agents and execution runtimes

## Purpose

TEO defines internal contracts for responsibility, routing, risk, specialist selection, capabilities, implementation eligibility, verification, recovery, evidence, and qualified-human authority. What it does not yet define normatively is a portable boundary for embedding those contracts into a host AI system that already has its own identity, tools, planners, subagents, permissions, context management, and execution environment.

The Host Integration Contract is a research candidate for that boundary.

It is motivated by [`../runtime/2026-08-12-host-agent-integration-premortem.md`](../runtime/2026-08-12-host-agent-integration-premortem.md), which showed that an external host can misintegrate TEO by loading the entire specialist corpus, replacing host identity with specialist personas, over-applying approval gates, hallucinating generic tools, simulating verification inside one model session, or widening TEO orchestration authority into unrelated host authority.

Implementation-backed evidence now includes:

- [`../runtime/2026-08-12-host-integration-validation-round-1.md`](../runtime/2026-08-12-host-integration-validation-round-1.md), a host-local vendorized/capability-adapter pattern;
- [`../runtime/2026-08-12-host-integration-validation-round-2.md`](../runtime/2026-08-12-host-integration-validation-round-2.md), a structurally different revision-pinned upstream-dispatch/downstream-execution-adapter pattern;
- [`../runtime/host-integration-context-economics-2026-08-12.md`](../runtime/host-integration-context-economics-2026-08-12.md), bounded specialist projection versus naive active-corpus loading;
- [`../runtime/host-integration-dispatch-adapter-mutation-2026-08-12.md`](../runtime/host-integration-dispatch-adapter-mutation-2026-08-12.md), dispatch provenance and bundled-adapter payload self-expansion resistance;
- [`../runtime/host-integration-third-party-adapter-trust-2026-08-12.md`](../runtime/host-integration-third-party-adapter-trust-2026-08-12.md), process-local third-party adapter registration and non-self-authorization;
- [`../runtime/host-integration-authority-intersection-2026-08-12.md`](../runtime/host-integration-authority-intersection-2026-08-12.md), restrictive host/TEO authority intersection and host execution-scope binding;
- [`../runtime/host-integration-execution-envelope-integrity-2026-08-12.md`](../runtime/host-integration-execution-envelope-integrity-2026-08-12.md), exact process-local action-envelope integrity;
- [`../runtime/host-integration-verifier-artifact-binding-2026-08-12.md`](../runtime/host-integration-verifier-artifact-binding-2026-08-12.md), verifier-context independence and exact artifact/change-set stale-PASS resistance;
- [`../runtime/host-integration-cross-process-authority-2026-08-13.md`](../runtime/host-integration-cross-process-authority-2026-08-13.md), brokered conformant process-lifetime cross-process authority and replay resistance with the production/distributed boundary kept open;
- [`../runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), runtime-derived reconciliation of statically wired authority configuration and policy surfaces, with dynamic executable-hook discovery explicitly kept open;
- [`../runtime/host-integration-recursion-resistance-2026-08-14.md`](../runtime/host-integration-recursion-resistance-2026-08-14.md), process-lifetime root-scoped recursion admission with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings;
- [`../runtime/host-integration-freshness-binding-2026-08-14.md`](../runtime/host-integration-freshness-binding-2026-08-14.md), exact local freshness classification bound to release/runtime/revision plus authority-surface and effective routing/registry/model/composition fingerprints.

This document does not change current routing, runtime, specialist, verification, approval, Task Request, Dispatch Record, live-execution, or release authority.

## Core design principle

> The host remains the host. TEO governs orchestration within an explicit integration boundary.

The intended architecture is:

```text
HOST AGENT / RUNTIME
identity, mandate, native safety, tools, permissions, execution environment
                |
                v
HOST TASK ADMISSION / PORTFOLIO AUTHORITY
host or user chooses which work enters TEO
                |
                v
HOST INTEGRATION CONTRACT
identity preservation
version and freshness binding
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
EXACT ACTION ENVELOPE
risk, capability, operation, target, parameters, side effects, prerequisites, budget
                |
                v
HOST-NATIVE CAPABILITY EXECUTION
                |
                v
ARTIFACT-BOUND INDEPENDENT VERIFICATION / EVIDENCE
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

If host invariants and a selected specialist conflict materially, the conflict must be surfaced as an explicit compatibility condition rather than silently resolved by prompt order.

### 2. Bind to executable TEO truth

The contract must bind to versioned TEO authority rather than infer active configuration from repository files.

Candidate bindings include:

```yaml
teo_binding:
  release: v1.0.0
  runtime_version: 1.0.1.dev0
  routing_policy_version: <resolved-version>
  specialist_registry_version: <resolved-version>
  capability_registry_version: <resolved-version>
  executable_composition_id: <resolved-configbundle-or-equivalent>
  integration_contract_version: <candidate-version>
  pinned_revision: <optional-host-pin>
  freshness_state: <PINNED_CURRENT|PINNED_COMPATIBLE|UPDATE_AVAILABLE|STALE_UNSUPPORTED|MISMATCHED>
```

The active executable `ConfigBundle` remains authoritative for active teams, workers, specialists, and routing composition.

A copied Mission Control file, specialist count, Markdown inventory, or base registry alone is not sufficient version binding. Hosts that vendor or cache TEO artifacts should detect stale or mismatched copies against the declared executable composition and fail closed or explicitly degrade conformance rather than silently fork TEO authority.

A revision pin and a freshness judgment are separate claims. A host may intentionally remain on a reproducible compatible revision while a newer TEO revision exists. The integration should state that condition explicitly rather than calling every valid pin current.

Exact local classification is now executable at the non-normative research layer. The TEO-side harness derives an exact current binding and classifies host snapshots only against an authority-owned current binding plus explicitly recorded historical bindings as `PINNED_CURRENT`, `PINNED_COMPATIBLE`, `UPDATE_AVAILABLE`, `STALE_UNSUPPORTED`, or `MISMATCHED`. CI #676 preserved a red canary when a typed YAML date exposed a naïve JSON-fingerprinting assumption; typed canonicalization corrected that issue without collapsing dates into strings, and CI #678 passed the corrected slice. Production compatibility-catalog provenance, remote authenticity, downgrade resistance, distributed freshness coordination, and automated update authority remain open.

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

The current static research harness measured 1,157,957 bytes across all 82 active role cards and found one-card projection reduced specialist-card payload by 98.7805% on average and 97.6295% in the worst measured case. This satisfies only the static payload-size slice. Provider token usage, end-to-end latency, and task adherence remain open.

### 4. Classify host-native capabilities before binding them

Not every host-native capability belongs behind a TEO specialist dispatch. A host may contain security controls, runtime infrastructure, authority surfaces, verification mechanisms, and maintenance capabilities that operate before, beside, or beneath Mission Control.

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

A binding should declare concrete implementation identity, availability, permission/scope, network/external access, side-effect class, isolation boundary, prerequisites, output contract, rollback/compensation, fallback binding, and evidence/receipt production where applicable.

Unknown or unavailable required capabilities should fail closed according to existing TEO semantics rather than invite hypothetical tool use.

Programmatic enforcement must bind execution to an authority-owned dispatch snapshot, not to a capability name alone. Process-local research now demonstrates that tested dispatch tampering, unissued authority, and cross-dispatch token reuse can be rejected before adapter execution. The brokered cross-process research further demonstrates that a conformant separate host process can request and consume an exact TEO-side authorization without gaining an issuance operation or replaying a successful claim. These results do not yet prove compromised-host resistance, remote transport authenticity, host identity, or production/distributed loading.

Capability-adapter manifests are authority surfaces. Process-local research now also demonstrates that tested manifest claims, implementation-artifact replacement, factory substitution, provider drift, capability widening, token reuse, and revocation bypass can be rejected before provider execution. Production package provenance, transitive dependency identity, authority-controlled loading, downgrade resistance, and distributed persistence remain open.

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
  verifier_context:
    fresh_context: true
    executor_reasoning_inherited: false
    purpose_built_challenge_prompt: true
  artifact_binding:
    exact_change_identity: true
    stale_pass_rejected: true
  qualified_human_authority:
    integration_supported: false
```

A same-session persona shift must never be represented as independent model verification. A distinct subagent also does not automatically prove independence. When provider-diverse verification is required, the verifier must satisfy the applicable TEO independence contract.

The current research boundary rejects tested executor reasoning, executor messages, conversation history, prior verdicts, and executor self-assessment from independent-verifier requests. It also binds PASS evidence to the exact task, dispatch, change, artifact, revision, SHA-256 digest, and target reference. Those verifier-context and artifact-binding slices are satisfied at the non-normative research layer only.

Execution success, synchronization, deployment, and independent verification are distinct evidence states and should not be collapsed into one completion claim.

### 8. Bound recursive orchestration

Hosts that already orchestrate agents need explicit recursion controls.

Candidate controls:

```yaml
orchestration_budget:
  maximum_teo_reentry_depth: 1
  maximum_descendants: <bounded>
  maximum_specialist_spawns: <bounded>
  maximum_parallel_branches: <bounded>
  maximum_recovery_generations: <bounded>
  maximum_attempts: <bounded>
  deadline: <optional>
  normalized_usage_budget: <optional>
  source_backed_cost_budget: <optional>
```

Resource limits may refuse or constrain execution. They must never lower effective risk, waive required capabilities, or weaken verification.

Already-dispatched executor contexts should not recursively re-enter Mission Control unless a new bounded dispatch is explicitly required by policy or delegation semantics.

Process-lifetime recursion admission is now supported at the non-normative research layer. The tested TEO-side authority binds one root dispatch to immutable re-entry depth, total descendant, specialist-spawn, active-branch, and recovery-generation ceilings. Descendant admission uses stateless HMAC-bound claims tied to the exact root revision so host forgery, replay, stale claims, cross-root reuse, release-based budget reset, and raced same-revision claims fail closed. Same-dispatch provider retry remains governed separately by the existing retry policy. Restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host recursion/recovery boundaries remain open.

### 9. Preserve authority boundaries

| Decision | Authority |
|---|---|
| Host identity and native product constraints | Host |
| Host backlog, product priority, and task admission | Host / user unless explicitly delegated |
| User permissions granted to the host | Host / user |
| TEO Team, Worker, Specialist, capability and model routing for an admitted task | TEO control plane |
| Concrete host-tool implementation for an authorized capability | Host capability adapter |
| Effective risk | TEO policy; non-lowerable |
| Qualified-human requirement | TEO policy / applicable authority contract |
| Tool/action execution permission | Restrictive intersection of TEO authorization and host authorization |
| Independent-verification requirement | TEO policy |
| Verification implementation availability | Host declaration plus TEO eligibility |
| Final claim of conformance | Evidence-bound; never inferred from intent |

Authority conflict semantics are:

- deny wins;
- the more restrictive control wins;
- host permissions cannot lower TEO risk, verification, or qualified-human requirements;
- TEO authorization cannot weaken stricter host safety, permission, environment, or operator controls;
- TEO orchestration authority does not automatically become host portfolio, backlog, or task-admission authority;
- unresolved authority conflicts stop, escalate, or degrade conformance rather than being silently resolved by prompt order.

Process-local research now demonstrates restrictive intersection against task, risk, capability, provider, operation, and active-state host scope. It also demonstrates exact action binding for effective risk, capability, operation, resource target, canonical parameters, side-effect class, prerequisites, and TEO attempt budget. Brokered process-lifetime research demonstrates the same authority state can remain on the TEO side while separate conformant host processes request and consume exact authorization with session binding, one-time claim semantics, duplicate-claim serialization, and retry-budget preservation. Production target canonicalization, credential/account/tenant binding, compromised-host bypass resistance, remote/distributed authenticity, restart-durable replay state, effect evidence, and distributed retry coordination remain open.

Neither side should silently widen the other's authority.

### 10. Derive and protect authority surfaces

Host integrations should identify the files, manifests, hooks, scripts, registries, runtime loaders, and other surfaces that can alter routing, authorization, capability binding, verification, approval, or finalization behavior.

Where runtime wiring can identify those surfaces, the integration should derive the inventory from executable configuration rather than maintain a second hand-written list.

Where a manual authority inventory remains necessary, conformance should reconcile it against runtime discovery and fail on omissions or stale entries.

Protecting authority configuration is not sufficient by itself. Finalization and action paths must still prove that the governed decision was actually enforced.

Runtime-derived reconciliation of **statically wired authority configuration and policy paths** is now supported at the non-normative research layer by the 2026-08-14 adversarial slice and CI #644. The research derives canonical YAML/JSON authority paths from executable Python runtime source, retains dormant-but-wired paths, fingerprints present files, and rejects tested omission, unwired additions, aliasing, category/presence/digest mismatch, stale snapshots, new wiring, dormant-path materialization, duplicate entries, unknown widening fields, and repository-root escape.

This does not close the broader authority-surface problem. Dynamically constructed paths, arbitrary executable hooks, import hooks, plugins/loaders, generated code, monkey patches, transitive executable-code identity, signer/origin authenticity, and compromised-host bypass resistance remain open before any normative promotion claim.

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
    portfolio_authority: host_or_user

  teo_binding:
    release: <release>
    runtime_version: <runtime>
    routing_policy_version: <policy>
    specialist_registry_version: <registry>
    capability_registry_version: <registry>
    executable_composition_id: <configbundle-or-equivalent>
    pinned_revision: <optional-revision>
    freshness_state: <state>

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
    portfolio_authority_is_separate: true
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
    context_asymmetry:
      fresh_context: <bool>
      executor_reasoning_inherited: false
    artifact_binding:
      exact_change_identity: <bool>
      stale_pass_rejected: <bool>

  authority_surfaces:
    discovery: <runtime_derived|declared_and_reconciled>
    protected: true

  orchestration_budget:
    maximum_teo_reentry_depth: 1
    maximum_descendants: <int>
    maximum_specialist_spawns: <int>
    maximum_parallel_branches: <int>
    maximum_recovery_generations: <int>

  conformance:
    mission_control: <supported|partial|unsupported>
    routing_structure: <supported|partial|unsupported>
    specialist_routing: <supported|partial|unsupported>
    capability_classification: <supported|partial|unsupported>
    capability_binding: <supported|partial|unsupported>
    dispatch_bound_execution: <supported|partial|unsupported>
    non_lowerable_risk: <supported|partial|unsupported>
    authority_intersection: <supported|partial|unsupported>
    portfolio_authority_separation: <supported|partial|unsupported>
    independent_verification: <supported|partial|unsupported>
    verification_artifact_binding: <supported|partial|unsupported>
    route_outcome_evidence: <supported|partial|unsupported>
    qualified_human_authority: <supported|partial|unsupported>
    upstream_freshness_binding: <supported|partial|unsupported>
    authority_surface_reconciliation: <supported|partial|unsupported>
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

## Implementation-backed evidence status

| Research slice | Current status | Evidence boundary |
|---|---|---|
| Two-host architecture diversity | **Satisfied** | two materially different integration patterns; does not certify either host |
| Bounded context projection | **Static payload slice satisfied** | 98.7805% mean and 97.6295% worst measured payload reduction; provider token/latency/adherence evidence remains open |
| Dispatch provenance | **Process-local slice satisfied** | tested tampering, unissued token, and cross-dispatch reuse rejected before adapter invocation |
| Bundled-adapter self-expansion | **Satisfied for tested adapters/payloads** | OpenAI, Anthropic, and Google provider-native requests remained bounded to dispatch-selected behavior |
| Third-party adapter trust | **Process-local slice satisfied** | manifest/artifact/runtime/provider/operation/capability/revocation binding; production package/transitive trust remains open |
| Restrictive host/TEO authority intersection | **Process-local slice satisfied** | deny-wins and more-restrictive-control-wins against tested scopes |
| Exact execution-envelope integrity | **Process-local slice satisfied** | exact risk/capability/operation/target/parameters/side effects/prerequisites/attempt budget |
| Brokered cross-process authority/replay | **Conformant process-lifetime slice satisfied** | separate host processes cannot mint through the exposed gateway, mutate bound dispatch/action, replay or race two successful claims, or multiply retry budget; compromised-host bypass, remote/distributed authenticity, host identity, restart persistence, and effect evidence remain open |
| Verifier-context independence | **Satisfied at research layer** | tested executor-derived and verdict-priming context rejected |
| Exact artifact/change-set binding | **Satisfied at research layer** | stale, substituted, mutated, wrong-task/dispatch/change/target PASS evidence rejected |
| Authority-surface reconciliation | **Static runtime-wired slice satisfied** | runtime-derived canonical YAML/JSON authority paths, presence and content fingerprinting, exact declaration reconciliation, and tested stale/omitted/extra/aliased path resistance; dynamic executable hooks/plugins/transitive code remain open |
| Recursion resistance | **Process-lifetime slice satisfied** | root dispatch/budget binding with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC authorization plus replay/stale/cross-root/race/release-reset resistance; restart-durable, distributed, scheduler, and compromised-host boundaries remain open |
| Freshness binding | **Exact local classification slice satisfied** | current/compatible/update-available/stale-unsupported/mismatched classification from exact authority-owned bindings; typed configuration canonicalization and tested mixed/unknown/host-mislabeled rejection; production catalog provenance, remote authenticity, downgrade, expiry, and distributed coordination remain open |

Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, #644, #658, and corrected freshness validation CI #678. Red-canary CI #676 is retained as evidence that the first freshness encoder failed on a typed YAML date before typed canonicalization was introduced. CI evidence proves the tested repository research boundary only; it does not promote the contract into normative runtime authority.

## Anti-patterns

Treat the following as integration failures:

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
- collapsing Team, Worker, and Specialist into host-local labels while emitting a TEO dispatch record;
- treating TEO orchestration authority as automatic host backlog or portfolio authority;
- claiming a revision pin is current without a freshness/compatibility judgment;
- giving executor and verifier identical reasoning context by default and calling the result independent;
- allowing stale verification evidence to authorize later or unrelated mutations;
- protecting a hand-maintained authority-file list without reconciling it to actual runtime wiring;
- treating static authority-path discovery as proof that dynamic executable hooks or plugins cannot create additional authority surfaces;
- protecting policy text while leaving the action or finalization path able to ignore it;
- allowing a successful sandbox, test, or verifier result to self-authorize a broader production action.

## Evidence required before normative promotion

The contract remains research until the complete promotion case is supported. Current status is deliberately granular so a satisfied process-local or brokered conformant slice is not confused with production readiness.

1. **Premortem replay:** demonstrate that the contract directly prevents or truthfully detects all original failure paths. **Partially supported; complete integrated replay remains open.**
2. **Two-host validation:** test materially different host architectures. **Satisfied for research architecture diversity.**
3. **Context economics:** compare bounded projection with naive corpus loading for prompt size, provider token usage, latency, and task adherence. **Static payload-size slice satisfied; provider token, latency, and adherence evidence remain open.**
4. **Identity preservation:** verify host invariants remain intact while selected specialists retain canonical definitions. **Further architecture-diverse executable evidence remains open.**
5. **Capability correctness:** prove required capabilities resolve to real host implementations and unknown capabilities fail closed. **Partially supported; broader host coverage remains open.**
6. **Capability classification:** prove pre-routing safety, runtime, authority, verification, maintenance, and TEO-dispatched execution surfaces are classified without bypasses or unnecessary loops. **Partially supported.**
7. **Dispatch authorization:** prove governed execution cannot invoke a TEO-dispatched capability without authority-owned dispatch evidence. **Process-local and brokered conformant process-lifetime adversarial slices satisfied; production remote/distributed authenticity, host identity, restart persistence, and bypass resistance remain open.**
8. **Adapter integrity:** prove the executor cannot widen its own capability binding. **Process-local adversarial slice satisfied; production package provenance, loading, dependencies, downgrade, and distributed trust remain open.**
9. **Autonomy correctness:** prove routine multi-step work can remain autonomous while explicit human-authority requirements remain blocking. **Open as an integrated host-conformance gate.**
10. **Authority intersection:** prove host and TEO constraints resolve by deny-wins/more-restrictive-control-wins. **Process-local adversarial slice satisfied; distributed synchronization remains open.**
11. **Verification honesty:** prove unsupported independence is surfaced rather than simulated. **Verifier-context independence is satisfied at the research layer; broader host declaration/conformance remains open.**
12. **Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Process-lifetime slice satisfied by the 2026-08-14 recursion-resistance harness and CI #658; restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host boundaries remain open.**
13. **Registry freshness:** prove stale or mismatched TEO release, policy, registry, overlay, or executable-composition bindings are detected. **Exact local stale/mismatch detection slice satisfied by the 2026-08-14 freshness-binding harness and corrected CI #678; production compatibility-catalog provenance, remote authenticity, downgrade resistance, expiry, and distributed coordination remain open.**
14. **Routing conformance:** prove host-local taxonomies cannot collapse Team, Worker, Specialist, Capability, Implementation, or Verification fields. **Partially supported by validation rounds; formal conformance remains open.**
15. **Portfolio-authority separation:** prove TEO routing cannot silently seize host backlog, product-priority, or task-admission authority unless explicitly delegated. **Research principle established; executable promotion evidence remains open.**
16. **Verifier-context independence:** preserve required domain constraints without inheriting executor reasoning/implementation framing. **Satisfied at the non-normative research layer by PR #146 and CI #580.**
17. **Artifact-bound verification:** reject stale, mismatched, mutated, or wrong-target PASS evidence. **Satisfied at the non-normative research layer by PR #146 and CI #580.**
18. **Authority-surface reconciliation:** derive or reconcile authority surfaces against executable runtime wiring and fail on omissions. **Static runtime-wired YAML/JSON configuration and policy slice satisfied by the 2026-08-14 research harness and CI #644; dynamic path construction, arbitrary executable hooks/plugins/loaders, transitive code identity, and production authenticity remain open.**
19. **Integration freshness state:** distinguish current, compatible, update-available, unsupported, and mismatched TEO pins/vendorized copies. **Exact local classification semantics satisfied by the 2026-08-14 freshness-binding harness and corrected CI #678; production catalog governance/provenance, remote authenticity, downgrade resistance, expiry, and distributed coordination remain open.**
20. **Independent review:** challenge whether the integration layer creates a second routing/authority plane or weakens TEO invariants. **Open for any normative proposal.**
21. **Exact execution-envelope integrity:** bind risk, capability, operation, target, canonical parameters, side effects, prerequisites, and attempt budget. **Process-local and brokered conformant process-lifetime slices satisfied; production target canonicalization, tenant/credential binding, compromised-host bypass resistance, remote/distributed authenticity, effect evidence, restart-durable replay, and distributed retry coordination remain open.**

## Relationship to current TEO work

This work extends, rather than replaces, existing TEO architecture and research:

- **Mission Control:** remains the orchestration authority for an admitted task.
- **Specialist Execution Envelope:** host embedding now has concrete process-local and brokered process-lifetime evidence for scoped context, dispatch authorization, exact action binding, replay resistance on the conformant path, verifier-context separation, static runtime-wired authority-surface reconciliation, and exact local freshness binding.
- **Resource Budget and Admission Contract:** delegation depth, spawn count, context/token budgets, parallelism, and host task admission remain directly relevant to external-host recursion control.
- **Action Authority Plane:** host tool authorization remains distinct from provider access and TEO model routing; current research strengthens restrictive intersection and exact-action binding.
- **Final Execution Provenance:** `docs/specification/final-execution-provenance.md` can expose the observed successful route to a host after canonical evidence revalidation, but that projection carries no routing or action authority.
- **Execution Environment & Recovery Contract:** future isolation/checkpoint/rollback research must compose with host authority and exact action envelopes rather than self-authorize production execution.
- **Task Intent & Action Authority Contract:** future request-authority research sits before host execution authorization and must ensure the host/TEO intersection cannot widen the originating request or delegated authority ceiling.

No new specialist is proposed by this document. Existing architecture, platform, security, verification, and orchestration roles cover the current research responsibility.
