"""Application-layer repository configuration composition."""

from .composition import (
    ComposedRepositoryConfiguration,
    ConfigurationCompositionError,
    DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST,
    RepositoryConfigurationManifest,
    compose_repository_configuration,
)

__all__ = [
    "ComposedRepositoryConfiguration",
    "ConfigurationCompositionError",
    "DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST",
    "RepositoryConfigurationManifest",
    "compose_repository_configuration",
]
