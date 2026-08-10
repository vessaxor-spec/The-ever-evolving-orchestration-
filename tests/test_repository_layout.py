from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "ci/validate_repository_layout.py"
POLICY_PATH = REPO_ROOT / "policy/governance/repository-layout.yaml"

R2_OLD_PATHS = {
    "MANIFESTO.md",
    "LEXICON.md",
    "STEWARDSHIP.md",
    "ROADMAP.md",
    "V1_READINESS.md",
    "research/ROADMAP_RESEARCH.md",
}
R2_CANONICAL_PATHS = {
    "docs/philosophy/manifesto.md",
    "docs/specification/lexicon.md",
    "docs/stewardship/stewardship.md",
    "docs/stewardship/roadmap.md",
    "docs/releases/v1-readiness.md",
    "research/roadmaps/intelligence-control-plane.md",
}

R3_OLD_PATHS = {
    "docs/methodology/ai-mediated-discovery-refresh-2026-08-05.md",
    "docs/methodology/assurance-specialist-staging-2026-08-06.md",
    "docs/methodology/final-specialist-tranche-staging-2026-08-06.md",
    "docs/methodology/model-routing-audit-2026-08-07.md",
    "docs/methodology/native-operations-refresh-2026-08-05.md",
    "docs/methodology/physical-systems-staging-2026-08-06.md",
    "docs/methodology/platform-reliability-core-staging-2026-08-06.md",
    "docs/methodology/platform-reliability-operations-staging-2026-08-06.md",
    "docs/methodology/principal-engineering-activation-2026-08-06.md",
    "docs/methodology/principal-engineering-team-expansion-2026-08-06.md",
    "docs/methodology/regulated-specialist-refresh-2026-08-05.md",
    "docs/methodology/research-analytics-security-assurance-2026-08-05.md",
    "docs/methodology/systems-engineering-specialist-staging-2026-08-06.md",
    "docs/history/mission-control-routing-recalibration-2026-08-09.md",
}
R3_CANONICAL_PATHS = {
    "docs/history/audits/ai-mediated-discovery-refresh-2026-08-05.md",
    "docs/history/activation/assurance-specialist-staging-2026-08-06.md",
    "docs/history/activation/final-specialist-tranche-staging-2026-08-06.md",
    "docs/history/audits/model-routing-audit-2026-08-07.md",
    "docs/history/audits/native-operations-refresh-2026-08-05.md",
    "docs/history/activation/physical-systems-staging-2026-08-06.md",
    "docs/history/activation/platform-reliability-core-staging-2026-08-06.md",
    "docs/history/activation/platform-reliability-operations-staging-2026-08-06.md",
    "docs/history/activation/principal-engineering-activation-2026-08-06.md",
    "docs/history/activation/principal-engineering-team-expansion-2026-08-06.md",
    "docs/history/audits/regulated-specialist-refresh-2026-08-05.md",
    "docs/history/audits/research-analytics-security-assurance-2026-08-05.md",
    "docs/history/activation/systems-engineering-specialist-staging-2026-08-06.md",
    "docs/history/audits/mission-control-routing-recalibration-2026-08-09.md",
}


def _load_validator():
    spec = importlib.util.spec_from_file_location("teo_repository_layout", VALIDATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


def _current_paths() -> set[str]:
    return set(validator.collect_tracked_files(REPO_ROOT))


def test_current_tracked_repository_layout_conforms() -> None:
    policy = validator.load_policy(POLICY_PATH)
    assert validator.validate_layout(_current_paths(), policy) == []


def test_r2_normalized_paths_are_canonical() -> None:
    paths = _current_paths()
    assert R2_OLD_PATHS.isdisjoint(paths)
    assert R2_CANONICAL_PATHS <= paths


def test_r2_paths_are_no_longer_temporary_exceptions() -> None:
    policy = validator.load_policy(POLICY_PATH)
    root_exceptions = set(policy["root"]["temporary_exceptions"])
    research_exceptions = set(policy["contracts"]["research"]["temporary_direct_exceptions"])
    assert R2_OLD_PATHS.isdisjoint(root_exceptions | {f"research/{name}" for name in research_exceptions})
    assert "R2_root_and_research_normalization" in policy["migration"]["completed_phases"]


def test_r2_active_navigation_uses_canonical_paths() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    ai_instructions = (REPO_ROOT / "AI_INSTRUCTIONS.md").read_text(encoding="utf-8")
    release_contract = (REPO_ROOT / "docs/releases/v1.0.0.md").read_text(encoding="utf-8")

    for canonical in (
        "docs/philosophy/manifesto.md",
        "docs/specification/lexicon.md",
        "docs/releases/v1-readiness.md",
    ):
        assert canonical in readme

    assert "docs/specification/lexicon.md" in ai_instructions
    assert "docs/releases/v1-readiness.md" in release_contract

    for retired in ("](MANIFESTO.md)", "](LEXICON.md)", "](V1_READINESS.md)"):
        assert retired not in readme
    assert "`LEXICON.md`" not in ai_instructions
    assert "- `V1_READINESS.md`" not in release_contract


def test_r3_history_paths_are_canonical() -> None:
    paths = _current_paths()
    assert R3_OLD_PATHS.isdisjoint(paths)
    assert R3_CANONICAL_PATHS <= paths
    assert "docs/history/activation/README.md" in paths
    assert "docs/history/audits/README.md" in paths


def test_r3_history_exceptions_are_closed() -> None:
    policy = validator.load_policy(POLICY_PATH)
    assert policy["contracts"]["docs_methodology"]["temporary_history_exceptions"] == []
    assert policy["contracts"]["docs_history"]["temporary_direct_exceptions"] == []
    assert policy["migration"]["current_phase"] == "R5"
    assert "R3_documentation_lifecycle_separation" in policy["migration"]["completed_phases"]


def test_r3_methodology_and_history_indexes_explain_lifecycle() -> None:
    methodology = (REPO_ROOT / "docs/methodology/README.md").read_text(encoding="utf-8")
    history = (REPO_ROOT / "docs/history/README.md").read_text(encoding="utf-8")
    activation = (REPO_ROOT / "docs/history/activation/README.md").read_text(encoding="utf-8")
    audits = (REPO_ROOT / "docs/history/audits/README.md").read_text(encoding="utf-8")

    assert "reusable methods" in methodology.lower()
    assert "docs/history" in methodology
    assert "no longer represents current operational authority" in history
    assert "Do not use an activation-history record as current routing authority." in activation
    assert "may later become stale" in audits


def test_unknown_root_file_is_rejected() -> None:
    policy = validator.load_policy(POLICY_PATH)
    paths = _current_paths() | {"FINAL_ARCHITECTURE_V2.md"}
    errors = validator.validate_layout(paths, policy)
    assert any("Undeclared root file FINAL_ARCHITECTURE_V2.md" in error for error in errors)


def test_undeclared_direct_routing_policy_is_rejected() -> None:
    policy = validator.load_policy(POLICY_PATH)
    paths = _current_paths() | {"policy/routing/random-policy.yaml"}
    errors = validator.validate_layout(paths, policy)
    assert any("Undeclared direct routing policy" in error for error in errors)


def test_team_nested_specialist_identity_is_rejected() -> None:
    policy = validator.load_policy(POLICY_PATH)
    paths = _current_paths() | {"community/specialists/engineering/example-specialist.md"}
    errors = validator.validate_layout(paths, policy)
    assert any("Nested specialist path" in error for error in errors)


def test_bad_capsule_name_is_rejected() -> None:
    policy = validator.load_policy(POLICY_PATH)
    paths = _current_paths() | {"community/capsules/latest-state.md"}
    errors = validator.validate_layout(paths, policy)
    assert any("Capsule filename violates naming contract" in error for error in errors)


R4_OLD_PATHS = {
    "routing.yaml",
    "policy/routing/routing.yaml",
    "policy/routing/team-routing.yaml",
    "policy/routing/specialist-model-routing.yaml",
    "policy/routing/mission-control-routing.yaml",
    "policy/routing/research-routing.yaml",
    "policy/routing/review-routing.yaml",
    "policy/routing/principal-engineering-routing.yaml",
    "policy/routing/principal-engineering-team-routing.yaml",
    "policy/routing/specialist-spawn-routing.yaml",
    "policy/routing/specialist-spawn-team-routing.yaml",
    "policy/routing/principal-engineering-activation.yaml",
    "policy/routing/principal-engineering-expansion.yaml",
    "policy/routing/assurance-staging.yaml",
    "policy/routing/final-specialist-tranche-staging.yaml",
    "policy/routing/physical-systems-staging.yaml",
    "policy/routing/platform-reliability-core-staging.yaml",
    "policy/routing/platform-reliability-operations-staging.yaml",
    "policy/routing/systems-engineering-staging.yaml",
}

R4_CANONICAL_PATHS = {
    "policy/routing/core/routing.yaml",
    "policy/routing/core/team-routing.yaml",
    "policy/routing/core/specialist-model-routing.yaml",
    "policy/routing/extensions/mission-control-routing.yaml",
    "policy/routing/extensions/research-routing.yaml",
    "policy/routing/extensions/review-routing.yaml",
    "policy/routing/extensions/principal-engineering-routing.yaml",
    "policy/routing/extensions/principal-engineering-team-routing.yaml",
    "policy/routing/extensions/specialist-spawn-routing.yaml",
    "policy/routing/extensions/specialist-spawn-team-routing.yaml",
    "policy/routing/activation/principal-engineering.yaml",
    "docs/history/activation/initial-routing-draft.yaml",
    "docs/history/activation/principal-engineering-expansion.yaml",
    "docs/history/activation/assurance-staging.yaml",
    "docs/history/activation/final-specialist-tranche-staging.yaml",
    "docs/history/activation/physical-systems-staging.yaml",
    "docs/history/activation/platform-reliability-core-staging.yaml",
    "docs/history/activation/platform-reliability-operations-staging.yaml",
    "docs/history/activation/systems-engineering-staging.yaml",
}

def test_r4_policy_topology_paths_are_canonical() -> None:
    paths = _current_paths()
    assert R4_OLD_PATHS.isdisjoint(paths)
    assert R4_CANONICAL_PATHS <= paths

def test_r4_policy_topology_has_no_temporary_exceptions() -> None:
    policy = validator.load_policy(POLICY_PATH)
    routing = policy["contracts"]["policy_routing"]
    assert routing["active_direct_files"] == []
    assert routing["temporary_direct_exceptions"] == []
    assert set(routing["canonical_subdirectories"]) == {"core", "extensions", "activation"}
    assert "R4_policy_topology" in policy["migration"]["completed_phases"]
    assert policy["migration"]["current_phase"] == "R5"
    assert "routing.yaml" not in policy["root"]["temporary_exceptions"]

def test_undeclared_nested_routing_policy_is_rejected() -> None:
    policy = validator.load_policy(POLICY_PATH)
    paths = _current_paths() | {"policy/routing/extensions/random-policy.yaml"}
    errors = validator.validate_layout(paths, policy)
    assert any("Undeclared routing file" in error for error in errors)
