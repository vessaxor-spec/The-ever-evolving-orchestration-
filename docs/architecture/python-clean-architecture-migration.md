# Python Reference Clean-Architecture Migration

Status: **incremental implementation**  
Scope: `reference/implementations/python/src/teo_reference/`  
Behavioral rule: **no routing, risk, verification, authority, evidence, provider, or public-API behavior may change as a side effect of this migration.**

## Decision

The Python reference implementation will move toward explicit clean-architecture boundaries through small, compatibility-preserving tranches rather than a repository-wide file move.

TEO is already a mature control plane with strong conformance, mutation, authority, evidence, and live-runtime tests. A big-bang reorganization would create unnecessary regression and audit risk. The migration therefore uses a strangler-style approach: extract one stable responsibility at a time, keep existing import paths as compatibility facades, prove behavioral equivalence, then continue outward.

## Current-state diagnosis

The repository-level information architecture is already intentional and must remain unchanged. The architectural debt is primarily inside the Python package.

### 1. `engine.py` owns too many concerns

`OrchestrationEngine` currently performs deterministic task classification, risk assessment, team/worker/specialist resolution, capability resolution, implementation selection, fallback selection, verifier selection, and finalization. Finalization also reaches directly into filesystem-backed artifact integrity.

This makes the engine an orchestration facade, policy engine, selector, and infrastructure client at the same time.

### 2. `specialist_routing.py` is tightly coupled to engine internals

`SpecialistRoutingEngine` subclasses the base engine, overrides protected behavior, consumes private helpers, loads YAML policy itself, and mutates the dispatch returned by `super().dispatch()`. The behavior is tested, but the inheritance relationship makes internal refactoring expensive.

### 3. `config.py` combines loading, composition, normalization, validation, and projection

`ConfigBundle` owns filesystem/YAML I/O, the extension manifest, config composition, invariant validation, and runtime registry views. The result is a large boundary object whose responsibilities span infrastructure and application policy.

### 4. Provider contracts and provider implementations share the same package level

Provider-neutral contracts exist, but OpenAI, Anthropic, Google, retry/circuit behavior, verification, and runtime execution all occupy one flat namespace. The code is modular by file but not yet explicit by dependency direction.

### 5. The package root is a broad compatibility surface

`teo_reference.__init__` re-exports a large portion of the implementation and aliases the specialist router as `OrchestrationEngine`. That surface should be preserved during migration, then simplified only through an explicit compatibility decision.

## Target package structure

The target structure is a dependency map, not permission for an immediate bulk move.

```text
teo_reference/
├── domain/
│   ├── models.py                 # task, dispatch, verification, outcome value objects
│   ├── routing/
│   │   ├── classification.py     # deterministic task classification
│   │   ├── risk.py               # monotonic risk policy
│   │   ├── capability.py         # capability satisfaction rules
│   │   └── eligibility.py        # implementation eligibility rules
│   ├── evidence/                 # evidence/provenance invariants
│   └── authority/                # approval/authority invariants
├── application/
│   ├── dispatch/
│   │   ├── service.py            # dispatch use case
│   │   ├── worker_resolver.py
│   │   ├── specialist_resolver.py
│   │   ├── implementation_selector.py
│   │   └── verification_planner.py
│   ├── finalization/
│   │   └── service.py            # final outcome use case
│   ├── runtime/                  # guarded execution/retry/recovery use cases
│   └── evaluation/               # benchmark/shadow/calibration use cases
├── ports/
│   ├── configuration.py          # configuration source contract
│   ├── provider.py               # provider execution contract
│   ├── verifier.py               # independent verification contract
│   ├── artifact.py               # artifact identity/integrity contract
│   ├── telemetry.py              # telemetry sink contract
│   └── evidence_store.py         # append/read evidence contract
├── adapters/
│   ├── configuration/
│   │   └── yaml_repository.py
│   ├── providers/
│   │   ├── openai.py
│   │   ├── anthropic.py
│   │   └── google.py
│   ├── verification/
│   ├── filesystem/
│   └── persistence/
├── interfaces/
│   └── cli/
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

Application services may depend on domain policy and abstract ports. Concrete adapters implement those ports. Compatibility facades may temporarily bridge old import paths to the new structure, but new domain code must not depend back on the facades.

## Migration sequence

### Tranche 1 — deterministic routing domain boundary

Implemented in the first migration PR:

- extract task-classification rules from `engine.py` into `domain/routing.py`;
- extract monotonic risk assessment from `engine.py` into the same pure domain module;
- keep `teo_reference.engine.RoutingError`, `TASK_PATTERNS`, and `RISK_PATTERNS` import-compatible by re-exporting the domain definitions;
- make the engine delegate to pure policies;
- add direct behavior tests and an architectural fitness test prohibiting outer-layer imports from the new domain module.

This is intentionally narrow. It reduces engine responsibility without changing route selection, provider policy, risk semantics, or public entry points.

### Tranche 2 — finalization use case + artifact-integrity port

Extract final outcome construction from `engine.py`. Replace the direct dependency on filesystem artifact revalidation with an injected artifact-integrity port whose default adapter preserves current behavior. Keep `OrchestrationEngine.finalize()` as the compatibility facade.

Acceptance requires all artifact-bound finalization, execution-provenance, authority, recovery, and mutation tests to remain green.

### Tranche 3 — dispatch application service

Move worker/specialist/capability resolution, primary/fallback selection, and verification planning behind a dispatch service. Preserve deterministic policy and all current fail-closed behavior. `engine.py` becomes a thin composition facade.

### Tranche 4 — specialist routing by composition

Replace inheritance-heavy specialist routing with composable policy refinement. Specialist model policy loading moves behind a configuration port. The public `SpecialistRoutingEngine` remains available until compatibility evidence supports a later simplification.

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

1. `engine.py` is a thin compatibility/composition facade rather than the owner of domain rules;
2. inner policies are pure and mechanically protected from outer dependencies;
3. configuration and provider I/O sit behind explicit ports;
4. specialist refinement no longer relies on fragile subclass coupling;
5. public behavior and accepted import surfaces are either preserved or deliberately versioned;
6. the complete canonical test, mutation, layout, and CI gates pass on the final migration head;
7. stewardship documentation reflects the merged repository state.
