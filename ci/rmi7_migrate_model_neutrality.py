from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

WORKER_FILES = (
    "community/workers/workers.yaml",
    "community/workers/extensions/incident-response-worker.yaml",
    "community/workers/extensions/research-worker.yaml",
    "community/workers/extensions/market-research-worker.yaml",
    "community/workers/extensions/analytics-worker.yaml",
    "community/workers/extensions/user-research-worker.yaml",
    "community/workers/extensions/compliance-worker.yaml",
    "community/workers/extensions/systems-engineering-worker.yaml",
    "community/workers/extensions/platform-reliability-core-workers.yaml",
    "community/workers/extensions/platform-reliability-operations-workers.yaml",
    "community/workers/extensions/physical-systems-workers.yaml",
    "community/workers/extensions/assurance-workers.yaml",
    "community/workers/extensions/principal-engineering-active-workers.yaml",
    "community/workers/extensions/specialist-completion-workers.yaml",
    "community/workers/extensions/runtime-worker-overrides.yaml",
)

ROUTING_FILES = (
    "policy/routing/core/routing.yaml",
    "policy/routing/extensions/mission-control-routing.yaml",
    "policy/routing/extensions/research-routing.yaml",
    "policy/routing/extensions/review-routing.yaml",
    "policy/routing/extensions/principal-engineering-routing.yaml",
    "policy/routing/extensions/specialist-spawn-routing.yaml",
)

OLD_SPECIALIST_POLICY = "policy/routing/core/specialist-model-routing.yaml"
NEW_SPECIALIST_POLICY = "policy/routing/core/specialist-selection-policy.yaml"
COMPATIBILITY_DEFAULTS = "policy/routing/core/runtime-compatibility-defaults.yaml"

TEMPLATE_RENAMES = {
    "opus_critical_reasoning": "critical_reasoning",
    "sol_deep_engineering": "deep_engineering",
    "terra_engineering_execution": "engineering_execution",
    "gemini_research": "research_synthesis",
    "sonnet_semantic": "semantic_synthesis",
    "gemini_flash_multimodal": "multimodal_analysis",
    "luna_throughput": "throughput",
}

PROFILE_PURPOSES = {
    "critical_reasoning": "high-consequence reasoning with provider-diverse fallback and verification",
    "deep_engineering": "deep technical reasoning and implementation-aware verification",
    "engineering_execution": "implementation, debugging, and executable verification",
    "research_synthesis": "current evidence synthesis with independent technical challenge",
    "semantic_synthesis": "requirements, strategy, writing, and semantic review",
    "multimodal_analysis": "visual and cross-modal interpretation with technical follow-up",
    "throughput": "bounded economical throughput with sampled or targeted verification",
}


def _load(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"YAML root must be a mapping: {relative}")
    return data


def _dump(relative: str, data: dict[str, Any]) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )


def _compose_workers() -> dict[str, dict[str, Any]]:
    base = _load(WORKER_FILES[0])
    workers = deepcopy(base.get("workers", {}))
    if not isinstance(workers, dict):
        raise SystemExit("canonical workers registry must be a mapping")
    for relative in WORKER_FILES[1:]:
        data = _load(relative)
        extension_workers = data.get("workers", {})
        if not isinstance(extension_workers, dict):
            raise SystemExit(f"workers must be a mapping: {relative}")
        duplicate = sorted(set(workers).intersection(extension_workers))
        if duplicate:
            raise SystemExit(f"duplicate worker definitions in {relative}: {', '.join(duplicate)}")
        workers.update(deepcopy(extension_workers))
        overrides = data.get("worker_overrides", {})
        if not isinstance(overrides, dict):
            raise SystemExit(f"worker_overrides must be a mapping: {relative}")
        for name, override in overrides.items():
            if name not in workers or not isinstance(override, dict):
                raise SystemExit(f"invalid worker override for {name}: {relative}")
            workers[name].update(deepcopy(override))
    return workers


def _compose_routes() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    base = _load(ROUTING_FILES[0])
    routes = deepcopy(base.get("routing", {}))
    if not isinstance(routes, dict):
        raise SystemExit("canonical routing registry must be a mapping")
    for relative in ROUTING_FILES[1:]:
        data = _load(relative)
        extension_routes = data.get("routing", {})
        if not isinstance(extension_routes, dict):
            raise SystemExit(f"routing must be a mapping: {relative}")
        duplicate = sorted(set(routes).intersection(extension_routes))
        if duplicate:
            raise SystemExit(f"duplicate route definitions in {relative}: {', '.join(duplicate)}")
        routes.update(deepcopy(extension_routes))
    for route in routes.values():
        if isinstance(route, dict) and "escalation" in route:
            route["conditional_escalation"] = route.pop("escalation")
    task_routing = deepcopy(base.get("task_routing", {}))
    fallback_order = deepcopy(base.get("fallback_order", {}))
    return routes, task_routing, fallback_order


def _candidate_identity(candidate: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key in ("agent", "model", "profile", "reasoning", "reasoning_by_risk", "mode"):
        if key in candidate:
            result[key] = deepcopy(candidate[key])
    return result


def _candidate_defaults(value: Any) -> Any:
    if isinstance(value, dict) and value.get("model"):
        return _candidate_identity(value)
    if isinstance(value, list):
        candidates = [_candidate_identity(item) for item in value if isinstance(item, dict) and item.get("model")]
        return candidates or None
    return None


def _extract_route_defaults(routes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for route_name, route in routes.items():
        if not isinstance(route, dict):
            continue
        defaults: dict[str, Any] = {}
        for key, value in route.items():
            extracted = _candidate_defaults(value)
            if extracted:
                defaults[key] = extracted
        if defaults:
            result[route_name] = defaults
    return result


def _extract_task_routing_defaults(task_routing: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in task_routing.items():
        extracted = _candidate_defaults(value)
        if extracted:
            result[key] = extracted
    return result


def _normalize_fallback_order(fallback_order: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for family, values in fallback_order.items():
        if not isinstance(values, list):
            continue
        candidates = [_candidate_identity(item) for item in values if isinstance(item, dict) and item.get("model")]
        if candidates:
            result[str(family)] = candidates
    return result


def _strip_candidate_identity(value: Any) -> None:
    if isinstance(value, dict):
        had_model = bool(value.get("model"))
        if had_model:
            for key in ("agent", "model", "profile", "reasoning", "reasoning_by_risk", "mode"):
                value.pop(key, None)
        for key in list(value):
            _strip_candidate_identity(value[key])
            nested = value.get(key)
            if isinstance(nested, list) and nested and all(isinstance(item, dict) and not item for item in nested):
                value.pop(key, None)
    elif isinstance(value, list):
        for item in value:
            _strip_candidate_identity(item)


def _strip_worker_sources() -> None:
    for relative in WORKER_FILES:
        data = _load(relative)
        if relative == WORKER_FILES[0]:
            required = data.get("worker_template", {}).get("required_fields", [])
            if isinstance(required, list):
                data["worker_template"]["required_fields"] = [
                    item for item in required if item not in {"preferred_implementations", "fallbacks"}
                ]
        for collection in (data.get("workers", {}), data.get("worker_overrides", {})):
            if isinstance(collection, dict):
                for worker in collection.values():
                    if isinstance(worker, dict):
                        worker.pop("preferred_implementations", None)
                        worker.pop("fallbacks", None)
        if relative.endswith("runtime-worker-overrides.yaml"):
            data["policy"] = (
                "Runtime-specific implementation defaults belong to the dedicated runtime compatibility/defaults layer, "
                "not worker responsibility definitions. Worker overrides may change responsibility metadata only."
            )
        data["reviewed_at"] = "2026-08-23"
        _dump(relative, data)


def _strip_routing_sources() -> None:
    for relative in ROUTING_FILES:
        data = _load(relative)
        _strip_candidate_identity(data)
        if relative == ROUTING_FILES[0]:
            data.pop("fallback_order", None)
            data["runtime_compatibility_defaults"] = COMPATIBILITY_DEFAULTS
            data["reviewed_at"] = "2026-08-23"
        else:
            data["reviewed_at"] = "2026-08-23"
            policy = data.get("policy")
            if isinstance(policy, str):
                policy = policy.replace("implementation routes", "responsibility routes")
                policy = policy.replace("implementation route", "responsibility route")
                policy = policy.replace("specialist-model policy", "specialist selection policy")
                data["policy"] = policy
        _dump(relative, data)


def _specialist_layers() -> tuple[dict[str, Any], dict[str, Any]]:
    old = _load(OLD_SPECIALIST_POLICY)
    templates = old.get("templates", {})
    assignments = old.get("specialists", {})
    if not isinstance(templates, dict) or not isinstance(assignments, dict):
        raise SystemExit("specialist model policy must contain templates and specialists")

    compatibility_profiles: dict[str, Any] = {}
    for old_name, template in templates.items():
        new_name = TEMPLATE_RENAMES.get(str(old_name))
        if not new_name:
            raise SystemExit(f"missing neutral template rename for {old_name}")
        compatibility_profiles[new_name] = deepcopy(template)

    neutral_assignments: dict[str, Any] = {}
    for specialist, assignment in assignments.items():
        if not isinstance(assignment, dict) or not assignment.get("template"):
            raise SystemExit(f"invalid specialist assignment: {specialist}")
        old_name = str(assignment["template"])
        neutral_assignments[str(specialist)] = {"selection_profile": TEMPLATE_RENAMES[old_name]}

    policy = {
        "version": 2.0,
        "status": "active",
        "reviewed_at": "2026-08-23",
        "policy": (
            "Specialists remain model- and provider-independent responsibility definitions. "
            "This policy assigns only provider-neutral runtime selection profiles; concrete implementation defaults "
            f"live exclusively in {COMPATIBILITY_DEFAULTS}."
        ),
        "rules": [
            "team_and_worker_route_resolves_before_specialist_selection_profile",
            "selection_profile_cannot_change_team_worker_specialist_or_authority",
            "selection_profile_cannot_widen_risk_or_live_scope",
            "concrete_implementation_selection_remains_runtime_bound",
            "connection_method_does_not_affect_runtime_fitness",
        ],
        "profiles": {
            name: {"purpose": PROFILE_PURPOSES[name]} for name in TEMPLATE_RENAMES.values()
        },
        "specialists": neutral_assignments,
    }
    return compatibility_profiles, policy


def main() -> None:
    workers = _compose_workers()
    routes, task_routing, fallback_order = _compose_routes()
    old_specialist = _load(OLD_SPECIALIST_POLICY)
    specialist_profiles, specialist_policy = _specialist_layers()

    worker_defaults: dict[str, Any] = {}
    for name, worker in workers.items():
        if not isinstance(worker, dict):
            continue
        preferred = [str(item) for item in worker.get("preferred_implementations", [])]
        fallbacks = [str(item) for item in worker.get("fallbacks", [])]
        if preferred or fallbacks:
            worker_defaults[str(name)] = {
                "preferred_implementations": preferred,
                "fallbacks": fallbacks,
            }

    compatibility = {
        "version": 1.0,
        "status": "active",
        "reviewed_at": "2026-08-23",
        "model_registry": "policy/routing/core/implementation-defaults.yaml",
        "purpose": (
            "Reference-router compatibility and known-good defaults only. These named implementations seed "
            "RuntimeSelectionPort when an installation-specific selector is not injected. They are not worker, team, "
            "specialist, task-route, capability, risk, or authority identity and cannot widen lifecycle eligibility."
        ),
        "worker_defaults": worker_defaults,
        "task_routing_defaults": _extract_task_routing_defaults(task_routing),
        "task_routes": _extract_route_defaults(routes),
        "fallback_order": _normalize_fallback_order(fallback_order),
        "specialist_profiles": specialist_profiles,
        "migration_source": {
            "workers": list(WORKER_FILES),
            "routing": list(ROUTING_FILES),
            "specialist_policy": OLD_SPECIALIST_POLICY,
            "specialist_policy_version": old_specialist.get("version"),
        },
    }

    _dump(COMPATIBILITY_DEFAULTS, compatibility)
    _dump(NEW_SPECIALIST_POLICY, specialist_policy)
    _strip_worker_sources()
    _strip_routing_sources()
    (ROOT / OLD_SPECIALIST_POLICY).unlink()


if __name__ == "__main__":
    main()
