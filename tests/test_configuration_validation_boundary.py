from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path

import pytest

import teo_reference.application.configuration.validation as validation_module
from teo_reference.adapters.repository_configuration import YamlRepositoryConfigurationAdapter
from teo_reference.application.configuration.validation import (
    RepositoryConfigurationValidationInput,
    validate_repository_configuration,
)
from teo_reference.config import ConfigBundle, ConfigurationError


REPO_ROOT = Path(__file__).resolve().parents[1]


def _validation_input(bundle: ConfigBundle) -> RepositoryConfigurationValidationInput:
    return RepositoryConfigurationValidationInput(
        team_routing=bundle.team_routing,
        routing=bundle.routing,
        runtime_compatibility=bundle.runtime_compatibility,
        workers=bundle.workers,
        specialists=bundle.specialists,
        models=bundle.models,
        capabilities=bundle.capabilities,
        model_evidence=bundle.model_evidence,
    )


def test_application_validator_matches_clean_config_bundle_facade() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    direct = validate_repository_configuration(_validation_input(bundle))

    assert direct == bundle.validate() == []


def test_application_validator_matches_mutated_config_bundle_facade() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    bundle.routing["routing"]["daily_coding"]["primary"]["model"] = "gpt-5.6-terra"

    direct = validate_repository_configuration(_validation_input(bundle))

    assert direct == bundle.validate()
    assert direct == [
        "ERROR: model/provider implementation identity is not allowed in responsibility configuration: "
        "routing.routing.daily_coding.primary.model"
    ]


def test_validation_input_preserves_mutable_config_bundle_compatibility() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    validation_input = _validation_input(bundle)

    bundle.routing["routing"]["daily_coding"]["primary"]["model"] = "gpt-5.6-terra"

    assert validate_repository_configuration(validation_input) == bundle.validate()
    assert any("daily_coding.primary.model" in issue for issue in bundle.validate())


def test_config_bundle_validate_is_a_thin_application_facade() -> None:
    source = inspect.getsource(ConfigBundle.validate)

    assert "validate_repository_configuration" in source
    assert "runtime compatibility worker-default coverage" not in source
    assert "provider-diverse verifier candidate" not in source
    assert "specialist bindings without worker definitions" not in source


def test_validation_application_boundary_has_no_outer_or_io_dependencies() -> None:
    source = inspect.getsource(validation_module)

    for forbidden in (
        "teo_reference.config",
        "from ...adapters",
        "from ...provider_",
        "from ...cli",
        "import yaml",
        ".read_text(",
        ".glob(",
        ".rglob(",
    ):
        assert forbidden not in source


class InvalidInvariantSource:
    def __init__(self) -> None:
        self.delegate = YamlRepositoryConfigurationAdapter()

    def load(self, path: Path):
        payload = self.delegate.load(path)
        if path.name != "runtime-compatibility-defaults.yaml":
            return payload
        mutated = deepcopy(payload)
        worker_name = next(iter(mutated["worker_defaults"]))
        del mutated["worker_defaults"][worker_name]
        return mutated

    def load_optional(self, path: Path):
        return self.delegate.load_optional(path)


def test_config_bundle_load_remains_fail_closed_on_validation_errors() -> None:
    with pytest.raises(
        ConfigurationError,
        match="runtime compatibility worker-default coverage must exactly match active workers",
    ):
        ConfigBundle.load(REPO_ROOT, source=InvalidInvariantSource())
