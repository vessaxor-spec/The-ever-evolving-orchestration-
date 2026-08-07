from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from time import time
from typing import Callable, Literal, Protocol

import yaml

from .provider_adapter import ProviderAdapterContractError, ProviderExecutionResponse
from .schemas import DispatchRecord, TaskConstraints, TaskRequest

CIRCUIT_POLICY_PATH = "policy/runtime/provider-circuit-breaker.yaml"
CircuitState = Literal["closed", "open", "half_open"]
Clock = Callable[[], float]


@dataclass(frozen=True, slots=True)
class ProviderCircuitPolicy:
    failure_threshold: int
    failure_window_seconds: float
    base_open_cooldown_seconds: float
    open_cooldown_multiplier: float
    max_open_cooldown_seconds: float
    half_open_max_probe_dispatches: int
    half_open_successes_required_to_close: int
    service_health_signals: dict[str, frozenset[str]]
    never_global_health_signals: frozenset[str]

    @classmethod
    def load(cls, repo_root: str | Path) -> "ProviderCircuitPolicy":
        path = Path(repo_root) / CIRCUIT_POLICY_PATH
        if not path.is_file():
            raise ProviderAdapterContractError(f"Provider circuit policy not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("status") != "active":
            raise ProviderAdapterContractError("Provider circuit policy must be an active mapping")
        if data.get("scope") != "provider_family":
            raise ProviderAdapterContractError("Provider circuit policy must be provider-family scoped")

        trip = data.get("trip_policy")
        half_open = data.get("half_open")
        signals = data.get("service_health_signals")
        exclusions = data.get("never_global_health_signals")
        if not isinstance(trip, dict) or not isinstance(half_open, dict):
            raise ProviderAdapterContractError("Provider circuit policy requires trip and half-open mappings")
        if not isinstance(signals, dict) or not isinstance(exclusions, list):
            raise ProviderAdapterContractError("Provider circuit policy requires health signals and exclusions")

        policy = cls(
            failure_threshold=int(trip.get("failure_threshold", 0)),
            failure_window_seconds=float(trip.get("failure_window_seconds", 0)),
            base_open_cooldown_seconds=float(trip.get("base_open_cooldown_seconds", 0)),
            open_cooldown_multiplier=float(trip.get("open_cooldown_multiplier", 0)),
            max_open_cooldown_seconds=float(trip.get("max_open_cooldown_seconds", 0)),
            half_open_max_probe_dispatches=int(half_open.get("max_probe_dispatches", 0)),
            half_open_successes_required_to_close=int(half_open.get("successes_required_to_close", 0)),
            service_health_signals={
                str(provider): frozenset(str(code).strip().lower() for code in codes)
                for provider, codes in signals.items()
                if isinstance(codes, list)
            },
            never_global_health_signals=frozenset(str(code).strip().lower() for code in exclusions),
        )
        policy.validate()
        return policy

    def validate(self) -> None:
        if self.failure_threshold < 2:
            raise ProviderAdapterContractError("Provider circuit failure threshold must be at least 2")
        if self.failure_window_seconds <= 0:
            raise ProviderAdapterContractError("Provider circuit failure window must be positive")
        if self.base_open_cooldown_seconds <= 0 or self.max_open_cooldown_seconds <= 0:
            raise ProviderAdapterContractError("Provider circuit cooldowns must be positive")
        if self.open_cooldown_multiplier < 1:
            raise ProviderAdapterContractError("Provider circuit cooldown multiplier must be at least 1")
        if self.max_open_cooldown_seconds < self.base_open_cooldown_seconds:
            raise ProviderAdapterContractError("Provider circuit max cooldown cannot be below the base cooldown")
        if self.half_open_max_probe_dispatches != 1:
            raise ProviderAdapterContractError("Reference provider circuit permits exactly one half-open probe at a time")
        if self.half_open_successes_required_to_close < 1:
            raise ProviderAdapterContractError("Half-open provider circuit requires at least one successful probe")
        required = {"anthropic", "openai", "google"}
        if set(self.service_health_signals) != required:
            raise ProviderAdapterContractError("Provider circuit health signals must cover Anthropic, OpenAI, and Google")
        for provider, codes in self.service_health_signals.items():
            if not codes:
                raise ProviderAdapterContractError(f"Provider circuit health signal set is empty for {provider}")
            if codes & self.never_global_health_signals:
                overlap = ", ".join(sorted(codes & self.never_global_health_signals))
                raise ProviderAdapterContractError(
                    f"Provider circuit health signals conflict with global exclusions for {provider}: {overlap}"
                )


@dataclass(frozen=True, slots=True)
class ProviderCircuitRecord:
    provider_family: str
    state: CircuitState = "closed"
    failure_count: int = 0
    failure_window_started_at: float | None = None
    opened_at: float | None = None
    reopen_at: float | None = None
    trip_count: int = 0
    half_open_successes: int = 0
    probe_in_flight: bool = False
    last_failure_code: str | None = None
    last_transition_at: float | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "ProviderCircuitRecord":
        allowed = {
            "provider_family",
            "state",
            "failure_count",
            "failure_window_started_at",
            "opened_at",
            "reopen_at",
            "trip_count",
            "half_open_successes",
            "probe_in_flight",
            "last_failure_code",
            "last_transition_at",
        }
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ProviderAdapterContractError(
                f"Provider circuit record contains unsupported fields: {', '.join(unknown)}"
            )
        provider = str(data.get("provider_family") or "").strip()
        state = str(data.get("state") or "")
        if not provider or state not in {"closed", "open", "half_open"}:
            raise ProviderAdapterContractError("Provider circuit record has invalid provider or state")
        return cls(
            provider_family=provider,
            state=state,  # type: ignore[arg-type]
            failure_count=int(data.get("failure_count", 0)),
            failure_window_started_at=_optional_float(data.get("failure_window_started_at")),
            opened_at=_optional_float(data.get("opened_at")),
            reopen_at=_optional_float(data.get("reopen_at")),
            trip_count=int(data.get("trip_count", 0)),
            half_open_successes=int(data.get("half_open_successes", 0)),
            probe_in_flight=bool(data.get("probe_in_flight", False)),
            last_failure_code=str(data["last_failure_code"]) if data.get("last_failure_code") else None,
            last_transition_at=_optional_float(data.get("last_transition_at")),
        )

    def to_dict(self) -> dict:
        return asdict(self)


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


class CircuitStateStore(Protocol):
    def load_all(self) -> dict[str, ProviderCircuitRecord]:
        ...

    def save(self, record: ProviderCircuitRecord) -> None:
        ...


class InMemoryCircuitStateStore:
    def __init__(self) -> None:
        self._records: dict[str, ProviderCircuitRecord] = {}

    def load_all(self) -> dict[str, ProviderCircuitRecord]:
        return dict(self._records)

    def save(self, record: ProviderCircuitRecord) -> None:
        self._records[record.provider_family] = record


class JsonFileCircuitStateStore:
    """Persistent single-process reference store for provider circuit state.

    Multi-process or distributed deployments need a shared transactional store. The JSON
    implementation intentionally fails closed on malformed state rather than silently resetting it.
    """

    format_version = 1

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load_all(self) -> dict[str, ProviderCircuitRecord]:
        if not self.path.exists():
            return {}
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ProviderAdapterContractError("Provider circuit state is unreadable or corrupt") from exc
        if not isinstance(payload, dict) or payload.get("format_version") != self.format_version:
            raise ProviderAdapterContractError("Provider circuit state has an unsupported format version")
        records = payload.get("providers")
        if not isinstance(records, dict):
            raise ProviderAdapterContractError("Provider circuit state requires a providers mapping")
        result: dict[str, ProviderCircuitRecord] = {}
        for provider, raw in records.items():
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError("Provider circuit state record must be an object")
            record = ProviderCircuitRecord.from_dict(raw)
            if record.provider_family != provider:
                raise ProviderAdapterContractError("Provider circuit state key does not match record provider")
            result[provider] = record
        return result

    def save(self, record: ProviderCircuitRecord) -> None:
        records = self.load_all()
        records[record.provider_family] = record
        payload = {
            "format_version": self.format_version,
            "providers": {provider: item.to_dict() for provider, item in sorted(records.items())},
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f".{self.path.name}.{os.getpid()}.tmp")
        try:
            temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            temporary.replace(self.path)
        except OSError as exc:
            raise ProviderAdapterContractError("Provider circuit state could not be persisted") from exc
        finally:
            if temporary.exists():
                try:
                    temporary.unlink()
                except OSError:
                    pass


class ProviderCircuitBreaker:
    def __init__(
        self,
        policy: ProviderCircuitPolicy,
        store: CircuitStateStore,
        *,
        clock: Clock = time,
    ) -> None:
        policy.validate()
        self.policy = policy
        self.store = store
        self.clock = clock

    def _record(self, provider: str) -> ProviderCircuitRecord:
        return self.store.load_all().get(provider, ProviderCircuitRecord(provider_family=provider))

    def _cooldown_seconds(self, trip_count: int) -> float:
        exponent = max(trip_count - 1, 0)
        return min(
            self.policy.base_open_cooldown_seconds * (self.policy.open_cooldown_multiplier ** exponent),
            self.policy.max_open_cooldown_seconds,
        )

    def _open(self, record: ProviderCircuitRecord, now: float, code: str | None) -> ProviderCircuitRecord:
        trip_count = record.trip_count + 1
        opened = ProviderCircuitRecord(
            provider_family=record.provider_family,
            state="open",
            failure_count=0,
            failure_window_started_at=None,
            opened_at=now,
            reopen_at=now + self._cooldown_seconds(trip_count),
            trip_count=trip_count,
            half_open_successes=0,
            probe_in_flight=False,
            last_failure_code=code,
            last_transition_at=now,
        )
        self.store.save(opened)
        return opened

    def _close(self, record: ProviderCircuitRecord, now: float) -> ProviderCircuitRecord:
        closed = ProviderCircuitRecord(
            provider_family=record.provider_family,
            state="closed",
            failure_count=0,
            failure_window_started_at=None,
            opened_at=None,
            reopen_at=None,
            trip_count=record.trip_count,
            half_open_successes=0,
            probe_in_flight=False,
            last_failure_code=None,
            last_transition_at=now,
        )
        self.store.save(closed)
        return closed

    def _refresh(self, record: ProviderCircuitRecord, now: float) -> ProviderCircuitRecord:
        if record.state == "open" and record.reopen_at is not None and now >= record.reopen_at:
            refreshed = replace(
                record,
                state="half_open",
                half_open_successes=0,
                probe_in_flight=False,
                last_transition_at=now,
            )
            self.store.save(refreshed)
            return refreshed
        return record

    def prepare_task(self, task: TaskRequest) -> TaskRequest:
        """Apply active provider-health blocks without mutating the caller's task."""
        now = self.clock()
        blocked = list(task.constraints.blocked_providers)
        for provider, raw_record in self.store.load_all().items():
            record = self._refresh(raw_record, now)
            if record.state == "open" or (record.state == "half_open" and record.probe_in_flight):
                if provider not in blocked:
                    blocked.append(provider)

        constraints = TaskConstraints(
            contexts=list(task.constraints.contexts),
            required_capabilities=list(task.constraints.required_capabilities),
            blocked_implementations=list(task.constraints.blocked_implementations),
            blocked_providers=blocked,
            require_human_approval=task.constraints.require_human_approval,
        )
        return TaskRequest(
            task=task.task,
            task_id=task.task_id,
            task_type=task.task_type,
            risk_level=task.risk_level,
            domain=task.domain,
            specialist=task.specialist,
            constraints=constraints,
        )

    def claim_dispatch(self, dispatch: DispatchRecord) -> None:
        provider = dispatch.selected_implementation.provider_family
        if not provider:
            raise ProviderAdapterContractError("Circuit breaker cannot authorize a providerless dispatch")
        now = self.clock()
        record = self._refresh(self._record(provider), now)
        if record.state == "open":
            raise ProviderAdapterContractError(f"Provider circuit is open for {provider}")
        if record.state == "half_open":
            if record.probe_in_flight:
                raise ProviderAdapterContractError(f"Half-open provider circuit already has a probe for {provider}")
            self.store.save(replace(record, probe_in_flight=True, last_transition_at=now))

    def is_service_health_failure(self, response: ProviderExecutionResponse) -> bool:
        if response.status != "failed" or response.failure is None:
            return False
        code = response.failure.code.strip().lower()
        if code in self.policy.never_global_health_signals:
            return False
        return code in self.policy.service_health_signals.get(response.provider_family, frozenset())

    def observe(self, dispatch: DispatchRecord, response: ProviderExecutionResponse) -> ProviderCircuitRecord:
        provider = dispatch.selected_implementation.provider_family
        if not provider or provider != response.provider_family:
            raise ProviderAdapterContractError("Circuit observation must match the active dispatch provider")
        now = self.clock()
        record = self._refresh(self._record(provider), now)

        if response.status == "succeeded":
            if record.state == "half_open":
                successes = record.half_open_successes + 1
                if successes >= self.policy.half_open_successes_required_to_close:
                    return self._close(record, now)
                updated = replace(
                    record,
                    half_open_successes=successes,
                    probe_in_flight=False,
                    last_failure_code=None,
                    last_transition_at=now,
                )
                self.store.save(updated)
                return updated
            return self._close(record, now)

        failure = response.failure
        if failure is None:
            raise ProviderAdapterContractError("Failed provider response must include failure details")
        code = failure.code.strip().lower()
        health_failure = self.is_service_health_failure(response)

        if record.state == "half_open":
            if health_failure or code == "connection_error":
                return self._open(replace(record, probe_in_flight=False), now, code)
            return self._close(record, now)

        if not health_failure:
            return self._close(record, now)

        window_started = record.failure_window_started_at
        if window_started is None or now - window_started > self.policy.failure_window_seconds:
            failure_count = 1
            window_started = now
        else:
            failure_count = record.failure_count + 1

        if failure_count >= self.policy.failure_threshold:
            return self._open(record, now, code)

        updated = replace(
            record,
            state="closed",
            failure_count=failure_count,
            failure_window_started_at=window_started,
            last_failure_code=code,
            last_transition_at=now,
            probe_in_flight=False,
        )
        self.store.save(updated)
        return updated
