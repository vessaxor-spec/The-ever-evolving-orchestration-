---
capsule_id: TEO-CAPSULE-0007
status: accepted
captured_at: 2026-08-09T17:45:00+02:00
snapshot_commit: f3eda8289e3d5c85ab59f477e3fdbefdcb5a834d
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0006
immutability: accepted capsules are never rewritten
---

# Capsule 0007: Routing Is the Architecture, Access Is Not

This capsule records TEO after the August 2026 repository diagnostic, control-integrity remediation, model-freshness governance work, operational-evidence preparation, and the explicit architectural correction separating model routing from provider access.

It preserves the repository at commit `f3eda8289e3d5c85ab59f477e3fdbefdcb5a834d`, captured on **9 August 2026**. It extends [TEO-CAPSULE-0006](0006-2026-08-07-evidence-bearing-live-runtime.md). Earlier accepted capsules remain immutable.

## Why this moment was preserved

TEO had reached the reference-operational functional-v1 boundary, but a subtle drift appeared in operational language: API credentials were beginning to sound like an architectural prerequisite.

That framing was rejected.

TEO exists to decide **which intelligence should perform the work**, under what responsibility, capability, risk, fallback, reasoning, and verification constraints. It does not exist to own a user's provider subscription, credential lifecycle, billing relationship, entitlement, or authentication method.

Provider access changes independently from model fitness. A model may be reachable through an API key, OAuth, a subscription-backed session, delegated identity, service account, connector, credential broker, local runtime, or another provider-supported mechanism. None of those access methods makes the model intrinsically more or less appropriate for a task.

## Architectural boundary

### TEO owns

- task interpretation and deterministic routing
- risk and authority resolution
- team, worker, and specialist selection
- capability resolution
- model and reasoning-effort selection
- routine fallback and conditional escalation
- independent verification assignment
- evidence-bearing finalization
- model-freshness governance

### The user or integrator owns

- provider accounts
- API keys
- OAuth and subscription-backed sessions
- credentials and secrets
- billing and entitlement
- connector configuration
- service accounts and delegated identity
- other provider-supported access mechanisms

TEO may report that execution cannot proceed because the selected implementation is not reachable through the supplied connection. That is an execution-boundary condition. It is not evidence that routing selected the wrong model.

Authentication state must not become a hidden model-quality signal.

## Routing remains primary

```text
Task
  -> Risk
  -> Team
  -> Worker
  -> Optional Specialist
  -> Capability
  -> Model
  -> Reasoning effort
  -> Routine fallback
  -> Conditional escalation
  -> Independent verification
  -> Evidence-bearing outcome
```

Provider access occurs after the routing decision, at the execution boundary.

A user may implement that boundary however their environment permits. TEO's architecture should not need to change when the same routed model moves from API access to OAuth, from OAuth to a subscription-backed tool, or from one connection broker to another.

## Diagnostic and remediation milestone

The repository-wide diagnostic preceding this capsule found that the architecture was fundamentally sound but several controls needed stronger proof.

Remediation covered:

- negative-path protection for terminal finalization guards
- recoverable Half-Open circuit probes
- aligned circuit semantics across policy, runtime, and tests
- human-calibration blinding provenance
- preview-skip auditability
- hash-enforced CI dependencies
- routing configuration shape
- repeatability measurement semantics
- explicit treatment of registered but unrouted model candidates
- current model-freshness governance
- provider-access separation governance

The resulting CI suite exceeded five hundred automated tests while retaining schema validation, regulated-evidence validation, linked-configuration checks, and provider-diverse end-to-end verification.

## Model freshness without model churn

TEO now requires current model state to be established from authoritative provider evidence when model identity or availability matters.

A newer model does not automatically replace an existing route.

Freshness establishes what exists. Routing evidence establishes whether it belongs in a route.

User-specific authentication, billing, subscription, or entitlement state does not redefine model freshness.

## Operational evidence and v1 boundary

Functional v1 is defined as a credible vendor-neutral orchestration specification with a runnable reference control plane.

The stronger evidence tier uses blinded independent human review followed by repeated provider-diverse verifier observations. A provisional tier can use provider-diverse blinded machine judges followed by the repeated verifier study when human reviewers are not yet available.

The provisional tier may improve operational evidence and exercise the system, but it must not be represented as human ground truth and cannot silently expand routing authority or critical-risk autonomy.

Independent human calibration is preserved as a community-stewardship path rather than being allowed to block the functional reference implementation indefinitely. Qualified human approval for critical authority remains a separate boundary.

Distributed circuit coordination, distributed telemetry export, streaming, source-backed cost attribution, route-outcome learning, and qualified-human approval integration remain later hardening or expansion work rather than missing core routing architecture.

## Functional completion

TEO v1 should be judged primarily on whether the reference system can reliably:

- understand the task boundary
- resolve responsibility and specialist depth
- assess effective risk
- select the appropriate model and reasoning profile
- assign meaningful fallback and independent verification
- execute through a supplied provider connection where live execution is authorized
- recover from bounded failures
- preserve evidence
- fail closed when required controls cannot be satisfied

It should not be judged on whether TEO itself manages every provider's authentication lifecycle. That would turn orchestration into account and credential infrastructure and create coupling to a process that belongs outside TEO.

The guarded live execution canary remains intentionally narrower than the routing architecture. That is an authority boundary, not an indication that the broader routing system is incomplete.

## Message to future stewards

Do not let convenience integrations redefine the architecture.

A GitHub workflow may use API keys. A desktop client may use OAuth. A subscription product may expose the same model through its own authenticated session. An enterprise deployment may use delegated identity or a credential broker.

Those are access paths. They are not routing policy.

> **TEO chooses the intelligence. The user provides legitimate access to it.**

If access changes, adapt the connection boundary.

If model capability changes, revisit the evidence and routing.

Do not confuse the two.

The model is not the architecture.

The connection is not the architecture either.

---

**Recorded under the stewardship of Sylvester Roxas.**

**The signal persists.**
