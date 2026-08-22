from __future__ import annotations

import json
from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from ..domain.runtime_binding import AuthorityScope, CalibratedImplementation, RuntimeImplementation, select_best
from ..domain.runtime_selection import RuntimeSelectionDecision, RuntimeSelectionError, RuntimeSelectionPin, RuntimeSelectionRequest
from ..ports.runtime_calibration import RuntimeCalibrationRecordPort
from ..ports.runtime_eligibility import RuntimeEligibilityEvidencePort
from ..ports.runtime_inventory import RuntimeInventoryPort
from ..ports.runtime_selection import RuntimeFitnessPort
from .runtime_calibration import RuntimeCalibrationService
from .runtime_eligibility import RuntimeEligibilityService


@dataclass(frozen=True, slots=True)
class _SnapshotInventory:
    implementations: tuple[RuntimeImplementation, ...]

    def discover(self) -> Sequence[RuntimeImplementation]:
        return self.implementations


class RuntimeSelectionService:
    """Select best fit only after discovery, eligibility, and calibration."""

    def __init__(
        self,
        *,
        inventory: RuntimeInventoryPort,
        eligibility_evidence: RuntimeEligibilityEvidencePort,
        calibration_records: RuntimeCalibrationRecordPort,
        fitness: RuntimeFitnessPort,
        pins: Sequence[RuntimeSelectionPin] = (),
    ) -> None:
        self._inventory = inventory
        self._eligibility_evidence = eligibility_evidence
        self._calibration_records = calibration_records
        self._fitness = fitness
        self._pins = tuple(pins)
        if any(not isinstance(pin, RuntimeSelectionPin) for pin in self._pins):
            raise RuntimeSelectionError("runtime selection pins must be RuntimeSelectionPin values")

    @staticmethod
    def _authorized(implementation: RuntimeImplementation, request: RuntimeSelectionRequest) -> bool:
        configuration = implementation.configuration
        if request.authorized_implementation_ids and implementation.implementation_id not in request.authorized_implementation_ids:
            return False
        if request.authorized_models and configuration.model not in request.authorized_models:
            return False
        if implementation.implementation_id in request.excluded_implementation_ids:
            return False
        if configuration.model in request.excluded_models:
            return False
        if configuration.provider_family and configuration.provider_family in request.excluded_providers:
            return False
        required_effort = request.reasoning_effort_for(configuration.model)
        if required_effort is not None:
            encoded_effort = dict(configuration.reasoning_controls).get("effort")
            if encoded_effort is None:
                return False
            try:
                actual_effort = json.loads(encoded_effort)
            except (TypeError, json.JSONDecodeError):
                return False
            if str(actual_effort) != required_effort:
                return False
        return True

    def _snapshot(self) -> tuple[RuntimeImplementation, ...]:
        raw = tuple(self._inventory.discover())
        by_id: dict[str, RuntimeImplementation] = {}
        for implementation in raw:
            if not isinstance(implementation, RuntimeImplementation):
                raise RuntimeSelectionError("runtime inventory returned a non-RuntimeImplementation value")
            implementation_id = implementation.implementation_id
            if implementation_id in by_id:
                raise RuntimeSelectionError(
                    "runtime selection requires unique implementation ids: " + implementation_id
                )
            by_id[implementation_id] = implementation
        return tuple(by_id[key] for key in sorted(by_id))

    def _active_pin(self, request: RuntimeSelectionRequest) -> RuntimeSelectionPin | None:
        active = tuple(
            pin
            for pin in self._pins
            if pin.active_for(
                request.scope,
                evaluated_at=request.evaluated_at,
                satisfied_removal_conditions=request.satisfied_pin_removal_conditions,
            )
        )
        if len(active) > 1:
            raise RuntimeSelectionError(
                "multiple runtime pins match the same selection scope: "
                + ", ".join(pin.pin_id for pin in active)
            )
        return active[0] if active else None

    def select(self, request: RuntimeSelectionRequest) -> RuntimeSelectionDecision:
        if not isinstance(request, RuntimeSelectionRequest):
            raise RuntimeSelectionError("runtime selection requires a RuntimeSelectionRequest")

        inventory = self._snapshot()
        authorized_ids = frozenset(
            item.implementation_id for item in inventory if self._authorized(item, request)
        )
        authority = AuthorityScope(authorized_ids)

        eligibility = RuntimeEligibilityService(
            _SnapshotInventory(inventory), self._eligibility_evidence
        ).evaluate(authority=authority, requirements=request.eligibility_requirements)
        eligible_candidates = tuple(
            item.decision.eligible for item in eligibility.eligible if item.decision.eligible is not None
        )

        calibration = RuntimeCalibrationService(self._calibration_records).evaluate(
            eligible_candidates,
            requirements=request.calibration_requirements,
            evaluated_at=request.evaluated_at,
        )
        calibrated_candidates = tuple(
            item.calibrated for item in calibration.calibrated if item.calibrated is not None
        )

        pin = self._active_pin(request)
        if pin is not None:
            target = next(
                (
                    candidate
                    for candidate in calibrated_candidates
                    if candidate.implementation.implementation_id == pin.implementation_id
                ),
                None,
            )
            if target is None:
                raise RuntimeSelectionError(
                    f"runtime pin {pin.pin_id} target is not currently authorized, eligible, calibrated, and execution-config compatible"
                )
            selected = select_best(
                [target],
                fitness_scores={target.implementation.implementation_id: 0.0},
                selection_reason=f"runtime pin {pin.pin_id}: {pin.reason}",
                evaluated_at=request.evaluated_at,
            )
            return RuntimeSelectionDecision(
                selected=selected,
                eligible_candidate_count=len(eligible_candidates),
                calibrated_candidate_count=len(calibrated_candidates),
                pin_id=pin.pin_id,
            )

        if not calibrated_candidates:
            reasons: list[str] = []
            for item in eligibility.rejected:
                reasons.extend(item.decision.reasons)
            for item in calibration.rejected:
                reasons.extend(item.reasons)
            detail = "; ".join(dict.fromkeys(reasons)) or (
                "no candidate satisfied authority, execution configuration, eligibility, and calibration"
            )
            raise RuntimeSelectionError(
                "no authorized eligible calibrated runtime implementation is selectable: " + detail
            )

        fitness_scores: dict[str, float] = {}
        for candidate in calibrated_candidates:
            implementation_id = candidate.implementation.implementation_id
            score = float(self._fitness.score(candidate, request))
            if not isfinite(score):
                raise RuntimeSelectionError(f"runtime fitness score must be finite: {implementation_id}")
            fitness_scores[implementation_id] = score

        selected = select_best(
            calibrated_candidates,
            fitness_scores=fitness_scores,
            selection_reason="highest policy-constrained runtime fitness",
            evaluated_at=request.evaluated_at,
        )
        return RuntimeSelectionDecision(
            selected=selected,
            eligible_candidate_count=len(eligible_candidates),
            calibrated_candidate_count=len(calibrated_candidates),
        )