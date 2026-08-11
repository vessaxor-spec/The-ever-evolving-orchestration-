#!/usr/bin/env python3
"""Non-normative host-integration dispatch authorization research control.

The reference provider adapter contract intentionally consumes a DispatchRecord but does
not prove that an external host received that record from the TEO dispatcher. This module
models the smallest process-local provenance boundary needed to test that gap without
changing runtime authority or introducing a parallel routing system.

The registry is deliberately process-local. Its opaque tokens are capability references
into authority-owned state, not portable cryptographic attestations. Cross-process or
untrusted-host deployment would require a separately reviewed authoritative store or
cryptographic issuance design.
"""

from __future__ import annotations

import hmac
import json
import secrets
from dataclasses import dataclass, field
from typing import Any

from teo_reference.provider_adapter import ProviderAdapter, execute_provider_once
from teo_reference.schemas import DispatchRecord, ExecutionResult


class DispatchAuthorizationError(RuntimeError):
    """Raised when a host presents an unissued or altered dispatch."""


def canonical_dispatch_bytes(dispatch: DispatchRecord) -> bytes:
    """Canonicalize the complete issued DispatchRecord for exact host-boundary comparison."""
    return json.dumps(
        dispatch.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(slots=True)
class ProcessLocalDispatchAuthority:
    """Research-only registry binding opaque authorization tokens to exact dispatch snapshots."""

    _issued: dict[str, bytes] = field(default_factory=dict)

    def issue(self, dispatch: DispatchRecord) -> str:
        token = secrets.token_urlsafe(32)
        while token in self._issued:
            token = secrets.token_urlsafe(32)
        self._issued[token] = canonical_dispatch_bytes(dispatch)
        return token

    def verify(self, token: str, dispatch: DispatchRecord) -> None:
        expected = self._issued.get(token)
        if expected is None:
            raise DispatchAuthorizationError("dispatch authorization token was not issued")
        presented = canonical_dispatch_bytes(dispatch)
        if not hmac.compare_digest(expected, presented):
            raise DispatchAuthorizationError("dispatch differs from the authority-issued snapshot")


def execute_authorized_provider_once(
    authority: ProcessLocalDispatchAuthority,
    token: str,
    adapter: ProviderAdapter,
    dispatch: DispatchRecord,
    input_payload: dict[str, Any] | None = None,
) -> ExecutionResult:
    """Research wrapper proving provenance can be checked before any adapter call."""
    authority.verify(token, dispatch)
    return execute_provider_once(adapter, dispatch, input_payload)
