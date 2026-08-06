import hashlib
from pathlib import Path
from urllib.parse import urlparse

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGING_PATH = REPO_ROOT / "policy" / "routing" / "systems-engineering-staging.yaml"
ACTIVE_ROUTING_PATH = REPO_ROOT / "policy" / "routing" / "team-routing.yaml"
ACTIVE_SPECIALISTS_PATH = REPO_ROOT / "community" / "specialists" / "specialists.yaml"
EVIDENCE_PILOT_PATH = REPO_ROOT / "policy" / "specialists" / "evidence-pilot.yaml"

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


def test_staged_specialist_and_worker_match_canonical_blobs() -> None:
    staging = load_yaml(STAGING_PATH)
    specialist = staging["specialist"]
    worker = staging["worker"]

    specialist_path = REPO_ROOT / specialist["role_card"]
    worker_path = REPO_ROOT / worker["definition"]

    assert specialist_path.is_file()
    assert worker_path.is_file()
    assert git_blob_sha(specialist_path) == specialist["canonical_git_blob_sha"]
    assert git_blob_sha(worker_path) == worker["canonical_git_blob_sha"]


def test_systems_engineering_responsibility_surface_is_preserved() -> None:
    staging = load_yaml(STAGING_PATH)
    role_text = (REPO_ROOT / staging["specialist"]["role_card"]).read_text(
        encoding="utf-8"
    )
    worker_text = (REPO_ROOT / staging["worker"]["definition"]).read_text(
        encoding="utf-8"
    )

    required_role_sections = {
        "# Systems and Requirements Engineer",
        "## Stakeholder Need and Requirement Separation",
        "## Requirement Quality Doctrine",
        "## Traceability Doctrine",
        "## Interface Control Doctrine",
        "## Verification and Validation Doctrine",
        "## Change Impact Doctrine",
        "## Technical Baseline Doctrine",
        "## Model-Based Systems Engineering Doctrine",
        "## Human Systems Integration",
        "## TEO Allocation",
        "### Preservation rule",
    }
    for section in required_role_sections:
        assert section in role_text

    assert "**Worker binding:** `systems_requirements`" in role_text
    assert "Does not treat Rust systems programming" in role_text
    assert "no_self_approval_or_self_verification" in worker_text
    assert "no_validation_claim_from_requirement_verification_alone" in worker_text
    assert "qualified_human_approval_for_critical_acceptance" in worker_text
    assert "\u2014" not in role_text
    assert "\u2014" not in worker_text


def test_standards_posture_uses_official_iso_status_and_draft_boundary() -> None:
    staging = load_yaml(STAGING_PATH)
    authorities = {
        record["id"]: record for record in staging["standards_posture"]["authorities"]
    }

    assert authorities["iso-15288-2023"]["status"] == "published"
    assert authorities["iso-29148-2018"]["status"] == "published-current"
    assert authorities["iso-dis-29148-edition-3"]["status"] == "under-development"

    for authority in authorities.values():
        assert authority["authority"] == "ISO"
        assert urlparse(authority["source_url"]).hostname == "www.iso.org"

    draft_statement = authorities["iso-dis-29148-edition-3"][
        "governing_statement"
    ]
    assert "draft under development" in draft_statement
    assert "must not be represented as the published governing edition" in draft_statement

    rules = set(staging["standards_posture"]["application_rules"])
    assert "distinguish_published_current_draft_adopted_contractual_and_certification_basis" in rules
    assert "do_not_replace_project_authority_with_latest_publication_automatically" in rules
    assert "refuse_consequential_standards_claims_when_authoritative_status_cannot_be_verified" in rules


def test_systems_engineering_remains_staged_and_not_routable() -> None:
    staging = load_yaml(STAGING_PATH)

    assert staging["status"] == "staged-not-routable"
    assert staging["team"] == "systems_engineering"
    assert staging["specialist"]["worker_binding"] == "systems_requirements"
    assert staging["specialist"]["risk_profile"] == "high"

    assert set(staging["completed_gates"]) == {
        "team_charter_exists",
        "worker_definition_exists",
        "specialist_card_exists",
        "independent_verification_defined",
        "critical_risk_has_qualified_human_approval",
        "freshness_policy_present",
        "canonical_preservation_test_present",
    }
    assert set(staging["pending_gates"]) == {
        "routing_policy_exists",
        "capability_mapping_exists",
        "provider_diverse_fallback_exists",
        "conformance_dataset_exists",
    }

    active_routing_text = ACTIVE_ROUTING_PATH.read_text(encoding="utf-8")
    active_specialists = load_yaml(ACTIVE_SPECIALISTS_PATH)["specialists"]

    assert "primary_team: systems_engineering" not in active_routing_text
    assert "primary_worker: systems_requirements" not in active_routing_text
    assert "systems-requirements-engineer" not in active_specialists


def test_regulated_evidence_pilot_scope_is_unchanged() -> None:
    pilot = load_yaml(EVIDENCE_PILOT_PATH)

    assert set(pilot["pilot_specialists"]) == EXPECTED_PILOT_SPECIALISTS
    assert "systems-requirements-engineer" not in pilot["pilot_specialists"]
