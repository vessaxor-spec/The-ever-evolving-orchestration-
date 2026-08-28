from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class RepositoryConfigurationValidationInput:
    """Mutable configuration mappings presented through an immutable validation shell."""

    team_routing: dict[str, Any]
    routing: dict[str, Any]
    runtime_compatibility: dict[str, Any]
    workers: dict[str, Any]
    specialists: dict[str, Any]
    models: dict[str, Any]
    capabilities: dict[str, Any]
    model_evidence: dict[str, Any]


def _known_models(models: dict[str, Any]) -> set[str]:
    known: set[str] = set()
    registry = models.get("models", {})
    if not isinstance(registry, dict):
        return known
    for name, entry in registry.items():
        known.add(str(name))
        if not isinstance(entry, dict):
            continue
        if entry.get("concrete_model"):
            known.add(str(entry["concrete_model"]))
        for candidate in entry.get("candidate_implementations", []):
            known.add(str(candidate))
    return known


def _model_entry(models: dict[str, Any], model: str) -> dict[str, Any]:
    registry = models.get("models", {})
    if not isinstance(registry, dict):
        return {}
    direct = registry.get(model)
    if isinstance(direct, dict):
        return direct
    for entry in registry.values():
        if not isinstance(entry, dict):
            continue
        if entry.get("concrete_model") == model or model in entry.get("candidate_implementations", []):
            return entry
    return {}


def _provider_for_model(models: dict[str, Any], model: str) -> str | None:
    provider = _model_entry(models, model).get("provider_family")
    return str(provider) if provider else None


def _iter_model_candidates(value: Any, path: str = "runtime_compatibility"):
    if isinstance(value, dict):
        if value.get("model"):
            yield path, value
        for key, nested in value.items():
            if key == "model":
                continue
            yield from _iter_model_candidates(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from _iter_model_candidates(nested, f"{path}[{index}]")


_MODEL_IDENTITY_KEYS = {
    "agent",
    "model",
    "profile",
    "reasoning",
    "reasoning_by_risk",
    "preferred_implementations",
    "fallbacks",
}


def _iter_responsibility_model_identity(value: Any, path: str):
    if isinstance(value, dict):
        for key, nested in value.items():
            current = f"{path}.{key}"
            if key in _MODEL_IDENTITY_KEYS:
                yield current
            yield from _iter_responsibility_model_identity(nested, current)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from _iter_responsibility_model_identity(nested, f"{path}[{index}]")


_EXECUTION_KEYS = ("primary", "executor", "executable_review")
_VERIFIER_KEYS = (
    "verifier",
    "executable_verifier",
    "semantic_reviewer",
    "technical_verifier",
    "hypothesis_reviewer",
    "engineering_reasoning_review",
    "semantic_review",
    "synthesis",
)


def validate_repository_configuration(
    configuration: RepositoryConfigurationValidationInput,
) -> list[str]:
    """Return configuration issues using the established deterministic invariant order."""

    issues: list[str] = []
    routes = configuration.team_routing.get("team_routes")
    routing = configuration.routing.get("routing")
    workers = configuration.workers.get("workers")
    runtime_worker_defaults = configuration.runtime_compatibility.get("worker_defaults")
    runtime_task_routes = configuration.runtime_compatibility.get("task_routes")
    runtime_task_routing_defaults = configuration.runtime_compatibility.get("task_routing_defaults")
    runtime_fallback_order = configuration.runtime_compatibility.get("fallback_order")
    runtime_specialist_profiles = configuration.runtime_compatibility.get("specialist_profiles")
    specialists = configuration.specialists.get("specialists")
    models = configuration.models.get("models")
    capabilities = configuration.capabilities.get("capabilities")
    model_evidence = configuration.model_evidence.get("models")

    for name, value in {
        "team_routes": routes,
        "routing": routing,
        "workers": workers,
        "runtime_worker_defaults": runtime_worker_defaults,
        "runtime_task_routes": runtime_task_routes,
        "runtime_task_routing_defaults": runtime_task_routing_defaults,
        "runtime_fallback_order": runtime_fallback_order,
        "runtime_specialist_profiles": runtime_specialist_profiles,
        "specialists": specialists,
        "models": models,
        "capabilities": capabilities,
        "model_evidence": model_evidence,
    }.items():
        if not isinstance(value, dict) or not value:
            issues.append(f"ERROR: missing or empty {name}")

    if issues:
        return issues

    assert isinstance(routes, dict)
    assert isinstance(routing, dict)
    assert isinstance(workers, dict)
    assert isinstance(runtime_worker_defaults, dict)
    assert isinstance(runtime_task_routes, dict)
    assert isinstance(runtime_task_routing_defaults, dict)
    assert isinstance(runtime_fallback_order, dict)
    assert isinstance(runtime_specialist_profiles, dict)
    assert isinstance(specialists, dict)
    assert isinstance(models, dict)
    assert isinstance(model_evidence, dict)

    known_models = _known_models(configuration.models)

    for surface_name, surface in (("workers", configuration.workers), ("routing", configuration.routing)):
        for identity_path in _iter_responsibility_model_identity(surface, surface_name):
            issues.append(
                f"ERROR: model/provider implementation identity is not allowed in responsibility configuration: {identity_path}"
            )

    worker_names = set(workers)
    compatibility_worker_names = set(runtime_worker_defaults)
    if worker_names != compatibility_worker_names:
        missing = sorted(worker_names - compatibility_worker_names)
        extra = sorted(compatibility_worker_names - worker_names)
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        issues.append(
            "ERROR: runtime compatibility worker-default coverage must exactly match active workers: "
            + "; ".join(details)
        )

    reachable_pairs: set[tuple[str, str]] = set()
    for route_name, route in routes.items():
        if route_name not in routing and route_name != "release":
            issues.append(f"WARNING: team route {route_name} has no implementation route")
        worker_name = str(route.get("primary_worker") or "")
        team_name = str(route.get("primary_team") or "")
        if worker_name not in workers:
            issues.append(f"ERROR: route {route_name} references unregistered worker {worker_name}")
        elif workers[worker_name].get("owning_team") != team_name:
            issues.append(
                f"ERROR: route {route_name} selects {team_name}/{worker_name}, but the worker belongs to "
                f"{workers[worker_name].get('owning_team')}"
            )
        else:
            reachable_pairs.add((team_name, worker_name))

        overrides = route.get("worker_override_by_context", {})
        if overrides is not None and not isinstance(overrides, dict):
            issues.append(f"ERROR: route {route_name} worker_override_by_context must be a mapping")
            continue
        for context, override_worker in (overrides or {}).items():
            override_name = str(override_worker)
            if override_name not in workers:
                issues.append(
                    f"ERROR: route {route_name} context {context} references unregistered worker {override_name}"
                )
            elif workers[override_name].get("owning_team") != team_name:
                issues.append(
                    f"ERROR: route {route_name} context {context} selects {team_name}/{override_name}, but the worker belongs to "
                    f"{workers[override_name].get('owning_team')}"
                )
            else:
                reachable_pairs.add((team_name, override_name))

    missing_bindings = sorted(
        {
            str(entry.get("worker_binding"))
            for entry in specialists.values()
            if entry.get("worker_binding") not in workers
        }
    )
    if missing_bindings:
        issues.append(
            "ERROR: specialist bindings without worker definitions: " + ", ".join(missing_bindings)
        )

    unreachable = sorted(
        name
        for name, entry in specialists.items()
        if (
            str(entry.get("primary_team") or ""),
            str(entry.get("worker_binding") or ""),
        )
        not in reachable_pairs
    )
    if unreachable:
        issues.append(
            "ERROR: active specialists without a deterministic Team -> Worker spawn path: "
            + ", ".join(unreachable)
        )

    for worker_name, worker in workers.items():
        if not isinstance(worker, dict):
            issues.append(f"ERROR: worker {worker_name} must be a mapping")
            continue
        team = str(worker.get("owning_team") or "")
        required_capabilities = worker.get("required_capabilities", [])
        if not isinstance(required_capabilities, list) or not required_capabilities:
            issues.append(f"ERROR: worker {worker_name} requires a non-empty required_capabilities list")
        compatibility_defaults = runtime_worker_defaults.get(worker_name, {})
        if not isinstance(compatibility_defaults, dict):
            issues.append(f"ERROR: runtime compatibility defaults for worker {worker_name} must be a mapping")
        else:
            for source_key in ("preferred_implementations", "fallbacks"):
                values = compatibility_defaults.get(source_key, [])
                if not isinstance(values, list) or not values:
                    issues.append(
                        f"ERROR: runtime compatibility worker {worker_name} requires a non-empty {source_key} list"
                    )
                    continue
                unknown_models = sorted(str(model) for model in values if str(model) not in known_models)
                if unknown_models:
                    issues.append(
                        f"ERROR: runtime compatibility worker {worker_name} references unregistered models in {source_key}: "
                        + ", ".join(unknown_models)
                    )
        if not team:
            issues.append(f"ERROR: worker {worker_name} requires owning_team")

    for alias, model in models.items():
        if not isinstance(model, dict):
            issues.append(f"ERROR: model registry entry {alias} must be a mapping")
            continue
        concrete = model.get("concrete_model")
        if not concrete:
            continue
        evidence = model_evidence.get(str(concrete))
        if not isinstance(evidence, dict):
            issues.append(
                f"ERROR: concrete model {concrete} has no canonical registry evidence entry"
            )
            continue
        configured_provider = str(model.get("provider_family") or "")
        evidence_provider = str(evidence.get("provider") or "")
        if configured_provider != evidence_provider:
            issues.append(
                f"ERROR: model {concrete} provider mismatch: policy/routing/core/implementation-defaults.yaml={configured_provider}, registry={evidence_provider}"
            )

    for path, candidate in _iter_model_candidates(configuration.runtime_compatibility):
        model = str(candidate.get("model") or "")
        if model not in known_models:
            issues.append(f"ERROR: {path} references unregistered model {model}")
            continue
        reasoning = candidate.get("reasoning")
        if reasoning is None:
            continue
        entry = model_evidence.get(model)
        levels = entry.get("reasoning_levels") if isinstance(entry, dict) else None
        if isinstance(levels, list) and levels and str(reasoning) not in {str(level) for level in levels}:
            issues.append(
                f"ERROR: {path} requests unsupported reasoning effort {reasoning} for {model}"
            )

    for route_name, route in runtime_task_routes.items():
        if not isinstance(route, dict):
            issues.append(f"ERROR: runtime compatibility task route {route_name} must be a mapping")
            continue
        execution: dict[str, Any] | None = None
        for key in _EXECUTION_KEYS:
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                execution = candidate
                break
        if execution is None:
            continue
        execution_model = str(execution["model"])
        execution_provider = _provider_for_model(configuration.models, execution_model)
        explicit_verifiers = [
            candidate
            for key in _VERIFIER_KEYS
            if isinstance((candidate := route.get(key)), dict) and candidate.get("model")
        ]
        if not explicit_verifiers:
            continue
        provider_diverse = False
        for candidate in explicit_verifiers:
            verifier_model = str(candidate["model"])
            verifier_provider = _provider_for_model(configuration.models, verifier_model)
            if verifier_model != execution_model and verifier_provider and verifier_provider != execution_provider:
                provider_diverse = True
                break
        if not provider_diverse:
            issues.append(
                f"ERROR: runtime compatibility route {route_name} has no explicit model- and provider-diverse verifier candidate"
            )

    return issues
