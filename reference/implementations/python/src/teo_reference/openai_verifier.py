from __future__ import annotations

import json
from typing import Any

from .openai_adapter import _extract_usage
from .provider_connection import ProviderConnectionRequest, ProviderConnectionError
from .verification_adapter import (
    LiveVerificationError,
    LiveVerificationRequest,
    LiveVerificationResponse,
    VERIFICATION_OUTPUT_SCHEMA,
    decode_structured_decision,
    validate_verifier_connection,
)

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
SUPPORTED_MODELS = {"gpt-5.6-sol", "gpt-5.6-luna", "gpt-5.6-terra"}
SUPPORTED_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}


def _decode_json(body: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _extract_output_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    output = payload.get("output")
    if not isinstance(output, list):
        return ""
    parts: list[str] = []
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
    return "\n".join(parts).strip()


class OpenAILiveVerifier:
    provider_family = "openai"

    def __init__(self, connections, *, timeout_seconds: float = 30.0) -> None:
        self._connections = connections
        self._timeout_seconds = float(timeout_seconds)

    def verify(self, request: LiveVerificationRequest) -> LiveVerificationResponse:
        if request.verifier_provider_family != self.provider_family:
            raise LiveVerificationError("OpenAI verifier received a non-OpenAI assignment")
        if request.verifier_model not in SUPPORTED_MODELS:
            raise LiveVerificationError(
                "Guarded OpenAI live verification supports GPT-5.6 Sol, Luna, and Terra"
            )
        if request.risk_level not in {"low", "medium"}:
            raise LiveVerificationError("Guarded live verification refuses high and critical risk")
        effort = request.verifier_reasoning_effort or (
            "low" if request.verifier_model == "gpt-5.6-luna" else "medium"
        )
        if effort not in SUPPORTED_EFFORTS:
            raise LiveVerificationError(
                f"{request.verifier_model} cannot represent assigned verifier effort {effort}"
            )
        connection = validate_verifier_connection(request, self._connections)
        payload = {
            "model": request.verifier_model,
            "input": [
                {
                    "role": "system",
                    "content": (
                        "You are an independent verification gate. Evaluate only the supplied task and candidate output. "
                        "Do not infer the executor identity. Use uncertain rather than guessing when evidence is insufficient."
                    ),
                },
                {"role": "user", "content": request.blinded_prompt()},
            ],
            "max_output_tokens": 1024,
            "store": False,
            "reasoning": {"effort": effort},
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "teo_live_verification",
                    "strict": True,
                    "schema": VERIFICATION_OUTPUT_SCHEMA,
                }
            },
        }
        try:
            response = connection.invoke(
                ProviderConnectionRequest(
                    operation="responses.create.verification",
                    url=OPENAI_RESPONSES_URL,
                    method="POST",
                    headers={"content-type": "application/json"},
                    body=json.dumps(payload).encode("utf-8"),
                    timeout_seconds=self._timeout_seconds,
                )
            )
        except ProviderConnectionError as exc:
            raise LiveVerificationError("Assigned OpenAI verifier connection failed") from exc

        response_payload = _decode_json(response.body)
        if not 200 <= response.status_code < 300 or response_payload is None:
            raise LiveVerificationError(
                f"Assigned OpenAI verifier failed with HTTP {response.status_code}"
            )
        provider_model = response_payload.get("model")
        observed_model = (
            provider_model.strip()
            if isinstance(provider_model, str) and provider_model.strip()
            else request.verifier_model
        )
        model_observed = isinstance(provider_model, str) and bool(provider_model.strip())
        if response_payload.get("status") in {"failed", "cancelled", "incomplete"}:
            raise LiveVerificationError(
                f"OpenAI verifier response ended with status {response_payload.get('status')}"
            )
        text = _extract_output_text(response_payload)
        if not text:
            raise LiveVerificationError("OpenAI verifier returned no structured decision")
        decision = decode_structured_decision(text)
        usage = _extract_usage(response_payload)
        request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
        evidence: list[str] = ["live_verification:openai_structured_output"]
        response_id = response_payload.get("id")
        if isinstance(response_id, str):
            evidence.append(f"openai_verifier_response_id:{response_id}")
        if request_id:
            evidence.append(f"openai_verifier_request_id:{request_id}")
        if model_observed:
            evidence.append(f"openai_verifier_response_model:{observed_model}")
        return LiveVerificationResponse(
            decision=decision,
            provider_family=self.provider_family,
            model=observed_model,
            evidence=tuple(evidence),
            usage=usage,
            model_observed=model_observed,
        )