from __future__ import annotations

import json
from typing import Any

from .anthropic_adapter import _extract_usage
from .provider_connection import ProviderConnectionRequest, ProviderConnectionError
from .verification_adapter import (
    LiveVerificationError,
    LiveVerificationRequest,
    LiveVerificationResponse,
    VERIFICATION_OUTPUT_SCHEMA,
    decode_structured_decision,
    validate_verifier_connection,
)

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
SUPPORTED_MODELS = {"claude-sonnet-5"}
SUPPORTED_EFFORTS = {"low", "medium", "high", "xhigh", "max"}


def _decode_json(body: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _extract_text(payload: dict[str, Any]) -> str:
    content = payload.get("content")
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
            parts.append(block["text"])
    return "\n".join(parts).strip()


class AnthropicLiveVerifier:
    provider_family = "anthropic"

    def __init__(self, connections, *, timeout_seconds: float = 30.0) -> None:
        self._connections = connections
        self._timeout_seconds = float(timeout_seconds)

    def verify(self, request: LiveVerificationRequest) -> LiveVerificationResponse:
        if request.verifier_provider_family != self.provider_family:
            raise LiveVerificationError("Anthropic verifier received a non-Anthropic assignment")
        if request.verifier_model not in SUPPORTED_MODELS:
            raise LiveVerificationError(
                "Guarded Anthropic live verification is restricted to Claude Sonnet 5"
            )
        if request.risk_level not in {"low", "medium"}:
            raise LiveVerificationError("Guarded live verification refuses high and critical risk")
        effort = request.verifier_reasoning_effort or "high"
        if effort not in SUPPORTED_EFFORTS:
            raise LiveVerificationError(
                f"Claude Sonnet 5 cannot represent assigned verifier effort {effort}"
            )
        connection = validate_verifier_connection(request, self._connections)
        payload = {
            "model": request.verifier_model,
            "max_tokens": 1024,
            "system": (
                "You are an independent verification gate. Evaluate only the supplied task and candidate output. "
                "Do not infer the executor identity. Use uncertain rather than guessing when evidence is insufficient."
            ),
            "messages": [{"role": "user", "content": request.blinded_prompt()}],
            "output_config": {
                "effort": effort,
                "format": {
                    "type": "json_schema",
                    "schema": VERIFICATION_OUTPUT_SCHEMA,
                },
            },
        }
        try:
            response = connection.invoke(
                ProviderConnectionRequest(
                    operation="messages.create.verification",
                    url=ANTHROPIC_MESSAGES_URL,
                    method="POST",
                    headers={
                        "content-type": "application/json",
                        "anthropic-version": ANTHROPIC_VERSION,
                    },
                    body=json.dumps(payload).encode("utf-8"),
                    timeout_seconds=self._timeout_seconds,
                )
            )
        except ProviderConnectionError as exc:
            raise LiveVerificationError("Assigned Anthropic verifier connection failed") from exc

        response_payload = _decode_json(response.body)
        if not 200 <= response.status_code < 300 or response_payload is None:
            raise LiveVerificationError(
                f"Assigned Anthropic verifier failed with HTTP {response.status_code}"
            )
        provider_model = response_payload.get("model")
        observed_model = (
            provider_model.strip()
            if isinstance(provider_model, str) and provider_model.strip()
            else request.verifier_model
        )
        model_observed = isinstance(provider_model, str) and bool(provider_model.strip())
        text = _extract_text(response_payload)
        if not text:
            raise LiveVerificationError("Anthropic verifier returned no structured decision")
        decision = decode_structured_decision(text)
        usage = _extract_usage(response_payload)
        request_id = response.headers.get("request-id") or response.headers.get("request_id")
        evidence: list[str] = ["live_verification:anthropic_structured_output"]
        if request_id:
            evidence.append(f"anthropic_verifier_request_id:{request_id}")
        if model_observed:
            evidence.append(f"anthropic_verifier_response_model:{observed_model}")
        return LiveVerificationResponse(
            decision=decision,
            provider_family=self.provider_family,
            model=observed_model,
            evidence=tuple(evidence),
            usage=usage,
            model_observed=model_observed,
        )