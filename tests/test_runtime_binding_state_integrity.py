from __future__ import annotations

import pytest

from teo_reference.domain.runtime_binding import (
    AuthorityScope,
    CalibrationRecord,
    CalibrationRequirements,
    CalibratedImplementation,
    EligibleImplementation,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeBindingError,
    RuntimeImplementation,
    SelectedImplementation,
    apply_calibration,
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


def _eligible() -> EligibleImplementation:
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
    return decision.eligible


def _fresh_record(eligible: EligibleImplementation) -> CalibrationRecord:
    return CalibrationRecord(
        configuration_fingerprint=eligible.implementation.configuration.fingerprint,
        status="passed",
        evidence_ref="benchmark://fresh",
        calibrated_at="2026-08-21T11:00:00+00:00",
        valid_until="2026-08-21T13:00:00+00:00",
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
    eligible = _eligible()
    changed = _implementation(quantization="q4")

    with pytest.raises(
        RuntimeBindingError,
        match="calibration fingerprint does not match",
    ):
        CalibratedImplementation(
            eligible=eligible,
            calibration=CalibrationRecord(
                configuration_fingerprint=changed.configuration.fingerprint,
                status="passed",
                evidence_ref="benchmark://wrong-configuration",
                calibrated_at="2026-08-21T11:00:00+00:00",
            ),
            requirements=CalibrationRequirements(required=True),
            evaluated_at="2026-08-21T12:00:00+00:00",
        )


def test_calibrated_state_constructor_cannot_bypass_staleness() -> None:
    eligible = _eligible()

    with pytest.raises(
        RuntimeBindingError,
        match="stale at evaluated_at",
    ):
        CalibratedImplementation(
            eligible=eligible,
            calibration=_fresh_record(eligible),
            requirements=CalibrationRequirements(required=True),
            evaluated_at="2026-08-21T13:00:00+00:00",
        )


def test_selected_state_constructor_rechecks_calibration_at_selection_time() -> None:
    eligible = _eligible()
    calibrated = apply_calibration(
        eligible,
        _fresh_record(eligible),
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    with pytest.raises(
        RuntimeBindingError,
        match="selected state cannot be constructed",
    ):
        SelectedImplementation(
            calibrated=calibrated,
            fitness_score=1.0,
            selection_reason="would otherwise win",
            evaluated_at="2026-08-21T13:00:00+00:00",
        )
