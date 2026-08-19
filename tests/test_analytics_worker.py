from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "reference/datasets/analytics-worker-conformance.yaml"
PREVIEW_MODELS = ["gemini-3.1-pro"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected a mapping in {path}"
    return data


def test_analytics_worker_binding_and_boundaries() -> None:
    fixture = load_yaml(DATASET)["binding"]
    bundle = ConfigBundle.load(REPO_ROOT)
    specialist = bundle.specialist_registry[fixture["specialist"]]
    worker = bundle.worker_registry[fixture["worker"]]

    assert specialist["worker_binding"] == fixture["worker"]
    assert specialist["primary_team"] == fixture["primary_team"]
    assert specialist["risk_profile"] == fixture["risk_profile"]
    assert specialist["role_card"] == fixture["role_card"]
    assert worker["owning_team"] == fixture["primary_team"]

    for field in (
        "mission",
        "responsibilities",
        "required_capabilities",
        "preferred_implementations",
        "fallbacks",
        "verification",
        "escalation",
        "authority_boundaries",
    ):
        assert worker.get(field), f"analytics is missing required worker field {field}"

    for field, expected_values in fixture["contains"].items():
        actual_values = worker[field]
        assert isinstance(actual_values, list), f"Expected a list at analytics.{field}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"analytics no longer contains {expected_value!r} in {field}"
            )


def test_analytics_dispatch_is_high_risk_and_provider_diverse() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "conformance-analytics",
                "task": "Analyze the dataset and design an A/B test using the data analyst.",
                "risk_level": "low",
                "specialist": "data-analyst",
                "constraints": {"accepted_preview_models": PREVIEW_MODELS},
            }
        )
    )

    assert dispatch.task_type == "analytics"
    assert dispatch.risk_level == "high"
    assert dispatch.selected_team == "research"
    assert dispatch.selected_worker == "analytics"
    assert dispatch.selected_specialist == "data-analyst"
    assert dispatch.specialist_risk_profile == "high"
    assert dispatch.selected_implementation.model == "gpt-5.6-sol"
    assert dispatch.selected_implementation.provider_family == "openai"
    assert dispatch.selected_implementation.source == "routing.analytics.primary"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "gemini-3.1-pro"
    assert dispatch.fallback_implementation.provider_family == "google"
    assert dispatch.verification.implementation.model == "claude-sonnet-5"
    assert dispatch.verification.implementation.provider_family == "anthropic"
    assert dispatch.verification.independent is True
    assert dispatch.verification.human_approval_required is False
    assert dispatch.warnings == []
    assert dispatch.selected_implementation.provider_family != dispatch.fallback_implementation.provider_family
    assert dispatch.selected_implementation.provider_family != dispatch.verification.implementation.provider_family

    for capability in (
        "quantitative_reasoning",
        "statistical_analysis",
        "sql_analysis",
        "experiment_design",
        "data_quality_assessment",
        "causal_reasoning",
        "model_validation",
        "reproducible_analysis",
    ):
        assert capability in dispatch.required_capabilities

    for method in (
        "independent_verifier",
        "explicit_reasoning_summary",
        "evidence_or_test_results",
        "rollback_or_recovery_plan",
    ):
        assert method in dispatch.verification.method


def test_analytics_remains_separate_from_research_and_data_engineering() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    assert bundle.team_routes["analytics"]["primary_worker"] == "analytics"
    assert bundle.team_routes["deep_research"]["primary_worker"] == "research"
    assert bundle.team_routes["daily_coding"]["worker_override_by_context"]["data_pipeline"] == "data_engineering"
    assert bundle.worker_registry["analytics"]["owning_team"] == "research"
    assert bundle.worker_registry["data_engineering"]["owning_team"] == "engineering"
    assert "no_data_pipeline_ownership" in bundle.worker_registry["analytics"]["authority_boundaries"]
    assert "no_business_strategy_decision_substitution" in bundle.worker_registry["analytics"]["authority_boundaries"]


def test_analytics_route_keeps_opus_conditional() -> None:
    route = ConfigBundle.load(REPO_ROOT).implementation_routes["analytics"]

    assert route["primary"]["model"] == "gpt-5.6-sol"
    assert route["fallback"]["model"] == "gemini-3.1-pro"
    assert route["verifier"]["model"] == "claude-sonnet-5"
    assert route["conditional_escalation"]["model"] == "claude-opus-5"
    assert "escalation" not in route
