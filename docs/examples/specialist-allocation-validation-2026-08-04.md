# Specialist Allocation Validation

**Validation date:** 2026-08-04  
**Source roster:** Roxas-Legion specialist roster  
**Creator:** Sylvester Roxas  
**TEO registry:** `community/specialists/specialists.yaml`

## Result

The public integration contains 56 unique specialists. Every specialist has:

- one primary TEO team
- zero or more supporting teams
- one worker binding
- one risk profile
- one public Markdown role card
- creator attribution to Sylvester Roxas
- a required handoff
- verification requirements
- authority and escalation boundaries

No specialist is unassigned.

## Allocation totals

| Primary team | Specialists |
|---|---:|
| Mission Control | 4 |
| Planning Team | 17 |
| Engineering Team | 13 |
| Research Team | 10 |
| Review Team | 10 |
| Verification Team | 2 |
| **Total** | **56** |

## Non-obvious allocations

### Technical Writer to Verification

The Technical Writer is assigned to Verification because the role validates documentation structure, links, examples, and technical accuracy. Research and Engineering remain supporting teams for content and executable behavior.

### UX Designer to Review

The UX Designer is assigned to Review because the role challenges usability, information architecture, accessibility, design-system consistency, and handoff quality. Planning, Research, Engineering, and Verification may support the work.

### Security Engineer to Review

The Security Engineer is assigned to Review because TEO's stable security worker is review-owned. Engineering performs authorized remediation and implementation, while Verification confirms the result independently.

### Customer Success to Planning

Customer Success is assigned to Planning because the role designs onboarding, support, health, retention, escalation, and knowledge programs. Research supplies customer evidence and Mission Control coordinates active escalations.

### Workflow Optimizer to Engineering

The Workflow Optimizer is assigned to Engineering because the role moves beyond analysis into automation selection and future-state workflow implementation. Planning defines the target state and Verification measures the outcome.

## High-consequence controls

Critical roles include security, compliance, legal, financial, lending, tax, civil engineering, blockchain, and incident-response specialists.

Their role cards require:

- independent specialist or executable verification
- current and traceable evidence
- human approval for consequential decisions
- auditability
- rollback, recovery, or remediation planning where applicable

Security specialists are explicitly limited to lawful, authorized, defensive work within a declared scope.

Regulated-domain specialists provide decision support and do not replace licensed professionals.

## Routing conclusion

The specialist roster extends domain coverage without changing TEO's authority chain:

```text
Task
  -> Mission Control
  -> Team
  -> Worker
  -> Optional Specialist
  -> Capability
  -> Implementation
  -> Verification
```

Specialists cannot bypass Mission Control, replace the owning team, select their own authority, or become the sole planner, executor, reviewer, and verifier for consequential work.

**Validation status:** accepted
