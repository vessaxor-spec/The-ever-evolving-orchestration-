from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from teo_reference.config import ConfigBundle


ROOT = Path(__file__).resolve().parents[1]
DISALLOWED_RESPONSIBILITY_KEYS = {
    "agent",
    "model",
    "profile",
    "reasoning",
    "reasoning_by_risk",
    "preferred_implementations",
    "fallbacks",
}


def _model_identity_paths(value: Any, path: str):
    if isinstance(value, dict):
        for key, nested in value.items():
            current = f"{path}.{key}"
            if key in DISALLOWED_RESPONSIBILITY_KEYS:
                yield current
            yield from _model_identity_paths(nested, current)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from _model_identity_paths(nested, f"{path}[{index}]")


def test_loaded_responsibility_surfaces_are_model_neutral() -> None:
    bundle = ConfigBundle.load(ROOT)

    worker_identity = list(_model_identity_paths(bundle.workers, "workers"))
    routing_identity = list(_model_identity_paths(bundle.routing, "routing"))

    assert worker_identity == []
    assert routing_identity == []


def test_runtime_compatibility_defaults_cover_active_workers() -> None:
    bundle = ConfigBundle.load(ROOT)

    assert set(bundle.worker_runtime_defaults) == set(bundle.worker_registry)
    for worker, defaults in bundle.worker_runtime_defaults.items():
        assert defaults["preferred_implementations"], worker
        assert defaults["fallbacks"], worker


def test_specialist_selection_profiles_are_model_neutral_and_compatibility_backed() -> None:
    bundle = ConfigBundle.load(ROOT)
    policy_path = ROOT / "policy/routing/core/specialist-selection-policy.yaml"
    policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))

    assert set(policy["specialists"]) == set(bundle.specialist_registry)
    assert set(policy["profiles"]) == set(bundle.runtime_specialist_profiles)
    assert list(_model_identity_paths(policy, "specialist_selection_policy")) == []

    for specialist, assignment in policy["specialists"].items():
        profile = assignment["selection_profile"]
        assert profile in policy["profiles"], specialist
        defaults = bundle.runtime_specialist_profiles[profile]
        assert defaults["primary"]["model"]
        assert defaults["fallback"]["model"]
        assert defaults["verifier"]["model"]


def test_legacy_specialist_model_policy_is_retired() -> None:
    assert not (ROOT / "policy/routing/core/specialist-model-routing.yaml").exists()
    assert (ROOT / "policy/routing/core/specialist-selection-policy.yaml").is_file()
    assert (ROOT / "policy/routing/core/runtime-compatibility-defaults.yaml").is_file()
