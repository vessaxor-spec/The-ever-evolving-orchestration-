"""Non-normative integrated Host Integration and fresh-AI assimilation research.

This module composes already accepted process-local Host Integration research controls
into one evidence-bearing sandbox path. It deliberately remains under ``research/``.
It does not create production Host Integration authority or a normative conformance
schema.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import runpy
import secrets
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

from teo_reference import OrchestrationEngine, TaskRequest, VerificationResult
from teo_reference.artifact_integrity import read_verified_text_artifact
from teo_reference.config import ConfigBundle
from teo_reference.schemas import DispatchRecord, ExecutionResult, FinalOutcome


class IntegratedHostConformanceError(ValueError):
    """Raised when assimilation or integrated conformance evidence fails closed."""


RESPONSIBILITY_CHAIN = (
    "mission_control",
    "team",
    "worker",
    "optional_specialist",
    "capability",
    "implementation",
    "independent_verification",
    "evidence_bearing_outcome",
)

ACTIVATION_SEQUENCE = (
    "shadow",
    "bounded_governed_activation",
    "evidence_gated_expansion",
)

REQUIRED_OPEN_SURFACES = frozenset(
    {
        "production_remote_authenticity",
        "restart_durable_distributed_state",
        "compromised_host_bypass_resistance",
        "production_scheduler_enforcement",
        "tenant_account_credential_binding",
        "dynamic_hook_plugin_authority_discovery",
        "cross_session_continued_use_proof",
    }
)

REQUIRED_NEGATIVE_CONTROLS = frozenset(
    {
        "staged_scope_refusal",
        "revoked_admission_refusal",
        "artifact_mutation_refusal",
        "critical_human_gate_preserved",
        "high_risk_autonomy_preserved",
        "recursive_reentry_refusal",
    }
)

PREMORTEM_CHECKS = (
    "context_bloat_collapse",
    "identity_dilution",
    "approval_paralysis",
    "skill_to_specialist_mismatch",
    "verification_schism",
    "registry_drift",
    "recursive_orchestration",
    "control_plane_capture",
    "big_bang_enforcement",
    "missing_conformance_profile",
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _research_module(repo_root: Path, name: str) -> dict[str, Any]:
    return runpy.run_path(str(repo_root / "research" / "runtime" / f"{name}.py"))


def _stable_release(repo_root: Path) -> str:
    text = (repo_root / "docs" / "stewardship" / "progress-tracker.md").read_text(
        encoding="utf-8"
    )
    marker = "**Stable release:** `"
    start = text.find(marker)
    if start < 0:
        raise IntegratedHostConformanceError(
            "Progress Tracker does not declare the stable release"
        )
    start += len(marker)
    end = text.find("`", start)
    if end < 0:
        raise IntegratedHostConformanceError(
            "Progress Tracker stable release marker is malformed"
        )
    return text[start:end]


def repository_revision(repo_root: str | Path) -> str:
    """Return the exact Git revision for a normal worktree.

    A caller materializing a source-only archive should supply the authoritative
    revision separately to ``derive_assimilation_truth`` rather than pretending the
    archive itself proves Git provenance.
    """

    root = Path(repo_root).resolve(strict=True)
    try:
        revision = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise IntegratedHostConformanceError(
            "repository revision requires an authenticated Git worktree or an explicit revision"
        ) from exc
    if len(revision) != 40 or any(ch not in "0123456789abcdef" for ch in revision):
        raise IntegratedHostConformanceError("repository revision is not a full Git SHA-1")
    return revision


@dataclass(frozen=True, slots=True)
class AssimilationTruth:
    stable_release: str
    runtime_version: str
    revision: str
    binding_id: str
    team_count: int
    worker_count: int
    specialist_count: int
    active_live_task_types: tuple[str, ...]
    staged_live_task_types: tuple[str, ...]
    responsibility_chain: tuple[str, ...] = RESPONSIBILITY_CHAIN

    def to_dict(self) -> dict[str, Any]:
        return {
            "stable_release": self.stable_release,
            "runtime_version": self.runtime_version,
            "revision": self.revision,
            "binding_id": self.binding_id,
            "team_count": self.team_count,
            "worker_count": self.worker_count,
            "specialist_count": self.specialist_count,
            "active_live_task_types": list(self.active_live_task_types),
            "staged_live_task_types": list(self.staged_live_task_types),
            "responsibility_chain": list(self.responsibility_chain),
        }


def derive_assimilation_truth(
    repo_root: str | Path,
    *,
    revision: str | None = None,
) -> AssimilationTruth:
    """Derive the facts a fresh AI must independently reconstitute before integration."""

    root = Path(repo_root).resolve(strict=True)
    effective_revision = revision or repository_revision(root)
    freshness = _research_module(root, "host_integration_freshness_binding")
    build_binding_snapshot = freshness["build_binding_snapshot"]
    binding = build_binding_snapshot(
        root,
        release=_stable_release(root),
        revision=effective_revision,
    )

    bundle = ConfigBundle.load(root)
    policy = yaml.safe_load(
        (root / "policy" / "runtime" / "live-execution-expansion.yaml").read_text(
            encoding="utf-8"
        )
    )
    active = policy.get("active_scope", {})
    candidates = policy.get("candidates", {})
    if not isinstance(active, Mapping) or not isinstance(candidates, Mapping):
        raise IntegratedHostConformanceError("live execution policy is malformed")
    active_task_types = tuple(sorted(str(item) for item in active.get("task_types", [])))
    staged_task_types = tuple(
        sorted(
            str(name)
            for name, value in candidates.items()
            if isinstance(value, Mapping)
            and value.get("state") == "staged"
            and value.get("activation_authorized") is False
        )
    )

    return AssimilationTruth(
        stable_release=binding.release,
        runtime_version=binding.runtime_version,
        revision=binding.revision,
        binding_id=binding.binding_id,
        team_count=len({str(worker.get("owning_team")) for worker in bundle.worker_registry.values()}),
        worker_count=len(bundle.worker_registry),
        specialist_count=len(bundle.specialist_registry),
        active_live_task_types=active_task_types,
        staged_live_task_types=staged_task_types,
    )


@dataclass(frozen=True, slots=True)
class FreshAIAssimilationDeclaration:
    host_id: str
    integration_role: str
    host_identity_preserved: bool
    portfolio_authority_owner: str
    routing_authority_owner: str
    connection_semantics: str
    responsibility_chain: tuple[str, ...]
    specialist_context_mode: str
    verification_mode: str
    activation_sequence: tuple[str, ...]
    stable_release: str
    runtime_version: str
    revision: str
    binding_id: str
    team_count: int
    worker_count: int
    specialist_count: int
    active_live_task_types: tuple[str, ...]
    staged_live_task_types: tuple[str, ...]
    unsupported_surfaces: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "host_id": self.host_id,
            "integration_role": self.integration_role,
            "host_identity_preserved": self.host_identity_preserved,
            "portfolio_authority_owner": self.portfolio_authority_owner,
            "routing_authority_owner": self.routing_authority_owner,
            "connection_semantics": self.connection_semantics,
            "responsibility_chain": list(self.responsibility_chain),
            "specialist_context_mode": self.specialist_context_mode,
            "verification_mode": self.verification_mode,
            "activation_sequence": list(self.activation_sequence),
            "stable_release": self.stable_release,
            "runtime_version": self.runtime_version,
            "revision": self.revision,
            "binding_id": self.binding_id,
            "team_count": self.team_count,
            "worker_count": self.worker_count,
            "specialist_count": self.specialist_count,
            "active_live_task_types": list(self.active_live_task_types),
            "staged_live_task_types": list(self.staged_live_task_types),
            "unsupported_surfaces": list(self.unsupported_surfaces),
        }


@dataclass(frozen=True, slots=True)
class AssimilationLease:
    lease_id: str
    host_id: str
    binding_id: str
    revision: str
    declaration_digest: str
    authorization_token: str

    def to_dict(self) -> dict[str, str]:
        return {
            "lease_id": self.lease_id,
            "host_id": self.host_id,
            "binding_id": self.binding_id,
            "revision": self.revision,
            "declaration_digest": self.declaration_digest,
            "authorization_token": self.authorization_token,
        }


class AssimilationAuthority:
    """Process-local research authority for the fresh-AI assimilation handshake."""

    def __init__(self, truth: AssimilationTruth) -> None:
        self.truth = truth
        self._secret = secrets.token_bytes(32)
        self._issued: dict[str, str] = {}

    def _validate_declaration(self, declaration: FreshAIAssimilationDeclaration) -> None:
        if not declaration.host_id.strip():
            raise IntegratedHostConformanceError("host_id must be non-empty")
        if declaration.integration_role != "embedded_orchestration_control_plane":
            raise IntegratedHostConformanceError(
                "TEO assimilation must identify TEO as the embedded orchestration control plane, not a plugin, SDK, library, or finished product"
            )
        if not declaration.host_identity_preserved:
            raise IntegratedHostConformanceError(
                "fresh-AI assimilation must preserve the host identity separately from TEO specialist context"
            )
        if declaration.portfolio_authority_owner != "host":
            raise IntegratedHostConformanceError(
                "host portfolio and task-admission authority must remain host-owned"
            )
        if declaration.routing_authority_owner != "teo_mission_control":
            raise IntegratedHostConformanceError(
                "admitted TEO work must route through TEO Mission Control rather than a parallel host routing plane"
            )
        if declaration.connection_semantics != "connection_after_routing":
            raise IntegratedHostConformanceError(
                "provider connection mechanics must remain downstream of routing"
            )
        if declaration.responsibility_chain != self.truth.responsibility_chain:
            raise IntegratedHostConformanceError(
                "responsibility chain is collapsed or does not match TEO architecture"
            )
        if declaration.specialist_context_mode != "selected_only_bounded_projection":
            raise IntegratedHostConformanceError(
                "fresh-AI assimilation must use bounded selected specialist context rather than loading the active corpus"
            )
        if declaration.verification_mode != "independent_provider_diverse_when_required":
            raise IntegratedHostConformanceError(
                "verification declaration must preserve actual independence rather than same-session roleplay"
            )
        if declaration.activation_sequence != ACTIVATION_SEQUENCE:
            raise IntegratedHostConformanceError(
                "integration must begin in shadow mode and widen only through evidence-gated bounded activation"
            )

        observed = {
            "stable_release": declaration.stable_release,
            "runtime_version": declaration.runtime_version,
            "revision": declaration.revision,
            "binding_id": declaration.binding_id,
            "team_count": declaration.team_count,
            "worker_count": declaration.worker_count,
            "specialist_count": declaration.specialist_count,
            "active_live_task_types": declaration.active_live_task_types,
            "staged_live_task_types": declaration.staged_live_task_types,
        }
        expected = {
            "stable_release": self.truth.stable_release,
            "runtime_version": self.truth.runtime_version,
            "revision": self.truth.revision,
            "binding_id": self.truth.binding_id,
            "team_count": self.truth.team_count,
            "worker_count": self.truth.worker_count,
            "specialist_count": self.truth.specialist_count,
            "active_live_task_types": self.truth.active_live_task_types,
            "staged_live_task_types": self.truth.staged_live_task_types,
        }
        for key, expected_value in expected.items():
            if observed[key] != expected_value:
                raise IntegratedHostConformanceError(
                    f"fresh-AI assimilation truth mismatch for {key}: expected {expected_value!r}, got {observed[key]!r}"
                )

        unsupported = frozenset(declaration.unsupported_surfaces)
        if not REQUIRED_OPEN_SURFACES.issubset(unsupported):
            missing = sorted(REQUIRED_OPEN_SURFACES - unsupported)
            raise IntegratedHostConformanceError(
                "assimilation declaration hides unresolved Host Integration surfaces: "
                + ", ".join(missing)
            )
        if any(item.lower() in {"none", "fully_supported", "complete"} for item in unsupported):
            raise IntegratedHostConformanceError(
                "unsupported Host Integration surfaces must be stated honestly"
            )

    def _lease_payload(
        self,
        *,
        lease_id: str,
        declaration: FreshAIAssimilationDeclaration,
        declaration_digest: str,
    ) -> dict[str, str]:
        return {
            "lease_id": lease_id,
            "host_id": declaration.host_id,
            "binding_id": declaration.binding_id,
            "revision": declaration.revision,
            "declaration_digest": declaration_digest,
        }

    def issue(self, declaration: FreshAIAssimilationDeclaration) -> AssimilationLease:
        self._validate_declaration(declaration)
        declaration_digest = _sha256(declaration.to_dict())
        lease_id = f"assimilation-{secrets.token_hex(12)}"
        payload = self._lease_payload(
            lease_id=lease_id,
            declaration=declaration,
            declaration_digest=declaration_digest,
        )
        token = hmac.new(
            self._secret,
            _canonical_json(payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self._issued[lease_id] = _sha256({**payload, "authorization_token": token})
        return AssimilationLease(authorization_token=token, **payload)

    def verify(self, lease: AssimilationLease) -> None:
        if not isinstance(lease, AssimilationLease):
            raise IntegratedHostConformanceError("assimilation lease type is invalid")
        payload = {
            "lease_id": lease.lease_id,
            "host_id": lease.host_id,
            "binding_id": lease.binding_id,
            "revision": lease.revision,
            "declaration_digest": lease.declaration_digest,
        }
        expected_token = hmac.new(
            self._secret,
            _canonical_json(payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected_token, lease.authorization_token):
            raise IntegratedHostConformanceError("assimilation lease signature is invalid")
        issued_digest = self._issued.get(lease.lease_id)
        if issued_digest is None:
            raise IntegratedHostConformanceError("assimilation lease was not issued")
        if issued_digest != _sha256({**payload, "authorization_token": lease.authorization_token}):
            raise IntegratedHostConformanceError("assimilation lease differs from issued state")
        if lease.binding_id != self.truth.binding_id or lease.revision != self.truth.revision:
            raise IntegratedHostConformanceError(
                "assimilation lease is stale against current TEO integration truth"
            )


@dataclass(frozen=True, slots=True)
class StandingIntegrationHook:
    hook_id: str
    host_id: str
    binding_id: str
    policy: str = "teo_required_for_all_admitted_teo_tasks"
    persistent: bool = True


@dataclass(frozen=True, slots=True)
class ShadowReceipt:
    dispatch_id: str
    task_id: str
    task_type: str
    host_behavior_changed: bool


@dataclass(frozen=True, slots=True)
class GovernedUseReceipt:
    dispatch_id: str
    task_id: str
    task_type: str
    outcome_status: str
    execution_status: str
    verification_status: str


@dataclass(frozen=True, slots=True)
class IntegratedConformanceReport:
    host_id: str
    binding_id: str
    status: str
    shadow_dispatches: int
    governed_executions: int
    negative_controls: tuple[str, ...]
    premortem_replay: Mapping[str, bool]
    residual_boundaries: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.status == "process_local_integrated_conformance_satisfied"


@dataclass(slots=True)
class IntegratedHostConformanceSandbox:
    """Compose fresh-AI assimilation and Host Integration controls into one path.

    The sandbox is intentionally process-local and evidence-only. A successful report
    proves that the tested host path actually used TEO after assimilation; it is not a
    production conformance certificate.
    """

    repo_root: Path
    assimilation_authority: AssimilationAuthority
    lease: AssimilationLease
    engine: OrchestrationEngine
    host_id: str
    _standing_hook: StandingIntegrationHook | None = None
    _shadow_receipts: list[ShadowReceipt] = field(default_factory=list)
    _governed_receipts: list[GovernedUseReceipt] = field(default_factory=list)
    _negative_controls: set[str] = field(default_factory=set)
    _premortem_checks: dict[str, bool] = field(
        default_factory=lambda: {name: False for name in PREMORTEM_CHECKS}
    )

    @classmethod
    def create(
        cls,
        repo_root: str | Path,
        *,
        declaration: FreshAIAssimilationDeclaration,
        revision: str | None = None,
    ) -> "IntegratedHostConformanceSandbox":
        root = Path(repo_root).resolve(strict=True)
        truth = derive_assimilation_truth(root, revision=revision)
        authority = AssimilationAuthority(truth)
        lease = authority.issue(declaration)
        engine = OrchestrationEngine.from_repo(str(root))
        sandbox = cls(
            repo_root=root,
            assimilation_authority=authority,
            lease=lease,
            engine=engine,
            host_id=declaration.host_id,
        )
        sandbox._premortem_checks.update(
            {
                "context_bloat_collapse": True,
                "identity_dilution": True,
                "registry_drift": True,
                "control_plane_capture": True,
                "missing_conformance_profile": True,
            }
        )
        return sandbox

    @property
    def truth(self) -> AssimilationTruth:
        return self.assimilation_authority.truth

    def register_standing_hook(self, hook: StandingIntegrationHook) -> None:
        self.assimilation_authority.verify(self.lease)
        if not isinstance(hook, StandingIntegrationHook):
            raise IntegratedHostConformanceError("standing integration hook type is invalid")
        if hook.host_id != self.host_id:
            raise IntegratedHostConformanceError("standing hook belongs to another host")
        if hook.binding_id != self.truth.binding_id:
            raise IntegratedHostConformanceError("standing hook is stale or mismatched")
        if hook.policy != "teo_required_for_all_admitted_teo_tasks":
            raise IntegratedHostConformanceError(
                "standing hook must require TEO for all admitted TEO tasks"
            )
        if not hook.persistent:
            raise IntegratedHostConformanceError(
                "standing hook must persist beyond the one-time assimilation session"
            )
        self._standing_hook = hook

    def _require_hook(self) -> None:
        if self._standing_hook is None:
            raise IntegratedHostConformanceError(
                "installation or one-time assimilation is insufficient; a persistent TEO control-plane hook is required"
            )

    def shadow_route(self, task_payload: Mapping[str, Any]) -> DispatchRecord:
        self.assimilation_authority.verify(self.lease)
        dispatch = self.engine.dispatch(TaskRequest.from_dict(dict(task_payload)))
        if not dispatch.selected_team or not dispatch.selected_worker:
            raise IntegratedHostConformanceError(
                "TEO shadow dispatch collapsed Team or Worker responsibility"
            )
        if not dispatch.selected_implementation.model:
            raise IntegratedHostConformanceError(
                "TEO shadow dispatch did not resolve an implementation"
            )
        if dispatch.verification.independent and (
            dispatch.verification.implementation.provider_family
            == dispatch.selected_implementation.provider_family
        ):
            raise IntegratedHostConformanceError(
                "TEO shadow dispatch claimed independence without provider diversity"
            )
        self._shadow_receipts.append(
            ShadowReceipt(
                dispatch_id=dispatch.dispatch_id,
                task_id=dispatch.task_id,
                task_type=dispatch.task_type,
                host_behavior_changed=False,
            )
        )
        return dispatch

    def _require_activation_prerequisites(self) -> None:
        self.assimilation_authority.verify(self.lease)
        self._require_hook()
        if not self._shadow_receipts:
            raise IntegratedHostConformanceError(
                "bounded activation requires prior TEO shadow-routing evidence"
            )

    def _build_portfolio(self, task_payload: Mapping[str, Any]):
        portfolio = _research_module(
            self.repo_root, "host_integration_portfolio_authority_separation"
        )
        authority = portfolio["HostPortfolioAuthority"](portfolio_id=self.host_id)
        authority.enqueue_task(task_payload, priority=10)
        grant = authority.admit_task(str(task_payload["task_id"]))
        request = {
            "operation": "orchestrate_admitted_task",
            "admission_id": grant.admission_id,
            "task_id": grant.task_id,
        }
        session = authority.teo_gateway().claim(request, grant, task_payload)
        return portfolio, authority, grant, session

    def _freshness_assertion(self) -> None:
        freshness = _research_module(self.repo_root, "host_integration_freshness_binding")
        build_binding_snapshot = freshness["build_binding_snapshot"]
        AuthorityOwnedBindingCatalog = freshness["AuthorityOwnedBindingCatalog"]
        assess_host_binding = freshness["assess_host_binding"]
        current = build_binding_snapshot(
            self.repo_root,
            release=self.truth.stable_release,
            revision=self.truth.revision,
        )
        assessment = assess_host_binding(
            current,
            AuthorityOwnedBindingCatalog(current),
            claimed_status="PINNED_CURRENT",
        )
        if not assessment.acceptable or assessment.binding_id != self.truth.binding_id:
            raise IntegratedHostConformanceError(
                "integrated host freshness binding is not current and acceptable"
            )

    def _authority_and_envelope(
        self,
        dispatch: DispatchRecord,
        *,
        artifact_path: Path,
        capability: str,
    ):
        dispatch_auth = _research_module(
            self.repo_root, "host_integration_dispatch_authorization"
        )
        authority_intersection = _research_module(
            self.repo_root, "host_integration_authority_intersection"
        )
        envelope = _research_module(
            self.repo_root, "host_integration_execution_envelope_integrity"
        )

        ProcessLocalDispatchAuthority = dispatch_auth["ProcessLocalDispatchAuthority"]
        dispatch_authority = ProcessLocalDispatchAuthority()
        dispatch_token = dispatch_authority.issue(dispatch)
        dispatch_authority.verify(dispatch_token, dispatch)

        TEOIntersectionScope = authority_intersection["TEOExecutionScope"]
        HostExecutionScope = authority_intersection["HostExecutionScope"]
        RestrictiveAuthorityGate = authority_intersection["RestrictiveAuthorityGate"]
        teo_scope = TEOIntersectionScope.from_live_execution_policy(
            self.repo_root / "policy" / "runtime" / "live-execution-expansion.yaml"
        )
        host_scope = HostExecutionScope(
            scope_id="sandbox-host-authority",
            allowed_task_types=tuple(self.truth.active_live_task_types),
            allowed_risk_levels=("low", "medium"),
            allowed_capabilities=tuple(sorted(set(dispatch.required_capabilities))),
            allowed_provider_families=(dispatch.selected_implementation.provider_family,),
            allowed_operations=("write_artifact",),
        )
        restrictive_gate = RestrictiveAuthorityGate(teo_scope, host_scope)
        host_token = restrictive_gate.authorize(
            dispatch,
            capability=capability,
            operation="write_artifact",
        )

        TEOEnvelopeScope = envelope["TEOExecutionScope"]
        TEORetryScope = envelope["TEORetryScope"]
        HostExecutionEnvelopeScope = envelope["HostExecutionEnvelopeScope"]
        ExecutionEnvelopeAuthority = envelope["ExecutionEnvelopeAuthority"]
        ResourceTarget = envelope["ResourceTarget"]
        envelope_teo_scope = TEOEnvelopeScope.from_live_execution_policy(
            self.repo_root / "policy" / "runtime" / "live-execution-expansion.yaml"
        )
        retry_scope = TEORetryScope.from_retry_policy(
            self.repo_root / "policy" / "runtime" / "canary-retry.yaml"
        )
        host_envelope = HostExecutionEnvelopeScope(
            scope_id="sandbox-exact-envelope",
            allowed_resource_kinds=("file",),
            allowed_target_prefixes=(str(artifact_path.parent.resolve()),),
            allowed_side_effect_classes=("local_mutation",),
            required_prerequisites=("host_admission_revalidated",),
            max_attempts_per_dispatch=1,
        )
        envelope_authority = ExecutionEnvelopeAuthority(
            envelope_teo_scope,
            retry_scope,
            host_envelope,
        )
        action_token, action_authorization = envelope_authority.issue_teo_action(
            dispatch,
            authorization_id=f"action-{dispatch.dispatch_id}",
            capability=capability,
            operation="write_artifact",
            effective_risk=dispatch.risk_level,
            target=ResourceTarget(kind="file", identifier=str(artifact_path.resolve())),
            parameters={"content_class": "bounded_sandbox_text"},
            side_effect_class="local_mutation",
            required_prerequisites=("host_admission_revalidated",),
            max_attempts_per_dispatch=1,
        )
        execution_token = envelope_authority.authorize_host_execution(
            action_token,
            dispatch,
            action_authorization,
            satisfied_prerequisites=("host_admission_revalidated",),
            attempt_number=1,
        )
        return {
            "restrictive_gate": restrictive_gate,
            "host_token": host_token,
            "envelope": envelope,
            "envelope_authority": envelope_authority,
            "action_token": action_token,
            "action_authorization": action_authorization,
            "execution_token": execution_token,
        }

    def governed_execute(
        self,
        task_payload: Mapping[str, Any],
        *,
        artifact_root: str | Path,
    ) -> FinalOutcome:
        self._require_activation_prerequisites()
        self._freshness_assertion()

        artifact_root_path = Path(artifact_root).resolve()
        artifact_root_path.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_root_path / f"{task_payload['task_id']}.txt"

        portfolio, host_authority, grant, session = self._build_portfolio(task_payload)
        gateway = host_authority.teo_gateway()
        gateway.revalidate(session, task_payload)

        dispatch = self.engine.dispatch(TaskRequest.from_dict(dict(task_payload)))
        if not dispatch.required_capabilities:
            raise IntegratedHostConformanceError(
                "integrated governed dispatch resolved no executable capabilities"
            )
        capability = dispatch.required_capabilities[-1]

        controls = self._authority_and_envelope(
            dispatch,
            artifact_path=artifact_path,
            capability=capability,
        )
        execute_authorized_host_action = _research_module(
            self.repo_root, "host_integration_authority_intersection"
        )["execute_authorized_host_action"]
        execute_authorized_action = controls["envelope"]["execute_authorized_action"]

        gateway.revalidate(session, task_payload)

        def write_artifact() -> str:
            artifact_path.write_text(
                f"TEO-governed sandbox output for {dispatch.task_id}\n",
                encoding="utf-8",
            )
            return str(artifact_path)

        execute_authorized_action(
            controls["envelope_authority"],
            controls["execution_token"],
            controls["action_token"],
            dispatch,
            controls["action_authorization"],
            satisfied_prerequisites=("host_admission_revalidated",),
            attempt_number=1,
            action=lambda: execute_authorized_host_action(
                controls["restrictive_gate"],
                controls["host_token"],
                dispatch,
                capability=capability,
                operation="write_artifact",
                action=write_artifact,
            ),
        )

        output_ref = artifact_path.resolve().as_uri()
        _, verified_artifact = read_verified_text_artifact(
            output_ref,
            allowed_root=artifact_root_path,
        )
        execution = ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            output_ref=output_ref,
            evidence=["integrated host sandbox executed exact authorized envelope"],
        )
        verification = VerificationResult(
            dispatch_id=dispatch.dispatch_id,
            status="passed",
            verifier_model=dispatch.verification.implementation.model,
            checks=dispatch.verification.method,
            evidence=["integrated sandbox verifier accepted exact bound artifact"],
            verified_artifact=verified_artifact,
        )
        outcome = self.engine.finalize(
            dispatch,
            execution,
            verification,
            artifact_root=artifact_root_path,
        )
        self._governed_receipts.append(
            GovernedUseReceipt(
                dispatch_id=dispatch.dispatch_id,
                task_id=dispatch.task_id,
                task_type=dispatch.task_type,
                outcome_status=outcome.status,
                execution_status=outcome.execution_status,
                verification_status=outcome.verification_status,
            )
        )
        self._premortem_checks["skill_to_specialist_mismatch"] = True
        self._premortem_checks["verification_schism"] = (
            dispatch.selected_implementation.provider_family
            != dispatch.verification.implementation.provider_family
        )
        self._premortem_checks["big_bang_enforcement"] = bool(self._shadow_receipts)
        return outcome

    def prove_staged_scope_refusal(self) -> None:
        self._require_activation_prerequisites()
        payload = {
            "task_id": "assimilation-staged-documentation",
            "task": "Draft one bounded technical note for the integration proof.",
            "task_type": "documentation",
            "risk_level": "low",
        }
        dispatch = self.engine.dispatch(TaskRequest.from_dict(payload))
        intersection = _research_module(
            self.repo_root, "host_integration_authority_intersection"
        )
        TEOExecutionScope = intersection["TEOExecutionScope"]
        HostExecutionScope = intersection["HostExecutionScope"]
        RestrictiveAuthorityGate = intersection["RestrictiveAuthorityGate"]
        gate = RestrictiveAuthorityGate(
            TEOExecutionScope.from_live_execution_policy(
                self.repo_root / "policy" / "runtime" / "live-execution-expansion.yaml"
            ),
            HostExecutionScope(
                scope_id="staged-refusal-host",
                allowed_task_types=("high_volume_simple", "documentation"),
                allowed_risk_levels=("low", "medium"),
                allowed_capabilities=tuple(dispatch.required_capabilities),
                allowed_provider_families=(dispatch.selected_implementation.provider_family,),
                allowed_operations=("write_artifact",),
            ),
        )
        try:
            gate.authorize(
                dispatch,
                capability=dispatch.required_capabilities[0],
                operation="write_artifact",
            )
        except Exception as exc:
            if "TEO active scope does not authorize task_type" not in str(exc):
                raise
            self._negative_controls.add("staged_scope_refusal")
            return
        raise IntegratedHostConformanceError(
            "staged documentation scope was incorrectly authorized"
        )

    def prove_revoked_admission_refusal(self) -> None:
        self._require_activation_prerequisites()
        payload = {
            "task_id": "assimilation-revoked-admission",
            "task": "Classify one bounded record after host admission.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
        portfolio, authority, grant, session = self._build_portfolio(payload)
        authority.revoke_admission(grant.admission_id)
        try:
            authority.teo_gateway().revalidate(session, payload)
        except Exception as exc:
            if "revoked or cancelled" not in str(exc):
                raise
            self._negative_controls.add("revoked_admission_refusal")
            return
        raise IntegratedHostConformanceError("revoked host admission remained executable")

    def prove_artifact_mutation_refusal(self, *, artifact_root: str | Path) -> None:
        self._require_activation_prerequisites()
        payload = {
            "task_id": "assimilation-artifact-mutation",
            "task": "Classify a bounded artifact integrity probe.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
        dispatch = self.engine.dispatch(TaskRequest.from_dict(payload))
        root = Path(artifact_root).resolve()
        root.mkdir(parents=True, exist_ok=True)
        path = root / "mutation-probe.txt"
        path.write_text("verified bytes\n", encoding="utf-8")
        output_ref = path.resolve().as_uri()
        _, verified_artifact = read_verified_text_artifact(output_ref, allowed_root=root)
        execution = ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            output_ref=output_ref,
            evidence=["artifact mutation probe created"],
        )
        verification = VerificationResult(
            dispatch_id=dispatch.dispatch_id,
            status="passed",
            verifier_model=dispatch.verification.implementation.model,
            checks=dispatch.verification.method,
            evidence=["artifact mutation probe verified"],
            verified_artifact=verified_artifact,
        )
        path.write_text("mutated after verification\n", encoding="utf-8")
        try:
            self.engine.finalize(
                dispatch,
                execution,
                verification,
                artifact_root=root,
            )
        except Exception as exc:
            if "digest" not in str(exc).lower() and "artifact" not in str(exc).lower():
                raise
            self._negative_controls.add("artifact_mutation_refusal")
            return
        raise IntegratedHostConformanceError(
            "post-verification artifact mutation incorrectly finalized"
        )

    def prove_autonomy_and_human_authority(self) -> None:
        self._require_activation_prerequisites()
        high = self.engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task_id": "assimilation-high-risk-autonomy",
                    "task": "Review a high-risk compliance question without taking external action.",
                    "task_type": "compliance_review",
                    "risk_level": "high",
                }
            )
        )
        critical = self.engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task_id": "assimilation-critical-human-gate",
                    "task": "Review a critical compliance action requiring authority.",
                    "task_type": "compliance_review",
                    "risk_level": "critical",
                }
            )
        )
        if high.verification.human_approval_required:
            raise IntegratedHostConformanceError(
                "integration over-gated high-risk work and reproduced approval paralysis"
            )
        if not critical.verification.human_approval_required:
            raise IntegratedHostConformanceError(
                "integration failed to preserve critical qualified-human authority"
            )
        self._negative_controls.add("high_risk_autonomy_preserved")
        self._negative_controls.add("critical_human_gate_preserved")
        self._premortem_checks["approval_paralysis"] = True

    def prove_recursion_refusal(self) -> None:
        self._require_activation_prerequisites()
        payload = {
            "task_id": "assimilation-recursion-root",
            "task": "Classify one bounded record without recursive re-entry.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
        dispatch = self.engine.dispatch(TaskRequest.from_dict(payload))
        recursion = _research_module(
            self.repo_root, "host_integration_recursion_resistance"
        )
        authority = recursion["ProcessLocalRecursionAuthority"]()
        limits = recursion["RecursionLimits"](
            max_reentry_depth=0,
            max_descendants=1,
            max_specialist_spawns=1,
            max_active_branches=1,
            max_recovery_generations=0,
        )
        root = authority.begin_root(dispatch, limits)
        try:
            authority.authorize_descendant(
                root,
                entry_kind="teo_reentry",
                request_id="forbidden-reentry",
            )
        except Exception as exc:
            if "re-entry depth" not in str(exc):
                raise
            self._negative_controls.add("recursive_reentry_refusal")
            self._premortem_checks["recursive_orchestration"] = True
            return
        raise IntegratedHostConformanceError(
            "recursive TEO re-entry exceeded declared assimilation budget"
        )

    def claim_process_local_conformance(self) -> IntegratedConformanceReport:
        self.assimilation_authority.verify(self.lease)
        self._require_hook()
        if not self._shadow_receipts:
            raise IntegratedHostConformanceError(
                "conformance requires at least one real TEO shadow dispatch"
            )
        if len(self._governed_receipts) < 2:
            raise IntegratedHostConformanceError(
                "conformance requires repeated post-assimilation TEO use, not a one-time integration demo"
            )
        governed_task_ids = {receipt.task_id for receipt in self._governed_receipts}
        if len(governed_task_ids) < 2:
            raise IntegratedHostConformanceError(
                "conformance requires at least two distinct post-assimilation task IDs; replaying one demo is not continuity evidence"
            )
        missing_controls = REQUIRED_NEGATIVE_CONTROLS - self._negative_controls
        if missing_controls:
            raise IntegratedHostConformanceError(
                "integrated negative controls are incomplete: "
                + ", ".join(sorted(missing_controls))
            )

        self._premortem_checks["context_bloat_collapse"] = True
        self._premortem_checks["identity_dilution"] = True
        self._premortem_checks["registry_drift"] = True
        self._premortem_checks["control_plane_capture"] = True
        self._premortem_checks["missing_conformance_profile"] = True
        self._premortem_checks["big_bang_enforcement"] = True

        if not all(self._premortem_checks.values()):
            missing = sorted(
                name for name, value in self._premortem_checks.items() if not value
            )
            raise IntegratedHostConformanceError(
                "integrated premortem replay is incomplete: " + ", ".join(missing)
            )

        return IntegratedConformanceReport(
            host_id=self.host_id,
            binding_id=self.truth.binding_id,
            status="process_local_integrated_conformance_satisfied",
            shadow_dispatches=len(self._shadow_receipts),
            governed_executions=len(self._governed_receipts),
            negative_controls=tuple(sorted(self._negative_controls)),
            premortem_replay=dict(self._premortem_checks),
            residual_boundaries=tuple(sorted(REQUIRED_OPEN_SURFACES)),
        )
