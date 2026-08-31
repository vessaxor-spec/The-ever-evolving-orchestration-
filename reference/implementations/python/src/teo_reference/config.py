from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .adapters.repository_configuration import (
    RepositoryConfigurationSourceError,
    YamlRepositoryConfigurationAdapter,
)
from .application.configuration.composition import (
    ConfigurationCompositionError,
    compose_repository_configuration,
    load_routing as _compose_routing,
    load_specialists as _compose_specialists,
    load_team_routing as _compose_team_routing,
    load_workers as _compose_workers,
)
from .application.configuration.runtime_view import (
    RuntimeConfigurationView,
    build_runtime_configuration_view,
)
from .application.configuration.validation import (
    RepositoryConfigurationValidationInput,
    _EXECUTION_KEYS,
    _MODEL_IDENTITY_KEYS,
    _VERIFIER_KEYS,
    _iter_model_candidates,
    _iter_responsibility_model_identity,
    _known_models,
    _model_entry,
    _provider_for_model,
    validate_repository_configuration,
)
from .ports.configuration import RepositoryConfigurationSourcePort


class ConfigurationError(RuntimeError):
    pass


# Compatibility shims for repository-internal characterization tests and callers that
# reached into the former private composition helpers. Composition semantics now live
# in the application boundary; these wrappers only preserve the historical public
# ConfigurationError translation for composition failures.
def _load_team_routing(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    try:
        return _compose_team_routing(source, path, extension_paths)
    except ConfigurationCompositionError as exc:
        raise ConfigurationError(str(exc)) from exc


def _load_routing(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    try:
        return _compose_routing(source, path, extension_paths)
    except ConfigurationCompositionError as exc:
        raise ConfigurationError(str(exc)) from exc


def _load_workers(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    try:
        return _compose_workers(source, path, extension_paths)
    except ConfigurationCompositionError as exc:
        raise ConfigurationError(str(exc)) from exc


def _load_specialists(
    source: RepositoryConfigurationSourcePort,
    path: Path,
    extension_paths: tuple[Path, ...] = (),
) -> dict[str, Any]:
    try:
        return _compose_specialists(source, path, extension_paths)
    except ConfigurationCompositionError as exc:
        raise ConfigurationError(str(exc)) from exc


@dataclass(slots=True)
class ConfigBundle:
    root: Path
    team_routing: dict[str, Any]
    routing: dict[str, Any]
    runtime_compatibility: dict[str, Any]
    workers: dict[str, Any]
    specialists: dict[str, Any]
    models: dict[str, Any]
    capabilities: dict[str, Any]
    model_evidence: dict[str, Any]

    @classmethod
    def load(
        cls,
        root: str | Path,
        *,
        source: RepositoryConfigurationSourcePort | None = None,
    ) -> "ConfigBundle":
        root_path = Path(root).resolve()
        configuration_source = source or YamlRepositoryConfigurationAdapter()
        try:
            composed = compose_repository_configuration(root_path, configuration_source)
            bundle = cls(
                root=root_path,
                team_routing=composed.team_routing,
                routing=composed.routing,
                runtime_compatibility=composed.runtime_compatibility,
                workers=composed.workers,
                specialists=composed.specialists,
                models=composed.models,
                capabilities=composed.capabilities,
                model_evidence=composed.model_evidence,
            )
        except (RepositoryConfigurationSourceError, ConfigurationCompositionError) as exc:
            raise ConfigurationError(str(exc)) from exc
        errors = [issue for issue in bundle.validate() if issue.startswith("ERROR:")]
        if errors:
            raise ConfigurationError("\n".join(errors))
        return bundle

    def validate(self) -> list[str]:
        return validate_repository_configuration(
            RepositoryConfigurationValidationInput(
                team_routing=self.team_routing,
                routing=self.routing,
                runtime_compatibility=self.runtime_compatibility,
                workers=self.workers,
                specialists=self.specialists,
                models=self.models,
                capabilities=self.capabilities,
                model_evidence=self.model_evidence,
            )
        )

    def runtime_view(self) -> RuntimeConfigurationView:
        """Return a detached immutable snapshot for one runtime execution boundary."""

        return build_runtime_configuration_view(self)

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
    def runtime_compatibility_defaults(self) -> dict[str, Any]:
        return self.runtime_compatibility

    @property
    def worker_runtime_defaults(self) -> dict[str, Any]:
        return self.runtime_compatibility["worker_defaults"]

    @property
    def runtime_task_routes(self) -> dict[str, Any]:
        return self.runtime_compatibility["task_routes"]

    @property
    def runtime_task_routing_defaults(self) -> dict[str, Any]:
        return self.runtime_compatibility["task_routing_defaults"]

    @property
    def runtime_fallback_order(self) -> dict[str, Any]:
        return self.runtime_compatibility["fallback_order"]

    @property
    def runtime_specialist_profiles(self) -> dict[str, Any]:
        return self.runtime_compatibility["specialist_profiles"]

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
