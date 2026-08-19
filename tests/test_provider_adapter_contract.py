from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from teo_reference.provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionRequest,
    ProviderExecutionResponse,
    ProviderFailure,
    execute_provider_once,
)
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


REPO_ROOT = Path(__file__).resolve().parents[1]


def choice(
    model: str,
    provider_family: str,
    *,
    agent: str,
    profile: str = "sol",
) -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile=profile,
        provider_family=provider_family,
        availability="current",
        source="test-route",
    )


def dispatch() -> DispatchRecord:
    return DispatchRecord(
        task_id="task-provider-contract",
        dispatch_id="dispatch-provider-contract",
        created_at="2026-08-07T07:00:00+00:00",
        task="Implement the approved change and produce an artifact.",
        task_type="daily_coding",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["coding", "tool_execution"],
        selected_implementation=choice(
            "gpt-5.6-terra", "openai", agent="codex", profile="terra"
        ),
        fallback_implementation=choice(
            "gemini-3.1-pro", "google", agent="gemini"
        ),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation", "targeted_review"],
            implementation=choice("claude-sonnet-5", "anthropic", agent="claude"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=[],
        warnings=[],
    )


class SuccessAdapter:
    provider_family = "openai"

    def __init__(self) -> None:
        self.requests: list[ProviderExecutionRequest] = []

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        self.requests.append(request)
        return ProviderExecutionResponse(
            dispatch_id=request.dispatch_id,
            status="succeeded",
            provider_family=request.provider_family,
            model=request.model,
            output_ref="artifact://provider-output",
            evidence=("provider attempt completed",),
        )


class FailedAdapter:
    provider_family = "openai"

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        self.calls += 1
        return ProviderExecutionResponse(
            dispatch_id=request.dispatch_id,
            status="failed",
            provider_family=request.provider_family,
            model=request.model,
            failure=ProviderFailure(
                scope="provider",
                code="service_unavailable",
                message="Provider service unavailable",
            ),
        )


def test_request_is_bound_to_dispatch_without_fallback_or_verifier_authority() -> None:
    request = ProviderExecutionRequest.from_dispatch(dispatch())
    payload = request.to_dict()

    assert payload["contract_version"] == "1"
    assert payload["provider_family"] == "openai"
    assert payload["model"] == "gpt-5.6-terra"
    assert payload["input_payload"] == {
        "task": "Implement the approved change and produce an artifact."
    }
    assert "fallback_implementation" not in payload
    assert "verification" not in payload
    assert "human_approval_required" not in payload


def test_matching_adapter_executes_once_and_normalizes_existing_execution_result() -> None:
    adapter = SuccessAdapter()
    execution = execute_provider_once(adapter, dispatch())

    assert len(adapter.requests) == 1
    assert execution.dispatch_id == "dispatch-provider-contract"
    assert execution.status == "succeeded"
    assert execution.output_ref == "artifact://provider-output"
    assert execution.evidence == ["provider attempt completed"]
    assert execution.failed_attempts == 0


def test_adapter_provider_mismatch_fails_before_execution() -> None:
    class WrongProviderAdapter(SuccessAdapter):
        provider_family = "google"

    adapter = WrongProviderAdapter()
    with pytest.raises(ProviderAdapterContractError, match="provider family"):
        execute_provider_once(adapter, dispatch())
    assert adapter.requests == []


def test_adapter_cannot_report_execution_by_a_different_model() -> None:
    class WrongModelAdapter:
        provider_family = "openai"

        def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
            return ProviderExecutionResponse(
                dispatch_id=request.dispatch_id,
                status="succeeded",
                provider_family=request.provider_family,
                model="gpt-5.6-sol",
                output_ref="artifact://wrong-model",
            )

    with pytest.raises(ProviderAdapterContractError, match="changed the selected implementation model"):
        execute_provider_once(WrongModelAdapter(), dispatch())


def test_adapter_must_return_normalized_response_not_provider_native_payload() -> None:
    class NativePayloadAdapter:
        provider_family = "openai"

        def execute(self, request: ProviderExecutionRequest):
            return {"id": "provider-native-response"}

    with pytest.raises(ProviderAdapterContractError, match="ProviderExecutionResponse"):
        execute_provider_once(NativePayloadAdapter(), dispatch())


def test_failed_attempt_is_normalized_without_executing_fallback() -> None:
    adapter = FailedAdapter()
    execution = execute_provider_once(adapter, dispatch())

    assert adapter.calls == 1
    assert execution.status == "failed"
    assert execution.failed_attempts == 1
    assert execution.output_ref is None


def test_success_and_failure_states_fail_closed() -> None:
    with pytest.raises(ProviderAdapterContractError, match="output_ref"):
        ProviderExecutionResponse(
            dispatch_id="dispatch-provider-contract",
            status="succeeded",
            provider_family="openai",
            model="gpt-5.6-terra",
        )

    with pytest.raises(ProviderAdapterContractError, match="failure details"):
        ProviderExecutionResponse(
            dispatch_id="dispatch-provider-contract",
            status="failed",
            provider_family="openai",
            model="gpt-5.6-terra",
        )


def test_failure_scope_is_bounded_to_routing_taxonomy() -> None:
    with pytest.raises(ProviderAdapterContractError, match="failure scope"):
        ProviderFailure(
            scope="mystery",  # type: ignore[arg-type]
            code="unknown",
            message="Unclassified failure",
        )


@pytest.mark.parametrize(
    "credential_key",
    [
        "api_key",
        "access_token",
        "refresh_token",
        "client_secret",
        "private_key",
        "service_account_key",
        "session_token",
        "authorization_code",
        "vendor-access-token",
        "nested_private_key",
    ],
)
def test_credentials_cannot_enter_serialized_execution_payload(credential_key: str) -> None:
    with pytest.raises(ProviderAdapterContractError, match="Credential material"):
        ProviderExecutionRequest.from_dispatch(
            dispatch(),
            {
                "messages": [{"role": "user", "content": "run"}],
                "nested": {credential_key: "secret"},
            },
        )


def test_noncredential_token_word_is_not_rejected_by_substring_only() -> None:
    request = ProviderExecutionRequest.from_dispatch(
        dispatch(),
        {"token_count": 12, "task": "run"},
    )
    assert request.input_payload["token_count"] == 12


def test_contract_rejects_unknown_fields() -> None:
    request = ProviderExecutionRequest.from_dispatch(dispatch()).to_dict()
    request["fallback_model"] = "gemini-3.1-pro"
    with pytest.raises(ProviderAdapterContractError, match="unsupported fields"):
        ProviderExecutionRequest.from_dict(request)

    response = ProviderExecutionResponse(
        dispatch_id="dispatch-provider-contract",
        status="succeeded",
        provider_family="openai",
        model="gpt-5.6-terra",
        output_ref="artifact://provider-output",
    ).to_dict()
    response["verifier_model"] = "claude-sonnet-5"
    with pytest.raises(ProviderAdapterContractError, match="unsupported fields"):
        ProviderExecutionResponse.from_dict(response)


def test_json_schemas_validate_reference_envelopes() -> None:
    request_schema = json.loads(
        (REPO_ROOT / "reference/schemas/provider-execution-request.schema.json").read_text(
            encoding="utf-8"
        )
    )
    response_schema = json.loads(
        (REPO_ROOT / "reference/schemas/provider-execution-response.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(request_schema)
    Draft202012Validator.check_schema(response_schema)

    request = ProviderExecutionRequest.from_dispatch(dispatch()).to_dict()
    success = ProviderExecutionResponse(
        dispatch_id="dispatch-provider-contract",
        status="succeeded",
        provider_family="openai",
        model="gpt-5.6-terra",
        output_ref="artifact://provider-output",
    ).to_dict()
    failure = ProviderExecutionResponse(
        dispatch_id="dispatch-provider-contract",
        status="failed",
        provider_family="openai",
        model="gpt-5.6-terra",
        failure=ProviderFailure(
            scope="transient",
            code="timeout",
            message="Provider request timed out",
        ),
    ).to_dict()

    Draft202012Validator(request_schema).validate(request)
    Draft202012Validator(response_schema).validate(success)
    Draft202012Validator(response_schema).validate(failure)
