# Roadmap

TEO has completed the foundation, team architecture, routing validation, registry population, and reference control-plane phases.

The current roadmap is focused on proving and operating the decision system rather than adding model/provider abstractions for their own sake.

## Completed foundation

- public project identity, Constitution, Lexicon, and stewardship rules
- ten accountable teams
- stable worker architecture
- 78 preserved specialist role cards
- provider/model/capability registries
- deterministic task and risk routing
- fallback, escalation, verification, and human-authority controls
- runnable Python reference control plane
- guarded live provider execution for bounded `high_volume_simple` work
- bounded retry and canonical fallback redispatch
- provider-family circuit state
- content-free runtime telemetry
- provider-diverse live independent verification
- six-card regulated evidence/freshness pilot

## Current: control integrity and operational evidence

### Control integrity

- require effective risk to preserve all higher risk signals
- prove all 78 active specialists are deterministically spawnable
- enforce capability and implementation eligibility at runtime
- require explicit preview-model authorization
- enforce provider-diverse independent verification
- protect local runtime artifacts and credential boundaries
- bind verifier artifacts to authorized runtime roots
- keep caller/user identifiers out of default telemetry
- enforce JSON Schemas at external control-plane boundaries
- keep machine-readable policy and implementation behavior mutation-tested

### Verifier calibration

Build deterministic gold-label and human-rated calibration evidence for the guarded verifier rubric.

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

Do not broaden live verification based on model confidence alone.

### Route-outcome evidence

Join routing, provider-attempt telemetry, verification evidence, and final outcomes into an evaluation layer that measures decision quality without allowing the execution model to grade itself.

### Cost attribution

Add source-backed, effective-dated pricing records and versioned cost calculations. Pricing must remain separate from provider usage telemetry.

### Qualified-human authority

Implement an explicit approval lifecycle for decisions requiring qualified human authority, including identity/role of the approval authority, disposition, evidence, and audit linkage.

### Distributed runtime hardening

Replace single-process reference persistence where production deployment requires:

- coordinated distributed circuit state
- concurrency-safe telemetry export
- access control and retention
- integrity and recovery guarantees
- distributed workflow/audit correlation
- streaming and richer latency evidence

## Regulated specialist pilot

Keep the evidence-backed freshness pilot limited to the approved six cards until maintainability is demonstrated through repeated refresh cycles, authority resolution, provenance checks, expiry behavior, independent verification, mutation tests, and explicit approval.

A broader regulated evidence registry is not authorized merely because the pilot validates structurally.

## Live execution expansion gate

Broaden live execution by task class only when the applicable authority, capability, verification, telemetry, recovery, evidence, and human-approval controls have demonstrated reliable behavior.

High and critical live execution remains outside the current guarded runtime.

## Community and licensing

Finalize licensing and contribution terms before representing TEO as open source or inviting external code contribution under reuse rights that have not yet been granted.

The roadmap is directional. Routing and verification quality remain the priority.
