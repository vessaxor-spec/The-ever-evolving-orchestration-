# TEO Team Architecture

TEO routes work to responsibilities before selecting workers, capabilities, and implementations.

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
Capability
  |
  v
Implementation
  |
  v
Verification
```

Models and providers are replaceable implementations. Teams and workers define stable responsibilities and decision boundaries.

## Core teams

| Team | Primary ownership | Typical handoff |
|---|---|---|
| [Mission Control](mission-control.md) | intake, classification, dispatch, coordination, verification assignment, final assembly | selects and coordinates all other teams |
| [Planning Team](planning-team.md) | decomposition, architecture, sequencing, tradeoffs, acceptance criteria | hands executable plans to Engineering and review requests to Review |
| [Engineering Team](engineering-team.md) | implementation, debugging, testing, runtime validation, technical handoff | hands evidence and changes to Review and Verification |
| [Research Team](research-team.md) | source collection, comparison, synthesis, uncertainty, traceability | hands evidence to Planning, Review, or Verification |
| [Review Team](review-team.md) | challenge, risk review, requirements alignment, finding classification | returns required changes or requests verification |
| [Verification Team](verification-team.md) | independent checks, acceptance status, residual risk, release recommendation | returns accept, revise, reject, or escalate |

## Standard team contract

Every core team definition contains the same operating sections:

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
- Research separates facts, source interpretations, and inference.
- Review classifies findings and does not approve unresolved blockers silently.
- Verification follows evidence and records every material criterion as passed, failed, skipped, unavailable, or inconclusive.
- Consequential work must not use the same implementation as the sole planner, executor, reviewer, and verifier.

## Specialist roster

TEO includes a public roster of 56 specialist role cards created by **Sylvester Roxas** and integrated from the Roxas-Legion specialist system.

| Primary team | Specialists |
|---|---:|
| Mission Control | 4 |
| Planning Team | 17 |
| Engineering Team | 13 |
| Research Team | 10 |
| Review Team | 10 |
| Verification Team | 2 |

The complete roster, creator attribution, worker bindings, supporting teams, risk profiles, and individual role cards are available in [`community/specialists/`](../specialists/).

Specialists narrow domain expertise. They do not replace the core team, bypass Mission Control, select their own authority, or approve their own consequential work.

## Specialist workers

Core teams dispatch specialist workers according to task context. The original stable worker set includes:

- Architecture
- Backend
- Frontend
- Mobile
- DevOps
- Infrastructure
- Performance
- Security
- Database
- Data Engineering
- AI Engineering
- Documentation
- QA
- Accessibility
- Release

Worker responsibilities and capability mappings are defined in [`community/workers/workers.yaml`](../workers/workers.yaml).

The extended domain-specialist bindings are defined in [`community/specialists/specialists.yaml`](../specialists/specialists.yaml).

## Routing authority

Team dispatch order, task routes, required dispatch fields, and implementation resolution are defined in [`policy/routing/team-routing.yaml`](../../policy/routing/team-routing.yaml).

Implementation selection remains governed by capability fit, task risk, context, cost, latency, tool access, availability, and verification requirements.
