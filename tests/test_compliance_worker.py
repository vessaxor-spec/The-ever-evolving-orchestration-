from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "reference/datasets/compliance-worker-conformance.yaml"
PREVIEW_MODELS = ["gemini-3.1-pro-preview"]


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected a mapping in {path}"
    return data


def test_compliance_worker_binding_and_boundaries() -> None:
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
        assert worker.get(field), f"compliance is missing required worker field {field}"
    for field in ("preferred_implementations", "fallbacks"):
        assert runtime_defaults.get(field), f"compliance is missing runtime compatibility field {field}"

    for field, expected_values in fixture["contains"].items():
        actual_values = worker[field]
        assert isinstance(actual_values, list), f"Expected a list at compliance.{field}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"compliance no longer contains {expected_value!r} in {field}"
            )


def test_compliance_dispatch_is_critical_provider_diverse_and_human_gated() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "conformance-compliance",
                "task": "Run a SOC 2 compliance audit and control mapping using the compliance auditor.",
                "risk_level": "low",
                "specialist": "compliance-auditor",
                "constraints": {"accepted_preview_models": PREVIEW_MODELS},
            }
        )
    )

    assert dispatch.task_type == "compliance_review"
    assert dispatch.risk_level == "critical"
    assert dispatch.selected_team == "review"
    assert dispatch.selected_worker == "compliance"
    assert dispatch.selected_specialist == "compliance-auditor"
    assert dispatch.specialist_risk_profile == "critical"
    assert dispatch.selected_implementation.model == "claude-sonnet-5"
    assert dispatch.selected_implementation.provider_family == "anthropic"
    assert dispatch.selected_implementation.source == "runtime_compatibility.task_routes.compliance_review.primary"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "gpt-5.6-sol"
    assert dispatch.fallback_implementation.provider_family == "openai"
    assert dispatch.verification.implementation.model == "gemini-3.1-pro-preview"
    assert dispatch.verification.implementation.provider_family == "google"
    assert dispatch.verification.independent is True
    assert dispatch.verification.human_approval_required is True
    assert dispatch.warnings == []
    assert dispatch.selected_implementation.provider_family != dispatch.fallback_implementation.provider_family
    assert dispatch.selected_implementation.provider_family != dispatch.verification.implementation.provider_family

    for capability in (
        "compliance_reasoning",
        "regulatory_applicability_analysis",
        "control_mapping",
        "evidence_assessment",
        "audit_methodology",
        "privacy_and_data_governance",
        "ai_governance",
        "third_party_risk_analysis",
        "risk_classification",
        "source_validation",
        "traceable_writing",
    ):
        assert capability in dispatch.required_capabilities

    for method in (
        "independent_multi_agent_review",
        "executable_verification",
        "human_approval",
        "audit_trace",
        "rollback_plan",
    ):
        assert method in dispatch.verification.method


def test_compliance_classification_precedes_security_and_documentation() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))

    compliance = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Generate a privacy policy based on our data flow and perform a GDPR compliance review.",
            }
        )
    )
    security = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Perform a security review of authentication and authorization vulnerabilities.",
            }
        )
    )
    documentation = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Write documentation for the public API.",
            }
        )
    )
    research = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare primary sources on the history of privacy regulation.",
            }
        )
    )

    assert compliance.task_type == "compliance_review"
    assert compliance.selected_worker == "compliance"
    assert security.task_type == "security_review"
    assert security.selected_worker == "security"
    assert documentation.task_type == "documentation"
    assert documentation.selected_worker == "documentation"
    assert research.task_type == "deep_research"
    assert research.selected_worker == "research"


def test_compliance_remains_separate_from_legal_security_and_implementation() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    assert bundle.team_routes["compliance_review"]["primary_worker"] == "compliance"
    assert bundle.team_routes["security_review"]["primary_worker"] == "security"
    assert bundle.worker_registry["compliance"]["owning_team"] == "review"
    assert bundle.worker_registry["security"]["owning_team"] == "review"

    boundaries = bundle.worker_registry["compliance"]["authority_boundaries"]
    assert "no_legal_opinion_or_regulator_representation" in boundaries
    assert "no_certification_or_audit_opinion_issuance" in boundaries
    assert "no_technical_control_implementation" in boundaries
    assert "no_self_approval_or_self_verification" in boundaries
    assert "no_regulated_or_high_consequence_decision_without_qualified_human_owner" in boundaries


def test_compliance_route_keeps_opus_conditional() -> None:
    route = ConfigBundle.load(REPO_ROOT).runtime_task_routes["compliance_review"]

    assert route["primary"]["model"] == "claude-sonnet-5"
    assert route["fallback"]["model"] == "gpt-5.6-sol"
    assert route["verifier"]["model"] == "gemini-3.1-pro-preview"
    assert route["conditional_escalation"]["model"] == "claude-opus-5"
    assert "escalation" not in route
