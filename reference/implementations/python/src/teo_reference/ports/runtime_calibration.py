from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..domain.runtime_binding import CalibrationRecord


class RuntimeCalibrationEvidenceUnavailable(RuntimeError):
    """Raised when runtime calibration evidence cannot be obtained."""


class RuntimeCalibrationRecordPort(Protocol):
    """Provider-independent source of calibration history by exact configuration.

    The port exposes evidence only. It does not decide eligibility, calibration
    freshness, selection fitness, routing authority, or execution permission.
    """

    def records_for(self, configuration_fingerprint: str) -> Sequence[CalibrationRecord]:
        """Return calibration records bound to the exact execution configuration."""
        ...
