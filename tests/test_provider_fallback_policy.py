from __future__ import annotations

from pathlib import Path
from typing import Any

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]

PRIMARY_KEYS = {
    "orchestration": "primary",
    "operations": "primary",
    "project_delivery": "primary",
    "incident_response": "primary",
    "market_research": "primary",
    "analytics": "primary",
    "architecture_design": "primary",
    "daily_coding": "primary",
    "deep_debugging": "primary",
    "repo_wide_refactor": "executor",
    "deep_research": "primary",
    "code_review": "executable_review",
    "security_review": "primary",
    "multimodal_analysis": "primary",
    "high_volume_simple": "primary",
    "documentation": "primary",
}


def model_entry(bundle: ConfigBundle, model: str) -> dict[str, Any]:
    direct = bundle.model_registry.get(model)
    if direct:
        return direct
    for entry in bundle.model_registry.values():
        if entry.get("concrete_model") == model or model in entry.get("candidate_implementations", []):
            return entry
    raise AssertionError(f"Model {model!r} has no canonical provider metadata")


def provider(bundle: ConfigBundle, model: str) -> str:
    value = model_entry(bundle, model).get("provider_family")
    assert value, f"Model {model!r} has no provider family"
    return str(value)


def test_active_routes_have_cross_provider_non_local_fallbacks() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    for route_name, primary_key in PRIMARY_KEYS.items():
        route = bundle.implementation_routes[route_name]
        primary = route[primary_key]
        fallback = route.get("fallback")

        assert isinstance(fallback, dict) and fallback.get("model"), (
            f"{route_name} must declare an explicit routine fallback"
        )
        primary_provider = provider(bundle, str(primary["model"]))
        fallback_provider = provider(bundle, str(fallback["model"]))

        assert fallback_provider != primary_provider, (
            f"{route_name} repeats provider {primary_provider} across primary and fallback"
        )
        assert not fallback_provider.startswith("local"), (
            f"{route_name} uses a local automatic fallback"
        )


def test_worker_and_family_fallbacks_are_canonical_non_local_and_exclude_opus() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    for worker_name, worker in bundle.worker_registry.items():
        for field in ("preferred_implementations", "fallbacks"):
            for model in worker.get(field, []):
                provider(bundle, str(model))
        for model in worker.get("fallbacks", []):
            assert model != "claude-opus-5", f"{worker_name} uses Opus as a routine fallback"
            assert not provider(bundle, str(model)).startswith("local"), (
                f"{worker_name} uses a local automatic fallback"
            )

    for family, candidates in bundle.routing.get("fallback_order", {}).items():
        seen: set[str] = set()
        for candidate in candidates:
            candidate_provider = provider(bundle, str(candidate["model"]))
            assert not candidate_provider.startswith("local"), (
                f"fallback_order.{family} contains a local model"
            )
            assert candidate_provider not in seen, (
                f"fallback_order.{family} repeats provider {candidate_provider}"
            )
            seen.add(candidate_provider)
            assert candidate["model"] != "claude-opus-5", (
                f"fallback_order.{family} uses Opus as routine fallback"
            )


def test_escalation_is_not_loaded_as_automatic_fallback() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    opus_locations: list[str] = []

    for route_name, route in bundle.implementation_routes.items():
        assert "escalation" not in route, f"{route_name} exposes escalation to automatic fallback"
        primary_key = PRIMARY_KEYS.get(route_name)
        if primary_key and route[primary_key].get("model") == "claude-opus-5":
            opus_locations.append(f"{route_name}.{primary_key}")
        conditional = route.get("conditional_escalation")
        if conditional and conditional.get("model") == "claude-opus-5":
            opus_locations.append(f"{route_name}.conditional_escalation")
        fallback = route.get("fallback")
        if fallback:
            assert fallback.get("model") != "claude-opus-5", (
                f"{route_name} uses Opus as a routine fallback"
            )

    assert "security_review.primary" in opus_locations
    assert all(
        location == "security_review.primary" or location.endswith(".conditional_escalation")
        for location in opus_locations
    )


def test_provider_scoped_blocking_moves_dispatch_across_provider_boundary() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))

    research = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Investigate and compare primary sources using the researcher.",
                "task_type": "deep_research",
                "specialist": "researcher",
                "constraints": {"blocked_providers": ["google"]},
            }
        )
    )
    assert research.selected_implementation.provider_family == "anthropic"
    assert research.fallback_implementation is not None
    assert research.fallback_implementation.provider_family == "openai"

    security = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Review authentication and authorization controls.",
                "task_type": "security_review",
                "specialist": "security-engineer",
                "constraints": {"blocked_providers": ["anthropic"]},
            }
        )
    )
    assert security.selected_implementation.provider_family == "openai"
    assert security.fallback_implementation is not None
    assert security.fallback_implementation.provider_family == "google"


def test_policy_distinguishes_model_and_provider_scoped_failures() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    defaults = bundle.routing["defaults"]

    assert defaults["automatic_local_models_allowed"] is False
    assert defaults["prefer_cross_provider_fallbacks"] is True
    assert defaults["fallback_reselection_requires_new_verifier"] is True
    assert "model_specific_failure" in defaults["same_provider_fallback_allowed_when"]
    assert "provider_rate_limit" in defaults["provider_scoped_failure_signals"]
    assert "provider_quota_exhausted" in defaults["provider_scoped_failure_signals"]
    assert "provider_authentication_failure" in defaults["provider_scoped_failure_signals"]
    assert "provider_service_outage" in defaults["provider_scoped_failure_signals"]
