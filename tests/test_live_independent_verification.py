from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.provider_adapter import ProviderExecutionResponse, ProviderFailure
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_canary import CanaryRuntimeOutcome
from teo_reference.runtime_verification import (
    execute_live_verification,
    verify_guarded_canary_outcome,
)
from teo_reference.schemas import (
    DispatchRecord,
    ImplementationChoice,
    TaskRequest,
    VerificationPlan,
)
from teo_reference.specialist_routing import SpecialistRoutingEngine
from teo_reference.verification_adapter import LiveVerificationError


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def task(*, blocked_providers=None, blocked_models=None, risk="low") -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": "task-live-verifier",
            "task": "Classify the bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": risk,
            "constraints": {
                "blocked_providers": list(blocked_providers or []),
                "blocked_implementations": list(blocked_models or []),
            },
        }
    )


def write_output(tmp_path: Path, text: str = "label_a\nlabel_b") -> str:
    path = tmp_path / "execution.txt"
    path.write_text(text + "\n", encoding="utf-8")
    return path.resolve().as_uri()


def success_response(dispatch: DispatchRecord, output_ref: str) -> ProviderExecutionResponse:
    return ProviderExecutionResponse(
        dispatch_id=dispatch.dispatch_id,
        status="succeeded",
        provider_family=dispatch.selected_implementation.provider_family or "",
        model=dispatch.selected_implementation.model,
        output_ref=output_ref,
    )


def decision(status: str = "passed") -> dict:
    if status == "passed":
        return {
            "status": "passed",
            "output_present": "pass",
            "task_adherence": "pass",
            "format_consistency": "pass",
            "unsupported_claims_absent": "pass",
            "human_reason": "none",
        }
    if status == "failed":
        return {
            "status": "failed",
            "output_present": "pass",
            "task_adherence": "fail",
            "format_consistency": "pass",
            "unsupported_claims_absent": "pass",
            "human_reason": "none",
        }
    return {
        "status": "needs_human",
        "output_present": "pass",
        "task_adherence": "uncertain",
        "format_consistency": "pass",
        "unsupported_claims_absent": "pass",
        "human_reason": "insufficient_evidence",
    }


def connection(provider: str, calls: list[dict], payload: dict, *, status_code: int = 200):
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        calls.append(
            {
                "url": url,
                "method": method,
                "body": json.loads(body.decode("utf-8")),
                "headers": dict(headers),
                "timeout": timeout,
            }
        )
        return status_code, {"x-request-id": f"req_{provider}"}, json.dumps(payload).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider,
        authorization_headers={"authorization": "Bearer secret-runtime-token"},
        transport=transport,
    )


def google_payload(verdict: dict) -> dict:
    return {
        "id": "int_verify",
        "model": "gemini-3.6-flash",
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [{"type": "text", "text": json.dumps(verdict)}],
            }
        ],
    }


def anthropic_payload(verdict: dict) -> dict:
    return {
        "id": "msg_verify",
        "model": "claude-sonnet-5",
        "content": [{"type": "text", "text": json.dumps(verdict)}],
    }


def openai_payload(verdict: dict) -> dict:
    return {
        "id": "resp_verify",
        "model": "gpt-5.6-sol",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(verdict)}],
            }
        ],
    }


def test_primary_canary_uses_provider_diverse_gemini_verifier() -> None:
    dispatch = engine().dispatch(task())
    assert dispatch.selected_implementation.model == "claude-haiku-4-5"
    assert dispatch.selected_implementation.provider_family == "anthropic"
    assert dispatch.verification.implementation.model == "gemini-3.6-flash"
    assert dispatch.verification.implementation.provider_family == "google"
    assert dispatch.verification.implementation.reasoning == "medium"


def test_model_scoped_fallback_gets_fresh_anthropic_verifier() -> None:
    primary = engine().dispatch(task())
    fallback = engine().dispatch(task(blocked_models=["claude-haiku-4-5"]))
    assert fallback.selected_implementation.model == "gemini-3.6-flash"
    assert fallback.verification.implementation.model == "claude-sonnet-5"
    assert fallback.verification.implementation.provider_family == "anthropic"
    assert fallback.verification.implementation.model != primary.verification.implementation.model


def test_provider_scoped_fallback_gets_fresh_openai_verifier() -> None:
    primary = engine().dispatch(task())
    fallback = engine().dispatch(task(blocked_providers=["anthropic"]))
    assert fallback.selected_implementation.model == "gemini-3.6-flash"
    assert fallback.verification.implementation.model == "gpt-5.6-sol"
    assert fallback.verification.implementation.provider_family == "openai"
    assert fallback.verification.implementation.model != primary.verification.implementation.model


def test_primary_live_verifier_is_blinded_and_uses_google_structured_output(tmp_path: Path) -> None:
    dispatch = engine().dispatch(task())
    calls: list[dict] = []
    result = execute_live_verification(
        dispatch,
        success_response(dispatch, write_output(tmp_path)),
        {"google": connection("google", calls, google_payload(decision()))},
    )

    assert result.status == "passed"
    assert result.verifier_model == "gemini-3.6-flash"
    body = calls[0]["body"]
    assert body["model"] == "gemini-3.6-flash"
    assert body["generation_config"]["thinking_level"] == "medium"
    assert body["response_format"]["type"] == "text"
    assert body["response_format"]["mime_type"] == "application/json"
    serialized = json.dumps(body)
    assert "claude-haiku-4-5" not in serialized
    assert "anthropic" not in serialized.lower()
    assert "fallback" not in serialized.lower()
    assert "runtime-telemetry" not in serialized.lower()


def test_model_fallback_uses_assigned_sonnet_verifier_and_effort(tmp_path: Path) -> None:
    dispatch = engine().dispatch(task(blocked_models=["claude-haiku-4-5"]))
    calls: list[dict] = []
    result = execute_live_verification(
        dispatch,
        success_response(dispatch, write_output(tmp_path)),
        {"anthropic": connection("anthropic", calls, anthropic_payload(decision()))},
    )

    assert result.status == "passed"
    assert result.verifier_model == "claude-sonnet-5"
    body = calls[0]["body"]
    assert body["model"] == "claude-sonnet-5"
    assert body["output_config"]["effort"] == "medium"
    assert body["output_config"]["format"]["type"] == "json_schema"
    serialized = json.dumps(body)
    assert "gemini-3.6-flash" not in serialized
    assert "google" not in serialized.lower()


def test_provider_fallback_uses_assigned_sol_verifier_and_structured_output(tmp_path: Path) -> None:
    dispatch = engine().dispatch(task(blocked_providers=["anthropic"]))
    calls: list[dict] = []
    result = execute_live_verification(
        dispatch,
        success_response(dispatch, write_output(tmp_path)),
        {"openai": connection("openai", calls, openai_payload(decision()))},
    )

    assert result.status == "passed"
    assert result.verifier_model == "gpt-5.6-sol"
    body = calls[0]["body"]
    assert body["model"] == "gpt-5.6-sol"
    assert body["text"]["format"]["type"] == "json_schema"
    assert body["text"]["format"]["strict"] is True
    assert body["store"] is False
    serialized = json.dumps(body)
    assert "gemini-3.6-flash" not in serialized
    assert "google" not in serialized.lower()


@pytest.mark.parametrize(
    ("verdict", "expected"),
    [(decision("failed"), "failed"), (decision("needs_human"), "needs_human")],
)
def test_structured_verifier_status_maps_to_existing_verification_contract(
    tmp_path: Path,
    verdict: dict,
    expected: str,
) -> None:
    dispatch = engine().dispatch(task())
    result = execute_live_verification(
        dispatch,
        success_response(dispatch, write_output(tmp_path)),
        {"google": connection("google", [], google_payload(verdict))},
    )
    assert result.status == expected
    if expected == "needs_human":
        assert result.notes == ["live_verifier_human_reason:insufficient_evidence"]


def test_live_verifier_missing_assigned_connection_fails_closed(tmp_path: Path) -> None:
    dispatch = engine().dispatch(task())
    with pytest.raises(LiveVerificationError, match="No runtime connection"):
        execute_live_verification(
            dispatch,
            success_response(dispatch, write_output(tmp_path)),
            {},
        )


def test_malformed_verifier_json_fails_closed(tmp_path: Path) -> None:
    dispatch = engine().dispatch(task())
    malformed = google_payload(decision())
    malformed["steps"][0]["content"][0]["text"] = "not-json"
    with pytest.raises(LiveVerificationError, match="malformed structured JSON"):
        execute_live_verification(
            dispatch,
            success_response(dispatch, write_output(tmp_path)),
            {"google": connection("google", [], malformed)},
        )


def test_same_provider_live_verification_is_refused(tmp_path: Path) -> None:
    base = engine().dispatch(task())
    same_provider = DispatchRecord(
        task_id=base.task_id,
        dispatch_id=base.dispatch_id,
        created_at=base.created_at,
        task=base.task,
        task_type=base.task_type,
        risk_level=base.risk_level,
        selected_team=base.selected_team,
        selected_worker=base.selected_worker,
        selected_specialist=base.selected_specialist,
        specialist_source=base.specialist_source,
        specialist_risk_profile=base.specialist_risk_profile,
        required_capabilities=list(base.required_capabilities),
        selected_implementation=base.selected_implementation,
        fallback_implementation=base.fallback_implementation,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=ImplementationChoice(
                agent="claude",
                model="claude-sonnet-5",
                profile="sol",
                provider_family="anthropic",
                availability="current",
                source="test",
                reasoning="medium",
            ),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=list(base.routing_explanation),
        warnings=list(base.warnings),
    )
    with pytest.raises(LiveVerificationError, match="provider-diverse"):
        execute_live_verification(
            same_provider,
            success_response(same_provider, write_output(tmp_path)),
            {"anthropic": connection("anthropic", [], anthropic_payload(decision()))},
        )


def test_high_risk_live_verification_is_refused(tmp_path: Path) -> None:
    base = engine().dispatch(task())
    high = DispatchRecord(
        task_id=base.task_id,
        dispatch_id=base.dispatch_id,
        created_at=base.created_at,
        task=base.task,
        task_type=base.task_type,
        risk_level="high",
        selected_team=base.selected_team,
        selected_worker=base.selected_worker,
        selected_specialist=base.selected_specialist,
        specialist_source=base.specialist_source,
        specialist_risk_profile=base.specialist_risk_profile,
        required_capabilities=list(base.required_capabilities),
        selected_implementation=base.selected_implementation,
        fallback_implementation=base.fallback_implementation,
        verification=base.verification,
        routing_explanation=list(base.routing_explanation),
        warnings=list(base.warnings),
    )
    with pytest.raises(LiveVerificationError, match="refuses high and critical"):
        execute_live_verification(
            high,
            success_response(high, write_output(tmp_path)),
            {},
        )


def test_live_verification_integrates_with_existing_finalize_without_bypass(tmp_path: Path) -> None:
    runtime = engine()
    dispatch = runtime.dispatch(task())
    execution = success_response(dispatch, write_output(tmp_path))
    verification = execute_live_verification(
        dispatch,
        execution,
        {"google": connection("google", [], google_payload(decision()))},
    )
    outcome = runtime.finalize(
        dispatch,
        execution.to_execution_result(),
        verification,
    )
    assert outcome.status == "completed"
    assert outcome.verifier_model == "gemini-3.6-flash"


def test_guarded_outcome_uses_fallback_dispatch_fresh_verifier(tmp_path: Path) -> None:
    primary = engine().dispatch(task())
    fallback = engine().dispatch(task(blocked_providers=["anthropic"]))
    primary_failure = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="failed",
        provider_family="anthropic",
        model="claude-haiku-4-5",
        failure=ProviderFailure(
            scope="provider",
            code="rate_limit_error",
            message="provider unavailable",
        ),
    )
    fallback_success = success_response(fallback, write_output(tmp_path))
    outcome = CanaryRuntimeOutcome(
        status="fallback_executed",
        primary_dispatch=primary,
        primary_response=primary_failure,
        fallback_dispatch=fallback,
        fallback_response=fallback_success,
        fallback_attempts=1,
        fallback_trigger_scope="provider",
    )
    result = verify_guarded_canary_outcome(
        outcome,
        {"openai": connection("openai", [], openai_payload(decision()))},
    )
    assert result.status == "passed"
    assert result.dispatch_id == fallback.dispatch_id
    assert result.verifier_model == "gpt-5.6-sol"
    assert result.verifier_model != primary.verification.implementation.model
