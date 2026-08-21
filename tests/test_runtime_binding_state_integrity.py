from __future__ import annotations

import pytest

from teo_reference.domain.runtime_binding import (
    AuthorityScope,
    CalibrationRecord,
    CalibratedImplementation,
    EligibleImplementation,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeBindingError,
    RuntimeImplementation,
    discover,
    evaluate_eligibility,
)


def _implementation(*, quantization: str | None = None) -> RuntimeImplementation:
    return RuntimeImplementation(
        configuration=ExecutionConfigurationIdentity.from_runtime(
            implementation_id="impl-a",
            model="model-a",
            runtime="runtime-a",
            quantization=quantization,
            context_window=32768,
        ),
        inventory_state="running",
        capabilities=frozenset({"coding"}),
    )


def _evidence() -> EligibilityEvidence:
    return EligibilityEvidence(
        reachable=True,
        healthy=True,
        privacy_allowed=True,
        runtime_constraints_satisfied=True,
    )


def test_eligible_state_constructor_cannot_bypass_authority() -> None:
    discovered = discover(_implementation())

    with pytest.raises(
        RuntimeBindingError,
        match="eligible state cannot be constructed",
    ):
        EligibleImplementation(
            discovered=discovered,
            authority=AuthorityScope(frozenset()),
            requirements=EligibilityRequirements(
                required_capabilities=frozenset({"coding"})
            ),
            evidence=_evidence(),
        )


def test_calibrated_state_constructor_cannot_bypass_configuration_binding() -> None:
    implementation = _implementation()
    decision = evaluate_eligibility(
        discover(implementation),
        authority=AuthorityScope(frozenset({"impl-a"})),
        requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        evidence=_evidence(),
    )
    assert decision.eligible is not None

    changed = _implementation(quantization="q4")
    with pytest.raises(
        RuntimeBindingError,
        match="calibration fingerprint does not match",
    ):
        CalibratedImplementation(
            eligible=decision.eligible,
            calibration=CalibrationRecord(
                configuration_fingerprint=changed.configuration.fingerprint,
                status="passed",
                evidence_ref="benchmark://wrong-configuration",
            ),
        )
