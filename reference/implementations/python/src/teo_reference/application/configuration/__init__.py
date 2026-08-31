"""Application-layer repository configuration composition, validation, and runtime views."""

from .composition import (
    ComposedRepositoryConfiguration,
    ConfigurationCompositionError,
    DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST,
    RepositoryConfigurationManifest,
    compose_repository_configuration,
)
from .runtime_view import (
    FrozenDict,
    FrozenList,
    RuntimeConfigurationBinding,
    RuntimeConfigurationView,
    build_runtime_configuration_view,
)
from .validation import (
    RepositoryConfigurationValidationInput,
    validate_repository_configuration,
)

__all__ = [
    "ComposedRepositoryConfiguration",
    "ConfigurationCompositionError",
    "DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST",
    "FrozenDict",
    "FrozenList",
    "RepositoryConfigurationManifest",
    "RepositoryConfigurationValidationInput",
    "RuntimeConfigurationBinding",
    "RuntimeConfigurationView",
    "build_runtime_configuration_view",
    "compose_repository_configuration",
    "validate_repository_configuration",
]
