from __future__ import annotations

from pathlib import Path

import yaml

from teo_reference.config import ConfigBundle
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/routing/specialist-model-routing.yaml"


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def test_specialist_model_policy_covers_all_78_active_specialists_exactly_once() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    assert len(bundle.specialist_registry) == 78
    assert len(policy["specialists"]) == 78
    assert set(policy["specialists"]) == set(bundle.specialist_registry)


def test_every_template_has_cross_provider_fallback_and_third_provider_verifier() -> None:
    router = engine()
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    for name, template in policy["templates"].items():
        models = [template[key]["model"] for key in ("primary", "fallback", "verifier")]
        providers = [router._provider_for_model(model) for model in models]
        assert len(set(models)) == 3, name
        assert len(set(providers)) == 3, name


def test_security_specialist_uses_opus_xhigh_with_sol_fallback_and_gemini_verifier() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Review authentication and authorization controls with the security engineer.",
                "task_type": "security_review",
                "risk_level": "low",
                "specialist": "security-engineer",
            }
        )
    )
    assert dispatch.risk_level == "critical"
    assert dispatch.selected_implementation.model == "claude-opus-5"
    assert dispatch.selected_implementation.reasoning == "xhigh"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "gpt-5.6-sol"
    assert dispatch.fallback_implementation.reasoning == "xhigh"
    assert dispatch.verification.implementation.model == "gemini-3.1-pro-preview"
    assert dispatch.verification.implementation.reasoning == "high"
    assert dispatch.verification.human_approval_required is True
    assert len(
        {
            dispatch.selected_implementation.provider_family,
            dispatch.fallback_implementation.provider_family,
            dispatch.verification.implementation.provider_family,
        }
    ) == 3


def test_backend_specialist_uses_terra_medium_with_flash_fallback_and_sonnet_verifier() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Implement a bounded backend endpoint with tests using the backend engineer.",
                "task_type": "daily_coding",
                "risk_level": "low",
                "specialist": "backend-engineer",
            }
        )
    )
    assert dispatch.risk_level == "medium"
    assert dispatch.selected_implementation.model == "gpt-5.6-terra"
    assert dispatch.selected_implementation.reasoning == "medium"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "gemini-3.6-flash"
    assert dispatch.fallback_implementation.reasoning == "medium"
    assert dispatch.verification.implementation.model == "claude-sonnet-5"
    assert dispatch.verification.implementation.reasoning == "medium"


def test_research_specialist_uses_gemini_pro_with_sonnet_fallback_and_sol_verifier() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research current evidence and compare primary sources using the researcher.",
                "task_type": "deep_research",
                "risk_level": "medium",
                "specialist": "researcher",
            }
        )
    )
    assert dispatch.selected_implementation.model == "gemini-3.1-pro-preview"
    assert dispatch.selected_implementation.reasoning == "high"
    assert dispatch.selected_implementation.availability == "preview"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "claude-sonnet-5"
    assert dispatch.verification.implementation.model == "gpt-5.6-sol"
    assert dispatch.verification.implementation.reasoning == "high"


def test_blocked_specialist_primary_can_promote_cross_provider_fallback() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Review authentication and authorization controls with the security engineer.",
                "task_type": "security_review",
                "specialist": "security-engineer",
                "constraints": {"blocked_providers": ["anthropic"]},
            }
        )
    )
    assert dispatch.selected_implementation.model == "gpt-5.6-sol"
    assert dispatch.selected_implementation.provider_family == "openai"
    assert dispatch.verification.implementation.provider_family != "openai"
    assert dispatch.verification.human_approval_required is True


def test_non_specialist_route_preserves_existing_model_and_exposes_existing_reasoning() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Implement a small endpoint.",
                "task_type": "daily_coding",
                "risk_level": "low",
            }
        )
    )
    assert dispatch.selected_specialist is None
    assert dispatch.selected_implementation.model == "gpt-5.6-terra"
    assert dispatch.selected_implementation.reasoning == "medium"


def test_specialist_model_refinement_never_changes_team_worker_or_specialist_source() -> None:
    router = engine()
    task = TaskRequest.from_dict(
        {
            "task": "Implement a bounded backend endpoint with tests using the backend engineer.",
            "task_type": "daily_coding",
            "risk_level": "medium",
            "specialist": "backend-engineer",
        }
    )
    base = router.__class__.__mro__[1].dispatch(router, task)
    refined = router.dispatch(task)
    assert refined.selected_team == base.selected_team
    assert refined.selected_worker == base.selected_worker
    assert refined.selected_specialist == base.selected_specialist
    assert refined.specialist_source == base.specialist_source
    assert refined.specialist_risk_profile == base.specialist_risk_profile
