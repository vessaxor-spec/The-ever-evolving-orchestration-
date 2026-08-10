# Routing Policy

This directory contains current machine-readable routing authority. Its structure separates base policy, additive active extensions, and current activation manifests.

## Canonical areas

- [`core/`](core/) contains canonical base team, implementation, specialist-model routing policy, and implementation defaults.
- [`extensions/`](extensions/) contains additive active route families loaded alongside the core policy.
- [`activation/`](activation/) contains current activation manifests that prove which staged topology has become active.

[`core/implementation-defaults.yaml`](core/implementation-defaults.yaml) defines active implementation aliases and routing defaults. Current provider and model evidence remains separately authoritative under [`registry/models/models.yaml`](../../registry/models/models.yaml). Routing defaults must not be treated as a substitute for current evidence.

Superseded routing drafts, expansion plans, and staging manifests are historical evidence under [`docs/history/activation/`](../../docs/history/activation/). They do not provide current routing authority.

The reference implementation loads explicit canonical paths. It does not discover or load arbitrary YAML by directory traversal. New routing files require an intentional repository-layout policy update and corresponding conformance coverage.
