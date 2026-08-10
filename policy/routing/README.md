# Routing Policy

This directory contains current machine-readable routing authority. Its structure separates base policy, additive active extensions, and current activation manifests.

## Canonical areas

- [`core/`](core/) contains canonical base team, implementation, and specialist-model routing policy.
- [`extensions/`](extensions/) contains additive active route families loaded alongside the core policy.
- [`activation/`](activation/) contains current activation manifests that prove which staged topology has become active.

Superseded routing drafts, expansion plans, and staging manifests are historical evidence under [`docs/history/activation/`](../../docs/history/activation/). They do not provide current routing authority.

The reference implementation loads explicit canonical paths. It does not discover or load arbitrary YAML by directory traversal. New routing files require an intentional repository-layout policy update and corresponding conformance coverage.
