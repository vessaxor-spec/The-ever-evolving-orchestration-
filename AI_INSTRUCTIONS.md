# AI Instructions

Use this repository as the source of truth for model orchestration.

## Required read order

1. Read `routing.yaml`.
2. Read `models.yaml`.
3. Classify the task by type, risk, complexity, context size, tool needs, and verification needs.
4. Select the matching route.
5. Use the listed fallback only when the primary option is unavailable, constrained, or repeatedly unsuccessful.
6. Apply the verification rule before presenting consequential output.

## Core behavior

- Prefer capability fit over provider loyalty.
- Use Codex or the strongest available coding agent for implementation, debugging, testing, repository edits, and executable review.
- Use Gemini Pro for deep research, large-context synthesis, grounded comparison, and coding fallback when the coding agent is unavailable.
- Use Gemini Flash for fast extraction, classification, repository mapping, and multimodal triage.
- Use Claude Sonnet for architecture, planning, requirements analysis, semantic review, and adversarial challenge.
- Use Claude Opus only when ambiguity, risk, or unresolved complexity justifies the added cost.
- Use Haiku, Flash, Luna, or a suitable local model for simple and high-volume work.
- Use Terra for engineering execution, Sol for synthesis and difficult reasoning, and Luna for economical throughput when these profiles are available.

## Escalation rules

Escalate when any of the following is true:

- Two credible attempts fail.
- Tests remain failing or nondeterministic.
- Security, identity, payment, permissions, personal data, or destructive operations are involved.
- The selected models materially disagree.
- The task expands beyond its original scope.
- Confidence is insufficient for the consequence level.

## Verification rules

- Code must be checked through tests, static analysis, execution, or repository inspection where available.
- Research claims should be grounded in primary sources where practical.
- High-risk architecture should receive independent review.
- The same agent should not be the sole planner, executor, and verifier for consequential changes.

## Update rule

Model names and capabilities change. Treat entries in `models.yaml` as time-bound defaults. When a newer model is proposed, compare it against the role requirements and update the registry through a public pull request with evidence.
