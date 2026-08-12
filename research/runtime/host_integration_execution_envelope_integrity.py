from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

from teo_reference.schemas import DispatchRecord


class ExecutionEnvelopeError(ValueError):
    """Raised when execution would escape an authority-bound action envelope."""


def _text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExecutionEnvelopeError(f"{field_name} must be a non-empty string")
    return value.strip()


def _string_tuple(values, field_name: str) -> tuple[str, ...]:
    normalized = tuple(_text(value, field_name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ExecutionEnvelopeError(f"{field_name} contains duplicate values")
    return normalized


def canonical_json(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ExecutionEnvelopeError(
            f"parameters must be canonical JSON data: {exc}"
        ) from exc


@dataclass(frozen=True, slots=True)
class TEOExecutionScope:
    source: str
    task_types: tuple[str, ...]
    risk_levels: tuple[str, ...]

    @classmethod
    def from_live_execution_policy(cls, path: Path) -> "TEOExecutionScope":
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        active_scope = payload.get("active_scope", {})
        return cls(
            source=str(path),
            task_types=_string_tuple(
                tuple(active_scope.get("task_types", ())), "TEO task type"
            ),
            risk_levels=_string_tuple(
                tuple(active_scope.get("risk_levels", ())), "TEO risk level"
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "task_types": list(self.task_types),
            "risk_levels": list(self.risk_levels),
        }


@dataclass(frozen=True, slots=True)
class TEORetryScope:
    source: str
    task_types: tuple[str, ...]
    risk_levels: tuple[str, ...]
    max_attempts_per_dispatch: int
    retry_same_dispatch: bool
    redispatch_during_retry: bool
    fallback_after_transient_exhaustion: bool

    @classmethod
    def from_retry_policy(cls, path: Path) -> "TEORetryScope":
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        scope = payload.get("scope", {})
        retry = payload.get("retry", {})
        max_attempts = retry.get("max_attempts_per_dispatch")
        if not isinstance(max_attempts, int) or max_attempts < 1:
            raise ExecutionEnvelopeError(
                "TEO retry policy must declare a positive max_attempts_per_dispatch"
            )
        return cls(
            source=str(path),
            task_types=_string_tuple(
                tuple(scope.get("task_types", ())), "retry task type"
            ),
            risk_levels=_string_tuple(
                tuple(scope.get("risk_levels", ())), "retry risk level"
            ),
            max_attempts_per_dispatch=max_attempts,
            retry_same_dispatch=bool(retry.get("retry_same_dispatch")),
            redispatch_during_retry=bool(retry.get("redispatch_during_retry")),
            fallback_after_transient_exhaustion=bool(
                retry.get("fallback_after_transient_exhaustion")
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "task_types": list(self.task_types),
            "risk_levels": list(self.risk_levels),
            "max_attempts_per_dispatch": self.max_attempts_per_dispatch,
            "retry_same_dispatch": self.retry_same_dispatch,
            "redispatch_during_retry": self.redispatch_during_retry,
            "fallback_after_transient_exhaustion": self.fallback_after_transient_exhaustion,
        }


@dataclass(frozen=True, slots=True)
class ResourceTarget:
    kind: str
    identifier: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", _text(self.kind, "resource kind"))
        object.__setattr__(
            self, "identifier", _text(self.identifier, "resource identifier")
        )

    def to_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "identifier": self.identifier}


@dataclass(frozen=True, slots=True)
class TEOActionAuthorization:
    authorization_id: str
    capability: str
    operation: str
    effective_risk: str
    target: ResourceTarget
    parameters_json: str
    side_effect_class: str
    required_prerequisites: tuple[str, ...]
    max_attempts_per_dispatch: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "authorization_id", _text(self.authorization_id, "authorization_id")
        )
        object.__setattr__(self, "capability", _text(self.capability, "capability"))
        object.__setattr__(self, "operation", _text(self.operation, "operation"))
        object.__setattr__(
            self, "effective_risk", _text(self.effective_risk, "effective_risk")
        )
        object.__setattr__(
            self,
            "side_effect_class",
            _text(self.side_effect_class, "side_effect_class"),
        )
        object.__setattr__(
            self,
            "required_prerequisites",
            _string_tuple(self.required_prerequisites, "required prerequisite"),
        )
        if (
            not isinstance(self.max_attempts_per_dispatch, int)
            or self.max_attempts_per_dispatch < 1
        ):
            raise ExecutionEnvelopeError(
                "max_attempts_per_dispatch must be a positive integer"
            )
        try:
            parsed = json.loads(self.parameters_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ExecutionEnvelopeError(
                "parameters_json must contain valid JSON"
            ) from exc
        if not isinstance(parsed, dict):
            raise ExecutionEnvelopeError(
                "parameters_json must encode a JSON object"
            )
        if canonical_json(parsed) != self.parameters_json:
            raise ExecutionEnvelopeError(
                "parameters_json must use canonical JSON serialization"
            )

    @classmethod
    def from_parameters(
        cls,
        *,
        authorization_id: str,
        capability: str,
        operation: str,
        effective_risk: str,
        target: ResourceTarget,
        parameters: Mapping[str, Any],
        side_effect_class: str,
        required_prerequisites: tuple[str, ...] = (),
        max_attempts_per_dispatch: int,
    ) -> "TEOActionAuthorization":
        return cls(
            authorization_id=authorization_id,
            capability=capability,
            operation=operation,
            effective_risk=effective_risk,
            target=target,
            parameters_json=canonical_json(parameters),
            side_effect_class=side_effect_class,
            required_prerequisites=required_prerequisites,
            max_attempts_per_dispatch=max_attempts_per_dispatch,
        )

    @property
    def parameters(self) -> dict[str, Any]:
        value = json.loads(self.parameters_json)
        assert isinstance(value, dict)
        return value

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_id": self.authorization_id,
            "capability": self.capability,
            "operation": self.operation,
            "effective_risk": self.effective_risk,
            "target": self.target.to_dict(),
            "parameters": self.parameters,
            "side_effect_class": self.side_effect_class,
            "required_prerequisites": list(self.required_prerequisites),
            "max_attempts_per_dispatch": self.max_attempts_per_dispatch,
        }


@dataclass(frozen=True, slots=True)
class HostExecutionEnvelopeScope:
    scope_id: str
    allowed_resource_kinds: tuple[str, ...]
    allowed_target_prefixes: tuple[str, ...]
    allowed_side_effect_classes: tuple[str, ...]
    required_prerequisites: tuple[str, ...] = ()
    max_attempts_per_dispatch: int = 1
    active: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "scope_id", _text(self.scope_id, "host scope_id"))
        object.__setattr__(
            self,
            "allowed_resource_kinds",
            _string_tuple(self.allowed_resource_kinds, "allowed resource kind"),
        )
        object.__setattr__(
            self,
            "allowed_target_prefixes",
            _string_tuple(self.allowed_target_prefixes, "allowed target prefix"),
        )
        object.__setattr__(
            self,
            "allowed_side_effect_classes",
            _string_tuple(
                self.allowed_side_effect_classes, "allowed side effect class"
            ),
        )
        object.__setattr__(
            self,
            "required_prerequisites",
            _string_tuple(
                self.required_prerequisites, "host required prerequisite"
            ),
        )
        if (
            not isinstance(self.max_attempts_per_dispatch, int)
            or self.max_attempts_per_dispatch < 1
        ):
            raise ExecutionEnvelopeError(
                "host max_attempts_per_dispatch must be a positive integer"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope_id": self.scope_id,
            "allowed_resource_kinds": list(self.allowed_resource_kinds),
            "allowed_target_prefixes": list(self.allowed_target_prefixes),
            "allowed_side_effect_classes": list(self.allowed_side_effect_classes),
            "required_prerequisites": list(self.required_prerequisites),
            "max_attempts_per_dispatch": self.max_attempts_per_dispatch,
            "active": self.active,
        }


def _teo_action_bytes(
    dispatch: DispatchRecord,
    action: TEOActionAuthorization,
    teo_scope: TEOExecutionScope,
    retry_scope: TEORetryScope,
) -> bytes:
    payload = {
        "dispatch": dispatch.to_dict(),
        "action": action.to_dict(),
        "teo_scope": teo_scope.to_dict(),
        "retry_scope": retry_scope.to_dict(),
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _execution_bytes(
    dispatch: DispatchRecord,
    action: TEOActionAuthorization,
    teo_scope: TEOExecutionScope,
    retry_scope: TEORetryScope,
    host_scope: HostExecutionEnvelopeScope,
    *,
    action_token: str,
    satisfied_prerequisites: tuple[str, ...],
    attempt_number: int,
) -> bytes:
    payload = {
        "dispatch": dispatch.to_dict(),
        "action": action.to_dict(),
        "teo_scope": teo_scope.to_dict(),
        "retry_scope": retry_scope.to_dict(),
        "host_scope": host_scope.to_dict(),
        "action_token": action_token,
        "satisfied_prerequisites": list(satisfied_prerequisites),
        "attempt_number": attempt_number,
    }
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


@dataclass(slots=True)
class ExecutionEnvelopeAuthority:
    """Research-only exact-action authority for one process-local host boundary."""

    teo_scope: TEOExecutionScope
    retry_scope: TEORetryScope
    host_scope: HostExecutionEnvelopeScope
    _actions: dict[str, bytes] = field(default_factory=dict)
    _pending_attempts: dict[str, tuple[int, str]] = field(default_factory=dict)
    _used_attempts: dict[str, set[int]] = field(default_factory=dict)
    _executions: dict[str, bytes] = field(default_factory=dict)

    def replace_teo_scope(self, scope: TEOExecutionScope) -> None:
        self.teo_scope = scope

    def replace_retry_scope(self, scope: TEORetryScope) -> None:
        self.retry_scope = scope

    def replace_host_scope(self, scope: HostExecutionEnvelopeScope) -> None:
        self.host_scope = scope

    def _check_teo_dispatch(self, dispatch: DispatchRecord) -> None:
        if dispatch.task_type not in self.teo_scope.task_types:
            raise ExecutionEnvelopeError(
                f"TEO active scope does not authorize task_type: {dispatch.task_type}"
            )
        if dispatch.risk_level not in self.teo_scope.risk_levels:
            raise ExecutionEnvelopeError(
                f"TEO active scope does not authorize risk_level: {dispatch.risk_level}"
            )
        if dispatch.task_type not in self.retry_scope.task_types:
            raise ExecutionEnvelopeError(
                f"TEO retry scope does not authorize task_type: {dispatch.task_type}"
            )
        if dispatch.risk_level not in self.retry_scope.risk_levels:
            raise ExecutionEnvelopeError(
                f"TEO retry scope does not authorize risk_level: {dispatch.risk_level}"
            )
        if not self.retry_scope.retry_same_dispatch:
            raise ExecutionEnvelopeError(
                "current TEO retry policy does not preserve same-dispatch retry"
            )
        if self.retry_scope.redispatch_during_retry:
            raise ExecutionEnvelopeError(
                "current TEO retry policy permits redispatch during retry"
            )
        if self.retry_scope.fallback_after_transient_exhaustion:
            raise ExecutionEnvelopeError(
                "current TEO retry policy permits fallback after transient exhaustion"
            )

    def issue_teo_action(
        self,
        dispatch: DispatchRecord,
        *,
        authorization_id: str,
        capability: str,
        operation: str,
        effective_risk: str,
        target: ResourceTarget,
        parameters: Mapping[str, Any],
        side_effect_class: str,
        required_prerequisites: tuple[str, ...] = (),
        max_attempts_per_dispatch: int,
    ) -> tuple[str, TEOActionAuthorization]:
        self._check_teo_dispatch(dispatch)
        action = TEOActionAuthorization.from_parameters(
            authorization_id=authorization_id,
            capability=capability,
            operation=operation,
            effective_risk=effective_risk,
            target=target,
            parameters=parameters,
            side_effect_class=side_effect_class,
            required_prerequisites=required_prerequisites,
            max_attempts_per_dispatch=max_attempts_per_dispatch,
        )
        if action.capability not in dispatch.required_capabilities:
            raise ExecutionEnvelopeError(
                f"TEO dispatch does not authorize capability: {action.capability}"
            )
        if action.effective_risk != dispatch.risk_level:
            raise ExecutionEnvelopeError(
                "action effective risk must exactly match the dispatch effective risk"
            )
        if action.max_attempts_per_dispatch > self.retry_scope.max_attempts_per_dispatch:
            raise ExecutionEnvelopeError(
                "TEO action authorization exceeds current retry-policy attempt budget"
            )
        token = secrets.token_urlsafe(32)
        while token in self._actions:
            token = secrets.token_urlsafe(32)
        self._actions[token] = _teo_action_bytes(
            dispatch, action, self.teo_scope, self.retry_scope
        )
        self._used_attempts[token] = set()
        return token, action

    def _verify_teo_action(
        self,
        action_token: str,
        dispatch: DispatchRecord,
        action: TEOActionAuthorization,
    ) -> None:
        expected = self._actions.get(action_token)
        if expected is None:
            raise ExecutionEnvelopeError("TEO action token was not issued")
        self._check_teo_dispatch(dispatch)
        current = _teo_action_bytes(
            dispatch, action, self.teo_scope, self.retry_scope
        )
        if not secrets.compare_digest(expected, current):
            raise ExecutionEnvelopeError(
                "TEO action no longer matches the authority-issued snapshot"
            )

    def _effective_attempt_limit(self, action: TEOActionAuthorization) -> int:
        return min(
            action.max_attempts_per_dispatch,
            self.retry_scope.max_attempts_per_dispatch,
            self.host_scope.max_attempts_per_dispatch,
        )

    def authorize_host_execution(
        self,
        action_token: str,
        dispatch: DispatchRecord,
        action: TEOActionAuthorization,
        *,
        satisfied_prerequisites: tuple[str, ...],
        attempt_number: int,
    ) -> str:
        self._verify_teo_action(action_token, dispatch, action)
        if not self.host_scope.active:
            raise ExecutionEnvelopeError(
                "host execution envelope scope is inactive"
            )
        if action.target.kind not in self.host_scope.allowed_resource_kinds:
            raise ExecutionEnvelopeError(
                f"host did not authorize resource kind: {action.target.kind}"
            )
        if not any(
            action.target.identifier.startswith(prefix)
            for prefix in self.host_scope.allowed_target_prefixes
        ):
            raise ExecutionEnvelopeError(
                f"host did not authorize target: {action.target.identifier}"
            )
        if action.side_effect_class not in self.host_scope.allowed_side_effect_classes:
            raise ExecutionEnvelopeError(
                "host did not authorize side effect class: "
                f"{action.side_effect_class}"
            )

        prerequisites = _string_tuple(
            satisfied_prerequisites, "satisfied prerequisite"
        )
        required = set(action.required_prerequisites) | set(
            self.host_scope.required_prerequisites
        )
        missing = sorted(required - set(prerequisites))
        if missing:
            raise ExecutionEnvelopeError(
                "required prerequisites are not satisfied: " + ", ".join(missing)
            )

        if not isinstance(attempt_number, int) or attempt_number < 1:
            raise ExecutionEnvelopeError(
                "attempt_number must be a positive integer"
            )
        attempt_limit = self._effective_attempt_limit(action)
        if attempt_number > attempt_limit:
            raise ExecutionEnvelopeError(
                f"attempt {attempt_number} exceeds effective attempt budget "
                f"{attempt_limit}"
            )

        used = self._used_attempts.setdefault(action_token, set())
        expected_attempt = len(used) + 1
        if attempt_number != expected_attempt:
            raise ExecutionEnvelopeError(
                f"attempt sequence must continue at {expected_attempt}"
            )
        if action_token in self._pending_attempts:
            raise ExecutionEnvelopeError(
                "a host execution attempt is already pending for this action"
            )

        execution_token = secrets.token_urlsafe(32)
        while execution_token in self._executions:
            execution_token = secrets.token_urlsafe(32)
        self._executions[execution_token] = _execution_bytes(
            dispatch,
            action,
            self.teo_scope,
            self.retry_scope,
            self.host_scope,
            action_token=action_token,
            satisfied_prerequisites=prerequisites,
            attempt_number=attempt_number,
        )
        self._pending_attempts[action_token] = (attempt_number, execution_token)
        return execution_token

    def verify_host_execution(
        self,
        execution_token: str,
        action_token: str,
        dispatch: DispatchRecord,
        action: TEOActionAuthorization,
        *,
        satisfied_prerequisites: tuple[str, ...],
        attempt_number: int,
    ) -> None:
        expected = self._executions.get(execution_token)
        if expected is None:
            raise ExecutionEnvelopeError(
                "host execution token was not issued"
            )
        self._verify_teo_action(action_token, dispatch, action)
        prerequisites = _string_tuple(
            satisfied_prerequisites, "satisfied prerequisite"
        )
        current = _execution_bytes(
            dispatch,
            action,
            self.teo_scope,
            self.retry_scope,
            self.host_scope,
            action_token=action_token,
            satisfied_prerequisites=prerequisites,
            attempt_number=attempt_number,
        )
        if not secrets.compare_digest(expected, current):
            raise ExecutionEnvelopeError(
                "host execution no longer matches the authorized envelope"
            )
        if self._pending_attempts.get(action_token) != (
            attempt_number,
            execution_token,
        ):
            raise ExecutionEnvelopeError(
                "host execution token is not the pending attempt for this action"
            )

    def consume_host_execution(
        self,
        execution_token: str,
        action_token: str,
        dispatch: DispatchRecord,
        action: TEOActionAuthorization,
        *,
        satisfied_prerequisites: tuple[str, ...],
        attempt_number: int,
    ) -> None:
        self.verify_host_execution(
            execution_token,
            action_token,
            dispatch,
            action,
            satisfied_prerequisites=satisfied_prerequisites,
            attempt_number=attempt_number,
        )
        del self._executions[execution_token]
        del self._pending_attempts[action_token]
        self._used_attempts.setdefault(action_token, set()).add(attempt_number)


def execute_authorized_action(
    authority: ExecutionEnvelopeAuthority,
    execution_token: str,
    action_token: str,
    dispatch: DispatchRecord,
    action_authorization: TEOActionAuthorization,
    *,
    satisfied_prerequisites: tuple[str, ...],
    attempt_number: int,
    action,
):
    authority.consume_host_execution(
        execution_token,
        action_token,
        dispatch,
        action_authorization,
        satisfied_prerequisites=satisfied_prerequisites,
        attempt_number=attempt_number,
    )
    return action()
