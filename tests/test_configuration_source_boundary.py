from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import teo_reference.config as config_module
from teo_reference.adapters.repository_configuration import YamlRepositoryConfigurationAdapter
from teo_reference.config import ConfigBundle, ConfigurationError


REPO_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_REQUIRED = {
    "policy/routing/core/team-routing.yaml",
    "policy/routing/core/routing.yaml",
    "policy/routing/core/runtime-compatibility-defaults.yaml",
    "community/workers/workers.yaml",
    "community/specialists/specialists.yaml",
    "policy/routing/core/implementation-defaults.yaml",
    "registry/capabilities/capabilities.yaml",
    "registry/models/models.yaml",
}

EXPECTED_OPTIONAL = {
    "policy/routing/extensions/principal-engineering-team-routing.yaml",
    "policy/routing/extensions/specialist-spawn-team-routing.yaml",
    "policy/routing/extensions/mission-control-routing.yaml",
    "policy/routing/extensions/research-routing.yaml",
    "policy/routing/extensions/review-routing.yaml",
    "policy/routing/extensions/principal-engineering-routing.yaml",
    "policy/routing/extensions/specialist-spawn-routing.yaml",
    "community/workers/extensions/incident-response-worker.yaml",
    "community/workers/extensions/research-worker.yaml",
    "community/workers/extensions/market-research-worker.yaml",
    "community/workers/extensions/analytics-worker.yaml",
    "community/workers/extensions/user-research-worker.yaml",
    "community/workers/extensions/compliance-worker.yaml",
    "community/workers/extensions/systems-engineering-worker.yaml",
    "community/workers/extensions/platform-reliability-core-workers.yaml",
    "community/workers/extensions/platform-reliability-operations-workers.yaml",
    "community/workers/extensions/physical-systems-workers.yaml",
    "community/workers/extensions/assurance-workers.yaml",
    "community/workers/extensions/principal-engineering-active-workers.yaml",
    "community/workers/extensions/specialist-completion-workers.yaml",
    "community/workers/extensions/runtime-worker-overrides.yaml",
    "community/specialists/principal-engineering-active.yaml",
    "community/specialists/workforce-expansion-active.yaml",
}


class RecordingSource:
    def __init__(self) -> None:
        self.delegate = YamlRepositoryConfigurationAdapter()
        self.required: list[Path] = []
        self.optional: list[Path] = []

    def load(self, path: Path):
        self.required.append(path)
        return self.delegate.load(path)

    def load_optional(self, path: Path):
        self.optional.append(path)
        return self.delegate.load_optional(path)


def _relative(paths: list[Path]) -> set[str]:
    return {path.relative_to(REPO_ROOT).as_posix() for path in paths}


def test_config_bundle_load_uses_only_explicit_source_paths() -> None:
    source = RecordingSource()

    bundle = ConfigBundle.load(REPO_ROOT, source=source)

    assert not [issue for issue in bundle.validate() if issue.startswith("ERROR:")]
    assert _relative(source.required) == EXPECTED_REQUIRED
    assert _relative(source.optional) == EXPECTED_OPTIONAL
    assert len(source.required) == len(EXPECTED_REQUIRED)
    assert len(source.optional) == len(EXPECTED_OPTIONAL)


def test_config_compatibility_facade_performs_no_yaml_or_file_reads() -> None:
    source = inspect.getsource(config_module)

    assert "import yaml" not in source
    assert "yaml.safe_load" not in source
    assert ".read_text(" not in source
    assert ".glob(" not in source
    assert ".rglob(" not in source


def test_missing_required_file_still_raises_public_configuration_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="Required configuration file not found"):
        ConfigBundle.load(tmp_path)
