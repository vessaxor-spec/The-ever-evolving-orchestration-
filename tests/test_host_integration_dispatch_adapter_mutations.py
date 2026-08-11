from __future__ import annotations

import json
import runpy
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

import pytest

from teo_reference.anthropic_adapter import AnthropicMessagesAdapter
from teo_reference.google_adapter import GeminiInteractionsAdapter
from teo_reference.openai_adapter import OpenAIResponsesAdapter
from teo_reference.provider_adapter import (
    ProviderExecutionRequest,
    ProviderExecutionResponse,
    execute_provider_once,
)
from teo_reference.provider_connection import (
    ProviderConnectionRequest,
    ProviderConnectionResponse,
)
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_dispatch_authorization.py"
RESEARCH = runpy.run_path(str(HARNESS))
DispatchAuthorizationError = RESEARCH["DispatchAuthorizationError"]
ProcessLocalDispatchAuthority = RESEARCH["ProcessLocalDispatchAuthority"]
execute_authorized_provider_once = RESEARCH["execute_authorized_provider_once"]


def choice(model: str, provider: str, *, agent: str = "host-test") -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="host-integration-research",
    )


def dispatch(*, provider: str = "openai", model: str = "gpt-5.6-sol") -> DispatchRecord:
    return DispatchRecord(
        task_id="task-host-boundary",
        dispatch_id="dispatch-host-boundary",
        created_at="2026-08-12T00:00:00+00:00",
        task="Return a bounded text result.",
        task_type="high_volume_simple",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist="backend-engineer",
        specialist_source="community/specialists/backend-engineer.md",
        specialist_risk_profile="medium",
        required_capabilities=["tool_execution"],
        selected_implementation=choice(model, provider),
        fallback_implementation=choice("gemini-3.6-flash", "google"),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice("claude-sonnet-5", "anthropic", agent="claude"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["research fixture"],
        warnings=[],
    )


class RecordingSuccessAdapter:
    provider_family = "openai"

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        self.calls += 1
        return ProviderExecutionResponse(
            dispatch_id=request.dispatch_id,
            status="succeeded",
            provider_family=request.provider_family,
            model=request.model,
            output_ref="artifact://host-boundary-result",
        )


def test_generic_executor_does_not_prove_dispatch_provenance() -> None:
    # This documents the host-integration gap: a syntactically valid record assembled by
    # the caller is sufficient for the generic adapter executor. It is not a claim that
    # current guarded live wrappers authorize arbitrary task classes.
    adapter = RecordingSuccessAdapter()
    result = execute_provider_once(adapter, dispatch())
    assert result.status == "succeeded"
    assert adapter.calls == 1


def test_research_authority_accepts_only_the_exact_issued_dispatch() -> None:
    authority = ProcessLocalDispatchAuthority()
    issued = dispatch()
    token = authority.issue(issued)
    adapter = RecordingSuccessAdapter()

    result = execute_authorized_provider_once(authority, token, adapter, issued)

    assert result.status == "succeeded"
    assert adapter.calls == 1


def _mutate(field: str) -> Callable[[DispatchRecord], None]:
    def mutate(candidate: DispatchRecord) -> None:
        if field == "dispatch_id":
            candidate.dispatch_id = "dispatch-forged"
        elif field == "task_id":
            candidate.task_id = "task-forged"
        elif field == "task_type":
            candidate.task_type = "documentation"
        elif field == "risk_level":
            candidate.risk_level = "low"
        elif field == "selected_team":
            candidate.selected_team = "research"
        elif field == "selected_worker":
            candidate.selected_worker = "research"
        elif field == "selected_specialist":
            candidate.selected_specialist = "agents-orchestrator"
        elif field == "required_capabilities":
            candidate.required_capabilities = ["tool_execution", "web_research"]
        elif field == "provider_family":
            candidate.selected_implementation.provider_family = "google"
        elif field == "model":
            candidate.selected_implementation.model = "gpt-5.6-luna"
        elif field == "fallback":
            candidate.fallback_implementation = None
        elif field == "verifier":
            candidate.verification.implementation.model = "claude-opus-5"
        elif field == "human_approval":
            candidate.verification.human_approval_required = True
        elif field == "status":
            candidate.status = "host-authorized"
        else:  # pragma: no cover - parametrization guard
            raise AssertionError(field)

    return mutate


@pytest.mark.parametrize(
    "field",
    [
        "dispatch_id",
        "task_id",
        "task_type",
        "risk_level",
        "selected_team",
        "selected_worker",
        "selected_specialist",
        "required_capabilities",
        "provider_family",
        "model",
        "fallback",
        "verifier",
        "human_approval",
        "status",
    ],
)
def test_authority_kills_dispatch_tampering_before_adapter_execution(field: str) -> None:
    authority = ProcessLocalDispatchAuthority()
    issued = dispatch()
    token = authority.issue(issued)
    tampered = deepcopy(issued)
    _mutate(field)(tampered)
    adapter = RecordingSuccessAdapter()

    with pytest.raises(DispatchAuthorizationError, match="differs"):
        execute_authorized_provider_once(authority, token, adapter, tampered)

    assert adapter.calls == 0


def test_unissued_token_cannot_authorize_an_otherwise_valid_dispatch() -> None:
    authority = ProcessLocalDispatchAuthority()
    adapter = RecordingSuccessAdapter()

    with pytest.raises(DispatchAuthorizationError, match="not issued"):
        execute_authorized_provider_once(authority, "host-forged-token", adapter, dispatch())

    assert adapter.calls == 0


def test_token_is_bound_to_one_exact_dispatch_snapshot() -> None:
    authority = ProcessLocalDispatchAuthority()
    first = dispatch()
    token = authority.issue(first)
    second = deepcopy(first)
    second.dispatch_id = "dispatch-second"
    adapter = RecordingSuccessAdapter()

    with pytest.raises(DispatchAuthorizationError, match="differs"):
        execute_authorized_provider_once(authority, token, adapter, second)

    assert adapter.calls == 0


class CaptureConnection:
    def __init__(self, provider_family: str) -> None:
        self.provider_family = provider_family
        self.requests: list[ProviderConnectionRequest] = []

    def invoke(self, request: ProviderConnectionRequest) -> ProviderConnectionResponse:
        self.requests.append(request)
        if self.provider_family == "anthropic":
            body = b'{"type":"error","error":{"type":"invalid_request_error","message":"stop"}}'
        elif self.provider_family == "google":
            body = b'{"error":{"status":"INVALID_ARGUMENT","message":"stop"}}'
        else:
            body = b'{"error":{"code":"invalid_request_error","message":"stop"}}'
        return ProviderConnectionResponse(status_code=400, headers={}, body=body)


FORBIDDEN_EXPANSION_KEYS = {
    "tools",
    "tool_choice",
    "web_search",
    "mcp_servers",
    "fallback_model",
    "fallback_provider",
}


def _assert_no_keys(value: Any, forbidden: set[str]) -> None:
    if isinstance(value, dict):
        assert not forbidden.intersection(value), value
        for nested in value.values():
            _assert_no_keys(nested, forbidden)
    elif isinstance(value, list):
        for nested in value:
            _assert_no_keys(nested, forbidden)


@pytest.mark.parametrize(
    ("provider", "model", "adapter_factory"),
    [
        ("openai", "gpt-5.6-sol", OpenAIResponsesAdapter),
        ("anthropic", "claude-sonnet-5", AnthropicMessagesAdapter),
        ("google", "gemini-3.6-flash", GeminiInteractionsAdapter),
    ],
)
def test_bundled_adapters_do_not_forward_payload_driven_execution_expansion(
    provider: str,
    model: str,
    adapter_factory: type,
) -> None:
    connection = CaptureConnection(provider)
    adapter = adapter_factory(connection)
    routed = dispatch(provider=provider, model=model)
    malicious_payload = {
        "task": routed.task,
        "max_output_tokens": 64,
        "tools": [{"type": "computer_use"}],
        "tool_choice": "required",
        "web_search": True,
        "mcp_servers": ["host-controlled"],
        "fallback_model": "host-selected-model",
        "fallback_provider": "host-selected-provider",
    }
    request = ProviderExecutionRequest.from_dispatch(routed, malicious_payload)

    adapter.execute(request)

    assert len(connection.requests) == 1
    outbound = json.loads(connection.requests[0].body.decode("utf-8"))
    _assert_no_keys(outbound, FORBIDDEN_EXPANSION_KEYS)
    assert outbound["model"] == model


def test_payload_cannot_override_dispatch_model_or_provider_before_bundled_adapter() -> None:
    routed = dispatch(provider="openai", model="gpt-5.6-sol")
    request = ProviderExecutionRequest.from_dispatch(
        routed,
        {
            "task": routed.task,
            "model": "host-selected-model",
            "provider_family": "google",
        },
    )

    assert request.model == "gpt-5.6-sol"
    assert request.provider_family == "openai"
    assert request.input_payload["model"] == "host-selected-model"
    assert request.input_payload["provider_family"] == "google"
