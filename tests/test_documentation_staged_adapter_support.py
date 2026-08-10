from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from teo_reference.anthropic_adapter import (
    CANARY_MODELS as ANTHROPIC_CANARY_MODELS,
    IMPLEMENTED_MODELS as ANTHROPIC_IMPLEMENTED_MODELS,
    AnthropicMessagesAdapter,
)
from teo_reference.openai_adapter import (
    CANARY_MODELS as OPENAI_CANARY_MODELS,
    IMPLEMENTED_MODELS as OPENAI_IMPLEMENTED_MODELS,
    OpenAIResponsesAdapter,
)
from teo_reference.openai_verifier import OpenAILiveVerifier, SUPPORTED_MODELS
from teo_reference.provider_adapter import ProviderAdapterContractError, ProviderExecutionRequest
from teo_reference.provider_connection import ProviderConnectionRequest, ProviderConnectionResponse
from teo_reference.verification_adapter import LiveVerificationRequest


@dataclass
class FakeConnection:
    provider_family: str
    response: ProviderConnectionResponse
    calls: list[ProviderConnectionRequest]

    def invoke(self, request: ProviderConnectionRequest) -> ProviderConnectionResponse:
        self.calls.append(request)
        return self.response


def test_sonnet5_is_implemented_without_becoming_an_active_anthropic_canary_model(
    tmp_path: Path,
) -> None:
    connection = FakeConnection(
        provider_family="anthropic",
        response=ProviderConnectionResponse(
            status_code=200,
            headers={"request-id": "req-sonnet"},
            body=json.dumps(
                {
                    "model": "claude-sonnet-5",
                    "content": [{"type": "text", "text": "bounded documentation output"}],
                    "usage": {"input_tokens": 5, "output_tokens": 7},
                }
            ).encode("utf-8"),
        ),
        calls=[],
    )
    request = ProviderExecutionRequest(
        dispatch_id="dispatch-sonnet-stage",
        task_id="task-sonnet-stage",
        provider_family="anthropic",
        model="claude-sonnet-5",
        risk_level="low",
        required_capabilities=("synthesis", "technical_accuracy", "clear_writing"),
        input_payload={"task": "Draft a bounded technical note."},
        reasoning_effort="medium",
    )

    response = AnthropicMessagesAdapter(
        connection,
        artifact_dir=tmp_path / "anthropic",
    ).execute(request)

    assert "claude-sonnet-5" in ANTHROPIC_IMPLEMENTED_MODELS
    assert "claude-sonnet-5" not in ANTHROPIC_CANARY_MODELS
    assert response.status == "succeeded"
    assert response.model == "claude-sonnet-5"
    assert "teo_reasoning_effort:medium" in response.evidence
    assert len(connection.calls) == 1
    payload = json.loads(connection.calls[0].body.decode("utf-8"))
    assert payload["model"] == "claude-sonnet-5"
    assert payload["output_config"] == {"effort": "medium"}
    assert "thinking" not in payload
    assert "temperature" not in payload
    assert "top_p" not in payload
    assert "top_k" not in payload


def test_sonnet5_requires_explicit_supported_effort_before_provider_invocation(
    tmp_path: Path,
) -> None:
    connection = FakeConnection(
        provider_family="anthropic",
        response=ProviderConnectionResponse(status_code=500, headers={}, body=b"{}"),
        calls=[],
    )
    request = ProviderExecutionRequest(
        dispatch_id="dispatch-sonnet-no-effort",
        task_id="task-sonnet-no-effort",
        provider_family="anthropic",
        model="claude-sonnet-5",
        risk_level="low",
        required_capabilities=("synthesis",),
        input_payload={"task": "Draft a bounded technical note."},
        reasoning_effort=None,
    )

    with pytest.raises(
        ProviderAdapterContractError,
        match="requires an explicit supported effort",
    ):
        AnthropicMessagesAdapter(
            connection,
            artifact_dir=tmp_path / "anthropic",
        ).execute(request)

    assert connection.calls == []


def test_sol_is_implemented_without_becoming_an_active_openai_canary_model(
    tmp_path: Path,
) -> None:
    connection = FakeConnection(
        provider_family="openai",
        response=ProviderConnectionResponse(
            status_code=200,
            headers={"x-request-id": "req-sol"},
            body=json.dumps(
                {
                    "id": "resp-sol",
                    "model": "gpt-5.6-sol",
                    "status": "completed",
                    "output_text": "fallback documentation output",
                    "usage": {"input_tokens": 4, "output_tokens": 6, "total_tokens": 10},
                }
            ).encode("utf-8"),
        ),
        calls=[],
    )
    request = ProviderExecutionRequest(
        dispatch_id="dispatch-sol-stage",
        task_id="task-sol-stage",
        provider_family="openai",
        model="gpt-5.6-sol",
        risk_level="low",
        required_capabilities=("synthesis", "technical_accuracy", "clear_writing"),
        input_payload={"task": "Draft a bounded technical note."},
        reasoning_effort="medium",
    )

    response = OpenAIResponsesAdapter(
        connection,
        artifact_dir=tmp_path / "openai",
    ).execute(request)

    assert "gpt-5.6-sol" in OPENAI_IMPLEMENTED_MODELS
    assert "gpt-5.6-sol" not in OPENAI_CANARY_MODELS
    assert response.status == "succeeded"
    assert response.model == "gpt-5.6-sol"
    assert len(connection.calls) == 1
    payload = json.loads(connection.calls[0].body.decode("utf-8"))
    assert payload["model"] == "gpt-5.6-sol"
    assert payload["reasoning"] == {"effort": "medium"}
    assert payload["store"] is False


def test_terra_verifier_support_preserves_strict_structured_output_and_effort() -> None:
    decision = {
        "status": "passed",
        "output_present": "pass",
        "task_adherence": "pass",
        "format_consistency": "pass",
        "unsupported_claims_absent": "pass",
        "human_reason": "none",
    }
    connection = FakeConnection(
        provider_family="openai",
        response=ProviderConnectionResponse(
            status_code=200,
            headers={"x-request-id": "req-terra-verifier"},
            body=json.dumps(
                {
                    "id": "resp-terra-verifier",
                    "model": "gpt-5.6-terra",
                    "status": "completed",
                    "output_text": json.dumps(decision),
                    "usage": {"input_tokens": 8, "output_tokens": 5, "total_tokens": 13},
                }
            ).encode("utf-8"),
        ),
        calls=[],
    )
    request = LiveVerificationRequest(
        dispatch_id="dispatch-terra-verifier",
        task_id="task-terra-verifier",
        verifier_provider_family="openai",
        verifier_model="gpt-5.6-terra",
        verifier_reasoning_effort="medium",
        risk_level="low",
        verification_methods=("output_validation",),
        task="Draft a bounded technical note.",
        output_text="Bounded documentation output.",
    )

    response = OpenAILiveVerifier({"openai": connection}).verify(request)

    assert "gpt-5.6-terra" in SUPPORTED_MODELS
    assert response.decision.status == "passed"
    assert response.model == "gpt-5.6-terra"
    assert len(connection.calls) == 1
    payload = json.loads(connection.calls[0].body.decode("utf-8"))
    assert payload["model"] == "gpt-5.6-terra"
    assert payload["reasoning"] == {"effort": "medium"}
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert payload["store"] is False
