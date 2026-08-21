from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence

from ..domain.runtime_binding import (
    CalibratedImplementation,
    CalibrationRecord,
    CalibrationRequirements,
    EligibleImplementation,
    RuntimeBindingError,
    apply_calibration,
)
from ..ports.runtime_calibration import (
    RuntimeCalibrationEvidenceUnavailable,
    RuntimeCalibrationRecordPort,
)


class RuntimeCalibrationEvaluationError(RuntimeError):
    """Raised when runtime calibration inputs are structurally invalid."""


def _timestamp_rank(value: str | None) -> float:
    if value is None:
        return float("-inf")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RuntimeCalibrationEvaluationError(
            "calibration timestamps must be valid ISO-8601 timestamps"
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RuntimeCalibrationEvaluationError(
            "calibration timestamps must include an explicit timezone offset"
        )
    return parsed.astimezone(timezone.utc).timestamp()


@dataclass(frozen=True, slots=True)
class RuntimeCalibrationAssessment:
    eligible: EligibleImplementation
    records: tuple[CalibrationRecord, ...]
    calibrated: CalibratedImplementation | None
    reasons: tuple[str, ...] = ()
    evidence_error: str | None = None

    @property
    def implementation_id(self) -> str:
        return self.eligible.implementation.implementation_id

    @property
    def satisfied(self) -> bool:
        return self.calibrated is not None


@dataclass(frozen=True, slots=True)
class RuntimeCalibrationSnapshot:
    """Deterministic calibration result for eligible runtime candidates."""

    assessments: tuple[RuntimeCalibrationAssessment, ...]
    evaluated_at: str

    def __post_init__(self) -> None:
        implementation_ids = [item.implementation_id for item in self.assessments]
        if len(implementation_ids) != len(set(implementation_ids)):
            raise RuntimeCalibrationEvaluationError(
                "calibration snapshot cannot contain duplicate implementation ids"
            )

    @property
    def calibrated(self) -> tuple[RuntimeCalibrationAssessment, ...]:
        return tuple(item for item in self.assessments if item.satisfied)

    @property
    def rejected(self) -> tuple[RuntimeCalibrationAssessment, ...]:
        return tuple(item for item in self.assessments if not item.satisfied)

    def get(self, implementation_id: str) -> RuntimeCalibrationAssessment | None:
        for assessment in self.assessments:
            if assessment.implementation_id == implementation_id:
                return assessment
        return None


class RuntimeCalibrationService:
    """Qualify exact execution configurations against calibration freshness policy.

    The service consumes already-eligible candidates. It cannot discover candidates,
    widen authority, rank fitness, select routes, or execute providers. A missing or
    unavailable calibration record fails closed unless an exact configuration-bound
    record explicitly states that calibration is not required by the supplied policy.
    """

    def __init__(self, records: RuntimeCalibrationRecordPort) -> None:
        self._records = records

    def evaluate(
        self,
        eligible: Sequence[EligibleImplementation],
        *,
        requirements: CalibrationRequirements,
        evaluated_at: str,
    ) -> RuntimeCalibrationSnapshot:
        if not isinstance(requirements, CalibrationRequirements):
            raise RuntimeCalibrationEvaluationError(
                "runtime calibration requires CalibrationRequirements"
            )
        _timestamp_rank(evaluated_at)

        by_id: dict[str, EligibleImplementation] = {}
        for candidate in eligible:
            if not isinstance(candidate, EligibleImplementation):
                raise RuntimeCalibrationEvaluationError(
                    "runtime calibration requires EligibleImplementation candidates"
                )
            implementation_id = candidate.implementation.implementation_id
            if implementation_id in by_id:
                raise RuntimeCalibrationEvaluationError(
                    "runtime calibration requires unique implementation ids: "
                    f"{implementation_id}"
                )
            by_id[implementation_id] = candidate

        assessments: list[RuntimeCalibrationAssessment] = []
        for implementation_id in sorted(by_id):
            candidate = by_id[implementation_id]
            fingerprint = candidate.implementation.configuration.fingerprint
            evidence_error: str | None = None
            try:
                raw_records = tuple(self._records.records_for(fingerprint))
            except RuntimeCalibrationEvidenceUnavailable as exc:
                raw_records = ()
                evidence_error = str(exc).strip() or "calibration evidence unavailable"

            records: list[CalibrationRecord] = []
            for record in raw_records:
                if not isinstance(record, CalibrationRecord):
                    raise RuntimeCalibrationEvaluationError(
                        "calibration evidence source returned a non-CalibrationRecord "
                        f"value for {implementation_id}"
                    )
                if record.configuration_fingerprint != fingerprint:
                    raise RuntimeCalibrationEvaluationError(
                        "calibration evidence source returned a record for the wrong "
                        f"execution configuration: {implementation_id}"
                    )
                if record not in records:
                    records.append(record)

            if not records:
                reason = (
                    "calibration evidence unavailable"
                    if evidence_error is not None
                    else "no calibration record for exact execution configuration"
                )
                assessments.append(
                    RuntimeCalibrationAssessment(
                        eligible=candidate,
                        records=(),
                        calibrated=None,
                        reasons=(reason,),
                        evidence_error=evidence_error,
                    )
                )
                continue

            accepted: list[CalibratedImplementation] = []
            rejected_reasons: list[str] = []
            for record in records:
                try:
                    accepted.append(
                        apply_calibration(
                            candidate,
                            record,
                            requirements=requirements,
                            evaluated_at=evaluated_at,
                        )
                    )
                except RuntimeBindingError as exc:
                    rejected_reasons.append(f"{record.evidence_ref}: {exc}")

            if accepted:
                chosen = max(
                    accepted,
                    key=lambda item: (
                        1 if item.calibration.status == "passed" else 0,
                        _timestamp_rank(item.calibration.calibrated_at),
                        _timestamp_rank(item.calibration.valid_until),
                        item.calibration.evidence_ref,
                    ),
                )
                assessments.append(
                    RuntimeCalibrationAssessment(
                        eligible=candidate,
                        records=tuple(records),
                        calibrated=chosen,
                        evidence_error=evidence_error,
                    )
                )
                continue

            assessments.append(
                RuntimeCalibrationAssessment(
                    eligible=candidate,
                    records=tuple(records),
                    calibrated=None,
                    reasons=tuple(dict.fromkeys(rejected_reasons)),
                    evidence_error=evidence_error,
                )
            )

        return RuntimeCalibrationSnapshot(
            assessments=tuple(assessments),
            evaluated_at=evaluated_at,
        )
