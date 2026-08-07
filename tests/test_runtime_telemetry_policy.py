from __future__ import annotations

from pathlib import Path

import pytest

from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.runtime_telemetry import RuntimeTelemetryPolicy


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_telemetry_policy_is_content_free_and_non_derivative() -> None:
    policy = RuntimeTelemetryPolicy.load(REPO_ROOT)
    assert policy.task_types == {"high_volume_simple"}
    assert policy.risk_levels == {"low", "medium"}
    assert policy.record_every_provider_attempt is True
    assert policy.default_sink == "jsonl"
    assert policy.default_filename == "runtime-telemetry.jsonl"
    assert policy.sink_failure_behavior == "fail_closed"
    assert policy.include_task_or_prompt_content is False
    assert policy.include_model_output_content is False
    assert policy.include_provider_native_payloads is False
    assert policy.include_provider_headers is False
    assert policy.include_credentials_or_authorization is False
    assert policy.include_connection_mechanism is False
    assert policy.include_user_identifiers is False
    assert policy.calculate_cost is False
    assert policy.calculate_quality is False


def test_runtime_telemetry_policy_rejects_sensitive_or_derived_fields() -> None:
    policy = RuntimeTelemetryPolicy(
        task_types=frozenset({"high_volume_simple"}),
        risk_levels=frozenset({"low", "medium"}),
        event_type="provider_attempt",
        record_every_provider_attempt=True,
        default_sink="jsonl",
        default_filename="runtime-telemetry.jsonl",
        sink_failure_behavior="fail_closed",
        include_task_or_prompt_content=True,
        include_model_output_content=False,
        include_provider_native_payloads=False,
        include_provider_headers=False,
        include_credentials_or_authorization=False,
        include_connection_mechanism=False,
        include_user_identifiers=False,
        calculate_cost=False,
        calculate_quality=False,
    )
    with pytest.raises(ProviderAdapterContractError, match="unsupported sensitive or derived fields"):
        policy.validate()
