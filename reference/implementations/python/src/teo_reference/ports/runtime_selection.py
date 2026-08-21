from __future__ import annotations

from typing import Protocol

from ..domain.runtime_binding import CalibratedImplementation
from ..domain.runtime_selection import (
    RuntimeSelectionDecision,
    RuntimeSelectionRequest,
)


class RuntimeFitnessPort(Protocol):
    """Provider-neutral fitness evidence for an already calibrated candidate."""

    def score(
        self,
        candidate: CalibratedImplementation,
        request: RuntimeSelectionRequest,
    ) -> float:
        """Return one finite policy-comparable fitness score."""
        ...


class RuntimeSelectionPort(Protocol):
    """Application boundary for policy-constrained runtime implementation selection."""

    def select(self, request: RuntimeSelectionRequest) -> RuntimeSelectionDecision:
        """Select one candidate without widening discovery or execution authority."""
        ...
