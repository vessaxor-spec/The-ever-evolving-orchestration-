from __future__ import annotations

import json
import re
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

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
CANARY_TASK_TYPES = {"high_volume_simple"}
CANARY_RISK_LEVELS = {"low", "medium"}
CANARY_MODELS = {"gpt-5.6-luna"}
OPENAI_REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}
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

    parts: list[str] = []
    output = payload.get("output")
    if not isinstance(output, list):
        return ""
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "output_text"
                and isinstance(block.get("text"), str)
            ):
                parts.append(block["text"])
    return "\n".join(part for part in parts if part).strip()


def _error_details(payload: dict[str, Any] | None) -> tuple[str, str]:
    if not payload:
        return "unknown_provider_error", "OpenAI returned an unreadable error response"
    error = payload.get("error")
    if isinstance(error, dict):
        code = error.get("code") or error.get("type") or "unknown_provider_error"
        message = error.get("message") or "OpenAI returned an error"
        return str(code), str(message)
    return "unknown_provider_error", "OpenAI returned an error"


def _failure_scope(status_code: int, code: str) -> str:
    normalized = code.lower()
    if status_code in {400, 409, 422} or normalized in {
        "invalid_request_error",
        "invalid_request",
        "bad_request",
    }:
        return "request"
    if status_code == 404 or "model_not_found" in normalized:
        return "model"
    if status_code == 413 or "context_length" in normalized or "too_large" in normalized:
        return "capability"
    if status_code in {401, 402, 403, 429} or any(
        token in normalized
        for token in ("authentication", "permission", "billing", "quota", "rate_limit")
    ):
        return "provider"
    if status_code in {408, 425, 500, 502, 503, 504} or "timeout" in normalized:
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
    input_tokens = _non_negative_int(raw.get("input_tokens"))
    output_tokens = _non_negative_int(raw.get("output_tokens"))
    total_tokens = _non_negative_int(raw.get("total_tokens"))
    input_details = raw.get("input_tokens_details")
    output_details = raw.get("output_tokens_details")
    cached = (
        _non_negative_int(input_details.get("cached_tokens"))
        if isinstance(input_details, dict)
        else None
    )
    cache_write = (
        _non_negative_int(input_details.get("cache_write_tokens"))
        if isinstance(input_details, dict)
        else None
    )
    reasoning = (
        _non_negative_int(output_details.get("reasoning_tokens"))
        if isinstance(output_details, dict)
        else None
    )
    if all(
        item is None
        for item in (input_tokens, output_tokens, cached, cache_write, reasoning, total_tokens)
    ):
        return None
    return ProviderUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached,
        cache_creation_input_tokens=cache_write,
        reasoning_output_tokens=reasoning,
        total_tokens=total_tokens,
    )


class OpenAIResponsesAdapter:
    """Single-attempt OpenAI Responses adapter for the guarded TEO canary."""

    provider_family = "openai"

    def __init__(
        self,
        connection: ProviderConnection,
        artifact_dir: str | Path = ".teo/runtime/artifacts/openai",
        timeout_seconds: float = 30.0,
    ) -> None:
        if connection.provider_family != self.provider_family:
            raise ProviderAdapterContractError(
                "OpenAI adapter requires an OpenAI provider connection"
            )
        self._connection = connection
        self._artifact_dir = Path(artifact_dir)
        self._timeout_seconds = float(timeout_seconds)

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        if request.provider_family != self.provider_family:
            raise ProviderAdapterContractError("OpenAI adapter received a non-OpenAI request")
        if request.risk_level not in CANARY_RISK_LEVELS:
            raise ProviderAdapterContractError(
                "OpenAI live canary is restricted to low and medium risk execution"
            )
        if request.model not in CANARY_MODELS:
            raise ProviderAdapterContractError(
                "OpenAI live canary is restricted to GPT-5.6 Luna"
            )
        if request.reasoning_effort is not None and request.reasoning_effort not in OPENAI_REASONING_EFFORTS:
            raise ProviderAdapterContractError(
                f"OpenAI does not support TEO reasoning effort {request.reasoning_effort}"
            )

        task = request.input_payload.get("task")
        if not isinstance(task, str) or not task.strip():
            raise ProviderAdapterContractError("OpenAI canary input_payload.task must be non-empty text")

        raw_max_tokens = request.input_payload.get("max_output_tokens", 512)
        if not isinstance(raw_max_tokens, int) or isinstance(raw_max_tokens, bool):
            raise ProviderAdapterContractError("max_output_tokens must be an integer")
        if raw_max_tokens < 1 or raw_max_tokens > MAX_CANARY_OUTPUT_TOKENS:
            raise ProviderAdapterContractError(
                f"max_output_tokens must be between 1 and {MAX_CANARY_OUTPUT_TOKENS} for the canary"
            )

        payload: dict[str, Any] = {
            "model": request.model,
            "input": task,
            "max_output_tokens": raw_max_tokens,
            "store": False,
        }
        if request.reasoning_effort is not None:
            payload["reasoning"] = {"effort": request.reasoning_effort}

        try:
            connection_response = self._connection.invoke(
                ProviderConnectionRequest(
                    operation="responses.create",
                    url=OPENAI_RESPONSES_URL,
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
                        message="OpenAI returned a non-JSON success response",
                    ),
                )
            provider_model = response_payload.get("model") if isinstance(response_payload.get("model"), str) else None
            if provider_model and provider_model != request.model:
                raise ProviderAdapterContractError(
                    "OpenAI response reported a model different from the dispatch-authorized model"
                )
            response_status = response_payload.get("status")
            if response_status in {"failed", "cancelled"}:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="provider",
                        code=f"response_{response_status}",
                        message=f"OpenAI response ended with status {response_status}",
                    ),
                    usage=usage,
                )
            if response_status == "incomplete":
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="capability",
                        code="incomplete_response",
                        message="OpenAI response was incomplete within the authorized canary limits",
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
                        message="OpenAI returned no text content for the canary task",
                    ),
                    usage=usage,
                )
            self._artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = self._artifact_dir / f"{_safe_artifact_name(request.dispatch_id)}.txt"
            artifact_path.write_text(text + "\n", encoding="utf-8")
            evidence: list[str] = []
            response_id = response_payload.get("id")
            if isinstance(response_id, str):
                evidence.append(f"openai_response_id:{response_id}")
            if request_id:
                evidence.append(f"openai_request_id:{request_id}")
            if provider_model:
                evidence.append(f"openai_response_model:{provider_model}")
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
            evidence=(f"openai_request_id:{request_id}",) if request_id else (),
            failure=ProviderFailure(
                scope=_failure_scope(status_code, code),  # type: ignore[arg-type]
                code=code,
                message=message,
            ),
            retry_after_seconds=retry_after_seconds_from_headers(connection_response.headers),
            usage=usage,
        )


def execute_openai_canary_once(
    dispatch: DispatchRecord,
    connection: ProviderConnection,
    input_payload: dict[str, Any] | None = None,
    *,
    artifact_dir: str | Path = ".teo/runtime/artifacts/openai",
    timeout_seconds: float = 30.0,
) -> ProviderExecutionResponse:
    """Execute one live OpenAI canary attempt while preserving TEO routing authority."""
    if dispatch.task_type not in CANARY_TASK_TYPES:
        raise ProviderAdapterContractError(
            "Live OpenAI canary is authorized only for high_volume_simple dispatches"
        )
    if dispatch.risk_level not in CANARY_RISK_LEVELS:
        raise ProviderAdapterContractError(
            "Live OpenAI canary refuses high and critical risk dispatches"
        )
    if dispatch.selected_implementation.provider_family != "openai":
        raise ProviderAdapterContractError(
            "Live OpenAI canary requires an OpenAI-selected dispatch"
        )
    if dispatch.selected_implementation.model not in CANARY_MODELS:
        raise ProviderAdapterContractError(
            "Live OpenAI canary requires a GPT-5.6 Luna selected implementation"
        )

    adapter = OpenAIResponsesAdapter(
        connection,
        artifact_dir=artifact_dir,
        timeout_seconds=timeout_seconds,
    )
    request = ProviderExecutionRequest.from_dispatch(dispatch, input_payload)
    response = adapter.execute(request)
    validate_provider_response(dispatch, request, response)
    return response
