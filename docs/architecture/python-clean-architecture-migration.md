# Python Reference Clean-Architecture Migration

Status: **incremental implementation — Tranches 1–3 merged**  
Scope: `reference/implementations/python/src/teo_reference/`  
Behavioral rule: **no routing, risk, verification, authority, evidence, provider, or public-API behavior may change as a side effect of this migration.**

## Decision

The Python reference implementation will move toward explicit clean-architecture boundaries through small, compatibility-preserving tranches rather than a repository-wide file move.

TEO is already a mature control plane with strong conformance, mutation, authority, evidence, and live-runtime tests. A big-bang reorganization would create unnecessary regression and audit risk. The migration therefore uses a strangler-style approach: extract one stable responsibility at a time, keep existing import paths as compatibility facades, prove behavioral equivalence, then continue outward.

## Current-state diagnosis

The repository-level information architecture is intentional and remains unchanged. The architectural debt is primarily inside the Python package.

### 1. `engine.py` remains a compatibility/composition facade

Tranches 1–3 have removed deterministic classification/risk ownership, finalization ownership, and dispatch orchestration ownership from `engine.py`. `OrchestrationEngine.dispatch()` now delegates to an application service. Runtime-selection compatibility methods remain in the facade so the specialist inheritance bridge can be removed independently in Tranche 4.

### 2. `specialist_routing.py` remains the next coupling target

`SpecialistRoutingEngine` still subclasses the base engine and overrides protected risk/preference behavior. Tranche 3 deliberately preserved that bridge so dispatch extraction could be qualified without combining an inheritance rewrite. Tranche 4 owns the transition to composition.

### 3. `config.py` still combines loading, composition, normalization, validation, and projection

`ConfigBundle` owns filesystem/YAML I/O, the extension manifest, config composition, invariant validation, and runtime registry views. That split remains Tranche 5.

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
│   ├── dispatch/
│   │   ├── service.py
│   │   ├── resolvers.py
│   │   └── selectors.py
│   ├── finalization/
│   │   └── service.py
│   ├── runtime/
│   └── evaluation/
├── ports/
├── adapters/
├── interfaces/
└── compatibility facades
    ├── engine.py
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
- explicit preservation of the `SpecialistRoutingEngine` inheritance/refinement/preference bridge for Tranche 4.

Exact-head qualification on `504c05f67ee6d89e0144e6d16c11c3a19509e780` was Reference Implementation CI #960: **1,118 tests passed**, **607 tracked files** validated, **42 schemas** parsed, regulated-specialist evidence passed, linked configuration `status: valid` with `issues: []`, and provider-diverse end-to-end routing passed.

### Tranche 4 — specialist routing by composition — NEXT

Replace inheritance-heavy specialist routing with composable policy refinement. Specialist selection-policy loading should move behind an appropriate configuration boundary while preserving the public `SpecialistRoutingEngine` compatibility surface.

Acceptance must prove that specialist risk elevation, specialist selection-profile preferences, documentation recovery verifier behavior, provider diversity, runtime lifecycle gates, and current public dispatch behavior remain unchanged. Tranche 4 must not absorb the broader ConfigBundle split reserved for Tranche 5.

### Tranche 5 — configuration boundary

Split `ConfigBundle` responsibilities into:

1. YAML/filesystem adapter;
2. configuration composition;
3. invariant validation;
4. immutable runtime configuration view.

The extension manifest must remain explicit and fail closed; the migration must not weaken repository governance or permit implicit policy discovery.

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
