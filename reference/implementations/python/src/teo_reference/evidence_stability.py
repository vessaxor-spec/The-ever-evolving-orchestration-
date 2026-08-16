from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

import yaml

from .evidence import EXPECTED_PILOT, load_registry, validate_registry

QUALIFICATION_POLICY = Path("policy/specialists/evidence-stability-qualification.yaml")
REQUIRED_MUTATIONS = (
    "authority_unavailable",
    "undeclared_redirect_host",
    "url_host_not_declared",
    "expired_evidence",
    "excessive_evidence_lifetime",
    "tier_downgrade",
    "verification_independence_removed",
    "same_preparer_verifier",
    "stale_behavior_weakened",
    "conflict_behavior_weakened",
    "pilot_scope_expanded",
    "unknown_schema_field",
    "non_https_authority",
    "duplicate_claim_id",
    "specialist_card_blob_mismatch",
)

Resolver = Callable[[str, set[str]], str | None]


def load_qualification_policy(root: Path) -> dict[str, Any]:
    payload = yaml.safe_load((root / QUALIFICATION_POLICY).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evidence stability qualification policy must be an object")
    return payload


def validate_qualification_policy(policy: dict[str, Any], registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if policy.get("version") != 0.1:
        errors.append("qualification policy version must remain 0.1")
    if policy.get("status") != "active":
        errors.append("qualification policy status must remain active")
    if policy.get("registry_path") != "policy/specialists/evidence-pilot.yaml":
        errors.append("qualification policy must bind the active evidence pilot registry")

    qualification = policy.get("qualification")
    if not isinstance(qualification, dict):
        return errors + ["qualification must be an object"]
    if qualification.get("calendar_wait_required") is not False:
        errors.append("calendar waiting must not be a qualification requirement")
    if qualification.get("minimum_clean_resolution_replays") != 5:
        errors.append("minimum_clean_resolution_replays must remain 5")
    if qualification.get("minimum_repeatability_runs") != 3:
        errors.append("minimum_repeatability_runs must remain 3")
    for key in (
        "require_all_declared_authorities_per_replay",
        "require_repeatable_normalized_result",
        "require_controlled_authority_move",
        "require_external_network_resolution_observation",
    ):
        if qualification.get(key) is not True:
            errors.append(f"{key} must remain true")
    if tuple(qualification.get("required_mutation_classes", ())) != REQUIRED_MUTATIONS:
        errors.append("required_mutation_classes must match the governed mutation matrix")

    monitoring = policy.get("continuous_monitoring")
    if not isinstance(monitoring, dict):
        return errors + ["continuous_monitoring must be an object"]
    registry_cadence = registry.get("controls", {}).get("source_resolution_cadence_days")
    if monitoring.get("source_resolution_cadence_days") != registry_cadence:
        errors.append("continuous monitoring cadence must match the active evidence registry")
    if monitoring.get("qualification_does_not_replace_monitoring") is not True:
        errors.append("qualification must not replace continuous authority monitoring")

    expansion = policy.get("expansion_authority")
    if not isinstance(expansion, dict):
        return errors + ["expansion_authority must be an object"]
    if expansion.get("explicit_next_batch_approval_required") is not True:
        errors.append("explicit next-batch approval must remain required")
    if expansion.get("qualification_auto_authorizes_expansion") is not False:
        errors.append("qualification must not auto-authorize registry expansion")
    return errors


def _claim_count(registry: dict[str, Any]) -> int:
    return sum(len(entry["claims"]) for entry in registry["pilot_specialists"].values())


def _first_claim(registry: dict[str, Any], specialist: str) -> dict[str, Any]:
    return registry["pilot_specialists"][specialist]["claims"][0]


def _success_resolver(url: str, expected_hosts: set[str]) -> str | None:
    del url, expected_hosts
    return None


def _stage_repo(root: Path, destination: Path) -> None:
    paths = [
        Path("policy/specialists/evidence-pilot.yaml"),
        Path("policy/specialists/freshness.yaml"),
        QUALIFICATION_POLICY,
        Path("reference/schemas/specialist-evidence-pilot.schema.json"),
    ]
    registry = load_registry(root)
    for entry in registry["pilot_specialists"].values():
        paths.append(Path(entry["card_path"]))
    for relative in paths:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / relative, target)


def _resolution_replay(
    registry: dict[str, Any],
    root: Path,
    *,
    as_of: dt.date,
    resolver: Resolver,
    claim_count: int,
) -> dict[str, Any]:
    observations: list[dict[str, Any]] = []

    def recording_resolver(url: str, expected_hosts: set[str]) -> str | None:
        error = resolver(url, expected_hosts)
        observations.append(
            {
                "url": url,
                "expected_hosts": sorted(expected_hosts),
                "error": error,
            }
        )
        return error

    errors = validate_registry(
        registry,
        root,
        as_of=as_of,
        resolve=True,
        resolver=recording_resolver,
    )
    return {
        "passed": not errors,
        "resolved_authorities": len(observations) if not errors else 0,
        "expected_authorities": claim_count,
        "observations": observations,
        "errors": errors,
    }


def _mutation_result(
    staged_root: Path,
    baseline: dict[str, Any],
    name: str,
    *,
    as_of: dt.date,
) -> dict[str, Any]:
    registry = copy.deepcopy(baseline)
    resolver: Resolver = _success_resolver

    if name == "authority_unavailable":
        resolver = lambda _url, _hosts: "authority could not be resolved: simulated outage"
    elif name == "undeclared_redirect_host":
        resolver = lambda _url, _hosts: "authority redirected to undeclared host attacker.example"
    elif name == "url_host_not_declared":
        _first_claim(registry, "embedded-engineer")["authority"]["expected_hosts"] = ["www.iso.org"]
    elif name == "expired_evidence":
        _first_claim(registry, "loan-officer-assistant")["expires_at"] = (as_of - dt.timedelta(days=1)).isoformat()
    elif name == "excessive_evidence_lifetime":
        claim = _first_claim(registry, "loan-officer-assistant")
        claim["expires_at"] = (
            dt.date.fromisoformat(str(claim["verified_at"])) + dt.timedelta(days=31)
        ).isoformat()
    elif name == "tier_downgrade":
        _first_claim(registry, "compliance-auditor")["authority"]["tier"] = 2
    elif name == "verification_independence_removed":
        _first_claim(registry, "compliance-auditor")["verification"]["independent"] = False
    elif name == "same_preparer_verifier":
        verification = _first_claim(registry, "compliance-auditor")["verification"]
        verification["verified_by"] = verification["prepared_by"]
    elif name == "stale_behavior_weakened":
        _first_claim(registry, "legal-operations")["required_behavior"]["stale_or_unavailable"] = "warn_only"
    elif name == "conflict_behavior_weakened":
        _first_claim(registry, "legal-operations")["required_behavior"]["conflict"] = "prefer_first_source"
    elif name == "pilot_scope_expanded":
        registry["pilot_specialists"]["extra-specialist"] = copy.deepcopy(
            registry["pilot_specialists"]["embedded-engineer"]
        )
    elif name == "unknown_schema_field":
        _first_claim(registry, "legal-operations")["unsupported_field"] = True
    elif name == "non_https_authority":
        claim = _first_claim(registry, "embedded-engineer")
        claim["authority"]["url"] = claim["authority"]["url"].replace("https://", "http://", 1)
    elif name == "duplicate_claim_id":
        _first_claim(registry, "tax-strategist")["id"] = _first_claim(registry, "legal-operations")["id"]
    elif name == "specialist_card_blob_mismatch":
        card_path = staged_root / registry["pilot_specialists"]["embedded-engineer"]["card_path"]
        card_path.write_text(
            card_path.read_text(encoding="utf-8") + "\nqualification tamper\n",
            encoding="utf-8",
        )
    else:
        raise ValueError(f"unsupported qualification mutation {name}")

    errors = validate_registry(
        registry,
        staged_root,
        as_of=as_of,
        resolve=True,
        resolver=resolver,
    )
    return {"case": name, "killed": bool(errors), "errors": errors}


def _validate_external_observation(
    observation: dict[str, Any] | None, claim_count: int
) -> list[str]:
    if not isinstance(observation, dict):
        return ["external network resolution observation is required"]
    errors: list[str] = []
    if observation.get("conclusion") != "success":
        errors.append("external network observation must have success conclusion")
    if observation.get("resolved_authorities") != claim_count:
        errors.append("external network observation must resolve every declared authority")
    run_id = observation.get("run_id")
    if not isinstance(run_id, int) or isinstance(run_id, bool) or run_id <= 0:
        errors.append("external network observation requires a positive GitHub Actions run_id")
    head_sha = observation.get("head_sha")
    if (
        not isinstance(head_sha, str)
        or len(head_sha) != 40
        or any(c not in "0123456789abcdef" for c in head_sha.lower())
    ):
        errors.append("external network observation requires an exact 40-character head_sha")
    if not isinstance(observation.get("workflow"), str) or not observation["workflow"].strip():
        errors.append("external network observation requires a workflow identity")
    return errors


def run_stability_qualification(
    root: Path,
    *,
    as_of: dt.date | None = None,
    resolver: Resolver = _success_resolver,
    external_network_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    as_of = as_of or dt.date.today()
    registry = load_registry(root)
    policy = load_qualification_policy(root)
    policy_errors = validate_qualification_policy(policy, registry)
    claim_count = _claim_count(registry)

    baseline_errors = validate_registry(registry, root, as_of=as_of, resolve=False)
    clean_replays: list[dict[str, Any]] = []
    replay_count = int(
        policy.get("qualification", {}).get("minimum_clean_resolution_replays", 0)
    )
    for index in range(replay_count):
        replay = _resolution_replay(
            registry,
            root,
            as_of=as_of,
            resolver=resolver,
            claim_count=claim_count,
        )
        clean_replays.append({"replay": index + 1, **replay})

    repeatability_runs = int(
        policy.get("qualification", {}).get("minimum_repeatability_runs", 0)
    )
    repeatability_results: list[dict[str, Any]] = []
    repeatability_digests: list[str] = []
    for index in range(repeatability_runs):
        replay = _resolution_replay(
            registry,
            root,
            as_of=as_of,
            resolver=resolver,
            claim_count=claim_count,
        )
        normalized = json.dumps(replay, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        repeatability_digests.append(digest)
        repeatability_results.append(
            {"run": index + 1, "digest": digest, **replay}
        )
    repeatable = (
        bool(repeatability_digests)
        and len(set(repeatability_digests)) == 1
        and all(
            item["passed"]
            and item["resolved_authorities"] == claim_count
            for item in repeatability_results
        )
    )

    mutation_results: list[dict[str, Any]] = []
    for name in REQUIRED_MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="teo-evidence-stability-") as temp:
            staged_root = Path(temp)
            _stage_repo(root, staged_root)
            mutation_results.append(
                _mutation_result(
                    staged_root,
                    load_registry(staged_root),
                    name,
                    as_of=as_of,
                )
            )

    controlled = copy.deepcopy(registry)
    iso_claim = _first_claim(controlled, "embedded-engineer")
    original_statement = iso_claim["statement"]
    original_verification = copy.deepcopy(iso_claim["verification"])
    iso_claim["authority"]["url"] = (
        "https://committee.iso.org/ru/standard/82075.html?qualification-move=1"
    )
    controlled_errors = validate_registry(
        controlled,
        root,
        as_of=as_of,
        resolve=True,
        resolver=resolver,
    )
    controlled_move = (
        not controlled_errors
        and iso_claim["statement"] == original_statement
        and iso_claim["verification"] == original_verification
    )

    external_errors = _validate_external_observation(
        external_network_observation, claim_count
    )
    all_mutations_killed = all(item["killed"] for item in mutation_results)
    clean = all(
        item["passed"] and item["resolved_authorities"] == claim_count
        for item in clean_replays
    )
    qualified = not (
        policy_errors
        or baseline_errors
        or external_errors
        or not clean
        or not repeatable
        or not all_mutations_killed
        or not controlled_move
    )

    return {
        "qualified": qualified,
        "as_of": as_of.isoformat(),
        "registry_path": policy.get("registry_path"),
        "pilot_specialists": sorted(EXPECTED_PILOT),
        "baseline_claim_count": claim_count,
        "policy_errors": policy_errors,
        "baseline_errors": baseline_errors,
        "clean_resolution_replays": clean_replays,
        "repeatability": {
            "runs": repeatability_runs,
            "passed": repeatable,
            "digest": repeatability_digests[0] if repeatability_digests else None,
            "digests": repeatability_digests,
            "results": repeatability_results,
        },
        "mutation_results": mutation_results,
        "mutations_killed": sum(1 for item in mutation_results if item["killed"]),
        "mutations_total": len(mutation_results),
        "controlled_authority_move": {
            "passed": controlled_move,
            "errors": controlled_errors,
        },
        "external_network_observation": external_network_observation,
        "external_network_errors": external_errors,
        "continuous_monitoring": {
            "source_resolution_cadence_days": registry["controls"][
                "source_resolution_cadence_days"
            ],
            "calendar_wait_gate": False,
        },
        "expansion_authority": {
            "explicit_next_batch_approval_required": True,
            "expansion_auto_authorized": False,
        },
    }
