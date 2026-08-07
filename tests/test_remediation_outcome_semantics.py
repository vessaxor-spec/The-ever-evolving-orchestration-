from __future__ import annotations

from pathlib import Path

from teo_reference.config import ConfigBundle
from teo_reference.runtime_canary import _copy_task_for_redispatch
from teo_reference.schemas import ExecutionResult, TaskRequest, VerificationResult
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIEW_MODEL = "gemini-3.1-pro-preview"


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def test_available_fallback_is_not_recorded_as_executed_escalation() -> None:
    runtime = engine()
    dispatch = runtime.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Design the service architecture for a bounded internal component.",
                "task_type": "architecture_design",
                "risk_level": "medium",
                "constraints": {"accepted_preview_models": [PREVIEW_MODEL]},
            }
        )
    )
    assert dispatch.fallback_implementation is not None

    outcome = runtime.finalize(
        dispatch,
        ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="failed",
            failed_attempts=1,
        ),
        VerificationResult(
            dispatch_id=dispatch.dispatch_id,
            status="passed",
            verifier_model=dispatch.verification.implementation.model,
        ),
    )

    assert outcome.status == "escalated"
    assert outcome.escalation_used is False
    assert any("available but is not recorded as executed" in note for note in outcome.notes)


def test_preview_acceptance_survives_model_failure_redispatch_without_expansion() -> None:
    runtime = engine()
    task = TaskRequest.from_dict(
        {
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
            "constraints": {"accepted_preview_models": [PREVIEW_MODEL]},
        }
    )
    dispatch = runtime.dispatch(task)
    redispatch = _copy_task_for_redispatch(task, dispatch, "model")

    assert redispatch.constraints.accepted_preview_models == [PREVIEW_MODEL]
    assert dispatch.selected_implementation.model in redispatch.constraints.blocked_implementations
    assert set(redispatch.constraints.accepted_preview_models) == set(
        task.constraints.accepted_preview_models
    )


def test_preview_acceptance_survives_provider_failure_redispatch_without_expansion() -> None:
    runtime = engine()
    task = TaskRequest.from_dict(
        {
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
            "constraints": {"accepted_preview_models": [PREVIEW_MODEL]},
        }
    )
    dispatch = runtime.dispatch(task)
    redispatch = _copy_task_for_redispatch(task, dispatch, "provider")

    assert redispatch.constraints.accepted_preview_models == [PREVIEW_MODEL]
    assert dispatch.selected_implementation.provider_family in redispatch.constraints.blocked_providers
    assert set(redispatch.constraints.accepted_preview_models) == set(
        task.constraints.accepted_preview_models
    )
