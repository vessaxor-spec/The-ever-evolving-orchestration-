from __future__ import annotations

import json
import runpy
import secrets
import socket
import socketserver
import threading
from pathlib import Path
from typing import Any, Mapping


_BASE = runpy.run_path(
    str(Path(__file__).with_name("host_integration_execution_envelope_integrity.py"))
)
ExecutionEnvelopeAuthority = _BASE["ExecutionEnvelopeAuthority"]
ExecutionEnvelopeError = _BASE["ExecutionEnvelopeError"]
TEOActionAuthorization = _BASE["TEOActionAuthorization"]

PROTOCOL_VERSION = "research-0"
MAX_REQUEST_BYTES = 64 * 1024


class CrossProcessAuthorityError(ValueError):
    """Raised when the research host-authority protocol is malformed or unbound."""


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
        raise CrossProcessAuthorityError(
            f"protocol value is not canonical JSON data: {exc}"
        ) from exc


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CrossProcessAuthorityError(f"{field_name} must be a non-empty string")
    return value.strip()


def _require_attempt_number(value: Any) -> int:
    if type(value) is not int or value < 1:
        raise CrossProcessAuthorityError(
            "attempt_number must be a positive integer"
        )
    return value


def _require_prerequisites(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise CrossProcessAuthorityError(
            "satisfied_prerequisites must be a JSON array"
        )
    normalized = tuple(
        _require_string(item, "satisfied prerequisite") for item in value
    )
    if len(set(normalized)) != len(normalized):
        raise CrossProcessAuthorityError(
            "satisfied_prerequisites contains duplicate values"
        )
    return normalized


def _require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise CrossProcessAuthorityError(f"{field_name} must be a JSON object")
    return value


def _require_exact_fields(request: Mapping[str, Any], operation: str) -> None:
    fields = {
        "version",
        "session_id",
        "operation",
        "action_token",
        "dispatch",
        "action",
        "satisfied_prerequisites",
        "attempt_number",
    }
    if operation == "claim":
        fields.add("execution_token")
    actual = set(request)
    if actual != fields:
        missing = sorted(fields - actual)
        unexpected = sorted(actual - fields)
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if unexpected:
            details.append("unexpected=" + ",".join(unexpected))
        raise CrossProcessAuthorityError(
            "protocol fields do not match the operation contract"
            + (": " + "; ".join(details) if details else "")
        )


class HostAuthorityGateway:
    """Brokered research authority retained outside the host execution process.

    The gateway exposes no action-issuance operation. It receives one action token that
    was already issued by the TEO-side ExecutionEnvelopeAuthority, then allows a host
    process only to request exact execution authorization and atomically claim the
    resulting single-use execution token.
    """

    def __init__(
        self,
        authority: ExecutionEnvelopeAuthority,
        *,
        action_token: str,
        dispatch: Any,
        action: TEOActionAuthorization,
    ) -> None:
        self.authority = authority
        self.action_token = _require_string(action_token, "action_token")
        self.dispatch = dispatch
        self.action = action
        self.session_id = secrets.token_urlsafe(24)
        self._dispatch_json = _canonical_json(dispatch.to_dict())
        self._action_json = _canonical_json(action.to_dict())
        self._lock = threading.Lock()

    def descriptor(self) -> dict[str, Any]:
        return {
            "version": PROTOCOL_VERSION,
            "session_id": self.session_id,
            "action_token": self.action_token,
            "dispatch": self.dispatch.to_dict(),
            "action": self.action.to_dict(),
        }

    def _validate_common(
        self, request: Mapping[str, Any]
    ) -> tuple[tuple[str, ...], int]:
        version = _require_string(request.get("version"), "version")
        if version != PROTOCOL_VERSION:
            raise CrossProcessAuthorityError(
                f"unsupported protocol version: {version}"
            )
        session_id = _require_string(request.get("session_id"), "session_id")
        if not secrets.compare_digest(session_id, self.session_id):
            raise CrossProcessAuthorityError(
                "host request is not bound to this authority session"
            )
        action_token = _require_string(
            request.get("action_token"), "action_token"
        )
        if not secrets.compare_digest(action_token, self.action_token):
            raise CrossProcessAuthorityError(
                "host request does not carry the authority-issued action token"
            )
        dispatch = _require_mapping(request.get("dispatch"), "dispatch")
        if not secrets.compare_digest(
            _canonical_json(dispatch), self._dispatch_json
        ):
            raise CrossProcessAuthorityError(
                "host dispatch does not match the TEO-side authority snapshot"
            )
        action = _require_mapping(request.get("action"), "action")
        if not secrets.compare_digest(_canonical_json(action), self._action_json):
            raise CrossProcessAuthorityError(
                "host action does not match the TEO-side authority snapshot"
            )
        prerequisites = _require_prerequisites(
            request.get("satisfied_prerequisites")
        )
        attempt_number = _require_attempt_number(request.get("attempt_number"))
        return prerequisites, attempt_number

    def handle(self, request: Mapping[str, Any]) -> dict[str, Any]:
        operation = _require_string(request.get("operation"), "operation")
        if operation not in {"authorize", "claim"}:
            raise CrossProcessAuthorityError(
                f"host operation is not exposed by this authority gateway: {operation}"
            )
        _require_exact_fields(request, operation)

        with self._lock:
            prerequisites, attempt_number = self._validate_common(request)
            if operation == "authorize":
                execution_token = self.authority.authorize_host_execution(
                    self.action_token,
                    self.dispatch,
                    self.action,
                    satisfied_prerequisites=prerequisites,
                    attempt_number=attempt_number,
                )
                return {
                    "ok": True,
                    "version": PROTOCOL_VERSION,
                    "session_id": self.session_id,
                    "operation": "authorize",
                    "execution_token": execution_token,
                    "attempt_number": attempt_number,
                }

            execution_token = _require_string(
                request.get("execution_token"), "execution_token"
            )
            self.authority.consume_host_execution(
                execution_token,
                self.action_token,
                self.dispatch,
                self.action,
                satisfied_prerequisites=prerequisites,
                attempt_number=attempt_number,
            )
            return {
                "ok": True,
                "version": PROTOCOL_VERSION,
                "session_id": self.session_id,
                "operation": "claim",
                "attempt_number": attempt_number,
            }


class _AuthorityTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], gateway: HostAuthorityGateway):
        self.gateway = gateway
        super().__init__(server_address, _AuthorityRequestHandler)


class _AuthorityRequestHandler(socketserver.StreamRequestHandler):
    def _write(self, payload: Mapping[str, Any]) -> None:
        encoded = (_canonical_json(dict(payload)) + "\n").encode("utf-8")
        self.wfile.write(encoded)

    def handle(self) -> None:
        raw = self.rfile.readline(MAX_REQUEST_BYTES + 1)
        if not raw:
            return
        if len(raw) > MAX_REQUEST_BYTES:
            self._write(
                {
                    "ok": False,
                    "error": "CrossProcessAuthorityError",
                    "message": "protocol request exceeds maximum size",
                }
            )
            return
        try:
            request = json.loads(raw.decode("utf-8"))
            if not isinstance(request, dict):
                raise CrossProcessAuthorityError(
                    "protocol request must be a JSON object"
                )
            result = self.server.gateway.handle(request)  # type: ignore[attr-defined]
        except (
            CrossProcessAuthorityError,
            ExecutionEnvelopeError,
            UnicodeDecodeError,
            json.JSONDecodeError,
        ) as exc:
            self._write(
                {
                    "ok": False,
                    "error": type(exc).__name__,
                    "message": str(exc),
                }
            )
            return
        self._write(result)


class CrossProcessAuthorityEndpoint:
    """Loopback research endpoint for a TEO-side HostAuthorityGateway."""

    def __init__(self, gateway: HostAuthorityGateway) -> None:
        self.gateway = gateway
        self._server: _AuthorityTCPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def host(self) -> str:
        if self._server is None:
            raise RuntimeError("authority endpoint is not running")
        return str(self._server.server_address[0])

    @property
    def port(self) -> int:
        if self._server is None:
            raise RuntimeError("authority endpoint is not running")
        return int(self._server.server_address[1])

    def descriptor(self) -> dict[str, Any]:
        payload = self.gateway.descriptor()
        payload.update({"host": self.host, "port": self.port})
        return payload

    def start(self) -> "CrossProcessAuthorityEndpoint":
        if self._server is not None:
            raise RuntimeError("authority endpoint is already running")
        self._server = _AuthorityTCPServer(("127.0.0.1", 0), self.gateway)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="teo-host-authority-research",
            daemon=True,
        )
        self._thread.start()
        return self

    def close(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._server = None
        self._thread = None

    def __enter__(self) -> "CrossProcessAuthorityEndpoint":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def send_request(
    host: str,
    port: int,
    request: Mapping[str, Any],
    *,
    timeout_seconds: float = 3.0,
) -> dict[str, Any]:
    """Send one JSON request over a new connection and return one JSON response."""

    payload = (_canonical_json(dict(request)) + "\n").encode("utf-8")
    if len(payload) > MAX_REQUEST_BYTES:
        raise CrossProcessAuthorityError(
            "protocol request exceeds maximum size before transport"
        )
    with socket.create_connection((host, port), timeout=timeout_seconds) as connection:
        connection.sendall(payload)
        reader = connection.makefile("rb")
        raw = reader.readline(MAX_REQUEST_BYTES + 1)
    if not raw or len(raw) > MAX_REQUEST_BYTES:
        raise CrossProcessAuthorityError(
            "authority endpoint returned an invalid response size"
        )
    response = json.loads(raw.decode("utf-8"))
    if not isinstance(response, dict):
        raise CrossProcessAuthorityError(
            "authority endpoint response must be a JSON object"
        )
    return response
