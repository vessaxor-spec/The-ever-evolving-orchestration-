from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class RepositoryConfigurationSourcePort(Protocol):
    """Source boundary for repository configuration mappings.

    The port exposes only explicit path reads. It performs no discovery and grants no
    routing or policy authority by itself.
    """

    def load(self, path: Path) -> dict[str, Any]:
        """Load a required configuration mapping or fail closed."""
        ...

    def load_optional(self, path: Path) -> dict[str, Any] | None:
        """Load an explicitly named optional configuration mapping when present."""
        ...


class SpecialistSelectionPolicyPort(Protocol):
    """Source boundary for the model-neutral specialist selection policy."""

    def load(self) -> dict[str, Any]:
        """Return the specialist selection policy mapping or fail closed."""
        ...
