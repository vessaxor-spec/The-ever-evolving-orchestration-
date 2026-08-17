# TEO Specialist Roster

The specialist roster extends TEO with preserved specialist role cards while keeping the control chain explicit:

```text
Task
  -> Mission Control
  -> Team
  -> Worker
  -> Specialist
  -> Capability
  -> Implementation
  -> Independent Verification
```

The specialists were created by **Sylvester Roxas** and integrated into TEO.

## Current control-plane roster

The active executable configuration currently resolves to:

- **10 teams**
- **84 workers**
- **82 active specialists**
- **4 Mission Control workers**

The 82 active specialists are composed of:

- 56 preserved base specialists in [`specialists.yaml`](specialists.yaml)
- 22 principal-engineering specialists activated through [`principal-engineering-active.yaml`](principal-engineering-active.yaml)
- 4 bounded workforce/orchestration specialists activated through [`workforce-expansion-active.yaml`](workforce-expansion-active.yaml)

The activation boundaries are recorded in:

- [`policy/routing/activation/principal-engineering.yaml`](../../policy/routing/activation/principal-engineering.yaml), which extended the active roster from 56 to 78
- [`policy/routing/activation/workforce-expansion.yaml`](../../policy/routing/activation/workforce-expansion.yaml), which extended the active roster from 78 to 82

The executable `ConfigBundle` composition is the current roster truth. The canonical operational snapshot is tracked in [`docs/stewardship/progress-tracker.md`](../../docs/stewardship/progress-tracker.md).

## Current primary-team allocation

| Primary team | Active specialists |
|---|---:|
| Mission Control | 6 |
| Planning Team | 17 |
| Engineering Team | 12 |
| Platform and Reliability | 10 |
| Systems Engineering | 1 |
| Physical Systems | 7 |
| Research Team | 13 |
| Assurance | 4 |
| Review Team | 10 |
| Verification Team | 2 |

**Total active specialists: 82**

These counts reflect current allocation overrides and active extensions. Do not infer current team ownership from the original 56-role import alone.

## Regulated evidence pilot

Six active specialists currently participate in the bounded regulated evidence pilot: Legal Operations, Tax Strategist, Loan Officer Assistant, Compliance Auditor, Civil Engineer, and Embedded Engineer. The pilot has completed two formal refresh cycles and its executable stability qualification without rewriting or narrowing any canonical specialist role card.

The active claim registry is [`policy/specialists/evidence-pilot.yaml`](../../policy/specialists/evidence-pilot.yaml), the qualification contract is [`policy/specialists/evidence-stability-qualification.yaml`](../../policy/specialists/evidence-stability-qualification.yaml), and the completed qualification evidence is preserved under [`docs/history/validation/`](../../docs/history/validation/). Seven-day authority resolution remains continuous monitoring. Qualification does not add specialists to the pilot automatically; expansion requires explicit next risk-tier batch approval and a separate reviewed change.

## Canonical preservation rule

Each specialist Markdown file is the canonical capability definition for that specialist. TEO does not summarize, narrow, demote, simplify, or rewrite the specialist role.

Each TEO role card therefore follows this order:

1. The complete specialist specification.
2. A separate TEO Allocation appendix containing team placement, supporting teams, worker binding, risk profile, and registry links.

The allocation appendix controls where and how the specialist participates in TEO. It does not reduce or redefine what the specialist can do. See the binding [`Specialist Preservation Contract`](PRESERVATION.md).

## Integration rules

- The full specialist specification remains authoritative for specialist identity, capabilities, protocols, responsibilities, outputs, boundaries, collaboration rules, and examples.
- Mission Control selects the owning team before selecting a specialist.
- The primary team owns routing, task scope, handoff, and acceptance responsibility.
- Supporting teams provide planning, evidence, execution, review, or verification without rewriting the specialist.
- TEO governance adds orchestration and proportional controls around consequential work. It must not silently remove or weaken specialist capability.
- Any capability reduction or behavioral restriction requires explicit written approval from Sylvester Roxas and a versioned migration record.
- Every specialist role card preserves creator attribution.

## Active specialist index

This README intentionally does **not** duplicate specialist descriptions, worker bindings, supporting-team lists, or risk metadata. Those values already exist in the role cards and machine-readable allocation registries and duplicating them here created documentation drift.

### Preserved base roster: 56

- [Agents Orchestrator](agents-orchestrator.md)
- [Incident Commander](incident-commander.md)
- [Operations Manager](operations-manager.md)
- [Project Manager](project-manager.md)
- [Architect](architect.md)
- [Brand Designer](brand-designer.md)
- [China Marketing Specialist](china-marketing-specialist.md)
- [Civil Engineer](civil-engineer.md)
- [Corporate Trainer](corporate-trainer.md)
- [Cross-Border Ecommerce](cross-border-ecommerce.md)
- [Customer Success](customer-success.md)
- [Image Prompt Engineer](image-prompt-engineer.md)
- [Paid Search Strategist](paid-search-strategist.md)
- [Paid Social Strategist](paid-social-strategist.md)
- [Product Manager](product-manager.md)
- [Programmatic Buyer](programmatic-buyer.md)
- [Sales Coach](sales-coach.md)
- [Sales Engineer](sales-engineer.md)
- [Sales Strategist](sales-strategist.md)
- [Social Media Strategist](social-media-strategist.md)
- [Supply Chain Strategist](supply-chain-strategist.md)
- [AI Engineer](ai-engineer.md)
- [Backend Engineer](backend-engineer.md)
- [Blockchain Engineer](blockchain-engineer.md)
- [Data Engineer](data-engineer.md)
- [DevOps Engineer](devops-engineer.md)
- [DevSecOps Engineer](devsecops-engineer.md)
- [Embedded Engineer](embedded-engineer.md)
- [Frontend Engineer](frontend-engineer.md)
- [Game Engineer](game-engineer.md)
- [Rust Engineer](rust-engineer.md)
- [Spatial Terminal](spatial-terminal.md)
- [Workflow Optimizer](workflow-optimizer.md)
- [XR Developer](xr-developer.md)
- [Content Creator](content-creator.md)
- [Data Analyst](data-analyst.md)
- [Feedback Synthesizer](feedback-synthesizer.md)
- [Finance Analyst](finance-analyst.md)
- [Market Analyst](market-analyst.md)
- [OSINT Specialist](osint-specialist.md)
- [Real Estate Agent](real-estate-agent.md)
- [Researcher](researcher.md)
- [Revenue Analyst](revenue-analyst.md)
- [ZK Steward](zk-steward.md)
- [Code Reviewer](code-reviewer.md)
- [Compliance Auditor](compliance-auditor.md)
- [Legal Operations](legal-operations.md)
- [Loan Officer Assistant](loan-officer-assistant.md)
- [Malware Analyst](malware-analyst.md)
- [Red Team Advisor](red-team-advisor.md)
- [Security Engineer](security-engineer.md)
- [SEO Specialist](seo-specialist.md)
- [Tax Strategist](tax-strategist.md)
- [UX Designer](ux-designer.md)
- [QA Engineer](qa-engineer.md)
- [Technical Writer](technical-writer.md)

### Principal-engineering activation: 22

- [Cloud Architect](cloud-architect.md)
- [Mobile Engineer](mobile-engineer.md)
- [Compiler Toolchain Engineer](compiler-toolchain-engineer.md)
- [Distributed Systems Engineer](distributed-systems-engineer.md)
- [Database Reliability Engineer](database-reliability-engineer.md)
- [Network Engineer](network-engineer.md)
- [Platform Engineer](platform-engineer.md)
- [Performance Engineer](performance-engineer.md)
- [FinOps Engineer](finops-engineer.md)
- [Site Reliability Engineer](site-reliability-engineer.md)
- [MLOps Engineer](mlops-engineer.md)
- [Systems Requirements Engineer](systems-requirements-engineer.md)
- [Hardware Engineer](hardware-engineer.md)
- [Robotics Autonomous Systems Engineer](robotics-autonomous-systems-engineer.md)
- [Silicon ASIC Engineer](silicon-asic-engineer.md)
- [Aerospace Satellite Engineer](aerospace-satellite-engineer.md)
- [Manufacturing Engineer](manufacturing-engineer.md)
- [Applied Scientist](applied-scientist.md)
- [Privacy Engineer](privacy-engineer.md)
- [Functional Safety Engineer](functional-safety-engineer.md)
- [Formal Methods Engineer](formal-methods-engineer.md)
- [Application Security Engineer](application-security-engineer.md)

### Workforce and orchestration expansion: 4

- [Fraud and Forensic Investigation Specialist](fraud-forensic-investigation-specialist.md)
- [Talent Acquisition Specialist](talent-acquisition-specialist.md)
- [Insurance Claims Specialist](insurance-claims-specialist.md)
- [Orchestration Evaluation Analyst](orchestration-evaluation-analyst.md)

## Machine-readable authority

Use these sources in order:

1. [`specialists.yaml`](specialists.yaml) for the preserved 56-role base allocation registry.
2. [`principal-engineering-active.yaml`](principal-engineering-active.yaml) for the 22-role principal-engineering extension and allocation overrides.
3. [`workforce-expansion-active.yaml`](workforce-expansion-active.yaml) for the four currently active bounded extensions.
4. The applicable activation policy under [`policy/routing/activation/`](../../policy/routing/activation/) for activation scope and gates.
5. Executable `ConfigBundle` composition for the effective active roster.
6. [`docs/stewardship/progress-tracker.md`](../../docs/stewardship/progress-tracker.md) for the current operational snapshot.

Role-card Markdown files remain the canonical capability specifications. Allocation registries add routing context and must not rewrite or reduce those capabilities.

## Documentation truth rule

Roster counts and the active specialist index are control-plane documentation and must remain aligned with executable configuration.

When specialists are activated, retired, or reallocated:

- update the applicable machine-readable registry and activation policy first;
- update this README in the same change;
- update the canonical Progress Tracker when the active roster count changes;
- keep documentation-truth tests aligned with the executable `ConfigBundle`;
- do not preserve obsolete counts as current truth.

## Creator credit

Every specialist role card preserves the creator attribution:

> Creator: Sylvester Roxas

This credit and the complete specialist specification must remain unless Sylvester Roxas explicitly requests otherwise.
