# Reference Datasets

Public datasets and fixtures used for examples, evaluation, and conformance testing.

## Routing conformance

[`routing-conformance.yaml`](routing-conformance.yaml) records representative tasks and the stable dispatch properties they are expected to produce.

The fixtures intentionally assert only routing-significant fields. Runtime identifiers and timestamps are excluded. Each scenario also requires the execution implementation and verification implementation to remain independent.

A routing change is not rejected merely because it differs from the baseline. It is rejected when the change is silent. Intentional changes must update the affected fixture with the policy or registry change that justifies the new result.

## Mission Control worker conformance

[`mission-control-worker-conformance.yaml`](mission-control-worker-conformance.yaml) binds the `agents-orchestrator`, `operations-manager`, and `project-manager` specialists to distinct Mission Control core workers.

The fixtures verify team ownership, worker binding, specialist risk profile, role-card reference, responsibilities, capabilities, verification requirements, escalation coverage, and authority boundaries. The worker layer is additive and does not replace the authoritative specialist specifications.

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
