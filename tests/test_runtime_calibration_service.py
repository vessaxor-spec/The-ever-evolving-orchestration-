from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.adapters.runtime_calibration import (
    DeclaredRuntimeCalibrationAdapter,
    RuntimeCalibrationAdapterError,
)
from teo_reference.application.runtime_calibration import (
    RuntimeCalibrationEvaluationError,
    RuntimeCalibrationService,
)
from teo_reference.domain.runtime_binding import (
    AuthorityScope,
    CalibrationRecord,
    CalibrationRequirements,
    EligibilityEvidence,
    EligibilityRequirements,
    ExecutionConfigurationIdentity,
    RuntimeImplementation,
    discover,
    evaluate_eligibility,
)
from teo_reference.ports.runtime_calibration import RuntimeCalibrationEvidenceUnavailable


def _eligible(*, implementation_id: str = "impl-a", quantization: str | None = None):
    implementation = RuntimeImplementation(
        configuration=ExecutionConfigurationIdentity.from_runtime(
            implementation_id=implementation_id,
            model="model-a",
            runtime="runtime-a",
            provider_family="provider-a",
            version="1",
            digest="sha256:abc",
            quantization=quantization,
            context_window=32768,
            hardware="cpu",
            serving_stack="test-stack",
            tools=("tool-a",),
            reasoning_controls={"effort": "high"},
            material_settings={"temperature": 0},
        ),
        inventory_state="running",
        capabilities=frozenset({"coding"}),
    )
    decision = evaluate_eligibility(
        discover(implementation),
        authority=AuthorityScope(frozenset({implementation_id})),
        requirements=EligibilityRequirements(required_capabilities=frozenset({"coding"})),
        evidence=EligibilityEvidence(
            reachable=True,
            healthy=True,
            privacy_allowed=True,
            runtime_constraints_satisfied=True,
        ),
    )
    assert decision.eligible is not None
    return decision.eligible


def _record(
    eligible,
    *,
    evidence_ref: str = "benchmark://a",
    status: str = "passed",
    calibrated_at: str | None = "2026-08-21T11:00:00+00:00",
    valid_until: str | None = "2026-08-21T13:00:00+00:00",
) -> CalibrationRecord:
    return CalibrationRecord(
        configuration_fingerprint=eligible.implementation.configuration.fingerprint,
        status=status,  # type: ignore[arg-type]
        evidence_ref=evidence_ref,
        calibrated_at=calibrated_at,
        valid_until=valid_until,
    )


def test_fresh_exact_configuration_calibration_is_accepted() -> None:
    eligible = _eligible()
    service = RuntimeCalibrationService(
        DeclaredRuntimeCalibrationAdapter((_record(eligible),))
    )

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True, max_age_seconds=7200),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is True
    assert assessment.calibrated is not None
    assert assessment.calibrated.calibration.evidence_ref == "benchmark://a"


def test_valid_until_boundary_is_stale() -> None:
    eligible = _eligible()
    service = RuntimeCalibrationService(
        DeclaredRuntimeCalibrationAdapter((_record(eligible),))
    )

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T13:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert any("stale at evaluated_at" in reason for reason in assessment.reasons)


def test_max_age_boundary_is_stale() -> None:
    eligible = _eligible()
    record = _record(eligible, valid_until=None)
    service = RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter((record,)))

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True, max_age_seconds=3600),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert any("maximum allowed age" in reason for reason in assessment.reasons)


def test_passed_record_without_calibrated_at_fails_closed() -> None:
    eligible = _eligible()
    record = _record(eligible, calibrated_at=None, valid_until=None)
    service = RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter((record,)))

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert any("requires calibrated_at" in reason for reason in assessment.reasons)


def test_future_dated_calibration_fails_closed() -> None:
    eligible = _eligible()
    record = _record(
        eligible,
        calibrated_at="2026-08-21T12:01:00+00:00",
        valid_until="2026-08-21T14:00:00+00:00",
    )
    service = RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter((record,)))

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert any("dated after evaluated_at" in reason for reason in assessment.reasons)


def test_policy_can_require_explicit_expiry() -> None:
    eligible = _eligible()
    record = _record(eligible, valid_until=None)
    service = RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter((record,)))

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True, require_valid_until=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert any("requires an explicit valid_until" in reason for reason in assessment.reasons)


def test_not_required_record_needs_policy_to_allow_the_exception() -> None:
    eligible = _eligible()
    record = _record(
        eligible,
        status="not_required",
        calibrated_at=None,
        valid_until=None,
    )
    adapter = DeclaredRuntimeCalibrationAdapter((record,))

    required = RuntimeCalibrationService(adapter).evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )
    optional = RuntimeCalibrationService(adapter).evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=False),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assert required.get("impl-a") is not None
    assert required.get("impl-a").satisfied is False  # type: ignore[union-attr]
    assert optional.get("impl-a") is not None
    assert optional.get("impl-a").satisfied is True  # type: ignore[union-attr]


def test_expired_not_required_exception_fails_closed() -> None:
    eligible = _eligible()
    record = _record(
        eligible,
        status="not_required",
        calibrated_at=None,
        valid_until="2026-08-21T12:00:00+00:00",
    )
    service = RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter((record,)))

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=False),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assert snapshot.get("impl-a") is not None
    assert snapshot.get("impl-a").satisfied is False  # type: ignore[union-attr]


def test_configuration_change_does_not_inherit_old_calibration() -> None:
    original = _eligible(quantization=None)
    changed = _eligible(quantization="q4")
    adapter = DeclaredRuntimeCalibrationAdapter((_record(original),))

    snapshot = RuntimeCalibrationService(adapter).evaluate(
        [changed],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert assessment.reasons == (
        "no calibration record for exact execution configuration",
    )


def test_history_prefers_newest_fresh_passed_record() -> None:
    eligible = _eligible()
    older = _record(
        eligible,
        evidence_ref="benchmark://older",
        calibrated_at="2026-08-21T09:00:00+00:00",
        valid_until="2026-08-21T14:00:00+00:00",
    )
    newer = _record(
        eligible,
        evidence_ref="benchmark://newer",
        calibrated_at="2026-08-21T11:00:00+00:00",
        valid_until="2026-08-21T14:00:00+00:00",
    )
    service = RuntimeCalibrationService(
        DeclaredRuntimeCalibrationAdapter((older, newer))
    )

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None and assessment.calibrated is not None
    assert assessment.calibrated.calibration.evidence_ref == "benchmark://newer"


def test_fresh_passed_record_is_preferred_over_not_required_exception() -> None:
    eligible = _eligible()
    passed = _record(eligible, evidence_ref="benchmark://passed")
    exception = _record(
        eligible,
        evidence_ref="policy://exception",
        status="not_required",
        calibrated_at=None,
        valid_until=None,
    )
    service = RuntimeCalibrationService(
        DeclaredRuntimeCalibrationAdapter((exception, passed))
    )

    snapshot = service.evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=False),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None and assessment.calibrated is not None
    assert assessment.calibrated.calibration.status == "passed"


def test_typed_calibration_evidence_unavailability_fails_closed_and_is_auditable() -> None:
    eligible = _eligible()

    class Unavailable:
        def records_for(self, configuration_fingerprint: str):
            raise RuntimeCalibrationEvidenceUnavailable("registry offline")

    snapshot = RuntimeCalibrationService(Unavailable()).evaluate(
        [eligible],
        requirements=CalibrationRequirements(required=True),
        evaluated_at="2026-08-21T12:00:00+00:00",
    )

    assessment = snapshot.get("impl-a")
    assert assessment is not None
    assert assessment.satisfied is False
    assert assessment.evidence_error == "registry offline"
    assert assessment.reasons == ("calibration evidence unavailable",)


def test_wrong_fingerprint_from_port_is_rejected_as_structural_error() -> None:
    eligible = _eligible()
    other = _eligible(implementation_id="impl-b")
    wrong = _record(other)

    class WrongPort:
        def records_for(self, configuration_fingerprint: str):
            return (wrong,)

    with pytest.raises(
        RuntimeCalibrationEvaluationError,
        match="wrong execution configuration",
    ):
        RuntimeCalibrationService(WrongPort()).evaluate(
            [eligible],
            requirements=CalibrationRequirements(required=True),
            evaluated_at="2026-08-21T12:00:00+00:00",
        )


def test_duplicate_eligible_ids_are_rejected() -> None:
    eligible = _eligible()

    with pytest.raises(
        RuntimeCalibrationEvaluationError,
        match="unique implementation ids",
    ):
        RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter()).evaluate(
            [eligible, eligible],
            requirements=CalibrationRequirements(required=True),
            evaluated_at="2026-08-21T12:00:00+00:00",
        )


def test_evaluated_at_requires_explicit_timezone_even_for_empty_input() -> None:
    with pytest.raises(
        RuntimeCalibrationEvaluationError,
        match="explicit timezone offset",
    ):
        RuntimeCalibrationService(DeclaredRuntimeCalibrationAdapter()).evaluate(
            [],
            requirements=CalibrationRequirements(required=True),
            evaluated_at="2026-08-21T12:00:00",
        )


def test_declared_adapter_preserves_history_but_rejects_duplicate_evidence_identity() -> None:
    eligible = _eligible()
    first = _record(eligible, evidence_ref="benchmark://same")
    duplicate_identity = _record(
        eligible,
        evidence_ref="benchmark://same",
        calibrated_at="2026-08-21T11:30:00+00:00",
        valid_until="2026-08-21T14:00:00+00:00",
    )

    with pytest.raises(
        RuntimeCalibrationAdapterError,
        match="evidence_ref must be unique",
    ):
        DeclaredRuntimeCalibrationAdapter((first, duplicate_identity))


def test_runtime_calibration_layers_do_not_import_routing_or_provider_execution() -> None:
    root = Path(__file__).resolve().parents[1]
    paths = [
        root
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
        / "application"
        / "runtime_calibration.py",
        root
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
        / "ports"
        / "runtime_calibration.py",
        root
        / "reference"
        / "implementations"
        / "python"
        / "src"
        / "teo_reference"
        / "adapters"
        / "runtime_calibration.py",
    ]
    forbidden = {"config", "engine", "provider", "routing", "verifier"}

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        assert not any(
            any(part in name.split(".") for part in forbidden)
            for name in imported
        ), path
