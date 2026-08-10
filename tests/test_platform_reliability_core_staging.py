import hashlib
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = REPO_ROOT / "docs" / "history" / "activation" / "platform-reliability-core-staging.yaml"
ACTIVE_ROUTING_PATH = REPO_ROOT / "policy" / "routing" / "core" / "team-routing.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"

EXPECTED_SPECIALISTS = {
    "distributed-systems-engineer": "distributed_systems",
    "database-reliability-engineer": "database_reliability",
    "network-engineer": "network_engineering",
    "platform-engineer": "platform_engineering",
}

EXPECTED_PILOT_SPECIALISTS = {
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
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def test_core_specialists_and_worker_file_match_canonical_blobs() -> None:
    staging = load_yaml(STAGING_PATH)

    assert set(staging["specialists"]) == set(EXPECTED_SPECIALISTS)
    for specialist_id, worker_binding in EXPECTED_SPECIALISTS.items():
        record = staging["specialists"][specialist_id]
        role_path = REPO_ROOT / record["role_card"]
        assert role_path.is_file()
        assert record["worker_binding"] == worker_binding
        assert record["freshness_policy"] == "live-verification-required"
        assert git_blob_sha(role_path) == record["canonical_git_blob_sha"]

    worker_record = staging["worker_definition"]
    worker_path = REPO_ROOT / worker_record["path"]
    assert worker_path.is_file()
    assert git_blob_sha(worker_path) == worker_record["canonical_git_blob_sha"]

    workers = load_yaml(worker_path)["workers"]
    assert set(workers) == set(EXPECTED_SPECIALISTS.values())
    assert all(worker["owning_team"] == "platform_reliability" for worker in workers.values())


def test_specialist_depth_and_separation_are_preserved() -> None:
    staging = load_yaml(STAGING_PATH)
    texts = {
        specialist_id: (REPO_ROOT / record["role_card"]).read_text(encoding="utf-8")
        for specialist_id, record in staging["specialists"].items()
    }

    required_sections = {
        "distributed-systems-engineer": {
            "## Consistency Doctrine",
            "## Consensus and Coordination Doctrine",
            "## Messaging and Idempotency Doctrine",
            "## Distributed Transaction Doctrine",
            "## Replication and Recovery Doctrine",
            "## Overload and Backpressure Doctrine",
        },
        "database-reliability-engineer": {
            "## Durability and Replication Doctrine",
            "## Backup and Restore Doctrine",
            "## Failover Doctrine",
            "## Transaction and Isolation Doctrine",
            "## Schema Change Doctrine",
            "## Query and Planner Doctrine",
        },
        "network-engineer": {
            "## Routing Doctrine",
            "## DNS Doctrine",
            "## Load Balancing and Traffic Doctrine",
            "## Hybrid Connectivity Doctrine",
            "## Segmentation Doctrine",
            "## Packet Diagnosis Doctrine",
        },
        "platform-engineer": {
            "## Platform as Product Doctrine",
            "## Self-Service Doctrine",
            "## Golden Path Doctrine",
            "## Service Catalog Doctrine",
            "## Platform API Doctrine",
            "## Guardrail and Exception Doctrine",
        },
    }

    for specialist_id, sections in required_sections.items():
        text = texts[specialist_id]
        for section in sections:
            assert section in text
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "\u2014" not in text

    assert "Does not own analytical data pipelines" in texts["database-reliability-engineer"]
    assert "Network reachability alone is never authorization" in texts["network-engineer"]
    assert "Does not own every infrastructure implementation personally" in texts["platform-engineer"]
    assert "Does not operate database fleets" in texts["distributed-systems-engineer"]


def test_activation_is_staged_and_all_missing_gates_remain_visible() -> None:
    staging = load_yaml(STAGING_PATH)

    assert staging["status"] == "staged-not-routable"
    assert staging["team"] == "platform_reliability"
    assert set(staging["completed_gates"]) == {
        "team_charter_exists",
        "worker_definition_exists",
        "specialist_cards_exist",
        "independent_verification_defined",
        "critical_risk_has_qualified_human_approval",
        "freshness_policy_present",
        "canonical_preservation_tests_present",
    }
    assert set(staging["pending_gates"]) == {
        "routing_policy_exists",
        "capability_mappings_exist",
        "provider_diverse_fallbacks_exist",
        "conformance_datasets_exist",
        "existing_devops_and_devsecops_reallocations_are_implemented",
    }

    rules = set(staging["activation_rules"])
    assert "no_active_platform_reliability_route_until_every_pending_gate_is_complete" in rules
    assert "staged_specialists_must_not_enter_the_canonical_active_registry_before_route_conformance" in rules
    assert "database_reliability_must_not_absorb_data_engineering" in rules
    assert "network_reachability_must_not_be_treated_as_application_authorization" in rules
    assert "platform_engineering_must_not_absorb_service_team_ownership" in rules


def test_core_wave_is_not_in_active_routing_or_specialist_registry() -> None:
    active_routing_text = ACTIVE_ROUTING_PATH.read_text(encoding="utf-8")
    active_specialists = load_yaml(ACTIVE_SPECIALISTS_PATH)["specialists"]

    assert "primary_team: platform_reliability" not in active_routing_text
    for specialist_id, worker_binding in EXPECTED_SPECIALISTS.items():
        assert specialist_id not in active_specialists
        assert f"primary_worker: {worker_binding}" not in active_routing_text

    assert (REPO_ROOT / "community" / "specialists" / "devops-engineer.md").is_file()
    assert (REPO_ROOT / "community" / "specialists" / "devsecops-engineer.md").is_file()


def test_regulated_evidence_pilot_scope_is_unchanged() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)

    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT_SPECIALISTS
    assert set(EXPECTED_SPECIALISTS).isdisjoint(pilot["pilot_specialists"])
