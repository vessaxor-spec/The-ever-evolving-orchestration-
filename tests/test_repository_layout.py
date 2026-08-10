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
    assert policy["migration"]["current_phase"] == "R3"
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
