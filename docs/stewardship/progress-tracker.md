# TEO Progress Tracker

**Status:** active stewardship record  
**Last reconciled:** 2026-08-30  
**Stable release:** `v1.0.0`  
**Current development line:** `teo-reference-router==1.0.1.dev0`

This is the canonical operational progress tracker for The Ever-Evolving Orchestration (TEO). It records current repository truth, active workstreams, accepted evidence, and the next material gates. Historical implementation detail remains available in Git history and dedicated research/evidence records; this tracker should not preserve stale state as if it were current.

Normative runtime, routing, release, authority, and governance behavior remains defined by the applicable executable policy, schema, registry, runtime, and release artifacts.

## Current system snapshot

| Surface | Current state |
|---|---|
| Stable release | `v1.0.0` in `reference_operational` state |
| Development package | `1.0.1.dev0` |
| Current executable code baseline | `93a5bb98fcef116000af90fa417098553ef4160d` after clean-architecture Tranche 5C / PR #221; stewardship-only reconciliation does not change executable behavior |
| Organizational teams | 10 |
| Workers | 84 |
| Active specialists | 82 |
| Mission Control workers | 4 |
| Current validated scale | **1,141 tests passed**, **617 tracked-file layout checks**, **42 schemas**, valid linked configuration with zero issues, regulated-specialist evidence pass, provider-diverse end-to-end pass; established by Reference Implementation CI #987 on merged `main@93a5bb98fcef116000af90fa417098553ef4160d` |
| Runtime model binding | Complete through RMI-8; PR #209 merged as `8e5bef0f209f6fe14b46311c7345cea141eb0a4b` and Issue #200 is closed completed |
| Responsibility architecture | model/provider neutral; concrete implementation identity is not owned by Teams, Workers, Specialists, task routes, risk, or authority |
| Runtime compatibility defaults | explicit compatibility/default evidence in `policy/routing/core/runtime-compatibility-defaults.yaml`; not proof of live availability or fitness |
| Specialist selection policy | model-neutral `policy/routing/core/specialist-selection-policy.yaml` |
| Clean architecture | Tranches 1–4 plus Tranche 5A, Tranche 5B, and Tranche 5C merged and qualified; T5D immutable runtime configuration view is the next actionable repository gate |
| Guarded live execution | bounded `high_volume_simple` canary at low or medium effective risk |
| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |
| High and critical live execution | not authorized |
| Regulated evidence pilot | 6 specialists, stability-qualified and intentionally bounded |
| Repository information architecture | R1 through R5 complete |

## Runtime model binding — completed executable truth

TEO routes capabilities and responsibility, not model brands.

Canonical lifecycle:

```text
Task
  -> Mission Control / responsibility
  -> Team / Worker / optional Specialist
  -> capability requirements
  -> runtime inventory
  -> eligibility
  -> calibration
  -> best-fit selection / scoped pin
  -> execution
  -> observed runtime identity
  -> verification
  -> evidence-bearing outcome
```

The strict candidate lifecycle is:

**Discovered -> Eligible -> Calibrated -> Selected**

Key invariants now executable:

- discovery, availability, eligibility, calibration, fitness, and pins never widen authority;
- responsibility configuration is model/provider neutral;
- named implementations are isolated to compatibility/default/evidence, experiments, explicit scoped pins, reproduction, or incident-mitigation surfaces;
- local and remote candidates are peers unless explicit policy says otherwise;
- calibration binds the exact execution configuration rather than a marketing name;
- primary, fallback, verifier, and specialist implementation choice flows through `RuntimeSelectionPort`;
- reasoning controls are bound before calibration/selection;
- fallback and verifier selection remain inside the authorized eligible set and preserve applicable provider-diversity policy;
- connection/authentication mechanics remain separate from runtime fitness and selection;
- executor and checker observed runtime identity is carried independently from intended identity;
- intended-versus-observed mismatch or unconfirmed identity cannot be silently promoted to verified completion;
- exact execution-configuration identity is not fabricated when only provider/model identity is observed.

The default configured compatibility bridge represents configured implementations honestly as `user_declared` compatibility inputs. It does not claim that those implementations are currently running, reachable, healthy, or empirically calibrated. Installations may inject actual runtime inventory, eligibility evidence, calibration history, and fitness evidence through the provider-independent runtime-binding ports.

### RMI sequence

- [x] RMI-1 — provider-independent runtime-binding contracts and inventory port; PR #201.
- [x] RMI-2 — runtime inventory composition and installation adapter; PR #202.
- [x] RMI-3 — provider-independent eligibility evidence and fail-closed evaluation; PR #203.
- [x] RMI-4 — exact execution-configuration calibration history and freshness; PR #204.
- [x] RMI-5 — policy-constrained runtime best-fit selection and dispatch cutover; PRs #205 and #206.
- [x] RMI-6 — observed executor/checker identity through execution, telemetry, Route-Outcome, finalization, and provenance; PR #207.
- [x] RMI-7 — remove model identity from workers/responsibility routes and isolate named implementations to explicit compatibility/default surfaces; PR #208, merged as `3d121fde56f840bbfaa6bcb240c262f045525786`.
- [x] RMI-8 — reconcile canonical documentation, AI operating instructions, roadmap, Progress Tracker, and documentation-truth tests; PR #209 merged as `8e5bef0f209f6fe14b46311c7345cea141eb0a4b`.

RMI-8 final qualification on exact PR head `d5ab4791e7b037bade24e2780a9aaef7df42878f` was Reference Implementation CI #958: **1,115 tests passed**, **602 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing.

## Clean-architecture migration — current executable truth

Issue #197 remains behavior-preserving and separate from Runtime Model Binding.

- [x] Tranche 1 — deterministic classification/risk domain policy; PR #196, `a63887179a1ff3adfa7d7119a7db1a5f598a0f86`.
- [x] Tranche 2 — finalization use case and artifact-integrity port; PR #198, `467c706d6f1077371928e3fcbe3f32f5ec51fb19`.
- [x] Tranche 3 — dispatch application service and responsibility resolvers/selectors; PR #210, `74c128947f1d98f0e42c595bd1229561ab6dab50`.
- [x] Tranche 4 — replace specialist-routing inheritance coupling with composition; PR #212, `2f4df9d1124be91473e346ddb926f5d93c93de3e`.
- [ ] Tranche 5 — separate configuration loading/composition/validation/runtime view.
  - [x] T5A — repository configuration source I/O port/adapter; PR #214, `1ba1a4b0a83e403b422b47f2e7b7cef733ccb201`.
  - [x] T5B — configuration composition and explicit manifest; PR #219, `6528be6e54b5acc8c37ef8ab1f5198ab1e61d20f`.
  - [x] T5C — invariant validation boundary; PR #221, `93a5bb98fcef116000af90fa417098553ef4160d`.
  - [ ] T5D — immutable runtime configuration view behind the mutable `ConfigBundle` compatibility façade.
- [ ] Tranche 6 — move provider/verifier/runtime/evaluation implementations behind explicit outer namespaces with compatibility shims.
- [ ] Tranche 7 — reduce compatibility surface only through explicit API evidence/versioning.

Tranche 3 exact-head qualification was Reference Implementation CI #960 on `504c05f67ee6d89e0144e6d16c11c3a19509e780`: **1,118 tests**, **607 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing. `OrchestrationEngine.dispatch()` became a thin application-service façade with Worker, Specialist, and capability resolution extracted.

Tranche 4 exact-head qualification was Reference Implementation CI #968 on `176217f9803c2ec274d2b225c52cf1f4d5c0f27f`: **1,120 tests**, **610 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing. `SpecialistRoutingEngine` remains the public compatibility façade but no longer subclasses `OrchestrationEngine`; specialist risk/preference refinement is composed through a pure application policy, and specialist-selection YAML/filesystem loading is behind a narrow port/adapter.

Tranche 5A isolated repository configuration YAML/filesystem I/O behind `RepositoryConfigurationSourcePort` and `YamlRepositoryConfigurationAdapter` without changing composition, validation, routing, authority, Runtime Model Binding, provider/default policy, or live scope. PR #214 exact head `17afc5d5ff3b74897e6c2bcd534ccb6158fbc2cb` passed Reference Implementation CI #977 with **1,127 tests**, **612 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration valid with zero issues, and provider-diverse end-to-end routing. The merged executable baseline `1ba1a4b0a83e403b422b47f2e7b7cef733ccb201` then passed Reference Implementation CI #978 with the same **1,127 tests**, **612 tracked files**, **42 schemas**, valid linked configuration, regulated-specialist evidence, and provider-diverse end-to-end behavior.

Tranche 5B moved the explicit repository configuration manifest, extension ordering, Team-route/routing/Worker/Specialist merge and override rules, and existing routing normalization into `application/configuration/composition.py`. `ConfigBundle.load()` now delegates composition through that application boundary while retaining compatibility/error-translation shims. PR #219 exact head `d52a834509dd04f141550806871a203b0d850560` passed Reference Implementation CI #982 with **1,135 tests**, **615 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration valid with zero issues, and provider-diverse end-to-end routing. The merged executable baseline `6528be6e54b5acc8c37ef8ab1f5198ab1e61d20f` then passed Reference Implementation CI #983 with the same **1,135 tests**, **615 tracked files**, **42 schemas**, valid linked configuration, regulated-specialist evidence, and provider-diverse end-to-end behavior.

Tranche 5C moved invariant-validation ownership and deterministic issue construction into `application/configuration/validation.py`. `ConfigBundle.validate()` remains a thin compatibility façade, `RepositoryConfigurationValidationInput` is a frozen shell over the existing mutable mappings, and post-load mutation/conformance behavior remains observable. PR #221 exact head `e2f602175ace0b0a3466142f331154f4840842f2` passed Reference Implementation CI #986 with **1,141 tests**, **617 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration valid with zero issues, and provider-diverse end-to-end routing. The merged executable baseline `93a5bb98fcef116000af90fa417098553ef4160d` then passed Reference Implementation CI #987 with the same **1,141 tests**, **617 tracked files**, **42 schemas**, valid linked configuration, regulated-specialist evidence, and provider-diverse end-to-end behavior.

Full Tranche 5 remains incomplete. T5D is the next bounded clean-architecture gate: introduce an immutable runtime-facing configuration view behind the existing mutable `ConfigBundle` compatibility façade while keeping intentional mutable validation/conformance callers compatible. T5D must not change routing, authority, Runtime Model Binding, provider/default policy, risk, live scope, finalization, verification, or Issue #215 Stage B.

## Portfolio view

| Workstream | Status | Progress | Current milestone | Next gate |
|---|---|---:|---|---|
| Core architecture and governance | Complete | 100% | Functional v1 reference contract | Maintain protected invariants through compatible evolution |
| Runtime model binding | Complete | 100% | RMI-1 through RMI-8 merged and reconciled | Preserve runtime-binding invariants through future compatible evolution |
| Repository information architecture | Complete | 100% | R1 through R5 | Preserve governed placement and lifecycle boundaries |
| Team, worker, and specialist architecture | Operational | 100% | 10 teams, 84 workers, 82 active specialists | Add roles only after proven responsibility-gap and authority review |
| Control integrity | Operational | 90% | Post-v1 conformance, mutation resistance, artifact-bound finalization, observed-identity integrity | Continue closing newly discovered finalization, authority, and recovery mutation gaps |
| Verifier calibration evidence | In progress | 70% | Deterministic and empirical verifier evidence | Strengthen repeatability, disagreement, adversarial, and route-specific evidence |
| Regulated specialist evidence pilot | Complete | 100% | Six-card pilot stability-qualified | Maintain seven-day drift monitoring; expansion requires explicit next risk-tier batch approval |
| Route-outcome evidence | Complete | 100% | Canonical executable route-outcome evidence contract | Preserve schema/version compatibility and controlled downstream use |
| Benchmark and Outcome Lab | Complete | 100% | Controlled evaluation and conclusion handoff | Preserve compatibility and evidence boundaries |
| Source-backed cost attribution | Complete | 100% | Effective-dated reproducible route-level attribution | Maintain authoritative price evidence |
| Shadow route evaluation | Complete | 100% | Governed recommendation-only evidence loop | Preserve anti-Goodhart and no-policy-write boundaries |
| Qualified-human approval lifecycle | Complete | 100% | Evidence-bound qualified-human authority lifecycle | Preserve scope, integrity, expiry, revocation, temporal causality, and finalization boundaries |
| Live execution expansion | In progress | 65% | `documentation` staged replay harness and operator evidence path validated | Produce provider-backed controlled documentation replay evidence |
| Clean-architecture migration (#197) | In progress | — | Tranches 1–4 plus T5A, T5B, and T5C merged and qualified | T5D: immutable runtime configuration view |
| Distributed runtime hardening | Future | 20% | Single-process reference behavior proven | Add coordinated state, concurrency-safe export, access control, retention, integrity, and recovery |
| Licensing and contribution terms | Pending | 10% | Public repository with no reuse license selected | Select licensing and contribution terms before representing TEO as open source |

## NOW

### 1. Clean-architecture Tranche 5D — immutable runtime configuration view

T5A isolated configuration source I/O, T5B isolated explicit composition and normalization, and T5C isolated invariant validation while preserving the mutable `ConfigBundle` compatibility façade. T5D is now the next bounded repository gate: introduce an immutable runtime-facing configuration view behind that façade so runtime consumers do not depend on accidental mutability, while preserving intentional mutable validation/conformance callers.

T5D must preserve the existing source, composition, and validation boundaries and their exact semantics. It must not change routing, risk, authority, Runtime Model Binding, model/provider defaults, provider access, live scope, finalization, verification, or Issue #215 Stage B. Compatibility reduction remains a later explicit API decision rather than an automatic side effect of immutability.

### 2. Evidence-governed live execution expansion

The product evidence gate remains provider-backed controlled `documentation` replay through the existing bounded operator path. It remains deferred until provider access is supplied for that evidence run.

`documentation` is **staged only** and has **no live-execution authority**. The active guarded runtime remains limited to `high_volume_simple` at low or medium effective risk. CI uses deterministic fake provider transports and therefore does not constitute empirical provider-backed replay evidence.

No access mechanism is itself routing authority. Do not authorize high or critical live execution from the architectural migration. **High and critical live execution remains unauthorized.**

## NEXT

After full Tranche 5, continue #197 only after exact repository recalibration. Tranche 6 is the planned provider/verifier/runtime/evaluation namespace migration, but it is not automatically authorized if Tranche 5 evidence reveals a different required sequence.

T5D must itself be implemented, exact-head qualified, merged-main qualified, and reconciled before Tranche 5 is complete.

The product-priority gate remains provider-backed controlled `documentation` replay evidence unless repository truth or an explicit owner decision changes sequencing.

## LATER

### Host Integration Contract research

The Host Integration Contract remains non-normative research. The two-host architecture-diversity gate is satisfied, together with provider-independent work on bounded-context projection, dispatch provenance, adapter non-self-authorization, restrictive host/TEO authority intersection, exact execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, brokered cross-process authority/replay, runtime-wired authority-surface reconciliation, process-lifetime recursion resistance, exact local freshness binding, portfolio/task-admission separation, and integrated Fresh-AI assimilation/conformance.

Empirical Fresh-AI trial 001 supports fresh-session/no-reminder **routing continuity**, but not full end-to-end selected-executor/verifier assimilation. Research simulation may report only `routing_continuity_only` unless authenticated selected-versus-observed executor and verifier identity plus digest/artifact binding are proved.

Remaining production/distributed questions include durable hooks, dynamic executable-hook discovery, external-adapter package provenance, transitive code identity, distributed authority synchronization, remote freshness authenticity, downgrade/expiry, scheduler containment, tenant/account/credential binding, remote transport authenticity, and distributed recovery/recursion state.

### Execution Environment & Recovery Contract

Accepted non-normative future research. It must preserve TEO's orchestration-only scope while studying isolation requirements, checkpoint binding, rollback authority, recovery verification, and simulation-to-promotion boundaries.

### Task Intent & Action Authority Contract

Accepted non-normative future research. It studies an explicit originating-request authority ceiling across assessment, recommendation, preparation, execution, verification, fallback, recovery, and host-native action without creating a second routing or permissions plane.

### Distributed runtime hardening

Future productionization may require coordinated circuit state, concurrency-safe telemetry export, durable storage, access control, retention, integrity, and recovery. These remain implementation concerns beneath TEO's orchestration contract rather than reasons to turn TEO into a generic infrastructure platform.

## Continuous drift rules

- Repository truth beats remembered counts, route names, model versions, issue status, and earlier-session assumptions.
- Time-sensitive model/provider claims require current authoritative provider evidence.
- Historical CI runs remain historical evidence; only the latest explicitly accepted current baseline should be labeled current.
- Research results must remain labeled research until separately promoted through reviewed executable policy/schema/runtime changes.
- Discovery, inventory, compatibility data, access mechanism, calibration history, and telemetry never create authority by themselves.
- Material work is complete only after implementation/evidence, verification, and canonical documentation are aligned.
