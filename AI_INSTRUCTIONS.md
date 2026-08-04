# AI Instructions

Use this repository as the source of truth for orchestration.

## Required read order

1. Read `community/teams/README.md`.
2. Read `community/teams/mission-control.md`.
3. Read `policy/routing/team-routing.yaml`.
4. Read `community/workers/workers.yaml`.
5. Read `policy/routing/routing.yaml`.
6. Read `models.yaml`.
7. Classify the task by type, risk, complexity, context size, tool needs, and verification needs.
8. Route the task to a team and worker before selecting an implementation.
9. Resolve the worker to the best available implementation.
10. Apply fallback, escalation, and verification rules before presenting consequential output.

## Core routing rule

Route responsibilities, not brands.

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

A worker is not a model. A model is a replaceable implementation of the capabilities required by a worker.

## Core behavior

- Prefer capability fit over provider loyalty.
- Use Mission Control to interpret, dispatch, coordinate, and assemble results.
- Use the Planning Team for architecture, decomposition, sequencing, and tradeoff analysis.
- Use the Engineering Team for implementation, debugging, refactoring, tests, and tool execution.
- Use the Research Team for primary-source research, documentation, standards, and large-context synthesis.
- Use the Review Team for semantic, architectural, code, security, and risk review.
- Use the Verification Team to test claims, reproduce failures, confirm acceptance criteria, and record residual risk.
- Use specialist workers when the task belongs to a defined domain.

## Implementation preferences

- Use Codex Terra for engineering execution, debugging, testing, repository edits, and executable verification.
- Use Codex Sol for engineering architecture, difficult debugging strategy, cross-component planning, and repository-aware reasoning.
- Use Gemini Pro for deep research, large-context synthesis, grounded comparison, and coding fallback.
- Use Gemini Flash for fast extraction, classification, repository mapping, and multimodal triage.
- Use Claude Sonnet for architecture, planning, requirements analysis, semantic review, and adversarial challenge.
- Use Claude Opus only when ambiguity, risk, or unresolved complexity justifies the added cost.
- Use Haiku, Flash, Luna, or a suitable local model for simple and high-volume work.

## Escalation rules

Escalate when any of the following is true:

- Two credible attempts fail.
- Tests remain failing or nondeterministic.
- Security, identity, payment, permissions, personal data, or destructive operations are involved.
- Selected implementations materially disagree.
- The task expands beyond its original scope.
- Confidence is insufficient for the consequence level.

## Verification rules

- Code must be checked through tests, static analysis, execution, or repository inspection where available.
- Research claims should be grounded in primary sources where practical.
- High-risk architecture should receive independent review.
- The same worker and implementation should not be the sole planner, executor, reviewer, and verifier for consequential changes.

## Required dispatch record

Record:

- Task type
- Risk level
- Selected team
- Selected worker
- Required capabilities
- Selected implementation
- Fallback implementation
- Verification team
- Verification method
- Routing explanation

## Update rule

Model names and capabilities change. Treat entries in `models.yaml` as time-bound defaults. When a newer implementation is proposed, compare it against the worker requirements and update the registry through a public pull request with evidence.
