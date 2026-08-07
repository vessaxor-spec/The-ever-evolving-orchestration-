from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .engine import OrchestrationEngine as BaseOrchestrationEngine, RoutingError
from .schemas import DispatchRecord, ImplementationChoice, TaskRequest

SPECIALIST_MODEL_POLICY = "policy/routing/specialist-model-routing.yaml"


class SpecialistRoutingError(RoutingError):
    pass


class SpecialistRoutingEngine(BaseOrchestrationEngine):
    """TEO router with additive specialist-aware model and effort refinement.

    Team, worker, specialist and effective-risk resolution are delegated to the
    canonical router first. This layer may refine only implementation, routine
    fallback, verifier and reasoning effort after a specialist has been selected.
    """

    def __init__(self, config):
        super().__init__(config)
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
                "Specialist model-routing coverage must exactly match the active registry: " + "; ".join(details)
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

    def _specialist_choice(
        self,
        candidate: dict[str, Any],
        risk: str,
        source: str,
    ) -> ImplementationChoice:
        model = str(candidate["model"])
        registry_entry = self._model_entry(model)
        profile = candidate.get("profile") or registry_entry.get("profile")
        reasoning = candidate.get("reasoning")
        by_risk = candidate.get("reasoning_by_risk")
        if isinstance(by_risk, dict) and by_risk.get(risk):
            reasoning = by_risk[risk]
        return ImplementationChoice(
            agent=str(candidate.get("agent", "registry")),
            model=model,
            profile=str(profile) if profile else None,
            provider_family=str(registry_entry.get("provider_family")) if registry_entry.get("provider_family") else None,
            availability=str(registry_entry.get("availability")) if registry_entry.get("availability") else None,
            source=source,
            reasoning=str(reasoning) if reasoning else None,
        )

    def dispatch(self, task: TaskRequest) -> DispatchRecord:
        dispatch = super().dispatch(task)
        specialist = dispatch.selected_specialist
        if not specialist:
            return dispatch

        template_name, template = self._template_for(specialist)
        source = f"{SPECIALIST_MODEL_POLICY}.templates.{template_name}"
        primary = self._specialist_choice(template["primary"], dispatch.risk_level, source + ".primary")
        fallback = self._specialist_choice(template["fallback"], dispatch.risk_level, source + ".fallback")
        verifier = self._specialist_choice(template["verifier"], dispatch.risk_level, source + ".verifier")

        if not self._eligible(primary, task):
            if self._eligible(fallback, task):
                primary = fallback
                base_fallback = dispatch.fallback_implementation
                fallback = (
                    base_fallback
                    if base_fallback
                    and base_fallback.model != primary.model
                    and self._eligible(base_fallback, task)
                    else None
                )
            else:
                dispatch.routing_explanation.append(
                    f"Specialist model policy {template_name} was blocked by task constraints; canonical eligible routing was preserved."
                )
                return dispatch
        elif not self._eligible(fallback, task):
            fallback = dispatch.fallback_implementation
            if fallback and (fallback.model == primary.model or not self._eligible(fallback, task)):
                fallback = None

        if verifier.model == primary.model or not self._eligible(verifier, task):
            base_verifier = dispatch.verification.implementation
            if base_verifier.model == primary.model or not self._eligible(base_verifier, task):
                raise SpecialistRoutingError(
                    f"No independent eligible verifier remains for specialist {specialist}"
                )
            verifier = base_verifier

        if fallback and fallback.provider_family == primary.provider_family:
            raise SpecialistRoutingError(
                f"Specialist route {specialist} lost cross-provider routine fallback diversity"
            )
        if verifier.provider_family == primary.provider_family:
            raise SpecialistRoutingError(
                f"Specialist route {specialist} lost provider-independent verification"
            )

        dispatch.selected_implementation = primary
        dispatch.fallback_implementation = fallback
        dispatch.verification.implementation = verifier
        effort = primary.reasoning or "provider-default"
        dispatch.routing_explanation.append(
            f"Specialist model policy {template_name} refined execution to {primary.model} at {effort} reasoning effort."
        )
        if fallback:
            dispatch.routing_explanation.append(
                f"Routine fallback remains cross-provider on {fallback.model}."
            )
        dispatch.routing_explanation.append(
            f"Independent specialist-model verification assigned to {verifier.model}."
        )
        return dispatch
