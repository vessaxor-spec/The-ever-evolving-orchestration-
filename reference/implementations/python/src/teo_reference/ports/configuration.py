from __future__ import annotations

from typing import Any, Protocol


class SpecialistSelectionPolicyPort(Protocol):
    """Source boundary for the model-neutral specialist selection policy."""

    def load(self) -> dict[str, Any]:
        """Return the specialist selection policy mapping or fail closed."""
        ...
