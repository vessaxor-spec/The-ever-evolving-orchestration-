from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    file = ROOT / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}: {old!r}; found {count}")
    write(path, text.replace(old, new, 1))


def insert_before(path: str, marker: str, section: str) -> None:
    text = read(path)
    if text.count(marker) != 1:
        raise SystemExit(f"Expected one insertion marker in {path}: {marker!r}")
    write(path, text.replace(marker, section.rstrip() + "\n\n" + marker, 1))


# Customer success: remove a sunset VoC product and add migration continuity.
replace_once(
    "community/specialists/customer-success.md",
    "  - Delighted\n",
    "",
)
insert_before(
    "community/specialists/customer-success.md",
    "## Health Score Decay Model",
    '''## Voice-of-Customer Platform Continuity

Survey and feedback platforms are systems of record for customer consent, contact history, response metadata, segmentation, and longitudinal trends. Verify product lifecycle, export capability, API support, retention, regional hosting, and integration status before designing a CSAT or NPS program around a vendor.

As of `tools_last_verified`, Delighted has been sunset and must not be recommended for new programs. A migration from a retiring VoC platform includes:

1. inventory surveys, question wording, distribution channels, schedules, automations, integrations, users, permissions, and dashboards;
2. export responses with timestamps, respondent identifiers, consent basis, tags, comments, and delivery metadata where lawfully available;
3. document retention, deletion, access, and regional-data requirements before transfer;
4. map historical scales and segments without silently changing trend definitions;
5. validate trigger delivery, suppression, deduplication, identity matching, and closed-loop workflows in the replacement;
6. run parallel validation where permitted before disabling the old integration;
7. preserve a read-only evidence archive and record the cutover date in reporting.

A vendor's shutdown does not justify losing historical customer evidence or breaking detractor follow-up obligations.''',
)

# Incident response: replace Opsgenie with Atlassian's current incident products and add lifecycle controls.
replace_once(
    "community/specialists/incident-commander.md",
    "  - OpsGenie",
    "  - Jira Service Management / Compass",
)
replace_once(
    "community/specialists/incident-commander.md",
    "  - JIRA / Linear (incident tracking)",
    "  - Jira / Linear (incident action tracking)",
)
replace_once(
    "community/specialists/incident-commander.md",
    "- Tool tasks: verify current status page or incident management tool capabilities (PagerDuty, OpsGenie, Incident.io) when recommending tooling",
    "- Tool tasks: verify current status page, paging, incident, and on-call capabilities (PagerDuty, Jira Service Management, Compass, incident.io, or equivalent) when recommending tooling",
)
insert_before(
    "community/specialists/incident-commander.md",
    "## Severity Reference",
    '''## Incident Tool Lifecycle and Exit Readiness

Incident tooling is part of the response control plane. Before adopting or renewing a paging, on-call, status, or incident-management platform, verify current sale status, support horizon, data export, API/webhook compatibility, mobile delivery, escalation semantics, audit retention, and migration path.

As of `tools_last_verified`, Atlassian no longer sells Opsgenie to new customers and has announced end of support and access on 5 April 2027. Do not recommend Opsgenie for a new deployment. Existing users require a governed migration to Jira Service Management, Compass, or another approved platform before the support deadline.

**Migration evidence:**

- schedules, rotations, overrides, teams, services, escalation policies, notification rules, integrations, heartbeats, status-page links, and audit history inventoried;
- alert deduplication, routing, acknowledgment, escalation, and handoff behavior replayed in a non-production test;
- mobile, SMS, voice, email, chat, webhook, and incident-creation paths verified;
- old and new platforms run in a controlled parallel period where feasible;
- rollback, missed-page detection, ownership, training, and final cutover are documented.

The incident commander validates operational readiness; procurement and platform implementation remain with their accountable owners.''',
)

# Corporate learning: use the current Seismic Learning name and treat vendor identity as volatile.
replace_once(
    "community/specialists/corporate-trainer.md",
    "- Tool tasks: verify current capabilities and pricing of LMS platforms (Workday Learning, Cornerstone, Docebo, Lessonly) when recommending a training infrastructure",
    "- Tool tasks: verify current capabilities and pricing of LMS platforms (Workday Learning, Cornerstone, Docebo, Seismic Learning, or equivalent) when recommending a training infrastructure",
)
insert_before(
    "community/specialists/corporate-trainer.md",
    "## Research Protocol",
    '''## Learning Platform Lifecycle and Naming

Learning-platform names, ownership, packaging, APIs, and migration paths are volatile. Seismic Learning is the current product name for the platform formerly known as Lessonly; use `Lessonly` only when referring to a legacy tenant, contract, export, URL, or historical integration.

Before recommending or migrating an LMS or learning platform, verify:

- current product and vendor name;
- supported content standards and import/export formats;
- learner, completion, assessment, skills, and audit-data export;
- SSO, SCIM, HRIS, CRM, webinar, content-authoring, and reporting integrations;
- accessibility, localization, mobile, privacy, retention, and regional-hosting requirements;
- licensing unit, inactive-user handling, implementation effort, support model, and exit capability.

A renamed product is not necessarily a drop-in replacement. Validate the actual tenant capabilities and contract rather than relying on the old brand name.''',
)

# Technical writing: correct the framework's current name without changing its four-type doctrine.
technical_path = "community/specialists/technical-writer.md"
technical = read(technical_path)
if technical.count("Divio") < 8:
    raise SystemExit("Expected multiple Divio references in technical-writer.md")
technical = technical.replace("description: Documentation specialist using the Divio system.", "description: Documentation specialist using Diátaxis.")
technical = technical.replace("  - Divio Documentation System", "  - Diátaxis documentation framework")
technical = technical.replace("Divio", "Diátaxis")
write(technical_path, technical)

# Malware analysis: use maintained CAPEv2 while retaining legacy Cuckoo report compatibility.
replace_once(
    "community/specialists/malware-analyst.md",
    "  - Cuckoo",
    "  - CAPEv2",
)
replace_once(
    "community/specialists/malware-analyst.md",
    "- Sandbox analysis: interpreting Cuckoo/ANY.RUN/Joe Sandbox reports, identifying sandbox evasion",
    "- Sandbox analysis: interpreting CAPEv2/ANY.RUN/Joe Sandbox reports and legacy Cuckoo-derived artifacts, identifying sandbox evasion",
)
replace_once(
    "community/specialists/malware-analyst.md",
    "- Sandbox report (Cuckoo JSON, ANY.RUN report, VirusTotal report)",
    "- Sandbox report (CAPEv2 output, legacy Cuckoo-derived JSON, ANY.RUN report, or VirusTotal report)",
)
replace_once(
    "community/specialists/malware-analyst.md",
    '"Interpret this Cuckoo sandbox report and extract ATT&CK TTPs"',
    '"Interpret this CAPEv2 sandbox report and extract ATT&CK TTPs"',
)
insert_before(
    "community/specialists/malware-analyst.md",
    "## Static Analysis Doctrine",
    '''## Sandbox Platform and Evidence Integrity

CAPEv2 is the maintained Cuckoo-derived sandbox baseline for new self-hosted analysis designs. Legacy Cuckoo reports may still be valid evidence inputs, but an unmaintained Cuckoo deployment must not be recommended as the default new platform.

Before dynamic analysis:

- confirm written authorization, sample provenance, hash, classification, handling restrictions, and analysis purpose;
- use an isolated, resettable environment with controlled networking, no production credentials, no shared clipboard or host mounts, and monitored egress;
- verify the sandbox release, guest image, signatures, extractors, behavioral modules, YARA/Sigma content, and dependency health;
- preserve original sample hashes, configuration, execution time, environment fingerprint, report version, packet capture, dropped artifacts, screenshots, and analyst notes;
- distinguish observed behavior from sandbox inference and from third-party reputation data;
- treat sandbox-detection or non-execution as an inconclusive result, not proof that a sample is benign;
- reset or destroy the analysis environment according to the approved containment procedure.

No tool lifecycle update changes this card's prohibition on malware execution outside isolated, authorized analysis environments.''',
)

# AI engineering: distinguish semantic caches from provider prompt/context caches and govern both.
replace_once(
    "community/specialists/ai-engineer.md",
    "- `cache_hit` — whether the response was served from semantic cache",
    "- `cache_type` — `none | semantic_response | provider_prompt_context`\n- `cache_read_tokens` / `cache_write_tokens` — provider-reported cached-token accounting when available\n- `cache_policy_version` — version/hash of the cache layout, TTL, and invalidation policy",
)
insert_before(
    "community/specialists/ai-engineer.md",
    "## Prompt Regression Testing Doctrine",
    '''## Prompt and Context Caching Governance

Two different cache classes must not be conflated:

1. **Semantic response cache** — returns a prior answer for a sufficiently similar request. It changes application behavior and requires semantic matching, freshness, authorization, and quality controls.
2. **Provider prompt/context cache** — reuses a stable prompt prefix or context inside the model provider while still generating a new response. It changes latency and token billing but should not silently change output semantics.

Provider support, automatic versus explicit caching, minimum cacheable size, TTL, retention, regional behavior, supported content, and pricing are volatile. Verify the current official API documentation for the selected model and endpoint.

**Design rules:**

- place stable instructions, schemas, examples, and reusable context before dynamic request content when the provider's cache semantics support prefix reuse;
- version the stable prefix and include the cache-policy version in traces;
- record cache-read tokens, cache-write tokens, latency, total cost, provider, model, and request class;
- invalidate on prompt, policy, tool schema, retrieval corpus, authorization, tenant, model, or safety-control changes that affect correctness;
- never share cached sensitive context across tenants or authorization boundaries;
- verify provider retention, data-use, encryption, residency, and deletion behavior before caching regulated or confidential material;
- test cached and uncached paths for output-quality equivalence and failure behavior;
- do not promise a universal percentage saving—report measured hit rate, latency, and cost for the actual workload.

Caching is an optimization layer, not a substitute for retrieval freshness, model evaluation, or access control.''',
)

# Orchestration: add workflow-engine/MCP deployment decisions and current n8n exposure controls.
replace_once(
    "community/specialists/agents-orchestrator.md",
    "  - agent frameworks (LangGraph, CrewAI, custom)",
    "  - agent frameworks (LangGraph, CrewAI, custom)\n  - n8n / Temporal workflow runtimes",
)
replace_once(
    "community/specialists/agents-orchestrator.md",
    "- Maintain agent capability registry: what each agent can do, what it cannot, and who it collaborates with",
    "- Maintain agent capability registry: what each agent can do, what it cannot, and who it collaborates with\n- Select the workflow runtime and MCP exposure mode based on determinism, replay, side effects, authority, observability, and failure recovery",
)
replace_once(
    "community/specialists/agents-orchestrator.md",
    "- Agent capability registry update (if new agents or tools were added)",
    "- Agent capability registry update (if new agents or tools were added)\n- Workflow-runtime and MCP exposure decision record",
)
replace_once(
    "community/specialists/agents-orchestrator.md",
    "- Orchestration framework tasks: verify current capabilities and limitations of orchestration tools (LangGraph, CrewAI, AutoGen, Temporal) before recommending",
    "- Orchestration framework tasks: verify current capabilities and limitations of orchestration tools (LangGraph, CrewAI, AutoGen, n8n, Temporal, or custom runtimes) before recommending",
)
insert_before(
    "community/specialists/agents-orchestrator.md",
    "## Agent Capability Versioning",
    '''## Workflow Runtime and MCP Exposure Decision

Choose the simplest execution model that satisfies the task. An MCP server, workflow engine, and reasoning agent solve different problems.

| Mode | Use when | Required controls |
|---|---|---|
| Deterministic workflow | Steps, inputs, branches, retries, and side effects are known | Idempotency, typed inputs, retries, replay, audit log, explicit approvals |
| Durable workflow runtime | Long-running state, timers, compensation, or exactly-once business coordination is required | Versioned workflow, deterministic replay rules, state migration, operator tooling |
| Agent graph | The task requires bounded interpretation, tool selection, planning, or adaptation | Eval suite, tool allow-list, budget, loop limits, uncertainty handling, HITL gates |
| MCP server | A capability must be exposed through a standard tool/resource/prompt interface | Authentication, authorization, schemas, least privilege, rate limits, audit, versioning |
| Hybrid | Deterministic control flow contains bounded reasoning stages | Workflow owns state and side effects; agents return typed proposals or evidence |

n8n can expose selected workflows through an instance-level MCP server in supported versions. Treat this as an external capability boundary:

- expose only explicitly reviewed workflows;
- verify current n8n version, MCP feature status, authentication, client compatibility, and execution permissions;
- separate read-only tools from side-effecting tools;
- require approval gates for payments, messages, provisioning, deletion, credential, and production changes;
- avoid exposing internal administrative or arbitrary-code workflows;
- log caller identity, workflow version, arguments, result, side effects, and failure classification;
- maintain a disable/rollback path independent of the agent using the tool.

Do not introduce an agent where a deterministic workflow is sufficient, and do not expose a workflow through MCP merely because the protocol is available.''',
)

# Code review: add AI-authored code provenance, hallucination, and licensing controls.
replace_once(
    "community/specialists/code-reviewer.md",
    "  - quality-gates",
    "  - quality-gates\n  - ai-authored-code-review",
)
replace_once(
    "community/specialists/code-reviewer.md",
    "- Codebase read access for onboarding tasks",
    "- Codebase read access for onboarding tasks\n- AI-generation provenance, model/tool metadata, prompts or agent run logs when available",
)
replace_once(
    "community/specialists/code-reviewer.md",
    "- Technical documentation artifact (guide, runbook, API reference, diagram)",
    "- Technical documentation artifact (guide, runbook, API reference, diagram)\n- AI-authored code provenance and verification findings when generation was used",
)
replace_once(
    "community/specialists/code-reviewer.md",
    "- Security vulnerability tasks: check for known CVEs in a specific library version before approving its use",
    "- Security vulnerability tasks: check for known CVEs in a specific library version before approving its use\n- AI-authored code tasks: verify cited APIs, packages, licenses, generated-code terms, and version-specific behavior against primary sources",
)
replace_once(
    "community/specialists/code-reviewer.md",
    "- Reviewing a PR or diff — all context is in the provided code; search adds no value",
    "- Reviewing pure local logic when all contracts, dependencies, and requirements are present; do not skip current-source verification when generated code depends on external APIs, packages, standards, or licenses",
)
insert_before(
    "community/specialists/code-reviewer.md",
    "## PR Quality Metrics Doctrine",
    '''## AI-Authored Code Review Protocol

AI-assisted code is reviewed as untrusted proposed code, not as evidence that an implementation is correct. The reviewer does not lower standards because a model, coding agent, or autocomplete tool produced the diff.

**Required checks:**

| Risk | Review action |
|---|---|
| Hallucinated API or option | Verify symbol, signature, version, behavior, and deprecation status in source code or official documentation |
| Invented dependency | Confirm the package exists in the intended registry, publisher/owner is correct, activity is legitimate, and the name is not typosquatted |
| License / provenance contamination | Review dependency licenses, copied comments or distinctive fragments, generated-code terms, notices, and organization policy |
| Security regression | Trace trust boundaries, validation, auth, secrets, deserialization, command execution, network access, file access, and failure paths |
| Unsupported assumption | Require evidence for platform limits, framework behavior, environment variables, paths, feature flags, and external contracts |
| Test mirroring | Ensure tests challenge requirements and failure modes rather than reproducing the generated implementation's assumptions |
| Hidden scope expansion | Compare the diff to the task, generation transcript where available, and dependency/config changes |
| Unclear authorship | Record the accountable human author/reviewer and the generation tool where policy requires it |

Rules:

- Execute or independently inspect critical paths; model-generated explanations and tests are not sole verification.
- Review lockfiles, manifests, generated files, migrations, CI, permissions, and infrastructure—not only source files highlighted by the agent.
- Require a human-readable rationale for security-sensitive, irreversible, or architectural changes.
- Block unverifiable APIs, packages, licenses, or claims rather than guessing that the model is probably current.
- Treat prompts and agent logs as potentially sensitive; do not require disclosure beyond organizational policy, but never infer provenance that was not provided.''',
)

# Workflow optimization: add an explicit deterministic automation vs agent decision gate.
replace_once(
    "community/specialists/workflow-optimizer.md",
    "  - workflow design",
    "  - workflow design\n  - agent-versus-automation selection",
)
replace_once(
    "community/specialists/workflow-optimizer.md",
    "  - UiPath / RPA tooling",
    "  - UiPath / RPA tooling\n  - n8n / Temporal\n  - MCP and agent workflow patterns",
)
replace_once(
    "community/specialists/workflow-optimizer.md",
    "- Recommend RPA, Zapier, Power Automate, or custom code based on fit — not familiarity",
    "- Recommend manual control, deterministic workflow, integration automation, RPA, custom service, or bounded agent based on fit — not novelty or familiarity",
)
replace_once(
    "community/specialists/workflow-optimizer.md",
    "- Tool evaluation matrix (weighted scoring, TCO, recommendation with rationale)",
    "- Tool and execution-mode evaluation matrix (weighted scoring, TCO, recommendation with rationale)",
)
replace_once(
    "community/specialists/workflow-optimizer.md",
    '"Compare Zapier vs Power Automate vs custom script for our invoice processing workflow"',
    '"Compare a deterministic workflow, RPA, custom service, and bounded agent for our invoice processing process"',
)
insert_before(
    "community/specialists/workflow-optimizer.md",
    "## Technical Feasibility Assessment",
    '''## Deterministic Automation vs Agent Decision

An agent is one execution option, not the default maturity destination. Choose the least autonomous mode that handles the process reliably.

| Mode | Appropriate when | Reject or constrain when |
|---|---|---|
| Manual / checklist | Low volume, changing process, judgment or accountability dominates | Volume and repetition justify standardization |
| Deterministic workflow / integration | Inputs, rules, branches, and expected outputs are known | Exceptions require interpretation that cannot be encoded economically |
| RPA | A stable UI is the only available integration surface | UI changes frequently, API exists, or failure is difficult to detect |
| Custom service | Scale, latency, reliability, domain logic, or ownership justifies software | Maintenance cost exceeds value or process is not stable |
| Bounded agent | Inputs are variable and the task requires interpretation, planning, retrieval, or tool selection | Transaction is deterministic, side effects are irreversible, evidence cannot be evaluated, or authority cannot be bounded |
| Human decision with agent assistance | Consequence, ambiguity, ethics, regulation, or relationship ownership requires a person | None—retain human accountability even when preparation is automated |

**Agent-specific cost and risk fields:**

- model/provider cost and availability;
- prompt, model, tool, and retrieval drift;
- evaluation-set design and regression burden;
- uncertainty detection and abstention behavior;
- tool allow-list, authorization, identity, and data egress;
- loop, token, latency, and retry budgets;
- replayability, idempotency, compensation, and audit evidence;
- human gate placement and accountable decision owner.

A bounded agent recommendation requires a measurable eval set, typed input/output contract, failure and fallback plan, and handoff to **agents-orchestrator** for implementation governance. If the same outcome can be achieved through deterministic rules at acceptable cost, prefer the deterministic design.''',
)

write(
    "docs/methodology/native-operations-refresh-2026-08-05.md",
    '''# Native Operations and Tool Lifecycle Refresh — 2026-08-05

This tranche updates specialist operations where product lifecycle or 2026-native AI practices changed the work itself.

## Tool lifecycle corrections

- Delighted was sunset on 30 June 2026; customer-success now requires VoC export and migration continuity.
- Opsgenie is no longer sold to new customers and is scheduled to end support/access on 5 April 2027; incident-commander now requires migration readiness.
- Lessonly is now Seismic Learning; corporate-trainer distinguishes current product identity from legacy tenants.
- The documentation framework is named Diátaxis, formerly known through the Divio documentation-system presentation.
- CAPEv2 is the maintained Cuckoo-derived sandbox baseline; malware-analyst retains compatibility with legacy Cuckoo report artifacts.

## Native operating protocols

- ai-engineer distinguishes semantic response caching from provider prompt/context caching.
- agents-orchestrator selects among deterministic workflows, durable runtimes, agent graphs, MCP servers, and hybrids; current n8n MCP exposure is treated as a governed capability boundary.
- code-reviewer treats AI-authored code as untrusted proposed code and verifies APIs, dependencies, licenses, provenance, tests, and external claims.
- workflow-optimizer explicitly decides among manual work, deterministic automation, RPA, custom services, bounded agents, and human decisions.

## Primary authorities reviewed

Official product documentation, lifecycle notices, maintained project documentation, and current provider API documentation were used. Volatile availability, pricing, limits, and implementation details remain subject to live verification under the specialist freshness policy.
''',
)

write(
    "tests/test_native_operations_refresh.py",
    '''from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIALISTS = ROOT / "community" / "specialists"


def text(name: str) -> str:
    return (SPECIALISTS / name).read_text(encoding="utf-8")


def test_retired_and_renamed_tools_are_corrected() -> None:
    customer = text("customer-success.md")
    incident = text("incident-commander.md")
    trainer = text("corporate-trainer.md")
    writer = text("technical-writer.md")
    malware = text("malware-analyst.md")

    assert "  - Delighted" not in customer
    assert "## Voice-of-Customer Platform Continuity" in customer
    assert "Delighted has been sunset" in customer

    assert "  - OpsGenie" not in incident
    assert "Jira Service Management / Compass" in incident
    assert "5 April 2027" in incident

    assert "Seismic Learning" in trainer
    assert "Docebo, Lessonly" not in trainer

    assert "Diátaxis" in writer
    assert "Divio" not in writer

    assert "  - CAPEv2" in malware
    assert "  - Cuckoo" not in malware
    assert "## Sandbox Platform and Evidence Integrity" in malware


def test_ai_engineer_governs_prompt_and_context_caching() -> None:
    card = text("ai-engineer.md")
    assert "## Prompt and Context Caching Governance" in card
    assert "Semantic response cache" in card
    assert "Provider prompt/context cache" in card
    assert "cache_read_tokens" in card
    assert "never share cached sensitive context across tenants" in card


def test_orchestrator_selects_runtime_and_governs_mcp_exposure() -> None:
    card = text("agents-orchestrator.md")
    assert "## Workflow Runtime and MCP Exposure Decision" in card
    assert "n8n can expose selected workflows through an instance-level MCP server" in card
    assert "Do not introduce an agent where a deterministic workflow is sufficient" in card
    assert "Workflow-runtime and MCP exposure decision record" in card


def test_code_review_covers_ai_authored_code() -> None:
    card = text("code-reviewer.md")
    assert "## AI-Authored Code Review Protocol" in card
    assert "Hallucinated API or option" in card
    assert "License / provenance contamination" in card
    assert "model-generated explanations and tests are not sole verification" in card
    assert "search adds no value" not in card


def test_workflow_optimizer_has_agent_decision_gate() -> None:
    card = text("workflow-optimizer.md")
    assert "## Deterministic Automation vs Agent Decision" in card
    assert "An agent is one execution option, not the default maturity destination" in card
    assert "Bounded agent" in card
    assert "prefer the deterministic design" in card
    assert "handoff to **agents-orchestrator**" in card
''',
)
