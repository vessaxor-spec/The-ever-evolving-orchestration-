from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ...ports.configuration import RepositoryConfigurationSourcePort


class ConfigurationCompositionError(RuntimeError):
    """Raised when explicit repository configuration cannot be composed safely."""


@dataclass(frozen=True, slots=True)
class RepositoryConfigurationManifest:
    """Explicit ordered repository configuration manifest.

    Paths are deliberately enumerated. This boundary performs no directory discovery,
    and configuration presence does not grant routing or policy authority.
    """

    team_routing: Path
    team_routing_extensions: tuple[Path, ...]
    routing: Path
    routing_extensions: tuple[Path, ...]
    runtime_compatibility: Path
    workers: Path
    worker_extensions: tuple[Path, ...]
    specialists: Path
    specialist_extensions: tuple[Path, ...]
    models: Path
    capabilities: Path
    model_evidence: Path


DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST = RepositoryConfigurationManifest(
    team_routing=Path("policy/routing/core/team-routing.yaml"),
    team_routing_extensions=(
        Path("policy/routing/extensions/principal-engineering-team-routing.yaml"),
        Path("policy/routing/extensions/specialist-spawn-team-routing.yaml"),
    ),
    routing=Path("policy/routing/core/routing.yaml"),
    routing_extensions=(
        Path("policy/routing/extensions/mission-control-routing.yaml"),
        Path("policy/routing/extensions/research-routing.yaml"),
        Path("policy/routing/extensions/review-routing.yaml"),
        Path("policy/routing/extensions/principal-engineering-routing.yaml"),
        Path("policy/routing/extensions/specialist-spawn-routing.yaml"),
    ),
    runtime_compatibility=Path("policy/routing/core/runtime-compatibility-defaults.yaml"),
    workers=Path("community/workers/workers.yaml"),
    worker_extensions=(
        Path("community/workers/extensions/incident-response-worker.yaml"),
        Path("community/workers/extensions/research-worker.yaml"),
        Path("community/workers/extensions/market-research-worker.yaml"),
        Path("community/workers/extensions/analytics-worker.yaml"),
        Path("community/workers/extensions/user-research-worker.yaml"),
        Path("community/workers/extensions/compliance-worker.yaml"),
        Path("community/workers/extensions/systems-engineering-worker.yaml"),
        Path("community/workers/extensions/platform-reliability-core-workers.yaml"),
        Path("community/workers/extensions/platform-reliability-operations-workers.yaml"),
        Path("community/workers/extensions/physical-systems-workers.yaml"),
        Path("community/workers/extensions/assurance-workers.yaml"),
        Path("community/workers/extensions/principal-engineering-active-workers.yaml"),
        Path("community/workers/extensions/specialist-completion-workers.yaml"),
        Path("community/workers/extensions/runtime-worker-overrides.yaml"),
    ),
    specialists=Path("community/specialists/specialists.yaml"),
    specialist_extensions=(
        Path("community/specialists/principal-engineering-active.yaml"),
        Path("community/specialists/workforce-expansion-active.yaml"),
    ),
    models=Path("policy/routing/core/implementation-defaults.yaml"),
    capabilities=Path("registry/capabilities/capabilities.yaml"),
    model_evidence=Path("registry/models/models.yaml"),
)


@dataclass(slots=True)
class ComposedRepositoryConfiguration:
    team_routing: dict[str, Any]
    routing: dict[str, Any]
    runtime_compatibility: dict[str, Any]
    workers: dict[str, Any]
    specialists: dict[str, Any]
    models: dict[str, Any]
    capabilities: dict[str, Any]
    model_evidence: dict[str, Any]


def _mapping(data: dict[str, Any], key: str, path: Path) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigurationCompositionError(
            f"Configuration must contain a {key} mapping: {path}"
        )
    return value


def _absolute(root: Path, paths: tuple[Path, ...]) -> tuple[Path, ...]:
    return tuple(root / path for path in paths)


def _separate_conditional_escalations(routes: dict[str, Any]) -> None:
    for route in routes.values():
        if not isinstance(route, dict):
            continue
        escalation = route.pop("escalation", None)
        if escalation is not None:
            route["conditional_escalation"] = escalation


def load_team_routing(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    data = source.load(path)
    routes = _mapping(data, "team_routes", path)

    for extension_path in extension_paths:
        extension = source.load_optional(extension_path)
        if extension is None:
            continue
        extension_routes = _mapping(extension, "team_routes", extension_path)
        duplicates = sorted(set(routes).intersection(extension_routes))
        if duplicates:
            raise ConfigurationCompositionError(
                f"Team-routing extension duplicates canonical routes in {extension_path}: "
                + ", ".join(duplicates)
            )
        routes.update(extension_routes)

        route_overrides = extension.get("route_overrides", {})
        if not isinstance(route_overrides, dict):
            raise ConfigurationCompositionError(
                f"Team-routing extension route_overrides must be a mapping: {extension_path}"
            )
        for route_name, override in route_overrides.items():
            if route_name not in routes:
                raise ConfigurationCompositionError(
                    f"Team-routing override references unknown route {route_name}: {extension_path}"
                )
            if not isinstance(override, dict):
                raise ConfigurationCompositionError(
                    f"Team-routing override must be a mapping for {route_name}: {extension_path}"
                )
            routes[route_name] = override
    return data


def load_routing(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    data = source.load(path)
    routes = _mapping(data, "routing", path)

    for extension_path in extension_paths:
        extension = source.load_optional(extension_path)
        if extension is None:
            continue
        extension_routes = _mapping(extension, "routing", extension_path)
        duplicates = sorted(set(routes).intersection(extension_routes))
        if duplicates:
            raise ConfigurationCompositionError(
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


def load_workers(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    data = source.load(path)
    workers = _mapping(data, "workers", path)

    for extension_path in extension_paths:
        extension = source.load_optional(extension_path)
        if extension is None:
            continue
        extension_workers = _mapping(extension, "workers", extension_path)
        duplicates = sorted(set(workers).intersection(extension_workers))
        if duplicates:
            raise ConfigurationCompositionError(
                f"Worker extension duplicates canonical workers in {extension_path}: "
                + ", ".join(duplicates)
            )
        workers.update(extension_workers)

        overrides = extension.get("worker_overrides", {})
        if not isinstance(overrides, dict):
            raise ConfigurationCompositionError(
                f"Worker extension worker_overrides must be a mapping: {extension_path}"
            )
        for worker_name, override in overrides.items():
            if worker_name not in workers:
                raise ConfigurationCompositionError(
                    f"Worker override references unknown worker {worker_name}: {extension_path}"
                )
            if not isinstance(override, dict):
                raise ConfigurationCompositionError(
                    f"Worker override must be a mapping for {worker_name}: {extension_path}"
                )
            workers[worker_name].update(override)
    return data


def load_specialists(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    data = source.load(path)
    specialists = _mapping(data, "specialists", path)
    allowed_override_fields = {
        "primary_team",
        "supporting_teams",
        "worker_binding",
        "risk_profile",
    }

    for extension_path in extension_paths:
        extension = source.load_optional(extension_path)
        if extension is None:
            continue
        extension_specialists = _mapping(extension, "specialists", extension_path)
        duplicates = sorted(set(specialists).intersection(extension_specialists))
        if duplicates:
            raise ConfigurationCompositionError(
                f"Specialist extension duplicates canonical specialists in {extension_path}: "
                + ", ".join(duplicates)
            )
        specialists.update(extension_specialists)

        overrides = extension.get("allocation_overrides", {})
        if not isinstance(overrides, dict):
            raise ConfigurationCompositionError(
                f"Specialist extension allocation_overrides must be a mapping: {extension_path}"
            )
        for specialist_name, override in overrides.items():
            if specialist_name not in specialists:
                raise ConfigurationCompositionError(
                    f"Specialist override references unknown specialist {specialist_name}: {extension_path}"
                )
            if not isinstance(override, dict):
                raise ConfigurationCompositionError(
                    f"Specialist override must be a mapping for {specialist_name}: {extension_path}"
                )
            disallowed = sorted(set(override).difference(allowed_override_fields))
            if disallowed:
                raise ConfigurationCompositionError(
                    f"Specialist override changes protected fields for {specialist_name}: "
                    + ", ".join(disallowed)
                )
            specialists[specialist_name].update(override)
    return data


def compose_repository_configuration(
    root: Path,
    source: RepositoryConfigurationSourcePort,
    *,
    manifest: RepositoryConfigurationManifest = DEFAULT_REPOSITORY_CONFIGURATION_MANIFEST,
) -> ComposedRepositoryConfiguration:
    """Compose the explicit repository configuration in canonical order."""

    return ComposedRepositoryConfiguration(
        team_routing=load_team_routing(
            source,
            root / manifest.team_routing,
            _absolute(root, manifest.team_routing_extensions),
        ),
        routing=load_routing(
            source,
            root / manifest.routing,
            _absolute(root, manifest.routing_extensions),
        ),
        runtime_compatibility=source.load(root / manifest.runtime_compatibility),
        workers=load_workers(
            source,
            root / manifest.workers,
            _absolute(root, manifest.worker_extensions),
        ),
        specialists=load_specialists(
            source,
            root / manifest.specialists,
            _absolute(root, manifest.specialist_extensions),
        ),
        models=source.load(root / manifest.models),
        capabilities=source.load(root / manifest.capabilities),
        model_evidence=source.load(root / manifest.model_evidence),
    )
