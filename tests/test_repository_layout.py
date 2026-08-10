from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "ci/validate_repository_layout.py"
POLICY_PATH = REPO_ROOT / "policy/governance/repository-layout.yaml"


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
