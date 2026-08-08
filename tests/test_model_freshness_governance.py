from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/governance/model-freshness.yaml"


def load_policy() -> dict:
    payload = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_model_freshness_policy_requires_current_authoritative_evidence() -> None:
    policy = load_policy()

    assert policy["status"] == "active"

    freshness = policy["freshness"]
    assert freshness["pretrained_or_remembered_knowledge_authoritative"] is False
    assert freshness["previously_documented_model_state_authoritative_without_revalidation"] is False
    assert freshness["require_current_authoritative_provider_check"] is True
    assert freshness["fail_state_when_current_authority_unavailable"] == "unverified"
    assert freshness["require_verification_date"] is True
    assert freshness["require_authoritative_source_record"] is True

    source_authority = policy["source_authority"]
    assert source_authority["secondary_sources_may_override_provider_lifecycle_or_identifier_facts"] is False
    assert "provider_api_documentation" in source_authority["authoritative"]
    assert "provider_release_notes" in source_authority["authoritative"]

    release = policy["release_behavior"]
    assert release["newer_release_triggers_review"] is True
    assert release["newer_release_auto_replaces_existing_route"] is False
    assert "fallback_independence" in release["review_must_consider"]
    assert "verifier_independence" in release["review_must_consider"]
    assert "regression_risk" in release["review_must_consider"]

    acceptance = policy["acceptance"]
    assert acceptance["allow_unverified_model_change"] is False
    assert acceptance["allow_training_memory_as_fallback_authority"] is False
    assert acceptance["allow_automatic_route_update_on_release"] is False
    assert acceptance["require_evidence_preservation_for_accepted_model_change"] is True


def test_model_freshness_policy_covers_all_model_bearing_surfaces() -> None:
    policy = load_policy()
    surfaces = set(policy["scope"]["applies_to"])

    required = {
        "primary_execution",
        "routine_fallback",
        "independent_verifier",
        "calibration_judge",
        "machine_panel",
        "guarded_canary",
        "provider_adapter",
        "registry",
        "example",
        "fixture",
        "test",
        "documentation",
    }

    assert required.issubset(surfaces)
