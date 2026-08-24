# Roadmap

TEO has completed the foundation, team architecture, routing validation, registry population, reference control plane, operational evidence chain, and the executable runtime-model-binding migration through RMI-7.

The roadmap is directional. Current operational state, exact evidence, completion percentages, and NOW/NEXT/LATER sequencing belong in [`progress-tracker.md`](progress-tracker.md).

## True north

TEO evolves strictly as an orchestrator. Its job is to improve how it:

- interprets work;
- resolves Mission Control, Team, Worker, Specialist, and capability responsibility;
- assesses risk and authority boundaries;
- discovers and evaluates execution resources;
- binds capability requirements to concrete runtime implementations;
- selects primary, fallback, verifier, and specialist implementations;
- preserves evidence, observed identity, and auditability;
- learns from measured outcomes without silently self-authorizing policy changes.

TEO does not become a provider, IDE, workspace, generic agent platform, credential broker, container runtime, deployment system, or universal workflow engine merely to improve orchestration.

## Completed foundation

- public project identity, Constitution, Lexicon, and stewardship rules;
- ten accountable teams;
- 84 workers and 82 active specialist role cards;
- provider/model/capability registries as evidence/catalog surfaces rather than routing authority;
- deterministic Team/Worker/Specialist/capability resolution;
- non-lowerable effective-risk controls;
- fallback, escalation, verification, and qualified-human authority controls;
- runnable Python reference control plane;
- guarded live provider execution for bounded `high_volume_simple` work;
- bounded retry, canonical redispatch, provider-family circuit state, and content-free runtime telemetry;
- provider-diverse independent verification;
- route-outcome evidence, Benchmark and Outcome Lab, source-backed cost attribution, Shadow Route Evaluation, and qualified-human approval lifecycle;
- six-card regulated evidence/freshness pilot with executable stability qualification;
- R1 through R5 repository information architecture;
- observed executor/checker identity carried independently from intended identity through telemetry, Route-Outcome, finalization, and provenance.

## Completed runtime-model-binding architecture

The governing invariant is:

> **TEO routes capabilities and responsibility, not model brands.**

The executable control path is now:

```text
Task
  -> responsibility
  -> capability requirements
  -> runtime inventory
  -> eligibility
  -> calibration
  -> best-fit selection / scoped pin
  -> execution
  -> observed identity
  -> independent verification
  -> evidence-bearing outcome
```

The strict lifecycle is **Discovered -> Eligible -> Calibrated -> Selected**.

RMI-1 through RMI-7 are merged:

- provider-independent runtime inventory and five inventory classes;
- deterministic multi-source inventory composition with fail-closed conflict handling;
- provider-independent eligibility evidence;
- exact execution-configuration calibration history and freshness enforcement;
- best-fit runtime selection after authority, deny-wins exclusions, eligibility, and calibration;
- explicit scoped runtime pins with expiry/removal conditions that cannot widen authority;
- production primary/fallback/verifier/specialist dispatch through `RuntimeSelectionPort`;
- reasoning controls bound before calibration/selection;
- observed executor/checker identity and intended-versus-observed mismatch handling;
- model/provider-neutral worker, specialist-responsibility, and task-route configuration;
- named implementations isolated to explicit compatibility/default/evidence, experiment, pin, reproduction, or incident-mitigation surfaces.

`policy/routing/core/runtime-compatibility-defaults.yaml` is therefore a compatibility/default evidence surface, not responsibility authority and not proof that a candidate is live, healthy, reachable, or empirically calibrated. `policy/routing/core/specialist-selection-policy.yaml` is the current model-neutral specialist selection policy. The retired `specialist-model-routing.yaml` is not a current authority surface.

Connection mechanism remains separate from runtime fitness and routing. API keys, OAuth, subscription-backed sessions, delegated identity, service accounts, connector sessions, SDK-managed identity, credential brokers, local runtimes, or future provider-supported access methods do not become intrinsic model-selection signals.

## Current: RMI-8 truth reconciliation

RMI-8 reconciles canonical policy descriptions, README guidance, AI operating instructions, the Progress Tracker, roadmap, and documentation-truth tests against the completed executable runtime-binding architecture.

RMI-8 must remain documentation/governance truth work only. It must not:

- widen live execution;
- refresh concrete model versions merely because documentation is changing;
- change provider authentication or access semantics;
- alter product verification or qualified-human authority policy;
- create runtime discovery claims unsupported by the reference implementation;
- fold behavior-changing runtime work into the separate clean-architecture migration in #197.

The accepted current executable baseline before RMI-8 documentation changes is `main@3d121fde56f840bbfaa6bcb240c262f045525786`, qualified by RMI-7 Reference Implementation CI #951 with 1,113 tests, 602 tracked-file layout checks, 42 schemas, valid linked configuration with zero issues, regulated-specialist evidence, and provider-diverse end-to-end routing.

## Current operational priority: evidence-governed live execution expansion

The runtime-binding migration does not widen live authority.

The existing low or medium risk `high_volume_simple` canary remains the only accepted guarded live execution scope. `documentation` remains the first staged candidate and is evaluation only.

Its staged replay harness and operator path are implemented, but provider-backed empirical replay evidence is still pending. CI conformance with deterministic fake transports is not provider-backed evidence.

The next product evidence gate remains:

1. provider-backed controlled `documentation` replay through the bounded operator path;
2. integrity-protected replay and canonical Route-Outcome Evidence;
3. applicable shadow evaluation, recovery/rollback evidence, and independent review;
4. only then a separately reviewed active-scope decision.

High and critical live execution remains outside the current guarded runtime.

## Control integrity

Continue adversarially testing the control plane rather than assuming architectural intent proves implementation behavior.

Priorities include:

- non-lowerable effective risk;
- authority intersection and deny-wins behavior;
- exact expiry and temporal causality;
- fallback/recovery risk preservation;
- exact artifact-bound finalization;
- observed runtime identity integrity;
- verifier independence;
- runtime-binding lifecycle bypass resistance;
- stale calibration and stale evidence rejection;
- mutation tests for newly discovered failure modes.

Control integrity remains intentionally an ongoing discipline rather than a one-time completion claim.

## Verifier calibration evidence

Continue deterministic and empirical calibration of the guarded verifier rubric.

Measure:

- false-pass rate;
- false-fail rate;
- `needs_human` rate;
- criterion-level confusion;
- repeatability;
- provider/model disagreement;
- adversarial candidate-output resistance;
- latency and normalized usage;
- retry/fallback relationship to outcomes.

Independent human calibration under Issue #75 remains optional evidence enhancement rather than an engineering-progress gate. It becomes mandatory only before making a claim specifically framed as independently human-validated evidence.

## Regulated specialist evidence

The bounded six-card regulated specialist evidence pilot has completed its current executable stability milestone.

Maintain the seven-day authority-resolution cadence as continuous drift detection. Do not auto-authorize a larger regulated registry. Any next risk-tier batch requires explicit approval and a separate bounded reviewed change.

## Clean-architecture migration (#197)

The Python clean-architecture migration remains a separate behavior-preserving workstream.

Rules:

- recalibrate #197 against current `main` before each tranche;
- preserve dependency direction and existing behavior;
- do not fold runtime-model-binding product behavior into #197;
- where both workstreams touch a surface, sequence changes so each remains independently understandable and reversible.

## Host Integration Contract research

External-host integration remains non-normative research.

Current satisfied provider-independent research slices include:

- two-host architecture diversity;
- bounded specialist/context projection;
- dispatch provenance;
- bundled-adapter self-expansion resistance;
- process-local third-party adapter non-self-authorization;
- restrictive host/TEO authority intersection and host execution-scope binding;
- exact execution-envelope integrity;
- verifier-context independence;
- exact artifact/change-set stale-PASS resistance;
- brokered process-lifetime cross-process authority/replay resistance;
- runtime-wired authority-surface reconciliation;
- process-lifetime recursion resistance;
- exact local freshness binding;
- portfolio/task-admission authority separation;
- integrated Fresh-AI assimilation/conformance and premortem replay.

The assimilation rule remains **Assimilation is not installation**. A host must not treat TEO as a bypassable prompt persona, plugin, SDK, specialist pack, or optional sidecar for work it has admitted into the TEO-governed boundary.

Empirical Fresh-AI trial 001 supports fresh-session/no-reminder routing continuity, but it does not prove full end-to-end selected-executor/verifier assimilation. Research simulation may support `routing_continuity_only`; authenticated observed executor/verifier identity plus artifact/digest binding remains required for a stronger claim.

Remaining pre-normative evidence includes durable hooks, dynamic executable-hook discovery, external-adapter package provenance and transitive code identity, distributed host/TEO authority synchronization, remote freshness authenticity, downgrade/expiry semantics, scheduler containment, tenant/account/credential binding, remote transport authenticity/replay resistance, production resource containment, and distributed recovery/recursion state.

## Execution Environment & Recovery Contract research

Accepted non-normative future research.

The contract should study isolation, pre-change checkpointing, rollback authority, recovery verification, and simulation-to-promotion boundaries without turning TEO into an infrastructure runtime. Any later normative promotion must remain compatible with request authority, Host Integration authority intersection, exact execution-envelope binding, independent verification, and current live-scope controls.

## Task Intent & Action Authority Contract research

Accepted non-normative future research.

The goal is to make the authority granted by the originating request explicit before routing, delegation, host-native action, recovery, or state-changing execution. A request-authority record should be an authority ceiling that later TEO controls may narrow but never silently widen.

This research must not create a second routing or permissions plane.

## Distributed runtime hardening

Future production deployment may require:

- coordinated distributed circuit state;
- concurrency-safe telemetry export;
- durable access control and retention;
- integrity and recovery guarantees;
- distributed workflow/audit correlation;
- remote authenticity and freshness coordination.

These are implementation concerns beneath the orchestration contract, not justification for expanding TEO into a generic infrastructure platform.

## Community and licensing

Select licensing and contribution terms before representing TEO as open source or inviting reuse under rights that have not been granted.

## Roadmap decision rule

Before promoting new work:

1. verify it does not already exist, remain open, or have a previously rejected path;
2. recalibrate current repository truth;
3. state the protected invariant;
4. gather current authoritative evidence where freshness matters;
5. prefer the smallest reversible change;
6. independently verify consequential changes;
7. update canonical progress/governance records only after executable truth exists.
