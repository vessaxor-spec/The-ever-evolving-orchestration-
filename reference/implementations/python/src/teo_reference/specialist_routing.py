from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .engine import OrchestrationEngine as BaseOrchestrationEngine, RoutingError
from .schemas import RISK_ORDER, TaskRequest

SPECIALIST_SELECTION_POLICY = "policy/routing/core/specialist-selection-policy.yaml"


class SpecialistRoutingError(RoutingError):
    pass


class SpecialistRoutingEngine(BaseOrchestrationEngine):
    """TEO router with specialist policy expressed as pre-selection constraints.

    Specialist responsibility remains model- and provider-neutral. The specialist policy
    may elevate effective risk and assign a provider-neutral selection profile. Concrete
    compatibility defaults for that profile are resolved separately and still pass through
    the runtime selection lifecycle.
    """

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self._specialist_selection_policy = self._load_specialist_selection_policy()
        self._validate_specialist_selection_policy()

    def _load_specialist_selection_policy(self) -> dict[str, Any]:
        path = Path(self.config.root) / SPECIALIST_SELECTION_POLICY
        if not path.is_file():
            raise SpecialistRoutingError(f"Specialist selection policy not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SpecialistRoutingError("Specialist selection policy root must be a mapping")
        if data.get("status") != "active":
            raise SpecialistRoutingError("Specialist selection policy must be active")
        if not isinstance(data.get("profiles"), dict) or not isinstance(data.get("specialists"), dict):
            raise SpecialistRoutingError("Specialist selection policy requires profiles and specialists")
        return data

    def _provider_for_model(self, model: str) -> str | None:
        entry = self._model_entry(model)
        provider = entry.get("provider_family")
        return str(provider) if provider else None

    def _validate_specialist_selection_policy(self) -> None:
        profiles = self._specialist_selection_policy["profiles"]
        assignments = self._specialist_selection_policy["specialists"]
        compatibility_profiles = self.config.runtime_specialist_profiles
        registered = set(self.config.specialist_registry)
        assigned = set(assignments)
        if registered != assigned:
            missing = sorted(registered - assigned)
            extra = sorted(assigned - registered)
            details = []
            if missing:
                details.append("missing=" + ",".join(missing))
            if extra:
                details.append("extra=" + ",".join(extra))
            raise SpecialistRoutingError(
                "Specialist selection-profile coverage must exactly match the active registry: "
                + "; ".join(details)
            )

        if set(profiles) != set(compatibility_profiles):
            raise SpecialistRoutingError(
                "Model-neutral specialist profiles and runtime compatibility profiles must match exactly"
            )

        for specialist, assignment in assignments.items():
            if not isinstance(assignment, dict) or not assignment.get("selection_profile"):
                raise SpecialistRoutingError(f"Specialist {specialist} has no selection profile")
            profile_name = str(assignment["selection_profile"])
            if profile_name not in profiles:
                raise SpecialistRoutingError(
                    f"Specialist {specialist} references unknown selection profile {profile_name}"
                )
            compatibility = compatibility_profiles.get(profile_name)
            if not isinstance(compatibility, dict):
                raise SpecialistRoutingError(
                    f"Selection profile {profile_name} has no runtime compatibility defaults"
                )
            providers: list[str] = []
            models: list[str] = []
            for key in ("primary", "fallback", "verifier"):
                candidate = compatibility.get(key)
                if not isinstance(candidate, dict) or not candidate.get("model"):
                    raise SpecialistRoutingError(
                        f"Runtime compatibility profile {profile_name} is missing {key}"
                    )
                model = str(candidate["model"])
                provider = self._provider_for_model(model)
                if not provider:
                    raise SpecialistRoutingError(
                        f"Runtime compatibility profile {profile_name} references model without provider metadata: {model}"
                    )
                models.append(model)
                providers.append(provider)
            if len(set(models)) != 3:
                raise SpecialistRoutingError(
                    f"Runtime compatibility profile {profile_name} must use distinct primary, fallback and verifier models"
                )
            if len(set(providers)) != 3:
                raise SpecialistRoutingError(
                    f"Runtime compatibility profile {profile_name} must preserve three-provider primary/fallback/verifier diversity"
                )

    def _selection_profile_for(self, specialist: str) -> tuple[str, dict[str, Any]]:
        assignment = self._specialist_selection_policy["specialists"][specialist]
        profile_name = str(assignment["selection_profile"])
        return profile_name, self.config.runtime_specialist_profiles[profile_name]

    @staticmethod
    def _specialist_preference(
        candidate: dict[str, Any],
        risk: str,
        source: str,
    ) -> dict[str, Any]:
        reasoning = candidate.get("reasoning")
        by_risk = candidate.get("reasoning_by_risk")
        if isinstance(by_risk, dict) and by_risk.get(risk):
            reasoning = by_risk[risk]
        return {
            "agent": candidate.get("agent", "registry"),
            "model": candidate.get("model"),
            "profile": candidate.get("profile"),
            "reasoning": reasoning,
            "source": source,
        }

    def _refine_effective_risk(
        self,
        task: TaskRequest,
        specialist: str | None,
        risk: str,
    ) -> tuple[str, str | None]:
        if not specialist:
            return risk, None
        entry = self.config.specialist_registry.get(specialist, {})
        escalation = entry.get("risk_escalation", {})
        if not isinstance(escalation, dict):
            return risk, None
        patterns = escalation.get("critical_patterns", [])
        if not isinstance(patterns, list):
            raise SpecialistRoutingError(
                f"Specialist {specialist} risk_escalation.critical_patterns must be a list"
            )
        text = task.task.lower()
        matched = next(
            (
                str(pattern)
                for pattern in patterns
                if str(pattern).strip() and str(pattern).lower() in text
            ),
            None,
        )
        if not matched or RISK_ORDER[risk] >= RISK_ORDER["critical"]:
            return risk, None
        return (
            "critical",
            f"Specialist {specialist} consequence rule elevated effective risk to critical using trigger {matched!r}.",
        )

    def _documentation_recovery_verifier_preferences(
        self,
        *,
        worker: str,
    ) -> list[dict[str, Any]]:
        """Secondary verifier candidates preserving the staged documentation recovery contract.

        These entries widen neither task authority nor live scope. They only retain the
        pre-RMI documentation worker recovery pool inside the normal runtime-selection
        lifecycle. Explicit route verifiers remain preferred; these candidates matter
        only when exclusions or task constraints make those choices ineligible.
        """
        worker_defaults = self.config.worker_runtime_defaults[worker]
        return [
            {
                "agent": "registry",
                "model": model,
                "profile": None,
                "reasoning": "medium",
                "source": f"runtime_compatibility.worker_defaults.{worker}.preferred_implementations.documentation_recovery",
            }
            for model in worker_defaults.get("preferred_implementations", [])
        ]

    def _selection_preferences(
        self,
        *,
        task: TaskRequest,
        task_type: str,
        worker: str,
        role: str,
        risk: str,
        capabilities: list[str],
        specialist: str | None,
    ) -> list[dict[str, Any]]:
        base = super()._selection_preferences(
            task=task,
            task_type=task_type,
            worker=worker,
            role=role,
            risk=risk,
            capabilities=capabilities,
            specialist=specialist,
        )
        if task_type == "documentation" and role == "verifier":
            base.extend(
                self._documentation_recovery_verifier_preferences(worker=worker)
            )
            base = self._dedupe_preferences(base)

        if not specialist:
            return base

        profile_name, template = self._selection_profile_for(specialist)
        source = f"policy/routing/core/runtime-compatibility-defaults.yaml.specialist_profiles.{profile_name}"
        preferences: list[dict[str, Any]] = []

        if role == "primary":
            preferences.append(
                self._specialist_preference(template["primary"], risk, source + ".primary")
            )
            preferences.append(
                self._specialist_preference(template["fallback"], risk, source + ".fallback")
            )
        elif role == "fallback":
            preferences.append(
                self._specialist_preference(template["fallback"], risk, source + ".fallback")
            )
        elif role == "verifier":
            preferences.append(
                self._specialist_preference(template["verifier"], risk, source + ".verifier")
            )
        else:
            raise SpecialistRoutingError(f"Unsupported specialist runtime selection role: {role}")

        preferences.extend(base)
        return self._dedupe_preferences(preferences)