from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPANSION_PATH = REPO_ROOT / "policy" / "routing" / "principal-engineering-expansion.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"

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


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw)


def test_all_twenty_two_approved_specialist_cards_exist() -> None:
    expansion = load_yaml(EXPANSION_PATH)
    records = {item["id"]: item for item in expansion["new_specialists"]}

    assert expansion["target_specialist_count"] == 78
    assert set(records) == EXPECTED_NEW_SPECIALISTS
    assert len(records) == 22

    for specialist_id in EXPECTED_NEW_SPECIALISTS:
        path = REPO_ROOT / "community" / "specialists" / f"{specialist_id}.md"
        assert path.is_file(), f"Missing approved specialist card: {specialist_id}"

        metadata = frontmatter(path)
        text = path.read_text(encoding="utf-8")

        assert metadata["name"] == specialist_id
        assert metadata["freshness_policy"] == "live-verification-required"
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "must remain intact" in text
        assert "—" not in text


def test_approved_specialists_remain_staged_until_routing_completion() -> None:
    active = load_yaml(ACTIVE_SPECIALISTS_PATH)["specialists"]

    assert EXPECTED_NEW_SPECIALISTS.isdisjoint(active)

    expansion = load_yaml(EXPANSION_PATH)
    assert expansion["activation"] == "staged"
    assert all(
        team["activation_ready"] is False
        for team in expansion["new_teams"].values()
    )


def test_expansion_keeps_preservation_and_human_gates() -> None:
    expansion = load_yaml(EXPANSION_PATH)
    gates = set(expansion["activation_gates"])
    rules = set(expansion["routing_rules"])

    assert "canonical_preservation_test_present" in gates
    assert "independent_verification_defined" in gates
    assert "critical_risk_has_qualified_human_approval" in gates
    assert "conformance_dataset_exists" in gates
    assert "provider_diverse_fallback_exists" in gates

    assert "specialist_allocation_is_additive_and_must_not_reduce_existing_capability" in rules
    assert "new_teams_are_not_active_until_all_activation_gates_pass" in rules
    assert "evidence_pilot_scope_remains_exactly_six_until_its_maintainability_gate_passes" in rules
