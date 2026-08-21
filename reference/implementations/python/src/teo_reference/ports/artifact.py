from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..schemas import VerifiedArtifact


class ArtifactIntegrityPortError(ValueError):
    """Raised when an artifact-integrity adapter cannot validate the required binding."""


class ArtifactIntegrityPort(Protocol):
    """Port used by finalization to revalidate the artifact observed by verification."""

    def revalidate(
        self,
        output_ref: str,
        verified_artifact: VerifiedArtifact,
        *,
        allowed_root: str | Path,
    ) -> None:
        """Fail closed unless the current artifact still matches the verified binding."""
        ...
