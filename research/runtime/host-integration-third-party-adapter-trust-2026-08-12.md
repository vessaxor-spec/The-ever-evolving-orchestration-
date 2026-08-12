# Host Integration Third-Party Adapter Trust Mutation Audit

**Date:** 2026-08-12  
**Authority:** non-normative research  
**Base revision:** `57005b6469295ff1c53c62abee85d5de8b1cc50a`

## Question

Can an external host execute an arbitrary or modified provider adapter merely by presenting an adapter-like object or self-declared manifest, or can TEO require an authority-owned registration that binds the approved adapter identity before any provider attempt?

## Mission Control lenses

- orchestration security
- supply-chain integrity
- authority boundaries
- adversarial verification

## Repository diagnosis

The normative Provider Adapter Contract already constrains what an authorized adapter may do during one provider attempt. It does not define a third-party adapter discovery, approval, registration, package-integrity, or code-provenance authority.

The canonical `registry/` currently covers providers, models, capabilities, and benchmarks. There is no active adapter registry. Creating a normative adapter registry solely to run this experiment would therefore promote an unproven Host Integration concept into repository authority prematurely.

The Host Integration research roadmap already states that capability-adapter manifests are authority surfaces and that an active executor must not rewrite a binding and consume the widened binding in the same dispatch. This audit therefore remains under `research/runtime/` and does not create `registry/adapters/`, change the Provider Adapter Contract, or widen live execution.

## Candidate research boundary

The research harness introduces a process-local `ProcessLocalAdapterAuthority` with four authority-owned bindings:

1. the exact canonical manifest snapshot;
2. a SHA-256 digest of implementation artifact bytes obtained through an authority-owned artifact reader;
3. the exact runtime adapter type returned by the approved factory at registration time;
4. an opaque registration token whose lifecycle can be revoked.

The approved manifest binds:

- adapter identifier;
- provider family;
- Provider Adapter Contract version `1`;
- the single allowed operation `provider_execute_once`;
- the capabilities the registration is permitted to satisfy.

At execution, the host supplies only the registration token, approved manifest view, and already-routed dispatch. The authority rechecks its own registration state, remeasures the implementation artifact, resolves the authority-owned factory, confirms exact runtime type and provider family, intersects dispatch-required capabilities with the approved manifest, and only then calls the existing `execute_provider_once()` contract.

## Adversarial cases

The executable suite challenges the candidate boundary with:

1. an entirely self-issued registration token;
2. a revoked registration;
3. implementation artifact replacement after approval;
4. adapter-ID manifest substitution;
5. provider-family manifest substitution;
6. capability-manifest widening;
7. cross-registration token reuse;
8. post-registration factory substitution to a different runtime adapter type;
9. post-registration provider-family drift on the registered runtime type;
10. a factory whose provider family never matched the approved manifest;
11. a dispatch whose selected provider differs from the approved adapter;
12. a dispatch requiring capabilities outside the approved registration;
13. an adapter attempting to self-assert a wider manifest;
14. a manifest attempting to declare a different contract version;
15. a manifest attempting to declare a wider execution operation including fallback authority.

The candidate passes only when every unauthorized case fails before provider execution.

## Trust boundary

This experiment deliberately does not claim production-grade software-supply-chain attestation.

The `artifact_reader` is an abstraction for a trusted loader or package store. If an untrusted host can choose both the executable adapter and the bytes used for measurement, a matching digest proves nothing. A production design must derive executable identity from an authority-controlled loading path and bind the measured artifact to what is actually loaded.

Likewise, process-local Python type identity is useful for detecting tested factory substitution but is not portable code signing, package provenance, sandboxing, or distributed attestation.

A later production design would require separate review of at least:

- trusted package acquisition and loading;
- signature or provenance verification where applicable;
- dependency and transitive-code identity;
- revocation and update semantics;
- restart and cross-process persistence;
- rollback and downgrade resistance;
- least-privilege execution isolation;
- authority for approving, activating, and removing external adapters.

## Decision boundary

If the mutation suite passes, the narrow supported proposition is:

> A third-party adapter can be made non-self-authorizing when execution resolves through an authority-owned registration that binds exact manifest state, measured artifact identity, registered runtime type, provider family, operation, capability scope, and revocation state before the existing Provider Adapter Contract is invoked.

That result would not make third-party adapters supported by TEO, create a normative adapter registry, authorize external-host execution, establish production package provenance, or change live scope.

## Verification record

Pending branch CI. The final evidence record must include the exact passing suite count and repository validation result before this research slice can be marked satisfied in the Progress Tracker.
