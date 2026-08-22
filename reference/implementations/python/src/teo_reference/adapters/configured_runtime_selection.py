from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from ..application.runtime_selection import RuntimeSelectionService
from ..domain.runtime_binding import (
    CalibrationRecord,
    EligibilityEvidence,
    ExecutionConfigurationIdentity,
    RuntimeImplementation,
)
from ..domain.runtime_selection import (
    RuntimeSelectionDecision,
    RuntimeSelectionPin,
    RuntimeSelectionRequest,
)
from .runtime_calibration import DeclaredRuntimeCalibrationAdapter
from .runtime_eligibility import DeclaredRuntimeEligibilityEvidenceAdapter
from .runtime_selection import PreferenceRuntimeFitnessAdapter


class ConfiguredRuntimeSelectionError(RuntimeError):
    """Raised when transitional configured runtime inventory cannot be composed."""


class _StaticInventory:
    def __init__(self, implementations: Sequence[RuntimeImplementation]) -> None:
        self._implementations = tuple(implementations)

    def discover(self) -> tuple[RuntimeImplementation, ...]:
        return self._implementations


class ConfiguredRuntimeSelectionAdapter:
    """Transitional RMI-5/RMI-7 bridge for the reference router.

    Legacy configured model names are converted into explicit *user-declared* runtime
    inventory and then passed through the normal RMI lifecycle. The adapter does not
    claim live discovery, reachability measurement, or empirical calibration. Its
    positive eligibility evidence and `not_required` calibration records are explicit
    compatibility assumptions preserving the pre-RMI reference router until RMI-7
    removes model identity from responsibility policy.

    Real installations can inject a different RuntimeSelectionPort with actual runtime
    inventory, health/privacy evidence, calibration history, and fitness observations.
    """

    def __init__(
        self,
        model_registry: Mapping[str, Mapping[str, Any]],
        *,
        pins: Sequence[RuntimeSelectionPin] = (),
    ) -> None:
        self._model_registry = dict(model_registry)
        self._pins = tuple(pins)

    def _entry(self, model: str) -> Mapping[str, Any]:
        direct = self._model_registry.get(model)
        if direct:
            return direct
        for entry in self._model_registry.values():
            if entry.get("concrete_model") == model or model in entry.get(
                "candidate_implementations", []
            ):
                return entry
        return {}

    @staticmethod
    def _implementation_id(model: str, effort: str | None) -> str:
        payload = json.dumps(
            {"model": model, "effort": effort or "provider-default"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        suffix = hashlib.sha256(payload).hexdigest()[:12]
        return f"configured:{model}:{suffix}"

    def select(self, request: RuntimeSelectionRequest) -> RuntimeSelectionDecision:
        models = tuple(sorted(request.authorized_models))
        if not models:
            raise ConfiguredRuntimeSelectionError(
                "configured compatibility selection requires explicit model authority"
            )

        implementations: list[RuntimeImplementation] = []
        evidence: dict[str, EligibilityEvidence] = {}
        calibration: list[CalibrationRecord] = []
        required_capabilities = request.eligibility_requirements.required_capabilities

        for model in models:
            entry = self._entry(model)
            if not entry:
                raise ConfiguredRuntimeSelectionError(
                    f"authorized configured model is absent from the model registry: {model}"
                )
            provider = entry.get("provider_family")
            availability = str(entry.get("availability") or "")
            effort = request.reasoning_effort_for(model)
            implementation_id = self._implementation_id(model, effort)
            configuration = ExecutionConfigurationIdentity.from_runtime(
                implementation_id=implementation_id,
                model=model,
                runtime="configured-compatibility",
                provider_family=str(provider) if provider else None,
                version=availability or None,
                tools=(),
                reasoning_controls={"effort": effort} if effort else {},
                material_settings={
                    "inventory_evidence": "legacy-configured-compatibility"
                },
            )
            implementation = RuntimeImplementation(
                configuration=configuration,
                inventory_state="user_declared",
                capabilities=frozenset(required_capabilities or {"general_reasoning"}),
            )
            implementations.append(implementation)
            evidence[implementation_id] = EligibilityEvidence(
                reachable=True,
                healthy=True,
                privacy_allowed=True,
                runtime_constraints_satisfied=True,
            )
            calibration.append(
                CalibrationRecord(
                    configuration_fingerprint=configuration.fingerprint,
                    status="not_required",
                    evidence_ref="policy://runtime-selection/configured-compatibility",
                )
            )

        service = RuntimeSelectionService(
            inventory=_StaticInventory(implementations),
            eligibility_evidence=DeclaredRuntimeEligibilityEvidenceAdapter(evidence),
            calibration_records=DeclaredRuntimeCalibrationAdapter(calibration),
            fitness=PreferenceRuntimeFitnessAdapter(),
            pins=self._pins,
        )
        return service.select(request)
