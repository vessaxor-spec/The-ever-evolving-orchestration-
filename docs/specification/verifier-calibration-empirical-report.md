# Route-Specific Empirical Calibration Report

## Purpose

Aggregate verifier metrics are insufficient for acceptance because one strong verifier route can hide a weak route.

The final empirical report therefore evaluates each configured verifier route independently as well as reporting the aggregate evidence set.

The implementation is:

- `teo_reference.verifier_calibration_empirical_report`

## Route-specific metrics

For each provider/model/reasoning route, the report calculates the same fixed metrics used by the aggregate calibration evaluator, including:

- total observations
- exact status accuracy
- false-pass count, opportunities, and rate
- false-fail count, opportunities, and rate
- missed-human count, opportunities, and rate
- unnecessary-human count, opportunities, and rate
- criterion accuracy
- repeatability
- disagreement evidence
- observation window
- duration
- normalized input/output usage

Direct calibration remains labeled under `by_collection_path.calibration_direct`. It is never emitted as primary, retry, or fallback execution evidence.

## Completeness rule

The route-specific report compares the observed route set with the exact verifier routes configured by `policy/verification/verifier-calibration-empirical.yaml`.

If a configured route is absent:

- `route_specific_evidence_complete` is false
- `evidence_readiness.data_requirements_met` is forced false

Aggregate accuracy cannot override this failure.

## Authority boundary

Route-specific metrics remain evidence only.

The report keeps quality claims, scope expansion, routing authority, and automatic route updates disabled. Independent residual-risk review and explicit human acceptance remain required after a complete evidence package exists.

## Operator command

Build the final route-specific report with:

```text
python -m teo_reference.verifier_calibration_empirical_report --repo-root . \
  --human-labels .teo/runtime/verifier-calibration/human-labels.jsonl \
  --observations .teo/runtime/verifier-calibration/empirical-observations.jsonl \
  --output .teo/runtime/verifier-calibration/empirical-report.json
```

The lower-level empirical evaluator remains useful for collection diagnostics. Acceptance review should use the route-specific report so provider/model weaknesses cannot be averaged away.
