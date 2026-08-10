# Changelog

All notable public changes to TEO are recorded here.

## Unreleased

### Added

- ten-team organizational architecture
- public roster of 78 preserved specialist role cards
- principal-engineering specialist and worker activation
- effort-aware cross-provider specialist model routing
- provider-neutral execution contract and connection-neutral provider boundary
- guarded Anthropic, OpenAI, and Google live execution adapters
- bounded transient retry and provider-directed retry timing
- canonical model/provider fallback redispatch with fresh verifier assignment
- persistent provider-family circuit state
- content-free provider-attempt telemetry with normalized usage
- provider-diverse live independent verification
- six-card regulated evidence/freshness pilot with CI source validation and mutation testing
- explicit preview-model authorization in task constraints
- deterministic all-78 specialist spawn routes and spawnability conformance
- strict CLI JSON Schema validation for task, dispatch, execution, verification, and final outcome records
- repository protection for local `.teo/` runtime artifacts
- repository layout governance, tracked-path validation, and strategic authority/lifecycle zoning
- canonical philosophy, specification, stewardship, release, and research-roadmap locations with folder indexes

### Changed

- effective risk now preserves the highest content-derived, declared, and specialist risk signal rather than allowing caller input to lower the risk floor
- active specialist worker bindings are complete rather than retained as known configuration warnings
- capability resolution now rejects unknown or team-incompatible caller-requested capabilities
- base implementation selection is constrained by worker-authorized implementations
- preview implementations are ineligible until the concrete preview model is explicitly accepted by the task
- independent verification requires both model and provider-family separation from execution
- half-open provider circuits no longer treat local connection failure as provider service-health failure
- live verification confines output artifacts to an authorized runtime root
- verifier candidate output is explicitly untrusted data
- verifier status precedence now preserves mixed failed and uncertain criterion evidence
- runtime telemetry no longer persists caller-controlled task identifiers and explicitly fails closed on required persistence failure
- regulated evidence provenance for Rule 37(e) and ISO/IEC 9899:2024 was rechecked and corrected or clarified against primary sources
- `AI_INSTRUCTIONS.md`, `docs/stewardship/roadmap.md`, runtime specifications, and capability guidance now describe the active control plane
- root and research navigation now follow the repository layout contract instead of retaining temporary R2 placement exceptions

### Validation

- all active specialists must have a deterministic Team -> Worker -> Specialist spawn path
- known specialist binding warnings are no longer accepted as a configuration baseline
- credential-boundary tests cover common token, secret, and private-key field forms
- circuit tests cover half-open connection-health separation
- live verification tests cover artifact-root escape and candidate-output prompt injection
- telemetry tests prove caller identifiers and content remain absent
- routing tests prove a caller cannot lower content-derived risk and preview models require explicit acceptance
- CLI tests prove unknown schema fields fail at the external boundary
- repository layout tests reject undeclared root files, unscoped research, routing-policy drift, nested specialist identities, invalid capsule naming, and regression to retired R2 paths

### Status

Phases 1 through 5 are complete. Runtime execution remains intentionally guarded to explicit `high_volume_simple` work at low or medium effective risk.

Current work is operational evidence: control integrity, verifier calibration, route-outcome evaluation, source-backed cost attribution, qualified-human approval integration, distributed runtime hardening, and continued observation of the six-card regulated evidence pilot.

Repository information-architecture migration has completed R1 and R2. R3 documentation lifecycle separation is next.

High and critical live execution remain unauthorized.
