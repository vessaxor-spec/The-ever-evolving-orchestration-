from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from teo_reference.audit import append_jsonl
from teo_reference.config import ConfigBundle, ConfigurationError
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.schemas import ExecutionResult, TaskRequest, VerificationResult


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def build_repo(root: Path) -> Path:
    write_yaml(
        root / "policy/routing/team-routing.yaml",
        {
            "team_routes": {
                "daily_coding": {
                    "primary_team": "engineering",
                    "primary_worker": "backend",
                    "worker_override_by_context": {"frontend": "frontend"},
                    "verification_team": "verification",
                },
                "security_review": {
                    "primary_team": "review",
                    "primary_worker": "security",
                    "verification_team": "verification",
                },
                "architecture_design": {
                    "primary_team": "planning",
                    "primary_worker": "architecture",
                    "verification_team": "verification",
                },
            }
        },
    )
    write_yaml(
        root / "policy/routing/routing.yaml",
        {
            "routing": {
                "daily_coding": {
                    "primary": {"agent": "codex", "model": "gpt-terra", "profile": "terra"},
                    "planning_support": {"agent": "codex", "model": "gpt-sol", "profile": "sol"},
                    "fallback": {"agent": "agy", "model": "gemini-pro", "profile": "sol"},
                    "semantic_reviewer": {
                        "agent": "claude",
                        "model": "claude-sonnet",
                        "profile": "sol",
                    },
                },
                "security_review": {
                    "primary": {"agent": "claude", "model": "claude-opus", "profile": "sol"},
                    "executable_verifier": {
                        "agent": "codex",
                        "model": "gpt-terra",
                        "profile": "terra",
                    },
                },
                "architecture_design": {
                    "primary": {"agent": "claude", "model": "claude-sonnet", "profile": "sol"},
                    "verifier": {"agent": "codex", "model": "gpt-sol", "profile": "sol"},
                },
            },
            "fallback_order": {
                "coding": [
                    {"agent": "codex", "model": "gpt-terra"},
                    {"agent": "agy", "model": "gemini-pro"},
                    {"agent": "claude", "model": "claude-sonnet"},
                ],
                "engineering_reasoning": [
                    {"agent": "codex", "model": "gpt-sol"},
                    {"agent": "claude", "model": "claude-sonnet"},
                ],
                "general_reasoning": [
                    {"agent": "claude", "model": "claude-sonnet"},
                    {"agent": "codex", "model": "gpt-sol"},
                ],
            },
            "verification_policy": {
                "low": {"minimum": ["output_validation"]},
                "medium": {"minimum": ["output_validation", "targeted_review"]},
                "high": {"minimum": ["independent_verifier", "evidence_or_test_results"]},
                "critical": {
                    "minimum": ["independent_multi_agent_review", "human_approval", "audit_trace"]
                },
            },
        },
    )
    write_yaml(
        root / "community/workers/workers.yaml",
        {
            "workers": {
                "backend": {
                    "owning_team": "engineering",
                    "required_capabilities": ["coding", "debugging", "tool_execution"],
                    "preferred_implementations": ["gpt-terra", "gpt-sol"],
                    "fallbacks": ["gemini-pro", "claude-sonnet"],
                },
                "frontend": {
                    "owning_team": "engineering",
                    "required_capabilities": ["coding", "visual_reasoning"],
                    "preferred_implementations": ["gpt-terra"],
                    "fallbacks": ["gemini-pro", "claude-sonnet"],
                },
                "security": {
                    "owning_team": "review",
                    "required_capabilities": ["high_reasoning", "adversarial_review"],
                    "preferred_implementations": ["claude-opus", "gpt-sol"],
                    "fallbacks": ["claude-sonnet", "gpt-terra"],
                },
                "architecture": {
                    "owning_team": "planning",
                    "required_capabilities": ["high_reasoning", "planning"],
                    "preferred_implementations": ["claude-sonnet", "gpt-sol"],
                    "fallbacks": ["claude-opus", "gemini-pro"],
                },
            }
        },
    )
    write_yaml(
        root / "community/specialists/specialists.yaml",
        {
            "specialists": {
                "backend-engineer": {
                    "primary_team": "engineering",
                    "worker_binding": "backend",
                    "risk_profile": "medium",
                    "role_card": "community/specialists/backend-engineer.md",
                },
                "security-engineer": {
                    "primary_team": "review",
                    "worker_binding": "security",
                    "risk_profile": "critical",
                    "role_card": "community/specialists/security-engineer.md",
                },
            }
        },
    )
    write_yaml(
        root / "registry/capabilities/capabilities.yaml",
        {
            "capabilities": {
                "configuration_validation": {
                    "definition": "validate linked configuration",
                    "typical_teams": ["engineering"],
                    "evidence": ["configuration_check"],
                }
            }
        },
    )
    write_yaml(
        root / "models.yaml",
        {
            "models": {
                "terra": {
                    "provider_family": "openai",
                    "concrete_model": "gpt-terra",
                    "availability": "current",
                    "profile": "terra",
                },
                "sol": {
                    "provider_family": "openai",
                    "concrete_model": "gpt-sol",
                    "availability": "current",
                    "profile": "sol",
                },
                "gemini": {
                    "provider_family": "google",
                    "concrete_model": "gemini-pro",
                    "availability": "preview",
                    "profile": "sol",
                },
                "sonnet": {
                    "provider_family": "anthropic",
                    "concrete_model": "claude-sonnet",
                    "availability": "ga",
                    "profile": "sol",
                },
                "opus": {
                    "provider_family": "anthropic",
                    "concrete_model": "claude-opus",
                    "availability": "ga",
                    "profile": "sol",
                },
            }
        },
    )
    return root


def engine(tmp_path: Path) -> OrchestrationEngine:
    return OrchestrationEngine(ConfigBundle.load(build_repo(tmp_path)))


def test_config_loading_fails_closed_on_unreachable_specialist_binding(tmp_path: Path) -> None:
    root = build_repo(tmp_path)
    specialist_path = root / "community/specialists/specialists.yaml"
    payload = yaml.safe_load(specialist_path.read_text(encoding="utf-8"))
    payload["specialists"]["unresolved-role"] = {
        "primary_team": "planning",
        "worker_binding": "missing_worker",
        "risk_profile": "medium",
        "role_card": "community/specialists/unresolved-role.md",
    }
    write_yaml(specialist_path, payload)

    with pytest.raises(ConfigurationError, match="missing_worker"):
        ConfigBundle.load(root)


def test_dispatch_resolves_complete_route(tmp_path: Path) -> None:
    router = engine(tmp_path)
    dispatch = router.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "demo",
                "task": "Implement the backend API with tests using the backend engineer.",
                "task_type": "daily_coding",
                "risk_level": "medium",
                "domain": "backend",
                "specialist": "backend-engineer",
                "constraints": {
                    "required_capabilities": ["configuration_validation"],
                    "accepted_preview_models": ["gemini-pro"],
                },
            }
        )
    )
    assert dispatch.selected_team == "engineering"
    assert dispatch.selected_worker == "backend"
    assert dispatch.selected_specialist == "backend-engineer"
    assert dispatch.selected_implementation.model == "gpt-terra"
    assert dispatch.fallback_implementation is not None
    assert dispatch.fallback_implementation.model == "gemini-pro"
    assert dispatch.verification.implementation.model == "claude-sonnet"
    assert dispatch.verification.independent is True
    assert "configuration_validation" in dispatch.required_capabilities


def test_blocked_implementations_apply_fallback(tmp_path: Path) -> None:
    router = engine(tmp_path)
    dispatch = router.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Implement a backend endpoint.",
                "task_type": "daily_coding",
                "constraints": {
                    "blocked_implementations": ["gpt-terra", "gpt-sol"],
                    "accepted_preview_models": ["gemini-pro"],
                },
            }
        )
    )
    assert dispatch.selected_implementation.model == "gemini-pro"
    assert dispatch.verification.implementation.model == "claude-sonnet"


def test_specialist_binding_mismatch_fails_closed(tmp_path: Path) -> None:
    router = engine(tmp_path)
    task = TaskRequest.from_dict(
        {
            "task": "Implement a backend endpoint.",
            "task_type": "daily_coding",
            "specialist": "security-engineer",
        }
    )
    with pytest.raises(RoutingError, match="does not match"):
        router.dispatch(task)


def test_critical_specialist_requires_human_approval(tmp_path: Path) -> None:
    router = engine(tmp_path)
    dispatch = router.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Review authentication and authorization controls.",
                "task_type": "security_review",
                "risk_level": "low",
                "specialist": "security-engineer",
            }
        )
    )
    assert dispatch.specialist_risk_profile == "critical"
    assert dispatch.risk_level == "critical"
    assert dispatch.verification.human_approval_required is True
    assert "human_approval" in dispatch.verification.method


def test_finalize_records_evidence_and_audit(tmp_path: Path) -> None:
    router = engine(tmp_path)
    dispatch = router.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Design the service architecture.",
                "task_type": "architecture_design",
                "risk_level": "high",
            }
        )
    )
    execution = ExecutionResult(
        dispatch_id=dispatch.dispatch_id,
        status="succeeded",
        output_ref="artifact://architecture",
        evidence=["architecture document produced"],
    )
    verification = VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model=dispatch.verification.implementation.model,
        checks=dispatch.verification.method,
        evidence=["implementation feasibility reviewed"],
    )
    outcome = router.finalize(dispatch, execution, verification)
    assert outcome.status == "completed"
    assert outcome.selected_model != outcome.verifier_model
    assert len(outcome.evidence) == 2

    audit = tmp_path / "audit.jsonl"
    append_jsonl(audit, "dispatch", dispatch.to_dict())
    append_jsonl(audit, "final_outcome", outcome.to_dict())
    records = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines()]
    assert [record["record_type"] for record in records] == ["dispatch", "final_outcome"]
