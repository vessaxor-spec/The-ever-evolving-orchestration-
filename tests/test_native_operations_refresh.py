from pathlib import Path

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
