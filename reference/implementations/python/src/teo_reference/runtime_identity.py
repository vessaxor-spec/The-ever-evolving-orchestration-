from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

IdentityStatus = Literal["match", "mismatch", "unconfirmed"]
IdentitySource = Literal[
    "provider_response",
    "provider_adapter",
    "verifier_response",
    "verifier_adapter",
]

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RuntimeIdentityError(ValueError):
    """Raised when runtime identity evidence is structurally invalid."""


def _require_text(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RuntimeIdentityError(f"{name} is required")
    return text


@dataclass(frozen=True, slots=True)
class RuntimeIdentityObservation:
    """Provider-neutral identity evidence reported by the execution boundary.

    Provider and model identity are kept separate from dispatch intent. A model value may
    be present for compatibility while ``model_observed`` is false; callers must not treat
    such a value as runtime attestation. Exact execution-configuration evidence is optional
    because current provider APIs do not all attest TEO's full calibration fingerprint.
    """

    provider_family: str
    model: str
    source: IdentitySource
    model_observed: bool
    configuration_fingerprint: str | None = None
    configuration_observed: bool = False

    def __post_init__(self) -> None:
        _require_text(self.provider_family, "observed provider_family")
        _require_text(self.model, "observed model")
        if self.source not in {
            "provider_response",
            "provider_adapter",
            "verifier_response",
            "verifier_adapter",
        }:
            raise RuntimeIdentityError(f"unsupported identity source: {self.source}")
        if self.configuration_observed:
            if self.configuration_fingerprint is None or not _SHA256_RE.fullmatch(
                self.configuration_fingerprint
            ):
                raise RuntimeIdentityError(
                    "observed configuration fingerprint must be a lowercase SHA-256 digest"
                )
        elif self.configuration_fingerprint is not None:
            raise RuntimeIdentityError(
                "configuration_fingerprint cannot be populated when configuration_observed is false"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_family": self.provider_family,
            "model": self.model,
            "source": self.source,
            "model_observed": self.model_observed,
            "configuration_fingerprint": self.configuration_fingerprint,
            "configuration_observed": self.configuration_observed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RuntimeIdentityObservation":
        allowed = {
            "provider_family",
            "model",
            "source",
            "model_observed",
            "configuration_fingerprint",
            "configuration_observed",
        }
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise RuntimeIdentityError(
                "runtime identity observation contains unsupported fields: "
                + ", ".join(unknown)
            )
        return cls(
            provider_family=_require_text(data.get("provider_family"), "observed provider_family"),
            model=_require_text(data.get("model"), "observed model"),
            source=str(data.get("source")),  # type: ignore[arg-type]
            model_observed=bool(data.get("model_observed", False)),
            configuration_fingerprint=(
                str(data["configuration_fingerprint"])
                if data.get("configuration_fingerprint") is not None
                else None
            ),
            configuration_observed=bool(data.get("configuration_observed", False)),
        )


def compare_runtime_identity(
    *,
    expected_provider_family: str | None,
    expected_model: str,
    observed: RuntimeIdentityObservation | None,
) -> IdentityStatus:
    """Compare explicit dispatch intent with independent runtime identity evidence."""

    if observed is None:
        return "unconfirmed"
    if not expected_provider_family:
        return "unconfirmed"
    if observed.provider_family != expected_provider_family:
        return "mismatch"
    if not observed.model_observed:
        return "unconfirmed"
    if observed.model != expected_model:
        return "mismatch"
    return "match"
