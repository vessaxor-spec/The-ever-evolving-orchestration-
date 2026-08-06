from hashlib import sha1
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = REPO_ROOT / "policy" / "routing" / "assurance-staging.yaml"
EXPANSION_PATH = REPO_ROOT / "policy" / "routing" / "principal-engineering-expansion.yaml"
ACTIVE_ROUTING_PATH = REPO_ROOT / "policy" / "routing" / "team-routing.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"
METHODOLOGY_PATH = REPO_ROOT / "docs" / "methodology" / "assurance-specialist-staging-2026-08-06.md"

EXPECTED_SPECIALISTS = {
    "privacy-engineer": ("privacy_engineering", "critical"),
    "functional-safety-engineer": ("functional_safety", "critical"),
    "formal-methods-engineer": ("formal_methods", "high"),
    "application-security-engineer": ("application_security", "critical"),
}

EXPECTED_WORKERS = {
    "privacy_engineering",
    "functional_safety",
    "formal_methods",
    "application_security",
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


def test_exact_assurance_scope_is_staged() -> None:
    staging = load_yaml(STAGING_PATH)

    assert staging["status"] == "staged"
    assert staging["team"] == "assurance"
    assert staging["activation_ready"] is False
    assert set(staging["specialists"]) == set(EXPECTED_SPECIALISTS)
    assert set(staging["worker_contract"]["expected_workers"]) == EXPECTED_WORKERS
    assert set(staging["pending_gates"]) == {
        "routing_policy_exists",
        "capability_mapping_exists",
        "provider_diverse_fallback_exists",
        "conformance_dataset_exists",
    }


def test_assurance_cards_are_full_preserved_allocations() -> None:
    staging = load_yaml(STAGING_PATH)

    for specialist_id, (worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = staging["specialists"][specialist_id]
        path = REPO_ROOT / record["card_path"]
        metadata = frontmatter(path)
        text = path.read_text(encoding="utf-8")

        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert metadata["name"] == specialist_id
        assert metadata["category"] == "assurance"
        assert metadata["freshness_policy"] == "live-verification-required"
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile
        assert f"`{worker_binding}`" in text
        assert "## TEO Allocation" in text
        assert "### Preservation rule" in text
        assert "must remain intact" in text
        assert "Independent" in text or "independent" in text
        assert "qualified human approval" in text
        assert "—" not in text


def test_assurance_workers_enforce_independence_and_human_authority() -> None:
    staging = load_yaml(STAGING_PATH)
    worker_path = REPO_ROOT / staging["worker_contract"]["path"]
    workers = load_yaml(worker_path)["workers"]

    assert git_blob_sha(worker_path) == staging["worker_contract"]["canonical_blob_sha"]
    assert set(workers) == EXPECTED_WORKERS

    for worker in workers.values():
        assert worker["owning_team"] == "assurance"
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


def test_existing_compliance_and_security_cards_are_preserved() -> None:
    staging = load_yaml(STAGING_PATH)
    preserved = staging["preserved_existing_specialists"]

    assert set(preserved) == {"compliance-auditor", "security-engineer"}
    for record in preserved.values():
        path = REPO_ROOT / record["card_path"]
        assert path.is_file()
        assert git_blob_sha(path) == record["canonical_blob_sha"]
        assert record["boundary"]


def test_standards_checkpoint_distinguishes_published_from_draft() -> None:
    checkpoint = load_yaml(STAGING_PATH)["standards_checkpoint"]

    assert checkpoint["privacy_engineering"]["published_framework"] == "NIST Privacy Framework 1.0"
    assert "Initial Public Draft" in checkpoint["privacy_engineering"]["draft_not_governing_by_default"]
    assert checkpoint["functional_safety"]["horizontal_reference"] == "IEC 61508 series"
    assert checkpoint["functional_safety"]["automotive_published_series"] == "ISO 26262:2018 Edition 2"
    assert "working drafts" in checkpoint["functional_safety"]["automotive_draft_not_governing_by_default"]
    assert checkpoint["formal_methods"]["testing_still_required"] is True
    assert checkpoint["application_security"]["latest_stable_verification_standard"] == "OWASP ASVS 5.0.0"
    assert checkpoint["application_security"]["versioned_requirement_references_required"] is True

    methodology = METHODOLOGY_PATH.read_text(encoding="utf-8")
    assert "nist.gov/itl/applied-cybersecurity/privacy-engineering" in methodology
    assert "webstore.iec.ch/en/publication/5520" in methodology
    assert "iso.org/standard/90021" in methodology
    assert "csrc.nist.gov/projects/automated-combinatorial-testing" in methodology
    assert "owasp.org/www-project-application-security-verification-standard" in methodology


def test_expansion_registry_contains_the_same_assurance_specialists() -> None:
    expansion = load_yaml(EXPANSION_PATH)
    records = {item["id"]: item for item in expansion["new_specialists"]}

    for specialist_id, (worker_binding, risk_profile) in EXPECTED_SPECIALISTS.items():
        record = records[specialist_id]
        assert record["primary_team"] == "assurance"
        assert record["worker_binding"] == worker_binding
        assert record["risk_profile"] == risk_profile


def test_assurance_is_not_active_yet() -> None:
    active_routing = load_yaml(ACTIVE_ROUTING_PATH)
    active_text = ACTIVE_SPECIALISTS_PATH.read_text(encoding="utf-8")

    assert all(
        route.get("primary_team") != "assurance"
        for route in active_routing["team_routes"].values()
    )
    for specialist_id in EXPECTED_SPECIALISTS:
        assert specialist_id not in active_text

    rules = set(load_yaml(STAGING_PATH)["activation_rules"])
    assert "no_assurance_route_is_active_from_this_file" in rules
    assert "all_pending_gates_must_pass_before_team_activation" in rules
    assert "assurance_defines_and_builds_claims_controls_and_evidence_but_does_not_self_verify" in rules


def test_assurance_authority_boundaries_are_locked() -> None:
    rules = set(load_yaml(STAGING_PATH)["activation_rules"])

    assert "compliance_legal_security_product_and_domain_authorities_remain_distinct" in rules
    assert "privacy_engineering_does_not_issue_legal_or_compliance_judgment" in rules
    assert "functional_safety_does_not_replace_regulator_certifier_or_release_authority" in rules
    assert "formal_methods_does_not_turn_bounded_or_assumption_dependent_evidence_into_unbounded_claims" in rules
    assert "application_security_requires_written_authorization_before_active_testing" in rules
    assert "critical_privacy_safety_or_application_security_decisions_require_qualified_human_approval" in rules


def test_regulated_evidence_pilot_remains_exactly_six() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)
    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT
    assert len(pilot["pilot_specialists"]) == 6

    rules = set(load_yaml(STAGING_PATH)["activation_rules"])
    assert "evidence_pilot_scope_remains_exactly_six_until_maintainability_gate_passes" in rules
