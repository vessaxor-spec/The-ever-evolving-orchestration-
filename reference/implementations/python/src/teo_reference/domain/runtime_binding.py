from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import isfinite
from typing import Literal, Mapping, Sequence

InventoryState = Literal[
    "running",
    "available_local",
    "available_remote",
    "user_declared",
    "unavailable",
]
BindingState = Literal["discovered", "eligible", "calibrated", "selected"]
CalibrationStatus = Literal["passed", "not_required"]

_EXECUTABLE_INVENTORY_STATES = {
    "running",
    "available_local",
    "available_remote",
    "user_declared",
}


class RuntimeBindingError(RuntimeError):
    """Raised when runtime binding would violate a lifecycle or authority invariant."""


def _require_text(value: str | None, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RuntimeBindingError(f"{name} is required")
    return text


def _parse_instant(value: str | None, name: str) -> datetime:
    text = _require_text(value, name)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RuntimeBindingError(f"{name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RuntimeBindingError(f"{name} must include an explicit timezone offset")
    return parsed.astimezone(timezone.utc)


def _normalized_pairs(values: Mapping[str, object] | None) -> tuple[tuple[str, str], ...]:
    if not values:
        return ()
    return tuple(
        sorted(
            (
                str(key),
                json.dumps(value, sort_keys=True, separators=(",", ":")),
            )
            for key, value in values.items()
        )
    )


@dataclass(frozen=True, slots=True)
class ExecutionConfigurationIdentity:
    """Identity of the concrete execution configuration, not just a marketing model name."""

    implementation_id: str
    model: str
    runtime: str
    provider_family: str | None = None
    version: str | None = None
    digest: str | None = None
    quantization: str | None = None
    context_window: int | None = None
    hardware: str | None = None
    serving_stack: str | None = None
    tools: tuple[str, ...] = ()
    reasoning_controls: tuple[tuple[str, str], ...] = ()
    material_settings: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_text(self.implementation_id, "implementation_id")
        _require_text(self.model, "model")
        _require_text(self.runtime, "runtime")
        if self.context_window is not None and self.context_window <= 0:
            raise RuntimeBindingError("context_window must be positive when provided")
        if len(set(self.tools)) != len(self.tools):
            raise RuntimeBindingError("tools must not contain duplicates")

    @classmethod
    def from_runtime(
        cls,
        *,
        implementation_id: str,
        model: str,
        runtime: str,
        provider_family: str | None = None,
        version: str | None = None,
        digest: str | None = None,
        quantization: str | None = None,
        context_window: int | None = None,
        hardware: str | None = None,
        serving_stack: str | None = None,
        tools: Sequence[str] = (),
        reasoning_controls: Mapping[str, object] | None = None,
        material_settings: Mapping[str, object] | None = None,
    ) -> "ExecutionConfigurationIdentity":
        return cls(
            implementation_id=implementation_id,
            model=model,
            runtime=runtime,
            provider_family=provider_family,
            version=version,
            digest=digest,
            quantization=quantization,
            context_window=context_window,
            hardware=hardware,
            serving_stack=serving_stack,
            tools=tuple(sorted(str(tool) for tool in tools)),
            reasoning_controls=_normalized_pairs(reasoning_controls),
            material_settings=_normalized_pairs(material_settings),
        )

    @property
    def fingerprint(self) -> str:
        payload = {
            "implementation_id": self.implementation_id,
            "model": self.model,
            "runtime": self.runtime,
            "provider_family": self.provider_family,
            "version": self.version,
            "digest": self.digest,
            "quantization": self.quantization,
            "context_window": self.context_window,
            "hardware": self.hardware,
            "serving_stack": self.serving_stack,
            "tools": list(self.tools),
            "reasoning_controls": list(self.reasoning_controls),
            "material_settings": list(self.material_settings),
        }
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class RuntimeImplementation:
    configuration: ExecutionConfigurationIdentity
    inventory_state: InventoryState
    capabilities: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.inventory_state not in {
            "running",
            "available_local",
            "available_remote",
            "user_declared",
            "unavailable",
        }:
            raise RuntimeBindingError(f"unsupported inventory_state: {self.inventory_state}")
        if not self.capabilities:
            raise RuntimeBindingError(
                "runtime implementation requires at least one declared capability"
            )
        if any(not str(capability).strip() for capability in self.capabilities):
            raise RuntimeBindingError("capabilities cannot contain empty values")

    @property
    def implementation_id(self) -> str:
        return self.configuration.implementation_id


@dataclass(frozen=True, slots=True)
class DiscoveredImplementation:
    implementation: RuntimeImplementation
    state: Literal["discovered"] = "discovered"


@dataclass(frozen=True, slots=True)
class AuthorityScope:
    """Explicit runtime authority set. Discovery never adds members to this set."""

    allowed_implementation_ids: frozenset[str]

    def __post_init__(self) -> None:
        if any(not str(item).strip() for item in self.allowed_implementation_ids):
            raise RuntimeBindingError(
                "authority scope cannot contain empty implementation ids"
            )

    def permits(self, implementation_id: str) -> bool:
        return implementation_id in self.allowed_implementation_ids


@dataclass(frozen=True, slots=True)
class EligibilityRequirements:
    required_capabilities: frozenset[str] = field(default_factory=frozenset)
    require_reachable: bool = True
    require_healthy: bool = True
    require_privacy_allowed: bool = True
    require_runtime_constraints: bool = True


@dataclass(frozen=True, slots=True)
class EligibilityEvidence:
    reachable: bool | None = None
    healthy: bool | None = None
    privacy_allowed: bool | None = None
    runtime_constraints_satisfied: bool | None = None


def _eligibility_reasons(
    discovered: DiscoveredImplementation,
    *,
    authority: AuthorityScope,
    requirements: EligibilityRequirements,
    evidence: EligibilityEvidence,
) -> tuple[str, ...]:
    implementation = discovered.implementation
    reasons: list[str] = []

    if implementation.inventory_state == "unavailable":
        reasons.append("implementation is unavailable")
    elif implementation.inventory_state not in _EXECUTABLE_INVENTORY_STATES:
        reasons.append(
            f"inventory state is not executable: {implementation.inventory_state}"
        )

    if not authority.permits(implementation.implementation_id):
        reasons.append("implementation is outside the authorized set")

    missing_capabilities = sorted(
        requirements.required_capabilities - implementation.capabilities
    )
    if missing_capabilities:
        reasons.append(
            "missing required capabilities: " + ", ".join(missing_capabilities)
        )

    mandatory_checks = (
        ("reachable", requirements.require_reachable, evidence.reachable),
        ("healthy", requirements.require_healthy, evidence.healthy),
        (
            "privacy_allowed",
            requirements.require_privacy_allowed,
            evidence.privacy_allowed,
        ),
        (
            "runtime_constraints_satisfied",
            requirements.require_runtime_constraints,
            evidence.runtime_constraints_satisfied,
        ),
    )
    for name, required, value in mandatory_checks:
        if not required:
            continue
        if value is None:
            reasons.append(f"missing mandatory eligibility evidence: {name}")
        elif value is False:
            reasons.append(f"mandatory eligibility constraint failed: {name}")

    return tuple(reasons)


@dataclass(frozen=True, slots=True)
class EligibleImplementation:
    discovered: DiscoveredImplementation
    authority: AuthorityScope
    requirements: EligibilityRequirements
    evidence: EligibilityEvidence
    state: Literal["eligible"] = "eligible"

    def __post_init__(self) -> None:
        if not isinstance(self.discovered, DiscoveredImplementation):
            raise RuntimeBindingError(
                "eligible state requires a discovered implementation"
            )
        reasons = _eligibility_reasons(
            self.discovered,
            authority=self.authority,
            requirements=self.requirements,
            evidence=self.evidence,
        )
        if reasons:
            raise RuntimeBindingError(
                "eligible state cannot be constructed: " + "; ".join(reasons)
            )

    @property
    def implementation(self) -> RuntimeImplementation:
        return self.discovered.implementation


@dataclass(frozen=True, slots=True)
class EligibilityDecision:
    eligible: EligibleImplementation | None
    reasons: tuple[str, ...]

    @property
    def permitted(self) -> bool:
        return self.eligible is not None


@dataclass(frozen=True, slots=True)
class CalibrationRequirements:
    """Policy requirements for promoting one eligible configuration to calibrated."""

    required: bool = True
    max_age_seconds: int | None = None
    require_valid_until: bool = False

    def __post_init__(self) -> None:
        if self.max_age_seconds is not None:
            if isinstance(self.max_age_seconds, bool) or self.max_age_seconds <= 0:
                raise RuntimeBindingError(
                    "max_age_seconds must be a positive integer when provided"
                )


@dataclass(frozen=True, slots=True)
class CalibrationRecord:
    configuration_fingerprint: str
    status: CalibrationStatus
    evidence_ref: str
    calibrated_at: str | None = None
    valid_until: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.configuration_fingerprint, "configuration_fingerprint")
        _require_text(self.evidence_ref, "evidence_ref")
        if self.status not in {"passed", "not_required"}:
            raise RuntimeBindingError(
                f"unsupported calibration status: {self.status}"
            )
        calibrated_at = (
            _parse_instant(self.calibrated_at, "calibrated_at")
            if self.calibrated_at is not None
            else None
        )
        valid_until = (
            _parse_instant(self.valid_until, "valid_until")
            if self.valid_until is not None
            else None
        )
        if (
            calibrated_at is not None
            and valid_until is not None
            and valid_until <= calibrated_at
        ):
            raise RuntimeBindingError("valid_until must be later than calibrated_at")


def _calibration_reasons(
    eligible: EligibleImplementation,
    *,
    calibration: CalibrationRecord,
    requirements: CalibrationRequirements,
    evaluated_at: str,
) -> tuple[str, ...]:
    evaluated = _parse_instant(evaluated_at, "evaluated_at")
    expected = eligible.implementation.configuration.fingerprint
    reasons: list[str] = []

    if calibration.configuration_fingerprint != expected:
        reasons.append(
            "calibration fingerprint does not match the eligible execution configuration"
        )

    calibrated = (
        _parse_instant(calibration.calibrated_at, "calibrated_at")
        if calibration.calibrated_at is not None
        else None
    )
    expires = (
        _parse_instant(calibration.valid_until, "valid_until")
        if calibration.valid_until is not None
        else None
    )

    if requirements.require_valid_until and expires is None:
        reasons.append("calibration policy requires an explicit valid_until")

    if calibrated is not None and calibrated > evaluated:
        reasons.append("calibration evidence is dated after evaluated_at")

    if expires is not None and evaluated >= expires:
        reasons.append("calibration evidence is stale at evaluated_at")

    if calibration.status == "passed":
        if calibrated is None:
            reasons.append("passed calibration requires calibrated_at")
        elif (
            requirements.max_age_seconds is not None
            and evaluated
            >= calibrated + timedelta(seconds=requirements.max_age_seconds)
        ):
            reasons.append("calibration evidence exceeds the maximum allowed age")
    elif requirements.required:
        reasons.append("calibration is required by policy")

    return tuple(reasons)


@dataclass(frozen=True, slots=True)
class CalibratedImplementation:
    eligible: EligibleImplementation
    calibration: CalibrationRecord
    requirements: CalibrationRequirements
    evaluated_at: str
    state: Literal["calibrated"] = "calibrated"

    def __post_init__(self) -> None:
        if not isinstance(self.eligible, EligibleImplementation):
            raise RuntimeBindingError(
                "calibrated state requires an eligible implementation"
            )
        if not isinstance(self.calibration, CalibrationRecord):
            raise RuntimeBindingError("calibrated state requires a CalibrationRecord")
        if not isinstance(self.requirements, CalibrationRequirements):
            raise RuntimeBindingError(
                "calibrated state requires CalibrationRequirements"
            )
        reasons = _calibration_reasons(
            self.eligible,
            calibration=self.calibration,
            requirements=self.requirements,
            evaluated_at=self.evaluated_at,
        )
        if reasons:
            raise RuntimeBindingError(
                "calibrated state cannot be constructed: " + "; ".join(reasons)
            )

    @property
    def implementation(self) -> RuntimeImplementation:
        return self.eligible.implementation


@dataclass(frozen=True, slots=True)
class SelectedImplementation:
    calibrated: CalibratedImplementation
    fitness_score: float
    selection_reason: str
    evaluated_at: str
    state: Literal["selected"] = "selected"

    def __post_init__(self) -> None:
        if not isinstance(self.calibrated, CalibratedImplementation):
            raise RuntimeBindingError(
                "selected state requires a calibrated implementation"
            )
        if self.calibrated.implementation.inventory_state == "unavailable":
            raise RuntimeBindingError("unavailable implementation cannot be selected")
        if not isfinite(float(self.fitness_score)):
            raise RuntimeBindingError("selected fitness_score must be finite")
        _require_text(self.selection_reason, "selection_reason")
        freshness_reasons = _calibration_reasons(
            self.calibrated.eligible,
            calibration=self.calibrated.calibration,
            requirements=self.calibrated.requirements,
            evaluated_at=self.evaluated_at,
        )
        if freshness_reasons:
            raise RuntimeBindingError(
                "selected state cannot be constructed from stale or invalid calibration: "
                + "; ".join(freshness_reasons)
            )

    @property
    def implementation(self) -> RuntimeImplementation:
        return self.calibrated.implementation


def discover(implementation: RuntimeImplementation) -> DiscoveredImplementation:
    """Record inventory presence without creating eligibility or execution authority."""

    return DiscoveredImplementation(implementation=implementation)


def evaluate_eligibility(
    discovered: DiscoveredImplementation,
    *,
    authority: AuthorityScope,
    requirements: EligibilityRequirements,
    evidence: EligibilityEvidence,
) -> EligibilityDecision:
    if not isinstance(discovered, DiscoveredImplementation):
        raise RuntimeBindingError(
            "eligibility evaluation requires a discovered implementation"
        )
    reasons = _eligibility_reasons(
        discovered,
        authority=authority,
        requirements=requirements,
        evidence=evidence,
    )
    if reasons:
        return EligibilityDecision(eligible=None, reasons=reasons)
    return EligibilityDecision(
        eligible=EligibleImplementation(
            discovered=discovered,
            authority=authority,
            requirements=requirements,
            evidence=evidence,
        ),
        reasons=(),
    )


def apply_calibration(
    eligible: EligibleImplementation,
    calibration: CalibrationRecord,
    *,
    requirements: CalibrationRequirements,
    evaluated_at: str,
) -> CalibratedImplementation:
    """Promote only fresh, policy-satisfying calibration for the exact configuration."""

    if not isinstance(eligible, EligibleImplementation):
        raise RuntimeBindingError("calibration requires an eligible implementation")
    return CalibratedImplementation(
        eligible=eligible,
        calibration=calibration,
        requirements=requirements,
        evaluated_at=evaluated_at,
    )


def select_best(
    candidates: Sequence[CalibratedImplementation],
    *,
    fitness_scores: Mapping[str, float],
    selection_reason: str,
    evaluated_at: str,
) -> SelectedImplementation:
    """Select best fit only from candidates still calibration-valid at selection time."""

    _require_text(selection_reason, "selection_reason")
    _parse_instant(evaluated_at, "evaluated_at")
    if not candidates:
        raise RuntimeBindingError(
            "selection requires at least one calibrated candidate"
        )

    ranked: list[tuple[float, str, CalibratedImplementation]] = []
    for candidate in candidates:
        if not isinstance(candidate, CalibratedImplementation):
            raise RuntimeBindingError("selection requires calibrated candidates")
        implementation = candidate.implementation
        if implementation.inventory_state == "unavailable":
            raise RuntimeBindingError("unavailable implementation cannot be selected")
        freshness_reasons = _calibration_reasons(
            candidate.eligible,
            calibration=candidate.calibration,
            requirements=candidate.requirements,
            evaluated_at=evaluated_at,
        )
        if freshness_reasons:
            raise RuntimeBindingError(
                "calibrated candidate is not valid at selection time: "
                f"{implementation.implementation_id}: "
                + "; ".join(freshness_reasons)
            )
        implementation_id = implementation.implementation_id
        if implementation_id not in fitness_scores:
            raise RuntimeBindingError(
                f"missing fitness score for calibrated candidate: {implementation_id}"
            )
        score = float(fitness_scores[implementation_id])
        if not isfinite(score):
            raise RuntimeBindingError(
                f"fitness score must be finite: {implementation_id}"
            )
        ranked.append((score, implementation_id, candidate))

    score, _, selected = max(ranked, key=lambda item: (item[0], item[1]))
    return SelectedImplementation(
        calibrated=selected,
        fitness_score=score,
        selection_reason=selection_reason,
        evaluated_at=evaluated_at,
    )
