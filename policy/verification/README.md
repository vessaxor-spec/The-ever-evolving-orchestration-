# Verification Policy

Verification determines whether a plan, execution, research result, review response, or release satisfies the original requirements with adequate evidence.

Verification is not a restatement of the executor's confidence. It is a separate decision based on acceptance criteria, observed results, risk, and unresolved uncertainty.

## Required record

Every verification record must identify:

- the original task and authorized scope
- the acceptance criteria
- the checks performed
- the evidence produced
- the checks not performed and why
- residual risk
- independence status
- the final recommendation

Every material criterion must be recorded as one of:

- `passed`
- `failed`
- `skipped`
- `unavailable`
- `inconclusive`

Silence is not a passing result.

## Final recommendations

Verification concludes with one of:

- **accept**: all required criteria passed and residual risk is within the authorized tolerance
- **revise**: correctable failures or missing evidence remain
- **reject**: the result does not satisfy the task or creates unacceptable risk
- **escalate**: human approval, specialist judgment, or additional evidence is required

## Risk depth

The minimum verification depth is defined in `policy/routing/routing.yaml`.

### Low risk

Require output validation.

### Medium risk

Require output validation and targeted review.

### High risk

Require an independent verifier, an explicit reasoning summary, evidence or test results, and a rollback or recovery plan.

### Critical

Require independent multi-agent review, executable verification, human approval, an audit trace, and a rollback plan.

## Independence

Consequential work must not use the same implementation as the sole planner, executor, reviewer, and verifier.

Independence may be satisfied through:

- a separate implementation
- a separate specialist worker using independent evidence
- an executable test process that does not rely on the executor's claim
- human approval where required

Changing only the role label while preserving the same unchecked reasoning does not provide meaningful independence.

## Evidence standards

Verification evidence may include:

- targeted and regression test results
- reproducible failure and fix demonstrations
- static analysis or build results
- source citations and contradiction checks
- before-and-after measurements
- interface or contract comparisons
- migration and rollback tests
- release artifacts and checksums
- explicit human approval records

Evidence must be relevant to the acceptance criterion it supports.

## Stop conditions

Verification must not return `accept` when:

- required evidence is unavailable
- a required check failed
- the scope expanded beyond authorization
- critical assumptions remain unresolved
- independence requirements were not satisfied
- rollback or recovery requirements were omitted for high-risk work

## Routing validation

Phase 3 routing validation uses this policy to confirm that every route names a verification team, assigns adequate controls, preserves independence where required, and can produce a complete verification record.
