from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFORMANCE_PATH = (
    REPO_ROOT / "reference" / "datasets" / "principal-engineering-routing-conformance.yaml"
)
ACTIVATION_PATH = REPO_ROOT / "policy" / "routing" / "activation" / "principal-engineering.yaml"
WARNING_BASELINE_PATH = (
    REPO_ROOT / "reference" / "datasets" / "configuration-warning-baseline.yaml"
)
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"
PREVIEW_MODELS = ["gemini-3.1-pro"]

EXPECTED_NEW_SPECIALISTS = {
    "cloud-architect",
    "mobile-engineer",
    "compiler-toolchain-engineer",
    "distributed-systems-engineer",
    "database-reliability-engineer",
    "network-engineer",
    "platform-engineer",
    "performance-engineer",
    "finops-engineer",
    "site-reliability-engineer",
    "mlops-engineer",
    "systems-requirements-engineer",
    "hardware-engineer",
    "robotics-autonomous-systems-engineer",
    "silicon-asic-engineer",
    "aerospace-satellite-engineer",
    "manufacturing-engineer",
    "applied-scientist",
    "privacy-engineer",
    "functional-safety-engineer",
    "formal-methods-engineer",
    "application-security-engineer",
}

EXPECTED_CORRECTIONS = {
    "devops-engineer": ("platform_reliability", "devops"),
    "devsecops-engineer": ("platform_reliability", "devsecops"),
    "embedded-engineer": ("physical_systems", "embedded"),
    "civil-engineer": ("physical_systems", "civil_engineering"),
    "rust-engineer": ("engineering", "rust_systems_programming"),
}

EXPECTED_PILOT = {
    "legal-operations",
    "tax-strategist",
    "loan-officer-assistant",
    "compliance-auditor",
    "civil-engineer",
    "embedded-engineer",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def model_entry(bundle: ConfigBundle, model: str) -> dict[str, Any]:
    direct = bundle.model_registry.get(model)
    if direct:
        return direct
    for entry in bundle.model_registry.values():
        if entry.get("concrete_model") == model or model in entry.get(
            "candidate_implementations", []
        ):
            return entry
    raise AssertionError(f"Model {model!r} has no canonical provider metadata")


def provider(bundle: ConfigBundle, model: str) -> str:
    value = model_entry(bundle, model).get("provider_family")
    assert value, f"Model {model!r} has no provider family"
    return str(value)


def conformance_cases() -> list[dict[str, Any]]:
    cases = load_yaml(CONFORMANCE_PATH).get("cases")
    assert isinstance(cases, list)
    return cases


def test_principal_activation_preserves_its_original_seventy_eight_specialist_boundary() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    activation = load_yaml(ACTIVATION_PATH)

    assert activation["status"] == "active"
    assert activation["scope"] == {
        "team_count": 10,
        "specialist_count": 78,
        "new_team_count": 4,
        "new_specialist_count": 22,
        "explicit_route_count": 27,
    }
    assert len(bundle.specialist_registry) >= 78
    assert EXPECTED_NEW_SPECIALISTS.issubset(bundle.specialist_registry)
    assert set(activation["activated_specialists"]) == EXPECTED_NEW_SPECIALISTS
    assert set(activation["activated_new_teams"]) == {
        "platform_reliability",
        "systems_engineering",
        "physical_systems",
        "assurance",
    }


def test_all_new_specialist_cards_are_linked_without_role_card_override() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    for specialist_id in EXPECTED_NEW_SPECIALISTS:
        entry = bundle.specialist_registry[specialist_id]
        role_card = REPO_ROOT / str(entry["role_card"])
        assert role_card.is_file(), f"Missing role card for {specialist_id}"
        assert role_card.name == f"{specialist_id}.md"
        text = role_card.read_text(encoding="utf-8")
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "must remain intact" in text


def test_approved_existing_allocations_are_corrected_only_in_loaded_registry() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    activation = load_yaml(ACTIVATION_PATH)

    for specialist_id, (team, worker) in EXPECTED_CORRECTIONS.items():
        entry = bundle.specialist_registry[specialist_id]
        assert entry["primary_team"] == team
        assert entry["worker_binding"] == worker
        assert activation["allocation_corrections"][specialist_id] == {
            "primary_team": team,
            "worker_binding": worker,
        }
        role_card = REPO_ROOT / str(entry["role_card"])
        assert role_card.is_file()


def test_every_principal_route_has_registered_team_worker_and_implementation() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    cases = conformance_cases()

    assert len(cases) == 27
    assert len({case["task_type"] for case in cases}) == 27

    for case in cases:
        task_type = str(case["task_type"])
        route = bundle.team_routes[task_type]
        worker_name = str(route["primary_worker"])
        team_name = str(route["primary_team"])

        assert team_name == case["expected_team"]
        assert worker_name == case["expected_worker"]
        assert worker_name in bundle.worker_registry
        assert bundle.worker_registry[worker_name]["owning_team"] == team_name
        assert task_type in bundle.implementation_routes


def test_conformance_dispatches_risk_provider_and_verification() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    engine = OrchestrationEngine(bundle)

    for case in conformance_cases():
        dispatch = engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task": case["task"],
                    "task_type": case["task_type"],
                    "risk_level": "low",
                    "specialist": case["specialist"],
                    "constraints": {"accepted_preview_models": PREVIEW_MODELS},
                }
            )
        )

        assert dispatch.selected_team == case["expected_team"]
        assert dispatch.selected_worker == case["expected_worker"]
        assert dispatch.selected_specialist == case["specialist"]
        assert dispatch.risk_level == case["expected_risk"]
        assert dispatch.warnings == []

        assert dispatch.selected_implementation.provider_family == case["primary_provider"]
        assert dispatch.fallback_implementation is not None
        assert dispatch.fallback_implementation.provider_family == case["fallback_provider"]
        assert dispatch.verification.implementation.provider_family == case["verifier_provider"]

        providers = {
            dispatch.selected_implementation.provider_family,
            dispatch.fallback_implementation.provider_family,
            dispatch.verification.implementation.provider_family,
        }
        assert len(providers) == 3
        assert all(not str(value).startswith("local") for value in providers)
        assert dispatch.verification.implementation.model != dispatch.selected_implementation.model
        assert dispatch.verification.independent is True
        assert dispatch.verification.human_approval_required is (
            case["expected_risk"] == "critical"
        )


def test_principal_routes_use_cross_provider_routine_fallbacks() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    for case in conformance_cases():
        route = bundle.implementation_routes[str(case["task_type"])]
        primary_model = str(route["primary"]["model"])
        fallback_model = str(route["fallback"]["model"])
        verifier_model = str(route["verifier"]["model"])

        primary_provider = provider(bundle, primary_model)
        fallback_provider = provider(bundle, fallback_model)
        verifier_provider = provider(bundle, verifier_model)

        assert primary_provider == case["primary_provider"]
        assert fallback_provider == case["fallback_provider"]
        assert verifier_provider == case["verifier_provider"]
        assert len({primary_provider, fallback_provider, verifier_provider}) == 3
        assert fallback_model != "claude-opus-5"
        assert not fallback_provider.startswith("local")


def test_generic_coding_routes_no_longer_cross_team_into_devops() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    engine = OrchestrationEngine(bundle)

    daily = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Implement a bounded deployment-related code change.",
                "task_type": "daily_coding",
                "domain": "deployment",
                "risk_level": "low",
            }
        )
    )
    assert daily.selected_team == "engineering"
    assert daily.selected_worker == "backend"
    assert daily.warnings == []

    debugging = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Debug an infrastructure-related application failure.",
                "task_type": "deep_debugging",
                "domain": "infrastructure",
                "risk_level": "low",
            }
        )
    )
    assert debugging.selected_team == "engineering"
    assert debugging.selected_worker == "backend"
    assert debugging.warnings == []


def test_principal_specialists_require_explicit_task_type() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))

    with pytest.raises(RoutingError, match="ambiguous"):
        engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task": "Evaluate leader election quorum behavior under a network partition.",
                    "risk_level": "low",
                }
            )
        )


def test_configuration_warning_baseline_is_exact() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    expected = load_yaml(WARNING_BASELINE_PATH)["expected_issues"]
    assert bundle.validate() == expected


def test_activation_loader_rejects_protected_specialist_field_override(
    tmp_path: Path,
) -> None:
    from teo_reference.config import ConfigurationError, _load_specialists

    canonical = tmp_path / "canonical.yaml"
    extension = tmp_path / "extension.yaml"
    canonical.write_text(
        "specialists:\n  specialist-a:\n    primary_team: engineering\n    worker_binding: backend\n    role_card: role.md\n",
        encoding="utf-8",
    )
    extension.write_text(
        "specialists: {}\nallocation_overrides:\n  specialist-a:\n    role_card: replaced.md\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="protected fields"):
        _load_specialists(canonical, (extension,))


def test_regulated_evidence_pilot_remains_exactly_six() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)
    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT
    assert len(pilot["pilot_specialists"]) == 6

    activation = load_yaml(ACTIVATION_PATH)
    assert activation["regulated_evidence_pilot"] == {
        "scope_count": 6,
        "expansion_authorized": False,
        "maintainability_gate_still_required": True,
    }


def test_activation_artifacts_do_not_use_em_dashes() -> None:
    artifacts = [
        REPO_ROOT / "community" / "specialists" / "principal-engineering-active.yaml",
        REPO_ROOT / "community" / "workers" / "extensions" / "principal-engineering-active-workers.yaml",
        REPO_ROOT / "policy" / "routing" / "extensions" / "principal-engineering-team-routing.yaml",
        REPO_ROOT / "policy" / "routing" / "extensions" / "principal-engineering-routing.yaml",
        ACTIVATION_PATH,
        CONFORMANCE_PATH,
        REPO_ROOT / "docs" / "history" / "activation" / "principal-engineering-activation-2026-08-06.md",
    ]
    for path in artifacts:
        assert path.is_file()
        assert "—" not in path.read_text(encoding="utf-8"), f"Em dash found in {path}"
