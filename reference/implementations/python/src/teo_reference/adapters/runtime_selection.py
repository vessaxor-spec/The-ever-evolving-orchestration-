from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType
from typing import Mapping

from ..domain.runtime_binding import CalibratedImplementation
from ..domain.runtime_selection import RuntimeSelectionRequest


class RuntimeFitnessAdapterError(RuntimeError):
    """Raised when declared runtime fitness evidence is missing or invalid."""


class DeclaredRuntimeFitnessAdapter:
    """Provider-neutral exact-ID fitness evidence.

    Fitness is evidence only. Missing candidate scores fail closed and this adapter
    cannot discover, authorize, calibrate, pin, select, or execute implementations.
    """

    def __init__(self, scores_by_implementation_id: Mapping[str, float]) -> None:
        normalized: dict[str, float] = {}
        for implementation_id, raw_score in dict(scores_by_implementation_id).items():
            key = str(implementation_id).strip()
            if not key:
                raise RuntimeFitnessAdapterError(
                    "fitness implementation_id cannot be empty"
                )
            score = float(raw_score)
            if not isfinite(score):
                raise RuntimeFitnessAdapterError(
                    f"fitness score must be finite: {key}"
                )
            normalized[key] = score
        self._scores = MappingProxyType(normalized)

    def score(
        self,
        candidate: CalibratedImplementation,
        request: RuntimeSelectionRequest,
    ) -> float:
        implementation_id = candidate.implementation.implementation_id
        if implementation_id not in self._scores:
            raise RuntimeFitnessAdapterError(
                f"missing runtime fitness evidence: {implementation_id}"
            )
        return self._scores[implementation_id]


@dataclass(frozen=True, slots=True)
class PreferenceRuntimeFitnessAdapter:
    """Transitional known-good preference prior for RMI-5/RMI-7 migration.

    The ordered model preference is not authority: it is consulted only for candidates
    that already passed authorization, eligibility, and calibration. Exact runtime
    evidence may add candidate-specific adjustments. RMI-7 can remove configured model
    preferences without changing the selection lifecycle.
    """

    candidate_adjustments: Mapping[str, float] = field(default_factory=dict)
    preferred_model_step: float = 1.0

    def __post_init__(self) -> None:
        step = float(self.preferred_model_step)
        if not isfinite(step) or step <= 0:
            raise RuntimeFitnessAdapterError(
                "preferred_model_step must be a positive finite value"
            )
        normalized: dict[str, float] = {}
        for implementation_id, raw_score in dict(self.candidate_adjustments).items():
            key = str(implementation_id).strip()
            if not key:
                raise RuntimeFitnessAdapterError(
                    "fitness adjustment implementation_id cannot be empty"
                )
            score = float(raw_score)
            if not isfinite(score):
                raise RuntimeFitnessAdapterError(
                    f"fitness adjustment must be finite: {key}"
                )
            normalized[key] = score
        object.__setattr__(self, "candidate_adjustments", MappingProxyType(normalized))
        object.__setattr__(self, "preferred_model_step", step)

    def score(
        self,
        candidate: CalibratedImplementation,
        request: RuntimeSelectionRequest,
    ) -> float:
        implementation = candidate.implementation
        model = implementation.configuration.model
        preference = 0.0
        try:
            index = request.preferred_models.index(model)
        except ValueError:
            index = -1
        if index >= 0:
            preference = (len(request.preferred_models) - index) * self.preferred_model_step
        return preference + float(
            self.candidate_adjustments.get(implementation.implementation_id, 0.0)
        )
