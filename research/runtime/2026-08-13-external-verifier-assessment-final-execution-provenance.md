# External Independent Technical Verifier Assessment — Final Execution Provenance

Date: 2026-08-13
Status: bounded post-calibration external verification evidence
Repository baseline assessed: `2bd216c6ea5c473338d0b0bc098894663717efe3`
Verifier classification: External Independent Technical Verifier, evidence authority only
Authority effect: none
Live-scope effect: none
Routing effect: none
Qualified-human approval effect: none

## Purpose

This record preserves the first substantive assessment performed after the external verifier completed the paired positive-control and negative-control calibration recorded in `2026-08-13-external-verifier-calibration.md`.

The verifier output remains untrusted external evidence until reconciled against current repository truth. This record therefore separates the external verdict from TEO Mission Control corroboration.

## Verification target

The verifier was asked to independently attempt to falsify the current normative Final Execution Provenance Projection and determine whether it substantiates the documented invariant:

> Routing intent says what TEO chose; Route-Outcome Evidence says what TEO observed; final execution provenance may report only the validated successful active route.

The minimum inspection surface included:

- `docs/specification/final-execution-provenance.md`
- `reference/implementations/python/src/teo_reference/final_execution_provenance.py`
- `reference/implementations/python/src/teo_reference/schemas.py`
- `reference/implementations/python/src/teo_reference/route_outcome.py`
- `reference/implementations/python/src/teo_reference/cli.py`
- `reference/schemas/final-outcome.schema.json`
- `tests/test_final_execution_provenance.py`

The verifier was instructed to treat documentation, tests, commit messages, and prior TEO conclusions as untrusted claims and to inspect whether the implementation and tests actually falsify the load-bearing invariants.

## External verdict

`PASS`

## External evidence summary

The verifier reported that `attach_execution_provenance`:

1. revalidates supplied Route-Outcome Evidence through `RouteOutcomeRecord.from_dict`, including JSON Schema validation, route semantic validation, and integrity SHA-256 recomputation;
2. requires `active_route_role` to identify a primary or fallback route whose execution status is `succeeded`;
3. requires the active dispatch to match the final outcome dispatch;
4. requires the final outcome execution status to be `succeeded`;
5. requires active-route model identity to match the final outcome selected model;
6. requires active-route verifier model identity to match the final outcome verifier model;
7. requires verification provenance to belong to the active dispatch;
8. requires Route-Outcome verification status to equal the final outcome verification status;
9. requires final disposition to map consistently to final outcome status;
10. refuses replacement when different execution provenance is already attached; and
11. constructs execution provenance from the validated active route rather than from original routing intent or verifier identity.

The verifier also confirmed the fallback case reports the successful fallback provider/model rather than a failed primary, and that `FinalOutcome.to_dict()` preserves legacy serialization by omitting `execution_provenance` when absent.

The CLI path was assessed as ordinary finalization followed by optional route-outcome attachment and strict final-outcome schema validation, so mismatched route evidence is subject to the same attachment checks before emission.

## External adversarial coverage assessment

The verifier independently examined the current final-execution-provenance test suite and identified executable negative coverage for:

- tampered Route-Outcome content and integrity/provider drift;
- failed-primary versus successful-fallback active-route selection;
- active dispatch mismatch;
- selected-model mismatch;
- verifier-model mismatch;
- final-status versus disposition mismatch;
- verification-status mismatch;
- silent replacement of already attached provenance;
- legacy serialization compatibility;
- strict projected FinalOutcome schema compatibility; and
- the successful CLI attachment path.

The verifier concluded that these tests exercise the primary mutation classes declared by the specification rather than only confirming happy-path equality.

## External residual findings

The PASS was explicitly bounded by the following residual gaps:

- no dedicated unit test for rejecting a `FinalOutcome` whose `execution_status` is `failed`, although the implementation contains the check;
- no dedicated unit tests for rejecting `execution_failed`, `abandoned`, or `verification_missing` dispositions at projection time, although the disposition map rejects them;
- no negative CLI test using a mismatched `--route-outcome` record;
- SHA-256 provides content integrity, not origin authentication, non-repudiation, or protection against wholesale substitution of a different internally consistent record;
- the module cannot itself prove that downstream consumers never misuse read-only provenance as routing or host-action authority; and
- concurrent or out-of-order attachment remains bounded only by the existing different-provenance replacement guard in this process-local surface.

The verifier did not treat these residuals as contradictions of the documented invariant because the specification does not claim cryptographic origin authentication or broader production trust guarantees.

## TEO Mission Control corroboration

TEO Mission Control independently checked the central assessment against the same current repository baseline.

The normative projection code revalidates Route-Outcome Evidence before projection, requires a successful active route, binds active dispatch, execution status, active model, verifier model, verification dispatch provenance, verification status, and final disposition, and rejects replacement by different already-attached provenance.

`RouteOutcomeRecord.from_dict` independently performs strict schema validation, route-semantic validation, and recomputation of the stored content-integrity hash before accepting the record. Its semantic checks bind active-route success, fallback semantics, telemetry/dispatch lineage, verification provenance, and disposition/verification consistency.

The current tests contain the negative cases identified by the external verifier for tamper, fallback selection, dispatch/model/verifier/status mismatch, replacement, compatibility, and schema validity. The verifier's observation that the CLI suite has only a positive attachment case is also accurate.

The specification itself explicitly states that the Route-Outcome digest is a content-integrity identifier rather than a cryptographic signature or identity-authentication mechanism, so the verifier correctly did not reinterpret that limitation as a failed invariant.

Mission Control therefore corroborates the external `PASS` for the declared optional read-only provenance projection scope.

## Evidence-quality interpretation

This is the first substantive post-calibration assessment from the external verifier.

It strengthens confidence that the calibration result generalizes beyond the two prepared controls because the verifier:

- attempted falsification against a current normative feature;
- identified both supporting evidence and concrete coverage gaps;
- preserved scope boundaries rather than converting a PASS into a broader trust claim; and
- distinguished content integrity from source authentication.

The assessment does not grant automatic acceptance to future verifier outputs. Each future consequential verdict remains subject to TEO-side evidence reconciliation and, where appropriate, independent reproduction.

## Authority and progress effect

No runtime, schema, policy, routing, provider, specialist, live-scope, release, or qualified-human authority changes follow from this record.

The `Verifier calibration evidence` Progress Tracker workstream remains at 70%. This assessment adds useful adversarial and independent evidence but does not by itself complete the broader repeatability, disagreement, route-specific, empirical, or optional human-calibration program.

## Follow-up evidence opportunities

The verifier identified three inexpensive test-evidence improvements that may be considered separately from this verification record:

1. explicit failed-execution rejection coverage for projection;
2. explicit unsupported-disposition rejection coverage; and
3. a negative CLI test proving mismatched `--route-outcome` fails closed.

These are evidence-hardening opportunities, not demonstrated production-control defects, because the corresponding rejection logic already exists in the implementation.
