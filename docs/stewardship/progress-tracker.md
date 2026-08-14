# TEO Progress Tracker

**Status:** active stewardship record  
**Last reconciled:** 2026-08-14  
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
| Current validated scale | 842 tests passed, 526 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #651 |
| Documentation reconciliation baseline | CI #602: 802 tests, 515 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse end-to-end pass |
| Host-integration research validation | CI #658: 863 tests, 528 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the corrected executable process-lifetime recursion-resistance research head |
| Host Integration Contract | Two-host architecture diversity, static bounded-context payload, process-local dispatch provenance, bundled-adapter payload self-expansion, process-local third-party adapter trust, process-local restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, and process-lifetime recursion-resistance research slices satisfied; contract remains non-normative and restart-durable/distributed recursion, production scheduler containment, dynamic authority discovery, and production/distributed authenticity remain open |
| Artifact-bound finalization | PR #154 merged; verifier-observed local `file://` identity, SHA-256, and byte length are revalidated under an explicit authorized artifact root before artifact-backed PASS can complete; independently verified |
| Final execution provenance | Optional read-only projection from revalidated canonical Route-Outcome Evidence into `FinalOutcome`; implemented without routing, execution, host, or permission authority |
| Regulated evidence pilot | 6 specialists, intentionally bounded |
| Repository information architecture | R1 through R5 complete |
| Guarded live execution | bounded `high_volume_simple` canary at low or medium effective risk |
| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |
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
| Control integrity | Operational | 90% | Post-v1 hardening with conformance, mutation resistance, and exact artifact-bound finalization | Continue closing uncovered finalization, authority, and recovery mutation gaps as discovered |
| Verifier calibration evidence | In progress | 70% | Deterministic and empirical verifier evidence | Strengthen repeatability, disagreement, adversarial, and route-specific evidence |
| Regulated specialist evidence pilot | In progress | 70% | Formal refresh cycle 1 completed across the six-card pilot | Complete refresh cycle 2 and establish 30-day scheduled authority-resolution stability before any expansion decision |
| Route-outcome evidence | Complete | 100% | Canonical executable route-outcome evidence contract | Preserve schema/version compatibility and feed controlled evaluation |
| Benchmark and Outcome Lab | Complete | 100% | Controlled evaluation, live replay, disagreement, and conclusion handoff | Preserve compatibility and feed governed downstream evaluation |
| Source-backed cost attribution | Complete | 100% | Effective-dated reproducible route-level attribution | Maintain first-party price evidence and feed governed downstream evaluation |
| Shadow route evaluation | Complete | 100% | Governed recommendation-only evidence loop | Preserve evidence and authority boundaries through later reviewed adaptation |
| Qualified-human approval lifecycle | Complete | 100% | Evidence-bound qualified-human authority lifecycle | Preserve scope, integrity, expiry, revocation, temporal causality, and finalization boundaries |
| Live execution expansion | In progress | 65% | `documentation` staged replay harness and operator evidence path validated | Produce provider-backed controlled documentation replay evidence |
| Distributed runtime hardening | Future | 20% | Single-process reference behavior proven | Add coordinated state, concurrency-safe export, access control, retention, integrity, and recovery |
| Licensing and contribution terms | Pending | 10% | Public repository with no reuse license selected | Select licensing and contribution terms before representing TEO as open source |

The Host Integration Contract remains a non-normative research track rather than a scored operational workstream. Satisfying its architecture-diversity, bounded-context static-payload, dispatch-provenance, bundled-adapter, process-local third-party adapter trust, restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, or process-lifetime recursion-resistance research slices does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage. Dynamic executable-hook discovery, production/distributed authenticity, host identity, effect-evidence, restart-durable/distributed recursion state, production scheduler containment, and remote-transport gates remain open.

The Execution Environment & Recovery Contract is likewise a non-normative future research track rather than a scored operational workstream. Its acceptance records direction only: isolation requirements, checkpoint binding, rollback/recovery authority, recovery verification, and simulation-to-promotion boundaries remain research questions and do not change current live authority or progress percentages.

The Task Intent & Action Authority Contract is also a non-normative future research track rather than a scored operational workstream. Its acceptance records a request-authority research gap between task interpretation and exact execution authorization; it does not change the canonical Task Request, Dispatch Record, live authority, or progress percentages.

Final execution provenance is a compatible evidence extension rather than a separate scored workstream. It projects only already-validated Route-Outcome Evidence into a host-consumable `FinalOutcome` and cannot create routing, request-action, host, capability, or live-execution authority.

## NOW

### Evidence-governed live execution expansion

Reconsider live-scope expansion task class by task class using the now-complete route-outcome, Benchmark Lab, source-backed cost, shadow-evaluation, recovery, verification, and qualified-human authority evidence chain.

`documentation` is the first bounded candidate. It is **staged only** and has no live-execution authority. The active guarded runtime remains limited to `high_volume_simple` at low or medium effective risk.

Reference Implementation CI run #463 validated the original candidate-selection and executable-preflight slice with 634 passing tests, 463 tracked-file layout checks, regulated evidence validation, 38 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

The candidate preflight exposed an unintended global worker override that changed ordinary `documentation` routing. That override has now been removed. Canonical documentation routing again preserves Sonnet 5 as primary, GPT-5.6 Sol as the provider-diverse non-preview routine fallback, GPT-5.6 Terra as the primary verifier, and Gemini 3.6 Flash as the fresh provider-diverse verifier after Sonnet or Anthropic failure redispatch. The route-level Gemini 3.1 Pro Preview fallback remains blocked without explicit acceptance.

The exact staged adapter capabilities needed by that topology are now implemented without granting live authority: Claude Sonnet 5 bounded execution carries assigned effort through Anthropic `output_config.effort`; GPT-5.6 Sol is implemented by the OpenAI Responses adapter; and GPT-5.6 Terra is implemented by the strict structured-output OpenAI verifier. Existing canary wrappers and live-verification task scope remain `high_volume_simple` only.

Reference Implementation CI run #473 validated this topology and adapter-readiness gate with 641 passing tests, 465 tracked-file layout checks, regulated evidence validation, 38 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example. The same suite also proves the existing Flash-Lite -> Haiku throughput recovery and fresh-verifier rotation remain intact after removal of the global worker override.

The staged documentation replay harness is now implemented. It provides strict replay-plan and replay-record schemas, whole-plan no-network routing preflight, exact candidate-route checks, active retry-policy alignment, isolated per-trial circuit state, assigned Terra verification, in-memory replay telemetry, canonical Route-Outcome Evidence generation, and an operator CLI with explicit `--execute-live` acknowledgement. Automatic fallback is intentionally disabled in this replay milestone so a staged evidence runner cannot become a hidden alternate live runtime. Provider-scoped recovery, rollback, and deliberate fallback execution remain separate later gates.

Reference Implementation CI run #488 validated the clean replay-harness and operator-path state with 651 passing tests, 472 tracked-file layout checks, regulated evidence validation, 40 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example. CI uses deterministic fake provider transports for conformance and therefore does not constitute empirical provider-backed documentation replay evidence.

Reference Implementation CI run #506 validated the Actions-native replay path and provider-access blocker record with 653 passing tests, 474 tracked-file layout checks, regulated specialist evidence validation, 40 parsed JSON Schemas, valid linked configuration with zero issues, and the provider-diverse end-to-end example. That validation does not create empirical provider-backed replay evidence or widen live authority.

Reference Implementation CI run #514 is the current accepted substantive repository-validation baseline after the targeted finalization -> authority -> recovery control-integrity audit: 657 passing tests, 477 tracked-file layout checks, regulated specialist evidence validation, 40 parsed JSON Schemas, valid linked configuration with zero issues, and the provider-diverse end-to-end example. The audit closed a proven qualified-human temporal-causality gap and added recovery-authority regression coverage without changing live scope, routing, risk, provider access, or approval authority. Control integrity remains intentionally scored at 90% because continuing mutation depth and newly discovered failure modes remain an ongoing adversarial discipline.

A follow-on targeted mutation audit then weakened ten finalization, authority, expiry, and recovery invariants one at a time. Reference Implementation CI run #519 intentionally exposed four surviving mutants, proving four test-evidence gaps rather than production-control defects. Exact approval, request, and authority-grant expiry boundaries plus caller-risk versus dispatch-effective-risk fallback preservation were then covered explicitly. Reference Implementation CI run #521 killed **10 of 10 targeted mutants** and passed 671 tests, 479 tracked-file layout checks, regulated specialist evidence validation, 40 parsed JSON Schemas, valid linked configuration with zero issues, and the provider-diverse end-to-end example. This is control-integrity evidence hardening and does not replace CI #514 as the accepted substantive runtime baseline or change live authority.

Host Integration Validation Round 2 then completed a separate provider-independent research milestone. Its merge candidate passed Reference Implementation CI #546 with 680 tests, 491 tracked-file layout checks, regulated specialist evidence structural validation, 41 parsed JSON Schemas, valid linked configuration with zero issues, and the provider-diverse end-to-end example. Two materially different external-host integration architectures have now been examined, so the two-host architecture-diversity research gate is satisfied. This does not replace CI #514 as the accepted substantive runtime baseline, does not make the Host Integration Contract normative, and does not change live authority or the `NOW` workstream.

A first Host Integration adversarial slice then measured bounded specialist projection against naive loading of every runtime-resolved active specialist card. Reference Implementation CI #552 passed 681 tests and 494 tracked-file layout checks while the research harness measured 1,157,957 bytes across 82 active role cards, with 98.7805% mean and 97.6295% worst-case payload reduction for one-card projection. This supports only the static specialist-card prompt-size slice; provider token usage, latency, task adherence, and architecture-diverse live execution remain unproven.

The next Host Integration adversarial slice made dispatch provenance and bundled-adapter self-expansion executable. The generic provider executor was confirmed not to independently prove that a host-supplied `DispatchRecord` came from the TEO dispatcher. A non-normative process-local research authority then rejected 14 independent dispatch tamper classes, an unissued token, and cross-dispatch token reuse before adapter invocation. The bundled OpenAI, Anthropic, and Google adapters also omitted attempted tool, MCP, web-search, and fallback-expansion fields from provider-native requests while preserving the dispatch-selected model. CI #554 was intentionally red because the first Anthropic fixture omitted Sonnet 5's required effort; after correcting that fixture without weakening the boundary, CI #555 passed 703 tests and 497 tracked-file layout checks. That slice left arbitrary third-party adapter provenance, registration, and manifest integrity open.

A following Host Integration adversarial slice tested whether an external adapter could self-authorize through manifest claims, implementation-artifact replacement, factory substitution, provider drift, capability widening, token reuse, or revocation bypass. A non-normative process-local adapter authority bound the exact manifest snapshot, measured implementation artifact digest, registered runtime type, provider family, single-attempt operation, capability scope, and revocation state before invoking the unchanged Provider Adapter Contract. Reference Implementation CI #560 passed 719 tests and 500 tracked-file layout checks, with all declared unauthorized cases rejected before provider execution while the exact registered positive control executed once. This supports only process-local non-self-authorization; production package provenance, authority-controlled loading, transitive dependency identity, distributed persistence, downgrade resistance, and execution isolation remain open.

The next Host Integration adversarial slice made restrictive host/TEO authority intersection and host execution-scope binding executable against the current repository live-authority boundary. The research gate derives TEO authority from the exact dispatch plus `active_scope`, then intersects it with an explicit host task, risk, capability, provider, operation, and active-state permission scope. CI #565 passed 742 tests and 503 tracked-file layout checks. Host denial blocked otherwise TEO-authorized actions, TEO denial blocked the host-authorized staged `documentation` task and high-risk execution, explicit host deny won over host allow, host-only capabilities could not widen the dispatch, and authorization could not be reused after dispatch, capability, operation, TEO-scope, or host-scope changes. This supports deny-wins and more-restrictive-control-wins semantics plus exact process-local execution-scope binding; distributed authority synchronization and cross-process replay resistance remain open.

A further Host Integration adversarial slice bound one exact authority-issued host action beyond capability and operation authorization. A two-stage process-local authority binds the complete dispatch plus exact effective risk, capability, operation, resource target, canonical parameters, side-effect class, prerequisites, and TEO attempt budget before applying the more-restrictive host execution scope. Reference Implementation CI #570 passed 767 tests and 506 tracked-file layout checks. Host-created action tokens, risk lowering, target, parameter, or side-effect mutation, missing prerequisites, retry-budget multiplication, scope replacement, token replay, and cross-dispatch reuse were rejected before the action callback. This supports exact process-local execution-envelope integrity; production resource canonicalization, credential or tenant binding, cross-process authenticity, distributed retry coordination, and a normative exact-action schema remain open. The exact reconciled PR #144 head later passed Reference Implementation CI #573 with the same 767-test, 506-tracked-file, 41-schema, valid-configuration, provider-diverse end-to-end result.

The next bounded Host Integration adversarial slice then tested verifier-context independence plus exact artifact/change-set verification and stale-PASS resistance. The research boundary rejects tested executor reasoning, executor messages, conversation history, prior verdicts, and executor self-assessment from the independent-verifier request, and binds a PASS to the exact task, dispatch, change, artifact, revision, SHA-256 digest, and target reference. The 21-case matrix also rejects wrong-task, wrong-dispatch, wrong-change, sibling-artifact, stale-revision, post-verification content mutation, wrong-target, non-PASS, failed-execution, blank-identity, and malformed-digest cases. Reference Implementation CI #577 passed 788 tests and 509 tracked-file layout checks, regulated specialist evidence validation, 41 parsed JSON Schemas, valid linked configuration with zero issues, and the provider-diverse end-to-end example. The exact reconciled PR #146 head then passed CI #580 with the same 788-test, 509-layout, 41-schema, valid-configuration result. At that Host Integration research slice, the canonical `VerificationResult` and `FinalOutcome` schemas remained unchanged and no live authority widened; the later route-backed final execution provenance change was a separate compatible extension to `FinalOutcome`.

A compatible post-v1 evidence extension then added route-backed final execution provenance. Finalization may accept a canonical Route-Outcome Evidence record, revalidate it, and project the successful active provider/model route into optional `FinalOutcome.execution_provenance`. The projection is read-only evidence: it cannot nominate a provider, override routing, authorize a host action, widen live scope, or replace canonical Route-Outcome Evidence.

The accepted Task Intent & Action Authority research direction was then recorded on top of that provenance baseline. Exact-head Reference Implementation CI #602 passed **802 tests**, **515 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse end-to-end example. This is the documentation-reconciliation baseline; it does not replace CI #514 as the accepted substantive runtime-control baseline, create empirical provider-backed documentation replay evidence, or make the new authority research normative.

The next provider-independent Host Integration slice moved the existing exact execution-envelope authority across a real process boundary without promoting a normative protocol. A loopback broker retained all mutable TEO-side authority/replay state, exposed no action-issuance operation to the host, required exact session/dispatch/action binding, rejected unknown widening fields, serialized duplicate claims, and preserved sequential attempt/retry-budget enforcement across separate host processes. CI #624 was intentionally red because the first test wiring loaded two distinct `ExecutionEnvelopeError` class identities; the underlying negative cases were correctly rejected but escaped structured transport normalization. After correcting only that test-instance identity, CI #625 passed. The final PR #156 head then passed Reference Implementation CI #626 with **817 tests**, **520 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse end-to-end example. PR #156 was squash-merged as `558a54a3cf198e6f7d31468d353ee13c4d1b276d`. This supports brokered conformant process-lifetime cross-process authority and replay resistance only; a compromised-host bypass, remote transport authenticity, host identity, resource/credential/tenant binding, restart/distributed replay state, and effect-evidence remain open.

The next provider-independent Host Integration adversarial slice derived statically wired authority configuration and policy paths from executable Python runtime source rather than trusting a second hand-maintained inventory. Present files are content-fingerprinted, dormant-but-wired paths remain in the inventory, and a declared host inventory must match the derived set exactly. CI #643 intentionally failed **2 tests while 840 passed** because the first research head incorrectly assumed the still-present empty `runtime-worker-overrides.yaml` authority surface was absent and over-specified one symlink error message. Repository truth showed the file remains present with empty override payloads, so the research assumption was corrected without changing production behavior. Exact corrected head `9cc5694474d310bc50bac1aa342b61f45fb17e10` then passed CI #644 with **842 tests**, **525 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. This supports only static runtime-wired YAML/JSON authority-surface reconciliation; dynamic path construction, arbitrary executable hooks/plugins/loaders, transitive code identity, signer/origin authenticity, and compromised-host bypass resistance remain open. See [`../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md).

The next provider-independent Host Integration slice then bounded process-lifetime orchestration recursion independently from same-dispatch provider retry. A TEO-side root authority binds the exact dispatch snapshot to immutable ceilings for re-entry depth, total descendants, specialist spawns, concurrently active descendant branches, and recovery generations. A Security and Authority Boundaries review removed an unnecessary pending-authorization store before acceptance; the corrected design uses stateless HMAC-bound admission claims tied to the exact root revision. Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. Tested forgery, replay, stale claims, cross-root reuse, release-based budget reset, recursive recovery, and raced same-revision claims fail closed. Restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host boundaries remain open. See [`../../research/runtime/host-integration-recursion-resistance-2026-08-14.md`](../../research/runtime/host-integration-recursion-resistance-2026-08-14.md).

A separate normative control-integrity remediation then closed the calibrated External Independent Technical Verifier Task 002 gap. PR #154 bound the exact verifier-observed local artifact identity, SHA-256, and byte length into `VerificationResult`, required an explicit authorized artifact root at finalization, and revalidated the current artifact before an artifact-backed PASS can complete. Exact refreshed head `8e0d324a82568ab9fb52b097e3559add2111cb34` passed Reference Implementation CI #634 with **825 tests**, **522 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. The calibrated external verifier returned PASS on the original remediation and separately confirmed that PASS remained applicable after the current-main refresh. PR #154 was squash-merged as `04cd5c6b55c6c104399f09ee0913bd7c23bb924f`. This closes the scoped normative exact-artifact-binding gap without widening routing, provider/model assignment, live scope, capability, qualified-human, verifier, or filesystem authority.

Completion criteria for the current bounded milestone:

- select one explicitly bounded task class beyond the current `high_volume_simple` canary only when the candidate scope is low or medium effective risk and capability-valid;
- preserve non-lowerable effective risk and existing task-class authority boundaries;
- preserve provider-diverse fallback and independent verification;
- preserve retry, fallback, circuit-state, telemetry, and canonical Route-Outcome Evidence semantics;
- require explicit rollback or recovery behavior and reproducible evidence before widening scope;
- use shadow-evaluation evidence and source-backed cost only as supporting evidence, never as sole promotion criteria;
- prove the qualified-human approval lifecycle remains enforceable wherever policy independently requires it;
- preserve explicit preview-model acceptance;
- keep provider access and authentication outside routing decisions;
- do not authorize high or critical live execution in this milestone;
- add conformance and mutation tests that fail if live-scope boundaries, rollback, verification, or authority gates are weakened.

Candidate selection, fallback/fresh-verifier topology, direct adapter readiness, and the staged replay harness are now satisfied for `documentation`. The next material gate is a real provider-backed controlled replay using the exact staged plan and current repository revision. That execution must produce the integrity-protected replay record and canonical Route-Outcome Evidence set before the candidate's `controlled_replay` evidence pointer can be populated. Green CI alone must not be mislabeled as empirical replay evidence.

The provider-backed `documentation` replay is intentionally deferred as an open action item until legitimate provider access is supplied through an appropriate execution boundary. Deferral does not close, bypass, or downgrade the evidence gate.

The current `high_volume_simple` low or medium risk canary remains the only accepted live execution scope until a separate bounded activation change satisfies every applicable criterion. `documentation` remains `activation_authorized: false`. Shadow evaluation, rollback/recovery evidence, and independent review of any later active-scope change remain subsequent gates. High and critical live execution remains unauthorized.

## NEXT

No additional workstream is promoted ahead of the current evidence-governed live execution expansion milestone. While its provider-backed replay gate is deferred, provider-independent control-integrity, evidence-maintenance, and non-normative Host Integration adversarial research may continue without changing the sequencing or live-authority boundary. The next live-expansion sequencing decision should be made from repository evidence after provider-backed controlled `documentation` replay and its downstream shadow, recovery, and review gates have either supported or rejected activation.

## LATER

### Host Integration Contract research

The candidate Host Integration Contract has completed its two-host architecture-diversity research gate, the bounded-context static-payload slice, process-local dispatch provenance, bundled-adapter payload self-expansion testing, process-local third-party adapter trust, restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, a brokered conformant process-lifetime cross-process authority/replay slice, a static runtime-wired authority-surface reconciliation slice, and a process-lifetime recursion-resistance slice.

The contract remains non-normative. Before any schema or reference-runtime promotion, remaining evidence includes provider/model input economics, end-to-end latency, task adherence, production-grade external-adapter package provenance, authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, production-grade remote or distributed dispatch/exact-action authenticity and replay beyond the brokered conformant process-lifetime path, result/effect receipt authenticity, restart-durable and distributed retry-budget coordination, revision freshness and expiry semantics, portfolio/task-admission authority separation, dynamic authority-surface discovery for executable hooks/plugins/loaders and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane.

The next bounded provider-independent Host Integration gate should be selected from the remaining roadmap evidence, now narrowed to those genuinely open production, distributed, economic, freshness, dynamic-authority-surface, effect-evidence, and recursion/recovery requirements. This tracker does not promote Host Integration ahead of the deferred provider-backed `documentation` replay milestone.

This research does not alter current Mission Control policy, specialist cards, active roster, verifier rules, provider routing, qualified-human authority, or live-execution scope.

### Execution Environment & Recovery Contract research

TEO has accepted a future non-normative research direction for governing isolated execution, pre-change checkpointing, rollback, and recovery verification through a vendor-neutral contract. The research is recorded in [`../../research/roadmaps/execution-environment-recovery-contract.md`](../../research/roadmaps/execution-environment-recovery-contract.md).

The research must preserve current risk, authority, verification, and Host Integration boundaries. It does not promote a specific sandbox technology, does not authorize simulation-to-production promotion, and does not move ahead of the deferred provider-backed `documentation` replay milestone.

### Task Intent & Action Authority Contract research

TEO has accepted a future non-normative research direction for preserving the action authority granted by an originating request before routing, delegation, host-native action, recovery, or state-changing execution. The research is recorded in [`../../research/roadmaps/task-intent-action-authority-contract.md`](../../research/roadmaps/task-intent-action-authority-contract.md).

The research treats originating request authority as a ceiling that later TEO policy, Host Integration authority intersection, capability controls, qualified-human requirements, and exact execution-envelope authorization may narrow but never silently widen. It must distinguish assessment, recommendation, preparation, execution, and verification without turning task subject, model capability, or host standing permission into implicit execution authority.

This research does not alter the canonical Task Request or Dispatch Record, current Mission Control policy, specialist cards, provider routing, qualified-human authority, live-execution scope, or the deferred provider-backed `documentation` replay milestone.

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

The main invariants are implemented and heavily tested. The 2026-08-11 targeted finalization -> authority -> recovery audit proved and remediated two qualified-human temporal-causality gaps: a disposition can no longer predate its approval request, and finalization can no longer predate the current disposition it relies on. The same audit verified that bounded recovery preparation preserves effective risk and human-approval requirements and added regression guards against future recovery-based authority leakage. See [`../history/audits/control-integrity-authority-recovery-audit-2026-08-11.md`](../history/audits/control-integrity-authority-recovery-audit-2026-08-11.md).

The follow-on targeted mutation audit tested ten materially distinct weaknesses across chronology, exact authority binding, expiry equality boundaries, effective-risk preservation, and human-approval preservation. Four mutants initially survived because existing tests did not distinguish exact expiry boundaries or caller-declared risk from dispatch-elevated effective risk. Production behavior was already correct, so remediation added focused evidence rather than changing runtime code. CI #521 killed 10 of 10 targeted mutants after remediation. See [`../history/audits/control-integrity-mutation-audit-finalization-authority-recovery-2026-08-11.md`](../history/audits/control-integrity-mutation-audit-finalization-authority-recovery-2026-08-11.md).

The later Task 002 remediation added normative exact artifact-bound finalization. Artifact-backed PASS now requires verifier-observed canonical local identity, SHA-256, byte length, an explicit authorized artifact root, and finalization-time revalidation. The calibrated external verifier independently falsified the remediation and returned PASS, then carried that PASS forward after a current-main refresh that left the normative implementation byte-identical. See [`../../research/runtime/2026-08-14-external-verifier-assessment-artifact-bound-finalization.md`](../../research/runtime/2026-08-14-external-verifier-assessment-artifact-bound-finalization.md).

The remaining ten percent represents continuing mutation depth, finalization-path resistance, authority-leakage checks, recovery gaps, and new failure modes uncovered by future audits. It is intentionally not scored as permanently complete because control integrity is an ongoing adversarial discipline.

### Verifier calibration evidence, 70%

The fixed corpus, deterministic checks, empirical instrumentation, provider-diverse observations, blinded review tooling, and machine-panel path exist. Additional repeatability, route-specific, adversarial, and accumulated empirical evidence remains useful. Independent human calibration remains optional research and is not a release or routing gate.

Task 002 is now closed as a scoped normative remediation: PR #154 implemented exact artifact-bound finalization, CI #634 validated the refreshed integration, and the calibrated External Independent Technical Verifier returned PASS on the original remediation plus a narrow PASS carrying that verdict to exact refreshed head `8e0d324a82568ab9fb52b097e3559add2111cb34`.

The calibrated External Independent Technical Verifier is paused between material gates rather than used as a routine approval layer. Re-engage that verifier when a consequential boundary needs fresh independent falsification, especially when: Host Integration research is proposed for normative promotion; finalization, authority, or recovery architecture changes materially; the Task Intent & Action Authority Contract reaches implementation; live-execution authority is proposed to widen; Mission Control and another evidence source materially disagree; or a consequential release or architecture claim warrants external challenge. Each future verdict remains untrusted external evidence until reconciled against current repository truth and does not create governance, policy-write, routing, release-approval, live-execution, architecture-change, or qualified-human approval authority.

Benchmark Lab measures multi-verifier disagreement for controlled evaluations, but that diagnostic capability does not by itself complete the broader verifier-calibration evidence program.

### Regulated specialist evidence pilot, 70%

Formal refresh cycle 1 completed on 2026-08-11 across the exact six-card pilot. All seven consequential claims were re-reviewed against their declared tier-1 authorities: six were reaffirmed, one was amended, zero authoritative conflicts were found, and no specialist card changed. The Rule 37(e) claim was corrected to include the condition that the lost information cannot be restored or replaced through additional discovery.

The refresh now has append-only machine-readable history with contiguous cycle sequencing, active-registry blob binding, exact claim coverage, ownership/source consistency, maintenance counters, and mutation checks that reject forged history, missing claims, broken registry-hash continuity, or premature expansion authorization. This preserves proof of repeated maintenance instead of overwriting prior verification dates in the active registry.

Reference Implementation CI run #535 validated the refresh-cycle implementation with 680 passing tests, 487 tracked-file layout checks, regulated specialist evidence structural validation, 41 parsed JSON Schemas, valid linked configuration with zero issues, and the provider-diverse end-to-end example.

The pilot has completed **1 of 2 required formal refresh cycles**. The required 30-day scheduled authority-resolution stability window is not yet satisfied, and no next risk-tier batch has been approved. The controlled-change requirement has been exercised through the Rule 37(e) claim amendment, but registry expansion remains unauthorized. Complete refresh cycle 2 and the 30-day stability gate before any expansion decision.

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

### Qualified-human approval lifecycle, 100%

The current milestone is complete.

The executable lifecycle provides integrity-protected authority-grant, approval-request, disposition, and human-finalization records. Requests can be created only for dispatches already marked `human_approval_required` and exact Route-Outcome Evidence in the `awaiting_human` disposition. Each request binds the exact dispatch digest, task identity, task type, effective risk, authority requirement, verification evidence, and applicable review evidence.

Human decision records require a separately integrity-protected authority grant that covers the required authority class, authority requirement, effective risk, task type, and decision timestamp. The initial `requested` state and the `approved`, `rejected`, `unable_to_determine`, `expired`, and `revoked` lifecycle states are explicitly represented through the request plus append-only dispositions. A disposition cannot become effective before the bound request exists; subsequent dispositions cannot move backwards in time. An approval cannot outlive its request or authority grant.

Model, specialist, verifier, Mission Control, and maintainer actor types cannot impersonate the human actor contract. A maintainer may act only if independently qualified through a scoped human authority grant. Benchmark, shadow, Mission Control, and maintainer review evidence can support an approval request but cannot satisfy qualified-human approval.

Terminal human finalization revalidates the exact dispatch, Route-Outcome Evidence, approval request, linear disposition chain, authority-grant scope, request validity, approval validity, temporal causality, expiry, and revocation state. It cannot predate the request or the current disposition it relies on. It completes only a current valid scoped approval and otherwise blocks with an explicit reason. The original Route-Outcome Evidence remains `awaiting_human` and is not rewritten.

Identity, model selection, provider access, and billing identity remain outside approval qualification and routing. The lifecycle has no policy-write, live-routing, or live-scope-change authority.

Reference Implementation CI run #451 validated the original executable milestone with 626 passing tests, 458 tracked-file layout checks, regulated evidence validation, 38 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example. The later control-integrity hardening described above adds temporal-causality protection without reopening or widening the lifecycle's declared authority milestone.

This milestone implements authority evidence for requirements existing policy already imposes. It does not broaden which tasks require qualified-human approval and does not widen live execution.

### Live execution expansion, 65%

The first bounded expansion candidate is `documentation`, low or medium effective risk only. Candidate selection, a machine-readable staged policy, no-network route preflight, corrected fallback/fresh-verifier topology, direct adapter readiness, and a controlled staged replay harness are validated while active live authority remains unchanged.

The former `runtime-worker-overrides.yaml` behavior unintentionally mutated the shared documentation worker. That global implementation-order override has been removed. Ordinary documentation dispatch now records Claude Sonnet 5 as primary, GPT-5.6 Sol as the provider-diverse non-preview routine fallback, and GPT-5.6 Terra as the primary verifier. Model- or provider-scoped Sonnet recovery redispatch selects GPT-5.6 Sol with Gemini 3.6 Flash as a fresh provider-diverse verifier.

Claude Sonnet 5 execution, GPT-5.6 Sol execution, and GPT-5.6 Terra verification are implemented at the provider-adapter layer. The active provider canary wrappers and live-verification task scope remain limited to `high_volume_simple`, so adapter support does not create documentation live authority.

The staged replay layer now validates the entire replay plan before network access, preserves exact candidate routing and effective risk, reuses the active retry policy, isolates circuit state per trial, executes the staged Sonnet primary through the provider adapter, invokes the exact assigned Terra verifier, holds replay telemetry only in memory, and creates canonical integrity-protected Route-Outcome Evidence plus a staged replay record. Its operator CLI requires explicit live-execution acknowledgement and keeps provider access outside routing semantics.

Automatic fallback is disabled in this replay milestone. Model- or provider-scoped execution failure is recorded rather than automatically redispatched. Deliberate fallback, rollback, and recovery execution remains a distinct later evidence gate.

Reference Implementation CI run #488 validated the durable replay-harness state with 651 passing tests, 472 tracked-file layout checks, regulated evidence validation, 40 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example. The CI provider calls are deterministic fake transports used for conformance. They are not empirical provider-backed replay observations.

Provider-backed controlled documentation replay evidence therefore remains pending. `policy/runtime/live-execution-expansion.yaml` must continue to leave `controlled_replay` unset until a real operator execution produces the exact integrity-protected replay record and canonical Route-Outcome Evidence set. Downstream Shadow Route Evaluation, rollback/recovery evidence, and independent review of any later active-scope policy change also remain required.

No live scope has widened. `documentation` remains `activation_authorized: false`; `high_volume_simple` at low or medium effective risk remains the only accepted guarded live execution class, and high or critical live execution remains unauthorized.

### Distributed runtime hardening, 20%

The reference semantics for recovery, circuit state, telemetry, audit, execution, evaluation, cost evidence, shadow recommendation, qualified-human authority evidence, and route-backed final execution provenance are proven in the current single-process reference architecture. Distributed coordination, persistence, access control, retention, authenticity, replay resistance, and streaming remain later work.

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
- accepted strategic direction;
- current validation scale or another current-state claim used elsewhere in active documentation.

Every update should be grounded in merged repository state, executable validation, accepted research, or explicit maintainer decision. Do not update percentages merely because time passed or a model/provider release occurred.

When parallel sessions are active, reconcile against current `main` before editing this tracker so already-completed work is not reintroduced as pending.

## Related records

- [`roadmap.md`](roadmap.md): canonical stewardship roadmap
- [`research/roadmaps/intelligence-control-plane.md`](../../research/roadmaps/intelligence-control-plane.md): longer-horizon intelligence-control-plane research
- [`../../research/roadmaps/host-integration-contract.md`](../../research/roadmaps/host-integration-contract.md): non-normative Host Integration Contract research roadmap
- [`../../research/roadmaps/execution-environment-recovery-contract.md`](../../research/roadmaps/execution-environment-recovery-contract.md): non-normative isolated-execution, checkpoint, rollback, and recovery-verification research roadmap
- [`../../research/roadmaps/task-intent-action-authority-contract.md`](../../research/roadmaps/task-intent-action-authority-contract.md): non-normative request-intent, assessment-versus-action, delegation, and state-change authority research roadmap
- [`../../research/runtime/2026-08-13-external-verifier-calibration.md`](../../research/runtime/2026-08-13-external-verifier-calibration.md): paired positive/negative-control calibration and evidence-only verifier classification
- [`../../research/runtime/2026-08-13-external-verifier-assessment-final-execution-provenance.md`](../../research/runtime/2026-08-13-external-verifier-assessment-final-execution-provenance.md): first post-calibration substantive external-verifier assessment
- [`../../research/runtime/2026-08-14-external-verifier-assessment-artifact-bound-finalization.md`](../../research/runtime/2026-08-14-external-verifier-assessment-artifact-bound-finalization.md): Task 002 normative artifact-bound finalization PASS, residual limits, exact-head refresh reconciliation, and merged disposition
- [`../../research/runtime/2026-08-12-host-integration-validation-round-1.md`](../../research/runtime/2026-08-12-host-integration-validation-round-1.md): first implementation-backed external-host validation round
- [`../../research/runtime/2026-08-12-host-integration-validation-round-2.md`](../../research/runtime/2026-08-12-host-integration-validation-round-2.md): second structurally different host validation and architecture-diversity gate decision
- [`../../research/runtime/host-integration-context-economics-2026-08-12.md`](../../research/runtime/host-integration-context-economics-2026-08-12.md): static bounded-context specialist-payload measurement and remaining empirical context-economics gate
- [`../../research/runtime/host-integration-dispatch-adapter-mutation-2026-08-12.md`](../../research/runtime/host-integration-dispatch-adapter-mutation-2026-08-12.md): dispatch-provenance and bundled-adapter payload self-expansion adversarial evidence
- [`../../research/runtime/host-integration-third-party-adapter-trust-2026-08-12.md`](../../research/runtime/host-integration-third-party-adapter-trust-2026-08-12.md): process-local third-party adapter registration, provenance-binding, and non-self-authorization adversarial evidence
- [`../../research/runtime/host-integration-authority-intersection-2026-08-12.md`](../../research/runtime/host-integration-authority-intersection-2026-08-12.md): restrictive host/TEO authority intersection and exact host execution-scope binding adversarial evidence
- [`../../research/runtime/host-integration-execution-envelope-integrity-2026-08-12.md`](../../research/runtime/host-integration-execution-envelope-integrity-2026-08-12.md): exact process-local action target, parameter, side-effect, prerequisite, and retry-envelope adversarial evidence
- [`../../research/runtime/host-integration-verifier-artifact-binding-2026-08-12.md`](../../research/runtime/host-integration-verifier-artifact-binding-2026-08-12.md): verifier-context independence, exact artifact/change-set binding, and stale-PASS resistance adversarial evidence
- [`../../research/runtime/host-integration-cross-process-authority-2026-08-13.md`](../../research/runtime/host-integration-cross-process-authority-2026-08-13.md): brokered conformant process-lifetime cross-process authority/replay evidence and remaining production/distributed boundary
- [`../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md): runtime-derived static authority-surface reconciliation, red-canary correction, CI #644 evidence, and remaining dynamic executable-hook boundary
- [`../../research/runtime/host-integration-recursion-resistance-2026-08-14.md`](../../research/runtime/host-integration-recursion-resistance-2026-08-14.md): process-lifetime recursion admission, security-review hardening, CI #658 evidence, and remaining restart/distributed/scheduler boundary
- [`../../research/runtime/2026-08-10-live-execution-expansion-candidate-selection.md`](../../research/runtime/2026-08-10-live-execution-expansion-candidate-selection.md): staged `documentation` live-scope candidate research and blockers
- [`../../research/runtime/2026-08-11-documentation-live-topology-adapter-readiness.md`](../../research/runtime/2026-08-11-documentation-live-topology-adapter-readiness.md): repaired documentation fallback, fresh-verifier, and staged adapter-readiness evidence
- [`../../research/runtime/2026-08-11-documentation-controlled-replay.md`](../../research/runtime/2026-08-11-documentation-controlled-replay.md): staged replay harness, evidence boundary, and pending provider-backed replay gate
- [`../../policy/runtime/live-execution-expansion.yaml`](../../policy/runtime/live-execution-expansion.yaml): machine-readable staged live-scope candidate gate
- [`docs/releases/v1.0.0.md`](../releases/v1.0.0.md): immutable functional-v1 release contract
- [`docs/releases/v1-readiness.md`](../releases/v1-readiness.md): current release/readiness boundary
- [`docs/history/audits/post-v1-hard-audit-2026-08-10.md`](../history/audits/post-v1-hard-audit-2026-08-10.md): durable post-v1 hard audit
