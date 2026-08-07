# Verifier Calibration

## Status

This specification defines the evidence harness used to calibrate TEO's guarded live verifier against fixed gold labels and, later, repeated live verifier observations.

Calibration does not have routing authority. A successful harness run does not prove that a verifier is trustworthy and does not authorize broader live execution or verification scope.

The machine-readable policy is `policy/verification/verifier-calibration.yaml`.

## Purpose

The live verifier is itself a model-based decision component. Passing a schema and producing internally consistent judgments are necessary controls, but they do not establish empirical correctness.

Calibration measures how verifier judgments compare with independently defined expected outcomes.

## Gold corpus

The public reference corpus is `reference/datasets/verifier-calibration-gold.yaml`.

It contains at least one case from each required class:

- correct
- subtly wrong
- incomplete
- wrong format
- unsupported claim
- ambiguous
- unverifiable without missing evidence
- adversarial verifier-injection attempt

Each case preserves:

- original task
- candidate output
- expected overall status
- expected criterion verdicts
- expected human reason when applicable
- deterministic validation rules where the result is objectively machine-checkable

## Deterministic validation first

Objective checks run before semantic model judgment wherever possible.

The reference harness currently supports deterministic checks for:

- non-empty output
- exact ordered lines
- exact line count
- forbidden unsupported or adversarial substrings

A case declaring complete deterministic coverage must resolve all four guarded verifier criteria and must agree with the independently recorded gold decision.

Cases involving genuine ambiguity or missing external evidence remain unresolved by deterministic validation and require semantic or human judgment.

## Observation contract

Live or replayed verifier observations are content-free relative to the public gold corpus. An observation records:

- gold case ID
- verifier provider family
- verifier model
- run ID
- structured verifier decision
- primary or fallback execution role
- retry count
- whether fallback was used
- optional verification duration
- optional input and output token counts

Observation records must not persist the task or candidate output again. They join to the fixed corpus by case ID.

The schema is `reference/schemas/verifier-calibration-observation.schema.json`.

## Required metrics

The reference evaluator calculates:

- exact status accuracy
- false-pass count and rate
- false-fail count and rate
- missed-human count and rate
- unnecessary-human count and rate
- predicted `needs_human` rate
- per-criterion accuracy
- repeated-run agreement for the same verifier route
- cross-verifier disagreement cases
- average verifier duration
- p95 verifier duration
- total normalized input tokens
- total normalized output tokens
- outcome accuracy split by primary, retried-primary, and fallback execution paths

A false pass is any `passed` judgment when the gold status is not `passed`. This intentionally includes cases whose gold status is `needs_human` because an unsupported pass is the dangerous error direction.

A false fail is a `failed` judgment when the gold status is `passed`.

## Repeatability

One observation per case cannot establish repeatability.

The active policy requires at least three runs per case per verifier and at least three distinct verifier routes before a calibration evidence package can be considered for scope-expansion review.

Repeated-run agreement is measured within the same case, provider family, and verifier model.

Cross-verifier disagreement is recorded when different verifier identities produce different overall statuses for the same gold case.

## Retry and fallback relationship

Verifier calibration retains whether the associated execution path was:

- primary without retry
- primary after retry
- fallback

This does not imply that execution retry or fallback caused the verifier result. It preserves the evidence needed to test that hypothesis later.

## Adversarial calibration

The gold corpus includes candidate output that attempts to instruct the verifier to ignore its rubric and mark the output passed.

This case exists to measure whether the live verifier obeys the trusted evaluation instructions rather than candidate-controlled text.

The public corpus can expand with additional adversarial cases through reviewed evidence changes.

## Quality and expansion boundary

The calibration harness deliberately contains no automatic route-update or scope-expansion mechanism.

A valid corpus plus favorable metrics still requires independent human review before TEO can claim calibrated verifier quality or broaden live verification.

The expansion review must consider at least:

- false-pass behavior
- false-fail behavior
- uncertainty handling
- repeatability
- cross-provider/model disagreement
- adversarial performance
- latency and usage
- retry/fallback relationship
- residual risk

## Reference implementation

The harness is implemented in `teo_reference.verifier_calibration`.

Validate the gold corpus without making a quality claim:

```text
python -m teo_reference.verifier_calibration
```

Evaluate local JSONL observations:

```text
python -m teo_reference.verifier_calibration --observations .teo/runtime/calibration-observations.jsonl
```

Local runtime evidence belongs under `.teo/` and is repository-ignored by default.

## Non-goals

This phase does not:

- call provider APIs automatically in CI
- treat model output as ground truth
- set a universal quality threshold
- optimize routing from calibration results
- authorize high or critical live verification
- replace qualified-human approval
- claim production calibration before repeated live evidence exists
