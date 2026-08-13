from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

RiskLevel = Literal["low", "medium", "high", "critical"]
VerificationStatus = Literal["passed", "failed", "needs_human"]
ExecutionStatus = Literal["succeeded", "failed"]

RISK_ORDER: dict[str, int] = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _require(value: Any, name: str) -> Any:
    if value is None or value == "":
        raise ValueError(f"{name} is required")
    return value


def _risk(value: str) -> RiskLevel:
    if value not in RISK_ORDER:
        raise ValueError(f"Unsupported risk level: {value}")
    return value  # type: ignore[return-value]


@dataclass(slots=True)
class TaskConstraints:
    contexts: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    blocked_implementations: list[str] = field(default_factory=list)
    blocked_providers: list[str] = field(default_factory=list)
    accepted_preview_models: list[str] = field(default_factory=list)
    require_human_approval: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "TaskConstraints":
        data = data or {}
        return cls(
            contexts=list(data.get("contexts", [])),
            required_capabilities=list(data.get("required_capabilities", [])),
            blocked_implementations=list(data.get("blocked_implementations", [])),
            blocked_providers=list(data.get("blocked_providers", [])),
            accepted_preview_models=list(data.get("accepted_preview_models", [])),
            require_human_approval=bool(data.get("require_human_approval", False)),
        )


@dataclass(slots=True)
class TaskRequest:
    task: str
    task_id: str = field(default_factory=lambda: f"task-{uuid4().hex[:12]}")
    task_type: str | None = None
    risk_level: RiskLevel | None = None
    domain: str | None = None
    specialist: str | None = None
    constraints: TaskConstraints = field(default_factory=TaskConstraints)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskRequest":
        risk = data.get("risk_level")
        return cls(
            task=str(_require(data.get("task"), "task")),
            task_id=str(data.get("task_id") or f"task-{uuid4().hex[:12]}"),
            task_type=str(data["task_type"]) if data.get("task_type") else None,
            risk_level=_risk(str(risk)) if risk else None,
            domain=str(data["domain"]) if data.get("domain") else None,
            specialist=str(data["specialist"]) if data.get("specialist") else None,
            constraints=TaskConstraints.from_dict(data.get("constraints")),
        )


@dataclass(slots=True)
class ImplementationChoice:
    agent: str
    model: str
    profile: str | None
    provider_family: str | None
    availability: str | None
    source: str
    reasoning: str | None = None


@dataclass(slots=True)
class VerificationPlan:
    team: str
    method: list[str]
    implementation: ImplementationChoice
    independent: bool
    human_approval_required: bool


@dataclass(slots=True)
class DispatchRecord:
    task_id: str
    dispatch_id: str
    created_at: str
    task: str
    task_type: str
    risk_level: RiskLevel
    selected_team: str
    selected_worker: str
    selected_specialist: str | None
    specialist_source: str | None
    specialist_risk_profile: str | None
    required_capabilities: list[str]
    selected_implementation: ImplementationChoice
    fallback_implementation: ImplementationChoice | None
    verification: VerificationPlan
    routing_explanation: list[str]
    warnings: list[str]
    status: str = "dispatched"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExecutionResult:
    dispatch_id: str
    status: ExecutionStatus
    output_ref: str | None = None
    evidence: list[str] = field(default_factory=list)
    failed_attempts: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionResult":
        status = str(_require(data.get("status"), "execution.status"))
        if status not in {"succeeded", "failed"}:
            raise ValueError(f"Unsupported execution status: {status}")
        return cls(
            dispatch_id=str(_require(data.get("dispatch_id"), "execution.dispatch_id")),
            status=status,  # type: ignore[arg-type]
            output_ref=str(data["output_ref"]) if data.get("output_ref") else None,
            evidence=list(data.get("evidence", [])),
            failed_attempts=int(data.get("failed_attempts", 0)),
        )


@dataclass(slots=True)
class VerificationResult:
    dispatch_id: str
    status: VerificationStatus
    verifier_model: str
    checks: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationResult":
        status = str(_require(data.get("status"), "verification.status"))
        if status not in {"passed", "failed", "needs_human"}:
            raise ValueError(f"Unsupported verification status: {status}")
        return cls(
            dispatch_id=str(_require(data.get("dispatch_id"), "verification.dispatch_id")),
            status=status,  # type: ignore[arg-type]
            verifier_model=str(_require(data.get("verifier_model"), "verification.verifier_model")),
            checks=list(data.get("checks", [])),
            evidence=list(data.get("evidence", [])),
            notes=str(data["notes"]) if data.get("notes") else None,
        )


@dataclass(frozen=True, slots=True)
class ExecutionProvenance:
    source: Literal["route_outcome"]
    route_outcome_id: str
    route_outcome_integrity_sha256: str
    active_dispatch_id: str
    active_route_role: Literal["primary", "fallback"]
    provider_family: str
    model: str
    reasoning_effort: str | None
    verification_dispatch_id: str
    final_disposition: str
    fallback_assisted: bool
    retry_assisted: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FinalOutcome:
    dispatch_id: str
    task_id: str
    completed_at: str
    status: Literal["completed", "failed", "escalated", "awaiting_human"]
    execution_status: ExecutionStatus
    verification_status: VerificationStatus
    selected_model: str
    verifier_model: str
    evidence: list[str]
    failed_attempts: int
    escalation_used: bool
    notes: list[str]
    execution_provenance: ExecutionProvenance | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if self.execution_provenance is None:
            data.pop("execution_provenance")
        return data
