from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.google_adapter import GEMINI_INTERACTIONS_URL, execute_gemini_canary_once
from teo_reference.openai_adapter import OPENAI_RESPONSES_URL, execute_openai_canary_once
from teo_reference.provider_adapter import ProviderAdapterContractError, ProviderExecutionRequest
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


def choice(model: str, provider_family: str, reasoning: str | None = None) -> ImplementationChoice:
    return ImplementationChoice(
        agent="runtime-test",
        model=model,
        profile="luna",
        provider_family=provider_family,
        availability="current",
        source="test-route",
        reasoning=reasoning,
    )


def dispatch(
    provider_family: str,
    model: str,
    reasoning: str | None,
    *,
    risk_level: str = "low",
) -> DispatchRecord:
    return DispatchRecord(
        task_id=f"task-{provider_family}",
        dispatch_id=f"dispatch-{provider_family}",
        created_at="2026-08-07T08:30:00+00:00",
        task="Classify the bounded records and return the labels.",
        task_type="high_volume_simple",
        risk_level=risk_level,  # type: ignore[arg-type]
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["classification"],
        selected_implementation=choice(model, provider_family, reasoning),
        fallback_implementation=None,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice("claude-sonnet-5", "anthropic", "medium"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["test"],
        warnings=[],
    )


def connection(provider_family: str, calls: list[dict], status: int, payload: dict):
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
        return status, {"x-request-id": "req_test"}, json.dumps(payload).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider_family,
        authorization_headers={"authorization": "Bearer test-runtime-token"},
        transport=transport,
    )


def test_provider_request_carries_dispatch_selected_reasoning_effort() -> None:
    request = ProviderExecutionRequest.from_dispatch(
        dispatch("openai", "gpt-5.6-luna", "low")
    )
    assert request.reasoning_effort == "low"
    assert request.to_dict()["reasoning_effort"] == "low"


def test_openai_canary_uses_responses_api_and_explicit_reasoning_effort(tmp_path: Path) -> None:
    calls: list[dict] = []
    response = execute_openai_canary_once(
        dispatch("openai", "gpt-5.6-luna", "low"),
        connection(
            "openai",
            calls,
            200,
            {
                "id": "resp_123",
                "model": "gpt-5.6-luna",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "label_a\nlabel_b"}],
                    }
                ],
            },
        ),
        artifact_dir=tmp_path,
    )

    assert len(calls) == 1
    assert calls[0]["url"] == OPENAI_RESPONSES_URL
    assert calls[0]["method"] == "POST"
    assert calls[0]["body"]["model"] == "gpt-5.6-luna"
    assert calls[0]["body"]["store"] is False
    assert calls[0]["body"]["reasoning"] == {"effort": "low"}
    assert calls[0]["body"]["input"] == "Classify the bounded records and return the labels."
    assert response.status == "succeeded"
    assert "teo_reasoning_effort:low" in response.evidence
    artifact = Path(response.output_ref.removeprefix("file://"))
    assert artifact.read_text(encoding="utf-8") == "label_a\nlabel_b\n"


def test_gemini_canary_uses_stable_interactions_api_and_thinking_level(tmp_path: Path) -> None:
    calls: list[dict] = []
    response = execute_gemini_canary_once(
        dispatch("google", "gemini-3.7-flash", "medium"),
        connection(
            "google",
            calls,
            200,
            {
                "id": "int_123",
                "model": "gemini-3.7-flash",
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "label_a\nlabel_b"}],
                    }
                ],
            },
        ),
        artifact_dir=tmp_path,
    )

    assert len(calls) == 1
    assert calls[0]["url"] == GEMINI_INTERACTIONS_URL
    assert calls[0]["method"] == "POST"
    assert calls[0]["body"]["model"] == "gemini-3.7-flash"
    assert calls[0]["body"]["store"] is False
    assert calls[0]["body"]["generation_config"] == {
        "max_output_tokens": 512,
        "thinking_level": "medium",
    }
    assert response.status == "succeeded"
    assert "teo_reasoning_effort:medium" in response.evidence
    artifact = Path(response.output_ref.removeprefix("file://"))
    assert artifact.read_text(encoding="utf-8") == "label_a\nlabel_b\n"


def test_openai_rejects_provider_unsupported_minimal_effort_before_invocation(tmp_path: Path) -> None:
    calls: list[dict] = []
    with pytest.raises(ProviderAdapterContractError, match="does not support"):
        execute_openai_canary_once(
            dispatch("openai", "gpt-5.6-luna", "minimal"),
            connection("openai", calls, 200, {}),
            artifact_dir=tmp_path,
        )
    assert calls == []


def test_gemini_rejects_provider_unsupported_xhigh_effort_before_invocation(tmp_path: Path) -> None:
    calls: list[dict] = []
    with pytest.raises(ProviderAdapterContractError, match="does not support"):
        execute_gemini_canary_once(
            dispatch("google", "gemini-3.7-flash", "xhigh"),
            connection("google", calls, 200, {}),
            artifact_dir=tmp_path,
        )
    assert calls == []


@pytest.mark.parametrize(
    ("provider_family", "model", "executor"),
    [
        ("openai", "gpt-5.6-luna", execute_openai_canary_once),
        ("google", "gemini-3.7-flash", execute_gemini_canary_once),
    ],
)
def test_new_canaries_refuse_high_risk_before_invocation(
    tmp_path: Path,
    provider_family: str,
    model: str,
    executor,
) -> None:
    calls: list[dict] = []
    with pytest.raises(ProviderAdapterContractError, match="refuses high and critical"):
        executor(
            dispatch(provider_family, model, "high", risk_level="high"),
            connection(provider_family, calls, 200, {}),
            artifact_dir=tmp_path,
        )
    assert calls == []


def test_openai_rate_limit_is_provider_scoped_and_not_retried(tmp_path: Path) -> None:
    calls: list[dict] = []
    response = execute_openai_canary_once(
        dispatch("openai", "gpt-5.6-luna", "low"),
        connection(
            "openai",
            calls,
            429,
            {"error": {"type": "rate_limit_error", "message": "slow down"}},
        ),
        artifact_dir=tmp_path,
    )
    assert len(calls) == 1
    assert response.failure is not None
    assert response.failure.scope == "provider"


def test_gemini_unavailable_is_transient_and_not_retried(tmp_path: Path) -> None:
    calls: list[dict] = []
    response = execute_gemini_canary_once(
        dispatch("google", "gemini-3.7-flash", "medium"),
        connection(
            "google",
            calls,
            503,
            {"error": {"status": "UNAVAILABLE", "message": "try later"}},
        ),
        artifact_dir=tmp_path,
    )
    assert len(calls) == 1
    assert response.failure is not None
    assert response.failure.scope == "transient"


@pytest.mark.parametrize(
    ("provider_family", "model", "wrong_model", "executor", "payload"),
    [
        (
            "openai",
            "gpt-5.6-luna",
            "gpt-5.6-sol",
            execute_openai_canary_once,
            {
                "id": "resp_wrong",
                "model": "gpt-5.6-sol",
                "status": "completed",
                "output": [{"type": "message", "content": [{"type": "output_text", "text": "x"}]}],
            },
        ),
        (
            "google",
            "gemini-3.7-flash",
            "gemini-3.1-pro-preview",
            execute_gemini_canary_once,
            {
                "id": "int_wrong",
                "model": "gemini-3.1-pro-preview",
                "status": "completed",
                "steps": [{"type": "model_output", "content": [{"type": "text", "text": "x"}]}],
            },
        ),
    ],
)
def test_provider_cannot_silently_substitute_model(
    tmp_path: Path,
    provider_family: str,
    model: str,
    wrong_model: str,
    executor,
    payload: dict,
) -> None:
    calls: list[dict] = []
    with pytest.raises(ProviderAdapterContractError, match="different from the dispatch-authorized model"):
        executor(
            dispatch(provider_family, model, "low"),
            connection(provider_family, calls, 200, payload),
            artifact_dir=tmp_path,
        )
    assert len(calls) == 1
