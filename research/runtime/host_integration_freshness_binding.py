from __future__ import annotations

import hashlib
import json
import runpy
import tomllib
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

from teo_reference.config import ConfigBundle


class IntegrationFreshnessError(ValueError):
    """Raised when host-integration freshness evidence is malformed or ambiguous."""


class FreshnessStatus(str, Enum):
    PINNED_CURRENT = "PINNED_CURRENT"
    PINNED_COMPATIBLE = "PINNED_COMPATIBLE"
    UPDATE_AVAILABLE = "UPDATE_AVAILABLE"
    STALE_UNSUPPORTED = "STALE_UNSUPPORTED"
    MISMATCHED = "MISMATCHED"


class HistoricalDisposition(str, Enum):
    COMPATIBLE = "compatible"
    UPDATE_AVAILABLE = "update_available"
    UNSUPPORTED = "unsupported"


_BINDING_FIELDS = {
    "release",
    "runtime_version",
    "revision",
    "authority_surface_fingerprint",
    "team_routing_fingerprint",
    "implementation_routing_fingerprint",
    "worker_registry_fingerprint",
    "specialist_registry_fingerprint",
    "capability_registry_fingerprint",
    "model_registry_fingerprint",
    "model_evidence_fingerprint",
    "executable_composition_id",
}

_HASH_FIELDS = _BINDING_FIELDS - {"release", "runtime_version", "revision"}


def _canonicalize_for_hash(value: Any) -> Any:
    """Convert effective configuration values into deterministic typed JSON data.

    YAML may load scalars such as dates into Python objects that plain JSON cannot
    serialize. Those values must retain their type identity rather than being flattened
    to strings, because a YAML date and an ordinary string with the same characters are
    not the same executable configuration value.
    """

    if value is None or type(value) in {bool, int, str}:
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, datetime):
        return {"$type": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"$type": "date", "value": value.isoformat()}
    if isinstance(value, Mapping):
        canonical: dict[str, Any] = {}
        for key, nested in value.items():
            if not isinstance(key, str):
                raise IntegrationFreshnessError(
                    "effective configuration mappings must use string keys"
                )
            canonical[key] = _canonicalize_for_hash(nested)
        return canonical
    if isinstance(value, (list, tuple)):
        return [_canonicalize_for_hash(item) for item in value]
    raise IntegrationFreshnessError(
        "unsupported effective configuration value for freshness hashing: "
        f"{type(value).__name__}"
    )


def _sha256_payload(value: Any) -> str:
    encoded = json.dumps(
        _canonicalize_for_hash(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _require_text(value: Any, *, field_name: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise IntegrationFreshnessError(f"{field_name} must be canonical non-empty text")
    return value


def _require_sha256(value: Any, *, field_name: str) -> str:
    text = _require_text(value, field_name=field_name)
    if len(text) != 64 or text.lower() != text:
        raise IntegrationFreshnessError(
            f"{field_name} must be 64 lowercase hexadecimal characters"
        )
    try:
        int(text, 16)
    except ValueError as exc:
        raise IntegrationFreshnessError(f"{field_name} must be hexadecimal") from exc
    return text


def _require_revision(value: Any) -> str:
    text = _require_text(value, field_name="revision")
    if len(text) != 40 or text.lower() != text:
        raise IntegrationFreshnessError(
            "revision must be a 40-character lowercase hexadecimal commit id"
        )
    try:
        int(text, 16)
    except ValueError as exc:
        raise IntegrationFreshnessError("revision must be hexadecimal") from exc
    return text


@dataclass(frozen=True, slots=True)
class IntegrationBindingSnapshot:
    release: str
    runtime_version: str
    revision: str
    authority_surface_fingerprint: str
    team_routing_fingerprint: str
    implementation_routing_fingerprint: str
    worker_registry_fingerprint: str
    specialist_registry_fingerprint: str
    capability_registry_fingerprint: str
    model_registry_fingerprint: str
    model_evidence_fingerprint: str
    executable_composition_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "release", _require_text(self.release, field_name="release"))
        object.__setattr__(
            self,
            "runtime_version",
            _require_text(self.runtime_version, field_name="runtime_version"),
        )
        object.__setattr__(self, "revision", _require_revision(self.revision))
        for field_name in sorted(_HASH_FIELDS):
            object.__setattr__(
                self,
                field_name,
                _require_sha256(getattr(self, field_name), field_name=field_name),
            )

    @property
    def binding_id(self) -> str:
        return _sha256_payload(self.to_dict())

    def to_dict(self) -> dict[str, str]:
        return {
            field_name: str(getattr(self, field_name))
            for field_name in sorted(_BINDING_FIELDS)
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "IntegrationBindingSnapshot":
        if not isinstance(value, Mapping):
            raise IntegrationFreshnessError("binding snapshot must be a mapping")
        actual = set(value)
        if actual != _BINDING_FIELDS:
            missing = sorted(_BINDING_FIELDS - actual)
            extra = sorted(actual - _BINDING_FIELDS)
            details: list[str] = []
            if missing:
                details.append("missing=" + ",".join(missing))
            if extra:
                details.append("extra=" + ",".join(extra))
            raise IntegrationFreshnessError(
                "binding snapshot fields must match the research contract exactly: "
                + "; ".join(details)
            )
        return cls(**{field_name: value[field_name] for field_name in _BINDING_FIELDS})


@dataclass(frozen=True, slots=True)
class HistoricalBindingRecord:
    binding: IntegrationBindingSnapshot
    disposition: HistoricalDisposition


@dataclass(frozen=True, slots=True)
class FreshnessAssessment:
    status: FreshnessStatus
    binding_id: str
    claimed_status: FreshnessStatus | None
    claim_matches: bool
    acceptable: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "binding_id": self.binding_id,
            "claimed_status": (
                self.claimed_status.value if self.claimed_status is not None else None
            ),
            "claim_matches": self.claim_matches,
            "acceptable": self.acceptable,
        }


class AuthorityOwnedBindingCatalog:
    """TEO-side research catalog of exact current and historical integration bindings."""

    def __init__(
        self,
        current: IntegrationBindingSnapshot,
        historical: Sequence[HistoricalBindingRecord] = (),
    ) -> None:
        if not isinstance(current, IntegrationBindingSnapshot):
            raise IntegrationFreshnessError(
                "current binding must use IntegrationBindingSnapshot"
            )
        self.current = current
        self._by_binding_id: dict[str, HistoricalBindingRecord] = {}
        self._by_revision: dict[str, HistoricalBindingRecord] = {}

        for record in historical:
            if not isinstance(record, HistoricalBindingRecord):
                raise IntegrationFreshnessError(
                    "historical catalog entries must use HistoricalBindingRecord"
                )
            if not isinstance(record.disposition, HistoricalDisposition):
                raise IntegrationFreshnessError(
                    "historical disposition must use HistoricalDisposition"
                )
            binding = record.binding
            if not isinstance(binding, IntegrationBindingSnapshot):
                raise IntegrationFreshnessError(
                    "historical binding must use IntegrationBindingSnapshot"
                )
            if binding.revision == current.revision:
                raise IntegrationFreshnessError(
                    "historical binding cannot reuse the current revision"
                )
            if binding.binding_id == current.binding_id:
                raise IntegrationFreshnessError(
                    "historical binding cannot duplicate the current binding"
                )
            if binding.revision in self._by_revision:
                raise IntegrationFreshnessError(
                    f"historical catalog has duplicate revision: {binding.revision}"
                )
            if binding.binding_id in self._by_binding_id:
                raise IntegrationFreshnessError(
                    f"historical catalog has duplicate binding id: {binding.binding_id}"
                )
            self._by_revision[binding.revision] = record
            self._by_binding_id[binding.binding_id] = record

    def historical_by_binding_id(
        self, binding_id: str
    ) -> HistoricalBindingRecord | None:
        return self._by_binding_id.get(binding_id)

    def historical_by_revision(
        self, revision: str
    ) -> HistoricalBindingRecord | None:
        return self._by_revision.get(revision)


def _runtime_version(repo_root: Path) -> str:
    pyproject = repo_root / "pyproject.toml"
    try:
        payload = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise IntegrationFreshnessError(
            f"cannot read runtime package metadata: {pyproject}"
        ) from exc
    project = payload.get("project")
    if not isinstance(project, dict):
        raise IntegrationFreshnessError("pyproject.toml is missing [project]")
    return _require_text(project.get("version"), field_name="runtime_version")


def _authority_surface_fingerprint(repo_root: Path) -> str:
    sibling = Path(__file__).with_name(
        "host_integration_authority_surface_reconciliation.py"
    )
    namespace = runpy.run_path(str(sibling))
    snapshotter = namespace.get("snapshot_authority_surfaces")
    if not callable(snapshotter):
        raise IntegrationFreshnessError(
            "authority-surface research snapshotter is unavailable"
        )
    snapshot = snapshotter(repo_root)
    return _require_sha256(
        getattr(snapshot, "fingerprint", None),
        field_name="authority_surface_fingerprint",
    )


def build_binding_snapshot(
    repo_root: str | Path,
    *,
    release: str,
    revision: str,
) -> IntegrationBindingSnapshot:
    """Derive one exact TEO-side integration binding from executable repository truth."""

    root = Path(repo_root).resolve(strict=True)
    bundle = ConfigBundle.load(root)
    runtime_version = _runtime_version(root)
    authority_surface_fingerprint = _authority_surface_fingerprint(root)

    components = {
        "team_routing": bundle.team_routes,
        "implementation_routing": bundle.implementation_routes,
        "worker_registry": bundle.worker_registry,
        "specialist_registry": bundle.specialist_registry,
        "capability_registry": bundle.capability_registry,
        "model_registry": bundle.model_registry,
        "model_evidence": bundle.model_evidence_registry,
    }
    fingerprints = {
        name: _sha256_payload(value) for name, value in components.items()
    }
    executable_composition_id = _sha256_payload(
        {
            "runtime_version": runtime_version,
            "authority_surface_fingerprint": authority_surface_fingerprint,
            "components": fingerprints,
        }
    )

    return IntegrationBindingSnapshot(
        release=_require_text(release, field_name="release"),
        runtime_version=runtime_version,
        revision=_require_revision(revision),
        authority_surface_fingerprint=authority_surface_fingerprint,
        team_routing_fingerprint=fingerprints["team_routing"],
        implementation_routing_fingerprint=fingerprints["implementation_routing"],
        worker_registry_fingerprint=fingerprints["worker_registry"],
        specialist_registry_fingerprint=fingerprints["specialist_registry"],
        capability_registry_fingerprint=fingerprints["capability_registry"],
        model_registry_fingerprint=fingerprints["model_registry"],
        model_evidence_fingerprint=fingerprints["model_evidence"],
        executable_composition_id=executable_composition_id,
    )


def _status_for_record(record: HistoricalBindingRecord) -> FreshnessStatus:
    mapping = {
        HistoricalDisposition.COMPATIBLE: FreshnessStatus.PINNED_COMPATIBLE,
        HistoricalDisposition.UPDATE_AVAILABLE: FreshnessStatus.UPDATE_AVAILABLE,
        HistoricalDisposition.UNSUPPORTED: FreshnessStatus.STALE_UNSUPPORTED,
    }
    return mapping[record.disposition]


def assess_host_binding(
    host_binding: IntegrationBindingSnapshot | Mapping[str, Any],
    catalog: AuthorityOwnedBindingCatalog,
    *,
    claimed_status: FreshnessStatus | str | None = None,
) -> FreshnessAssessment:
    """Classify a host pin from TEO-side exact evidence, never from a host label."""

    if not isinstance(catalog, AuthorityOwnedBindingCatalog):
        raise IntegrationFreshnessError(
            "freshness assessment requires an authority-owned binding catalog"
        )
    if isinstance(host_binding, IntegrationBindingSnapshot):
        binding = host_binding
    else:
        binding = IntegrationBindingSnapshot.from_mapping(host_binding)

    if claimed_status is None:
        claimed = None
    else:
        try:
            claimed = (
                claimed_status
                if isinstance(claimed_status, FreshnessStatus)
                else FreshnessStatus(str(claimed_status))
            )
        except ValueError as exc:
            raise IntegrationFreshnessError(
                f"unknown claimed freshness state: {claimed_status}"
            ) from exc

    if binding == catalog.current:
        status = FreshnessStatus.PINNED_CURRENT
    else:
        record = catalog.historical_by_binding_id(binding.binding_id)
        status = _status_for_record(record) if record is not None else FreshnessStatus.MISMATCHED

    claim_matches = claimed is None or claimed == status
    acceptable = (
        claim_matches
        and status
        in {
            FreshnessStatus.PINNED_CURRENT,
            FreshnessStatus.PINNED_COMPATIBLE,
            FreshnessStatus.UPDATE_AVAILABLE,
        }
    )
    return FreshnessAssessment(
        status=status,
        binding_id=binding.binding_id,
        claimed_status=claimed,
        claim_matches=claim_matches,
        acceptable=acceptable,
    )
