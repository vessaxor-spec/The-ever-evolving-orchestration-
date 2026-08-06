from hashlib import sha1
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = REPO_ROOT / "policy" / "routing" / "physical-systems-staging.yaml"
EXPANSION_PATH = REPO_ROOT / "policy" / "routing" / "principal-engineering-expansion.yaml"
ACTIVE_ROUTING_PATH = REPO_ROOT / "policy" / "routing" / "team-routing.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"

EXPECTED_SPECIALISTS = {
    "hardware-engineer": ("hardware_engineering", "critical"),
    "robotics-autonomous-systems-engineer": ("robotics_autonomy", "critical"),
    "silicon-asic-engineer": ("silicon_engineering", "critical"),
    "aerospace-satellite-engineer": ("aerospace_systems", "critical"),
    "manufacturing-engineer": ("manufacturing_engineering", "high"),
}

EXPECTED_WORKERS = {
    "hardware_engineering",
    "robotics_autonomy",
    "silicon_engineering",
    "aerospace_systems",
    "manufacturing_engineering",
}

EXPECTED_PILOT = {
    "legal-operations",
    "tax-strategist",
    "loan-officer-assistant",
    "compliance-auditor",
    "civil-engineer",
    "embedded-engineer",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw)


def test_exact_physical_systems_scope_is_staged() -> None:
    staging = load_yaml(STAGING_PATH)

    assert staging["status"] == "staged"
    assert staging["team"] == "physical_systems"
    assert staging["activation_ready"] is False
    assert set(staging["specialists"]) == set(EXPECTED_SPECIALISTS)
    assert set(staging["worker_contract"]["expected_workers"]) == EXPECTED_WORKERS

    assert set(staging["pending_gates"]) == {
        "routing_policy_exists",
        "capability_mapping_exists",
        "provider_diverse_fallback_exists",
        "conformance_dataset_exists",
        "existing_specialist_reallocations_applied",
    }


def test_specialist_cards_are_full_preserved_allocations() -> None:
    staging = load_yaml(STAGING_PATH)

    for specialist_id, (worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = staging["specialists"][specialist_id]
        path = REPO_ROOT / record["card_path"]
        metadata = frontmatter(path)
        text = path.read_text(encoding="utf-8")

        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert metadata["name"] == specialist_id
        assert metadata["category"] == "physical-systems"
        assert metadata["freshness_policy"] == "live-verification-required"
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile
        assert f"`{worker_binding}`" in text
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "must remain intact" in text
        assert "self-approval" in text or "self-approve" in text


def test_worker_contract_matches_cards_and_human_boundaries() -> None:
    staging = load_yaml(STAGING_PATH)
    worker_path = REPO_ROOT / staging["worker_contract"]["path"]
    worker_registry = load_yaml(worker_path)

    assert git_blob_sha(worker_path) == staging["worker_contract"]["canonical_blob_sha"]
    assert set(worker_registry["workers"]) == EXPECTED_WORKERS

    for worker_name, worker in worker_registry["workers"].items():
        assert worker["owning_team"] == "physical_systems"
        assert worker["responsibilities"]
        assert worker["required_capabilities"]
        assert len(worker["preferred_implementations"]) >= 2
        assert worker["fallbacks"]
        assert worker["verification"]
        assert worker["escalation"]
        assert worker["authority_boundaries"]
        assert any("human_approval" in item for item in worker["verification"])
        assert any("self_approval" in item or "self_verification" in item for item in worker["authority_boundaries"])


def test_existing_embedded_and_civil_cards_are_not_rewritten() -> None:
    staging = load_yaml(STAGING_PATH)
    preserved = staging["preserved_existing_specialists"]

    assert set(preserved) == {"embedded-engineer", "civil-engineer"}
    for record in preserved.values():
        path = REPO_ROOT / record["card_path"]
        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert record["allocation_change_status"] == "deferred"
        assert record["intended_primary_team"] == "physical_systems"


def test_expansion_registry_contains_the_same_five_specialists() -> None:
    expansion = load_yaml(EXPANSION_PATH)
    records = {item["id"]: item for item in expansion["new_specialists"]}

    for specialist_id, (worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = records[specialist_id]
        assert record["primary_team"] == "physical_systems"
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile


def test_physical_systems_is_not_active_yet() -> None:
    active_routing = load_yaml(ACTIVE_ROUTING_PATH)
    active_specialists = load_yaml(ACTIVE_SPECIALISTS_PATH)
    active_text = ACTIVE_SPECIALISTS_PATH.read_text(encoding="utf-8")

    assert all(
        route.get("primary_team") != "physical_systems"
        for route in active_routing["team_routes"].values()
    )
    for specialist_id in EXPECTED_SPECIALISTS:
        assert specialist_id not in active_text

    staging = load_yaml(STAGING_PATH)
    assert "no_physical_systems_route_is_active_from_this_file" in staging["activation_rules"]
    assert "all_pending_gates_must_pass_before_team_activation" in staging["activation_rules"]


def test_systems_engineering_and_assurance_handoffs_are_mandatory() -> None:
    rules = set(load_yaml(STAGING_PATH)["activation_rules"])

    assert "physical_systems_changes_that_affect_requirements_interfaces_or_baselines_require_systems_engineering_handoff" in rules
    assert "safety_related_work_requires_assurance_handoff" in rules
    assert "specialist_execution_cannot_self_review_or_self_verify" in rules
    assert "critical_release_operation_tapeout_flight_or_production_decisions_require_qualified_human_approval" in rules


def test_regulated_evidence_pilot_remains_exactly_six() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)
    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT
    assert len(pilot["pilot_specialists"]) == 6

    staging = load_yaml(STAGING_PATH)
    assert "evidence_pilot_scope_remains_exactly_six_until_maintainability_gate_passes" in staging["activation_rules"]
