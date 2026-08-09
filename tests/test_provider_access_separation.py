from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
ACCESS_POLICY = REPO_ROOT / "policy/governance/provider-access-separation.yaml"
FRESHNESS_POLICY = REPO_ROOT / "policy/governance/model-freshness.yaml"
V1_POLICY = REPO_ROOT / "policy/governance/v1-readiness.yaml"
AI_INSTRUCTIONS = REPO_ROOT / "AI_INSTRUCTIONS.md"
PROVIDER_CONNECTION = (
    REPO_ROOT
    / "reference/implementations/python/src/teo_reference/provider_connection.py"
)
EVIDENCE_WORKFLOW = REPO_ROOT / ".github/workflows/provisional-operational-evidence.yml"


def _load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _walk_keys(value: object):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def test_access_policy_makes_access_external_to_routing() -> None:
    policy = _load_yaml(ACCESS_POLICY)
    assert policy["status"] == "active"

    boundary = policy["routing_boundary"]
    assert "model_selection" in boundary["teo_owns"]
    assert "reasoning_effort" in boundary["teo_owns"]
    assert "oauth_login" in boundary["teo_does_not_own"]
    assert "api_key_provisioning" in boundary["teo_does_not_own"]
    assert "subscription_management" in boundary["teo_does_not_own"]

    neutrality = policy["access_neutrality"]
    assert neutrality["authentication_method_may_change_route"] is False
    assert neutrality["subscription_type_may_change_route"] is False
    assert neutrality["credential_presence_may_change_route"] is False
    assert neutrality["caller_or_integrator_owns_access_resolution"] is True

    runtime = policy["runtime_boundary"]
    assert runtime["provider_connection_is_injected_after_routing"] is True
    assert runtime["reference_api_key_helpers_are_convenience_only"] is True
    assert runtime["reference_api_key_helpers_define_teo_architecture"] is False
    assert runtime["missing_or_invalid_access_may_poison_global_provider_health"] is False


def test_model_freshness_distinguishes_provider_model_state_from_user_access() -> None:
    policy = _load_yaml(FRESHNESS_POLICY)
    separation = policy["access_separation"]
    assert separation["policy"] == "policy/governance/provider-access-separation.yaml"
    assert separation["user_authentication_method_is_model_freshness"] is False
    assert separation["user_subscription_or_entitlement_is_model_freshness"] is False
    assert separation["credential_availability_is_model_freshness"] is False
    assert separation["provider_level_model_availability_remains_model_freshness"] is True
    assert "preview_authorization" in policy["release_behavior"]["review_must_consider"]
    assert "preview_or_access_constraints" not in policy["release_behavior"]["review_must_consider"]


def test_v1_does_not_claim_teo_owns_provider_account_access() -> None:
    policy = _load_yaml(V1_POLICY)
    definition = policy["v1_definition"]
    assert definition["provider_access_provisioning_owned_by_teo"] is False
    assert definition["caller_or_integrator_owns_valid_model_access"] is True

    access = policy["provider_access_boundary"]
    assert access["routing_must_be_authentication_method_neutral"] is True
    assert access["api_key_access_supported_by_reference_helpers"] is True
    assert access["oauth_or_subscription_access_may_be_supplied_by_integrating_runtime"] is True
    assert access["reference_api_key_evidence_workflow_is_convenience_harness"] is True
    assert access["reference_api_key_evidence_workflow_defines_teo_access_requirement"] is False


def test_provider_connection_contract_is_post_routing_and_access_neutral() -> None:
    text = PROVIDER_CONNECTION.read_text(encoding="utf-8")
    assert "independent from TEO model routing" in text
    assert "already-selected provider operation" in text
    assert "API key, OAuth flow, delegated identity, service account, credential broker, connector" in text
    assert "TEO routing never inspects or persists it" in text


def test_ai_instructions_preserve_connection_neutrality() -> None:
    text = AI_INSTRUCTIONS.read_text(encoding="utf-8")
    assert "## Connection neutrality" in text
    assert "Connection mechanism is separate from routing semantics" in text
    assert "API keys, OAuth, delegated identity, service accounts, connector sessions" in text
    assert "must not change the selected Team, Worker, Specialist, model role, fallback, verifier, or reasoning effort" in text


def test_routing_and_model_registry_do_not_encode_authentication_mechanics() -> None:
    paths = [
        REPO_ROOT / "policy/routing/routing.yaml",
        REPO_ROOT / "policy/routing/specialist-model-routing.yaml",
        REPO_ROOT / "policy/routing/team-routing.yaml",
        REPO_ROOT / "models.yaml",
    ]
    forbidden_keys = {
        "api_key",
        "api_keys",
        "oauth",
        "authentication",
        "credential",
        "credentials",
        "subscription",
        "billing_method",
        "login_state",
    }
    for path in paths:
        keys = set(_walk_keys(_load_yaml(path)))
        assert not (keys & forbidden_keys), f"{path} embeds provider-access mechanics into routing/model policy"


def test_github_evidence_workflow_is_explicitly_only_an_api_key_harness() -> None:
    text = EVIDENCE_WORKFLOW.read_text(encoding="utf-8")
    assert "API-key convenience harness" in text
    assert "workflow-environment choice, not a TEO routing or provider-access requirement" in text
    assert "TEO itself does not require API-key authentication" in text
    assert "ProviderConnection" in text
