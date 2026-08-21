# Roadmap

TEO has completed the foundation, team architecture, routing validation, registry population, reference control-plane, operational-evidence, shadow-evaluation, and qualified-human authority milestones declared to date.

The current roadmap is focused on proving and operating the decision system while improving the internal maintainability of the Python reference implementation without changing product behavior or authority.

For the current operational state, completion estimates, active milestone, and NOW/NEXT/LATER sequencing, see [`progress-tracker.md`](progress-tracker.md). This roadmap defines direction; the progress tracker records execution state.

## Completed foundation

- public project identity, Constitution, Lexicon, and stewardship rules
- ten accountable teams
- stable worker architecture
- 82 active preserved specialist role cards
- provider/model/capability registries
- deterministic task and risk routing
- fallback, escalation, verification, and human-authority controls
- runnable Python reference control plane
- guarded live provider execution for bounded `high_volume_simple` work
- bounded retry and canonical fallback redispatch
- provider-family circuit state
- content-free runtime telemetry
- provider-diverse live independent verification
- six-card regulated evidence/freshness pilot with completed executable stability qualification

## Current: control integrity and evidence-governed operation

### Control integrity

- require effective risk to preserve all higher risk signals
- prove all 82 active specialists are deterministically spawnable
- enforce capability and implementation eligibility at runtime
- require explicit preview-model authorization
- enforce provider-diverse independent verification
- protect local runtime artifacts and credential boundaries
- bind verifier artifacts to authorized runtime roots
- keep caller/user identifiers out of default telemetry
- enforce JSON Schemas at external control-plane boundaries
- keep machine-readable policy and implementation behavior mutation-tested

### Python reference clean-architecture migration

The Python reference implementation is undergoing a behavior-preserving, tranche-based internal architecture migration documented in [`../architecture/python-clean-architecture-migration.md`](../architecture/python-clean-architecture-migration.md) and tracked by Issue #197.

Current merged state:

- **Tranche 1 / PR #196:** deterministic task classification and monotonic risk assessment were extracted from `engine.py` into the pure `teo_reference.domain.routing` boundary.
- **Tranche 2 / PR #198:** finalization was extracted behind `teo_reference.application.finalization.FinalizationService` and `ArtifactIntegrityPort`, with the existing local-filesystem integrity behavior retained behind an adapter and the established engine/API compatibility surface preserved.
- **Tranche 3 is next:** extract dispatch orchestration, selectors, and resolvers behind an application service while preserving canonical dispatch records, routing explanations, errors, provider diversity, preview gating, specialist risk elevation, capability constraints, and verifier planning.

Reference Implementation CI #869 validated the merged Tranche 2 tree with 1,008 tests, 574 tracked-file layout checks, 42 parsed JSON Schemas, valid linked configuration, regulated-specialist evidence validation, and the provider-diverse artifact-bound end-to-end lifecycle.

This migration is compatible post-v1 maintenance. It does **not** change the current operational priority, live-execution scope, routing policy, provider/model assignment, risk semantics, qualified-human authority, or evidence requirements. Each tranche must be independently revertible and CI-qualified before acceptance.

### Verifier calibration evidence

Build deterministic and empirical calibration evidence for the guarded verifier rubric using the fixed reference corpus, machine-checkable invariants, provider-diverse observations, and other reproducible evaluation methods.

Independent human calibration is an optional evidence-enhancement study under Issue #75. It is not a release, routing, model-selection, live-scope, or architectural gate. A completed human study is required only before making a specifically scoped claim that verifier evidence has been independently human-validated.

Measure:

- false-pass rate
- false-fail rate
- `needs_human` rate
- criterion-level confusion
- repeatability
- provider/model disagreement
- adversarial candidate-output resistance
- latency and normalized usage
- retry/fallback relationship to outcomes

Do not broaden live verification based on model confidence alone. Broader scope remains governed by applicable authority, capability, verification, telemetry, recovery, evidence, risk, and maintainer-review controls. Optional human calibration may strengthen the evidence base but does not create a separate approval authority.

### Regulated specialist evidence

The bounded six-card regulated specialist evidence pilot has completed its current maintainability milestone. Two formal refresh cycles are preserved in validation history, followed by an executable stability qualification with five complete clean authority-resolution replays, three independent repeatability runs, 15 of 15 governed fail-closed mutations, controlled authority-move handling, and an external-network 7-of-7 authority observation.

The seven-day authority-resolution cadence remains mandatory continuous drift detection. There is no elapsed-time countdown gate. Qualification does not auto-authorize a larger registry: any next risk-tier batch requires explicit approval and a separate reviewed bounded change.

### Completed operational evidence chain

The current reference control plane now includes completed declared milestones for:

- canonical Route-Outcome Evidence with primary/fallback lineage, retry preservation, verification linkage, version context, and integrity protection;
- the Benchmark and Outcome Lab with controlled replay, multi-verifier disagreement, and independently challenged consequential conclusions;
- source-backed cost attribution with explicit billable surfaces, effective-dated evidence, and fail-closed unknown semantics;
- governed Shadow Route Evaluation with bounded specialist #82 recommendation states, anti-Goodhart controls, independent challenge, and no live policy-write authority;
- qualified-human approval with scoped authority grants, exact evidence-bound requests, append-only dispositions, expiry/revocation, and terminal human finalization;
- optional final-execution provenance projection that revalidates canonical Route-Outcome Evidence and exposes the observed active route through `FinalOutcome` without creating routing, execution, host, or permission authority.

These layers provide evidence and authority control. They do not automatically authorize route changes or broader live execution.

### Qualified-human authority

The explicit approval lifecycle is implemented for work that policy already marks as requiring qualified-human authority.

Human-required model execution remains `awaiting_human` until a separately scoped human authority grant and approval disposition are validated. Model, specialist, verifier, Mission Control, maintainer review, provider access, and billing identity do not self-satisfy that gate.

Completion of this lifecycle does not broaden which tasks require human approval and does not widen live execution.

### Evidence-governed live execution expansion

The current operational priority is to evaluate one bounded live task-class expansion at a time beyond the existing low or medium risk `high_volume_simple` canary.

`documentation` is the first staged candidate. Candidate selection, executable no-network preflight, fallback/fresh-verifier repair, direct provider-adapter readiness, and the staged replay harness are complete, but **live activation is not authorized** and provider-backed replay evidence is still pending.

The repaired staged route is:

- primary executor: Claude Sonnet 5 at medium effort;
- provider-diverse non-preview routine fallback: GPT-5.6 Sol;
- primary verifier: GPT-5.6 Terra at medium effort;
- model/provider failure redispatch executor: GPT-5.6 Sol;
- fresh redispatch verifier: Gemini 3.7 Flash at medium effort.

The previous runtime worker override no longer mutates the shared documentation worker. The current `high_volume_simple` route uses Gemini 3.7 Flash with Claude Haiku 4.5 recovery and fresh provider-diverse verifier rotation; regression tests protect that topology.

Claude Sonnet 5 execution, GPT-5.6 Sol execution, and GPT-5.6 Terra verification are implemented at the adapter layer without widening the active canary wrappers or live-verification task scope. Implemented capability is not live-execution authority.

The staged replay harness now provides strict replay-plan and replay-record schemas, full-plan no-network preflight, isolated per-trial circuit state, exact active retry-policy reuse, assigned Terra verification, in-memory replay telemetry, canonical Route-Outcome Evidence construction, and an operator CLI with an explicit live-execution acknowledgement. Automatic fallback is intentionally disabled in this replay milestone so the harness cannot become a hidden alternate live runtime.

The next evidence gate is **provider-backed controlled documentation replay** using the operator replay path. CI conformance with deterministic fake transports does not count as empirical provider-backed evidence. The candidate's `controlled_replay` evidence pointer must remain empty until a real integrity-protected replay record and its canonical Route-Outcome Evidence set exist.

Shadow evaluation, rollback/recovery evidence, and independent review of any later active-scope change remain subsequent gates.

Any candidate expansion must preserve:

- non-lowerable effective risk;
- capability-valid execution and fallback;
- provider-diverse recovery and independent verification;
- retry, fallback, circuit-state, telemetry, and Route-Outcome Evidence;
- explicit rollback or recovery behavior;
- shadow and cost evidence as supporting signals rather than sole promotion criteria;
- qualified-human approval wherever policy independently requires it;
- explicit preview-model acceptance;
- provider-access separation;
- conformance and mutation resistance for live-scope boundaries.

High and critical live execution remains outside the current guarded runtime and is not part of the next bounded milestone.

### Distributed runtime hardening

Replace single-process reference persistence where production deployment requires:

- coordinated distributed circuit state
- concurrency-safe telemetry export
- access control and retention
- integrity and recovery guarantees
- distributed workflow/audit correlation
- streaming and richer latency evidence

### Host integration contract research

External-host integration evidence has exposed a distinct embedding boundary that is not equivalent to missing core orchestration architecture. A pre-existing AI host can misintegrate TEO by loading the entire specialist corpus into prompt context, replacing host identity with specialist personas, over-applying human-approval semantics, failing to bind host-native tools to TEO capabilities, simulating independent verification inside one model session, or silently expanding TEO orchestration authority into unrelated host authority.

The non-normative research path is recorded in:

- [`../../research/runtime/2026-08-12-host-agent-integration-premortem.md`](../../research/runtime/2026-08-12-host-agent-integration-premortem.md);
- [`../../research/runtime/2026-08-12-host-integration-validation-round-1.md`](../../research/runtime/2026-08-12-host-integration-validation-round-1.md);
- [`../../research/runtime/2026-08-12-host-integration-validation-round-2.md`](../../research/runtime/2026-08-12-host-integration-validation-round-2.md);
- [`../../research/roadmaps/host-integration-contract.md`](../../research/roadmaps/host-integration-contract.md).

The candidate Host Integration Contract should preserve:

- host identity, safety floor, permissions, product constraints, and host/user portfolio authority separately from TEO orchestration authority;
- executable TEO version, registry, revision, and freshness binding rather than file-count or copied-policy inference;
- bounded context projection and deterministic specialist narrowing before semantic retrieval;
- host-native capability adapters rather than host-specific edits to specialist cards;
- explicit autonomy semantics without creating universal human-approval gates;
- restrictive host/TEO authority intersection, with deny-wins and more-restrictive-control-wins semantics;
- dispatch-bound executable capability authorization and protected adapter authority surfaces;
- truthful independent-verification capability declarations with purpose-built verifier context rather than executor-role mirroring;
- artifact/change-set binding so stale PASS evidence cannot authorize later or unrelated mutations;
- runtime-derived or reconciled inventories of authority-bearing integration surfaces;
- bounded orchestration re-entry, specialist spawning, attempts, and parallelism;
- explicit conformance declarations for supported, partial, and unsupported TEO surfaces;
- shadow-first validation before governed activation in an external host.

The **two-host architecture-diversity research gate is satisfied** by two materially different integration patterns: a host-local vendorized/capability-adapter architecture and a separate revision-pinned upstream-dispatch/downstream-execution-adapter architecture. Supporting ancestor experiments add further assurance and proportional-governance evidence but are not needed to inflate the host count.

Additional provider-independent research has also satisfied the static bounded-context payload slice, process-local dispatch-provenance and bundled-adapter self-expansion slice, process-local third-party adapter non-self-authorization slice, restrictive host/TEO authority-intersection and execution-scope slice, exact process-local execution-envelope integrity slice, verifier-context independence, and exact artifact/change-set stale-PASS resistance. Those are research findings, not normative host certification.

The `teo-host-integration/0.1` reference candidate now makes one bounded host-native execution/verification message path executable without promoting the broader contract. It preserves TEO ownership of route, retry/fallback authorization, verifier selection, and evidence acceptance; enforces one unresolved execution instruction at a time, monotonic primary-to-fallback progression, terminal success, and no execution after verification begins; and leaves provider authentication/transport with the host. It remains explicitly non-normative and non-production.

Remaining pre-normative evidence is narrower and materially different: provider/model input economics, end-to-end latency and task adherence, production-grade external-adapter package provenance and authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, cross-process dispatch and exact-action authenticity/replay, distributed retry-budget coordination, revision freshness and expiry semantics, portfolio/task-admission authority separation, runtime-derived authority-surface reconciliation, recursion/recovery failure behavior, and independent review against a parallel routing or authority plane.

This research does not alter current runtime policy, active specialist count, live-execution scope, verifier independence, human authority, or Progress Tracker sequencing.

### Execution environment and recovery contract research

TEO has accepted a future non-normative research track for governing isolated execution, pre-change checkpointing, rollback, and recovery verification through a vendor-neutral contract. The research is recorded in [`../../research/roadmaps/execution-environment-recovery-contract.md`](../../research/roadmaps/execution-environment-recovery-contract.md).

The contract should define when isolation is required, what guarantees an execution substrate must expose, how a checkpoint is bound to the exact governed action and target, how rollback preserves the original effective-risk and authority floor, how recovery is independently verified, and how sandbox evidence may support but never self-authorize later production execution.

Execution substrates remain replaceable host/runtime implementations. TEO should not become a container runtime, microVM manager, deployment platform, database backup engine, or universal workflow engine merely to implement this capability. The research must remain compatible with Host Integration authority intersection, exact execution-envelope binding, canonical evidence, independent verification, and current live-scope controls.

This accepted research direction does not alter the current `documentation` replay gate, active `high_volume_simple` scope, provider routing, specialist roster, qualified-human authority, or stable `v1.0.0` contract.

### Task intent and action authority contract research

TEO has accepted a future non-normative research track for making the authority granted by an originating request explicit before routing, delegation, host-native action, recovery, or state-changing execution. The research is recorded in [`../../research/roadmaps/task-intent-action-authority-contract.md`](../../research/roadmaps/task-intent-action-authority-contract.md).

The contract should distinguish assessment, recommendation, preparation, execution, and verification authority without using task topic, model capability, host permission, or specialist eligibility as a proxy for user intent. A request-authority record should act as an authority ceiling that later TEO policy, Host Integration authority intersection, capability controls, qualified-human requirements, and exact action-envelope authorization may narrow but never silently widen.

The research must remain content-minimized, preserve delegated-child authority inheritance, keep verification separate from repair authority, and reject fallback, escalation, sandbox, recovery, or host-standing-permission paths that increase the action scope granted by the originating request.

This accepted research direction does not modify the canonical Task Request or Dispatch Record, does not create a second routing or permissions plane, and does not alter current live scope, provider routing, specialist roster, qualified-human authority, Progress Tracker sequencing, or the stable `v1.0.0` contract.

## Regulated specialist pilot

Keep the evidence-backed freshness pilot limited to the approved six cards until maintainability is demonstrated through repeated refresh cycles, authority resolution, provenance checks, expiry behavior, independent verification, mutation tests, and explicit approval.

A broader regulated evidence registry is not authorized merely because the pilot validates structurally.

## Live execution expansion gate

Broaden live execution by task class only when the applicable authority, capability, verification, telemetry, recovery, evidence, and human-approval controls have demonstrated reliable behavior.

The current `high_volume_simple` low or medium risk canary remains the only accepted live execution scope. `documentation` has a validated staged replay harness but cannot enter active telemetry, verification, or guarded execution scope until provider-backed replay, shadow, recovery, and independent-review gates pass.

High and critical live execution remains outside the current guarded runtime.

## Community and licensing

Finalize licensing and contribution terms before representing TEO as open source or inviting external code contribution under reuse rights that have not yet been granted.

The roadmap is directional. Routing, authority, verification, evidence quality, and behavior-preserving maintainability remain the priority.
