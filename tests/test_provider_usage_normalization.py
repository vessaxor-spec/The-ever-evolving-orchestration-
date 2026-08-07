from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from teo_reference.openai_adapter import execute_openai_canary_once
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


def choice(model: str, provider: str, reasoning: str | None = None) -> ImplementationChoice:
    return ImplementationChoice(
        agent="usage-test",
        model=model,
        profile="test",
        provider_family=provider,
        availability="current",
        source="test",
        reasoning=reasoning,
    )


def dispatch() -> DispatchRecord:
    return DispatchRecord(
        task_id="task-openai-usage",
        dispatch_id="dispatch-openai-usage",
        created_at="2026-08-07T10:00:00+00:00",
        task="Classify the bounded records.",
        task_type="high_volume_simple",
        risk_level="low",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["classification"],
        selected_implementation=choice("gpt-5.6-luna", "openai", "low"),
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


def test_openai_response_usage_is_normalized(tmp_path: Path) -> None:
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        payload = {
            "id": "resp_usage",
            "model": "gpt-5.6-luna",
            "status": "completed",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "label_a"}],
                }
            ],
            "usage": {
                "input_tokens": 100,
                "input_tokens_details": {
                    "cached_tokens": 40,
                    "cache_write_tokens": 10,
                },
                "output_tokens": 20,
                "output_tokens_details": {"reasoning_tokens": 12},
                "total_tokens": 120,
            },
        }
        return 200, {"x-request-id": "req_usage"}, json.dumps(payload).encode("utf-8")

    connection = HeaderProviderConnection(
        provider_family="openai",
        authorization_headers={"authorization": "Bearer secret-test-token"},
        transport=transport,
    )
    response = execute_openai_canary_once(dispatch(), connection, artifact_dir=tmp_path)

    assert response.status == "succeeded"
    assert response.usage is not None
    assert response.usage.input_tokens == 100
    assert response.usage.cached_input_tokens == 40
    assert response.usage.cache_creation_input_tokens == 10
    assert response.usage.output_tokens == 20
    assert response.usage.reasoning_output_tokens == 12
    assert response.usage.total_tokens == 120
