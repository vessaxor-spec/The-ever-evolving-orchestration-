from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ...ports.artifact import ArtifactIntegrityPort, ArtifactIntegrityPortError
from ...schemas import (
    DispatchRecord,
    ExecutionResult,
    FinalOutcome,
    VerificationResult,
    utc_now,
)


class FinalizationError(RuntimeError):
    """Raised when a final outcome cannot be accepted under the finalization contract."""


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


class FinalizationService:
    """Application service for accepting execution and verification into a final outcome."""

    def __init__(self, artifact_integrity: ArtifactIntegrityPort):
        self._artifact_integrity = artifact_integrity

    def finalize(
        self,
        dispatch: DispatchRecord,
        execution: ExecutionResult,
        verification: VerificationResult,
        *,
        artifact_root: str | Path | None = None,
    ) -> FinalOutcome:
        if execution.dispatch_id != dispatch.dispatch_id or verification.dispatch_id != dispatch.dispatch_id:
            raise FinalizationError(
                "Execution and verification records must reference the dispatch being finalized"
            )
        if verification.verifier_model != dispatch.verification.implementation.model:
            raise FinalizationError("Verification was not performed by the assigned verifier")
        if (
            dispatch.verification.independent
            and verification.verifier_model == dispatch.selected_implementation.model
        ):
            raise FinalizationError("Independent verification cannot use the selected execution model")
        if (
            dispatch.verification.independent
            and dispatch.verification.implementation.provider_family
            and dispatch.selected_implementation.provider_family
            and dispatch.verification.implementation.provider_family
            == dispatch.selected_implementation.provider_family
        ):
            raise FinalizationError(
                "Independent verification cannot use the selected execution provider family"
            )

        if verification.verified_artifact is not None and not execution.output_ref:
            raise FinalizationError("Verification artifact binding has no execution output artifact")
        if execution.status == "succeeded" and verification.status == "passed" and execution.output_ref:
            if verification.verified_artifact is None:
                raise FinalizationError(
                    "Artifact-backed passed verification requires exact verified artifact identity"
                )
            if artifact_root is None:
                raise FinalizationError(
                    "Artifact-backed passed verification requires an authorized artifact_root"
                )
            try:
                self._artifact_integrity.revalidate(
                    execution.output_ref,
                    verification.verified_artifact,
                    allowed_root=artifact_root,
                )
            except ArtifactIntegrityPortError as exc:
                raise FinalizationError(str(exc)) from exc

        notes: list[str] = []
        escalation_used = False
        if execution.status == "failed":
            if dispatch.fallback_implementation:
                status = "escalated"
                notes.append(
                    "Execution failed; an eligible fallback is available but is not recorded as executed."
                )
            else:
                status = "failed"
                notes.append("Execution failed and no eligible fallback is available.")
        elif verification.status == "failed":
            status = "failed"
            notes.append("Independent verification failed; the outcome is not accepted.")
        elif verification.status == "needs_human" or dispatch.verification.human_approval_required:
            status = "awaiting_human"
            notes.append("The verification gate requires qualified human approval.")
        else:
            status = "completed"
            notes.append("Execution and independent verification passed.")

        return FinalOutcome(
            dispatch_id=dispatch.dispatch_id,
            task_id=dispatch.task_id,
            completed_at=utc_now(),
            status=status,  # type: ignore[arg-type]
            execution_status=execution.status,
            verification_status=verification.status,
            selected_model=dispatch.selected_implementation.model,
            verifier_model=verification.verifier_model,
            evidence=_unique([*execution.evidence, *verification.evidence]),
            failed_attempts=execution.failed_attempts,
            escalation_used=escalation_used,
            notes=notes,
        )
