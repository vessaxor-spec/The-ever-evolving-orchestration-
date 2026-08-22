from __future__ import annotations

import pytest

from teo_reference.adapters.runtime_calibration import DeclaredRuntimeCalibrationAdapter
from teo_reference.adapters.runtime_eligibility import DeclaredRuntimeEligibilityEvidenceAdapter
from teo_reference.adapters.runtime_selection import DeclaredRuntimeFitnessAdapter
from teo_reference.application.runtime_selection import RuntimeSelectionService
from teo_reference.domain.runtime_binding import (
    CalibrationRecord,
    CalibrationRequirements,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeImplementation,
)
from teo_reference.domain.runtime_selection import (
    RuntimeSelectionError,
    RuntimeSelectionRequest,
    RuntimeSelectionScope,
)

EVALUATED_AT = "2026-08-21T20:00:00+00:00"


class StaticInventory:
    def __init__(self, implementation: RuntimeImplementation) -> None:
        self.implementation = implementation

    def discover(self):
        return (self.implementation,)


def _implementation(*, encoded_effort: str | None = None) -> RuntimeImplementation:
    if encoded_effort is None:
        configuration = ExecutionConfigurationIdentity.from_runtime(
            implementation_id="impl-a",
            model="model-a",
            runtime="test-runtime",
            provider_family="provider-a",
            reasoning_controls={"effort": "high"},
        )
    else:
        configuration = ExecutionConfigurationIdentity(
            implementation_id="impl-a",
            model="model-a",
            runtime="test-runtime",
            provider_family="provider-a",
            reasoning_controls=(("effort", encoded_effort),),
        )
    return RuntimeImplementation(
        configuration=configuration,
        inventory_state="running",
        capabilities=frozenset({"coding"}),
    )


def _service(implementation: RuntimeImplementation) -> RuntimeSelectionService:
    return RuntimeSelectionService(
        inventory=StaticInventory(implementation),
        eligibility_evidence=DeclaredRuntimeEligibilityEvidenceAdapter(
            {
                "impl-a": EligibilityEvidence(
                    reachable=True,
                    healthy=True,
                    privacy_allowed=True,
                    runtime_constraints_satisfied=True,
                )
            }
        ),
        calibration_records=DeclaredRuntimeCalibrationAdapter(
            (
                CalibrationRecord(
                    configuration_fingerprint=implementation.configuration.fingerprint,
                    status="passed",
                    evidence_ref="benchmark://reasoning-control",
                    calibrated_at="2026-08-21T19:00:00+00:00",
                    valid_until="2026-08-21T21:00:00+00:00",
                ),
            )
        ),
        fitness=DeclaredRuntimeFitnessAdapter({"impl-a": 1.0}),
    )


def _request(effort: str) -> RuntimeSelectionRequest:
    return RuntimeSelectionRequest(
        scope=RuntimeSelectionScope(
            task_id="task-a",
            task_type="daily_coding",
            worker="backend",
            role="primary",
        ),
        eligibility_requirements=EligibilityRequirements(
            required_capabilities=frozenset({"coding"})
        ),
        calibration_requirements=CalibrationRequirements(
            required=True,
            max_age_seconds=7200,
            require_valid_until=True,
        ),
        evaluated_at=EVALUATED_AT,
        authorized_models=frozenset({"model-a"}),
        preferred_models=("model-a",),
        reasoning_effort_by_model=(("model-a", effort),),
    )


def test_normalized_reasoning_control_matches_logical_requested_effort() -> None:
    implementation = _implementation()

    decision = _service(implementation).select(_request("high"))

    assert decision.selected.implementation.implementation_id == "impl-a"


def test_mismatched_reasoning_control_fails_closed_before_selection() -> None:
    implementation = _implementation()

    with pytest.raises(RuntimeSelectionError, match="no authorized eligible calibrated"):
        _service(implementation).select(_request("medium"))


def test_malformed_normalized_reasoning_control_fails_closed() -> None:
    implementation = _implementation(encoded_effort="not-json")

    with pytest.raises(RuntimeSelectionError, match="no authorized eligible calibrated"):
        _service(implementation).select(_request("high"))
