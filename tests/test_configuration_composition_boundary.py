from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path
from typing import Any

import pytest

import teo_reference.config as config_module
from teo_reference.adapters.repository_configuration import YamlRepositoryConfigurationAdapter
from teo_reference.application.configuration.composition import (
    ConfigurationCompositionError,
    compose_repository_configuration,
    load_routing,
    load_specialists,
    load_team_routing,
    load_workers,
)
from teo_reference.config import ConfigBundle, ConfigurationError


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIGURATION_PACKAGE = (
    REPO_ROOT
    / "reference"
    / "implementations"
    / "python"
    / "src"
    / "teo_reference"
    / "application"
    / "configuration"
)

EXPECTED_REQUESTS = [
    ("required", "policy/routing/core/team-routing.yaml"),
    ("optional", "policy/routing/extensions/principal-engineering-team-routing.yaml"),
    ("optional", "policy/routing/extensions/specialist-spawn-team-routing.yaml"),
    ("required", "policy/routing/core/routing.yaml"),
    ("optional", "policy/routing/extensions/mission-control-routing.yaml"),
    ("optional", "policy/routing/extensions/research-routing.yaml"),
    ("optional", "policy/routing/extensions/review-routing.yaml"),
    ("optional", "policy/routing/extensions/principal-engineering-routing.yaml"),
    ("optional", "policy/routing/extensions/specialist-spawn-routing.yaml"),
    ("required", "policy/routing/core/runtime-compatibility-defaults.yaml"),
    ("required", "community/workers/workers.yaml"),
    ("optional", "community/workers/extensions/incident-response-worker.yaml"),
    ("optional", "community/workers/extensions/research-worker.yaml"),
    ("optional", "community/workers/extensions/market-research-worker.yaml"),
    ("optional", "community/workers/extensions/analytics-worker.yaml"),
    ("optional", "community/workers/extensions/user-research-worker.yaml"),
    ("optional", "community/workers/extensions/compliance-worker.yaml"),
    ("optional", "community/workers/extensions/systems-engineering-worker.yaml"),
    ("optional", "community/workers/extensions/platform-reliability-core-workers.yaml"),
    ("optional", "community/workers/extensions/platform-reliability-operations-workers.yaml"),
    ("optional", "community/workers/extensions/physical-systems-workers.yaml"),
    ("optional", "community/workers/extensions/assurance-workers.yaml"),
    ("optional", "community/workers/extensions/principal-engineering-active-workers.yaml"),
    ("optional", "community/workers/extensions/specialist-completion-workers.yaml"),
    ("optional", "community/workers/extensions/runtime-worker-overrides.yaml"),
    ("required", "community/specialists/specialists.yaml"),
    ("optional", "community/specialists/principal-engineering-active.yaml"),
    ("optional", "community/specialists/workforce-expansion-active.yaml"),
    ("required", "policy/routing/core/implementation-defaults.yaml"),
    ("required", "registry/capabilities/capabilities.yaml"),
    ("required", "registry/models/models.yaml"),
]


class RecordingSource:
    def __init__(self) -> None:
        self.delegate = YamlRepositoryConfigurationAdapter()
        self.requests: list[tuple[str, str]] = []

    def _relative(self, path: Path) -> str:
        return path.relative_to(REPO_ROOT).as_posix()

    def load(self, path: Path) -> dict[str, Any]:
        self.requests.append(("required", self._relative(path)))
        return self.delegate.load(path)

    def load_optional(self, path: Path) -> dict[str, Any] | None:
        self.requests.append(("optional", self._relative(path)))
        return self.delegate.load_optional(path)


class MappingSource:
    def __init__(self, values: dict[Path, dict[str, Any]]) -> None:
        self.values = values

    def load(self, path: Path) -> dict[str, Any]:
        return deepcopy(self.values[path])

    def load_optional(self, path: Path) -> dict[str, Any] | None:
        value = self.values.get(path)
        return deepcopy(value) if value is not None else None


def test_composition_requests_exact_manifest_in_exact_order() -> None:
    source = RecordingSource()

    composed = compose_repository_configuration(REPO_ROOT, source)

    assert source.requests == EXPECTED_REQUESTS
    assert composed.team_routing["team_routes"]
    assert composed.routing["routing"]
    assert composed.workers["workers"]
    assert composed.specialists["specialists"]


def test_config_bundle_delegates_to_application_composition_boundary() -> None:
    source = inspect.getsource(ConfigBundle.load)
    module_source = inspect.getsource(config_module)

    assert "compose_repository_configuration(root_path, configuration_source)" in source
    assert "policy/routing/core/team-routing.yaml" not in source
    assert "community/workers/extensions/runtime-worker-overrides.yaml" not in source
    assert "policy/routing/core/team-routing.yaml" not in module_source
    assert "community/workers/extensions/runtime-worker-overrides.yaml" not in module_source


def test_application_composition_boundary_has_no_outer_layer_dependencies() -> None:
    forbidden = (
        "teo_reference.config",
        "from ...adapters",
        "from ...provider_",
        "from ...cli",
        "import yaml",
        ".read_text(",
        ".glob(",
        ".rglob(",
    )
    for path in CONFIGURATION_PACKAGE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path.name} depends on outer boundary {marker}"


def test_team_route_duplicate_and_override_rules_are_preserved() -> None:
    base = Path("team.yaml")
    extension = Path("team-ext.yaml")
    duplicate_source = MappingSource(
        {
            base: {"team_routes": {"daily": {"primary_team": "engineering"}}},
            extension: {"team_routes": {"daily": {"primary_team": "research"}}},
        }
    )
    with pytest.raises(
        ConfigurationCompositionError,
        match="Team-routing extension duplicates canonical routes",
    ):
        load_team_routing(duplicate_source, base, (extension,))

    override_source = MappingSource(
        {
            base: {"team_routes": {"daily": {"primary_team": "engineering"}}},
            extension: {
                "team_routes": {},
                "route_overrides": {"daily": {"primary_team": "mission_control"}},
            },
        }
    )
    result = load_team_routing(override_source, base, (extension,))
    assert result["team_routes"]["daily"] == {"primary_team": "mission_control"}


def test_worker_override_rules_are_preserved() -> None:
    base = Path("workers.yaml")
    extension = Path("workers-ext.yaml")
    source = MappingSource(
        {
            base: {"workers": {"backend": {"owning_team": "engineering", "risk": "low"}}},
            extension: {
                "workers": {"researcher": {"owning_team": "research"}},
                "worker_overrides": {"backend": {"risk": "medium"}},
            },
        }
    )

    result = load_workers(source, base, (extension,))

    assert result["workers"]["backend"]["risk"] == "medium"
    assert result["workers"]["researcher"]["owning_team"] == "research"


def test_protected_specialist_override_is_still_rejected_publicly() -> None:
    base = Path("specialists.yaml")
    extension = Path("specialists-ext.yaml")
    source = MappingSource(
        {
            base: {
                "specialists": {
                    "backend-engineer": {
                        "primary_team": "engineering",
                        "worker_binding": "backend",
                    }
                }
            },
            extension: {
                "specialists": {},
                "allocation_overrides": {
                    "backend-engineer": {"model": "forbidden-concrete-model"}
                },
            },
        }
    )

    with pytest.raises(
        ConfigurationCompositionError,
        match="Specialist override changes protected fields for backend-engineer: model",
    ):
        load_specialists(source, base, (extension,))

    class FailingCompositionSource:
        def load(self, path: Path) -> dict[str, Any]:
            return source.load(path)

        def load_optional(self, path: Path) -> dict[str, Any] | None:
            return source.load_optional(path)

    with pytest.raises(ConfigurationError, match="protected fields"):
        config_module._load_specialists(FailingCompositionSource(), base, (extension,))


def test_routing_normalization_is_preserved() -> None:
    base = Path("routing.yaml")
    extension = Path("routing-ext.yaml")
    source = MappingSource(
        {
            base: {
                "routing": {
                    "daily": {"escalation": {"when": "blocked"}},
                },
                "verification_policy": {
                    "low_risk": {"method": ["output_validation"]},
                    "medium": {"method": ["targeted_review"]},
                    "high_risk": {"method": ["independent_review"]},
                },
            },
            extension: {
                "routing": {
                    "research": {"escalation": {"when": "uncertain"}},
                }
            },
        }
    )

    result = load_routing(source, base, (extension,))

    assert "escalation" not in result["routing"]["daily"]
    assert result["routing"]["daily"]["conditional_escalation"] == {"when": "blocked"}
    assert result["routing"]["research"]["conditional_escalation"] == {"when": "uncertain"}
    assert result["verification_policy"]["low"] == result["verification_policy"]["low_risk"]
    assert result["verification_policy"]["medium"] == {"method": ["targeted_review"]}
    assert result["verification_policy"]["high"] == result["verification_policy"]["high_risk"]


def test_composed_repository_matches_config_bundle_views() -> None:
    composed = compose_repository_configuration(
        REPO_ROOT,
        YamlRepositoryConfigurationAdapter(),
    )
    bundle = ConfigBundle.load(REPO_ROOT)

    assert composed.team_routing == bundle.team_routing
    assert composed.routing == bundle.routing
    assert composed.runtime_compatibility == bundle.runtime_compatibility
    assert composed.workers == bundle.workers
    assert composed.specialists == bundle.specialists
    assert composed.models == bundle.models
    assert composed.capabilities == bundle.capabilities
    assert composed.model_evidence == bundle.model_evidence
