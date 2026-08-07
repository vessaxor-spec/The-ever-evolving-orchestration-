# Empirical Verifier Calibration Evidence

## Status

This specification defines the first controlled collection protocol for empirical evidence about TEO's guarded live verifier.

It follows the calibration instrument defined in `docs/specification/verifier-calibration.md` and does not expand routing, live-execution scope, verification authority, or human approval authority.

The machine-readable policy is:

- `policy/verification/verifier-calibration-empirical.yaml`

## Purpose

The calibration harness can measure verifier decisions, but a reference control corpus is not independent human-rated ground truth.

This phase therefore separates three things:

1. the fixed public control corpus
2. independently produced human labels
3. repeated live verifier observations

Empirical metrics are evaluated against the independently reviewed human labels. The original control labels remain visible as a comparison and deterministic consistency check.

## Human labels first

Human labels must be completed before any live verifier observation is collected.

For every case:

- at least two independent reviewers provide a structured decision
- reviewers use opaque identifiers rather than names or email addresses
- reviewers attest that model observations were not shown to them
- reviewer disagreement requires adjudication
- the adjudicator must be distinct from the case reviewers
- all labels use the same rubric version as the control corpus
- all label timestamps include a UTC offset

A human label may not override an objectively machine-checkable deterministic invariant in the control corpus. If it does, the evidence set is rejected for investigation rather than silently treating the human rating as authoritative.

The human-label schema is:

- `reference/schemas/verifier-calibration-human-label.schema.json`

Human-label records do not repeat task or candidate-output content. They join to the fixed corpus by case ID.

## Direct calibration role

A calibration invocation is not a primary execution, retry, or fallback.

Empirical records therefore use the explicit role:

```text
calibration_direct
```

They do not persist `execution_role`, `retry_count`, or `fallback_used` fields.

This prevents direct verifier experiments from contaminating runtime execution-path evidence.

## Fixed live plan

The initial full evidence plan is:

- 8 fixed cases
- 3 verifier routes
- 3 runs per case per route
- 72 live verifier calls total

The routes are:

| Provider family | Model | Reasoning effort |
|---|---|---|
| Google | `gemini-3.6-flash` | `medium` |
| Anthropic | `claude-sonnet-5` | `medium` |
| OpenAI | `gpt-5.6-sol` | `medium` |

The three routes intentionally use three provider families. Variants from one provider do not satisfy provider-diversity evidence requirements.

## Verifier execution

The collector reuses TEO's existing guarded verifier adapters:

- `GoogleLiveVerifier`
- `AnthropicLiveVerifier`
- `OpenAILiveVerifier`

It constructs the same provider-neutral `LiveVerificationRequest` with:

- fixed task
- fixed candidate output
- fixed rubric
- low risk
- declared verification methods
- authorized provider/model/reasoning route

The collector does not create a separate judge prompt or a separate provider API contract.

Verifier infrastructure failure stops collection. It is not converted into a synthetic verifier judgment.

## Measurement record

Each successful empirical observation records:

- case ID
- provider family
- verifier model
- reasoning effort
- run ID
- offset-aware observation timestamp
- rubric version
- live-verification policy version
- empirical-policy version
- collector repository revision
- measured verifier duration
- normalized provider-reported input tokens
- normalized provider-reported output tokens
- structured verifier decision
- `calibration_direct` role

The collector requires provider-reported usage. Missing usage is a collection failure, not a zero-token observation.

For Anthropic, normalized input includes uncached input, cache-creation input, and cache-read input because Anthropic defines total input as their sum.

The empirical-observation schema is:

- `reference/schemas/verifier-calibration-empirical-observation.schema.json`

## Privacy and evidence minimization

Empirical observation records must not persist:

- original task text
- candidate output
- provider-native response payloads
- provider request or interaction identifiers
- credentials or authorization material
- connection mechanism
- reviewer names or email addresses

The task and candidate remain only in the fixed control corpus. Observation and human-label files join by case ID.

## Chronology invariant

Independent human labels must predate live observations.

The collector performs this check before any provider call. A label set whose completion timestamp is later than collection start is rejected before provider spend occurs.

Every observation is checked again before persistence.

## Collector revision invariant

One empirical evidence set must use one collector repository revision.

Collection can resume after interruption, but it refuses to append observations produced by another collector revision into the same evidence file.

This prevents code drift from becoming an unrecorded experimental variable.

## Resume behavior

The observation file is append-only JSONL under `.teo/` by default.

After each successful observation the collector flushes and fsyncs the record. On restart it reconstructs completed case/route/run identities and skips them rather than making duplicate provider calls.

A provider filter may be used for operational recovery, but the final evidence-readiness gate still requires the complete configured route set.

## Evaluation

Empirical evaluation uses independent human consensus as the gold decision set.

It reports the existing calibration metrics, including:

- exact status accuracy
- false-pass rate and opportunity count
- false-fail rate and opportunity count
- missed-human rate and opportunity count
- unnecessary-human rate and opportunity count
- criterion accuracy
- repeatability
- cross-verifier disagreement
- route and provider coverage
- observation window
- latency
- normalized token usage

Direct calibration observations are reported under:

```text
by_collection_path.calibration_direct
```

They are not represented as primary or fallback execution evidence.

The report also lists cases where independent human consensus differs from the initial reference-control label.

## Authority boundary

Neither complete evidence nor favorable metrics can set any of these values to true:

- `quality_claims_authorized`
- `scope_expansion_authorized`
- `routing_authority`
- `automatic_route_update`

After collection, an independent residual-risk review is still required. Any quality claim, route change, or broader live-verification scope requires explicit human acceptance through the normal repository governance path.

## Operator workflow

Show the plan without provider calls:

```text
python -m teo_reference.verifier_calibration_empirical --repo-root . plan
```

Validate independently collected human labels:

```text
python -m teo_reference.verifier_calibration_empirical --repo-root . labels \
  --human-labels .teo/runtime/verifier-calibration/human-labels.jsonl
```

Collect observations after labels are ready:

```text
python -m teo_reference.verifier_calibration_empirical --repo-root . collect \
  --human-labels .teo/runtime/verifier-calibration/human-labels.jsonl \
  --execute-live
```

The command requires an explicit `--execute-live` acknowledgement because it makes live provider calls.

The convenience connection bridge recognizes `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, and `OPENAI_API_KEY`. This is only one operator connection method. The library accepts the provider-neutral `ProviderConnection` interface, and connection method is not part of verifier route identity.

Evaluate completed evidence:

```text
python -m teo_reference.verifier_calibration_empirical --repo-root . evaluate \
  --human-labels .teo/runtime/verifier-calibration/human-labels.jsonl \
  --observations .teo/runtime/verifier-calibration/empirical-observations.jsonl \
  --output .teo/runtime/verifier-calibration/empirical-report.json
```

## CI boundary

CI validates the collection machinery with deterministic mock provider connections. CI does not call live providers and does not create empirical quality evidence.

A green CI run proves that the contracts, schemas, privacy boundaries, resume behavior, and evidence gates behave as tested. It does not prove that any live verifier is accurate.

## Capsule boundary

This protocol does not justify a new Capsule by itself.

A Capsule is appropriate only after the first real empirical evidence set is collected, independently reviewed, accepted, and preserved as a meaningful project milestone.
