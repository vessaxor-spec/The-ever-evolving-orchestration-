from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "reference/datasets/user-research-worker-conformance.yaml"
PREVIEW_MODELS = ["gemini-3.1-pro-preview"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected a mapping in {path}"
    return data


def test_user_research_worker_binding_and_boundaries() -> None:
    fixture = load_yaml(DATASET)["binding"]
    bundle = ConfigBundle.load(REPO_ROOT)
    specialist = bundle.specialist_registry[fixture["specialist"]]
    worker = bundle.worker_registry[fixture["worker"]]
    runtime_defaults = bundle.worker_runtime_defaults[fixture["worker"]]

    assert specialist["worker_binding"] == fixture["worker"]
    assert specialist["primary_team"] == fixture["primary_team"]
    assert specialist["risk_profile"] == fixture["risk_profile"]
    assert specialist["role_card"] == fixture["role_card"]
    assert worker["owning_team"] == fixture["primary_team"]

    for field in (
        "mission",
        "responsibilities",
        "required_capabilities",
        "verification",
        "escalation",
        "authority_boundaries",
    ):
        assert worker.get(field), f"user_research is missing required worker field {field}"
    for field in ("preferred_implementations", "fallbacks"):
        assert runtime_defaults.get(field), f"user_research is missing runtime compatibility field {field}"

    for field, expected_values in fixture["contains"].items():
        actual_values = worker[field]
        assert isinstance(actual_values, list), f"Expected a list at user_research.{field}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"user_research no longer contains {expected_value!r} in {field}"
            )


def test_user_research_dispatch_is_medium_risk_and_provider_diverse() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "conformance-user-research",
                "task": "Synthesize customer feedback and interview transcripts into user pain points using the feedback synthesizer.",
                "risk_level": "low",
                "specialist": "feedback-synthesizer",
                "constraints": {"accepted_preview_models": PREVIEW_MODELS},
            }
        )
    )

    assert dispatch.task_type == "user_research"
    assert dispatch.risk_level == "medium"
    assert dispatch.selected_team == "research"
    assert dispatch.selected_worker == "user_research"
    assert dispatch.selected_specialist == "feedback-synthesizer"
    assert dispatch.specialist_risk_profile == "medium"
    assert dispatch.selected_implementation.model == "claude-sonnet-5"
    assert dispatch.selected_implementation.provider_family == "anthropic"
    assert dispatch.selected_implementation.source == "runtime_compatibility.task_routes.user_research.primary"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "gemini-3.1-pro-preview"
    assert dispatch.fallback_implementation.provider_family == "google"
    assert dispatch.verification.implementation.model == "gpt-5.6-sol"
    assert dispatch.verification.implementation.provider_family == "openai"
    assert dispatch.verification.independent is True
    assert dispatch.verification.human_approval_required is False
    assert dispatch.warnings == []
    assert dispatch.selected_implementation.provider_family != dispatch.fallback_implementation.provider_family
    assert dispatch.selected_implementation.provider_family != dispatch.verification.implementation.provider_family

    for capability in (
        "qualitative_research",
        "thematic_analysis",
        "evidence_synthesis",
        "interview_transcript_analysis",
        "survey_analysis",
        "usability_research",
        "mixed_methods_reasoning",
        "source_validation",
        "uncertainty_calibration",
        "privacy_and_research_ethics",
        "user_insight_translation",
    ):
        assert capability in dispatch.required_capabilities

    for method in ("output_validation", "targeted_review"):
        assert method in dispatch.verification.method


def test_user_research_classification_precedes_broad_research_and_stays_separate() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    bundle = engine.config

    user_research = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Create an affinity map from the interview transcripts and synthesize the feedback.",
            }
        )
    )
    analytics = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Analyze the survey dataset for statistical significance and confidence intervals.",
            }
        )
    )
    market = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Conduct market research on competitor positioning and market sizing.",
            }
        )
    )
    broad = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare primary sources about the history of public libraries.",
            }
        )
    )

    assert user_research.task_type == "user_research"
    assert user_research.selected_worker == "user_research"
    assert analytics.task_type == "analytics"
    assert analytics.selected_worker == "analytics"
    assert market.task_type == "market_research"
    assert market.selected_worker == "market_research"
    assert broad.task_type == "deep_research"
    assert broad.selected_worker == "research"

    assert bundle.team_routes["user_research"]["primary_worker"] == "user_research"
    assert bundle.team_routes["analytics"]["primary_worker"] == "analytics"
    assert bundle.team_routes["market_research"]["primary_worker"] == "market_research"
    assert bundle.team_routes["deep_research"]["primary_worker"] == "research"
    assert bundle.team_routes["documentation"]["primary_worker"] == "documentation"

    boundaries = bundle.worker_registry["user_research"]["authority_boundaries"]
    assert "no_product_decision_substitution" in boundaries
    assert "no_market_research_ownership" in boundaries
    assert "no_analytics_infrastructure_ownership" in boundaries
    assert "no_ux_design_or_accessibility_verdict_substitution" in boundaries
    assert "no_live_human_interview_execution" in boundaries


def test_user_research_route_keeps_opus_conditional() -> None:
    route = ConfigBundle.load(REPO_ROOT).runtime_task_routes["user_research"]

    assert route["primary"]["model"] == "claude-sonnet-5"
    assert route["fallback"]["model"] == "gemini-3.1-pro-preview"
    assert route["verifier"]["model"] == "gpt-5.6-sol"
    assert route["conditional_escalation"]["model"] == "claude-opus-5"
    assert "escalation" not in route
