from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ...schemas import RISK_ORDER, TaskRequest


class SpecialistRoutingPolicyError(RuntimeError):
    pass


class SpecialistRoutingPolicy:
    """Model-neutral specialist risk and runtime-preference refinement.

    The policy consumes already-loaded configuration data and performs no filesystem,
    YAML, provider, or engine I/O. Concrete runtime preferences remain compatibility
    inputs to the normal runtime-selection lifecycle and never create authority.
    """

    def __init__(
        self,
        *,
        selection_policy: dict[str, Any],
        specialist_registry: dict[str, Any],
        runtime_specialist_profiles: dict[str, Any],
        worker_runtime_defaults: dict[str, Any],
        model_registry: dict[str, Any],
    ):
        self._selection_policy = selection_policy
        self._specialist_registry = specialist_registry
        self._runtime_specialist_profiles = runtime_specialist_profiles
        self._worker_runtime_defaults = worker_runtime_defaults
        self._model_registry = model_registry
        self._validate()

    def _model_entry(self, model: str) -> dict[str, Any]:
        direct = self._model_registry.get(model)
        if isinstance(direct, dict):
            return direct
        for entry in self._model_registry.values():
            if not isinstance(entry, dict):
                continue
            if entry.get("concrete_model") == model or model in entry.get(
                "candidate_implementations", []
            ):
                return entry
        return {}

    def provider_for_model(self, model: str) -> str | None:
        provider = self._model_entry(model).get("provider_family")
        return str(provider) if provider else None

    def _validate(self) -> None:
        if self._selection_policy.get("status") != "active":
            raise SpecialistRoutingPolicyError("Specialist selection policy must be active")
        profiles = self._selection_policy.get("profiles")
        assignments = self._selection_policy.get("specialists")
        if not isinstance(profiles, dict) or not isinstance(assignments, dict):
            raise SpecialistRoutingPolicyError(
                "Specialist selection policy requires profiles and specialists"
            )

        registered = set(self._specialist_registry)
        assigned = set(assignments)
        if registered != assigned:
            missing = sorted(registered - assigned)
            extra = sorted(assigned - registered)
            details = []
            if missing:
                details.append("missing=" + ",".join(missing))
            if extra:
                details.append("extra=" + ",".join(extra))
            raise SpecialistRoutingPolicyError(
                "Specialist selection-profile coverage must exactly match the active registry: "
                + "; ".join(details)
            )

        if set(profiles) != set(self._runtime_specialist_profiles):
            raise SpecialistRoutingPolicyError(
                "Model-neutral specialist profiles and runtime compatibility profiles must match exactly"
            )

        for specialist, assignment in assignments.items():
            if not isinstance(assignment, dict) or not assignment.get("selection_profile"):
                raise SpecialistRoutingPolicyError(
                    f"Specialist {specialist} has no selection profile"
                )
            profile_name = str(assignment["selection_profile"])
            if profile_name not in profiles:
                raise SpecialistRoutingPolicyError(
                    f"Specialist {specialist} references unknown selection profile {profile_name}"
                )
            compatibility = self._runtime_specialist_profiles.get(profile_name)
            if not isinstance(compatibility, dict):
                raise SpecialistRoutingPolicyError(
                    f"Selection profile {profile_name} has no runtime compatibility defaults"
                )
            providers: list[str] = []
            models: list[str] = []
            for key in ("primary", "fallback", "verifier"):
                candidate = compatibility.get(key)
                if not isinstance(candidate, dict) or not candidate.get("model"):
                    raise SpecialistRoutingPolicyError(
                        f"Runtime compatibility profile {profile_name} is missing {key}"
                    )
                model = str(candidate["model"])
                provider = self.provider_for_model(model)
                if not provider:
                    raise SpecialistRoutingPolicyError(
                        f"Runtime compatibility profile {profile_name} references model without provider metadata: {model}"
                    )
                models.append(model)
                providers.append(provider)
            if len(set(models)) != 3:
                raise SpecialistRoutingPolicyError(
                    f"Runtime compatibility profile {profile_name} must use distinct primary, fallback and verifier models"
                )
            if len(set(providers)) != 3:
                raise SpecialistRoutingPolicyError(
                    f"Runtime compatibility profile {profile_name} must preserve three-provider primary/fallback/verifier diversity"
                )

    def selection_profile_for(self, specialist: str) -> tuple[str, dict[str, Any]]:
        assignment = self._selection_policy["specialists"][specialist]
        profile_name = str(assignment["selection_profile"])
        return profile_name, self._runtime_specialist_profiles[profile_name]

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

    @staticmethod
    def _dedupe_preferences(
        preferences: Sequence[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        seen: set[str] = set()
        result: list[dict[str, Any]] = []
        for item in preferences:
            model = str(item.get("model") or "")
            if not model or model in seen:
                continue
            seen.add(model)
            result.append(dict(item))
        return result

    def refine_effective_risk(
        self,
        task: TaskRequest,
        specialist: str | None,
        risk: str,
    ) -> tuple[str, str | None]:
        if not specialist:
            return risk, None
        entry = self._specialist_registry.get(specialist, {})
        escalation = entry.get("risk_escalation", {})
        if not isinstance(escalation, dict):
            return risk, None
        patterns = escalation.get("critical_patterns", [])
        if not isinstance(patterns, list):
            raise SpecialistRoutingPolicyError(
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
        worker_defaults = self._worker_runtime_defaults[worker]
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

    def refine_selection_preferences(
        self,
        *,
        base_preferences: Sequence[dict[str, Any]],
        task: TaskRequest,
        task_type: str,
        worker: str,
        role: str,
        risk: str,
        capabilities: list[str],
        specialist: str | None,
    ) -> list[dict[str, Any]]:
        del task, capabilities
        base = [dict(item) for item in base_preferences]
        if task_type == "documentation" and role == "verifier":
            base.extend(
                self._documentation_recovery_verifier_preferences(worker=worker)
            )
            base = self._dedupe_preferences(base)

        if not specialist:
            return base

        profile_name, template = self.selection_profile_for(specialist)
        source = (
            "policy/routing/core/runtime-compatibility-defaults.yaml."
            f"specialist_profiles.{profile_name}"
        )
        preferences: list[dict[str, Any]] = []

        if role == "primary":
            preferences.append(
                self._specialist_preference(
                    template["primary"], risk, source + ".primary"
                )
            )
            preferences.append(
                self._specialist_preference(
                    template["fallback"], risk, source + ".fallback"
                )
            )
        elif role == "fallback":
            preferences.append(
                self._specialist_preference(
                    template["fallback"], risk, source + ".fallback"
                )
            )
        elif role == "verifier":
            preferences.append(
                self._specialist_preference(
                    template["verifier"], risk, source + ".verifier"
                )
            )
        else:
            raise SpecialistRoutingPolicyError(
                f"Unsupported specialist runtime selection role: {role}"
            )

        preferences.extend(base)
        return self._dedupe_preferences(preferences)
