from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from teo_reference.config import ConfigBundle
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVATION_PATH = REPO_ROOT / "policy" / "routing" / "activation" / "workforce-expansion.yaml"
ALLOCATION_PATH = REPO_ROOT / "community" / "specialists" / "workforce-expansion-active.yaml"
CONFORMANCE_PATH = REPO_ROOT / "reference" / "datasets" / "workforce-expansion-routing-conformance.yaml"
PREVIEW_ACCEPTANCE = {"accepted_preview_models": ["gemini-3.1-pro-preview"]}

EXPECTED_SPECIALISTS = {
    "fraud-forensic-investigation-specialist": ("research", "osint"),
    "talent-acquisition-specialist": ("mission_control", "operations"),
    "insurance-claims-specialist": ("mission_control", "operations"),
    "orchestration-evaluation-analyst": ("research", "analytics"),
}

EXPECTED_MODELS = {
    "fraud-forensic-investigation-specialist": ("claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview"),
    "talent-acquisition-specialist": ("claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview"),
    "insurance-claims-specialist": ("claude-opus-5", "gpt-5.6-sol", "gemini-3.1-pro-preview"),
    "orchestration-evaluation-analyst": ("gpt-5.6-sol", "claude-sonnet-5", "gemini-3.1-pro-preview"),
}

CRITICAL_CONSEQUENCE_CASES = {
    "fraud-forensic-investigation-specialist": {
        "task_type": "specialist_research",
        "domain": "osint",
        "task": "Use the investigation to accuse the named provider of fraud and prepare a regulatory referral.",
    },
    "talent-acquisition-specialist": {
        "task_type": "specialist_mission_control",
        "domain": "operations",
        "task": "Review the candidate evidence and make the final hiring decision.",
    },
    "insurance-claims-specialist": {
        "task_type": "specialist_mission_control",
        "domain": "operations",
        "task": "Review the claim file and make the coverage decision, including whether to deny claim payment.",
    },
    "orchestration-evaluation-analyst": {
        "task_type": "specialist_research",
        "domain": "analytics",
        "task": "Use the evaluation to modify live routing policy and apply route recommendation automatically.",
    },
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def conformance_cases() -> list[dict[str, Any]]:
    cases = load_yaml(CONFORMANCE_PATH).get("cases")
    assert isinstance(cases, list)
    return cases


def test_workforce_expansion_activates_exactly_four_additive_specialists() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    activation = load_yaml(ACTIVATION_PATH)
    allocations = load_yaml(ALLOCATION_PATH)

    assert activation["status"] == "active"
    assert activation["scope"] == {
        "prior_specialist_count": 78,
        "specialist_count": 82,
        "new_specialist_count": 4,
        "new_team_count": 0,
        "new_worker_count": 0,
        "new_generic_route_count": 0,
    }
    assert len(bundle.specialist_registry) == 82
    assert set(allocations["specialists"]) == set(EXPECTED_SPECIALISTS)
    assert set(activation["activated_specialists"]) == set(EXPECTED_SPECIALISTS)
    assert bundle.validate() == []


def test_workforce_expansion_reuses_existing_team_worker_spawn_paths() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    for specialist_id, (team, worker) in EXPECTED_SPECIALISTS.items():
        entry = bundle.specialist_registry[specialist_id]
        assert entry["primary_team"] == team
        assert entry["worker_binding"] == worker
        assert worker in bundle.worker_registry
        assert bundle.worker_registry[worker]["owning_team"] == team
        assert any(
            route["primary_team"] == team
            and (
                route["primary_worker"] == worker
                or worker in route.get("worker_override_by_context", {}).values()
            )
            for route in bundle.team_routes.values()
        )


def test_workforce_expansion_role_cards_preserve_authority_boundaries() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    required_phrases = {
        "fraud-forensic-investigation-specialist": [
            "does not establish fraud",
            "qualified-human approval",
            "must remain intact",
        ],
        "talent-acquisition-specialist": [
            "Final shortlist, rejection, offer, compensation, and hiring authority remains with qualified humans",
            "qualified-human approval",
            "must remain intact",
        ],
        "insurance-claims-specialist": [
            "Binding coverage, liability, denial, payment, settlement, medical, legal, and SIU decisions remain outside this specialist's authority",
            "qualified-human approval",
            "must remain intact",
        ],
        "orchestration-evaluation-analyst": [
            "I evaluate evidence about routing. I do not control live routing.",
            "Recommendations remain shadow recommendations until separately reviewed",
            "must remain intact",
        ],
    }

    for specialist_id, phrases in required_phrases.items():
        entry = bundle.specialist_registry[specialist_id]
        role_card = REPO_ROOT / str(entry["role_card"])
        assert role_card.is_file()
        text = role_card.read_text(encoding="utf-8")
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "—" not in text
        for phrase in phrases:
            assert phrase in text


def test_workforce_expansion_conformance_routes_risk_and_provider_diversity() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    engine = SpecialistRoutingEngine(bundle)
    cases = conformance_cases()

    assert len(cases) == 4
    assert {case["specialist"] for case in cases} == set(EXPECTED_SPECIALISTS)

    for case in cases:
        dispatch = engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task": case["task"],
                    "task_type": case["task_type"],
                    "domain": case["domain"],
                    "risk_level": "low",
                    "specialist": case["specialist"],
                    "constraints": PREVIEW_ACCEPTANCE,
                }
            )
        )

        assert dispatch.selected_team == case["expected_team"]
        assert dispatch.selected_worker == case["expected_worker"]
        assert dispatch.selected_specialist == case["specialist"]
        assert dispatch.risk_level == case["expected_risk"]
        assert dispatch.selected_implementation.provider_family == case["primary_provider"]
        assert dispatch.fallback_implementation is not None
        assert dispatch.fallback_implementation.provider_family == case["fallback_provider"]
        assert dispatch.verification.implementation.provider_family == case["verifier_provider"]
        assert len(
            {
                dispatch.selected_implementation.provider_family,
                dispatch.fallback_implementation.provider_family,
                dispatch.verification.implementation.provider_family,
            }
        ) == 3
        assert dispatch.verification.independent is True
        assert dispatch.verification.human_approval_required is False


def test_workforce_specialist_critical_request_preserves_human_approval() -> None:
    engine = SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))

    for case in conformance_cases():
        specialist = case["specialist"]
        expected_primary, expected_fallback, expected_verifier = EXPECTED_MODELS[specialist]
        dispatch = engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task": case["task"],
                    "task_type": case["task_type"],
                    "domain": case["domain"],
                    "risk_level": "critical",
                    "specialist": specialist,
                    "constraints": PREVIEW_ACCEPTANCE,
                }
            )
        )
        assert dispatch.risk_level == "critical"
        assert dispatch.verification.human_approval_required is True
        assert dispatch.selected_implementation.model == expected_primary
        assert dispatch.fallback_implementation is not None
        assert dispatch.fallback_implementation.model == expected_fallback
        assert dispatch.verification.implementation.model == expected_verifier


def test_workforce_consequence_rules_automatically_raise_critical_risk() -> None:
    engine = SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))

    for specialist, case in CRITICAL_CONSEQUENCE_CASES.items():
        expected_primary, expected_fallback, expected_verifier = EXPECTED_MODELS[specialist]
        dispatch = engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task": case["task"],
                    "task_type": case["task_type"],
                    "domain": case["domain"],
                    "risk_level": "low",
                    "specialist": specialist,
                    "constraints": PREVIEW_ACCEPTANCE,
                }
            )
        )
        assert dispatch.risk_level == "critical"
        assert dispatch.verification.human_approval_required is True
        assert dispatch.selected_implementation.model == expected_primary
        assert dispatch.selected_implementation.reasoning == "xhigh"
        assert dispatch.fallback_implementation is not None
        assert dispatch.fallback_implementation.model == expected_fallback
        assert dispatch.verification.implementation.model == expected_verifier
        assert any(
            "consequence rule elevated effective risk to critical" in explanation
            for explanation in dispatch.routing_explanation
        )


def test_orchestration_evaluator_remains_shadow_only() -> None:
    text = (REPO_ROOT / "community" / "specialists" / "orchestration-evaluation-analyst.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "I evaluate evidence about routing. I do not control live routing.",
        "Does not select or modify the live route for an active task",
        "Does not write routing, worker, specialist, risk, verification, capability, model, or runtime policy",
        "Recommendations remain shadow recommendations until separately reviewed",
        "The analyst may explain evidence relevant to such a decision. It may not execute or self-approve the decision.",
    ):
        assert phrase in text


def test_workforce_expansion_does_not_expand_regulated_evidence_pilot() -> None:
    activation = load_yaml(ACTIVATION_PATH)
    pilot = load_yaml(REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml")

    assert len(pilot["pilot_specialists"]) == 6
    assert activation["regulated_evidence_pilot"] == {
        "scope_count": 6,
        "expansion_authorized": False,
        "workforce_expansion_does_not_change_pilot_scope": True,
    }
