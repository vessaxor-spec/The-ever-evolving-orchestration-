from __future__ import annotations

import re
from typing import Any, Iterable
from uuid import uuid4

from .config import ConfigBundle
from .schemas import (
    DispatchRecord,
    ExecutionResult,
    FinalOutcome,
    ImplementationChoice,
    RISK_ORDER,
    TaskRequest,
    VerificationPlan,
    VerificationResult,
    utc_now,
)

TASK_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    (
        "orchestration",
        (
            "agent orchestration",
            "multi-agent pipeline",
            "multi agent pipeline",
            "handoff contract",
            "agent activation protocol",
            "mcp server",
        ),
    ),
    (
        "operations",
        (
            "operations plan",
            "operational plan",
            "onboarding workflow",
            "accounts payable",
            "vendor performance",
            "operational kpi",
            "process optimization",
            "recruitment operations",
        ),
    ),
    (
        "project_delivery",
        (
            "project plan",
            "delivery plan",
            "critical path",
            "risk register",
            "raci matrix",
            "scope negotiation",
            "project status report",
        ),
    ),
    (
        "incident_response",
        (
            "incident response",
            "incident commander",
            "production outage",
            "sev1",
            "sev2",
            "war room",
            "post-mortem",
            "postmortem",
            "on-call rotation",
        ),
    ),
    (
        "market_research",
        (
            "market research",
            "competitive landscape",
            "competitive positioning",
            "market sizing",
            "tam sam som",
            "weak signals",
            "category lifecycle",
            "go-to-market timing",
            "market opportunity",
            "ai search visibility",
            "agentic search visibility",
        ),
    ),
    (
        "analytics",
        (
            "data analysis",
            "analyze the dataset",
            "analyse the dataset",
            "statistical analysis",
            "statistical significance",
            "confidence interval",
            "regression analysis",
            "a/b test",
            "ab test",
            "cohort retention",
            "funnel analysis",
            "churn analysis",
            "pipeline velocity",
            "forecast accuracy",
            "model qa",
            "data leakage",
            "demographic bias",
        ),
    ),
    ("security_review", ("security review", "threat model", "vulnerability", "authentication", "authorization")),
    ("code_review", ("code review", "review this diff", "review the pull request", "review pr")),
    ("deep_debugging", ("debug", "root cause", "failing test", "failure", "incident")),
    ("repo_wide_refactor", ("repo-wide", "repository-wide", "refactor", "migration")),
    ("daily_coding", ("implement", "build", "code", "fix", "add feature", "create cli")),
    ("architecture_design", ("architecture", "system design", "design a system", "tradeoff")),
    ("deep_research", ("research", "compare sources", "literature", "investigate")),
    ("multimodal_analysis", ("image", "diagram", "video", "audio", "multimodal")),
    ("documentation", ("documentation", "readme", "write docs", "document")),
    ("release", ("release", "publish version", "ship version")),
    ("high_volume_simple", ("classify", "extract", "transform", "bulk", "high volume")),
]

RISK_PATTERNS: dict[str, tuple[str, ...]] = {
    "critical": ("production credentials", "critical infrastructure", "medical diagnosis", "execute trade", "weapons"),
    "high": (
        "production",
        "security",
        "authentication",
        "authorization",
        "permission",
        "financial",
        "payment",
        "personal data",
        "migration",
        "delete",
        "irreversible",
    ),
    "medium": ("public api", "database", "deployment", "dependency", "customer", "external"),
}

ROUTE_IMPLEMENTATION_KEYS: dict[str, tuple[str, ...]] = {
    "orchestration": ("primary",),
    "operations": ("primary",),
    "project_delivery": ("primary",),
    "incident_response": ("primary",),
    "market_research": ("primary",),
    "analytics": ("primary",),
    "architecture_design": ("primary",),
    "daily_coding": ("primary",),
    "deep_debugging": ("primary",),
    "repo_wide_refactor": ("executor",),
    "deep_research": ("primary",),
    "code_review": ("executable_review",),
    "security_review": ("primary",),
    "multimodal_analysis": ("primary",),
    "high_volume_simple": ("primary",),
    "documentation": ("primary",),
}

VERIFIER_KEYS: tuple[str, ...] = (
    "verifier",
    "executable_verifier",
    "semantic_reviewer",
    "technical_verifier",
    "hypothesis_reviewer",
    "engineering_reasoning_review",
    "semantic_review",
    "synthesis",
    "escalation",
)

CAPABILITY_FAMILY: tuple[tuple[set[str], str], ...] = (
    ({"coding", "debugging", "tool_execution", "executable_verification"}, "coding"),
    ({"architecture", "planning", "high_reasoning", "orchestration_reasoning"}, "engineering_reasoning"),
    (
        {
            "statistical_analysis",
            "sql_analysis",
            "experiment_design",
            "data_quality_assessment",
            "causal_reasoning",
            "model_validation",
            "reproducible_analysis",
        },
        "analytics",
    ),
    (
        {
            "market_intelligence",
            "competitive_analysis",
            "trend_analysis",
            "current_information_retrieval",
            "source_validation",
        },
        "research",
    ),
    ({"synthesis", "technical_accuracy", "clear_writing"}, "general_reasoning"),
    ({"visual_reasoning", "visual_analysis"}, "multimodal"),
)


class RoutingError(RuntimeError):
    pass


def _unique(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


class OrchestrationEngine:
    def __init__(self, config: ConfigBundle):
        self.config = config

    @classmethod
    def from_repo(cls, repo_root: str) -> "OrchestrationEngine":
        return cls(ConfigBundle.load(repo_root))

    def dispatch(self, task: TaskRequest) -> DispatchRecord:
        task_type, classification_reason = self._classify_task(task)
        risk, risk_reason = self._assess_risk(task)
        route = self.config.team_routes.get(task_type)
        if not route:
            raise RoutingError(f"No team route for task type: {task_type}")

        team = str(route["primary_team"])
        worker = self._resolve_worker(route, task)
        specialist, specialist_warning = self._resolve_specialist(task, team, worker)
        if specialist:
            specialist_risk = str(specialist[1].get("risk_profile", risk))
            if specialist_risk in RISK_ORDER and RISK_ORDER[specialist_risk] > RISK_ORDER[risk]:
                risk = specialist_risk
                risk_reason += (
                    f" Specialist {specialist[0]} elevated the effective risk to {specialist_risk}."
                )
        capabilities = self._resolve_capabilities(task, worker)
        primary = self._resolve_primary(task_type, worker, task)
        fallback = self._resolve_fallback(task_type, worker, capabilities, task, exclude={primary.model})
        verification = self._verification_plan(
            task_type, risk, task, primary, worker, specialist[1] if specialist else None
        )

        warnings = []
        if specialist_warning:
            warnings.append(specialist_warning)
        worker_entry = self.config.worker_registry.get(worker)
        if worker_entry and worker_entry.get("owning_team") != team:
            warnings.append(
                f"Selected worker {worker} is registered to {worker_entry.get('owning_team')}, not {team}; "
                "the canonical route was preserved and the mismatch was exposed."
            )

        explanation = [classification_reason, risk_reason]
        explanation.append(f"Team route {task_type} selected {team}/{worker}.")
        if specialist:
            explanation.append(
                f"Specialist {specialist[0]} matched team {team} and worker binding {worker}."
            )
        explanation.append(
            f"Implementation {primary.model} selected from the {task_type} implementation route."
        )
        explanation.append(
            f"Independent verification assigned to {verification.implementation.model} with "
            f"{', '.join(verification.method)}."
        )

        specialist_name = specialist[0] if specialist else None
        specialist_entry = specialist[1] if specialist else None
        return DispatchRecord(
            task_id=task.task_id,
            dispatch_id=f"dispatch-{uuid4().hex[:12]}",
            created_at=utc_now(),
            task=task.task,
            task_type=task_type,
            risk_level=risk,
            selected_team=team,
            selected_worker=worker,
            selected_specialist=specialist_name,
            specialist_source=str(specialist_entry.get("role_card")) if specialist_entry else None,
            specialist_risk_profile=str(specialist_entry.get("risk_profile")) if specialist_entry else None,
            required_capabilities=capabilities,
            selected_implementation=primary,
            fallback_implementation=fallback,
            verification=verification,
            routing_explanation=explanation,
            warnings=warnings,
        )

    def finalize(
        self,
        dispatch: DispatchRecord,
        execution: ExecutionResult,
        verification: VerificationResult,
    ) -> FinalOutcome:
        if execution.dispatch_id != dispatch.dispatch_id or verification.dispatch_id != dispatch.dispatch_id:
            raise RoutingError("Execution and verification records must reference the dispatch being finalized")
        if verification.verifier_model != dispatch.verification.implementation.model:
            raise RoutingError("Verification was not performed by the assigned verifier")
        if dispatch.verification.independent and verification.verifier_model == dispatch.selected_implementation.model:
            raise RoutingError("Independent verification cannot use the selected execution model")

        notes: list[str] = []
        escalation_used = False
        if execution.status == "failed":
            status = "escalated" if dispatch.fallback_implementation else "failed"
            escalation_used = bool(dispatch.fallback_implementation)
            notes.append("Execution failed; fallback or escalation is required.")
        elif verification.status == "failed":
            status = "failed"
            notes.append("Independent verification failed; the outcome is not accepted.")
        elif verification.status == "needs_human" or dispatch.verification.human_approval_required:
            status = "awaiting_human"
            notes.append("The verification gate requires qualified human approval.")
        else:
            status = "completed"
            notes.append("Execution and independent verification passed.")

        return FinalOutcome(
            dispatch_id=dispatch.dispatch_id,
            task_id=dispatch.task_id,
            completed_at=utc_now(),
            status=status,  # type: ignore[arg-type]
            execution_status=execution.status,
            verification_status=verification.status,
            selected_model=dispatch.selected_implementation.model,
            verifier_model=verification.verifier_model,
            evidence=_unique([*execution.evidence, *verification.evidence]),
            failed_attempts=execution.failed_attempts,
            escalation_used=escalation_used,
            notes=notes,
        )

    def _classify_task(self, task: TaskRequest) -> tuple[str, str]:
        if task.task_type:
            if task.task_type not in self.config.team_routes:
                raise RoutingError(f"Unsupported explicit task type: {task.task_type}")
            return task.task_type, f"Explicit task type {task.task_type} was accepted."
        text = task.task.lower()
        for task_type, patterns in TASK_PATTERNS:
            if any(pattern in text for pattern in patterns):
                return task_type, f"Task classified as {task_type} by deterministic keyword rules."
        raise RoutingError("Task type is ambiguous; supply task_type rather than allowing an invented route")

    def _assess_risk(self, task: TaskRequest):
        if task.risk_level:
            return task.risk_level, f"Explicit risk level {task.risk_level} was accepted."
        text = task.task.lower()
        for risk in ("critical", "high", "medium"):
            if any(pattern in text for pattern in RISK_PATTERNS[risk]):
                return risk, f"Risk assessed as {risk} from task content."
        return "low", "Risk assessed as low because no higher-risk trigger was detected."

    def _resolve_worker(self, route: dict[str, Any], task: TaskRequest) -> str:
        worker = str(route["primary_worker"])
        overrides = route.get("worker_override_by_context", {})
        contexts = _unique([task.domain or "", *task.constraints.contexts])
        for context in contexts:
            if context in overrides:
                worker = str(overrides[context])
                break
        if worker not in self.config.worker_registry:
            raise RoutingError(f"Selected worker is not defined in the core registry: {worker}")
        return worker

    def _resolve_specialist(
        self, task: TaskRequest, team: str, worker: str
    ) -> tuple[tuple[str, dict[str, Any]] | None, str | None]:
        registry = self.config.specialist_registry
        if task.specialist:
            entry = registry.get(task.specialist)
            if not entry:
                raise RoutingError(f"Requested specialist is not registered: {task.specialist}")
            if entry.get("primary_team") != team or entry.get("worker_binding") != worker:
                raise RoutingError(
                    f"Requested specialist {task.specialist} does not match selected route {team}/{worker}"
                )
            return (task.specialist, entry), None

        normalized = re.sub(r"[^a-z0-9]+", "-", task.task.lower()).strip("-")
        candidates: list[tuple[str, dict[str, Any]]] = []
        for name, entry in registry.items():
            if entry.get("primary_team") != team or entry.get("worker_binding") != worker:
                continue
            tokens = [token for token in name.split("-") if token not in {"engineer", "specialist", "analyst"}]
            if name in normalized or (tokens and all(token in normalized for token in tokens)):
                candidates.append((name, entry))
        if len(candidates) == 1:
            return candidates[0], None
        if len(candidates) > 1:
            return None, "Multiple specialists matched; no specialist was selected without an explicit hint."
        return None, None

    def _resolve_capabilities(self, task: TaskRequest, worker: str) -> list[str]:
        worker_entry = self.config.worker_registry[worker]
        return _unique(
            [*worker_entry.get("required_capabilities", []), *task.constraints.required_capabilities]
        )

    def _resolve_primary(self, task_type: str, worker: str, task: TaskRequest) -> ImplementationChoice:
        route = self.config.implementation_routes.get(task_type, {})
        for key in ROUTE_IMPLEMENTATION_KEYS.get(task_type, ("primary",)):
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                choice = self._choice(candidate, f"routing.{task_type}.{key}")
                if self._eligible(choice, task):
                    return choice

        for key in ("fallback", "local_fallback", "escalation"):
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                choice = self._choice(candidate, f"routing.{task_type}.{key}")
                if self._eligible(choice, task):
                    return choice

        worker_entry = self.config.worker_registry[worker]
        for source_key in ("preferred_implementations", "fallbacks"):
            for model in worker_entry.get(source_key, []):
                choice = self._choice(
                    {"agent": "registry", "model": model}, f"workers.{worker}.{source_key}"
                )
                if self._eligible(choice, task):
                    return choice
        raise RoutingError(f"No eligible implementation found for {task_type}/{worker}")

    def _resolve_fallback(
        self,
        task_type: str,
        worker: str,
        capabilities: list[str],
        task: TaskRequest,
        exclude: set[str],
    ) -> ImplementationChoice | None:
        route = self.config.implementation_routes.get(task_type, {})
        for key in ("fallback", "local_fallback", "escalation"):
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                choice = self._choice(candidate, f"routing.{task_type}.{key}")
                if choice.model not in exclude and self._eligible(choice, task):
                    return choice

        for model in self.config.worker_registry[worker].get("fallbacks", []):
            choice = self._choice({"agent": "registry", "model": model}, f"workers.{worker}.fallbacks")
            if choice.model not in exclude and self._eligible(choice, task):
                return choice

        family = self._fallback_family(capabilities)
        for candidate in self.config.routing.get("fallback_order", {}).get(family, []):
            choice = self._choice(candidate, f"fallback_order.{family}")
            if choice.model not in exclude and self._eligible(choice, task):
                return choice
        return None

    def _verification_plan(
        self,
        task_type: str,
        risk: str,
        task: TaskRequest,
        primary: ImplementationChoice,
        worker: str,
        specialist_entry: dict[str, Any] | None,
    ) -> VerificationPlan:
        policy = self.config.routing.get("verification_policy", {}).get(risk, {})
        methods = list(policy.get("minimum", ["output_validation"]))
        route = self.config.implementation_routes.get(task_type, {})
        choice: ImplementationChoice | None = None
        for key in VERIFIER_KEYS:
            candidate = route.get(key)
            if isinstance(candidate, dict) and candidate.get("model"):
                possible = self._choice(candidate, f"routing.{task_type}.{key}")
                if possible.model != primary.model and self._eligible(possible, task):
                    choice = possible
                    break
        if choice is None:
            capabilities = ["high_reasoning"]
            choice = self._resolve_fallback(task_type, worker, capabilities, task, {primary.model})
        if choice is None or choice.model == primary.model:
            raise RoutingError("No independent verifier is available for the selected implementation")

        specialist_risk = (specialist_entry or {}).get("risk_profile")
        effective_risk = risk
        if specialist_risk in RISK_ORDER and RISK_ORDER[specialist_risk] > RISK_ORDER[risk]:
            effective_risk = specialist_risk
            methods = list(
                self.config.routing.get("verification_policy", {}).get(effective_risk, {}).get("minimum", methods)
            )
        human = task.constraints.require_human_approval or effective_risk == "critical"
        return VerificationPlan(
            team=str(self.config.team_routes[task_type].get("verification_team", "verification")),
            method=_unique(methods),
            implementation=choice,
            independent=True,
            human_approval_required=human,
        )

    def _choice(self, candidate: dict[str, Any], source: str) -> ImplementationChoice:
        model = str(candidate["model"])
        registry_entry = self._model_entry(model)
        profile = candidate.get("profile") or registry_entry.get("profile")
        return ImplementationChoice(
            agent=str(candidate.get("agent", "registry")),
            model=model,
            profile=str(profile) if profile else None,
            provider_family=str(registry_entry.get("provider_family")) if registry_entry.get("provider_family") else None,
            availability=str(registry_entry.get("availability")) if registry_entry.get("availability") else None,
            source=source,
        )

    def _model_entry(self, model: str) -> dict[str, Any]:
        direct = self.config.model_registry.get(model)
        if direct:
            return direct
        for entry in self.config.model_registry.values():
            if entry.get("concrete_model") == model or model in entry.get("candidate_implementations", []):
                return entry
        return {}

    def _eligible(self, choice: ImplementationChoice, task: TaskRequest) -> bool:
        if choice.model in task.constraints.blocked_implementations:
            return False
        if choice.provider_family and choice.provider_family in task.constraints.blocked_providers:
            return False
        return True

    @staticmethod
    def _fallback_family(capabilities: list[str]) -> str:
        capability_set = set(capabilities)
        for triggers, family in CAPABILITY_FAMILY:
            if capability_set.intersection(triggers):
                return family
        return "general_reasoning"
