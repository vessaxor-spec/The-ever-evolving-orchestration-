from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(RuntimeError):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigurationError(f"Required configuration file not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigurationError(f"Configuration root must be a mapping: {path}")
    return data


def _mapping(data: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigurationError(f"Configuration must contain a {key} mapping: {path}")
    return value


def _separate_conditional_escalations(routes: dict[str, Any]) -> None:
    for route in routes.values():
        if not isinstance(route, dict):
            continue
        escalation = route.pop("escalation", None)
        if escalation is not None:
            route["conditional_escalation"] = escalation


def _load_team_routing(path: Path, extension_paths: tuple[Path, ...] = ()) -> dict[str, Any]:
    data = _load_yaml(path)
    routes = _mapping(data, "team_routes", path)

    for extension_path in extension_paths:
        if not extension_path.is_file():
            continue
        extension = _load_yaml(extension_path)
        extension_routes = _mapping(extension, "team_routes", extension_path)
        duplicates = sorted(set(routes).intersection(extension_routes))
        if duplicates:
            raise ConfigurationError(
                f"Team-routing extension duplicates canonical routes in {extension_path}: "
                + ", ".join(duplicates)
            )
        routes.update(extension_routes)

        route_overrides = extension.get("route_overrides", {})
        if not isinstance(route_overrides, dict):
            raise ConfigurationError(
                f"Team-routing extension route_overrides must be a mapping: {extension_path}"
            )
        for route_name, override in route_overrides.items():
            if route_name not in routes:
                raise ConfigurationError(
                    f"Team-routing override references unknown route {route_name}: {extension_path}"
                )
            if not isinstance(override, dict):
                raise ConfigurationError(
                    f"Team-routing override must be a mapping for {route_name}: {extension_path}"
                )
            routes[route_name] = override
    return data


def _load_routing(path: Path, extension_paths: tuple[Path, ...] = ()) -> dict[str, Any]:
    data = _load_yaml(path)
    routes = _mapping(data, "routing", path)

    for extension_path in extension_paths:
        if not extension_path.is_file():
            continue
        extension = _load_yaml(extension_path)
        extension_routes = _mapping(extension, "routing", extension_path)
        duplicates = sorted(set(routes).intersection(extension_routes))
        if duplicates:
            raise ConfigurationError(
                f"Routing extension duplicates canonical routes in {extension_path}: "
                + ", ".join(duplicates)
            )
        routes.update(extension_routes)

    _separate_conditional_escalations(routes)

    policy = data.get("verification_policy")
    if isinstance(policy, dict):
        for risk in ("low", "medium", "high"):
            canonical_key = f"{risk}_risk"
            if risk not in policy and canonical_key in policy:
                policy[risk] = policy[canonical_key]
    return data


def _load_workers(path: Path, extension_paths: tuple[Path, ...] = ()) -> dict[str, Any]:
    data = _load_yaml(path)
    workers = _mapping(data, "workers", path)

    for extension_path in extension_paths:
        if not extension_path.is_file():
            continue
        extension = _load_yaml(extension_path)
        extension_workers = _mapping(extension, "workers", extension_path)
        duplicates = sorted(set(workers).intersection(extension_workers))
        if duplicates:
            raise ConfigurationError(
                f"Worker extension duplicates canonical workers in {extension_path}: "
                + ", ".join(duplicates)
            )
        workers.update(extension_workers)

        overrides = extension.get("worker_overrides", {})
        if not isinstance(overrides, dict):
            raise ConfigurationError(
                f"Worker extension worker_overrides must be a mapping: {extension_path}"
            )
        for worker_name, override in overrides.items():
            if worker_name not in workers:
                raise ConfigurationError(
                    f"Worker override references unknown worker {worker_name}: {extension_path}"
                )
            if not isinstance(override, dict):
                raise ConfigurationError(
                    f"Worker override must be a mapping for {worker_name}: {extension_path}"
                )
            workers[worker_name].update(override)
    return data


def _load_specialists(path: Path, extension_paths: tuple[Path, ...] = ()) -> dict[str, Any]:
    data = _load_yaml(path)
    specialists = _mapping(data, "specialists", path)
    allowed_override_fields = {
        "primary_team",
        "supporting_teams",
        "worker_binding",
        "risk_profile",
    }

    for extension_path in extension_paths:
        if not extension_path.is_file():
            continue
        extension = _load_yaml(extension_path)
        extension_specialists = _mapping(extension, "specialists", extension_path)
        duplicates = sorted(set(specialists).intersection(extension_specialists))
        if duplicates:
            raise ConfigurationError(
                f"Specialist extension duplicates canonical specialists in {extension_path}: "
                + ", ".join(duplicates)
            )
        specialists.update(extension_specialists)

        overrides = extension.get("allocation_overrides", {})
        if not isinstance(overrides, dict):
            raise ConfigurationError(
                f"Specialist extension allocation_overrides must be a mapping: {extension_path}"
            )
        for specialist_name, override in overrides.items():
            if specialist_name not in specialists:
                raise ConfigurationError(
                    f"Specialist override references unknown specialist {specialist_name}: {extension_path}"
                )
            if not isinstance(override, dict):
                raise ConfigurationError(
                    f"Specialist override must be a mapping for {specialist_name}: {extension_path}"
                )
            disallowed = sorted(set(override).difference(allowed_override_fields))
            if disallowed:
                raise ConfigurationError(
                    f"Specialist override changes protected fields for {specialist_name}: "
                    + ", ".join(disallowed)
                )
            specialists[specialist_name].update(override)
    return data


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


def _iter_model_candidates(value: Any, path: str = "routing"):
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


@dataclass(slots=True)
class ConfigBundle:
    root: Path
    team_routing: dict[str, Any]
    routing: dict[str, Any]
    workers: dict[str, Any]
    specialists: dict[str, Any]
    models: dict[str, Any]
    capabilities: dict[str, Any]
    model_evidence: dict[str, Any]

    @classmethod
    def load(cls, root: str | Path) -> "ConfigBundle":
        root_path = Path(root).resolve()
        bundle = cls(
            root=root_path,
            team_routing=_load_team_routing(
                root_path / "policy/routing/core/team-routing.yaml",
                (
                    root_path / "policy/routing/extensions/principal-engineering-team-routing.yaml",
                    root_path / "policy/routing/extensions/specialist-spawn-team-routing.yaml",
                ),
            ),
            routing=_load_routing(
                root_path / "policy/routing/core/routing.yaml",
                (
                    root_path / "policy/routing/extensions/mission-control-routing.yaml",
                    root_path / "policy/routing/extensions/research-routing.yaml",
                    root_path / "policy/routing/extensions/review-routing.yaml",
                    root_path / "policy/routing/extensions/principal-engineering-routing.yaml",
                    root_path / "policy/routing/extensions/specialist-spawn-routing.yaml",
                ),
            ),
            workers=_load_workers(
                root_path / "community/workers/workers.yaml",
                (
                    root_path / "community/workers/extensions/incident-response-worker.yaml",
                    root_path / "community/workers/extensions/research-worker.yaml",
                    root_path / "community/workers/extensions/market-research-worker.yaml",
                    root_path / "community/workers/extensions/analytics-worker.yaml",
                    root_path / "community/workers/extensions/user-research-worker.yaml",
                    root_path / "community/workers/extensions/compliance-worker.yaml",
                    root_path / "community/workers/extensions/systems-engineering-worker.yaml",
                    root_path / "community/workers/extensions/platform-reliability-core-workers.yaml",
                    root_path / "community/workers/extensions/platform-reliability-operations-workers.yaml",
                    root_path / "community/workers/extensions/physical-systems-workers.yaml",
                    root_path / "community/workers/extensions/assurance-workers.yaml",
                    root_path / "community/workers/extensions/principal-engineering-active-workers.yaml",
                    root_path / "community/workers/extensions/specialist-completion-workers.yaml",
                    root_path / "community/workers/extensions/runtime-worker-overrides.yaml",
                ),
            ),
            specialists=_load_specialists(
                root_path / "community/specialists/specialists.yaml",
                (root_path / "community/specialists/principal-engineering-active.yaml",),
            ),
            models=_load_yaml(root_path / "policy/routing/core/implementation-defaults.yaml"),
            capabilities=_load_yaml(root_path / "registry/capabilities/capabilities.yaml"),
            model_evidence=_load_yaml(root_path / "registry/models/models.yaml"),
        )
        errors = [issue for issue in bundle.validate() if issue.startswith("ERROR:")]
        if errors:
            raise ConfigurationError("\n".join(errors))
        return bundle

    def validate(self) -> list[str]:
        issues: list[str] = []
        routes = self.team_routing.get("team_routes")
        routing = self.routing.get("routing")
        workers = self.workers.get("workers")
        specialists = self.specialists.get("specialists")
        models = self.models.get("models")
        capabilities = self.capabilities.get("capabilities")
        model_evidence = self.model_evidence.get("models")

        for name, value in {
            "team_routes": routes,
            "routing": routing,
            "workers": workers,
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
        assert isinstance(specialists, dict)
        assert isinstance(models, dict)
        assert isinstance(model_evidence, dict)

        known_models = _known_models(self.models)
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
            for source_key in ("preferred_implementations", "fallbacks"):
                values = worker.get(source_key, [])
                if not isinstance(values, list) or not values:
                    issues.append(f"ERROR: worker {worker_name} requires a non-empty {source_key} list")
                    continue
                unknown_models = sorted(str(model) for model in values if str(model) not in known_models)
                if unknown_models:
                    issues.append(
                        f"ERROR: worker {worker_name} references unregistered models in {source_key}: "
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

        for path, candidate in _iter_model_candidates(self.routing):
            model = str(candidate.get("model") or "")
            if model not in known_models:
                issues.append(f"ERROR: {path} references unregistered model {model}")
                continue
            reasoning = candidate.get("reasoning")
            if reasoning is None:
                continue
            entry = self.model_evidence_registry.get(model)
            levels = entry.get("reasoning_levels") if isinstance(entry, dict) else None
            if isinstance(levels, list) and levels and str(reasoning) not in {str(level) for level in levels}:
                issues.append(
                    f"ERROR: {path} requests unsupported reasoning effort {reasoning} for {model}"
                )

        for route_name, route in routing.items():
            if not isinstance(route, dict):
                issues.append(f"ERROR: implementation route {route_name} must be a mapping")
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
            execution_provider = _provider_for_model(self.models, execution_model)
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
                verifier_provider = _provider_for_model(self.models, verifier_model)
                if verifier_model != execution_model and verifier_provider and verifier_provider != execution_provider:
                    provider_diverse = True
                    break
            if not provider_diverse:
                issues.append(
                    f"ERROR: route {route_name} has no explicit model- and provider-diverse verifier candidate"
                )

        return issues

    @property
    def team_routes(self) -> dict[str, Any]:
        return self.team_routing["team_routes"]

    @property
    def implementation_routes(self) -> dict[str, Any]:
        return self.routing["routing"]

    @property
    def worker_registry(self) -> dict[str, Any]:
        return self.workers["workers"]

    @property
    def specialist_registry(self) -> dict[str, Any]:
        return self.specialists["specialists"]

    @property
    def model_registry(self) -> dict[str, Any]:
        return self.models["models"]

    @property
    def model_evidence_registry(self) -> dict[str, Any]:
        return self.model_evidence["models"]

    @property
    def capability_registry(self) -> dict[str, Any]:
        base = self.capabilities.get("capabilities", {})
        registry: dict[str, Any] = {
            str(name): dict(entry) if isinstance(entry, dict) else {"definition": str(entry)}
            for name, entry in base.items()
        }
        for worker_name, worker in self.worker_registry.items():
            if not isinstance(worker, dict):
                continue
            team = str(worker.get("owning_team") or "")
            evidence = [str(item) for item in worker.get("verification", [])]
            for capability in worker.get("required_capabilities", []):
                name = str(capability)
                if name in registry:
                    continue
                registry[name] = {
                    "definition": f"Worker-declared provider-neutral capability required by {worker_name}",
                    "typical_teams": [team] if team else [],
                    "evidence": evidence,
                    "derived_from_workers": [worker_name],
                }
        return registry
