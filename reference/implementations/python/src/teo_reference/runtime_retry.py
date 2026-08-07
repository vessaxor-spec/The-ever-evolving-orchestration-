from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import random
from time import monotonic, sleep
from typing import Callable, Mapping

import yaml

from .provider_adapter import ProviderAdapterContractError, ProviderExecutionResponse
from .provider_connection import ProviderConnection
from .schemas import DispatchRecord

CANARY_RETRY_POLICY = "policy/runtime/canary-retry.yaml"
Sleeper = Callable[[float], None]
RandomSource = Callable[[], float]
AttemptClock = Callable[[], float]
AttemptObserver = Callable[[DispatchRecord, int, ProviderExecutionResponse, float], None]
Executor = Callable[
    [DispatchRecord, Mapping[str, ProviderConnection], str | Path],
    ProviderExecutionResponse,
]


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    eligible_failure_scopes: frozenset[str]
    max_attempts_per_dispatch: int
    initial_delay_seconds: float
    backoff_multiplier: float
    max_delay_seconds: float
    jitter_ratio: float
    honor_provider_retry_after: bool
    max_provider_retry_after_seconds: float
    provider_retry_after_exceeds_budget: str
    fallback_after_transient_exhaustion: bool

    @classmethod
    def load(cls, repo_root: str | Path) -> "RetryPolicy":
        path = Path(repo_root) / CANARY_RETRY_POLICY
        if not path.is_file():
            raise ProviderAdapterContractError(f"Canary retry policy not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("status") != "active":
            raise ProviderAdapterContractError("Canary retry policy must be an active mapping")
        retry = data.get("retry")
        if not isinstance(retry, dict):
            raise ProviderAdapterContractError("Canary retry policy requires a retry mapping")
        if retry.get("retry_same_dispatch") is not True:
            raise ProviderAdapterContractError("Canary retry must preserve the active dispatch")
        if retry.get("redispatch_during_retry") is not False:
            raise ProviderAdapterContractError("Canary retry cannot redispatch during a retry sequence")

        policy = cls(
            eligible_failure_scopes=frozenset(str(item) for item in retry.get("eligible_failure_scopes", [])),
            max_attempts_per_dispatch=int(retry.get("max_attempts_per_dispatch", 0)),
            initial_delay_seconds=float(retry.get("initial_delay_seconds", -1)),
            backoff_multiplier=float(retry.get("backoff_multiplier", 0)),
            max_delay_seconds=float(retry.get("max_delay_seconds", -1)),
            jitter_ratio=float(retry.get("jitter_ratio", -1)),
            honor_provider_retry_after=bool(retry.get("honor_provider_retry_after", False)),
            max_provider_retry_after_seconds=float(
                retry.get("max_provider_retry_after_seconds", -1)
            ),
            provider_retry_after_exceeds_budget=str(
                retry.get("provider_retry_after_exceeds_budget", "")
            ),
            fallback_after_transient_exhaustion=bool(
                retry.get("fallback_after_transient_exhaustion", False)
            ),
        )
        policy.validate()
        return policy

    def validate(self) -> None:
        if self.eligible_failure_scopes != {"transient"}:
            raise ProviderAdapterContractError(
                "Guarded canary retry is restricted to transient failures"
            )
        if self.max_attempts_per_dispatch < 1 or self.max_attempts_per_dispatch > 2:
            raise ProviderAdapterContractError(
                "Guarded canary retry permits one or two attempts per dispatch"
            )
        if self.initial_delay_seconds < 0 or self.max_delay_seconds < 0:
            raise ProviderAdapterContractError("Retry delays cannot be negative")
        if self.backoff_multiplier < 1:
            raise ProviderAdapterContractError("Retry backoff multiplier must be at least 1")
        if not 0 <= self.jitter_ratio <= 0.5:
            raise ProviderAdapterContractError("Retry jitter_ratio must be between 0 and 0.5")
        if not self.honor_provider_retry_after:
            raise ProviderAdapterContractError(
                "Guarded canary retry must honor normalized provider retry timing when present"
            )
        if self.max_provider_retry_after_seconds <= 0:
            raise ProviderAdapterContractError(
                "Provider retry timing budget must be positive"
            )
        if self.provider_retry_after_exceeds_budget != "stop":
            raise ProviderAdapterContractError(
                "Provider retry timing above the guarded wait budget must stop rather than retry early"
            )
        if self.fallback_after_transient_exhaustion:
            raise ProviderAdapterContractError(
                "Transient retry exhaustion cannot silently authorize fallback in this runtime slice"
            )


@dataclass(frozen=True, slots=True)
class RetryExecution:
    response: ProviderExecutionResponse
    attempts: int
    delays_seconds: tuple[float, ...]


def _delay_for_retry(policy: RetryPolicy, retry_number: int, random_source: RandomSource) -> float:
    base = min(
        policy.initial_delay_seconds * (policy.backoff_multiplier ** (retry_number - 1)),
        policy.max_delay_seconds,
    )
    if base == 0 or policy.jitter_ratio == 0:
        return base
    sample = min(max(float(random_source()), 0.0), 1.0)
    multiplier = 1 + policy.jitter_ratio * ((2 * sample) - 1)
    return max(0.0, min(base * multiplier, policy.max_delay_seconds))


def _effective_retry_delay(
    policy: RetryPolicy,
    response: ProviderExecutionResponse,
    retry_number: int,
    random_source: RandomSource,
) -> float | None:
    local_delay = _delay_for_retry(policy, retry_number, random_source)
    provider_delay = response.retry_after_seconds
    if provider_delay is None:
        return local_delay
    if provider_delay > policy.max_provider_retry_after_seconds:
        return None
    return max(local_delay, provider_delay)


def execute_with_transient_retry(
    dispatch: DispatchRecord,
    connections: Mapping[str, ProviderConnection],
    artifact_root: str | Path,
    executor: Executor,
    policy: RetryPolicy,
    *,
    sleeper: Sleeper = sleep,
    random_source: RandomSource = random,
    attempt_observer: AttemptObserver | None = None,
    attempt_clock: AttemptClock = monotonic,
) -> RetryExecution:
    """Retry only transient failures while preserving the active dispatch.

    A normalized provider retry hint is a minimum wait, not authority for another attempt.
    The policy still owns the attempt budget. An optional observer receives each completed
    provider attempt immediately, before any sleep or later recovery action.
    """
    attempts = 0
    delays: list[float] = []

    while attempts < policy.max_attempts_per_dispatch:
        attempts += 1
        started_at = float(attempt_clock())
        response = executor(dispatch, connections, artifact_root)
        finished_at = float(attempt_clock())
        duration_seconds = max(0.0, finished_at - started_at)
        if attempt_observer is not None:
            attempt_observer(dispatch, attempts, response, duration_seconds)

        if response.status == "succeeded":
            return RetryExecution(response=response, attempts=attempts, delays_seconds=tuple(delays))

        failure = response.failure
        if failure is None or failure.scope not in policy.eligible_failure_scopes:
            return RetryExecution(response=response, attempts=attempts, delays_seconds=tuple(delays))
        if attempts >= policy.max_attempts_per_dispatch:
            return RetryExecution(response=response, attempts=attempts, delays_seconds=tuple(delays))

        delay = _effective_retry_delay(policy, response, attempts, random_source)
        if delay is None:
            return RetryExecution(response=response, attempts=attempts, delays_seconds=tuple(delays))
        delays.append(delay)
        sleeper(delay)

    raise ProviderAdapterContractError("Retry controller exhausted without returning a response")
