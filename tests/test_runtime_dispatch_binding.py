from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from teo_reference.adapters.configured_runtime_selection import (
    ConfiguredRuntimeSelectionAdapter,
)
from teo_reference.config import ConfigBundle
from teo_reference.domain.runtime_binding import CalibrationRequirements
from teo_reference.domain.runtime_selection import RuntimeSelectionPin
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIEW_ACCEPTANCE = {"accepted_preview_models": ["gemini-3.1-pro-preview"]}


class RecordingSelector:
    def __init__(self, delegate) -> None:
        self.delegate = delegate
        self.requests = []
        self.decisions = []

    def select(self, request):
        self.requests.append(request)
        decision = self.delegate.select(request)
        self.decisions.append(decision)
        return decision


class PreferModelSelector(RecordingSelector):
    def __init__(self, delegate, model: str) -> None:
        super().__init__(delegate)
        self.model = model

    def select(self, request):
        preferred = list(request.preferred_models)
        if self.model in preferred:
            preferred.remove(self.model)
            preferred.insert(0, self.model)
            request = replace(request, preferred_models=tuple(preferred))
        return super().select(request)


def _task(**overrides):
    payload = {
        "task": "Implement a bounded backend endpoint with tests.",
        "task_type": "daily_coding",
        "risk_level": "low",
        "constraints": PREVIEW_ACCEPTANCE,
    }
    payload.update(overrides)
    return TaskRequest.from_dict(payload)


def test_dispatch_uses_injected_runtime_selector_instead_of_static_first_match() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = PreferModelSelector(
        ConfiguredRuntimeSelectionAdapter(bundle.model_registry),
        "gemini-3.7-flash",
    )
    engine = OrchestrationEngine(bundle, runtime_selector=selector)

    dispatch = engine.dispatch(_task())

    assert dispatch.selected_implementation.model == "gemini-3.7-flash"
    assert dispatch.selected_implementation.model != "gpt-5.6-terra"
    assert selector.requests[0].scope.role == "primary"
    assert selector.decisions[0].selected.implementation.inventory_state == "user_declared"


def test_blocked_provider_remains_deny_wins_even_when_injected_selector_prefers_it() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = PreferModelSelector(
        ConfiguredRuntimeSelectionAdapter(bundle.model_registry),
        "gemini-3.7-flash",
    )
    engine = OrchestrationEngine(bundle, runtime_selector=selector)

    dispatch = engine.dispatch(
        _task(
            constraints={
                "accepted_preview_models": ["gemini-3.1-pro-preview"],
                "blocked_providers": ["google"],
            }
        )
    )

    assert dispatch.selected_implementation.provider_family != "google"
    assert dispatch.selected_implementation.model == "gpt-5.6-terra"


def test_fallback_and_verifier_are_reselected_through_runtime_lifecycle() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = RecordingSelector(ConfiguredRuntimeSelectionAdapter(bundle.model_registry))
    engine = OrchestrationEngine(bundle, runtime_selector=selector)

    dispatch = engine.dispatch(_task())

    roles = [request.scope.role for request in selector.requests]
    assert roles == ["primary", "fallback", "verifier"]
    assert dispatch.fallback_implementation is not None
    assert (
        dispatch.fallback_implementation.provider_family
        != dispatch.selected_implementation.provider_family
    )
    assert (
        dispatch.verification.implementation.provider_family
        != dispatch.selected_implementation.provider_family
    )


def test_dispatch_does_not_call_legacy_direct_resolvers() -> None:
    class GuardedEngine(OrchestrationEngine):
        def _resolve_primary(self, *args, **kwargs):  # pragma: no cover - must not run
            raise AssertionError("legacy primary resolver was called")

        def _resolve_fallback(self, *args, **kwargs):  # pragma: no cover - must not run
            raise AssertionError("legacy fallback resolver was called")

    dispatch = GuardedEngine(ConfigBundle.load(REPO_ROOT)).dispatch(_task())
    assert dispatch.selected_implementation.model == "gpt-5.6-terra"


def test_scoped_pin_can_change_dispatch_only_within_runtime_authority() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    target_id = ConfiguredRuntimeSelectionAdapter._implementation_id(
        "gemini-3.7-flash", "medium"
    )
    pin = RuntimeSelectionPin(
        pin_id="daily-coding-incident-pin",
        implementation_id=target_id,
        role="primary",
        reason="controlled incident mitigation",
        task_type="daily_coding",
        removal_conditions=frozenset({"incident-cleared"}),
    )
    selector = ConfiguredRuntimeSelectionAdapter(bundle.model_registry, pins=(pin,))

    dispatch = OrchestrationEngine(bundle, runtime_selector=selector).dispatch(_task())

    assert dispatch.selected_implementation.model == "gemini-3.7-flash"


def test_compatibility_selector_fails_closed_when_empirical_calibration_is_required() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    engine = OrchestrationEngine(
        bundle,
        runtime_calibration_requirements=CalibrationRequirements(required=True),
    )

    with pytest.raises(RoutingError, match="calibration is required by policy"):
        engine.dispatch(_task())


def test_specialist_preferences_do_not_overwrite_injected_runtime_selection() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = PreferModelSelector(
        ConfiguredRuntimeSelectionAdapter(bundle.model_registry),
        "gemini-3.7-flash",
    )
    engine = SpecialistRoutingEngine(bundle, runtime_selector=selector)

    dispatch = engine.dispatch(
        _task(specialist="backend-engineer")
    )

    assert dispatch.selected_specialist == "backend-engineer"
    assert dispatch.selected_implementation.model == "gemini-3.7-flash"
    assert dispatch.verification.implementation.provider_family != "google"


def test_specialist_reasoning_is_bound_before_calibration_and_preserved_in_dispatch() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = RecordingSelector(ConfiguredRuntimeSelectionAdapter(bundle.model_registry))
    engine = SpecialistRoutingEngine(bundle, runtime_selector=selector)

    dispatch = engine.dispatch(_task(specialist="backend-engineer"))

    primary_request = selector.requests[0]
    primary_decision = selector.decisions[0]
    assert primary_request.reasoning_effort_for("gpt-5.6-terra") == "medium"
    assert dict(
        primary_decision.selected.implementation.configuration.reasoning_controls
    )["effort"] == "medium"
    assert dispatch.selected_implementation.reasoning == "medium"


def test_configured_bridge_is_explicitly_user_declared_and_not_empirical_calibration() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = RecordingSelector(ConfiguredRuntimeSelectionAdapter(bundle.model_registry))
    engine = OrchestrationEngine(bundle, runtime_selector=selector)

    engine.dispatch(_task())
    selected = selector.decisions[0].selected

    assert selected.implementation.inventory_state == "user_declared"
    assert selected.calibrated.calibration.status == "not_required"
    assert (
        selected.calibrated.calibration.evidence_ref
        == "policy://runtime-selection/configured-compatibility"
    )


def test_runtime_binding_explanation_replaces_static_first_match_claim() -> None:
    dispatch = OrchestrationEngine(ConfigBundle.load(REPO_ROOT)).dispatch(_task())
    joined = " ".join(dispatch.routing_explanation)
    assert "Runtime binding selected" in joined
    assert "selected from the daily_coding implementation route" not in joined
