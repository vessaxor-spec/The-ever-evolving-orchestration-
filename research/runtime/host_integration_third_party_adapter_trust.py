#!/usr/bin/env python3
"""Non-normative third-party provider-adapter trust research harness.

This module models the smallest process-local registration boundary needed to test
third-party adapter provenance without changing the normative provider-adapter contract.

The authority owns the approved manifest snapshot, adapter factory, measured artifact
identity, and registered runtime type. The artifact reader stands in for a trusted
loader/package measurement. A production implementation must derive executable artifact
identity from an authority-controlled loader or package store rather than accept a digest
or bytes asserted by an untrusted host.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import dataclass
from typing import Callable

from teo_reference.provider_adapter import ProviderAdapter, execute_provider_once
from teo_reference.schemas import DispatchRecord, ExecutionResult


class AdapterTrustError(RuntimeError):
    """Raised when an adapter registration or execution trust check fails."""


def _require_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdapterTrustError(f"{name} is required")
    return value.strip()


@dataclass(frozen=True, slots=True)
class ThirdPartyAdapterManifest:
    """Research-only authority description for one external provider adapter."""

    adapter_id: str
    provider_family: str
    supported_capabilities: tuple[str, ...]
    contract_version: str = "1"
    operation: str = "provider_execute_once"

    def __post_init__(self) -> None:
        _require_text(self.adapter_id, "adapter_id")
        _require_text(self.provider_family, "provider_family")
        if self.contract_version != "1":
            raise AdapterTrustError("unsupported adapter contract_version")
        if self.operation != "provider_execute_once":
            raise AdapterTrustError("unsupported adapter operation")
        normalized = tuple(
            _require_text(item, "supported_capability")
            for item in self.supported_capabilities
        )
        if len(normalized) != len(set(normalized)):
            raise AdapterTrustError("supported_capabilities cannot contain duplicates")

    def to_dict(self) -> dict[str, object]:
        return {
            "adapter_id": self.adapter_id,
            "provider_family": self.provider_family,
            "supported_capabilities": list(self.supported_capabilities),
            "contract_version": self.contract_version,
            "operation": self.operation,
        }


def canonical_manifest_bytes(manifest: ThirdPartyAdapterManifest) -> bytes:
    return json.dumps(
        manifest.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def artifact_sha256(payload: bytes) -> str:
    if not isinstance(payload, bytes) or not payload:
        raise AdapterTrustError("adapter implementation artifact must be non-empty bytes")
    return hashlib.sha256(payload).hexdigest()


ArtifactReader = Callable[[], bytes]
AdapterFactory = Callable[[], ProviderAdapter]


@dataclass(slots=True)
class _Registration:
    manifest_snapshot: bytes
    artifact_digest: str
    artifact_reader: ArtifactReader
    adapter_factory: AdapterFactory
    adapter_type: type
    active: bool = True


class ProcessLocalAdapterAuthority:
    """Authority-owned process-local registry for adversarial trust experiments."""

    def __init__(self) -> None:
        self._registrations: dict[str, _Registration] = {}

    def register(
        self,
        manifest: ThirdPartyAdapterManifest,
        *,
        artifact_reader: ArtifactReader,
        adapter_factory: AdapterFactory,
    ) -> str:
        artifact = artifact_reader()
        probe = adapter_factory()
        if probe.provider_family != manifest.provider_family:
            raise AdapterTrustError(
                "adapter factory provider does not match the approved manifest"
            )
        token = secrets.token_urlsafe(24)
        self._registrations[token] = _Registration(
            manifest_snapshot=canonical_manifest_bytes(manifest),
            artifact_digest=artifact_sha256(artifact),
            artifact_reader=artifact_reader,
            adapter_factory=adapter_factory,
            adapter_type=type(probe),
        )
        return token

    def revoke(self, token: str) -> None:
        registration = self._registrations.get(token)
        if registration is None:
            raise AdapterTrustError("adapter registration token was not issued")
        registration.active = False

    def resolve(
        self,
        token: str,
        manifest: ThirdPartyAdapterManifest,
        dispatch: DispatchRecord,
    ) -> ProviderAdapter:
        registration = self._registrations.get(token)
        if registration is None:
            raise AdapterTrustError("adapter registration token was not issued")
        if not registration.active:
            raise AdapterTrustError("adapter registration is revoked")

        presented_manifest = canonical_manifest_bytes(manifest)
        if not hmac.compare_digest(
            presented_manifest, registration.manifest_snapshot
        ):
            raise AdapterTrustError(
                "adapter manifest differs from the authority-owned registration"
            )

        current_digest = artifact_sha256(registration.artifact_reader())
        if not hmac.compare_digest(current_digest, registration.artifact_digest):
            raise AdapterTrustError(
                "adapter implementation artifact changed after registration"
            )

        selected_provider = dispatch.selected_implementation.provider_family
        if selected_provider != manifest.provider_family:
            raise AdapterTrustError(
                "adapter manifest provider does not match the dispatch-selected provider"
            )

        missing = sorted(
            set(dispatch.required_capabilities) - set(manifest.supported_capabilities)
        )
        if missing:
            raise AdapterTrustError(
                "adapter registration does not cover dispatch capabilities: "
                + ", ".join(missing)
            )

        adapter = registration.adapter_factory()
        if type(adapter) is not registration.adapter_type:
            raise AdapterTrustError(
                "adapter factory resolved a different runtime type after registration"
            )
        if adapter.provider_family != manifest.provider_family:
            raise AdapterTrustError(
                "registered adapter runtime provider family drifted after registration"
            )
        return adapter


def execute_registered_provider_once(
    authority: ProcessLocalAdapterAuthority,
    token: str,
    manifest: ThirdPartyAdapterManifest,
    dispatch: DispatchRecord,
    input_payload: dict[str, object] | None = None,
) -> ExecutionResult:
    """Resolve only the authority-owned registered adapter, then execute exactly once."""

    adapter = authority.resolve(token, manifest, dispatch)
    return execute_provider_once(adapter, dispatch, input_payload)
