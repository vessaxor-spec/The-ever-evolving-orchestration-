from __future__ import annotations

from pathlib import Path

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.schemas import RISK_ORDER, TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
TEAM_TASK_TYPES = {
    "mission_control": "specialist_mission_control",
    "planning": "specialist_planning",
    "engineering": "specialist_engineering",
    "platform_reliability": "specialist_platform_reliability",
    "systems_engineering": "specialist_systems_engineering",
    "physical_systems": "specialist_physical_systems",
    "research": "specialist_research",
    "assurance": "specialist_assurance",
    "review": "specialist_review",
    "verification": "specialist_verification",
}


def bundle() -> ConfigBundle:
    return ConfigBundle.load(REPO_ROOT)


def specialist_ids() -> list[str]:
    return sorted(bundle().specialist_registry)


def test_active_registry_contains_exactly_82_spawnable_specialists() -> None:
    config = bundle()
    assert len(config.specialist_registry) == 82
    assert set(entry["primary_team"] for entry in config.specialist_registry.values()) == set(TEAM_TASK_TYPES)
    assert config.validate() == []


@pytest.mark.parametrize("specialist_id", specialist_ids())
def test_every_active_specialist_has_complete_authority_preserving_spawn_path(
    specialist_id: str,
) -> None:
    config = bundle()
    entry = config.specialist_registry[specialist_id]
    team = str(entry["primary_team"])
    worker = str(entry["worker_binding"])
    task_type = TEAM_TASK_TYPES[team]
    runtime = SpecialistRoutingEngine(config)

    dispatch = runtime.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": f"spawn-{specialist_id}",
                "task": f"Execute bounded work using the preserved {specialist_id} specialist role.",
                "task_type": task_type,
                "risk_level": "low",
                "domain": worker,
                "specialist": specialist_id,
                "constraints": {
                    "accepted_preview_models": ["gemini-3.1-pro-preview"],
                },
            }
        )
    )

    assert dispatch.selected_team == team
    assert dispatch.selected_worker == worker
    assert dispatch.selected_specialist == specialist_id
    assert dispatch.specialist_source == entry["role_card"]
    assert dispatch.specialist_risk_profile == entry["risk_profile"]
    assert RISK_ORDER[dispatch.risk_level] >= RISK_ORDER[str(entry["risk_profile"])]
    assert dispatch.selected_implementation.provider_family
    assert dispatch.fallback_implementation is not None
    assert dispatch.verification.implementation.provider_family
    assert len(
        {
            dispatch.selected_implementation.provider_family,
            dispatch.fallback_implementation.provider_family,
            dispatch.verification.implementation.provider_family,
        }
    ) == 3
    assert dispatch.verification.independent is True
    assert dispatch.verification.human_approval_required is (
        dispatch.risk_level == "critical"
    )


def test_regulated_pilot_specialists_are_spawnable_through_real_workers() -> None:
    config = bundle()
    for specialist_id in (
        "legal-operations",
        "tax-strategist",
        "loan-officer-assistant",
        "compliance-auditor",
        "civil-engineer",
        "embedded-engineer",
    ):
        entry = config.specialist_registry[specialist_id]
        assert entry["worker_binding"] in config.worker_registry
        assert (
            entry["primary_team"],
            entry["worker_binding"],
        ) in {
            (route["primary_team"], route["primary_worker"])
            for route in config.team_routes.values()
        } or any(
            route["primary_team"] == entry["primary_team"]
            and entry["worker_binding"] in route.get("worker_override_by_context", {}).values()
            for route in config.team_routes.values()
        )
