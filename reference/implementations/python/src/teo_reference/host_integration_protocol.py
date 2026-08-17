from __future__ import annotations

import copy
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


def _valid_sha256(value: str | None) -> bool:
    return bool(
        isinstance(value, str)
        and len(value) == 64
        and all(char in "0123456789abcdef" for char in value)
    )


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

    TEO owns route, fallback, retry budget, and verifier selection. The embedding host
    owns concrete provider transport. This candidate does not provide production
    transport authenticity, restart-persistent replay state, or hostile-host containment.
    """

    def __init__(self, dispatch: DispatchRecord, *, max_attempts_per_route: int = 1):
        if isinstance(max_attempts_per_route, bool) or max_attempts_per_route < 1:
            raise HostIntegrationProtocolError("max_attempts_per_route must be positive")
        self.dispatch = copy.deepcopy(dispatch)
        self._dispatch_sha256 = _digest(self.dispatch.to_dict())
        self.max_attempts_per_route = max_attempts_per_route
        self._issued_execution: dict[str, HostExecutionInstruction] = {}
        self._issued_attempts: dict[tuple[RouteRole, int], str] = {}
        self._accepted_execution: dict[tuple[RouteRole, int], HostExecutionReceipt] = {}
        self._issued_verification: dict[str, HostVerificationInstruction] = {}
        self._verification_receipt: HostVerificationReceipt | None = None

    def _validate_dispatch_snapshot(self) -> None:
        if _digest(self.dispatch.to_dict()) != self._dispatch_sha256:
            raise HostIntegrationProtocolError("bound dispatch snapshot changed after session creation")

    def _latest_receipt(self, route_role: RouteRole) -> HostExecutionReceipt | None:
        candidates = [
            receipt
            for (role, _), receipt in self._accepted_execution.items()
            if role == route_role
        ]
        return max(candidates, key=lambda receipt: receipt.attempt, default=None)

    def issue_execution(self, *, route_role: RouteRole = "primary", attempt: int = 1) -> HostExecutionInstruction:
        self._validate_dispatch_snapshot()
        if route_role not in {"primary", "fallback"}:
            raise HostIntegrationProtocolError("unsupported route role")
        if isinstance(attempt, bool) or not isinstance(attempt, int):
            raise HostIntegrationProtocolError("execution attempt must be an integer")
        if attempt < 1 or attempt > self.max_attempts_per_route:
            raise HostIntegrationProtocolError("execution attempt exceeds the protocol session budget")
        key = (route_role, attempt)
        if key in self._issued_attempts:
            raise HostIntegrationProtocolError("execution attempt was already issued")

        if route_role == "fallback":
            primary = self._latest_receipt("primary")
            if primary is None or primary.status != "failed":
                raise HostIntegrationProtocolError(
                    "fallback may be issued only after the latest accepted primary attempt failed"
                )
        latest = self._latest_receipt(route_role)
        if latest is not None and latest.status == "succeeded":
            raise HostIntegrationProtocolError(f"{route_role} route already succeeded")
        if attempt == 1:
            if latest is not None:
                raise HostIntegrationProtocolError("route already has accepted execution evidence")
        else:
            prior = self._accepted_execution.get((route_role, attempt - 1))
            if prior is None or prior.status != "failed":
                raise HostIntegrationProtocolError(
                    "retry attempt requires the immediately preceding accepted attempt to have failed"
                )

        choice = _choice_for_role(self.dispatch, route_role)
        provider = _require_text(choice.provider_family, f"{route_role}.provider_family")
        model = _require_text(choice.model, f"{route_role}.model")
        unsigned = {
            "protocol_version": PROTOCOL_VERSION,
            "instruction_id": f"host-exec-{uuid4().hex[:12]}",
            "dispatch_id": self.dispatch.dispatch_id,
            "task_id": self.dispatch.task_id,
            "route_role": route_role,
            "provider_family": provider,
            "model": model,
            "reasoning_effort": choice.reasoning,
            "attempt": attempt,
            "max_attempts": self.max_attempts_per_route,
            "task": self.dispatch.task,
            "required_capabilities": list(self.dispatch.required_capabilities),
        }
        instruction = HostExecutionInstruction(
            protocol_version=PROTOCOL_VERSION,
            instruction_id=unsigned["instruction_id"],
            dispatch_id=self.dispatch.dispatch_id,
            task_id=self.dispatch.task_id,
            route_role=route_role,
            provider_family=provider,
            model=model,
            reasoning_effort=choice.reasoning,
            attempt=attempt,
            max_attempts=self.max_attempts_per_route,
            task=self.dispatch.task,
            required_capabilities=tuple(self.dispatch.required_capabilities),
            instruction_sha256=_digest(unsigned),
        )
        self._issued_execution[instruction.instruction_id] = instruction
        self._issued_attempts[key] = instruction.instruction_id
        return instruction

    def accept_execution(self, receipt: HostExecutionReceipt) -> None:
        self._validate_dispatch_snapshot()
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
            raise HostIntegrationProtocolError(
                "execution receipt does not match the TEO-issued instruction"
            )
        key = (instruction.route_role, instruction.attempt)
        if key in self._accepted_execution:
            raise HostIntegrationProtocolError("execution receipt replay or duplicate attempt receipt")
        if receipt.status not in {"succeeded", "failed"}:
            raise HostIntegrationProtocolError("unsupported execution receipt status")
        if receipt.status == "succeeded":
            if not receipt.output_ref or not receipt.output_ref.strip() or not _valid_sha256(receipt.output_sha256):
                raise HostIntegrationProtocolError(
                    "successful execution requires output_ref and lowercase output_sha256"
                )
        elif receipt.output_ref is not None or receipt.output_sha256 is not None:
            raise HostIntegrationProtocolError(
                "failed execution must not claim successful output identity"
            )
        self._accepted_execution[key] = receipt

    def active_execution(self) -> HostExecutionReceipt:
        self._validate_dispatch_snapshot()
        fallback = self._latest_receipt("fallback")
        if fallback is not None and fallback.status == "succeeded":
            return fallback
        primary = self._latest_receipt("primary")
        if primary is not None and primary.status == "succeeded":
            return primary
        raise HostIntegrationProtocolError("no successful execution receipt is available")

    def issue_verification(self) -> HostVerificationInstruction:
        self._validate_dispatch_snapshot()
        if self._issued_verification:
            raise HostIntegrationProtocolError("verification instruction was already issued")
        active = self.active_execution()
        verifier = self.dispatch.verification.implementation
        verifier_provider = _require_text(verifier.provider_family, "verification.provider_family")
        verifier_model = _require_text(verifier.model, "verification.model")
        if self.dispatch.verification.independent:
            if verifier_model == active.model:
                raise HostIntegrationProtocolError(
                    "independent verifier cannot reuse the executor model"
                )
            if verifier_provider == active.provider_family:
                raise HostIntegrationProtocolError(
                    "independent verifier cannot reuse the executor provider family"
                )
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
        self._validate_dispatch_snapshot()
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
            raise HostIntegrationProtocolError(
                "verification receipt does not match the TEO-issued instruction"
            )
        if receipt.status not in {"passed", "failed", "needs_human"}:
            raise HostIntegrationProtocolError("unsupported verification receipt status")
        if self._verification_receipt is not None:
            raise HostIntegrationProtocolError("verification receipt replay or duplicate receipt")
        self._verification_receipt = receipt

    def evidence_projection(self) -> dict[str, Any]:
        self._validate_dispatch_snapshot()
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
            "execution_attempt": active.attempt,
            "output_ref": active.output_ref,
            "output_sha256": active.output_sha256,
            "verifier_provider_family": self._verification_receipt.verifier_provider_family,
            "verifier_model": self._verification_receipt.verifier_model,
            "verification_status": self._verification_receipt.status,
            "verification_instruction_sha256": self._verification_receipt.instruction_sha256,
        }
