#!/usr/bin/env python3
"""Non-normative Host Integration authority-intersection research control.

This module models the narrow boundary described by the Host Integration Contract:
a concrete host-native action may execute only when the already-routed TEO dispatch and
the host's own authority scope both permit that action. The more restrictive control
wins and any explicit host deny wins.

The control is deliberately process-local research. It does not create live authority,
a normative host-integration schema, portable authorization tokens, or a second routing
plane. It assumes dispatch provenance has already been established by the separate
host-integration dispatch-authorization research slice.
"""

from __future__ import annotations

import hmac
import json
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from teo_reference.schemas import DispatchRecord


class AuthorityIntersectionError(RuntimeError):
    """Raised when TEO or host authority does not permit one bound host action."""


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuthorityIntersectionError(f"{name} is required")
    return value.strip()


def _tuple_of_text(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(_text(value, name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise AuthorityIntersectionError(f"{name} cannot contain duplicates")
    return normalized


@dataclass(frozen=True, slots=True)
class TEOExecutionScope:
    """Research snapshot of the currently active TEO live-execution scope."""

    source: str
    task_types: tuple[str, ...]
    risk_levels: tuple[str, ...]

    def __post_init__(self) -> None:
        _text(self.source, "source")
        _tuple_of_text(self.task_types, "task_type")
        _tuple_of_text(self.risk_levels, "risk_level")

    @classmethod
    def from_live_execution_policy(cls, path: Path) -> "TEOExecutionScope":
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise AuthorityIntersectionError("live execution policy must be a mapping")
        active = payload.get("active_scope")
        if not isinstance(active, dict):
            raise AuthorityIntersectionError("live execution policy is missing active_scope")
        task_types = active.get("task_types")
        risk_levels = active.get("risk_levels")
        if not isinstance(task_types, list) or not isinstance(risk_levels, list):
            raise AuthorityIntersectionError("active_scope must declare task_types and risk_levels")
        return cls(
            source=str(path.as_posix()),
            task_types=tuple(str(value) for value in task_types),
            risk_levels=tuple(str(value) for value in risk_levels),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "task_types": list(self.task_types),
            "risk_levels": list(self.risk_levels),
        }


@dataclass(frozen=True, slots=True)
class HostExecutionScope:
    """Research-only host permission boundary for TEO-dispatched execution."""

    scope_id: str
    allowed_task_types: tuple[str, ...]
    allowed_risk_levels: tuple[str, ...]
    allowed_capabilities: tuple[str, ...]
    allowed_provider_families: tuple[str, ...]
    allowed_operations: tuple[str, ...]
    denied_task_types: tuple[str, ...] = ()
    denied_risk_levels: tuple[str, ...] = ()
    denied_capabilities: tuple[str, ...] = ()
    denied_provider_families: tuple[str, ...] = ()
    denied_operations: tuple[str, ...] = ()
    active: bool = True

    def __post_init__(self) -> None:
        _text(self.scope_id, "scope_id")
        for values, name in (
            (self.allowed_task_types, "allowed_task_type"),
            (self.allowed_risk_levels, "allowed_risk_level"),
            (self.allowed_capabilities, "allowed_capability"),
            (self.allowed_provider_families, "allowed_provider_family"),
            (self.allowed_operations, "allowed_operation"),
            (self.denied_task_types, "denied_task_type"),
            (self.denied_risk_levels, "denied_risk_level"),
            (self.denied_capabilities, "denied_capability"),
            (self.denied_provider_families, "denied_provider_family"),
            (self.denied_operations, "denied_operation"),
        ):
            _tuple_of_text(values, name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "allowed_task_types": list(self.allowed_task_types),
            "allowed_risk_levels": list(self.allowed_risk_levels),
            "allowed_capabilities": list(self.allowed_capabilities),
            "allowed_provider_families": list(self.allowed_provider_families),
            "allowed_operations": list(self.allowed_operations),
            "denied_task_types": list(self.denied_task_types),
            "denied_risk_levels": list(self.denied_risk_levels),
            "denied_capabilities": list(self.denied_capabilities),
            "denied_provider_families": list(self.denied_provider_families),
            "denied_operations": list(self.denied_operations),
            "active": self.active,
        }


def canonical_bound_action_bytes(
    dispatch: DispatchRecord,
    capability: str,
    operation: str,
    teo_scope: TEOExecutionScope,
    host_scope: HostExecutionScope,
) -> bytes:
    payload = {
        "dispatch": dispatch.to_dict(),
        "capability": _text(capability, "capability"),
        "operation": _text(operation, "operation"),
        "teo_scope": teo_scope.to_dict(),
        "host_scope": host_scope.to_dict(),
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _host_allows(
    value: str,
    allowed: tuple[str, ...],
    denied: tuple[str, ...],
    surface: str,
) -> None:
    if value in denied:
        raise AuthorityIntersectionError(f"host explicitly denied {surface}: {value}")
    if value not in allowed:
        raise AuthorityIntersectionError(f"host did not authorize {surface}: {value}")


@dataclass(slots=True)
class RestrictiveAuthorityGate:
    """Process-local deny-wins intersection of TEO dispatch authority and host authority."""

    teo_scope: TEOExecutionScope
    host_scope: HostExecutionScope
    _issued: dict[str, bytes] = field(default_factory=dict)

    def replace_host_scope(self, scope: HostExecutionScope) -> None:
        self.host_scope = scope

    def replace_teo_scope(self, scope: TEOExecutionScope) -> None:
        self.teo_scope = scope

    def _check_current_authority(
        self,
        dispatch: DispatchRecord,
        capability: str,
        operation: str,
    ) -> None:
        capability = _text(capability, "capability")
        operation = _text(operation, "operation")

        if dispatch.task_type not in self.teo_scope.task_types:
            raise AuthorityIntersectionError(
                f"TEO active scope does not authorize task_type: {dispatch.task_type}"
            )
        if dispatch.risk_level not in self.teo_scope.risk_levels:
            raise AuthorityIntersectionError(
                f"TEO active scope does not authorize risk_level: {dispatch.risk_level}"
            )
        if capability not in dispatch.required_capabilities:
            raise AuthorityIntersectionError(
                f"TEO dispatch does not authorize capability: {capability}"
            )

        if not self.host_scope.active:
            raise AuthorityIntersectionError("host execution scope is inactive")

        _host_allows(
            dispatch.task_type,
            self.host_scope.allowed_task_types,
            self.host_scope.denied_task_types,
            "task_type",
        )
        _host_allows(
            dispatch.risk_level,
            self.host_scope.allowed_risk_levels,
            self.host_scope.denied_risk_levels,
            "risk_level",
        )
        _host_allows(
            capability,
            self.host_scope.allowed_capabilities,
            self.host_scope.denied_capabilities,
            "capability",
        )
        _host_allows(
            dispatch.selected_implementation.provider_family,
            self.host_scope.allowed_provider_families,
            self.host_scope.denied_provider_families,
            "provider_family",
        )
        _host_allows(
            operation,
            self.host_scope.allowed_operations,
            self.host_scope.denied_operations,
            "operation",
        )

    def authorize(
        self,
        dispatch: DispatchRecord,
        *,
        capability: str,
        operation: str,
    ) -> str:
        """Issue a process-local token only after both TEO and host authority permit the action."""
        self._check_current_authority(dispatch, capability, operation)
        token = secrets.token_urlsafe(32)
        while token in self._issued:
            token = secrets.token_urlsafe(32)
        self._issued[token] = canonical_bound_action_bytes(
            dispatch,
            capability,
            operation,
            self.teo_scope,
            self.host_scope,
        )
        return token

    def verify(
        self,
        token: str,
        dispatch: DispatchRecord,
        *,
        capability: str,
        operation: str,
    ) -> None:
        expected = self._issued.get(token)
        if expected is None:
            raise AuthorityIntersectionError("host action authorization token was not issued")

        self._check_current_authority(dispatch, capability, operation)
        presented = canonical_bound_action_bytes(
            dispatch,
            capability,
            operation,
            self.teo_scope,
            self.host_scope,
        )
        if not hmac.compare_digest(expected, presented):
            raise AuthorityIntersectionError(
                "host action differs from the authority-bound execution scope"
            )


def execute_authorized_host_action(
    gate: RestrictiveAuthorityGate,
    token: str,
    dispatch: DispatchRecord,
    *,
    capability: str,
    operation: str,
    action: Callable[[], Any],
) -> Any:
    """Run one concrete host action only after restrictive authority verification."""
    gate.verify(
        token,
        dispatch,
        capability=capability,
        operation=operation,
    )
    return action()
