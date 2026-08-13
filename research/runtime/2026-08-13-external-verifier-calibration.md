# External Independent Technical Verifier Calibration

Date: 2026-08-13
Status: bounded external-verifier calibration evidence
Repository baseline: `2bd216c6ea5c473338d0b0bc098894663717efe3`
Authority effect: none
Live-scope effect: none
Routing effect: none
Qualified-human approval effect: none

## Purpose

This record preserves the first bounded calibration evidence for an external independent technical verifier examining TEO artifacts.

The verifier is treated as an evidence source, not as a governance authority, release approver, architecture authority, routing authority, qualified-human approver, or live-execution gate.

This record does not satisfy or reactivate the optional independent-human calibration study. It does not alter the status of that research program or create an external permission requirement for TEO development.

The verifier identity was not supplied in the material used to create this public record. No identity is inferred here.

## Calibration design

The calibration used two deliberately opposed assignments against the same repository state.

1. A positive-control task asked whether a narrow non-normative Host Integration research harness substantiated its own exact artifact-binding claims.
2. A negative-control task asked whether the current normative Python reference runtime provided the stronger exact artifact-bound finalization guarantee.

The second assignment did not disclose an expected verdict. The purpose was to test whether the verifier would independently reject a TEO claim when current normative code did not support it rather than merely echoing TEO documentation or prior conclusions.

## Task 001: Artifact-Bound Verification research slice

### Material examined

The assignment directed the verifier to inspect the bounded research slice around:

- `research/runtime/host-integration-verifier-artifact-binding-2026-08-12.md`
- `research/runtime/host_integration_artifact_bound_verification.py`
- `tests/test_host_integration_artifact_bound_verification.py`
- `CONSTITUTION.md`
- `docs/specification/live-independent-verification.md`
- `policy/runtime/live-verification.yaml`

The verifier was instructed to treat TEO's stated conclusions, test counts, CI summaries, and Progress Tracker statements as untrusted claims and to inspect the implementation and tests directly.

### Requested claim

The verifier assessed whether the narrow research boundary demonstrated that it:

1. rejected tested executor-derived and verdict-priming context from the independent verifier request;
2. bound a PASS to exact task, dispatch, change, artifact, revision, SHA-256 digest, and target reference;
3. failed closed against stale-PASS reuse, artifact substitution, post-verification mutation, identity mismatch, failed execution, and non-PASS verdicts;
4. preserved provider neutrality; and
5. stayed within the evidence actually demonstrated by the process-local non-normative research slice.

### External verdict

`PASS`

### External evidence summary

The verifier reported that:

- `build_independent_verifier_request` rejects both the explicit forbidden host-context keys and any remaining non-empty opaque host context;
- `ArtifactIdentity` binds `task_id`, `dispatch_id`, `change_id`, `artifact_id`, `revision`, `digest`, and `target_ref`;
- finalization requires exact identity equality and rejects non-PASS verdicts, failed execution, blank artifact identity, and malformed digest;
- provider family and model are recorded as provenance but do not form part of the artifact identity equality, preserving provider neutrality; and
- the research document correctly limits the result to a process-local, non-normative boundary and explicitly excludes distributed, signed, time-based, package-provenance, and canonical-runtime guarantees.

The verifier independently identified residual risks rather than converting the PASS into a broader claim. Those included fabricated evidence objects carrying matching fields, cross-process authenticity and replay, concurrent mutation, time-based freshness, and context injection outside the bounded request builder.

### Calibration interpretation

This result is a positive-control success. The verifier accepted a claim only inside the research record's declared scope and did not elevate it into normative runtime authority.

## Task 002: Normative Artifact-Bound Finalization

### Material examined

The second assignment asked the verifier to determine whether the current normative Python reference runtime, excluding research-only harnesses, guarantees that a successful verification PASS can authorize finalization only for the exact artifact or change-set the verifier actually examined.

The minimum inspection surface included:

- `reference/implementations/python/src/teo_reference/engine.py`
- `reference/implementations/python/src/teo_reference/schemas.py`
- the normative live-verification path and relevant tests

The verifier was again instructed not to treat TEO documentation, previous conclusions, Progress Tracker statements, or CI success as proof.

### External verdict

`FAIL`

### External evidence summary

The verifier reported that canonical `ExecutionResult` contains:

- `dispatch_id`
- `status`
- optional `output_ref`
- evidence strings
- failed-attempt count

and canonical `VerificationResult` contains:

- `dispatch_id`
- verification status
- verifier model
- checks
- evidence strings
- optional notes

Neither canonical type structurally carries artifact ID, change ID, revision, content digest, target reference, or equivalent exact artifact identity.

The verifier further reported that `OrchestrationEngine.finalize()` validates dispatch identity, assigned verifier identity, model independence, provider-family independence, execution status, and verification status, but does not compare the artifact examined by verification with the artifact being finalized.

The live-verification path reads the file named by `execution.output_ref` at verification time, but the durable result returned to canonical finalization is reduced to `VerificationResult`, which does not preserve the examined artifact digest or identity.

The verifier therefore concluded that a PASS for artifact A could be reused with a different or post-verification-mutated artifact under the same dispatch because the normative finalization contract has no exact artifact identity to compare.

The verifier found no normative test preventing that reuse and correctly distinguished the research-only artifact-binding tests from the normative runtime suite.

### TEO Mission Control corroboration

TEO Mission Control independently rechecked the central negative-control claim against the current repository baseline.

The normative schemas do not carry exact artifact identity in `VerificationResult`, and the live-verification path reads artifact content before producing the canonical result without persisting a digest or exact artifact identity into that result. The normative finalization path therefore cannot enforce the stronger artifact-bound guarantee.

This corroborates the external FAIL as a real normative boundary rather than a documentation-reading artifact.

### Calibration interpretation

This result is the negative-control success. The verifier rejected a TEO claim when current normative implementation did not support it and supplied concrete code-level reasons rather than relying on authority or prior TEO statements.

## Calibration conclusion

The combined positive and negative controls provide enough evidence to classify this verifier as:

**External Independent Technical Verifier: evidence authority only**

The evidence supports using the verifier for bounded independent technical assessments where the task, artifacts, claim, and requested verdict structure are explicit.

The evidence does not support granting the verifier:

- governance authority;
- release veto or approval authority;
- routing or provider-selection authority;
- architecture-change authority;
- policy-write authority;
- live-execution authority;
- qualified-human approval authority; or
- automatic acceptance of future verdicts without TEO-side evidence review.

Future verifier outputs remain untrusted external evidence until reconciled against current repository truth. Consequential findings should still be independently reproduced or otherwise verified before remediation or authority changes.

## Effect on existing calibration program

No Progress Tracker percentage is increased by this record alone.

The broader `Verifier calibration evidence` workstream remains an accumulated evidence program covering deterministic, empirical, repeatability, disagreement, adversarial, and route-specific behavior.

The optional independent-human calibration study remains optional and non-authoritative. This two-task technical calibration is not represented as the two-reviewer-plus-adjudicator human study and must not be counted as completing that protocol.

## Next bounded use

The next real assignment may use the calibrated verifier against an open technical target without disclosing an expected verdict. One suitable target is the current Final Execution Provenance Projection, where the verifier can attempt to falsify route-evidence integrity, active-route selection, verifier/disposition consistency, authority boundaries, and legacy compatibility.

That future assessment is separate evidence and is not included in this calibration record.
