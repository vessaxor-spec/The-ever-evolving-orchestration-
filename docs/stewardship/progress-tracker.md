# TEO Progress Tracker

**Status:** active stewardship record  
**Last reconciled:** 2026-08-24  
**Stable release:** `v1.0.0`  
**Current development line:** `teo-reference-router==1.0.1.dev0`

This is the canonical operational progress tracker for The Ever-Evolving Orchestration (TEO). It records current repository truth, active workstreams, accepted evidence, and the next material gates. Historical implementation detail remains available in Git history and dedicated research/evidence records; this tracker should not preserve stale state as if it were current.

Normative runtime, routing, release, authority, and governance behavior remains defined by the applicable executable policy, schema, registry, runtime, and release artifacts.

## Current system snapshot

| Surface | Current state |
|---|---|
| Stable release | `v1.0.0` in `reference_operational` state |
| Development package | `1.0.1.dev0` |
| Current executable main | `3d121fde56f840bbfaa6bcb240c262f045525786` after RMI-7 / PR #208 |
| Organizational teams | 10 |
| Workers | 84 |
| Active specialists | 82 |
| Mission Control workers | 4 |
| Current validated scale | 1,113 tests passed, 602 tracked-file layout checks, 42 schemas, valid linked configuration with zero issues, regulated-specialist evidence pass, provider-diverse end-to-end pass; established by Reference Implementation CI #951 |
| Runtime model binding | RMI-1 through RMI-7 executable and merged; RMI-8 documentation/progress reconciliation in progress |
| Responsibility architecture | model/provider neutral; concrete implementation identity is not owned by Teams, Workers, Specialists, task routes, risk, or authority |
| Runtime compatibility defaults | explicit compatibility/default evidence in `policy/routing/core/runtime-compatibility-defaults.yaml`; not proof of live availability or fitness |
| Specialist selection policy | model-neutral `policy/routing/core/specialist-selection-policy.yaml` |
| Guarded live execution | bounded `high_volume_simple` canary at low or medium effective risk |
| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |
| High and critical live execution | not authorized |
| Regulated evidence pilot | 6 specialists, stability-qualified and intentionally bounded |
| Repository information architecture | R1 through R5 complete |

## Runtime model binding — current executable truth

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

Key invariants now executable on `main`:

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
- [ ] RMI-8 — reconcile canonical documentation, policy descriptions, and the Progress Tracker against completed executable truth; current workstream.

RMI-7 qualification on exact PR head `2b3b5273c1b606ad8a862897a976ccd15a8aa247` was Reference Implementation CI #951 / run `32775297777`: **1,113 tests passed**, **602 tracked files**, **42 schemas**, regulated-specialist evidence pass, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing.

## Portfolio view

| Workstream | Status | Progress | Current milestone | Next gate |
|---|---|---:|---|---|
| Core architecture and governance | Complete | 100% | Functional v1 reference contract | Maintain protected invariants through compatible evolution |
| Runtime model binding | In progress | 95% | RMI-1 through RMI-7 executable and qualified | Complete RMI-8 canonical documentation/progress reconciliation |
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
| Clean-architecture migration (#197) | In progress | — | behavior-preserving migration remains separate from runtime-model binding | Continue only from current #197 repository truth; do not fold RMI behavior changes into it |
| Distributed runtime hardening | Future | 20% | Single-process reference behavior proven | Add coordinated state, concurrency-safe export, access control, retention, integrity, and recovery |
| Licensing and contribution terms | Pending | 10% | Public repository with no reuse license selected | Select licensing and contribution terms before representing TEO as open source |

## NOW

### 1. RMI-8 — canonical truth reconciliation

Reconcile the current authority-facing documentation against the executable runtime-model-binding architecture. This is documentation and governance truth alignment only. It must not widen live scope, change provider access, refresh model versions, alter product verification policy, or absorb the behavior-preserving #197 workstream.

Completion gate:

- Progress Tracker, roadmap, README, AI instructions, and documentation-truth tests agree with executable `main`;
- retired `specialist-model-routing.yaml` is not described as current authority;
- workers and responsibility routes are not described as owning concrete models;
- runtime compatibility/default surfaces are described as compatibility/evidence rather than discovery or fitness authority;
- current CI evidence is exact and dated;
- canonical CI passes on the exact RMI-8 head;
- independent scope audit confirms documentation/truth-test scope only.

### 2. Evidence-governed live execution expansion

The operational product milestone remains unchanged by RMI-8.

`documentation` is the first bounded staged candidate. It remains **staged only** and has **no live-execution authority**. The active guarded runtime remains limited to `high_volume_simple` at low or medium effective risk.

The staged documentation replay harness and operator path are validated. CI uses deterministic fake provider transports and therefore does not constitute empirical provider-backed replay evidence. The next material gate is a real provider-backed controlled `documentation` replay using the existing operator path, followed by the applicable shadow, recovery, and independent-review evidence before any active-scope mutation.

Provider-backed `documentation` replay is intentionally deferred as an open action item until provider access is supplied for the bounded evidence run. No access mechanism is itself routing authority.

Do not authorize high or critical live execution from the runtime-model-binding work. **High and critical live execution remains unauthorized.**

## NEXT

After RMI-8 closes, no additional workstream is automatically promoted by documentation completion. The product-priority gate remains provider-backed controlled `documentation` replay evidence unless repository truth or an explicit owner decision changes sequencing.

The #197 clean-architecture migration remains separately sequenced and behavior-preserving.

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
