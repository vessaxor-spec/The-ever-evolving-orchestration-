from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import threading
from dataclasses import dataclass
from typing import Any, Mapping

ENTRY_KINDS = frozenset({"specialist_spawn", "teo_reentry", "recovery_reentry"})


class RecursionAdmissionError(ValueError):
    """Raised when process-local orchestration recursion authority is invalid or exceeded."""


def _canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise RecursionAdmissionError(f"value is not canonical JSON data: {exc}") from exc


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecursionAdmissionError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_nonnegative_int(value: Any, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise RecursionAdmissionError(f"{field_name} must be a non-negative integer")
    return value


@dataclass(frozen=True, slots=True)
class RecursionLimits:
    max_reentry_depth: int
    max_descendants: int
    max_specialist_spawns: int
    max_active_branches: int
    max_recovery_generations: int

    def __post_init__(self) -> None:
        for field_name in (
            "max_reentry_depth",
            "max_descendants",
            "max_specialist_spawns",
            "max_active_branches",
            "max_recovery_generations",
        ):
            value = getattr(self, field_name)
            if type(value) is not int or value < 0:
                raise RecursionAdmissionError(
                    f"{field_name} must be a non-negative integer"
                )
        if self.max_active_branches < 1:
            raise RecursionAdmissionError("max_active_branches must be at least 1")
        if self.max_specialist_spawns > self.max_descendants:
            raise RecursionAdmissionError(
                "max_specialist_spawns cannot exceed max_descendants"
            )

    def to_dict(self) -> dict[str, int]:
        return {
            "max_reentry_depth": self.max_reentry_depth,
            "max_descendants": self.max_descendants,
            "max_specialist_spawns": self.max_specialist_spawns,
            "max_active_branches": self.max_active_branches,
            "max_recovery_generations": self.max_recovery_generations,
        }


@dataclass(frozen=True, slots=True)
class RecursionLease:
    lease_id: str
    root_id: str
    dispatch_id: str
    task_id: str
    parent_lease_id: str | None
    entry_kind: str
    request_id: str
    depth: int
    recovery_generation: int
    dispatch_digest: str
    limits_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "root_id": self.root_id,
            "dispatch_id": self.dispatch_id,
            "task_id": self.task_id,
            "parent_lease_id": self.parent_lease_id,
            "entry_kind": self.entry_kind,
            "request_id": self.request_id,
            "depth": self.depth,
            "recovery_generation": self.recovery_generation,
            "dispatch_digest": self.dispatch_digest,
            "limits_digest": self.limits_digest,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RecursionLease":
        expected = {
            "lease_id",
            "root_id",
            "dispatch_id",
            "task_id",
            "parent_lease_id",
            "entry_kind",
            "request_id",
            "depth",
            "recovery_generation",
            "dispatch_digest",
            "limits_digest",
        }
        if set(value) != expected:
            raise RecursionAdmissionError("recursion lease fields do not match the contract")
        parent = value["parent_lease_id"]
        if parent is not None:
            parent = _require_string(parent, "parent_lease_id")
        entry_kind = _require_string(value["entry_kind"], "entry_kind")
        if entry_kind != "root" and entry_kind not in ENTRY_KINDS:
            raise RecursionAdmissionError(f"unsupported entry_kind: {entry_kind}")
        dispatch_digest = _require_string(value["dispatch_digest"], "dispatch_digest")
        if len(dispatch_digest) != 64 or any(c not in "0123456789abcdef" for c in dispatch_digest):
            raise RecursionAdmissionError("dispatch_digest must be a lowercase SHA-256 digest")
        limits_digest = _require_string(value["limits_digest"], "limits_digest")
        if len(limits_digest) != 64 or any(c not in "0123456789abcdef" for c in limits_digest):
            raise RecursionAdmissionError("limits_digest must be a lowercase SHA-256 digest")
        return cls(
            lease_id=_require_string(value["lease_id"], "lease_id"),
            root_id=_require_string(value["root_id"], "root_id"),
            dispatch_id=_require_string(value["dispatch_id"], "dispatch_id"),
            task_id=_require_string(value["task_id"], "task_id"),
            parent_lease_id=parent,
            entry_kind=entry_kind,
            request_id=_require_string(value["request_id"], "request_id"),
            depth=_require_nonnegative_int(value["depth"], "depth"),
            recovery_generation=_require_nonnegative_int(
                value["recovery_generation"], "recovery_generation"
            ),
            dispatch_digest=dispatch_digest,
            limits_digest=limits_digest,
        )


@dataclass(frozen=True, slots=True)
class RecursionEntryAuthorization:
    authorization_token: str
    root_id: str
    parent_lease_id: str
    dispatch_id: str
    task_id: str
    request_id: str
    entry_kind: str
    depth: int
    recovery_generation: int
    state_revision: int
    dispatch_digest: str
    limits_digest: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_token": self.authorization_token,
            "root_id": self.root_id,
            "parent_lease_id": self.parent_lease_id,
            "dispatch_id": self.dispatch_id,
            "task_id": self.task_id,
            "request_id": self.request_id,
            "entry_kind": self.entry_kind,
            "depth": self.depth,
            "recovery_generation": self.recovery_generation,
            "state_revision": self.state_revision,
            "dispatch_digest": self.dispatch_digest,
            "limits_digest": self.limits_digest,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RecursionEntryAuthorization":
        expected = {
            "authorization_token",
            "root_id",
            "parent_lease_id",
            "dispatch_id",
            "task_id",
            "request_id",
            "entry_kind",
            "depth",
            "recovery_generation",
            "state_revision",
            "dispatch_digest",
            "limits_digest",
        }
        if set(value) != expected:
            raise RecursionAdmissionError(
                "recursion authorization fields do not match the contract"
            )
        kind = _require_string(value["entry_kind"], "entry_kind")
        if kind not in ENTRY_KINDS:
            raise RecursionAdmissionError(f"unsupported entry_kind: {kind}")
        dispatch_digest = _require_string(value["dispatch_digest"], "dispatch_digest")
        if len(dispatch_digest) != 64 or any(c not in "0123456789abcdef" for c in dispatch_digest):
            raise RecursionAdmissionError("dispatch_digest must be a lowercase SHA-256 digest")
        digest = _require_string(value["limits_digest"], "limits_digest")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise RecursionAdmissionError("limits_digest must be a lowercase SHA-256 digest")
        return cls(
            authorization_token=_require_string(
                value["authorization_token"], "authorization_token"
            ),
            root_id=_require_string(value["root_id"], "root_id"),
            parent_lease_id=_require_string(
                value["parent_lease_id"], "parent_lease_id"
            ),
            dispatch_id=_require_string(value["dispatch_id"], "dispatch_id"),
            task_id=_require_string(value["task_id"], "task_id"),
            request_id=_require_string(value["request_id"], "request_id"),
            entry_kind=kind,
            depth=_require_nonnegative_int(value["depth"], "depth"),
            recovery_generation=_require_nonnegative_int(
                value["recovery_generation"], "recovery_generation"
            ),
            state_revision=_require_nonnegative_int(
                value["state_revision"], "state_revision"
            ),
            dispatch_digest=dispatch_digest,
            limits_digest=digest,
        )


@dataclass(slots=True)
class _RootState:
    root_lease_id: str
    dispatch_digest: str
    limits: RecursionLimits
    limits_digest: str
    revision: int = 0
    descendants_claimed: int = 0
    specialist_spawns_claimed: int = 0
    active_descendants: int = 0


class ProcessLocalRecursionAuthority:
    """Non-normative process-local recursion admission authority.

    Mutable budget state remains inside this authority. Host-visible leases and
    authorizations are evidence-bearing claims only and cannot reset counters.
    """

    def __init__(self) -> None:
        self._roots_by_id: dict[str, _RootState] = {}
        self._root_id_by_dispatch_id: dict[str, str] = {}
        self._leases: dict[str, RecursionLease] = {}
        self._active_lease_ids: set[str] = set()
        self._authorization_secret = secrets.token_bytes(32)
        self._claimed_authorizations: set[str] = set()
        self._used_request_ids: dict[str, set[str]] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _dispatch_identity(dispatch: Any) -> tuple[str, str, str]:
        dispatch_id = _require_string(getattr(dispatch, "dispatch_id", None), "dispatch_id")
        task_id = _require_string(getattr(dispatch, "task_id", None), "task_id")
        to_dict = getattr(dispatch, "to_dict", None)
        if not callable(to_dict):
            raise RecursionAdmissionError("dispatch must expose to_dict()")
        digest = hashlib.sha256(_canonical_json(to_dict()).encode("utf-8")).hexdigest()
        return dispatch_id, task_id, digest

    @staticmethod
    def _limits_digest(limits: RecursionLimits) -> str:
        return hashlib.sha256(_canonical_json(limits.to_dict()).encode("utf-8")).hexdigest()

    def begin_root(self, dispatch: Any, limits: RecursionLimits) -> RecursionLease:
        dispatch_id, task_id, dispatch_digest = self._dispatch_identity(dispatch)
        limits_digest = self._limits_digest(limits)
        with self._lock:
            if dispatch_id in self._root_id_by_dispatch_id:
                raise RecursionAdmissionError(
                    "a recursion root already exists for this dispatch"
                )
            root_id = secrets.token_urlsafe(24)
            lease_id = secrets.token_urlsafe(24)
            lease = RecursionLease(
                lease_id=lease_id,
                root_id=root_id,
                dispatch_id=dispatch_id,
                task_id=task_id,
                parent_lease_id=None,
                entry_kind="root",
                request_id=f"root:{dispatch_id}",
                depth=0,
                recovery_generation=0,
                dispatch_digest=dispatch_digest,
                limits_digest=limits_digest,
            )
            self._roots_by_id[root_id] = _RootState(
                root_lease_id=lease_id,
                dispatch_digest=dispatch_digest,
                limits=limits,
                limits_digest=limits_digest,
            )
            self._root_id_by_dispatch_id[dispatch_id] = root_id
            self._leases[lease_id] = lease
            self._active_lease_ids.add(lease_id)
            self._used_request_ids[root_id] = {lease.request_id}
            return lease

    def _coerce_lease(self, lease: RecursionLease | Mapping[str, Any]) -> RecursionLease:
        if isinstance(lease, RecursionLease):
            return lease
        if isinstance(lease, Mapping):
            return RecursionLease.from_dict(lease)
        raise RecursionAdmissionError("lease must be a RecursionLease or mapping")

    def _coerce_authorization(
        self, authorization: RecursionEntryAuthorization | Mapping[str, Any]
    ) -> RecursionEntryAuthorization:
        if isinstance(authorization, RecursionEntryAuthorization):
            return authorization
        if isinstance(authorization, Mapping):
            return RecursionEntryAuthorization.from_dict(authorization)
        raise RecursionAdmissionError(
            "authorization must be a RecursionEntryAuthorization or mapping"
        )

    def _validate_lease(self, lease: RecursionLease | Mapping[str, Any]) -> tuple[RecursionLease, _RootState]:
        supplied = self._coerce_lease(lease)
        registered = self._leases.get(supplied.lease_id)
        if registered is None or registered != supplied:
            raise RecursionAdmissionError(
                "lease does not match a TEO-side recursion authority snapshot"
            )
        if supplied.lease_id not in self._active_lease_ids:
            raise RecursionAdmissionError("lease is not active")
        root = self._roots_by_id.get(supplied.root_id)
        if root is None or supplied.limits_digest != root.limits_digest:
            raise RecursionAdmissionError("lease is not bound to the active root budget")
        if supplied.dispatch_digest != root.dispatch_digest:
            raise RecursionAdmissionError("lease is not bound to the root dispatch snapshot")
        return supplied, root

    @staticmethod
    def _next_claim(parent: RecursionLease, entry_kind: str) -> tuple[int, int]:
        if entry_kind not in ENTRY_KINDS:
            raise RecursionAdmissionError(f"unsupported entry_kind: {entry_kind}")
        depth = parent.depth + 1
        recovery_generation = parent.recovery_generation + (
            1 if entry_kind == "recovery_reentry" else 0
        )
        return depth, recovery_generation

    @staticmethod
    def _validate_static_limits(
        root: _RootState,
        *,
        entry_kind: str,
        depth: int,
        recovery_generation: int,
    ) -> None:
        limits = root.limits
        if depth > limits.max_reentry_depth:
            raise RecursionAdmissionError("maximum TEO re-entry depth exceeded")
        if recovery_generation > limits.max_recovery_generations:
            raise RecursionAdmissionError("maximum recovery generation exceeded")
        if root.descendants_claimed >= limits.max_descendants:
            raise RecursionAdmissionError("maximum descendant admission budget exhausted")
        if (
            entry_kind == "specialist_spawn"
            and root.specialist_spawns_claimed >= limits.max_specialist_spawns
        ):
            raise RecursionAdmissionError("maximum specialist spawn budget exhausted")
        if root.active_descendants >= limits.max_active_branches:
            raise RecursionAdmissionError("maximum active branch budget exhausted")

    def _sign_authorization_fields(
        self,
        *,
        root_id: str,
        parent_lease_id: str,
        dispatch_id: str,
        task_id: str,
        request_id: str,
        entry_kind: str,
        depth: int,
        recovery_generation: int,
        state_revision: int,
        dispatch_digest: str,
        limits_digest: str,
    ) -> str:
        payload = {
            "root_id": root_id,
            "parent_lease_id": parent_lease_id,
            "dispatch_id": dispatch_id,
            "task_id": task_id,
            "request_id": request_id,
            "entry_kind": entry_kind,
            "depth": depth,
            "recovery_generation": recovery_generation,
            "state_revision": state_revision,
            "dispatch_digest": dispatch_digest,
            "limits_digest": limits_digest,
        }
        return hmac.new(
            self._authorization_secret,
            _canonical_json(payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def authorize_descendant(
        self,
        parent_lease: RecursionLease | Mapping[str, Any],
        *,
        entry_kind: str,
        request_id: str,
    ) -> RecursionEntryAuthorization:
        request_id = _require_string(request_id, "request_id")
        entry_kind = _require_string(entry_kind, "entry_kind")
        with self._lock:
            parent, root = self._validate_lease(parent_lease)
            if request_id in self._used_request_ids[parent.root_id]:
                raise RecursionAdmissionError(
                    "request_id has already consumed recursion admission"
                )
            depth, recovery_generation = self._next_claim(parent, entry_kind)
            self._validate_static_limits(
                root,
                entry_kind=entry_kind,
                depth=depth,
                recovery_generation=recovery_generation,
            )
            authorization_token = self._sign_authorization_fields(
                root_id=parent.root_id,
                parent_lease_id=parent.lease_id,
                dispatch_id=parent.dispatch_id,
                task_id=parent.task_id,
                request_id=request_id,
                entry_kind=entry_kind,
                depth=depth,
                recovery_generation=recovery_generation,
                state_revision=root.revision,
                dispatch_digest=root.dispatch_digest,
                limits_digest=root.limits_digest,
            )
            return RecursionEntryAuthorization(
                authorization_token=authorization_token,
                root_id=parent.root_id,
                parent_lease_id=parent.lease_id,
                dispatch_id=parent.dispatch_id,
                task_id=parent.task_id,
                request_id=request_id,
                entry_kind=entry_kind,
                depth=depth,
                recovery_generation=recovery_generation,
                state_revision=root.revision,
                dispatch_digest=root.dispatch_digest,
                limits_digest=root.limits_digest,
            )

    def claim_descendant(
        self,
        authorization: RecursionEntryAuthorization | Mapping[str, Any],
        parent_lease: RecursionLease | Mapping[str, Any],
    ) -> RecursionLease:
        with self._lock:
            supplied = self._coerce_authorization(authorization)
            expected_token = self._sign_authorization_fields(
                root_id=supplied.root_id,
                parent_lease_id=supplied.parent_lease_id,
                dispatch_id=supplied.dispatch_id,
                task_id=supplied.task_id,
                request_id=supplied.request_id,
                entry_kind=supplied.entry_kind,
                depth=supplied.depth,
                recovery_generation=supplied.recovery_generation,
                state_revision=supplied.state_revision,
                dispatch_digest=supplied.dispatch_digest,
                limits_digest=supplied.limits_digest,
            )
            if not hmac.compare_digest(supplied.authorization_token, expected_token):
                raise RecursionAdmissionError(
                    "authorization does not match a TEO-side recursion admission snapshot"
                )
            if supplied.authorization_token in self._claimed_authorizations:
                raise RecursionAdmissionError("recursion authorization has already been claimed")
            parent, root = self._validate_lease(parent_lease)
            if supplied.root_id != parent.root_id or supplied.parent_lease_id != parent.lease_id:
                raise RecursionAdmissionError(
                    "authorization is not bound to the supplied parent lineage"
                )
            if supplied.dispatch_id != parent.dispatch_id or supplied.task_id != parent.task_id:
                raise RecursionAdmissionError(
                    "authorization is not bound to the root dispatch identity"
                )
            if supplied.limits_digest != root.limits_digest:
                raise RecursionAdmissionError(
                    "authorization is not bound to the active root budget"
                )
            if supplied.dispatch_digest != root.dispatch_digest:
                raise RecursionAdmissionError(
                    "authorization is not bound to the root dispatch snapshot"
                )
            if supplied.state_revision != root.revision:
                raise RecursionAdmissionError(
                    "authorization is stale relative to current recursion budget state"
                )
            expected_depth, expected_recovery = self._next_claim(parent, supplied.entry_kind)
            if (
                supplied.depth != expected_depth
                or supplied.recovery_generation != expected_recovery
            ):
                raise RecursionAdmissionError(
                    "authorization lineage counters do not match the parent"
                )
            if supplied.request_id in self._used_request_ids[parent.root_id]:
                raise RecursionAdmissionError(
                    "request_id has already consumed recursion admission"
                )
            self._validate_static_limits(
                root,
                entry_kind=supplied.entry_kind,
                depth=supplied.depth,
                recovery_generation=supplied.recovery_generation,
            )

            lease = RecursionLease(
                lease_id=secrets.token_urlsafe(24),
                root_id=parent.root_id,
                dispatch_id=parent.dispatch_id,
                task_id=parent.task_id,
                parent_lease_id=parent.lease_id,
                entry_kind=supplied.entry_kind,
                request_id=supplied.request_id,
                depth=supplied.depth,
                recovery_generation=supplied.recovery_generation,
                dispatch_digest=root.dispatch_digest,
                limits_digest=root.limits_digest,
            )
            self._claimed_authorizations.add(supplied.authorization_token)
            self._used_request_ids[parent.root_id].add(supplied.request_id)
            self._leases[lease.lease_id] = lease
            self._active_lease_ids.add(lease.lease_id)
            root.descendants_claimed += 1
            if supplied.entry_kind == "specialist_spawn":
                root.specialist_spawns_claimed += 1
            root.active_descendants += 1
            root.revision += 1
            return lease

    def release(self, lease: RecursionLease | Mapping[str, Any]) -> None:
        with self._lock:
            supplied, root = self._validate_lease(lease)
            if supplied.parent_lease_id is None:
                raise RecursionAdmissionError(
                    "root lease lifetime is owned by the TEO-side orchestration session"
                )
            if any(
                candidate.parent_lease_id == supplied.lease_id
                and candidate.lease_id in self._active_lease_ids
                for candidate in self._leases.values()
            ):
                raise RecursionAdmissionError(
                    "cannot release a recursion lease while an active child remains"
                )
            self._active_lease_ids.remove(supplied.lease_id)
            root.active_descendants -= 1
            root.revision += 1

    def snapshot(self, root_lease: RecursionLease | Mapping[str, Any]) -> dict[str, Any]:
        with self._lock:
            root_lease_obj, root = self._validate_lease(root_lease)
            if root_lease_obj.parent_lease_id is not None:
                raise RecursionAdmissionError("snapshot requires the root lease")
            return {
                "root_id": root_lease_obj.root_id,
                "dispatch_id": root_lease_obj.dispatch_id,
                "task_id": root_lease_obj.task_id,
                "dispatch_digest": root.dispatch_digest,
                "limits": root.limits.to_dict(),
                "limits_digest": root.limits_digest,
                "revision": root.revision,
                "descendants_claimed": root.descendants_claimed,
                "specialist_spawns_claimed": root.specialist_spawns_claimed,
                "active_descendants": root.active_descendants,
            }
