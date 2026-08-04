# Model Registry

Public model metadata, versioned capabilities, access constraints, and supporting evidence.

Entries distinguish provider claims from TEO-observed results. A provider description is evidence that the provider makes a claim, not proof that the model is best for a TEO route.

## Registry

- [`models.yaml`](models.yaml) contains current routing-relevant model identifiers and source-backed provider metadata.
- The root [`models.yaml`](../../models.yaml) maps stable TEO aliases to concrete implementations.

## Required model fields

A model entry should identify:

- exact provider identifier
- provider and availability class
- provider-described role
- TEO routing role
- supported modalities and tools where documented
- context and output limits where material
- evidence type and source
- date reviewed
- limitations, preview status, and unresolved evidence

## Evidence types

- `teo_observed`: reproduced through a documented TEO evaluation
- `independent_benchmark`: produced by an external reproducible benchmark
- `provider_claim`: stated in current provider documentation
- `deployment_required`: cannot be generalized without the exact runtime and artifact

Model identifiers and availability should be rechecked before execution.
