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


@dataclass(slots=True)
class ConfigBundle:
    root: Path
    team_routing: dict[str, Any]
    routing: dict[str, Any]
    workers: dict[str, Any]
    specialists: dict[str, Any]
    models: dict[str, Any]

    @classmethod
    def load(cls, root: str | Path) -> "ConfigBundle":
        root_path = Path(root).resolve()
        bundle = cls(
            root=root_path,
            team_routing=_load_team_routing(
                root_path / "policy/routing/team-routing.yaml",
                (root_path / "policy/routing/principal-engineering-team-routing.yaml",),
            ),
            routing=_load_routing(
                root_path / "policy/routing/routing.yaml",
                (
                    root_path / "policy/routing/mission-control-routing.yaml",
                    root_path / "policy/routing/research-routing.yaml",
                    root_path / "policy/routing/review-routing.yaml",
                    root_path / "policy/routing/principal-engineering-routing.yaml",
                ),
            ),
            workers=_load_workers(
                root_path / "community/workers/workers.yaml",
                (
                    root_path / "community/workers/incident-response-worker.yaml",
                    root_path / "community/workers/research-worker.yaml",
                    root_path / "community/workers/market-research-worker.yaml",
                    root_path / "community/workers/analytics-worker.yaml",
                    root_path / "community/workers/user-research-worker.yaml",
                    root_path / "community/workers/compliance-worker.yaml",
                    root_path / "community/workers/systems-engineering-worker.yaml",
                    root_path / "community/workers/platform-reliability-core-workers.yaml",
                    root_path / "community/workers/platform-reliability-operations-workers.yaml",
                    root_path / "community/workers/physical-systems-workers.yaml",
                    root_path / "community/workers/assurance-workers.yaml",
                    root_path / "community/workers/principal-engineering-active-workers.yaml",
                ),
            ),
            specialists=_load_specialists(
                root_path / "community/specialists/specialists.yaml",
                (root_path / "community/specialists/principal-engineering-active.yaml",),
            ),
            models=_load_yaml(root_path / "models.yaml"),
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

        for name, value in {
            "team_routes": routes,
            "routing": routing,
            "workers": workers,
            "specialists": specialists,
            "models": models,
        }.items():
            if not isinstance(value, dict) or not value:
                issues.append(f"ERROR: missing or empty {name}")

        if issues:
            return issues

        assert isinstance(routes, dict)
        assert isinstance(routing, dict)
        assert isinstance(workers, dict)
        assert isinstance(specialists, dict)

        for route_name, route in routes.items():
            if route_name not in routing and route_name != "release":
                issues.append(f"WARNING: team route {route_name} has no implementation route")
            worker_name = route.get("primary_worker")
            team_name = route.get("primary_team")
            if worker_name not in workers:
                issues.append(f"WARNING: route {route_name} references unregistered worker {worker_name}")
            elif workers[worker_name].get("owning_team") != team_name:
                issues.append(
                    f"WARNING: route {route_name} selects {team_name}/{worker_name}, but the worker belongs to "
                    f"{workers[worker_name].get('owning_team')}"
                )

        missing_bindings = sorted(
            {
                str(entry.get("worker_binding"))
                for entry in specialists.values()
                if entry.get("worker_binding") not in workers
            }
        )
        if missing_bindings:
            issues.append(
                "WARNING: specialist bindings without core worker definitions: " + ", ".join(missing_bindings)
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
