from __future__ import annotations

from pathlib import Path

from ...artifact_integrity import ArtifactIntegrityError, revalidate_verified_artifact
from ...ports.artifact import ArtifactIntegrityPortError
from ...schemas import VerifiedArtifact


class FilesystemArtifactIntegrityAdapter:
    """Default local-filesystem implementation of the artifact-integrity port."""

    def revalidate(
        self,
        output_ref: str,
        verified_artifact: VerifiedArtifact,
        *,
        allowed_root: str | Path,
    ) -> None:
        try:
            revalidate_verified_artifact(
                output_ref,
                verified_artifact,
                allowed_root=allowed_root,
            )
        except ArtifactIntegrityError as exc:
            raise ArtifactIntegrityPortError(str(exc)) from exc
