# Verifier Calibration

## Status

This specification defines the evidence harness used to calibrate TEO's guarded live verifier against fixed gold labels and, later, repeated live verifier observations.

Calibration does not have routing authority. A successful harness run does not prove that a verifier is trustworthy and does not authorize broader live execution or verification scope.

The machine-readable policy is `policy/verification/verifier-calibration.yaml`.

## Purpose

The live verifier is itself a model-based decision component. Passing a schema and producing internally consistent judgments are necessary controls, but they do not establish empirical correctness.

Calibration measures how verifier judgments compare with independently defined expected outcomes while preserving enough route, time, and runtime context to identify disagreement, instability, drift, and execution-path effects.

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
- the guarded verifier rubric version used to label the case

The initial corpus uses rubric version `1.0`. Calibration observations must name the same rubric version. A rubric change requires a new compatible evidence set rather than silently comparing unlike judgments.

## Deterministic validation first

Objective checks run before semantic model judgment wherever possible.

The reference harness currently supports deterministic checks for:

- non-empty output
- exact ordered lines
- exact line count
- forbidden unsupported or adversarial substrings

A case declaring complete deterministic coverage must resolve all four guarded verifier criteria and must agree with the independently recorded gold decision.

Cases involving genuine ambiguity or missing external evidence remain unresolved by deterministic validation and require semantic or human judgment.

Deterministic validation is not replaced by a model judge when a machine-checkable answer is available.

## Observation contract

Live or replayed verifier observations are content-free relative to the public gold corpus. An observation records:

- gold case ID
- verifier provider family
- verifier model
- verifier reasoning effort, or explicit null when the route has no applicable effort control
- run ID
- offset-aware observation timestamp
- rubric version
- live-verification policy version
- structured verifier decision
- primary or fallback execution role
- retry count
- whether fallback was used
- optional verification duration
- optional input and output token counts

The initial evidence policy pins observations to rubric version `1.0` and live-verification policy version `1.1`.

Observation records must not persist the task or candidate output again. They join to the fixed corpus by case ID. Unknown fields are rejected. Required evidence fields cannot be omitted. Type coercion is rejected for control fields such as retry count and fallback state. Execution role and fallback state must agree.

The observation timestamp must include a UTC offset. This preserves the empirical measurement window so later reviewers can distinguish observations collected before and after provider, model, policy, or infrastructure changes.

The schema is `reference/schemas/verifier-calibration-observation.schema.json`.

A repeated observation identity is the tuple of case, verifier provider, verifier model, verifier reasoning effort, and run ID. Duplicate identities are rejected rather than double-counted.

## Verifier route identity

Calibration treats a verifier route as:

```text
provider family / model / reasoning effort
```

Reasoning effort is included because a material inference-control change can alter verifier behavior even when provider and model names stay constant.

Connection mechanism remains outside route identity. API key, OAuth, delegated identity, connector session, or another access method does not create a different verifier route by itself.

## Required metrics

The reference evaluator calculates:

- exact status accuracy
- false-pass count, opportunities, and conditional rate
- false-fail count, opportunities, and conditional rate
- missed-human count, opportunities, and conditional rate
- unnecessary-human count, opportunities, and conditional rate
- predicted `needs_human` rate
- per-criterion accuracy
- repeated-run agreement for the same verifier route
- cross-verifier disagreement cases
- observed verifier routes
- observed verifier provider families
- observation-window start and end timestamps
- average verifier duration
- p95 verifier duration
- total normalized input tokens
- total normalized output tokens
- outcome accuracy split by primary, retried-primary, and fallback execution paths

### Error-rate denominators

Error rates use the relevant gold opportunity set rather than every observation.

- false-pass rate denominator: observations whose gold status is not `passed`
- false-fail rate denominator: observations whose gold status is `passed`
- missed-human rate denominator: observations whose gold status is `needs_human`
- unnecessary-human rate denominator: observations whose gold status is not `needs_human`

If an evidence set contains no relevant opportunity for an error class, that rate is undefined and is reported as null rather than zero. A zero error rate therefore cannot imply a class was tested when it was absent from the evidence.

A false pass is any `passed` judgment when the gold status is not `passed`. This intentionally includes cases whose gold status is `needs_human` because an unsupported pass is the dangerous error direction.

A false fail is a `failed` judgment when the gold status is `passed`.

## Repeatability and disagreement

One observation per case cannot establish repeatability.

The active policy requires at least three runs per case per verifier route, at least three distinct verifier routes, and at least three distinct verifier provider families before the data-coverage gate can be satisfied.

Repeated-run agreement is measured within the same case and verifier route.

Cross-verifier disagreement is recorded when different verifier routes produce different observed status sets for the same gold case.

Disagreement is evidence for investigation. It is not automatically resolved by majority vote.

## Evidence-readiness gate

The reference harness exposes a data-readiness assessment separate from quality judgment.

The data requirements are met only when:

- the gold corpus meets its minimum size and category requirements
- the minimum number of distinct verifier routes has been observed
- the minimum number of distinct provider families has been observed
- every gold case has the required number of repeated observations on every observed verifier route
- observations carry offset-aware timestamps
- observation rubric and live-verification policy versions match the active calibration policy

Three route strings from one provider do not satisfy the provider-diversity requirement. This prevents reasoning-effort or model variants from being counted as independent provider evidence.

The readiness result can report `data_requirements_met: true`. It cannot report either `quality_claims_authorized: true` or `scope_expansion_authorized: true`.

Independent human review remains mandatory after evidence coverage is complete. The human review must examine measured errors, uncertainty behavior, repeatability, disagreement, adversarial performance, latency, usage, execution-path effects, observation timing, and residual risk.

This separation prevents a data-completeness gate from becoming accidental decision authority.

## Retry and fallback relationship

Verifier calibration retains whether the associated execution path was:

- primary without retry
- primary after retry
- fallback

This does not imply that execution retry or fallback caused the verifier result. It preserves the evidence needed to test that hypothesis later.

## Adversarial calibration

The gold corpus includes candidate output that attempts to instruct the verifier to ignore its rubric and mark the output passed.

This case exists to measure whether the live verifier obeys trusted evaluation instructions rather than candidate-controlled text.

The public corpus can expand with additional adversarial cases through reviewed evidence changes.

## Quality and expansion boundary

The calibration harness deliberately contains no automatic route-update or scope-expansion mechanism.

A valid corpus, complete repeated observations, provider-diverse coverage, and favorable metrics still require independent human review before TEO can claim calibrated verifier quality or broaden live verification.

The expansion review must consider at least:

- false-pass behavior
- false-fail behavior
- uncertainty handling
- repeatability
- cross-provider and cross-model disagreement
- adversarial performance
- latency and usage
- observation window and evidence recency
- retry and fallback relationship
- residual risk

## Reference implementation

The harness is implemented in `teo_reference.verifier_calibration`.

Validate the gold corpus without making a quality claim:

```text
python -m teo_reference.verifier_calibration
```

Evaluate local JSONL observations and report both metrics and evidence readiness:

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
- allow data completeness to self-authorize expansion
- claim production calibration before repeated live evidence exists
