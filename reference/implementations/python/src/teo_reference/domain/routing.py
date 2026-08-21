from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Protocol


class RoutingTask(Protocol):
    task: str
    task_type: str | None
    risk_level: str | None


class RoutingError(RuntimeError):
    """Raised when deterministic domain routing cannot produce a valid decision."""


TASK_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
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
        "user_research",
        (
            "user research",
            "feedback synthesis",
            "synthesize feedback",
            "synthesise feedback",
            "interview transcript",
            "interview transcripts",
            "survey responses",
            "usability findings",
            "user pain points",
            "voice of customer",
            "customer feedback",
            "support tickets into themes",
            "affinity map",
            "jobs to be done",
            "jtbd",
            "persona from feedback",
            "nps detractors",
        ),
    ),
    (
        "compliance_review",
        (
            "compliance audit",
            "compliance review",
            "soc 2",
            "soc2",
            "iso 27001",
            "iso 27701",
            "pci dss",
            "pci-dss",
            "gdpr compliance",
            "ccpa compliance",
            "hipaa compliance",
            "privacy impact assessment",
            "data protection impact assessment",
            "dpia",
            "control mapping",
            "operating effectiveness",
            "audit evidence",
            "ai act compliance",
            "agentic trust",
            "privacy policy based on data flow",
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
)

RISK_PATTERNS: Mapping[str, tuple[str, ...]] = {
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


def classify_task(
    task: RoutingTask,
    *,
    supported_task_types: Collection[str],
) -> tuple[str, str]:
    """Classify a task using only explicit input and deterministic domain rules."""
    if task.task_type:
        if task.task_type not in supported_task_types:
            raise RoutingError(f"Unsupported explicit task type: {task.task_type}")
        return task.task_type, f"Explicit task type {task.task_type} was accepted."

    text = task.task.lower()
    for task_type, patterns in TASK_PATTERNS:
        if any(pattern in text for pattern in patterns):
            return task_type, f"Task classified as {task_type} by deterministic keyword rules."
    raise RoutingError("Task type is ambiguous; supply task_type rather than allowing an invented route")


def assess_risk(
    task: RoutingTask,
    *,
    risk_order: Mapping[str, int],
) -> tuple[str, str]:
    """Return the monotonic effective risk and its deterministic explanation."""
    text = task.task.lower()
    content_risk = "low"
    content_trigger: str | None = None
    for risk in ("critical", "high", "medium"):
        matched = next((pattern for pattern in RISK_PATTERNS[risk] if pattern in text), None)
        if matched:
            content_risk = risk
            content_trigger = matched
            break

    declared_risk = task.risk_level or "low"
    effective_risk = (
        declared_risk
        if risk_order[declared_risk] >= risk_order[content_risk]
        else content_risk
    )

    if task.risk_level and risk_order[task.risk_level] < risk_order[content_risk]:
        return (
            effective_risk,
            f"Declared risk {task.risk_level} could not lower the content-derived {content_risk} risk floor"
            + (f" triggered by {content_trigger!r}." if content_trigger else "."),
        )
    if task.risk_level and risk_order[task.risk_level] > risk_order[content_risk]:
        return (
            effective_risk,
            f"Declared risk {task.risk_level} elevated the content-derived {content_risk} risk floor.",
        )
    if task.risk_level:
        return effective_risk, f"Declared risk {task.risk_level} matched the effective risk floor."
    if content_risk != "low":
        return (
            content_risk,
            f"Risk assessed as {content_risk} from task content"
            + (f" using trigger {content_trigger!r}." if content_trigger else "."),
        )
    return "low", "Risk assessed as low because no higher-risk trigger was detected."
