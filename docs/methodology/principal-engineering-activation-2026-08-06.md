# Principal Engineering Specialist Activation

Date: 2026-08-06
Status: active implementation candidate

## Decision

TEO now activates the approved principal-engineering expansion through additive configuration extensions.

The target state is:

- 10 teams
- 78 specialists
- 22 newly added specialist cards
- 27 explicit principal-engineering routes
- five corrected allocations for DevOps, DevSecOps, Embedded, Civil, and Rust

This activation does not rewrite any authoritative specialist role card.

## Extension design

The active control plane loads four types of additive extension:

1. **Team routes** define the accountable team and worker.
2. **Implementation routes** define primary execution, routine fallback, and independent verification.
3. **Worker extensions** load staged worker contracts and controlled enrichments for existing Mobile and DevOps workers.
4. **Specialist extensions** add the 22 new specialist allocations and apply only the five approved allocation corrections.

The loader rejects duplicate new entries and limits specialist allocation overrides to:

- primary team
- supporting teams
- worker binding
- risk profile

Role-card paths, practitioner content, responsibilities, protocols, safety boundaries, outputs, and examples cannot be overridden through the activation file.

## Explicit routing policy

Principal-engineering routes require an explicit `task_type`.

This is intentional. Terms such as platform, safety, performance, network, architecture, or research are too broad to activate a high-consequence specialist deterministically from keywords alone.

The router therefore follows this rule:

```text
Explicit task type
  -> accountable team
  -> worker
  -> explicit or uniquely matched specialist
  -> effective risk
  -> primary implementation
  -> cross-provider fallback
  -> independent verifier
  -> qualified human approval when critical
```

An ambiguous request without an explicit task type continues to fail rather than inventing a route.

## Activated teams

### Platform and Reliability

Owns shared platforms, distributed systems, operational databases, networks, reliability, performance, technology economics, ML operations, DevOps, and DevSecOps.

### Systems Engineering

Owns stakeholder needs, system requirements, interfaces, technical baselines, integration, lifecycle coherence, and system verification and validation strategy.

### Physical Systems

Owns hardware, embedded systems, civil engineering, robotics and autonomy, silicon, aerospace and satellite systems, manufacturing, and physical integration.

### Assurance

Owns technical privacy, functional safety, selected formal correctness, and application-security assurance claims and evidence. It does not self-verify or replace Review, Verification, Legal, Compliance, Security, or accountable human authority.

## Allocation corrections

The activation applies the previously approved corrections:

| Specialist | Corrected primary team | Corrected worker |
|---|---|---|
| DevOps Engineer | Platform and Reliability | `devops` |
| DevSecOps Engineer | Platform and Reliability | `devsecops` |
| Embedded Engineer | Physical Systems | `embedded` |
| Civil Engineer | Physical Systems | `civil_engineering` |
| Rust Engineer | Engineering | `rust_systems_programming` |

The corrections change TEO allocation only. The five authoritative role cards remain unchanged.

## Mobile reconciliation

TEO already had a basic canonical `mobile` worker. The activation enriches that worker through a controlled override rather than creating a duplicate.

The enriched worker adds lifecycle state, offline synchronization, permissions, accessibility, security, privacy, performance, device testing, signing, staged rollout, and rollback while preserving the same Engineering Team ownership.

## Provider diversity

Each active principal route has:

- an explicit primary implementation
- a routine fallback from a different provider family
- an independent verifier from a third provider family where available

The route families are:

| Responsibility family | Primary | Routine fallback | Independent verifier |
|---|---|---|---|
| Planning | Anthropic | OpenAI | Google |
| Engineering execution | OpenAI | Google | Anthropic |
| Engineering reasoning | OpenAI | Google | Anthropic |
| Research | Google | Anthropic | OpenAI |
| Physical systems | OpenAI | Anthropic | Google |
| Assurance | Anthropic or OpenAI by domain | OpenAI or Anthropic | Google |

Local models are not automatic fallbacks. Claude Opus is not used as a routine fallback.

## Risk and approval

Every conformance case begins at an explicit low risk level. The activated specialist must elevate the effective risk to its registered medium, high, or critical profile.

Critical effective risk requires qualified human approval. This includes, among others:

- database reliability
- site reliability when critical
- DevSecOps
- hardware
- robotics and autonomy
- silicon and ASIC
- aerospace and satellite
- civil engineering
- privacy engineering
- functional safety
- application security

Human approval does not replace independent machine or specialist verification. Both are required where the route declares them.

## Conformance coverage

The activation fixture exercises all 27 explicit routes:

- 22 newly added specialist routes
- DevOps Engineering
- DevSecOps Engineering
- Embedded Engineering
- Civil Engineering
- Rust Systems Programming

For every case, CI verifies:

- selected team
- selected worker
- selected specialist
- specialist risk elevation
- primary provider family
- routine fallback provider family
- independent verifier provider family
- provider separation
- human approval for critical work
- absence of route warnings

CI also verifies that generic coding routes no longer silently route deployment or infrastructure context to a worker whose team ownership changed.

## Warning-baseline change

The configuration warning baseline removes only the worker bindings resolved by this activation:

- `civil_engineering`
- `devsecops`
- `embedded`
- `systems_engineering`

The former `systems_engineering` warning disappears because Rust now binds to `rust_systems_programming`, while the real Systems Engineering worker is `systems_requirements`.

All other known unresolved worker bindings remain visible.

## Preservation

Activation does not modify any specialist card. It links the already reviewed cards into active routing through separate allocation records.

The loader permits only bounded allocation metadata changes for existing specialists. Any attempt to override a role-card path or other protected field is a configuration error.

## Regulated evidence boundary

The evidence-backed freshness pilot remains exactly six specialists:

- Legal Operations
- Tax Strategist
- Loan Officer Assistant
- Compliance Auditor
- Civil Engineer
- Embedded Engineer

Activating 22 specialist routes does not authorize expansion of the evidence registry. The pilot must still satisfy its maintainability gate, including refresh cycles, stable authority resolution, mutation survival, ownership evidence, and controlled source or card change handling.

## Acceptance condition

This activation is acceptable only when the complete Reference Implementation CI passes:

- source compilation
- all automated tests
- schema parsing
- linked configuration validation
- the end-to-end reference example
- the 27-route activation conformance suite
