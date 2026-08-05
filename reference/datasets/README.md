# Reference Datasets

Public datasets and fixtures used for examples, evaluation, and conformance testing.

## Routing conformance

[`routing-conformance.yaml`](routing-conformance.yaml) records representative tasks and the stable dispatch properties they are expected to produce.

The fixtures intentionally assert only routing-significant fields. Runtime identifiers and timestamps are excluded. Each scenario also requires the execution implementation and verification implementation to remain independent.

A routing change is not rejected merely because it differs from the baseline. It is rejected when the change is silent. Intentional changes must update the affected fixture with the policy or registry change that justifies the new result.

Provider-aware fallback behavior is additionally enforced by [`tests/test_provider_fallback_policy.py`](../../tests/test_provider_fallback_policy.py). Active routes must expose a non-local routine fallback from a different provider family, worker and family fallback pools must use canonical provider metadata, and Opus must remain outside routine fallback chains. The underlying methodology is documented in [`docs/methodology/provider-aware-fallbacks.md`](../../docs/methodology/provider-aware-fallbacks.md).

## Mission Control worker conformance

[`mission-control-worker-conformance.yaml`](mission-control-worker-conformance.yaml) binds the `agents-orchestrator`, `operations-manager`, `project-manager`, and `incident-commander` specialists to distinct Mission Control core workers.

The fixtures verify team ownership, worker binding, specialist risk profile, role-card reference, responsibilities, capabilities, verification requirements, escalation coverage, and authority boundaries. The worker layer is additive and does not replace the authoritative specialist specifications.

## Mission Control routing conformance

[`mission-control-routing-conformance.yaml`](mission-control-routing-conformance.yaml) records executable task classification, specialist activation, implementation fallback, risk elevation, and independent verification for the `orchestration`, `operations`, `project_delivery`, and `incident_response` routes.

The incident-response scenario additionally requires critical-risk verification, qualified human approval, technical sign-off confirmation, and preservation of the incident commander's coordination-only authority.

## Research worker conformance

[`research-worker-conformance.yaml`](research-worker-conformance.yaml) binds the `researcher` specialist to the dedicated Research Team `research` worker.

The fixture protects source triangulation, evidence traceability, contradiction analysis, confidence calibration, escalation boundaries, and the separation between research synthesis and final deliverable writing. Routing conformance separately requires `deep_research` to use this worker while documentation tasks remain on the `documentation` worker.

## Market research worker conformance

[`market-research-worker-conformance.yaml`](market-research-worker-conformance.yaml) binds the `market-analyst` specialist to the dedicated Research Team `market_research` worker.

The fixture protects explicit market boundaries, current-data requirements, methodology and source traceability, estimate labeling, moat and lifecycle analysis, weak-signal corroboration, willingness-to-pay weighting, and the separation from campaign execution, paid media, investment decisions, and broad-domain research.

## Configuration warning baseline

[`configuration-warning-baseline.yaml`](configuration-warning-baseline.yaml) records known inconsistencies currently exposed by configuration validation.

Warnings are not treated as acceptable forever. The exact comparison ensures that:

- new inconsistencies cannot enter unnoticed
- existing inconsistencies cannot disappear without review
- wording changes remain visible when validation semantics change
- resolved inconsistencies require removal from the baseline

Run the complete conformance suite with:

```bash
pytest
```
