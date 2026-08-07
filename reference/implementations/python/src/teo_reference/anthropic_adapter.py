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
    validate_provider_response,
)
from .provider_connection import (
    ProviderConnection,
    ProviderConnectionError,
    ProviderConnectionRequest,
)
from .schemas import DispatchRecord

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
CANARY_TASK_TYPES = {"high_volume_simple"}
CANARY_RISK_LEVELS = {"low", "medium"}
CANARY_MODELS = {"claude-haiku-4-5", "claude-haiku-4-5-20251001"}
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


def _error_details(payload: dict[str, Any] | None) -> tuple[str, str]:
    if not payload:
        return "unknown_provider_error", "Anthropic returned an unreadable error response"
    error = payload.get("error")
    if isinstance(error, dict):
        error_type = str(error.get("type") or "unknown_provider_error")
        message = str(error.get("message") or "Anthropic returned an error")
        return error_type, message
    return str(payload.get("type") or "unknown_provider_error"), "Anthropic returned an error"


def _failure_scope(status_code: int, error_type: str) -> str:
    if error_type in {"authentication_error", "billing_error", "permission_error", "rate_limit_error"}:
        return "provider"
    if error_type == "not_found_error":
        return "model"
    if error_type == "request_too_large" or status_code == 413:
        return "capability"
    if error_type in {"invalid_request_error", "conflict_error"} or status_code in {400, 409, 422}:
        return "request"
    if error_type == "overloaded_error" or status_code == 529:
        return "provider"
    if error_type in {"api_error", "timeout_error"} or status_code in {408, 425, 500, 502, 503, 504}:
        return "transient"
    if status_code in {401, 402, 403, 429}:
        return "provider"
    if status_code == 404:
        return "model"
    if 500 <= status_code < 600:
        return "transient"
    return "provider"


def _extract_text(payload: dict[str, Any]) -> str:
    blocks = payload.get("content")
    if not isinstance(blocks, list):
        return ""
    text_parts: list[str] = []
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
            text_parts.append(block["text"])
    return "\n".join(part for part in text_parts if part).strip()


def _provider_model_matches(requested_model: str, provider_model: str | None) -> bool:
    if not provider_model:
        return True
    if requested_model == provider_model:
        return True
    haiku_aliases = {"claude-haiku-4-5", "claude-haiku-4-5-20251001"}
    return requested_model in haiku_aliases and provider_model in haiku_aliases


class AnthropicMessagesAdapter:
    """Single-attempt Anthropic Messages adapter for the guarded TEO canary.

    Routing selects Anthropic and Claude Haiku 4.5. The injected ProviderConnection owns
    how that provider is reached and authorized. The adapter never branches on connection type.
    """

    provider_family = "anthropic"

    def __init__(
        self,
        connection: ProviderConnection,
        artifact_dir: str | Path = ".teo/runtime/artifacts/anthropic",
        timeout_seconds: float = 30.0,
    ) -> None:
        if connection.provider_family != self.provider_family:
            raise ProviderAdapterContractError(
                "Anthropic adapter requires an Anthropic provider connection"
            )
        self._connection = connection
        self._artifact_dir = Path(artifact_dir)
        self._timeout_seconds = float(timeout_seconds)

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        if request.provider_family != self.provider_family:
            raise ProviderAdapterContractError("Anthropic adapter received a non-Anthropic request")
        if request.risk_level not in CANARY_RISK_LEVELS:
            raise ProviderAdapterContractError(
                "Anthropic live canary is restricted to low and medium risk execution"
            )
        if request.model not in CANARY_MODELS:
            raise ProviderAdapterContractError(
                "Anthropic live canary is restricted to Claude Haiku 4.5"
            )

        task = request.input_payload.get("task")
        if not isinstance(task, str) or not task.strip():
            raise ProviderAdapterContractError("Anthropic canary input_payload.task must be non-empty text")

        raw_max_tokens = request.input_payload.get("max_output_tokens", 512)
        if not isinstance(raw_max_tokens, int) or isinstance(raw_max_tokens, bool):
            raise ProviderAdapterContractError("max_output_tokens must be an integer")
        if raw_max_tokens < 1 or raw_max_tokens > MAX_CANARY_OUTPUT_TOKENS:
            raise ProviderAdapterContractError(
                f"max_output_tokens must be between 1 and {MAX_CANARY_OUTPUT_TOKENS} for the canary"
            )

        body = json.dumps(
            {
                "model": request.model,
                "max_tokens": raw_max_tokens,
                "messages": [{"role": "user", "content": task}],
            }
        ).encode("utf-8")

        try:
            connection_response = self._connection.invoke(
                ProviderConnectionRequest(
                    operation="messages.create",
                    url=ANTHROPIC_MESSAGES_URL,
                    method="POST",
                    headers={
                        "content-type": "application/json",
                        "anthropic-version": ANTHROPIC_VERSION,
                    },
                    body=body,
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
        response_headers = connection_response.headers
        response_body = connection_response.body
        payload = _decode_json(response_body)
        request_id = response_headers.get("request-id") or response_headers.get("request_id")
        if not request_id and payload:
            request_id = payload.get("request_id") if isinstance(payload.get("request_id"), str) else None

        if 200 <= status_code < 300:
            if payload is None:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="provider",
                        code="invalid_provider_response",
                        message="Anthropic returned a non-JSON success response",
                    ),
                )
            provider_model = payload.get("model") if isinstance(payload.get("model"), str) else None
            if not _provider_model_matches(request.model, provider_model):
                raise ProviderAdapterContractError(
                    "Anthropic response reported a model outside the dispatch-authorized Haiku alias set"
                )
            text = _extract_text(payload)
            if not text:
                return ProviderExecutionResponse(
                    dispatch_id=request.dispatch_id,
                    status="failed",
                    provider_family=request.provider_family,
                    model=request.model,
                    failure=ProviderFailure(
                        scope="capability",
                        code="no_text_output",
                        message="Anthropic returned no text content for the canary task",
                    ),
                )
            self._artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = self._artifact_dir / f"{_safe_artifact_name(request.dispatch_id)}.txt"
            artifact_path.write_text(text + "\n", encoding="utf-8")
            evidence = []
            if request_id:
                evidence.append(f"anthropic_request_id:{request_id}")
            if provider_model:
                evidence.append(f"anthropic_response_model:{provider_model}")
            return ProviderExecutionResponse(
                dispatch_id=request.dispatch_id,
                status="succeeded",
                provider_family=request.provider_family,
                model=request.model,
                output_ref=artifact_path.resolve().as_uri(),
                evidence=tuple(evidence),
            )

        error_type, message = _error_details(payload)
        return ProviderExecutionResponse(
            dispatch_id=request.dispatch_id,
            status="failed",
            provider_family=request.provider_family,
            model=request.model,
            evidence=(f"anthropic_request_id:{request_id}",) if request_id else (),
            failure=ProviderFailure(
                scope=_failure_scope(status_code, error_type),  # type: ignore[arg-type]
                code=error_type,
                message=message,
            ),
        )


def execute_anthropic_canary_once(
    dispatch: DispatchRecord,
    connection: ProviderConnection,
    input_payload: dict[str, Any] | None = None,
    *,
    artifact_dir: str | Path = ".teo/runtime/artifacts/anthropic",
    timeout_seconds: float = 30.0,
) -> ProviderExecutionResponse:
    """Execute one live Anthropic canary attempt while preserving TEO routing authority."""
    if dispatch.task_type not in CANARY_TASK_TYPES:
        raise ProviderAdapterContractError(
            "Live Anthropic canary is authorized only for high_volume_simple dispatches"
        )
    if dispatch.risk_level not in CANARY_RISK_LEVELS:
        raise ProviderAdapterContractError(
            "Live Anthropic canary refuses high and critical risk dispatches"
        )
    if dispatch.selected_implementation.provider_family != "anthropic":
        raise ProviderAdapterContractError(
            "Live Anthropic canary requires an Anthropic-selected dispatch"
        )
    if dispatch.selected_implementation.model not in CANARY_MODELS:
        raise ProviderAdapterContractError(
            "Live Anthropic canary requires a Claude Haiku 4.5 selected implementation"
        )

    adapter = AnthropicMessagesAdapter(
        connection,
        artifact_dir=artifact_dir,
        timeout_seconds=timeout_seconds,
    )
    request = ProviderExecutionRequest.from_dispatch(dispatch, input_payload)
    response = adapter.execute(request)
    if not isinstance(response, ProviderExecutionResponse):
        raise ProviderAdapterContractError(
            "Anthropic adapter must return ProviderExecutionResponse rather than provider-native data"
        )
    validate_provider_response(dispatch, request, response)
    return response
