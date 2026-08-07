from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from math import isfinite
from typing import Any, Literal, Mapping, Protocol

from .schemas import DispatchRecord, ExecutionResult, ExecutionStatus, RiskLevel

CONTRACT_VERSION = "1"
FailureScope = Literal["request", "transient", "model", "provider", "capability"]
ReasoningEffort = Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]
FAILURE_SCOPES = {"request", "transient", "model", "provider", "capability"}
REASONING_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max"}
_CREDENTIAL_FIELDS = {
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "credentials",
    "password",
    "secret",
    "token",
}


class ProviderAdapterContractError(RuntimeError):
    """Raised when an adapter violates the provider-neutral execution contract."""


def _require_text(value: Any, name: str) -> str:
    if value is None or str(value).strip() == "":
        raise ProviderAdapterContractError(f"{name} is required")
    return str(value)


def _reject_unknown(data: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ProviderAdapterContractError(
            f"{name} contains unsupported fields: {', '.join(unknown)}"
        )


def _assert_no_credential_fields(value: Any, path: str = "input_payload") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in _CREDENTIAL_FIELDS:
                raise ProviderAdapterContractError(
                    f"Credential material must not be serialized in {path}: {key}"
                )
            _assert_no_credential_fields(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _assert_no_credential_fields(nested, f"{path}[{index}]")


def retry_after_seconds_from_headers(headers: Mapping[str, str]) -> float | None:
    """Normalize a numeric Retry-After response header without exposing provider-native headers."""
    value: str | None = None
    for key, item in headers.items():
        if str(key).strip().lower() == "retry-after":
            value = str(item).strip()
            break
    if not value:
        return None
    try:
        seconds = float(value)
    except ValueError:
        return None
    if not isfinite(seconds) or seconds < 0:
        return None
    return seconds


def _optional_non_negative_int(value: Any, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProviderAdapterContractError(f"{name} must be an integer or null")
    if value < 0:
        raise ProviderAdapterContractError(f"{name} cannot be negative")
    return value


@dataclass(frozen=True, slots=True)
class ProviderUsage:
    """Provider-neutral usage evidence for one provider attempt.

    Input and output totals follow OpenTelemetry GenAI semantics where practical.
    Provider-specific usage is normalized only when a stable equivalent exists.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    tool_tokens: int | None = None
    total_tokens: int | None = None

    def __post_init__(self) -> None:
        for name in (
            "input_tokens",
            "output_tokens",
            "cached_input_tokens",
            "cache_creation_input_tokens",
            "reasoning_output_tokens",
            "tool_tokens",
            "total_tokens",
        ):
            _optional_non_negative_int(getattr(self, name), f"usage.{name}")
        if (
            self.reasoning_output_tokens is not None
            and self.output_tokens is not None
            and self.reasoning_output_tokens > self.output_tokens
        ):
            raise ProviderAdapterContractError(
                "usage.reasoning_output_tokens cannot exceed usage.output_tokens"
            )
        if self.cached_input_tokens is not None and self.input_tokens is not None:
            if self.cached_input_tokens > self.input_tokens:
                raise ProviderAdapterContractError(
                    "usage.cached_input_tokens cannot exceed usage.input_tokens"
                )
        if self.cache_creation_input_tokens is not None and self.input_tokens is not None:
            if self.cache_creation_input_tokens > self.input_tokens:
                raise ProviderAdapterContractError(
                    "usage.cache_creation_input_tokens cannot exceed usage.input_tokens"
                )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderUsage":
        allowed = {
            "input_tokens",
            "output_tokens",
            "cached_input_tokens",
            "cache_creation_input_tokens",
            "reasoning_output_tokens",
            "tool_tokens",
            "total_tokens",
        }
        _reject_unknown(data, allowed, "usage")
        return cls(
            input_tokens=_optional_non_negative_int(data.get("input_tokens"), "usage.input_tokens"),
            output_tokens=_optional_non_negative_int(data.get("output_tokens"), "usage.output_tokens"),
            cached_input_tokens=_optional_non_negative_int(
                data.get("cached_input_tokens"), "usage.cached_input_tokens"
            ),
            cache_creation_input_tokens=_optional_non_negative_int(
                data.get("cache_creation_input_tokens"), "usage.cache_creation_input_tokens"
            ),
            reasoning_output_tokens=_optional_non_negative_int(
                data.get("reasoning_output_tokens"), "usage.reasoning_output_tokens"
            ),
            tool_tokens=_optional_non_negative_int(data.get("tool_tokens"), "usage.tool_tokens"),
            total_tokens=_optional_non_negative_int(data.get("total_tokens"), "usage.total_tokens"),
        )

    def to_dict(self) -> dict[str, int | None]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "reasoning_output_tokens": self.reasoning_output_tokens,
            "tool_tokens": self.tool_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass(frozen=True, slots=True)
class ProviderFailure:
    scope: FailureScope
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.scope not in FAILURE_SCOPES:
            raise ProviderAdapterContractError(f"Unsupported provider failure scope: {self.scope}")
        _require_text(self.code, "failure.code")
        _require_text(self.message, "failure.message")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderFailure":
        _reject_unknown(data, {"scope", "code", "message"}, "failure")
        return cls(
            scope=str(data.get("scope")),  # type: ignore[arg-type]
            code=_require_text(data.get("code"), "failure.code"),
            message=_require_text(data.get("message"), "failure.message"),
        )

    def to_dict(self) -> dict[str, str]:
        return {"scope": self.scope, "code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class ProviderExecutionRequest:
    dispatch_id: str
    task_id: str
    provider_family: str
    model: str
    risk_level: RiskLevel
    required_capabilities: tuple[str, ...]
    input_payload: dict[str, Any]
    reasoning_effort: ReasoningEffort | None = None
    contract_version: Literal["1"] = "1"

    def __post_init__(self) -> None:
        if self.contract_version != CONTRACT_VERSION:
            raise ProviderAdapterContractError(
                f"Unsupported provider adapter contract version: {self.contract_version}"
            )
        _require_text(self.dispatch_id, "dispatch_id")
        _require_text(self.task_id, "task_id")
        _require_text(self.provider_family, "provider_family")
        _require_text(self.model, "model")
        if self.risk_level not in {"low", "medium", "high", "critical"}:
            raise ProviderAdapterContractError(f"Unsupported risk level: {self.risk_level}")
        if self.reasoning_effort is not None and self.reasoning_effort not in REASONING_EFFORTS:
            raise ProviderAdapterContractError(
                f"Unsupported reasoning effort: {self.reasoning_effort}"
            )
        _assert_no_credential_fields(self.input_payload)

    @classmethod
    def from_dispatch(
        cls,
        dispatch: DispatchRecord,
        input_payload: dict[str, Any] | None = None,
    ) -> "ProviderExecutionRequest":
        provider_family = dispatch.selected_implementation.provider_family
        if not provider_family:
            raise ProviderAdapterContractError(
                "Selected implementation has no provider_family and cannot be executed by an adapter"
            )
        payload = deepcopy(input_payload) if input_payload is not None else {"task": dispatch.task}
        reasoning = dispatch.selected_implementation.reasoning
        return cls(
            dispatch_id=dispatch.dispatch_id,
            task_id=dispatch.task_id,
            provider_family=provider_family,
            model=dispatch.selected_implementation.model,
            risk_level=dispatch.risk_level,
            required_capabilities=tuple(dispatch.required_capabilities),
            input_payload=payload,
            reasoning_effort=str(reasoning) if reasoning else None,  # type: ignore[arg-type]
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderExecutionRequest":
        allowed = {
            "contract_version",
            "dispatch_id",
            "task_id",
            "provider_family",
            "model",
            "risk_level",
            "required_capabilities",
            "input_payload",
            "reasoning_effort",
        }
        _reject_unknown(data, allowed, "provider execution request")
        payload = data.get("input_payload")
        if not isinstance(payload, dict):
            raise ProviderAdapterContractError("input_payload must be an object")
        reasoning = data.get("reasoning_effort")
        return cls(
            contract_version=str(data.get("contract_version")),  # type: ignore[arg-type]
            dispatch_id=_require_text(data.get("dispatch_id"), "dispatch_id"),
            task_id=_require_text(data.get("task_id"), "task_id"),
            provider_family=_require_text(data.get("provider_family"), "provider_family"),
            model=_require_text(data.get("model"), "model"),
            risk_level=str(data.get("risk_level")),  # type: ignore[arg-type]
            required_capabilities=tuple(str(item) for item in data.get("required_capabilities", [])),
            input_payload=deepcopy(payload),
            reasoning_effort=str(reasoning) if reasoning is not None else None,  # type: ignore[arg-type]
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "dispatch_id": self.dispatch_id,
            "task_id": self.task_id,
            "provider_family": self.provider_family,
            "model": self.model,
            "risk_level": self.risk_level,
            "required_capabilities": list(self.required_capabilities),
            "input_payload": deepcopy(self.input_payload),
            "reasoning_effort": self.reasoning_effort,
        }


@dataclass(frozen=True, slots=True)
class ProviderExecutionResponse:
    dispatch_id: str
    status: ExecutionStatus
    provider_family: str
    model: str
    output_ref: str | None = None
    evidence: tuple[str, ...] = ()
    failure: ProviderFailure | None = None
    retry_after_seconds: float | None = None
    usage: ProviderUsage | None = None
    contract_version: Literal["1"] = "1"

    def __post_init__(self) -> None:
        if self.contract_version != CONTRACT_VERSION:
            raise ProviderAdapterContractError(
                f"Unsupported provider adapter contract version: {self.contract_version}"
            )
        _require_text(self.dispatch_id, "dispatch_id")
        _require_text(self.provider_family, "provider_family")
        _require_text(self.model, "model")
        if self.status not in {"succeeded", "failed"}:
            raise ProviderAdapterContractError(f"Unsupported execution status: {self.status}")
        if self.retry_after_seconds is not None:
            retry_after = float(self.retry_after_seconds)
            if not isfinite(retry_after) or retry_after < 0:
                raise ProviderAdapterContractError("retry_after_seconds must be finite and non-negative")
        if self.usage is not None and not isinstance(self.usage, ProviderUsage):
            raise ProviderAdapterContractError("usage must be ProviderUsage or null")
        if self.status == "succeeded":
            _require_text(self.output_ref, "output_ref")
            if self.failure is not None:
                raise ProviderAdapterContractError("Successful execution cannot include failure details")
            if self.retry_after_seconds is not None:
                raise ProviderAdapterContractError("Successful execution cannot include retry timing")
        elif self.failure is None:
            raise ProviderAdapterContractError("Failed execution must include normalized failure details")
        elif self.output_ref is not None:
            raise ProviderAdapterContractError("Failed execution cannot publish an accepted output_ref")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderExecutionResponse":
        allowed = {
            "contract_version",
            "dispatch_id",
            "status",
            "provider_family",
            "model",
            "output_ref",
            "evidence",
            "failure",
            "retry_after_seconds",
            "usage",
        }
        _reject_unknown(data, allowed, "provider execution response")
        failure_data = data.get("failure")
        if failure_data is not None and not isinstance(failure_data, dict):
            raise ProviderAdapterContractError("failure must be an object or null")
        usage_data = data.get("usage")
        if usage_data is not None and not isinstance(usage_data, dict):
            raise ProviderAdapterContractError("usage must be an object or null")
        retry_after = data.get("retry_after_seconds")
        return cls(
            contract_version=str(data.get("contract_version")),  # type: ignore[arg-type]
            dispatch_id=_require_text(data.get("dispatch_id"), "dispatch_id"),
            status=str(data.get("status")),  # type: ignore[arg-type]
            provider_family=_require_text(data.get("provider_family"), "provider_family"),
            model=_require_text(data.get("model"), "model"),
            output_ref=str(data["output_ref"]) if data.get("output_ref") else None,
            evidence=tuple(str(item) for item in data.get("evidence", [])),
            failure=ProviderFailure.from_dict(failure_data) if failure_data is not None else None,
            retry_after_seconds=float(retry_after) if retry_after is not None else None,
            usage=ProviderUsage.from_dict(usage_data) if usage_data is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "dispatch_id": self.dispatch_id,
            "status": self.status,
            "provider_family": self.provider_family,
            "model": self.model,
            "output_ref": self.output_ref,
            "evidence": list(self.evidence),
            "failure": self.failure.to_dict() if self.failure else None,
            "retry_after_seconds": self.retry_after_seconds,
            "usage": self.usage.to_dict() if self.usage else None,
        }

    def to_execution_result(self) -> ExecutionResult:
        return ExecutionResult(
            dispatch_id=self.dispatch_id,
            status=self.status,
            output_ref=self.output_ref,
            evidence=list(self.evidence),
            failed_attempts=1 if self.status == "failed" else 0,
        )


class ProviderAdapter(Protocol):
    provider_family: str

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        """Perform exactly one provider attempt and return a normalized response."""
        ...


def validate_provider_response(
    dispatch: DispatchRecord,
    request: ProviderExecutionRequest,
    response: ProviderExecutionResponse,
) -> None:
    expected_provider = dispatch.selected_implementation.provider_family
    expected_model = dispatch.selected_implementation.model
    if response.dispatch_id != dispatch.dispatch_id or response.dispatch_id != request.dispatch_id:
        raise ProviderAdapterContractError("Provider response does not reference the active dispatch")
    if response.provider_family != expected_provider or response.provider_family != request.provider_family:
        raise ProviderAdapterContractError("Provider response changed the selected provider family")
    if response.model != expected_model or response.model != request.model:
        raise ProviderAdapterContractError("Provider response changed the selected implementation model")
    if response.contract_version != request.contract_version:
        raise ProviderAdapterContractError("Provider response changed the adapter contract version")


def execute_provider_once(
    adapter: ProviderAdapter,
    dispatch: DispatchRecord,
    input_payload: dict[str, Any] | None = None,
) -> ExecutionResult:
    """Execute one authorized provider attempt without retry, fallback, or verification."""
    request = ProviderExecutionRequest.from_dispatch(dispatch, input_payload)
    if adapter.provider_family != request.provider_family:
        raise ProviderAdapterContractError(
            "Adapter provider family does not match the dispatch-selected provider family"
        )
    response = adapter.execute(request)
    if not isinstance(response, ProviderExecutionResponse):
        raise ProviderAdapterContractError(
            "Adapter must return ProviderExecutionResponse rather than a provider-native payload"
        )
    validate_provider_response(dispatch, request, response)
    return response.to_execution_result()
