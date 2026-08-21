from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .engine import OrchestrationEngine as BaseOrchestrationEngine, RoutingError
from .schemas import RISK_ORDER, TaskRequest

SPECIALIST_MODEL_POLICY = "policy/routing/core/specialist-model-routing.yaml"


class SpecialistRoutingError(RoutingError):
    pass


class SpecialistRoutingEngine(BaseOrchestrationEngine):
    """TEO router with specialist policy expressed as pre-selection constraints.

    Specialist policy may elevate effective risk and supply ordered implementation/
    reasoning preferences. Actual primary, fallback, and verifier choices remain owned
    by the runtime selection lifecycle; this layer no longer overwrites a completed
    DispatchRecord with static model choices.
    """

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self._specialist_model_policy = self._load_specialist_model_policy()
        self._validate_specialist_model_policy()

    def _load_specialist_model_policy(self) -> dict[str, Any]:
        path = Path(self.config.root) / SPECIALIST_MODEL_POLICY
        if not path.is_file():
            raise SpecialistRoutingError(f"Specialist model-routing policy not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SpecialistRoutingError("Specialist model-routing policy root must be a mapping")
        if data.get("status") != "active":
            raise SpecialistRoutingError("Specialist model-routing policy must be active")
        if not isinstance(data.get("templates"), dict) or not isinstance(data.get("specialists"), dict):
            raise SpecialistRoutingError("Specialist model-routing policy requires templates and specialists")
        return data

    def _provider_for_model(self, model: str) -> str | None:
        entry = self._model_entry(model)
        provider = entry.get("provider_family")
        return str(provider) if provider else None

    def _validate_specialist_model_policy(self) -> None:
        templates = self._specialist_model_policy["templates"]
        assignments = self._specialist_model_policy["specialists"]
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
                "Specialist model-routing coverage must exactly match the active registry: "
                + "; ".join(details)
            )

        for specialist, assignment in assignments.items():
            if not isinstance(assignment, dict) or not assignment.get("template"):
                raise SpecialistRoutingError(f"Specialist {specialist} has no model-routing template")
            template_name = str(assignment["template"])
            template = templates.get(template_name)
            if not isinstance(template, dict):
                raise SpecialistRoutingError(
                    f"Specialist {specialist} references unknown model-routing template {template_name}"
                )
            providers: list[str] = []
            models: list[str] = []
            for key in ("primary", "fallback", "verifier"):
                candidate = template.get(key)
                if not isinstance(candidate, dict) or not candidate.get("model"):
                    raise SpecialistRoutingError(f"Template {template_name} is missing {key}")
                model = str(candidate["model"])
                provider = self._provider_for_model(model)
                if not provider:
                    raise SpecialistRoutingError(
                        f"Template {template_name} references model without provider metadata: {model}"
                    )
                models.append(model)
                providers.append(provider)
            if len(set(models)) != 3:
                raise SpecialistRoutingError(
                    f"Template {template_name} must use distinct primary, fallback and verifier models"
                )
            if len(set(providers)) != 3:
                raise SpecialistRoutingError(
                    f"Template {template_name} must preserve three-provider primary/fallback/verifier diversity"
                )

    def _template_for(self, specialist: str) -> tuple[str, dict[str, Any]]:
        assignment = self._specialist_model_policy["specialists"][specialist]
        template_name = str(assignment["template"])
        return template_name, self._specialist_model_policy["templates"][template_name]

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
        if not specialist:
            return base

        template_name, template = self._template_for(specialist)
        source = f"{SPECIALIST_MODEL_POLICY}.templates.{template_name}"
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
