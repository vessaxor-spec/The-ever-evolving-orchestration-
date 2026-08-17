from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any, Literal
from uuid import uuid4

from .schemas import DispatchRecord, ImplementationChoice

PROTOCOL_VERSION = "teo-host-integration/0.1"
RouteRole = Literal["primary", "fallback"]
ReceiptStatus = Literal["succeeded", "failed"]
VerificationReceiptStatus = Literal["passed", "failed", "needs_human"]


class HostIntegrationProtocolError(ValueError):
    """Raised when a host-integration message violates the bound protocol state."""


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_text(value: str | None, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HostIntegrationProtocolError(f"{field_name} must be a non-empty string")
    return value.strip()


def _choice_for_role(dispatch: DispatchRecord, route_role: RouteRole) -> ImplementationChoice:
    if route_role == "primary":
        return dispatch.selected_implementation
    if dispatch.fallback_implementation is None:
        raise HostIntegrationProtocolError("dispatch has no fallback implementation")
    return dispatch.fallback_implementation


@dataclass(frozen=True, slots=True)
class HostExecutionInstruction:
    protocol_version: str
    instruction_id: str
    dispatch_id: str
    task_id: str
    route_role: RouteRole
    provider_family: str
    model: str
    reasoning_effort: str | None
    attempt: int
    max_attempts: int
    task: str
    required_capabilities: tuple[str, ...]
    instruction_sha256: str

    def unsigned_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("instruction_sha256")
        data["required_capabilities"] = list(self.required_capabilities)
        return data

    def to_dict(self) -> dict[str, Any]:
        data = self.unsigned_dict()
        data["instruction_sha256"] = self.instruction_sha256
        return data

    def validate_integrity(self) -> None:
        if self.protocol_version != PROTOCOL_VERSION:
            raise HostIntegrationProtocolError("unsupported host-integration protocol version")
        if self.attempt < 1 or self.max_attempts < 1 or self.attempt > self.max_attempts:
            raise HostIntegrationProtocolError("execution attempt is outside the authorized budget")
        if _digest(self.unsigned_dict()) != self.instruction_sha256:
            raise HostIntegrationProtocolError("execution instruction integrity mismatch")


@dataclass(frozen=True, slots=True)
class HostExecutionReceipt:
    protocol_version: str
    instruction_id: str
    instruction_sha256: str
    dispatch_id: str
    route_role: RouteRole
    provider_family: str
    model: str
    attempt: int
    status: ReceiptStatus
    output_ref: str | None = None
    output_sha256: str | None = None
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        return data


@dataclass(frozen=True, slots=True)
class HostVerificationInstruction:
    protocol_version: str
    instruction_id: str
    dispatch_id: str
    task_id: str
    active_route_role: RouteRole
    executor_provider_family: str
    executor_model: str
    verifier_provider_family: str
    verifier_model: str
    output_ref: str
    output_sha256: str
    verification_methods: tuple[str, ...]
    instruction_sha256: str

    def unsigned_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("instruction_sha256")
        data["verification_methods"] = list(self.verification_methods)
        return data

    def to_dict(self) -> dict[str, Any]:
        data = self.unsigned_dict()
        data["instruction_sha256"] = self.instruction_sha256
        return data

    def validate_integrity(self) -> None:
        if self.protocol_version != PROTOCOL_VERSION:
            raise HostIntegrationProtocolError("unsupported host-integration protocol version")
        if _digest(self.unsigned_dict()) != self.instruction_sha256:
            raise HostIntegrationProtocolError("verification instruction integrity mismatch")


@dataclass(frozen=True, slots=True)
class HostVerificationReceipt:
    protocol_version: str
    instruction_id: str
    instruction_sha256: str
    dispatch_id: str
    verifier_provider_family: str
    verifier_model: str
    output_ref: str
    output_sha256: str
    status: VerificationReceiptStatus
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence"] = list(self.evidence)
        return data


class HostIntegrationProtocolSession:
    """Process-local reference coordinator for a conformant host integration.

    This object preserves TEO ownership of route/fallback/verifier selection while the
    embedding host owns the concrete provider transport. It is not a transport-authentic
    production authority boundary.
    """

    def __init__(self, dispatch: DispatchRecord, *, max_attempts_per_route: int = 1):
        if max_attempts_per_route < 1:
            raise HostIntegrationProtocolError("max_attempts_per_route must be positive")
        self.dispatch = dispatch
        self.max_attempts_per_route = max_attempts_per_route
        self._issued_execution: dict[str, HostExecutionInstruction] = {}
        self._accepted_execution: dict[RouteRole, HostExecutionReceipt] = {}
        self._issued_verification: dict[str, HostVerificationInstruction] = {}
        self._verification_receipt: HostVerificationReceipt | None = None

    def issue_execution(self, *, route_role: RouteRole = "primary", attempt: int = 1) -> HostExecutionInstruction:
        if route_role == "fallback":
            primary = self._accepted_execution.get("primary")
            if primary is None or primary.status != "failed":
                raise HostIntegrationProtocolError("fallback may be issued only after an accepted failed primary receipt")
        previous = self._accepted_execution.get(route_role)
        if previous is not None and previous.status == "succeeded":
            raise HostIntegrationProtocolError(f"{route_role} route already succeeded")
        if attempt != 1:
            prior = [r for r in self._accepted_execution.values() if r.route_role == route_role]
            if not prior:
                raise HostIntegrationProtocolError("retry attempt requires an accepted prior receipt")
        if attempt < 1 or attempt > self.max_attempts_per_route:
            raise HostIntegrationProtocolError("execution attempt exceeds the protocol session budget")

        choice = _choice_for_role(self.dispatch, route_role)
        provider = _require_text(choice.provider_family, f"{route_role}.provider_family")
        unsigned = {
            "protocol_version": PROTOCOL_VERSION,
            "instruction_id": f"host-exec-{uuid4().hex[:12]}",
            "dispatch_id": self.dispatch.dispatch_id,
            "task_id": self.dispatch.task_id,
            "route_role": route_role,
            "provider_family": provider,
            "model": _require_text(choice.model, f"{route_role}.model"),
            "reasoning_effort": choice.reasoning,
            "attempt": attempt,
            "max_attempts": self.max_attempts_per_route,
            "task": self.dispatch.task,
            "required_capabilities": list(self.dispatch.required_capabilities),
        }
        instruction = HostExecutionInstruction(
            protocol_version=unsigned["protocol_version"],
            instruction_id=unsigned["instruction_id"],
            dispatch_id=unsigned["dispatch_id"],
            task_id=unsigned["task_id"],
            route_role=route_role,
            provider_family=provider,
            model=unsigned["model"],
            reasoning_effort=choice.reasoning,
            attempt=attempt,
            max_attempts=self.max_attempts_per_route,
            task=self.dispatch.task,
            required_capabilities=tuple(self.dispatch.required_capabilities),
            instruction_sha256=_digest(unsigned),
        )
        self._issued_execution[instruction.instruction_id] = instruction
        return instruction

    def accept_execution(self, receipt: HostExecutionReceipt) -> None:
        instruction = self._issued_execution.get(receipt.instruction_id)
        if instruction is None:
            raise HostIntegrationProtocolError("execution receipt references an unknown instruction")
        instruction.validate_integrity()
        expected = (
            receipt.protocol_version == PROTOCOL_VERSION
            and receipt.instruction_sha256 == instruction.instruction_sha256
            and receipt.dispatch_id == instruction.dispatch_id
            and receipt.route_role == instruction.route_role
            and receipt.provider_family == instruction.provider_family
            and receipt.model == instruction.model
            and receipt.attempt == instruction.attempt
        )
        if not expected:
            raise HostIntegrationProtocolError("execution receipt does not match the TEO-issued instruction")
        if receipt.status not in {"succeeded", "failed"}:
            raise HostIntegrationProtocolError("unsupported execution receipt status")
        if receipt.status == "succeeded":
            if not receipt.output_ref or not receipt.output_sha256:
                raise HostIntegrationProtocolError("successful execution requires output_ref and output_sha256")
            if len(receipt.output_sha256) != 64 or any(c not in "0123456789abcdef" for c in receipt.output_sha256):
                raise HostIntegrationProtocolError("output_sha256 must be a lowercase SHA-256 digest")
        if instruction.route_role in self._accepted_execution:
            raise HostIntegrationProtocolError("execution receipt replay or duplicate route receipt")
        self._accepted_execution[instruction.route_role] = receipt

    def active_execution(self) -> HostExecutionReceipt:
        fallback = self._accepted_execution.get("fallback")
        if fallback is not None and fallback.status == "succeeded":
            return fallback
        primary = self._accepted_execution.get("primary")
        if primary is not None and primary.status == "succeeded":
            return primary
        raise HostIntegrationProtocolError("no successful execution receipt is available")

    def issue_verification(self) -> HostVerificationInstruction:
        active = self.active_execution()
        verifier = self.dispatch.verification.implementation
        verifier_provider = _require_text(verifier.provider_family, "verification.provider_family")
        verifier_model = _require_text(verifier.model, "verification.model")
        if self.dispatch.verification.independent:
            if verifier_model == active.model:
                raise HostIntegrationProtocolError("independent verifier cannot reuse the executor model")
            if verifier_provider == active.provider_family:
                raise HostIntegrationProtocolError("independent verifier cannot reuse the executor provider family")
        assert active.output_ref is not None and active.output_sha256 is not None
        unsigned = {
            "protocol_version": PROTOCOL_VERSION,
            "instruction_id": f"host-verify-{uuid4().hex[:12]}",
            "dispatch_id": self.dispatch.dispatch_id,
            "task_id": self.dispatch.task_id,
            "active_route_role": active.route_role,
            "executor_provider_family": active.provider_family,
            "executor_model": active.model,
            "verifier_provider_family": verifier_provider,
            "verifier_model": verifier_model,
            "output_ref": active.output_ref,
            "output_sha256": active.output_sha256,
            "verification_methods": list(self.dispatch.verification.method),
        }
        instruction = HostVerificationInstruction(
            protocol_version=PROTOCOL_VERSION,
            instruction_id=unsigned["instruction_id"],
            dispatch_id=self.dispatch.dispatch_id,
            task_id=self.dispatch.task_id,
            active_route_role=active.route_role,
            executor_provider_family=active.provider_family,
            executor_model=active.model,
            verifier_provider_family=verifier_provider,
            verifier_model=verifier_model,
            output_ref=active.output_ref,
            output_sha256=active.output_sha256,
            verification_methods=tuple(self.dispatch.verification.method),
            instruction_sha256=_digest(unsigned),
        )
        self._issued_verification[instruction.instruction_id] = instruction
        return instruction

    def accept_verification(self, receipt: HostVerificationReceipt) -> None:
        instruction = self._issued_verification.get(receipt.instruction_id)
        if instruction is None:
            raise HostIntegrationProtocolError("verification receipt references an unknown instruction")
        instruction.validate_integrity()
        expected = (
            receipt.protocol_version == PROTOCOL_VERSION
            and receipt.instruction_sha256 == instruction.instruction_sha256
            and receipt.dispatch_id == instruction.dispatch_id
            and receipt.verifier_provider_family == instruction.verifier_provider_family
            and receipt.verifier_model == instruction.verifier_model
            and receipt.output_ref == instruction.output_ref
            and receipt.output_sha256 == instruction.output_sha256
        )
        if not expected:
            raise HostIntegrationProtocolError("verification receipt does not match the TEO-issued instruction")
        if receipt.status not in {"passed", "failed", "needs_human"}:
            raise HostIntegrationProtocolError("unsupported verification receipt status")
        if self._verification_receipt is not None:
            raise HostIntegrationProtocolError("verification receipt replay or duplicate receipt")
        self._verification_receipt = receipt

    def evidence_projection(self) -> dict[str, Any]:
        active = self.active_execution()
        if self._verification_receipt is None:
            raise HostIntegrationProtocolError("verification receipt has not been accepted")
        return {
            "protocol_version": PROTOCOL_VERSION,
            "dispatch_id": self.dispatch.dispatch_id,
            "active_route_role": active.route_role,
            "executor_provider_family": active.provider_family,
            "executor_model": active.model,
            "execution_instruction_sha256": active.instruction_sha256,
            "output_ref": active.output_ref,
            "output_sha256": active.output_sha256,
            "verifier_provider_family": self._verification_receipt.verifier_provider_family,
            "verifier_model": self._verification_receipt.verifier_model,
            "verification_status": self._verification_receipt.status,
            "verification_instruction_sha256": self._verification_receipt.instruction_sha256,
        }
