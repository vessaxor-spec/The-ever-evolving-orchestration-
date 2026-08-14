from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import threading
from dataclasses import dataclass
from typing import Any, Mapping


class PortfolioAuthorityError(ValueError):
    """Raised when host task-admission or portfolio authority is invalid."""


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
        raise PortfolioAuthorityError(
            f"value is not canonical JSON data: {exc}"
        ) from exc


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PortfolioAuthorityError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_nonnegative_int(value: Any, field_name: str) -> int:
    if type(value) is not int or value < 0:
        raise PortfolioAuthorityError(f"{field_name} must be a non-negative integer")
    return value


def _require_sha256(value: Any, field_name: str) -> str:
    digest = _require_string(value, field_name)
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise PortfolioAuthorityError(
            f"{field_name} must be a lowercase SHA-256 digest"
        )
    return digest


@dataclass(frozen=True, slots=True)
class HostTaskRecord:
    task_id: str
    task_digest: str
    priority: int
    state: str
    revision: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_digest": self.task_digest,
            "priority": self.priority,
            "state": self.state,
            "revision": self.revision,
        }


@dataclass(frozen=True, slots=True)
class TaskAdmissionGrant:
    authorization_token: str
    portfolio_id: str
    admission_id: str
    task_id: str
    task_digest: str
    admission_revision: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorization_token": self.authorization_token,
            "portfolio_id": self.portfolio_id,
            "admission_id": self.admission_id,
            "task_id": self.task_id,
            "task_digest": self.task_digest,
            "admission_revision": self.admission_revision,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TaskAdmissionGrant":
        expected = {
            "authorization_token",
            "portfolio_id",
            "admission_id",
            "task_id",
            "task_digest",
            "admission_revision",
        }
        if set(value) != expected:
            raise PortfolioAuthorityError(
                "task admission grant fields do not match the contract"
            )
        token = _require_sha256(value["authorization_token"], "authorization_token")
        return cls(
            authorization_token=token,
            portfolio_id=_require_string(value["portfolio_id"], "portfolio_id"),
            admission_id=_require_string(value["admission_id"], "admission_id"),
            task_id=_require_string(value["task_id"], "task_id"),
            task_digest=_require_sha256(value["task_digest"], "task_digest"),
            admission_revision=_require_nonnegative_int(
                value["admission_revision"], "admission_revision"
            ),
        )


@dataclass(frozen=True, slots=True)
class TEOAdmissionRequest:
    operation: str
    admission_id: str
    task_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "operation": self.operation,
            "admission_id": self.admission_id,
            "task_id": self.task_id,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TEOAdmissionRequest":
        expected = {"operation", "admission_id", "task_id"}
        if set(value) != expected:
            raise PortfolioAuthorityError(
                "TEO admission request fields do not match the contract"
            )
        operation = _require_string(value["operation"], "operation")
        if operation != "orchestrate_admitted_task":
            raise PortfolioAuthorityError(
                f"unsupported TEO admission operation: {operation}"
            )
        return cls(
            operation=operation,
            admission_id=_require_string(value["admission_id"], "admission_id"),
            task_id=_require_string(value["task_id"], "task_id"),
        )


@dataclass(frozen=True, slots=True)
class AdmittedTaskSession:
    session_id: str
    portfolio_id: str
    admission_id: str
    task_id: str
    task_digest: str
    admission_revision: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "portfolio_id": self.portfolio_id,
            "admission_id": self.admission_id,
            "task_id": self.task_id,
            "task_digest": self.task_digest,
            "admission_revision": self.admission_revision,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "AdmittedTaskSession":
        expected = {
            "session_id",
            "portfolio_id",
            "admission_id",
            "task_id",
            "task_digest",
            "admission_revision",
        }
        if set(value) != expected:
            raise PortfolioAuthorityError(
                "admitted task session fields do not match the contract"
            )
        return cls(
            session_id=_require_string(value["session_id"], "session_id"),
            portfolio_id=_require_string(value["portfolio_id"], "portfolio_id"),
            admission_id=_require_string(value["admission_id"], "admission_id"),
            task_id=_require_string(value["task_id"], "task_id"),
            task_digest=_require_sha256(value["task_digest"], "task_digest"),
            admission_revision=_require_nonnegative_int(
                value["admission_revision"], "admission_revision"
            ),
        )


@dataclass(slots=True)
class _TaskState:
    task_digest: str
    priority: int
    state: str
    revision: int


@dataclass(slots=True)
class _AdmissionState:
    task_id: str
    task_digest: str
    admission_revision: int
    active: bool = True
    claimed: bool = False
    session_id: str | None = None


class HostPortfolioAuthority:
    """Non-normative process-local host portfolio and task-admission authority.

    The host owns queue mutation, prioritization, admission, cancellation, and
    revocation state. TEO receives only a bounded gateway that can claim and
    revalidate one exact host-issued task admission.
    """

    def __init__(self, *, portfolio_id: str = "host-portfolio") -> None:
        self.portfolio_id = _require_string(portfolio_id, "portfolio_id")
        self._secret = secrets.token_bytes(32)
        self._revision = 0
        self._tasks: dict[str, _TaskState] = {}
        self._admissions: dict[str, _AdmissionState] = {}
        self._lock = threading.RLock()

    def _advance_revision(self) -> int:
        self._revision += 1
        return self._revision

    def _task_record(self, task_id: str) -> HostTaskRecord:
        state = self._tasks[task_id]
        return HostTaskRecord(
            task_id=task_id,
            task_digest=state.task_digest,
            priority=state.priority,
            state=state.state,
            revision=state.revision,
        )

    def enqueue_task(
        self, task_payload: Mapping[str, Any], *, priority: int
    ) -> HostTaskRecord:
        if not isinstance(task_payload, Mapping):
            raise PortfolioAuthorityError("task_payload must be a mapping")
        task_id = _require_string(task_payload.get("task_id"), "task_id")
        priority = _require_nonnegative_int(priority, "priority")
        digest = _sha256_json(task_payload)
        with self._lock:
            if task_id in self._tasks:
                raise PortfolioAuthorityError(f"task already exists: {task_id}")
            revision = self._advance_revision()
            self._tasks[task_id] = _TaskState(
                task_digest=digest,
                priority=priority,
                state="queued",
                revision=revision,
            )
            return self._task_record(task_id)

    def reprioritize_task(self, task_id: str, *, priority: int) -> HostTaskRecord:
        task_id = _require_string(task_id, "task_id")
        priority = _require_nonnegative_int(priority, "priority")
        with self._lock:
            state = self._tasks.get(task_id)
            if state is None:
                raise PortfolioAuthorityError(f"unknown task: {task_id}")
            if state.state == "cancelled":
                raise PortfolioAuthorityError("cancelled task cannot be reprioritized")
            state.priority = priority
            state.revision = self._advance_revision()
            return self._task_record(task_id)

    def cancel_task(self, task_id: str) -> HostTaskRecord:
        task_id = _require_string(task_id, "task_id")
        with self._lock:
            state = self._tasks.get(task_id)
            if state is None:
                raise PortfolioAuthorityError(f"unknown task: {task_id}")
            state.state = "cancelled"
            state.revision = self._advance_revision()
            for admission in self._admissions.values():
                if admission.task_id == task_id:
                    admission.active = False
            return self._task_record(task_id)

    def _grant_payload(
        self,
        *,
        admission_id: str,
        task_id: str,
        task_digest: str,
        admission_revision: int,
    ) -> dict[str, Any]:
        return {
            "portfolio_id": self.portfolio_id,
            "admission_id": admission_id,
            "task_id": task_id,
            "task_digest": task_digest,
            "admission_revision": admission_revision,
        }

    def _sign_grant(self, payload: Mapping[str, Any]) -> str:
        return hmac.new(
            self._secret,
            _canonical_json(payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def admit_task(self, task_id: str) -> TaskAdmissionGrant:
        task_id = _require_string(task_id, "task_id")
        with self._lock:
            state = self._tasks.get(task_id)
            if state is None:
                raise PortfolioAuthorityError(f"unknown task: {task_id}")
            if state.state != "queued":
                raise PortfolioAuthorityError(
                    f"task is not eligible for admission from state {state.state}"
                )
            admission_revision = self._advance_revision()
            admission_id = f"admission-{secrets.token_hex(12)}"
            state.state = "admitted"
            state.revision = admission_revision
            self._admissions[admission_id] = _AdmissionState(
                task_id=task_id,
                task_digest=state.task_digest,
                admission_revision=admission_revision,
            )
            payload = self._grant_payload(
                admission_id=admission_id,
                task_id=task_id,
                task_digest=state.task_digest,
                admission_revision=admission_revision,
            )
            return TaskAdmissionGrant(
                authorization_token=self._sign_grant(payload),
                **payload,
            )

    def revoke_admission(self, admission_id: str) -> None:
        admission_id = _require_string(admission_id, "admission_id")
        with self._lock:
            admission = self._admissions.get(admission_id)
            if admission is None:
                raise PortfolioAuthorityError(
                    f"unknown admission: {admission_id}"
                )
            if admission.active:
                admission.active = False
                self._advance_revision()

    def _parse_request(
        self, request: TEOAdmissionRequest | Mapping[str, Any]
    ) -> TEOAdmissionRequest:
        if isinstance(request, TEOAdmissionRequest):
            return request
        if not isinstance(request, Mapping):
            raise PortfolioAuthorityError("TEO admission request must be a mapping")
        return TEOAdmissionRequest.from_dict(request)

    def _parse_grant(
        self, grant: TaskAdmissionGrant | Mapping[str, Any]
    ) -> TaskAdmissionGrant:
        if isinstance(grant, TaskAdmissionGrant):
            return grant
        if not isinstance(grant, Mapping):
            raise PortfolioAuthorityError("task admission grant must be a mapping")
        return TaskAdmissionGrant.from_dict(grant)

    def _parse_session(
        self, session: AdmittedTaskSession | Mapping[str, Any]
    ) -> AdmittedTaskSession:
        if isinstance(session, AdmittedTaskSession):
            return session
        if not isinstance(session, Mapping):
            raise PortfolioAuthorityError("admitted task session must be a mapping")
        return AdmittedTaskSession.from_dict(session)

    def claim_admission(
        self,
        request: TEOAdmissionRequest | Mapping[str, Any],
        grant: TaskAdmissionGrant | Mapping[str, Any],
        task_payload: Mapping[str, Any],
    ) -> AdmittedTaskSession:
        if not isinstance(task_payload, Mapping):
            raise PortfolioAuthorityError("task_payload must be a mapping")
        parsed_request = self._parse_request(request)
        parsed_grant = self._parse_grant(grant)
        task_digest = _sha256_json(task_payload)
        task_id = _require_string(task_payload.get("task_id"), "task_id")
        payload = self._grant_payload(
            admission_id=parsed_grant.admission_id,
            task_id=parsed_grant.task_id,
            task_digest=parsed_grant.task_digest,
            admission_revision=parsed_grant.admission_revision,
        )
        expected_token = self._sign_grant(payload)
        with self._lock:
            if parsed_grant.portfolio_id != self.portfolio_id:
                raise PortfolioAuthorityError("admission belongs to another portfolio")
            if not hmac.compare_digest(
                parsed_grant.authorization_token, expected_token
            ):
                raise PortfolioAuthorityError("host-issued admission signature is invalid")
            if parsed_request.admission_id != parsed_grant.admission_id:
                raise PortfolioAuthorityError("request admission_id does not match grant")
            if parsed_request.task_id != parsed_grant.task_id:
                raise PortfolioAuthorityError("request task_id does not match grant")
            if task_id != parsed_grant.task_id:
                raise PortfolioAuthorityError("task payload identity does not match admission")
            if task_digest != parsed_grant.task_digest:
                raise PortfolioAuthorityError("task payload digest does not match admission")

            admission = self._admissions.get(parsed_grant.admission_id)
            if admission is None:
                raise PortfolioAuthorityError("admission is not known to host authority")
            if not admission.active:
                raise PortfolioAuthorityError("admission has been revoked or cancelled")
            if admission.claimed:
                raise PortfolioAuthorityError("admission has already been claimed")
            if admission.task_id != parsed_grant.task_id:
                raise PortfolioAuthorityError("host admission task identity mismatch")
            if admission.task_digest != parsed_grant.task_digest:
                raise PortfolioAuthorityError("host admission task digest mismatch")
            if admission.admission_revision != parsed_grant.admission_revision:
                raise PortfolioAuthorityError("host admission revision mismatch")

            task_state = self._tasks.get(parsed_grant.task_id)
            if task_state is None or task_state.state != "admitted":
                raise PortfolioAuthorityError("task is not currently admitted by the host")
            if task_state.task_digest != parsed_grant.task_digest:
                raise PortfolioAuthorityError("host task digest no longer matches admission")

            session_id = f"teo-session-{secrets.token_hex(12)}"
            admission.claimed = True
            admission.session_id = session_id
            return AdmittedTaskSession(
                session_id=session_id,
                portfolio_id=self.portfolio_id,
                admission_id=parsed_grant.admission_id,
                task_id=parsed_grant.task_id,
                task_digest=parsed_grant.task_digest,
                admission_revision=parsed_grant.admission_revision,
            )

    def validate_session(
        self,
        session: AdmittedTaskSession | Mapping[str, Any],
        task_payload: Mapping[str, Any],
    ) -> AdmittedTaskSession:
        if not isinstance(task_payload, Mapping):
            raise PortfolioAuthorityError("task_payload must be a mapping")
        parsed_session = self._parse_session(session)
        task_id = _require_string(task_payload.get("task_id"), "task_id")
        task_digest = _sha256_json(task_payload)
        with self._lock:
            if parsed_session.portfolio_id != self.portfolio_id:
                raise PortfolioAuthorityError("session belongs to another portfolio")
            if task_id != parsed_session.task_id:
                raise PortfolioAuthorityError("task payload identity does not match session")
            if task_digest != parsed_session.task_digest:
                raise PortfolioAuthorityError("task payload digest does not match session")
            admission = self._admissions.get(parsed_session.admission_id)
            if admission is None:
                raise PortfolioAuthorityError("session admission is unknown")
            if not admission.active:
                raise PortfolioAuthorityError("session admission has been revoked or cancelled")
            if not admission.claimed:
                raise PortfolioAuthorityError("session admission was never claimed")
            if admission.session_id != parsed_session.session_id:
                raise PortfolioAuthorityError("session identity does not match issued host session")
            if admission.task_id != parsed_session.task_id:
                raise PortfolioAuthorityError("session task identity does not match host admission")
            if admission.task_digest != parsed_session.task_digest:
                raise PortfolioAuthorityError("session task digest does not match host admission")
            if admission.admission_revision != parsed_session.admission_revision:
                raise PortfolioAuthorityError("session admission revision mismatch")
            task_state = self._tasks.get(parsed_session.task_id)
            if task_state is None or task_state.state != "admitted":
                raise PortfolioAuthorityError("task is no longer admitted by the host")
            return parsed_session

    def task_record(self, task_id: str) -> HostTaskRecord:
        task_id = _require_string(task_id, "task_id")
        with self._lock:
            if task_id not in self._tasks:
                raise PortfolioAuthorityError(f"unknown task: {task_id}")
            return self._task_record(task_id)

    def teo_gateway(self) -> "TEOTaskAdmissionGateway":
        return TEOTaskAdmissionGateway(self)


class TEOTaskAdmissionGateway:
    """Conformant TEO-facing surface with no portfolio mutation operations."""

    __slots__ = ("__authority",)

    def __init__(self, authority: HostPortfolioAuthority) -> None:
        if not isinstance(authority, HostPortfolioAuthority):
            raise PortfolioAuthorityError(
                "TEO task admission gateway requires host portfolio authority"
            )
        self.__authority = authority

    def claim(
        self,
        request: TEOAdmissionRequest | Mapping[str, Any],
        grant: TaskAdmissionGrant | Mapping[str, Any],
        task_payload: Mapping[str, Any],
    ) -> AdmittedTaskSession:
        return self.__authority.claim_admission(request, grant, task_payload)

    def revalidate(
        self,
        session: AdmittedTaskSession | Mapping[str, Any],
        task_payload: Mapping[str, Any],
    ) -> AdmittedTaskSession:
        return self.__authority.validate_session(session, task_payload)
