# TEO Team Architecture

TEO routes work to responsibilities before selecting workers, specialists, capabilities, and implementations.

```text
Task
  |
  v
Mission Control
  |
  v
Team
  |
  v
Worker
  |
  v
Optional Specialist
  |
  v
Capability
  |
  v
Implementation
  |
  v
Independent Verification
```

Models and providers are replaceable implementations. Teams and workers define stable responsibilities and decision boundaries. Specialists narrow domain expertise without replacing the owning team or worker.

## Current control-plane roster

The active executable registries currently resolve to:

- **10 teams**
- **84 workers**
- **81 specialists**
- **4 Mission Control workers**

These counts are derived from the same `ConfigBundle` composition used by the reference router rather than from a manually maintained subset.

## Active teams

| Team | Primary ownership | Typical handoff |
|---|---|---|
| [Mission Control](mission-control.md) | intake, classification, dispatch, coordination, authority boundaries, verification assignment, final assembly | selects and coordinates all other teams |
| [Planning Team](planning-team.md) | decomposition, architecture, sequencing, tradeoffs, acceptance criteria | hands executable plans to Engineering and review requests to Review |
| [Engineering Team](engineering-team.md) | implementation, debugging, testing, runtime validation, technical handoff | hands evidence and changes to Review and Verification |
| Platform and Reliability | shared platforms, distributed systems, database reliability, networking, performance, FinOps, SRE, MLOps, DevOps, DevSecOps | supports Engineering, Mission Control, Review, and Verification |
| Systems Engineering | requirements, interfaces, baselines, integration strategy, lifecycle coherence, verification and validation planning | coordinates cross-system technical boundaries |
| Physical Systems | hardware, embedded, civil, robotics, silicon, aerospace, manufacturing, physical integration | coordinates with Systems Engineering, Assurance, Review, and Verification |
| [Research Team](research-team.md) | source collection, comparison, synthesis, uncertainty, analytics, user and market research | hands evidence to Planning, Review, or Verification |
| Assurance | privacy engineering, functional safety, formal methods, application security | provides technical assurance evidence for independent review and verification |
| [Review Team](review-team.md) | challenge, risk review, code review, compliance review, requirements alignment, finding classification | returns required changes or requests verification |
| [Verification Team](verification-team.md) | independent checks, acceptance status, residual risk, release recommendation | returns accept, revise, reject, or escalate |

## Mission Control

Mission Control owns orchestration and coordination. It does not absorb specialist execution or bypass the accountable team.

Its active workers are:

| Worker | Responsibility |
|---|---|
| `orchestration` | governed multi-agent pipelines, handoffs, checkpoints, recovery, and termination |
| `operations` | operational controls, vendors, processes, approvals, dependencies, and accountable execution |
| `project_delivery` | scope, capacity, critical path, risk, change control, and delivery commitments |
| `incident_response` | severity, response roles, cadence, timeline, communications coordination, resolution readiness, and blameless learning |

## Standard team contract

Every team definition follows the same operating structure where applicable:

1. **Mission**: the durable responsibility owned by the team
2. **Inputs**: the information, evidence, access, and constraints required to begin
3. **Responsibilities**: the work the team is accountable for performing
4. **Boundaries**: actions the team must not take or claims it must not make
5. **Required outputs**: the artifacts and decision record handed to the next team
6. **Success criteria**: observable conditions that define satisfactory completion
7. **Escalation triggers**: conditions that require Mission Control, specialist, or human intervention
8. **Independence**: separation requirements for consequential work
9. **Preferred implementations**: current implementation choices, subject to routing policy and availability

## Handoff rules

- Mission Control preserves the original intent and owns the dispatch record.
- Planning defines acceptance criteria before consequential execution.
- Engineering reports actual results, including failed and unavailable checks.
- Platform and Reliability owns shared operational foundations without absorbing application ownership.
- Systems Engineering maintains cross-system requirements, interfaces, integration, and lifecycle coherence.
- Physical Systems owns engineering whose correctness depends on physical behavior and real-world integration.
- Research separates facts, source interpretations, quantitative evidence, and inference.
- Assurance produces technical assurance evidence but does not self-approve consequential claims.
- Review classifies findings and does not approve unresolved blockers silently.
- Verification follows evidence and records every material criterion as passed, failed, skipped, unavailable, or inconclusive.
- Consequential work must not use the same implementation as the sole planner, executor, reviewer, and verifier.

## Specialist roster

TEO currently contains **81 active preserved specialist role cards** with deterministic Team -> Worker -> Specialist spawn paths.

The authoritative base registry is [`community/specialists/specialists.yaml`](../specialists/specialists.yaml). Active additive allocations are defined in [`community/specialists/principal-engineering-active.yaml`](../specialists/principal-engineering-active.yaml) and [`community/specialists/workforce-expansion-active.yaml`](../specialists/workforce-expansion-active.yaml).

Specialists narrow domain expertise. They do not replace the owning team, bypass Mission Control, select their own authority, reduce worker responsibility, or approve their own consequential work.

## Worker registry

The executable worker registry currently resolves to **84 workers** after composing the canonical worker registry with the active additive worker extensions and controlled overrides loaded by the reference implementation.

The canonical base registry is [`community/workers/workers.yaml`](../workers/workers.yaml). Active worker extensions include Mission Control, Research, Review, Systems Engineering, Platform and Reliability, Physical Systems, Assurance, principal-engineering, and specialist-completion worker definitions.

Worker definitions establish stable routing responsibilities. The corresponding specialist role cards remain authoritative for domain methodology, boundaries, responsibilities, and output requirements.

## Routing authority

Team dispatch order, task routes, worker bindings, specialist spawn routes, required dispatch fields, and implementation resolution are defined by the active policies under [`policy/routing/`](../../policy/routing/).

Implementation selection remains governed by responsibility, capability fit, effective risk, current model evidence, tool access, availability, fallback requirements, and independent verification.
