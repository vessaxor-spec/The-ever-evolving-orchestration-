from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .benchmark_lab import BENCHMARK_LAB_VERSION, BenchmarkExperimentReport
from .provider_adapter import ProviderAdapterContractError

BENCHMARK_CONCLUSION_SCHEMA_PATH = "reference/schemas/benchmark-conclusion.schema.json"
BENCHMARK_CONCLUSION_VERIFICATION_SCHEMA_PATH = (
    "reference/schemas/benchmark-conclusion-verification.schema.json"
)
BENCHMARK_CONCLUSION_HANDOFF_SCHEMA_PATH = (
    "reference/schemas/benchmark-conclusion-handoff.schema.json"
)


def _canonical_sha256(data: Mapping[str, Any], *, omit: str | None = None) -> str:
    canonical = dict(data)
    if omit is not None:
        canonical.pop(omit, None)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_schema(repo_root: str | Path, relative_path: str) -> dict[str, Any]:
    path = Path(repo_root) / relative_path
    if not path.is_file():
        raise ProviderAdapterContractError(f"Benchmark conclusion schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Benchmark conclusion schema could not be loaded: {path}"
        ) from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Benchmark conclusion schema must be an object")
    return raw


def _validate_schema(
    data: dict[str, Any],
    *,
    repo_root: str | Path,
    relative_path: str,
    label: str,
) -> None:
    validator = Draft202012Validator(_load_schema(repo_root, relative_path))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        path = ".".join(str(item) for item in first.path) or "<root>"
        raise ProviderAdapterContractError(
            f"{label} schema validation failed at {path}: {first.message}"
        )


def _actor_semantics(actor: dict[str, Any], *, label: str) -> None:
    actor_type = str(actor["actor_type"])
    provider = actor.get("provider_family")
    model = actor.get("model")
    if (provider is None) != (model is None):
        raise ProviderAdapterContractError(
            f"{label} provider_family and model must either both be present or both be null"
        )
    if actor_type == "human" and (provider is not None or model is not None):
        raise ProviderAdapterContractError(f"{label} human actor cannot declare a model")
    if actor_type == "system" and (provider is not None or model is not None):
        raise ProviderAdapterContractError(f"{label} system actor cannot declare a model")
    if actor_type == "specialist" and (provider is None or model is None):
        raise ProviderAdapterContractError(
            f"{label} specialist actor must declare provider_family and model"
        )


def _validate_conclusion_semantics(data: dict[str, Any]) -> None:
    _actor_semantics(data["originator"], label="Benchmark conclusion originator")
    expected = data["consequence_level"] == "consequential"
    if bool(data["independent_verification_required"]) != expected:
        raise ProviderAdapterContractError(
            "Benchmark conclusion independent_verification_required must match consequence_level"
        )


def _validate_verification_semantics(data: dict[str, Any]) -> None:
    _actor_semantics(data["verifier"], label="Benchmark conclusion verifier")
    verdicts = list(data["checks"].values())
    failures = [value for value in verdicts if value == "fail"]
    uncertain = [value for value in verdicts if value == "uncertain"]
    decision = data["decision"]
    human_reason = data["human_reason"]
    if decision == "verified":
        if failures or uncertain or human_reason != "none":
            raise ProviderAdapterContractError(
                "Verified benchmark conclusion requires all checks to pass and no human reason"
            )
    elif decision == "rejected":
        if not failures or human_reason != "none":
            raise ProviderAdapterContractError(
                "Rejected benchmark conclusion requires at least one failed check and no human reason"
            )
    elif decision == "needs_human":
        if failures or not uncertain or human_reason == "none":
            raise ProviderAdapterContractError(
                "needs_human benchmark conclusion verification requires uncertainty, no failed checks, and an explicit human reason"
            )


def _validate_handoff_semantics(data: dict[str, Any]) -> None:
    performed = bool(data["independent_verification_performed"])
    verification_id = data["verification_id"]
    verification_hash = data["verification_integrity_sha256"]
    if performed != (verification_id is not None and verification_hash is not None):
        raise ProviderAdapterContractError(
            "Benchmark conclusion handoff verification references do not match independent_verification_performed"
        )
    if data["consequence_level"] == "consequential" and not performed:
        raise ProviderAdapterContractError(
            "Consequential benchmark conclusion cannot advance without independent verification"
        )
    if not performed and data["status"] != "ready_for_review":
        raise ProviderAdapterContractError(
            "Unverified routine benchmark conclusion handoff must remain ready_for_review"
        )


@dataclass(frozen=True, slots=True)
class BenchmarkConclusionRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkConclusionRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_CONCLUSION_SCHEMA_PATH,
            label="Benchmark conclusion",
        )
        _validate_conclusion_semantics(data)
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError(
                "Benchmark conclusion integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class BenchmarkConclusionVerificationRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkConclusionVerificationRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_CONCLUSION_VERIFICATION_SCHEMA_PATH,
            label="Benchmark conclusion verification",
        )
        _validate_verification_semantics(data)
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError(
                "Benchmark conclusion verification integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class BenchmarkConclusionHandoffRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkConclusionHandoffRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_CONCLUSION_HANDOFF_SCHEMA_PATH,
            label="Benchmark conclusion handoff",
        )
        _validate_handoff_semantics(data)
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError(
                "Benchmark conclusion handoff integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def build_benchmark_conclusion(
    report: BenchmarkExperimentReport,
    *,
    conclusion_kind: str,
    consequence_level: str,
    statement: str,
    evidence_refs: Sequence[str],
    originator: Mapping[str, Any],
    repo_root: str | Path,
    created_at: str | None = None,
) -> BenchmarkConclusionRecord:
    report_data = report.to_dict()
    statement_text = str(statement or "").strip()
    refs = list(dict.fromkeys(str(item).strip() for item in evidence_refs if str(item).strip()))
    if not statement_text:
        raise ProviderAdapterContractError("Benchmark conclusion statement is required")
    if not refs:
        raise ProviderAdapterContractError("Benchmark conclusion requires evidence_refs")
    if conclusion_kind not in {
        "descriptive_summary",
        "comparative_claim",
        "regression_finding",
        "evidence_insufficiency",
    }:
        raise ProviderAdapterContractError(
            f"Unsupported benchmark conclusion kind: {conclusion_kind}"
        )
    if consequence_level not in {"routine", "consequential"}:
        raise ProviderAdapterContractError(
            f"Unsupported benchmark conclusion consequence level: {consequence_level}"
        )

    if consequence_level == "consequential" and conclusion_kind in {
        "comparative_claim",
        "regression_finding",
    }:
        if report_data["comparability_status"] != "passed":
            raise ProviderAdapterContractError(
                "Consequential comparative benchmark conclusion requires passed comparability"
            )
        if report_data["evidence_sufficiency"] == "insufficient":
            raise ProviderAdapterContractError(
                "Consequential comparative benchmark conclusion requires sufficient benchmark evidence"
            )
        if report_data["verifier_disagreement"]["status"] != "measured":
            raise ProviderAdapterContractError(
                "Consequential comparative benchmark conclusion requires measured multi-verifier disagreement"
            )
    if conclusion_kind == "regression_finding" and not report_data["regression_signals"]:
        raise ProviderAdapterContractError(
            "Regression benchmark conclusion requires at least one report regression signal"
        )

    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    originator_payload = {
        "actor_type": originator.get("actor_type"),
        "actor_id": originator.get("actor_id"),
        "provider_family": originator.get("provider_family"),
        "model": originator.get("model"),
    }
    seed = json.dumps(
        {
            "report": report_data["integrity_sha256"],
            "kind": conclusion_kind,
            "consequence": consequence_level,
            "statement": statement_text,
            "originator": originator_payload,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "benchmark_lab_version": BENCHMARK_LAB_VERSION,
        "record_type": "benchmark_conclusion",
        "conclusion_id": f"conclusion-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:20]}",
        "created_at": timestamp,
        "experiment_id": report_data["experiment_id"],
        "report_integrity_sha256": report_data["integrity_sha256"],
        "conclusion_kind": conclusion_kind,
        "consequence_level": consequence_level,
        "statement": statement_text,
        "evidence_refs": refs,
        "originator": originator_payload,
        "independent_verification_required": consequence_level == "consequential",
        "policy_write_authority": False,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return BenchmarkConclusionRecord.from_dict(payload, repo_root=repo_root)


def _assert_independent(
    conclusion: BenchmarkConclusionRecord,
    verifier: Mapping[str, Any],
) -> None:
    originator = conclusion.to_dict()["originator"]
    if str(verifier.get("actor_id") or "") == str(originator["actor_id"]):
        raise ProviderAdapterContractError(
            "Benchmark conclusion verifier must be independent from the originator"
        )
    origin_provider = originator.get("provider_family")
    verifier_provider = verifier.get("provider_family")
    if origin_provider is not None and verifier_provider == origin_provider:
        raise ProviderAdapterContractError(
            "Model-originated consequential benchmark conclusion requires provider-diverse verification"
        )
    origin_model = originator.get("model")
    verifier_model = verifier.get("model")
    if origin_model is not None and verifier_model == origin_model:
        raise ProviderAdapterContractError(
            "Benchmark conclusion verifier cannot reuse the originator model"
        )


def build_benchmark_conclusion_verification(
    conclusion: BenchmarkConclusionRecord,
    *,
    verifier: Mapping[str, Any],
    decision: str,
    checks: Mapping[str, str],
    human_reason: str,
    evidence: Sequence[str],
    repo_root: str | Path,
    verified_at: str | None = None,
) -> BenchmarkConclusionVerificationRecord:
    _assert_independent(conclusion, verifier)
    conclusion_data = conclusion.to_dict()
    evidence_items = list(dict.fromkeys(str(item).strip() for item in evidence if str(item).strip()))
    if not evidence_items:
        raise ProviderAdapterContractError(
            "Benchmark conclusion verification requires evidence"
        )
    verifier_payload = {
        "actor_type": verifier.get("actor_type"),
        "actor_id": verifier.get("actor_id"),
        "provider_family": verifier.get("provider_family"),
        "model": verifier.get("model"),
    }
    timestamp = verified_at or datetime.now(timezone.utc).isoformat()
    seed = json.dumps(
        {
            "conclusion": conclusion_data["integrity_sha256"],
            "verifier": verifier_payload,
            "decision": decision,
            "verified_at": timestamp,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "benchmark_lab_version": BENCHMARK_LAB_VERSION,
        "record_type": "benchmark_conclusion_verification",
        "verification_id": (
            "conclusion-verification-"
            + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "verified_at": timestamp,
        "conclusion_id": conclusion_data["conclusion_id"],
        "conclusion_integrity_sha256": conclusion_data["integrity_sha256"],
        "report_integrity_sha256": conclusion_data["report_integrity_sha256"],
        "verifier": verifier_payload,
        "independent": True,
        "decision": decision,
        "checks": {
            "evidence_support": checks.get("evidence_support"),
            "uncertainty_preserved": checks.get("uncertainty_preserved"),
            "authority_boundary_preserved": checks.get("authority_boundary_preserved"),
            "unsupported_causality_absent": checks.get("unsupported_causality_absent"),
        },
        "human_reason": human_reason,
        "evidence": evidence_items,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return BenchmarkConclusionVerificationRecord.from_dict(payload, repo_root=repo_root)


def _validate_verification_binding(
    conclusion: BenchmarkConclusionRecord,
    verification: BenchmarkConclusionVerificationRecord,
) -> None:
    conclusion_data = conclusion.to_dict()
    verification_data = verification.to_dict()
    if verification_data["conclusion_id"] != conclusion_data["conclusion_id"]:
        raise ProviderAdapterContractError(
            "Benchmark conclusion verification references a different conclusion"
        )
    if (
        verification_data["conclusion_integrity_sha256"]
        != conclusion_data["integrity_sha256"]
    ):
        raise ProviderAdapterContractError(
            "Benchmark conclusion verification does not bind the exact conclusion content"
        )
    if (
        verification_data["report_integrity_sha256"]
        != conclusion_data["report_integrity_sha256"]
    ):
        raise ProviderAdapterContractError(
            "Benchmark conclusion verification does not bind the source report"
        )
    _assert_independent(conclusion, verification_data["verifier"])


def advance_benchmark_conclusion(
    conclusion: BenchmarkConclusionRecord,
    *,
    repo_root: str | Path,
    verification: BenchmarkConclusionVerificationRecord | None = None,
    created_at: str | None = None,
) -> BenchmarkConclusionHandoffRecord:
    """Create a review handoff without creating policy-write or approval authority."""
    conclusion_data = conclusion.to_dict()
    consequential = conclusion_data["consequence_level"] == "consequential"
    if consequential and verification is None:
        raise ProviderAdapterContractError(
            "Consequential benchmark conclusion requires independent verification before review handoff"
        )

    verification_data: dict[str, Any] | None = None
    if verification is not None:
        _validate_verification_binding(conclusion, verification)
        verification_data = verification.to_dict()
        status = {
            "verified": "ready_for_review",
            "rejected": "rejected",
            "needs_human": "needs_human",
        }[str(verification_data["decision"])]
    else:
        status = "ready_for_review"

    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    seed = json.dumps(
        {
            "conclusion": conclusion_data["integrity_sha256"],
            "verification": (
                verification_data["integrity_sha256"] if verification_data else None
            ),
            "status": status,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    notes = [
        "Review handoff is evidence only and does not modify routing or policy.",
        "This handoff does not satisfy any qualified-human approval requirement.",
    ]
    if consequential:
        notes.append(
            "Consequential conclusion passed through an independent verification handoff before review."
        )
    payload: dict[str, Any] = {
        "benchmark_lab_version": BENCHMARK_LAB_VERSION,
        "record_type": "benchmark_conclusion_handoff",
        "handoff_id": (
            "conclusion-handoff-"
            + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "created_at": timestamp,
        "conclusion_id": conclusion_data["conclusion_id"],
        "conclusion_integrity_sha256": conclusion_data["integrity_sha256"],
        "experiment_id": conclusion_data["experiment_id"],
        "consequence_level": conclusion_data["consequence_level"],
        "destination": "mission_control_or_maintainer_review",
        "status": status,
        "verification_id": (
            verification_data["verification_id"] if verification_data else None
        ),
        "verification_integrity_sha256": (
            verification_data["integrity_sha256"] if verification_data else None
        ),
        "independent_verification_performed": verification_data is not None,
        "policy_write_authority": False,
        "qualified_human_approval_satisfied": False,
        "notes": notes,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return BenchmarkConclusionHandoffRecord.from_dict(payload, repo_root=repo_root)
