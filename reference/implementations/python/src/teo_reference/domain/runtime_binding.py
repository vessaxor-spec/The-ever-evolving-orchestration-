from __future__ import annotations

import hashlib
import json
from math import isfinite
from dataclasses import dataclass, field
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


@dataclass(frozen=True, slots=True)
class EligibleImplementation:
    discovered: DiscoveredImplementation
    evidence: EligibilityEvidence
    state: Literal["eligible"] = "eligible"

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


@dataclass(frozen=True, slots=True)
class CalibratedImplementation:
    eligible: EligibleImplementation
    calibration: CalibrationRecord
    state: Literal["calibrated"] = "calibrated"

    @property
    def implementation(self) -> RuntimeImplementation:
        return self.eligible.implementation


@dataclass(frozen=True, slots=True)
class SelectedImplementation:
    calibrated: CalibratedImplementation
    fitness_score: float
    selection_reason: str
    state: Literal["selected"] = "selected"

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

    if reasons:
        return EligibilityDecision(eligible=None, reasons=tuple(reasons))
    return EligibilityDecision(
        eligible=EligibleImplementation(discovered=discovered, evidence=evidence),
        reasons=(),
    )


def apply_calibration(
    eligible: EligibleImplementation,
    calibration: CalibrationRecord,
) -> CalibratedImplementation:
    """Advance only exact execution configurations through the calibration stage."""

    if not isinstance(eligible, EligibleImplementation):
        raise RuntimeBindingError("calibration requires an eligible implementation")
    expected = eligible.implementation.configuration.fingerprint
    if calibration.configuration_fingerprint != expected:
        raise RuntimeBindingError(
            "calibration fingerprint does not match the eligible execution configuration"
        )
    return CalibratedImplementation(eligible=eligible, calibration=calibration)


def select_best(
    candidates: Sequence[CalibratedImplementation],
    *,
    fitness_scores: Mapping[str, float],
    selection_reason: str,
) -> SelectedImplementation:
    """Select the best fit without creating authority or bypassing lifecycle stages."""

    _require_text(selection_reason, "selection_reason")
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
    )
