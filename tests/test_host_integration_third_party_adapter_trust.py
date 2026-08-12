from __future__ import annotations

import runpy
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Callable

import pytest

from teo_reference.provider_adapter import (
    ProviderExecutionRequest,
    ProviderExecutionResponse,
)
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_third_party_adapter_trust.py"
RESEARCH = runpy.run_path(str(HARNESS))
AdapterTrustError = RESEARCH["AdapterTrustError"]
ProcessLocalAdapterAuthority = RESEARCH["ProcessLocalAdapterAuthority"]
ThirdPartyAdapterManifest = RESEARCH["ThirdPartyAdapterManifest"]
execute_registered_provider_once = RESEARCH["execute_registered_provider_once"]


def choice(model: str, provider: str, *, agent: str = "external-host") -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="host-integration-third-party-adapter-research",
    )


def dispatch(
    *,
    provider: str = "openai",
    capabilities: list[str] | None = None,
) -> DispatchRecord:
    return DispatchRecord(
        task_id="task-third-party-adapter",
        dispatch_id="dispatch-third-party-adapter",
        created_at="2026-08-12T00:00:00+00:00",
        task="Return one bounded result through the approved adapter.",
        task_type="high_volume_simple",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist="backend-engineer",
        specialist_source="community/specialists/backend-engineer.md",
        specialist_risk_profile="medium",
        required_capabilities=capabilities or ["tool_execution"],
        selected_implementation=choice("gpt-5.6-sol", provider),
        fallback_implementation=choice("gemini-3.6-flash", "google"),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice("claude-sonnet-5", "anthropic", agent="claude"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["third-party adapter trust research fixture"],
        warnings=[],
    )


def manifest(
    *,
    adapter_id: str = "external.openai.responses.v1",
    provider: str = "openai",
    capabilities: tuple[str, ...] = ("tool_execution",),
):
    return ThirdPartyAdapterManifest(
        adapter_id=adapter_id,
        provider_family=provider,
        supported_capabilities=capabilities,
    )


class MutableArtifact:
    def __init__(self, payload: bytes = b"approved-adapter-artifact-v1") -> None:
        self.payload = payload

    def read(self) -> bytes:
        return self.payload


class RecordingAdapter:
    provider_family = "openai"

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: ProviderExecutionRequest) -> ProviderExecutionResponse:
        self.calls += 1
        return ProviderExecutionResponse(
            dispatch_id=request.dispatch_id,
            status="succeeded",
            provider_family=request.provider_family,
            model=request.model,
            output_ref="artifact://third-party-adapter-result",
        )


class SubstituteAdapter(RecordingAdapter):
    pass


def register(
    authority,
    approved_manifest,
    artifact: MutableArtifact,
    factory: Callable[[], RecordingAdapter],
) -> str:
    return authority.register(
        approved_manifest,
        artifact_reader=artifact.read,
        adapter_factory=factory,
    )


def test_exact_registered_adapter_executes_once() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)

    result = execute_registered_provider_once(authority, token, approved, dispatch())

    assert result.status == "succeeded"
    assert adapter.calls == 1


def test_unissued_registration_token_fails_before_adapter_resolution() -> None:
    authority = ProcessLocalAdapterAuthority()

    with pytest.raises(AdapterTrustError, match="not issued"):
        execute_registered_provider_once(
            authority,
            "host-self-issued-token",
            manifest(),
            dispatch(),
        )


def test_revoked_registration_cannot_execute() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)
    authority.revoke(token)

    with pytest.raises(AdapterTrustError, match="revoked"):
        execute_registered_provider_once(authority, token, approved, dispatch())

    assert adapter.calls == 0


def test_changed_implementation_artifact_is_rejected_before_execution() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)
    artifact.payload = b"host-replaced-adapter-artifact-v2"

    with pytest.raises(AdapterTrustError, match="artifact changed"):
        execute_registered_provider_once(authority, token, approved, dispatch())

    assert adapter.calls == 0


@pytest.mark.parametrize(
    "tampered",
    [
        manifest(adapter_id="external.openai.responses.v2"),
        manifest(provider="google"),
        manifest(capabilities=("tool_execution", "web_research")),
    ],
)
def test_manifest_tampering_cannot_widen_or_rebind_registration(tampered) -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)

    with pytest.raises(AdapterTrustError, match="manifest differs"):
        execute_registered_provider_once(authority, token, tampered, dispatch())

    assert adapter.calls == 0


def test_registration_token_cannot_be_reused_with_another_adapter_manifest() -> None:
    authority = ProcessLocalAdapterAuthority()
    artifact_a = MutableArtifact(b"adapter-a")
    artifact_b = MutableArtifact(b"adapter-b")
    adapter_a = RecordingAdapter()
    adapter_b = RecordingAdapter()
    manifest_a = manifest(adapter_id="external.adapter.a")
    manifest_b = manifest(adapter_id="external.adapter.b")
    token_a = register(authority, manifest_a, artifact_a, lambda: adapter_a)
    register(authority, manifest_b, artifact_b, lambda: adapter_b)

    with pytest.raises(AdapterTrustError, match="manifest differs"):
        execute_registered_provider_once(authority, token_a, manifest_b, dispatch())

    assert adapter_a.calls == 0
    assert adapter_b.calls == 0


def test_factory_substitution_after_registration_is_rejected() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    selected: list[type[RecordingAdapter]] = [RecordingAdapter]
    instances: list[RecordingAdapter] = []

    def mutable_factory() -> RecordingAdapter:
        instance = selected[0]()
        instances.append(instance)
        return instance

    token = register(authority, approved, artifact, mutable_factory)
    selected[0] = SubstituteAdapter

    with pytest.raises(AdapterTrustError, match="different runtime type"):
        execute_registered_provider_once(authority, token, approved, dispatch())

    assert all(instance.calls == 0 for instance in instances)


def test_runtime_provider_drift_after_registration_is_rejected() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)
    original = RecordingAdapter.provider_family
    try:
        RecordingAdapter.provider_family = "google"
        with pytest.raises(AdapterTrustError, match="provider family drifted"):
            execute_registered_provider_once(authority, token, approved, dispatch())
    finally:
        RecordingAdapter.provider_family = original

    assert adapter.calls == 0


def test_registration_rejects_factory_provider_mismatch() -> None:
    class WrongProviderAdapter(RecordingAdapter):
        provider_family = "google"

    authority = ProcessLocalAdapterAuthority()

    with pytest.raises(AdapterTrustError, match="does not match the approved manifest"):
        register(authority, manifest(), MutableArtifact(), WrongProviderAdapter)


def test_dispatch_provider_must_match_registered_manifest() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest()
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)
    routed = deepcopy(dispatch())
    routed.selected_implementation.provider_family = "google"

    with pytest.raises(AdapterTrustError, match="dispatch-selected provider"):
        execute_registered_provider_once(authority, token, approved, routed)

    assert adapter.calls == 0


def test_dispatch_capabilities_cannot_exceed_registered_manifest() -> None:
    authority = ProcessLocalAdapterAuthority()
    approved = manifest(capabilities=("tool_execution",))
    artifact = MutableArtifact()
    adapter = RecordingAdapter()
    token = register(authority, approved, artifact, lambda: adapter)

    with pytest.raises(AdapterTrustError, match="does not cover dispatch capabilities"):
        execute_registered_provider_once(
            authority,
            token,
            approved,
            dispatch(capabilities=["tool_execution", "web_research"]),
        )

    assert adapter.calls == 0


def test_adapter_self_asserted_manifest_cannot_expand_authority() -> None:
    class SelfWideningAdapter(RecordingAdapter):
        claimed_manifest = {
            "adapter_id": "external.openai.responses.v1",
            "provider_family": "openai",
            "supported_capabilities": ["tool_execution", "web_research", "computer_use"],
        }

    authority = ProcessLocalAdapterAuthority()
    approved = manifest(capabilities=("tool_execution",))
    artifact = MutableArtifact()
    adapter = SelfWideningAdapter()
    token = register(authority, approved, artifact, lambda: adapter)

    with pytest.raises(AdapterTrustError, match="does not cover dispatch capabilities"):
        execute_registered_provider_once(
            authority,
            token,
            approved,
            dispatch(capabilities=["tool_execution", "web_research"]),
        )

    assert adapter.calls == 0


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"contract_version": "2"}, "contract_version"),
        ({"operation": "provider_execute_with_fallback"}, "operation"),
    ],
)
def test_manifest_cannot_declare_a_wider_contract(kwargs, message: str) -> None:
    with pytest.raises(AdapterTrustError, match=message):
        replace(manifest(), **kwargs)
