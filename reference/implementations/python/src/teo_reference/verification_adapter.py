from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Mapping, Protocol
from urllib.parse import unquote, urlparse

from .provider_adapter import ProviderAdapterContractError
from .provider_connection import ProviderConnection
from .schemas import DispatchRecord, VerificationResult

VerificationCheckId = Literal[
    "output_present",
    "task_adherence",
    "format_consistency",
    "unsupported_claims_absent",
]
VerificationCheckVerdict = Literal["pass", "fail", "uncertain"]
HumanReason = Literal[
    "none",
    "insufficient_evidence",
    "ambiguous_task",
    "unverifiable_output",
    "conflicting_evidence",
]

VERIFICATION_CHECKS: tuple[VerificationCheckId, ...] = (
    "output_present",
    "task_adherence",
    "format_consistency",
    "unsupported_claims_absent",
)
VERIFICATION_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["passed", "failed", "needs_human"]},
        "output_present": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
        "task_adherence": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
        "format_consistency": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
        "unsupported_claims_absent": {"type": "string", "enum": ["pass", "fail", "uncertain"]},
        "human_reason": {
            "type": "string",
            "enum": [
                "none",
                "insufficient_evidence",
                "ambiguous_task",
                "unverifiable_output",
                "conflicting_evidence",
            ],
        },
    },
    "required": [
        "status",
        "output_present",
        "task_adherence",
        "format_consistency",
        "unsupported_claims_absent",
        "human_reason",
    ],
    "additionalProperties": False,
}


class LiveVerificationError(ProviderAdapterContractError):
    """Raised when the live verification gate cannot produce valid independent evidence."""


def _require_text(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise LiveVerificationError(f"{name} is required")
    return text


@dataclass(frozen=True, slots=True)
class LiveVerificationDecision:
    status: Literal["passed", "failed", "needs_human"]
    output_present: VerificationCheckVerdict
    task_adherence: VerificationCheckVerdict
    format_consistency: VerificationCheckVerdict
    unsupported_claims_absent: VerificationCheckVerdict
    human_reason: HumanReason

    def __post_init__(self) -> None:
        if self.status not in {"passed", "failed", "needs_human"}:
            raise LiveVerificationError(f"Unsupported live verification status: {self.status}")
        verdicts = self.verdicts
        if any(value not in {"pass", "fail", "uncertain"} for value in verdicts.values()):
            raise LiveVerificationError("Live verification contains an unsupported criterion verdict")
        if self.human_reason not in {
            "none",
            "insufficient_evidence",
            "ambiguous_task",
            "unverifiable_output",
            "conflicting_evidence",
        }:
            raise LiveVerificationError("Live verification contains an unsupported human reason")

        failures = [name for name, value in verdicts.items() if value == "fail"]
        uncertain = [name for name, value in verdicts.items() if value == "uncertain"]
        if self.status == "passed":
            if failures or uncertain or self.human_reason != "none":
                raise LiveVerificationError(
                    "Passed live verification requires every criterion to pass and no human reason"
                )
        elif self.status == "failed":
            if not failures or uncertain or self.human_reason != "none":
                raise LiveVerificationError(
                    "Failed live verification requires at least one failed criterion, no uncertain criteria, and no human reason"
                )
        else:
            if failures or not uncertain or self.human_reason == "none":
                raise LiveVerificationError(
                    "needs_human requires uncertainty, no definitive failed criterion, and an explicit human reason"
                )

    @property
    def verdicts(self) -> dict[VerificationCheckId, VerificationCheckVerdict]:
        return {
            "output_present": self.output_present,
            "task_adherence": self.task_adherence,
            "format_consistency": self.format_consistency,
            "unsupported_claims_absent": self.unsupported_claims_absent,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LiveVerificationDecision":
        expected = {
            "status",
            "output_present",
            "task_adherence",
            "format_consistency",
            "unsupported_claims_absent",
            "human_reason",
        }
        unknown = sorted(set(data) - expected)
        missing = sorted(expected - set(data))
        if unknown:
            raise LiveVerificationError(
                f"Live verification response contains unsupported fields: {', '.join(unknown)}"
            )
        if missing:
            raise LiveVerificationError(
                f"Live verification response is missing fields: {', '.join(missing)}"
            )
        return cls(
            status=str(data["status"]),  # type: ignore[arg-type]
            output_present=str(data["output_present"]),  # type: ignore[arg-type]
            task_adherence=str(data["task_adherence"]),  # type: ignore[arg-type]
            format_consistency=str(data["format_consistency"]),  # type: ignore[arg-type]
            unsupported_claims_absent=str(data["unsupported_claims_absent"]),  # type: ignore[arg-type]
            human_reason=str(data["human_reason"]),  # type: ignore[arg-type]
        )

    def to_verification_result(self, dispatch: DispatchRecord, *, evidence: list[str]) -> VerificationResult:
        checks = [f"{name}:{verdict}" for name, verdict in self.verdicts.items()]
        notes = (
            f"live_verifier_human_reason:{self.human_reason}"
            if self.status == "needs_human"
            else None
        )
        return VerificationResult(
            dispatch_id=dispatch.dispatch_id,
            status=self.status,
            verifier_model=dispatch.verification.implementation.model,
            checks=checks,
            evidence=evidence,
            notes=notes,
        )


@dataclass(frozen=True, slots=True)
class LiveVerificationRequest:
    dispatch_id: str
    task_id: str
    verifier_provider_family: str
    verifier_model: str
    verifier_reasoning_effort: str | None
    risk_level: str
    verification_methods: tuple[str, ...]
    task: str
    output_text: str

    @classmethod
    def from_execution(
        cls,
        dispatch: DispatchRecord,
        output_text: str,
    ) -> "LiveVerificationRequest":
        verifier = dispatch.verification.implementation
        if not verifier.provider_family:
            raise LiveVerificationError("Assigned verifier has no provider family")
        if not dispatch.verification.independent:
            raise LiveVerificationError("Live canary verification requires an independent verifier")
        if verifier.model == dispatch.selected_implementation.model:
            raise LiveVerificationError("Live verification refuses same-model self-verification")
        return cls(
            dispatch_id=_require_text(dispatch.dispatch_id, "dispatch_id"),
            task_id=_require_text(dispatch.task_id, "task_id"),
            verifier_provider_family=_require_text(verifier.provider_family, "verifier provider family"),
            verifier_model=_require_text(verifier.model, "verifier model"),
            verifier_reasoning_effort=verifier.reasoning,
            risk_level=dispatch.risk_level,
            verification_methods=tuple(str(item) for item in dispatch.verification.method),
            task=_require_text(dispatch.task, "task"),
            output_text=_require_text(output_text, "execution output"),
        )

    def blinded_prompt(self) -> str:
        methods = ", ".join(self.verification_methods) if self.verification_methods else "output_validation"
        return (
            "Evaluate the candidate output against the original task using only the evidence supplied here.\n"
            "Do not infer who produced the output. Do not reward style, verbosity, confidence, or familiarity.\n"
            "Do not guess semantic ground truth that is absent from the task. If required evidence is missing, use uncertain and needs_human.\n"
            f"Verification methods: {methods}\n\n"
            f"ORIGINAL TASK:\n{self.task}\n\n"
            f"CANDIDATE OUTPUT:\n{self.output_text}\n\n"
            "Criteria:\n"
            "- output_present: output is present and usable.\n"
            "- task_adherence: output follows the observable instructions in the task.\n"
            "- format_consistency: output structure is internally consistent with the requested work.\n"
            "- unsupported_claims_absent: output does not claim completion, correctness, or evidence that cannot be supported from the supplied task/output.\n"
            "Return only the structured decision."
        )


@dataclass(frozen=True, slots=True)
class LiveVerificationResponse:
    decision: LiveVerificationDecision
    provider_family: str
    model: str
    evidence: tuple[str, ...] = ()


class LiveVerifierAdapter(Protocol):
    provider_family: str

    def verify(self, request: LiveVerificationRequest) -> LiveVerificationResponse:
        ...


def read_execution_output(output_ref: str, *, max_bytes: int = 65536) -> str:
    parsed = urlparse(_require_text(output_ref, "output_ref"))
    if parsed.scheme != "file":
        raise LiveVerificationError(
            "Guarded live verification accepts only local file output artifacts"
        )
    path = Path(unquote(parsed.path))
    if not path.is_file():
        raise LiveVerificationError("Execution output artifact does not exist")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise LiveVerificationError("Execution output artifact could not be inspected") from exc
    if size > max_bytes:
        raise LiveVerificationError(
            f"Execution output artifact exceeds guarded verification limit of {max_bytes} bytes"
        )
    try:
        return _require_text(path.read_text(encoding="utf-8"), "execution output")
    except (OSError, UnicodeDecodeError) as exc:
        raise LiveVerificationError("Execution output artifact could not be read as UTF-8") from exc


def decode_structured_decision(text: str) -> LiveVerificationDecision:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LiveVerificationError("Verifier returned malformed structured JSON") from exc
    if not isinstance(payload, dict):
        raise LiveVerificationError("Verifier structured output must be a JSON object")
    return LiveVerificationDecision.from_dict(payload)


def validate_verifier_connection(
    request: LiveVerificationRequest,
    connections: Mapping[str, ProviderConnection],
) -> ProviderConnection:
    connection = connections.get(request.verifier_provider_family)
    if connection is None:
        raise LiveVerificationError(
            f"No runtime connection is available for assigned verifier provider {request.verifier_provider_family}"
        )
    if connection.provider_family != request.verifier_provider_family:
        raise LiveVerificationError("Verifier connection provider family does not match assigned verifier")
    return connection
