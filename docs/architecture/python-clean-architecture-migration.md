# Python Reference Clean-Architecture Migration

Status: **incremental implementation — Tranches 1–4 plus Tranche 5A merged**  
Scope: `reference/implementations/python/src/teo_reference/`  
Behavioral rule: **no routing, risk, verification, authority, evidence, provider, or public-API behavior may change as a side effect of this migration.**

## Decision

The Python reference implementation will move toward explicit clean-architecture boundaries through small, compatibility-preserving tranches rather than a repository-wide file move.

TEO is already a mature control plane with strong conformance, mutation, authority, evidence, and live-runtime tests. A big-bang reorganization would create unnecessary regression and audit risk. The migration therefore uses a strangler-style approach: extract one stable responsibility at a time, keep existing import paths as compatibility facades, prove behavioral equivalence, then continue outward.

## Current-state diagnosis

The repository-level information architecture is intentional and remains unchanged. The architectural debt is primarily inside the Python package.

### 1. `engine.py` remains a compatibility/composition facade

Tranches 1–4 have removed deterministic classification/risk ownership, finalization ownership, dispatch orchestration ownership, and specialist-routing inheritance from the base engine path. `OrchestrationEngine.dispatch()` delegates to the dispatch application service, and optional risk/preference refinement seams default to no-op behavior unless explicitly composed. Runtime-selection compatibility methods remain in the facade pending later bounded extraction.

### 2. Specialist routing is now composition-based

`SpecialistRoutingEngine` remains the accepted public compatibility façade but no longer subclasses `OrchestrationEngine`. Specialist risk refinement and runtime-preference refinement are composed through `application/dispatch/specialist_policy.py`, while specialist-selection YAML/filesystem loading is behind `SpecialistSelectionPolicyPort` and the YAML adapter. Existing specialist dispatch, documentation-recovery verifier behavior, runtime lifecycle gates, provider diversity, and public compatibility are preserved.

### 3. Configuration source I/O is separated; composition is the next coupling target

Tranche 5A moved repository configuration filesystem/PyYAML reads behind `RepositoryConfigurationSourcePort` and `YamlRepositoryConfigurationAdapter`. `config.py` no longer performs direct YAML or filesystem reads, but the `ConfigBundle` compatibility façade still owns the explicit repository path manifest, extension ordering, merge/override composition, normalization, invariant validation, and runtime registry projections.

Tranche 5B owns the explicit composition/manifest boundary. T5C and T5D remain separately reviewable validation and immutable-runtime-view boundaries.

### 4. Provider contracts and provider implementations still share package-level surfaces

Provider-neutral contracts exist, while provider implementations, retry/circuit behavior, verification, and runtime execution remain broadly distributed. Tranche 6 will move these behind explicit outer-layer namespaces with compatibility shims.

### 5. The package root remains a broad compatibility surface

`teo_reference.__init__` continues to preserve existing public imports. Compatibility reduction is an explicit later API decision, not an automatic effect of internal reorganization.

## Target package structure

The target structure is a dependency map, not permission for an immediate bulk move.

```text
teo_reference/
├── domain/
│   ├── models.py
│   ├── routing/
│   ├── evidence/
│   └── authority/
├── application/
│   ├── configuration/
│   │   └── composition.py
│   ├── dispatch/
│   │   ├── service.py
│   │   ├── resolvers.py
│   │   ├── selectors.py
│   │   └── specialist_policy.py
│   ├── finalization/
│   │   └── service.py
│   ├── runtime/
│   └── evaluation/
├── ports/
├── adapters/
├── interfaces/
└── compatibility facades
    ├── engine.py
    ├── specialist_routing.py
    ├── schemas.py
    ├── config.py
    ├── provider_adapter.py
    └── __init__.py
```

The compatibility facades remain at their existing import paths until downstream callers and tests prove that removal or deprecation is safe.

## Dependency rule

Dependencies point inward:

```text
interfaces/adapters -> ports/application -> domain
```

The domain layer must not import filesystem, YAML, provider SDK, environment, network, telemetry, runtime, or repository-loading modules.

Application services may depend on domain policy and abstract ports. Concrete adapters implement those ports. Compatibility facades may temporarily bridge old import paths to the new structure, but new domain/application code must not depend back on outer facades or concrete provider adapters.

## Migration sequence

### Tranche 1 — deterministic routing domain boundary — COMPLETE

Merged via PR #196 as `a63887179a1ff3adfa7d7119a7db1a5f598a0f86`.

- extracted task-classification rules from `engine.py` into the domain routing boundary;
- extracted monotonic risk assessment;
- preserved `teo_reference.engine.RoutingError`, `TASK_PATTERNS`, and `RISK_PATTERNS` compatibility;
- added direct behavior and dependency-direction tests.

### Tranche 2 — finalization use case + artifact-integrity port — COMPLETE

Merged via PR #198 as `467c706d6f1077371928e3fcbe3f32f5ec51fb19`.

- extracted final outcome construction behind `FinalizationService`;
- introduced the artifact-integrity port and filesystem default adapter;
- kept `OrchestrationEngine.finalize()` as the compatibility facade;
- preserved artifact-bound finalization and authority behavior.

### Tranche 3 — dispatch application service — COMPLETE

Merged via PR #210 as `74c128947f1d98f0e42c595bd1229561ab6dab50`.

Implemented:

- `application/dispatch/DispatchService` as the dispatch use-case coordinator;
- `WorkerResolver`, `SpecialistResolver`, and `CapabilityResolver` for responsibility resolution;
- an application-facing `ImplementationSelector` seam for primary/fallback/verifier selection;
- `OrchestrationEngine.dispatch()` reduced to a thin service facade;
- legacy protected resolver helpers retained as compatibility wrappers;
- dependency-direction tests preventing the dispatch application package from importing the outer engine, adapters, provider modules, or CLI;
- explicit preservation of the `SpecialistRoutingEngine` inheritance/refinement/preference bridge for the independently reviewable Tranche 4.

Exact-head qualification on `504c05f67ee6d89e0144e6d16c11c3a19509e780` was Reference Implementation CI #960: **1,118 tests passed**, **607 tracked files** validated, **42 schemas** parsed, regulated-specialist evidence passed, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing passed.

### Tranche 4 — specialist routing by composition — COMPLETE

Merged via PR #212 as `2f4df9d1124be91473e346ddb926f5d93c93de3e`.

Implemented:

- `SpecialistRoutingEngine` remains the public compatibility façade but no longer subclasses `OrchestrationEngine`;
- specialist risk and selection-preference refinement moved into the pure application-layer `SpecialistRoutingPolicy`;
- specialist-selection YAML/filesystem loading moved behind `SpecialistSelectionPolicyPort` and `YamlSpecialistSelectionPolicyAdapter`;
- base-engine risk/preference refinement seams are explicit, optional, and no-op when no policy is injected;
- the façade delegates accepted compatibility helpers to the composed base engine rather than relying on protected subclass coupling;
- temporary MRO/inheritance characterization tests were replaced by composition, dependency-direction, and responsibility-equivalence assertions.

Exact-head qualification on `176217f9803c2ec274d2b225c52cf1f4d5c0f27f` was Reference Implementation CI #968: **1,120 tests passed**, **610 tracked files** validated, **42 schemas** parsed, regulated-specialist evidence passed, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing passed.

The tranche did not change Runtime Model Binding behavior, model/default policy, provider access/authentication, live scope, routing authority, risk semantics, or provider-diverse verification.

### Tranche 5 — configuration boundary — IN PROGRESS

Tranche 5 is split into independently reversible subtranches so loading, composition, validation, and runtime projection are not moved together.

#### Tranche 5A — configuration source I/O — COMPLETE

Merged via PR #214 as `1ba1a4b0a83e403b422b47f2e7b7cef733ccb201`.

Implemented:

- `RepositoryConfigurationSourcePort` for required and explicitly named optional repository configuration mappings;
- `YamlRepositoryConfigurationAdapter` as the concrete filesystem/PyYAML adapter;
- `ConfigBundle.load()` source injection while preserving its accepted compatibility surface;
- exact explicit required/optional source paths with no directory scanning or implicit discovery;
- translation of adapter source errors back into the existing public `ConfigurationError` contract;
- boundary tests proving `config.py` itself performs no YAML/filesystem reads.

Exact PR-head qualification on `17afc5d5ff3b74897e6c2bcd534ccb6158fbc2cb` was Reference Implementation CI #977: **1,127 tests passed**, **612 tracked files** validated, **42 schemas** parsed, regulated-specialist evidence passed, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing passed.

Merged-main qualification on `1ba1a4b0a83e403b422b47f2e7b7cef733ccb201` was Reference Implementation CI #978: **1,127 tests passed**, **612 tracked files** validated, **42 schemas** parsed, regulated-specialist evidence passed, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing passed.

T5A deliberately preserved the explicit extension manifest, composition/merge/override rules, normalization, invariant validation, and mutable runtime projections for later bounded subtranches.

#### Tranche 5B — configuration composition and explicit manifest — NEXT

Extract from the `ConfigBundle` compatibility façade:

1. the exact required and optional repository configuration path manifest;
2. extension ordering;
3. team-route, routing, Worker, and Specialist merge/override rules;
4. conditional-escalation and verification-policy normalization.

The application-side composition boundary may depend on `RepositoryConfigurationSourcePort` but must not import concrete adapters, YAML, the outer `config.py` façade, provider modules, runtime execution, or CLI surfaces. `ConfigBundle.load()` remains the compatibility entry point and delegates composition through the extracted boundary.

Acceptance must prove exact source-path requests, ordering, duplicate rejection, approved override behavior, protected Specialist override rejection, normalization equivalence, and unchanged whole-repository behavior.

The manifest must remain explicit and fail closed. T5B must not weaken repository governance, permit implicit policy discovery, turn configuration discovery into routing authority, change provider/model defaults, alter Runtime Model Binding, widen live scope, or implement Issue #215 Stage B.

#### Tranche 5C — invariant validation — LATER

Extract `ConfigBundle.validate()` invariant ownership behind an explicit validation boundary while preserving existing mutable compatibility behavior, error/warning semantics, and fail-closed `ConfigBundle.load()` behavior.

#### Tranche 5D — immutable runtime configuration view — LATER

Introduce an immutable runtime-facing configuration view behind the existing mutable `ConfigBundle` compatibility façade. Existing tests and downstream callers that intentionally mutate `ConfigBundle` for validation/conformance remain supported until compatibility evidence permits a separate API decision.

Full Tranche 5 is not complete until T5A through T5D are qualified and canonical stewardship records are reconciled.

### Tranche 6 — providers, verification, runtime, and evaluation namespaces

Move concrete providers/verifiers and runtime/evaluation subsystems under explicit outer-layer namespaces. Existing top-level modules act as temporary compatibility shims. Perform moves in bounded groups, not as one mechanical relocation.

### Tranche 7 — compatibility reduction

Only after import telemetry, tests, release notes, and downstream evidence support it, reduce the broad package-root re-export surface. This is a separate API decision, not an automatic consequence of code organization.

## Architectural fitness requirements

Every tranche must preserve or strengthen these checks:

- deterministic classification and risk behavior;
- monotonic risk floors;
- provider-diverse independent verification;
- preview-model fail-closed behavior;
- artifact-bound finalization;
- authority and recovery integrity;
- routing conformance;
- mutation coverage for consequential invariants;
- repository-layout conformance;
- public compatibility paths until explicitly retired.

New boundary tests should enforce dependency direction mechanically where practical. The architecture is not considered improved merely because files were moved.

## Rollback strategy

Each tranche must be independently revertible. Do not combine behavior changes, model-routing changes, live-scope changes, or policy changes with architectural extraction. If a tranche changes a canonical output or invalidates a conformance test, revert the tranche and diagnose before proceeding.

## Completion criteria

The migration is complete when:

1. `engine.py` is a thin compatibility/composition facade rather than the owner of domain/use-case rules;
2. inner policies are pure and mechanically protected from outer dependencies;
3. configuration and provider I/O sit behind explicit ports;
4. specialist refinement no longer relies on fragile subclass coupling;
5. public behavior and accepted import surfaces are either preserved or deliberately versioned;
6. the complete canonical test, mutation, layout, and CI gates pass on the final migration head;
7. stewardship documentation reflects the merged repository state.
