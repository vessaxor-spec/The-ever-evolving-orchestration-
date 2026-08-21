from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..domain.runtime_binding import CalibrationRecord


class RuntimeCalibrationAdapterError(RuntimeError):
    """Raised when declared calibration history is structurally ambiguous."""


@dataclass(frozen=True, slots=True)
class DeclaredRuntimeCalibrationAdapter:
    """Provider-neutral in-memory calibration history adapter.

    Multiple records may exist for one execution-configuration fingerprint so
    calibration history can be retained. An evidence reference must be unique
    within one fingerprint to prevent an ambiguous record from being silently
    shadowed by another declaration.
    """

    records: tuple[CalibrationRecord, ...] = ()

    def __post_init__(self) -> None:
        seen: set[tuple[str, str]] = set()
        for record in self.records:
            if not isinstance(record, CalibrationRecord):
                raise RuntimeCalibrationAdapterError(
                    "calibration adapter contains a non-CalibrationRecord value"
                )
            identity = (record.configuration_fingerprint, record.evidence_ref)
            if identity in seen:
                raise RuntimeCalibrationAdapterError(
                    "calibration evidence_ref must be unique within one execution "
                    f"configuration: {record.evidence_ref}"
                )
            seen.add(identity)

    def records_for(self, configuration_fingerprint: str) -> Sequence[CalibrationRecord]:
        return tuple(
            record
            for record in self.records
            if record.configuration_fingerprint == configuration_fingerprint
        )
