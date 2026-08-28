"""Application-layer repository configuration composition and validation."""

from .composition import (
    ComposedRepositoryConfiguration,
    ConfigurationCompositionError,
    DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST,
    RepositoryConfigurationManifest,
    compose_repository_configuration,
)
from .validation import (
    RepositoryConfigurationValidationInput,
    validate_repository_configuration,
)

__all__ = [
    "ComposedRepositoryConfiguration",
    "ConfigurationCompositionError",
    "DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST",
    "RepositoryConfigurationManifest",
    "RepositoryConfigurationValidationInput",
    "compose_repository_configuration",
    "validate_repository_configuration",
]
