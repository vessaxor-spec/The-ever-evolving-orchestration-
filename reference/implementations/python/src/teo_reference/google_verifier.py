from __future__ import annotations

import json
from typing import Any

from .provider_connection import ProviderConnectionRequest, ProviderConnectionError
from .verification_adapter import (
    LiveVerificationError,
    LiveVerificationRequest,
    LiveVerificationResponse,
    VERIFICATION_OUTPUT_SCHEMA,
    decode_structured_decision,
    validate_verifier_connection,
)

GEMINI_INTERACTIONS_URL = "https://generativelanguage.googleapis.com/v1/interactions"
SUPPORTED_MODEL_EFFORTS = {
    "gemini-3.6-flash": {"minimal", "low", "medium", "high"},
    "gemini-3.1-pro-preview": {"low", "medium", "high"},
}


def _decode_json(body: bytes) -> dict[str, Any] | None:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _extract_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    steps = payload.get("steps")
    if not isinstance(steps, list):
        return ""
    parts: list[str] = []
    for step in steps:
        if not isinstance(step, dict) or step.get("type") != "model_output":
            continue
        content = step.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                parts.append(block["text"])
    return "\n".join(parts).strip()


class GoogleLiveVerifier:
    provider_family = "google"

    def __init__(self, connections, *, timeout_seconds: float = 30.0) -> None:
        self._connections = connections
        self._timeout_seconds = float(timeout_seconds)

    def verify(self, request: LiveVerificationRequest) -> LiveVerificationResponse:
        if request.verifier_provider_family != self.provider_family:
            raise LiveVerificationError("Google verifier received a non-Google assignment")
        supported_efforts = SUPPORTED_MODEL_EFFORTS.get(request.verifier_model)
        if supported_efforts is None:
            raise LiveVerificationError(
                "Guarded Google live verification supports Gemini 3.6 Flash and Gemini 3.1 Pro Preview"
            )
        if request.risk_level not in {"low", "medium"}:
            raise LiveVerificationError("Guarded live verification refuses high and critical risk")
        effort = request.verifier_reasoning_effort or "medium"
        if effort not in supported_efforts:
            raise LiveVerificationError(
                f"{request.verifier_model} cannot represent assigned verifier effort {effort}"
            )
        connection = validate_verifier_connection(request, self._connections)
        payload = {
            "model": request.verifier_model,
            "system_instruction": (
                "You are an independent verification gate. Evaluate only the supplied task and candidate output. "
                "Do not infer the executor identity. Use uncertain rather than guessing when evidence is insufficient."
            ),
            "input": request.blinded_prompt(),
            "store": False,
            "generation_config": {
                "max_output_tokens": 1024,
                "thinking_level": effort,
            },
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": VERIFICATION_OUTPUT_SCHEMA,
            },
        }
        try:
            response = connection.invoke(
                ProviderConnectionRequest(
                    operation="interactions.create.verification",
                    url=GEMINI_INTERACTIONS_URL,
                    method="POST",
                    headers={"content-type": "application/json"},
                    body=json.dumps(payload).encode("utf-8"),
                    timeout_seconds=self._timeout_seconds,
                )
            )
        except ProviderConnectionError as exc:
            raise LiveVerificationError("Assigned Google verifier connection failed") from exc

        response_payload = _decode_json(response.body)
        if not 200 <= response.status_code < 300 or response_payload is None:
            raise LiveVerificationError(
                f"Assigned Google verifier failed with HTTP {response.status_code}"
            )
        provider_model = response_payload.get("model")
        if isinstance(provider_model, str) and provider_model != request.verifier_model:
            raise LiveVerificationError("Google verifier response changed the assigned verifier model")
        if response_payload.get("status") in {"failed", "cancelled", "incomplete", "requires_action"}:
            raise LiveVerificationError(
                f"Google verifier response ended with status {response_payload.get('status')}"
            )
        text = _extract_text(response_payload)
        if not text:
            raise LiveVerificationError("Google verifier returned no structured decision")
        decision = decode_structured_decision(text)
        request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
        evidence: list[str] = ["live_verification:google_structured_output"]
        interaction_id = response_payload.get("id")
        if isinstance(interaction_id, str):
            evidence.append(f"google_verifier_interaction_id:{interaction_id}")
        if request_id:
            evidence.append(f"google_verifier_request_id:{request_id}")
        return LiveVerificationResponse(
            decision=decision,
            provider_family=self.provider_family,
            model=request.verifier_model,
            evidence=tuple(evidence),
        )
