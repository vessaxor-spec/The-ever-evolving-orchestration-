from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "policy" / "routing" / "principal-engineering-expansion.yaml"

EXPECTED_NEW_TEAMS = {
    "platform_reliability",
    "systems_engineering",
    "physical_systems",
    "assurance",
}

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

EXPECTED_REALLOCATIONS = {
    "devops-engineer": ("engineering", "platform_reliability"),
    "devsecops-engineer": ("engineering", "platform_reliability"),
    "embedded-engineer": ("engineering", "physical_systems"),
    "civil-engineer": ("planning", "physical_systems"),
}


def load_registry() -> dict:
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_expansion_scope_is_complete_and_staged() -> None:
    registry = load_registry()

    assert registry["status"] == "approved-foundation"
    assert registry["activation"] == "staged"
    assert registry["current_team_count"] == 6
    assert registry["target_team_count"] == 10
    assert registry["current_specialist_count"] == 56
    assert registry["target_specialist_count"] == 78

    assert set(registry["new_teams"]) == EXPECTED_NEW_TEAMS
    assert all(
        team["activation_ready"] is False
        for team in registry["new_teams"].values()
    )

    specialist_ids = {
        specialist["id"] for specialist in registry["new_specialists"]
    }
    assert specialist_ids == EXPECTED_NEW_SPECIALISTS
    assert len(registry["new_specialists"]) == 22


def test_every_new_team_has_a_charter_and_worker_family() -> None:
    registry = load_registry()

    for team_name, team in registry["new_teams"].items():
        charter = REPO_ROOT / team["charter"]
        assert charter.is_file(), f"Missing charter for {team_name}: {charter}"
        assert team["worker_families"], f"No worker families for {team_name}"


def test_existing_specialist_moves_are_allocation_only() -> None:
    registry = load_registry()
    reallocations = registry["existing_specialist_reallocations"]

    assert set(reallocations) == set(EXPECTED_REALLOCATIONS)
    for specialist, (source_team, target_team) in EXPECTED_REALLOCATIONS.items():
        move = reallocations[specialist]
        assert move["from"] == source_team
        assert move["to"] == target_team
        assert move["preserve_role_card"] is True

    rust_binding = registry["existing_binding_corrections"]["rust-engineer"]
    assert rust_binding == {
        "from": "systems_engineering",
        "to": "rust_systems_programming",
        "preserve_role_card": True,
    }


def test_activation_requires_conformance_and_independence() -> None:
    registry = load_registry()
    gates = set(registry["activation_gates"])
    rules = set(registry["routing_rules"])

    assert "worker_definition_exists" in gates
    assert "specialist_card_exists" in gates
    assert "routing_policy_exists" in gates
    assert "provider_diverse_fallback_exists" in gates
    assert "independent_verification_defined" in gates
    assert "conformance_dataset_exists" in gates
    assert "critical_risk_has_qualified_human_approval" in gates
    assert "canonical_preservation_test_present" in gates

    assert "new_teams_are_not_active_until_all_activation_gates_pass" in rules
    assert "assurance_produces_claims_and_evidence_requirements_but_does_not_self_verify" in rules
    assert "evidence_pilot_scope_remains_exactly_six_until_its_maintainability_gate_passes" in rules
