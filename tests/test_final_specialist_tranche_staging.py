from hashlib import sha1
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = REPO_ROOT / "docs" / "history" / "activation" / "final-specialist-tranche-staging.yaml"
EXPANSION_PATH = REPO_ROOT / "docs" / "history" / "activation" / "principal-engineering-expansion.yaml"
ACTIVE_ROUTING_PATH = REPO_ROOT / "policy" / "routing" / "core" / "team-routing.yaml"
ACTIVE_WORKERS_PATH = REPO_ROOT / "community" / "workers" / "workers.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"
HISTORY_PATH = REPO_ROOT / "docs" / "history" / "activation" / "final-specialist-tranche-staging-2026-08-06.md"

EXPECTED_SPECIALISTS = {
    "cloud-architect": ("planning", "cloud_architecture", "high"),
    "mobile-engineer": ("engineering", "mobile", "medium"),
    "compiler-toolchain-engineer": ("engineering", "compiler_toolchain", "high"),
    "applied-scientist": ("research", "applied_science", "high"),
}

EXPECTED_WORKERS = {
    "cloud_architecture": "planning",
    "mobile": "engineering",
    "compiler_toolchain": "engineering",
    "applied_science": "research",
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


def test_exact_final_tranche_scope_is_staged() -> None:
    staging = load_yaml(STAGING_PATH)

    assert staging["status"] == "staged"
    assert staging["activation_ready"] is False
    assert staging["tranche"] == "planning_engineering_research"
    assert set(staging["specialists"]) == set(EXPECTED_SPECIALISTS)
    assert set(staging["worker_contract"]["expected_workers"]) == set(EXPECTED_WORKERS)
    assert staging["worker_contract"]["status"] == "staged_contracts_not_loaded_by_active_config"
    assert set(staging["pending_gates"]) == {
        "routing_policy_exists",
        "capability_mappings_exist",
        "provider_diverse_fallbacks_exist",
        "conformance_datasets_exist",
        "canonical_active_registry_entries_exist",
        "mobile_canonical_worker_reconciliation_exists",
    }


def test_new_cards_match_canonical_blobs_and_allocations() -> None:
    staging = load_yaml(STAGING_PATH)

    category_by_specialist = {
        "cloud-architect": "architecture",
        "mobile-engineer": "engineering-core",
        "compiler-toolchain-engineer": "engineering-specialized",
        "applied-scientist": "research",
    }

    for specialist_id, (team, worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = staging["specialists"][specialist_id]
        path = REPO_ROOT / record["card_path"]
        metadata = frontmatter(path)
        text = path.read_text(encoding="utf-8")

        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert metadata["name"] == specialist_id
        assert metadata["category"] == category_by_specialist[specialist_id]
        assert metadata["freshness_policy"] == "live-verification-required"
        assert record["primary_team"] == team
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile
        assert f"`{worker_binding}`" in text
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "must remain intact" in text
        assert "—" not in text


def test_specialist_depth_and_boundaries_are_preserved() -> None:
    staging = load_yaml(STAGING_PATH)
    texts = {
        specialist_id: (REPO_ROOT / record["card_path"]).read_text(encoding="utf-8")
        for specialist_id, record in staging["specialists"].items()
    }

    required_sections = {
        "cloud-architect": {
            "## Landing-Zone Doctrine",
            "## Account and Subscription Doctrine",
            "## Service Selection Doctrine",
            "## Resilience Doctrine",
            "## Multi-Cloud Doctrine",
            "## Migration Doctrine",
            "## Exit Doctrine",
        },
        "mobile-engineer": {
            "## Lifecycle Doctrine",
            "## Offline and Synchronization Doctrine",
            "## Permission Doctrine",
            "## Local Data Doctrine",
            "## UI and Accessibility Doctrine",
            "## Background Execution Doctrine",
            "## Release Doctrine",
        },
        "compiler-toolchain-engineer": {
            "## Language Semantics Doctrine",
            "## Intermediate Representation Doctrine",
            "## Optimization Doctrine",
            "## ABI Doctrine",
            "## Reproducible-Build Doctrine",
            "## Compiler Testing Doctrine",
            "## Miscompilation Doctrine",
        },
        "applied-scientist": {
            "## Estimand Doctrine",
            "## Experimental Design Doctrine",
            "## Observational Study Doctrine",
            "## Benchmark Doctrine",
            "## Causal Inference Doctrine",
            "## Reproducibility Doctrine",
            "## Translation to Engineering Doctrine",
        },
    }

    for specialist_id, sections in required_sections.items():
        text = texts[specialist_id]
        for section in sections:
            assert section in text

    assert "Does not replace the general Architect" in texts["cloud-architect"]
    assert "Does not replace Product Management or UX Design" in texts["mobile-engineer"]
    assert "Does not replace general application" in texts["compiler-toolchain-engineer"]
    assert "Does not replace Data Engineering, AI Engineering, MLOps, Analytics" in texts["applied-scientist"]


def test_staged_worker_contract_has_distinct_teams_and_authority() -> None:
    staging = load_yaml(STAGING_PATH)
    worker_path = REPO_ROOT / "docs" / "history" / "activation" / "final-specialist-workers.yaml"
    workers = load_yaml(worker_path)["workers"]

    assert git_blob_sha(worker_path) == staging["worker_contract"]["canonical_blob_sha"]
    assert set(workers) == set(EXPECTED_WORKERS)

    for worker_name, owning_team in EXPECTED_WORKERS.items():
        worker = workers[worker_name]
        assert worker["owning_team"] == owning_team
        assert worker["responsibilities"]
        assert worker["required_capabilities"]
        assert len(worker["preferred_implementations"]) >= 2
        assert worker["fallbacks"]
        assert worker["verification"]
        assert worker["escalation"]
        assert worker["authority_boundaries"]
        assert any("independent" in item for item in worker["verification"])
        assert any(
            "self_approval" in item or "self_verification" in item
            for item in worker["authority_boundaries"]
        )


def test_existing_architect_ai_engineer_and_researcher_are_preserved() -> None:
    staging = load_yaml(STAGING_PATH)
    preserved = staging["preserved_existing_specialists"]

    assert set(preserved) == {"architect", "ai-engineer", "researcher"}
    for record in preserved.values():
        path = REPO_ROOT / record["card_path"]
        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert record["boundary"]


def test_existing_mobile_worker_is_preserved_but_specialist_is_staged() -> None:
    staging = load_yaml(STAGING_PATH)
    active_workers = load_yaml(ACTIVE_WORKERS_PATH)["workers"]
    active_specialists = load_yaml(ACTIVE_SPECIALISTS_PATH)["specialists"]
    reconciliation = staging["existing_active_worker_reconciliation"]["mobile"]

    assert "mobile" in active_workers
    assert active_workers["mobile"]["owning_team"] == "engineering"
    assert reconciliation["current_status"] == "active_core_worker"
    assert reconciliation["current_owning_team"] == "engineering"
    assert "without_duplicate_definition" in reconciliation["activation_requirement"]
    assert "mobile-engineer" not in active_specialists

    rules = set(staging["activation_rules"])
    assert "existing_mobile_worker_and_context_override_remain_active_and_unchanged" in rules
    assert "the_new_mobile_specialist_and_enriched_contract_remain_staged_until_canonical_reconciliation_and_conformance" in rules


def test_expansion_registry_contains_the_same_four_specialists() -> None:
    expansion = load_yaml(EXPANSION_PATH)
    records = {item["id"]: item for item in expansion["new_specialists"]}

    for specialist_id, (team, worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = records[specialist_id]
        assert record["primary_team"] == team
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile


def test_new_specialists_are_not_in_active_registry_or_new_routes() -> None:
    staging = load_yaml(STAGING_PATH)
    active_routes = load_yaml(ACTIVE_ROUTING_PATH)["team_routes"]
    active_specialists = load_yaml(ACTIVE_SPECIALISTS_PATH)["specialists"]

    for specialist_id in EXPECTED_SPECIALISTS:
        assert specialist_id not in active_specialists

    active_primary_workers = {
        route.get("primary_worker")
        for route in active_routes.values()
        if isinstance(route, dict)
    }
    assert "cloud_architecture" not in active_primary_workers
    assert "compiler_toolchain" not in active_primary_workers
    assert "applied_science" not in active_primary_workers

    rules = set(staging["activation_rules"])
    assert "no_route_is_activated_from_this_staging_file" in rules
    assert "all_pending_gates_must_pass_before_any_new_specialist_becomes_active" in rules
    assert "specialist_execution_cannot_self_review_or_self_verify" in rules


def test_history_record_and_staged_worker_file_avoid_em_dash() -> None:
    staging = load_yaml(STAGING_PATH)
    worker_text = (REPO_ROOT / "docs" / "history" / "activation" / "final-specialist-workers.yaml").read_text(encoding="utf-8")
    history_text = HISTORY_PATH.read_text(encoding="utf-8")

    assert "—" not in worker_text
    assert "—" not in history_text


def test_regulated_evidence_pilot_remains_exactly_six() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)
    staging = load_yaml(STAGING_PATH)

    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT
    assert len(pilot["pilot_specialists"]) == 6
    assert set(EXPECTED_SPECIALISTS).isdisjoint(pilot["pilot_specialists"])
    assert "evidence_pilot_scope_remains_exactly_six_until_maintainability_gate_passes" in staging["activation_rules"]
