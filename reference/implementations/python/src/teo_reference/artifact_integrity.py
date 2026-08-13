from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote, urlparse

from .schemas import VerifiedArtifact

MAX_VERIFIED_ARTIFACT_BYTES = 65536


class ArtifactIntegrityError(ValueError):
    """Raised when an execution artifact cannot be safely bound or revalidated."""


def _require_text(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ArtifactIntegrityError(f"{name} is required")
    return str(value)


def read_verified_text_artifact(
    output_ref: str,
    *,
    allowed_root: str | Path,
    max_bytes: int = MAX_VERIFIED_ARTIFACT_BYTES,
) -> tuple[str, VerifiedArtifact]:
    """Read one authorized local UTF-8 artifact and bind its exact bytes."""
    parsed = urlparse(_require_text(output_ref, "output_ref"))
    if parsed.scheme != "file":
        raise ArtifactIntegrityError(
            "Artifact-bound verification accepts only local file output artifacts"
        )
    try:
        root = Path(allowed_root).resolve(strict=True)
    except OSError as exc:
        raise ArtifactIntegrityError("Authorized execution artifact root does not exist") from exc
    try:
        path = Path(unquote(parsed.path)).resolve(strict=True)
    except OSError as exc:
        raise ArtifactIntegrityError("Execution output artifact does not exist") from exc
    if not path.is_relative_to(root):
        raise ArtifactIntegrityError("Execution output artifact is outside the authorized artifact root")
    if not path.is_file():
        raise ArtifactIntegrityError("Execution output artifact does not exist")
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise ArtifactIntegrityError("Execution output artifact could not be read") from exc
    if len(payload) > max_bytes:
        raise ArtifactIntegrityError(
            f"Execution output artifact exceeds guarded verification limit of {max_bytes} bytes"
        )
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ArtifactIntegrityError("Execution output artifact could not be read as UTF-8") from exc
    if not text.strip():
        raise ArtifactIntegrityError("execution output is required")
    return (
        text,
        VerifiedArtifact(
            output_ref=path.as_uri(),
            sha256=sha256(payload).hexdigest(),
            size_bytes=len(payload),
        ),
    )


def revalidate_verified_artifact(
    output_ref: str,
    verified_artifact: VerifiedArtifact,
    *,
    allowed_root: str | Path,
    max_bytes: int = MAX_VERIFIED_ARTIFACT_BYTES,
) -> None:
    """Fail closed unless finalization observes the exact artifact the verifier read."""
    _, observed = read_verified_text_artifact(
        output_ref,
        allowed_root=allowed_root,
        max_bytes=max_bytes,
    )
    if observed != verified_artifact:
        raise ArtifactIntegrityError(
            "Finalization artifact does not match the exact artifact bound by verification"
        )
