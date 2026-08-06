from hashlib import sha1
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = REPO_ROOT / "policy" / "routing" / "final-principal-specialists-staging.yaml"
EXPANSION_PATH = REPO_ROOT / "policy" / "routing" / "principal-engineering-expansion.yaml"
ACTIVE_ROUTING_PATH = REPO_ROOT / "policy" / "routing" / "team-routing.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"
METHODOLOGY_PATH = REPO_ROOT / "docs" / "methodology" / "final-principal-specialists-staging-2026-08-06.md"

EXPECTED_SPECIALISTS = {
    "cloud-architect": ("planning", "cloud_architecture", "high"),
    "mobile-engineer": ("engineering", "mobile", "medium"),
    "compiler-toolchain-engineer": ("engineering", "compiler_toolchain", "high"),
    "applied-scientist": ("research", "applied_science", "high"),
}

EXPECTED_CATEGORIES = {
    "cloud-architect": "planning",
    "mobile-engineer": "engineering-core",
    "compiler-toolchain-engineer": "engineering-specialized",
    "applied-scientist": "research",
}

EXPECTED_WORKERS = {
    "cloud_architecture",
    "mobile",
    "compiler_toolchain",
    "applied_science",
}

EXPECTED_ALL_NEW_SPECIALISTS = {
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


def test_exact_final_tranche_is_staged() -> None:
    staging = load_yaml(STAGING_PATH)

    assert staging["status"] == "staged"
    assert staging["activation_ready"] is False
    assert staging["scope"] == "final_principal_specialist_card_tranche"
    assert set(staging["specialists"]) == set(EXPECTED_SPECIALISTS)
    assert set(staging["worker_contract"]["expected_workers"]) == EXPECTED_WORKERS
    assert set(staging["pending_gates"]) == {
        "routing_policy_exists",
        "capability_mapping_exists",
        "provider_diverse_fallback_exists",
        "conformance_dataset_exists",
        "all_twenty_two_specialists_added_to_active_registry",
        "existing_specialist_allocation_changes_applied",
        "rust_worker_binding_corrected_in_active_registry",
    }


def test_final_cards_are_full_preserved_allocations() -> None:
    staging = load_yaml(STAGING_PATH)

    for specialist_id, (team, worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = staging["specialists"][specialist_id]
        path = REPO_ROOT / record["card_path"]
        metadata = frontmatter(path)
        text = path.read_text(encoding="utf-8")

        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert metadata["name"] == specialist_id
        assert metadata["category"] == EXPECTED_CATEGORIES[specialist_id]
        assert metadata["freshness_policy"] == "live-verification-required"
        assert record["primary_team"] == team
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile
        assert f"`{worker_binding}`" in text
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "must remain intact" in text
        assert "Independent" in text or "independent" in text
        assert "qualified human approval" in text
        assert "—" not in text


def test_final_worker_contracts_match_teams_and_authority() -> None:
    staging = load_yaml(STAGING_PATH)
    worker_path = REPO_ROOT / staging["worker_contract"]["path"]
    workers = load_yaml(worker_path)["workers"]

    assert git_blob_sha(worker_path) == staging["worker_contract"]["canonical_blob_sha"]
    assert set(workers) == EXPECTED_WORKERS

    assert workers["cloud_architecture"]["owning_team"] == "planning"
    assert workers["mobile"]["owning_team"] == "engineering"
    assert workers["compiler_toolchain"]["owning_team"] == "engineering"
    assert workers["applied_science"]["owning_team"] == "research"

    for worker in workers.values():
        assert worker["responsibilities"]
        assert worker["required_capabilities"]
        assert len(worker["preferred_implementations"]) >= 2
        assert worker["fallbacks"]
        assert worker["verification"]
        assert worker["escalation"]
        assert worker["authority_boundaries"]
        assert any(
            "qualified_human" in item and "approval" in item
            for item in worker["verification"]
        )
        assert any(
            "self_approval" in item or "self_verification" in item
            for item in worker["authority_boundaries"]
        )


def test_adjacent_existing_specialists_are_preserved() -> None:
    preserved = load_yaml(STAGING_PATH)["preserved_existing_specialists"]

    assert set(preserved) == {
        "architect",
        "ai-engineer",
        "data-analyst",
        "rust-engineer",
    }

    for specialist_id, record in preserved.items():
        path = REPO_ROOT / record["card_path"]
        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert record["boundary"]
        if specialist_id == "rust-engineer":
            assert record["intended_worker_binding"] == "rust_systems_programming"


def test_all_twenty_two_approved_cards_now_exist_in_staged_form() -> None:
    expansion = load_yaml(EXPANSION_PATH)
    records = {item["id"]: item for item in expansion["new_specialists"]}

    assert set(records) == EXPECTED_ALL_NEW_SPECIALISTS
    assert len(records) == 22

    for specialist_id in EXPECTED_ALL_NEW_SPECIALISTS:
        path = REPO_ROOT / "community" / "specialists" / f"{specialist_id}.md"
        assert path.is_file(), f"Missing approved specialist card: {specialist_id}"
        metadata = frontmatter(path)
        assert metadata["name"] == specialist_id
        assert metadata["freshness_policy"] == "live-verification-required"
        text = path.read_text(encoding="utf-8")
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text


def test_methodology_checkpoint_is_source_backed_and_role_specific() -> None:
    checkpoint = load_yaml(STAGING_PATH)["methodology_checkpoint"]

    assert checkpoint["cloud_architecture"]["current_provider_evidence_required"] is True
    assert checkpoint["mobile"]["platform_rules_are_volatile"] is True
    assert "LLVM" in checkpoint["compiler_toolchain"]["testing_categories_reference"]
    assert checkpoint["applied_science"]["production_readiness_not_inferred_from_research_prototype"] is True

    methodology = METHODOLOGY_PATH.read_text(encoding="utf-8")
    assert "developer.android.com/topic/architecture" in methodology
    assert "developer.apple.com/documentation/security" in methodology
    assert "llvm.org/docs/TestingGuide.html" in methodology
    assert "nist.gov/itl/ai-risk-management-framework" in methodology
    assert "—" not in methodology


def test_final_specialists_are_not_active_yet() -> None:
    active_routing = load_yaml(ACTIVE_ROUTING_PATH)
    active_text = ACTIVE_SPECIALISTS_PATH.read_text(encoding="utf-8")

    for specialist_id in EXPECTED_ALL_NEW_SPECIALISTS:
        assert specialist_id not in active_text

    active_teams = {
        route.get("primary_team")
        for route in active_routing["team_routes"].values()
    }
    assert "platform_reliability" not in active_teams
    assert "systems_engineering" not in active_teams
    assert "physical_systems" not in active_teams
    assert "assurance" not in active_teams

    rules = set(load_yaml(STAGING_PATH)["activation_rules"])
    assert "no_new_route_is_active_from_this_file" in rules
    assert "all_pending_gates_must_pass_before_activation" in rules


def test_final_authority_boundaries_are_locked() -> None:
    rules = set(load_yaml(STAGING_PATH)["activation_rules"])

    assert "cloud_architecture_does_not_replace_general_architecture_platform_operations_or_procurement" in rules
    assert "mobile_engineering_does_not_replace_product_ux_backend_platform_or_store_authority" in rules
    assert "compiler_toolchain_does_not_replace_language_standard_target_application_or_architecture_authority" in rules
    assert "applied_science_does_not_replace_product_production_ai_mlops_analytics_or_domain_authority" in rules
    assert "new_specialists_cannot_reduce_adjacent_existing_specialist_capabilities" in rules
    assert "specialist_execution_cannot_self_review_or_self_verify" in rules
    assert "consequential_commitment_release_toolchain_or_deployment_decisions_require_qualified_human_approval" in rules


def test_regulated_evidence_pilot_remains_exactly_six() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)
    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT
    assert len(pilot["pilot_specialists"]) == 6

    rules = set(load_yaml(STAGING_PATH)["activation_rules"])
    assert "evidence_pilot_scope_remains_exactly_six_until_maintainability_gate_passes" in rules
