from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from .runtime_binding import CalibrationRequirements, EligibilityRequirements, SelectedImplementation

SelectionRole = Literal["primary", "fallback", "verifier"]


class RuntimeSelectionError(RuntimeError):
    """Raised when runtime selection would violate policy or lifecycle invariants."""


def _require_text(value: str | None, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RuntimeSelectionError(f"{name} is required")
    return text


def _parse_instant(value: str, name: str) -> datetime:
    text = _require_text(value, name)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RuntimeSelectionError(f"{name} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RuntimeSelectionError(f"{name} must include an explicit timezone offset")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class RuntimeSelectionScope:
    task_id: str
    task_type: str
    worker: str
    role: SelectionRole

    def __post_init__(self) -> None:
        _require_text(self.task_id, "selection scope task_id")
        _require_text(self.task_type, "selection scope task_type")
        _require_text(self.worker, "selection scope worker")
        if self.role not in {"primary", "fallback", "verifier"}:
            raise RuntimeSelectionError(f"unsupported selection role: {self.role}")


@dataclass(frozen=True, slots=True)
class RuntimeSelectionPin:
    pin_id: str
    implementation_id: str
    role: SelectionRole
    reason: str
    task_id: str | None = None
    task_type: str | None = None
    worker: str | None = None
    expires_at: str | None = None
    removal_conditions: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        _require_text(self.pin_id, "pin_id")
        _require_text(self.implementation_id, "pin implementation_id")
        _require_text(self.reason, "pin reason")
        if self.role not in {"primary", "fallback", "verifier"}:
            raise RuntimeSelectionError(f"unsupported pin role: {self.role}")
        if not any(str(value or "").strip() for value in (self.task_id, self.task_type, self.worker)):
            raise RuntimeSelectionError("runtime pin must be scoped by task_id, task_type, or worker")
        if self.expires_at is None and not self.removal_conditions:
            raise RuntimeSelectionError("runtime pin requires expires_at or at least one removal condition")
        if self.expires_at is not None:
            _parse_instant(self.expires_at, "pin expires_at")
        if any(not str(item).strip() for item in self.removal_conditions):
            raise RuntimeSelectionError("pin removal conditions cannot contain empty values")

    def active_for(self, scope: RuntimeSelectionScope, *, evaluated_at: str, satisfied_removal_conditions: frozenset[str]) -> bool:
        if self.role != scope.role:
            return False
        if self.task_id is not None and self.task_id != scope.task_id:
            return False
        if self.task_type is not None and self.task_type != scope.task_type:
            return False
        if self.worker is not None and self.worker != scope.worker:
            return False
        if self.removal_conditions.intersection(satisfied_removal_conditions):
            return False
        evaluated = _parse_instant(evaluated_at, "evaluated_at")
        if self.expires_at is not None and evaluated >= _parse_instant(self.expires_at, "pin expires_at"):
            return False
        return True


@dataclass(frozen=True, slots=True)
class RuntimeSelectionRequest:
    scope: RuntimeSelectionScope
    eligibility_requirements: EligibilityRequirements
    calibration_requirements: CalibrationRequirements
    evaluated_at: str
    authorized_implementation_ids: frozenset[str] = field(default_factory=frozenset)
    authorized_models: frozenset[str] = field(default_factory=frozenset)
    excluded_implementation_ids: frozenset[str] = field(default_factory=frozenset)
    excluded_models: frozenset[str] = field(default_factory=frozenset)
    excluded_providers: frozenset[str] = field(default_factory=frozenset)
    preferred_models: tuple[str, ...] = ()
    reasoning_effort_by_model: tuple[tuple[str, str], ...] = ()
    satisfied_pin_removal_conditions: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not isinstance(self.scope, RuntimeSelectionScope):
            raise RuntimeSelectionError("selection request requires RuntimeSelectionScope")
        if not isinstance(self.eligibility_requirements, EligibilityRequirements):
            raise RuntimeSelectionError("selection request requires EligibilityRequirements")
        if not isinstance(self.calibration_requirements, CalibrationRequirements):
            raise RuntimeSelectionError("selection request requires CalibrationRequirements")
        _parse_instant(self.evaluated_at, "evaluated_at")
        if not self.authorized_implementation_ids and not self.authorized_models:
            raise RuntimeSelectionError("selection request requires explicit implementation-id or model authority")
        if len(set(self.preferred_models)) != len(self.preferred_models):
            raise RuntimeSelectionError("preferred_models must not contain duplicates")
        reasoning_models = [model for model, _ in self.reasoning_effort_by_model]
        if len(reasoning_models) != len(set(reasoning_models)):
            raise RuntimeSelectionError("reasoning_effort_by_model must not contain duplicate models")
        if any(not str(model).strip() or not str(effort).strip() for model, effort in self.reasoning_effort_by_model):
            raise RuntimeSelectionError("reasoning_effort_by_model cannot contain empty values")
        for name, values in (
            ("authorized_implementation_ids", self.authorized_implementation_ids),
            ("authorized_models", self.authorized_models),
            ("excluded_implementation_ids", self.excluded_implementation_ids),
            ("excluded_models", self.excluded_models),
            ("excluded_providers", self.excluded_providers),
            ("satisfied_pin_removal_conditions", self.satisfied_pin_removal_conditions),
        ):
            if any(not str(item).strip() for item in values):
                raise RuntimeSelectionError(f"{name} cannot contain empty values")

    def reasoning_effort_for(self, model: str) -> str | None:
        return dict(self.reasoning_effort_by_model).get(model)


@dataclass(frozen=True, slots=True)
class RuntimeSelectionDecision:
    selected: SelectedImplementation
    eligible_candidate_count: int
    calibrated_candidate_count: int
    pin_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.selected, SelectedImplementation):
            raise RuntimeSelectionError("selection decision requires a SelectedImplementation")
        if self.eligible_candidate_count < 0 or self.calibrated_candidate_count < 0:
            raise RuntimeSelectionError("selection candidate counts cannot be negative")
        if self.calibrated_candidate_count > self.eligible_candidate_count:
            raise RuntimeSelectionError("calibrated candidate count cannot exceed eligible candidate count")
