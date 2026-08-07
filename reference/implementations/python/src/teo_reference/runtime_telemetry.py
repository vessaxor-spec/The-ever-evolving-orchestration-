from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Any, Literal, Protocol

from .provider_adapter import ProviderAdapterContractError, ProviderExecutionResponse, ProviderUsage
from .schemas import DispatchRecord

TELEMETRY_VERSION = "1"
AttemptRole = Literal["primary", "fallback"]


@dataclass(frozen=True, slots=True)
class RuntimeTelemetryEvent:
    """Content-free evidence for one provider attempt."""

    recorded_at: str
    task_id: str
    dispatch_id: str
    task_type: str
    risk_level: str
    role: AttemptRole
    attempt_number: int
    provider_family: str
    model: str
    reasoning_effort: str | None
    verifier_provider_family: str | None
    verifier_model: str
    status: str
    failure_scope: str | None
    failure_code: str | None
    duration_ms: float
    retry_after_seconds: float | None
    usage: ProviderUsage | None
    event_type: Literal["provider_attempt"] = "provider_attempt"
    telemetry_version: Literal["1"] = "1"

    def __post_init__(self) -> None:
        if self.telemetry_version != TELEMETRY_VERSION:
            raise ProviderAdapterContractError("Unsupported runtime telemetry version")
        if self.event_type != "provider_attempt":
            raise ProviderAdapterContractError("Unsupported runtime telemetry event type")
        for name in (
            "recorded_at",
            "task_id",
            "dispatch_id",
            "task_type",
            "risk_level",
            "provider_family",
            "model",
            "verifier_model",
            "status",
        ):
            if not str(getattr(self, name)).strip():
                raise ProviderAdapterContractError(f"Telemetry {name} is required")
        if self.role not in {"primary", "fallback"}:
            raise ProviderAdapterContractError("Telemetry role must be primary or fallback")
        if self.attempt_number < 1:
            raise ProviderAdapterContractError("Telemetry attempt_number must be positive")
        duration = float(self.duration_ms)
        if not isfinite(duration) or duration < 0:
            raise ProviderAdapterContractError("Telemetry duration_ms must be finite and non-negative")
        if self.retry_after_seconds is not None:
            retry_after = float(self.retry_after_seconds)
            if not isfinite(retry_after) or retry_after < 0:
                raise ProviderAdapterContractError(
                    "Telemetry retry_after_seconds must be finite and non-negative"
                )
        if self.status == "succeeded":
            if self.failure_scope is not None or self.failure_code is not None:
                raise ProviderAdapterContractError(
                    "Successful telemetry event cannot include failure details"
                )
        elif self.status == "failed":
            if not self.failure_scope or not self.failure_code:
                raise ProviderAdapterContractError(
                    "Failed telemetry event requires failure scope and code"
                )
        else:
            raise ProviderAdapterContractError("Unsupported telemetry provider status")

    @classmethod
    def from_attempt(
        cls,
        dispatch: DispatchRecord,
        response: ProviderExecutionResponse,
        *,
        role: AttemptRole,
        attempt_number: int,
        duration_seconds: float,
        recorded_at: str | None = None,
    ) -> "RuntimeTelemetryEvent":
        verifier = dispatch.verification.implementation
        return cls(
            recorded_at=recorded_at or datetime.now(timezone.utc).isoformat(),
            task_id=dispatch.task_id,
            dispatch_id=dispatch.dispatch_id,
            task_type=dispatch.task_type,
            risk_level=dispatch.risk_level,
            role=role,
            attempt_number=attempt_number,
            provider_family=response.provider_family,
            model=response.model,
            reasoning_effort=dispatch.selected_implementation.reasoning,
            verifier_provider_family=verifier.provider_family,
            verifier_model=verifier.model,
            status=response.status,
            failure_scope=response.failure.scope if response.failure else None,
            failure_code=response.failure.code if response.failure else None,
            duration_ms=max(0.0, float(duration_seconds) * 1000.0),
            retry_after_seconds=response.retry_after_seconds,
            usage=response.usage,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuntimeTelemetryEvent":
        allowed = {
            "telemetry_version",
            "event_type",
            "recorded_at",
            "task_id",
            "dispatch_id",
            "task_type",
            "risk_level",
            "role",
            "attempt_number",
            "provider_family",
            "model",
            "reasoning_effort",
            "verifier_provider_family",
            "verifier_model",
            "status",
            "failure_scope",
            "failure_code",
            "duration_ms",
            "retry_after_seconds",
            "usage",
        }
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ProviderAdapterContractError(
                f"Runtime telemetry event contains unsupported fields: {', '.join(unknown)}"
            )
        usage_data = data.get("usage")
        if usage_data is not None and not isinstance(usage_data, dict):
            raise ProviderAdapterContractError("Telemetry usage must be an object or null")
        return cls(
            telemetry_version=str(data.get("telemetry_version")),  # type: ignore[arg-type]
            event_type=str(data.get("event_type")),  # type: ignore[arg-type]
            recorded_at=str(data.get("recorded_at") or ""),
            task_id=str(data.get("task_id") or ""),
            dispatch_id=str(data.get("dispatch_id") or ""),
            task_type=str(data.get("task_type") or ""),
            risk_level=str(data.get("risk_level") or ""),
            role=str(data.get("role")),  # type: ignore[arg-type]
            attempt_number=int(data.get("attempt_number", 0)),
            provider_family=str(data.get("provider_family") or ""),
            model=str(data.get("model") or ""),
            reasoning_effort=(
                str(data["reasoning_effort"]) if data.get("reasoning_effort") is not None else None
            ),
            verifier_provider_family=(
                str(data["verifier_provider_family"])
                if data.get("verifier_provider_family") is not None
                else None
            ),
            verifier_model=str(data.get("verifier_model") or ""),
            status=str(data.get("status") or ""),
            failure_scope=(
                str(data["failure_scope"]) if data.get("failure_scope") is not None else None
            ),
            failure_code=(
                str(data["failure_code"]) if data.get("failure_code") is not None else None
            ),
            duration_ms=float(data.get("duration_ms", -1)),
            retry_after_seconds=(
                float(data["retry_after_seconds"])
                if data.get("retry_after_seconds") is not None
                else None
            ),
            usage=ProviderUsage.from_dict(usage_data) if usage_data is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "telemetry_version": self.telemetry_version,
            "event_type": self.event_type,
            "recorded_at": self.recorded_at,
            "task_id": self.task_id,
            "dispatch_id": self.dispatch_id,
            "task_type": self.task_type,
            "risk_level": self.risk_level,
            "role": self.role,
            "attempt_number": self.attempt_number,
            "provider_family": self.provider_family,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "verifier_provider_family": self.verifier_provider_family,
            "verifier_model": self.verifier_model,
            "status": self.status,
            "failure_scope": self.failure_scope,
            "failure_code": self.failure_code,
            "duration_ms": self.duration_ms,
            "retry_after_seconds": self.retry_after_seconds,
            "usage": self.usage.to_dict() if self.usage else None,
        }


class RuntimeTelemetrySink(Protocol):
    def append(self, event: RuntimeTelemetryEvent) -> None:
        ...


class InMemoryRuntimeTelemetrySink:
    def __init__(self) -> None:
        self.events: list[RuntimeTelemetryEvent] = []

    def append(self, event: RuntimeTelemetryEvent) -> None:
        self.events.append(event)


class JsonlRuntimeTelemetrySink:
    """Append-only single-process reference sink for content-free runtime telemetry."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: RuntimeTelemetryEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError("Runtime telemetry could not be persisted") from exc

    def read_all(self) -> list[RuntimeTelemetryEvent]:
        if not self.path.exists():
            return []
        events: list[RuntimeTelemetryEvent] = []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ProviderAdapterContractError("Runtime telemetry could not be read") from exc
        for line in lines:
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderAdapterContractError("Runtime telemetry contains invalid JSONL") from exc
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError("Runtime telemetry line must be an object")
            events.append(RuntimeTelemetryEvent.from_dict(raw))
        return events
