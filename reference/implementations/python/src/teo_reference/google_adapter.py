from __future__ import annotations

import json
import re
from math import isfinite
from pathlib import Path
from typing import Any

from .provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionRequest,
    ProviderExecutionResponse,
    ProviderFailure,
    ProviderUsage,
    retry_after_seconds_from_headers,
    validate_provider_response,
)
from .provider_connection import (
    ProviderConnection,
    ProviderConnectionError,
    ProviderConnectionRequest,
)
from .schemas import DispatchRecord

GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1/interactions"
CANARY_TASK_TYPES = {"high_volume_simple"}
CANARY_RISK_LEVELS = {"low", "medium"}
CANARY_MODELS = {"gemini-3.7-flash", "gemini-3.1-pro"}
GEMINI_REASONING_EFFORTS = {"minimal", "low", "medium", "high"}
MAX_CANARY_OUTPUT_TOKENS = 1024


def _safe_artifact_name(dispatch_id: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9._-]+", "-", dispatch_id).strip("-.")
    return normalized or "provider-output"


def _decode_json(body: bytes) -> dict[str, Any] | None:
    try:
        decoded = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return decoded if isinstance(decoded, dict) else None


def _extract_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    text_parts: list[str] = []
    steps = payload.get("steps")
    if not isinstance(steps, list):
        return ""
    for step in steps:
        if not isinstance(step, dict) or step.get("type") != "model_output":
            continue
        content = step.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "text"
                and isinstance(block.get("text"), str)
            ):
                text_parts.append(block["text"])
    return "\n".join(part for part in text_parts if part).strip()


def _error_details(payload: dict[str, Any] | None) -> tuple[str, str]:
    if not payload:
        return "unknown_provider_error", "Google returned an unreadable error response"
    error = payload.get("error")
    if isinstance(error, dict):
        status = error.get("status") or error.get("code") or "unknown_provider_error"
        message = error.get("message") or "Google returned an error"
        return str(status), str(message)
    return "unknown_provider_error", "Google returned an error"


def _retry_info_seconds(payload: dict[str, Any] | None) -> float | None:
    """Read standard google.rpc.RetryInfo when a Google error response includes it."""
    if not payload:
        return None
    error = payload.get("error")
    if not isinstance(error, dict):
        return None
    details = error.get("details")
    if not isinstance(details, list):
        return None
    for detail in details:
        if not isinstance(detail, dict):
            continue
        type_name = str(detail.get("@type") or detail.get("type") or "")
        if not type_name.endswith("google.rpc.RetryInfo"):
            continue
        value = detail.get("retryDelay") or detail.get("retry_delay")
        if isinstance(value, str) and value.endswith("s"):
            try:
                seconds = float(value[:-1])
            except ValueError:
                return None
            if isfinite(seconds) and seconds >= 0:
                return seconds
    return None


def _retry_after_seconds(headers: dict[str, str] | Any, payload: dict[str, Any] | None) -> float | None:
    header_value = retry_after_seconds_from_headers(headers)
    if header_value is not None:
        return header_value
    return _retry_info_seconds(payload)


def _failure_scope(status_code: int, code: str) -> str:
    normalized = code.lower()
    if status_code in {400, 409, 422} or normalized in {
        "invalid_argument",
        "failed_precondition",
    }:
        return "request"
    if status_code == 404 or normalized == "not_found":
        return "model"
    if status_code == 413 or "too_large" in normalized or "resource_exhausted_context" in normalized:
        return "capability"
    if status_code in {401, 402, 403, 429} or normalized in {
        "unauthenticated",
        "permission_denied",
        "resource_exhausted",
    }:
        return "provider"
    if status_code in {408, 425, 500, 502, 503, 504} or normalized in {
        "deadline_exceeded",
        "unavailable",
        "internal",
    }:
        return "transient"
    if 500 <= status_code < 600:
        return "transient"
    return "provider"


def _non_negative_int(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def _extract_usage(payload: dict[str, Any]) -> ProviderUsage | None:
    raw = payload.get("usage")
    if not isinstance(raw, dict):
        return None
    input_tokens = _non_negative_int(raw.get("total_input_tokens"))
    output_tokens = _non_negative_int(raw.get("total_output_tokens"))
    cached = _non_negative_int(raw.get("total_cached_tokens"))
    reasoning = _non_negative_int(raw.get("total_thought_tokens"))
    tool_tokens = _non_negative_int(raw.get("total_tool_use_tokens"))
    total_tokens = _non_negative_int(raw.get("total_tokens"))
    if all(
        item is None
        for item in (input_tokens, output_tokens, cached, reasoning, tool_tokens, total_tokens)
    ):
        return None
    return ProviderUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached,
        reasoning_output_tokens=reasoning,
        tool_tokens=tool_tokens,
        total_tokens=total_tokens,
    )


class GeminiInteractionsAdapter:
    """Single-attempt Gemini Interactions adapter for the guarded TEO canary."""

    provider_family = "google"

    def __init__(
        self,
        connection: ProviderConnection,
        artifact_dir: str | Path = ".teo/runtime/artifacts/google",
        timeout_seconds: float = 30.0,
    ) -> None:
        if connection.provider_family != self.provider_family:
            raise ProviderAdapterContractError(
                "Gemini adapter requires a Google provider connection"
            )
        self._connection = connection
        self._artifact_dir = Path(artifact_dir)
        self._timeout_seconds = float(timeout_seconds)

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        if request.provider_family != self.provider_family:
            raise ProviderAdapterContractError("Gemini adapter received a non-Google request")
        if request.risk_level not in CANARY_RISK_LEVELS:
            raise ProviderAdapterContractError(
                "Gemini live canary is restricted to low and medium risk execution"
            )
        if request.model not in CANARY_MODELS:
            raise ProviderAdapterContractError(
                "Gemini live canary is restricted to the routed stable Gemini canary models"
            )
        if request.reasoning_effort is not None and request.reasoning_effort not in GEMINI_REASONING_EFFORTS:
            raise ProviderAdapterContractError(
                f"Selected Gemini canary model does not support TEO reasoning effort {request.reasoning_effort}"
            )

        task = request.input_payload.get("task")
        if not isinstance(task, str) or not task.strip():
            raise ProviderAdapterContractError("Gemini canary input_payload.task must be non-empty text")

        raw_max_tokens = request.input_payload.get("max_output_tokens", 512)
        if not isinstance(raw_max_tokens, int) or isinstance(raw_max_tokens, bool):
            raise ProviderAdapterContractError("max_output_tokens must be an integer")
        if raw_max_tokens < 1 or raw_max_tokens > MAX_CANARY_OUTPUT_TOKENS:
            raise ProviderAdapterContractError(
                f"max_output_tokens must be between 1 and {MAX_CANARY_OUTPUT_TOKENS} for the canary"
            )

        generation_config: dict[str, Any] = {"max_output_tokens": raw_max_tokens}
        if request.reasoning_effort is not None:
            generation_config["thinking_level"] = request.reasoning_effort
        payload = {
            "model": request.model,
            "input": task,
            "store": False,
            "generation_config": generation_config,
        }

        try:
            connection_response = self._connection.invoke(
                ProviderConnectionRequest(
                    operation="interactions.create",
                    url=GEMINI_INTERACTIONS_URL,
                    method="POST",
                    headers={"content-type": "application/json"},
                    body=json.dumps(payload).encode("utf-8"),
                    timeout_seconds=self._timeout_seconds,
                )
            )
        except ProviderConnectionError as exc:
            return ProviderExecutionResponse(
                dispatch_id=request.dispatch_id,
                status="failed",
                provider_family=request.provider_family,
                model=request.model,
                failure=ProviderFailure(
                    scope="transient",
                    code="connection_error",
                    message=str(exc),
                ),
            )

        status_code = connection_response.status_code
        response_payload = _decode_json(connection_response.body)
        request_id = (
            connection_response.headers.get("x-request-id")
            or connection_response.headers.get("request-id")
        )
        usage = _extract_usage(response_payload) if response_payload else None

        if 200 <= status_code < 300:
            if response_payload is None:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="provider",
                        code="invalid_provider_response",
                        message="Google returned a non-JSON success response",
                    ),
                )
            provider_model = response_payload.get("model") if isinstance(response_payload.get("model"), str) else None
            if provider_model and provider_model != request.model:
                raise ProviderAdapterContractError(
                    "Gemini response reported a model different from the dispatch-authorized model"
                )
            interaction_status = response_payload.get("status")
            if interaction_status in {"failed", "cancelled"}:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="provider",
                        code=f"interaction_{interaction_status}",
                        message=f"Gemini interaction ended with status {interaction_status}",
                    ),
                    usage=usage,
                )
            if interaction_status in {"incomplete", "budget_exceeded", "requires_action"}:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="capability",
                        code=f"interaction_{interaction_status}",
                        message=f"Gemini interaction could not complete as a bounded text canary: {interaction_status}",
                    ),
                    usage=usage,
                )
            text = _extract_text(response_payload)
            if not text:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="capability",
                        code="no_text_output",
                        message="Gemini returned no text content for the canary task",
                    ),
                    usage=usage,
                )
            self._artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = self._artifact_dir / f"{_safe_artifact_name(request.dispatch_id)}.txt"
            artifact_path.write_text(text + "\n", encoding="utf-8")
            evidence: list[str] = []
            interaction_id = response_payload.get("id")
            if isinstance(interaction_id, str):
                evidence.append(f"gemini_interaction_id:{interaction_id}")
            if request_id:
                evidence.append(f"google_request_id:{request_id}")
            if provider_model:
                evidence.append(f"gemini_response_model:{provider_model}")
            if request.reasoning_effort:
                evidence.append(f"teo_reasoning_effort:{request.reasoning_effort}")
            return ProviderExecutionResponse(
                dispatch_id=request.dispatch_id,
                status="succeeded",
                provider_family=request.provider_family,
                model=request.model,
                output_ref=artifact_path.resolve().as_uri(),
                evidence=tuple(evidence),
                usage=usage,
            )

        code, message = _error_details(response_payload)
        return ProviderExecutionResponse(
            dispatch_id=request.dispatch_id,
            status="failed",
            provider_family=request.provider_family,
            model=request.model,
            evidence=(f"google_request_id:{request_id}",) if request_id else (),
            failure=ProviderFailure(
                scope=_failure_scope(status_code, code),  # type: ignore[arg-type]
                code=code,
                message=message,
            ),
            retry_after_seconds=_retry_after_seconds(connection_response.headers, response_payload),
            usage=usage,
        )


def execute_gemini_canary_once(
    dispatch: DispatchRecord,
    connection: ProviderConnection,
    input_payload: dict[str, Any] | None = None,
    *,
    artifact_dir: str | Path = ".teo/runtime/artifacts/google",
    timeout_seconds: float = 30.0,
) -> ProviderExecutionResponse:
    """Execute one live Gemini canary attempt while preserving TEO routing authority."""
    if dispatch.task_type not in CANARY_TASK_TYPES:
        raise ProviderAdapterContractError(
            "Live Gemini canary is authorized only for high_volume_simple dispatches"
        )
    if dispatch.risk_level not in CANARY_RISK_LEVELS:
        raise ProviderAdapterContractError(
            "Live Gemini canary refuses high and critical risk dispatches"
        )
    if dispatch.selected_implementation.provider_family != "google":
        raise ProviderAdapterContractError(
            "Live Gemini canary requires a Google-selected dispatch"
        )
    if dispatch.selected_implementation.model not in CANARY_MODELS:
        raise ProviderAdapterContractError(
            "Live Gemini canary requires a Gemini 3.6 Flash selected implementation"
        )

    adapter = GeminiInteractionsAdapter(
        connection,
        artifact_dir=artifact_dir,
        timeout_seconds=timeout_seconds,
    )
    request = ProviderExecutionRequest.from_dispatch(dispatch, input_payload)
    response = adapter.execute(request)
    validate_provider_response(dispatch, request, response)
    return response
