from __future__ import annotations

from typing import Protocol

from ..domain.runtime_binding import EligibilityEvidence, RuntimeImplementation


class RuntimeEligibilityEvidenceUnavailable(RuntimeError):
    """Raised when required runtime eligibility evidence cannot be obtained."""


class RuntimeEligibilityEvidencePort(Protocol):
    """Provider-independent evidence source for runtime eligibility evaluation.

    Implementations may obtain reachability, health, privacy, and runtime-constraint
    observations from any installation-valid surface. The port reports evidence only;
    it does not grant authority, calibration, selection, or execution permission.
    """

    def observe(self, implementation: RuntimeImplementation) -> EligibilityEvidence:
        """Return current eligibility evidence for one discovered implementation."""
        ...
