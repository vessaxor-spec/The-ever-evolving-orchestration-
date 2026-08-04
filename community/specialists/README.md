# TEO Specialist Roster

The specialist roster extends TEO with domain-specific workers while preserving the core responsibility chain:

```text
Task
  -> Mission Control
  -> Team
  -> Worker
  -> Specialist
  -> Capability
  -> Implementation
  -> Verification
```

The specialists were originally created by **Sylvester Roxas** for the Roxas-Legion roster and integrated into TEO with the creator's permission.

## Integration rules

- A specialist narrows domain expertise. It does not replace a core team.
- Mission Control selects the team before selecting a specialist.
- The primary team owns the specialist's work and handoff.
- Supporting teams provide evidence, execution, review, or verification without collapsing responsibilities.
- High-risk and critical specialists require proportionate independence and human approval.
- Specialist instructions cannot override TEO routing, safety, verification, or governance policy.
- Every specialist role card preserves creator attribution.

## Allocation summary

| Primary team | Specialists |
|---|---:|
| Mission Control | 4 |
| Planning Team | 17 |
| Engineering Team | 13 |
| Research Team | 10 |
| Review Team | 10 |
| Verification Team | 2 |

**Total specialists:** 56

## Specialist index

| Specialist | Primary team | Worker binding | Supporting teams | Risk | Creator |
|---|---|---|---|---|---|
| [Agents Orchestrator](agents-orchestrator.md) | Mission Control | `orchestration` | Planning Team, Engineering Team, Verification Team | high | Sylvester Roxas |
| [Incident Commander](incident-commander.md) | Mission Control | `incident_response` | Engineering Team, Review Team, Verification Team | critical | Sylvester Roxas |
| [Operations Manager](operations-manager.md) | Mission Control | `operations` | Planning Team, Review Team, Verification Team | high | Sylvester Roxas |
| [Project Manager](project-manager.md) | Mission Control | `project_delivery` | Planning Team, Engineering Team, Verification Team | medium | Sylvester Roxas |
| [Architect](architect.md) | Planning Team | `architecture` | Engineering Team, Review Team | high | Sylvester Roxas |
| [Brand Designer](brand-designer.md) | Planning Team | `brand_design` | Research Team, Review Team | medium | Sylvester Roxas |
| [China Marketing Specialist](china-marketing-specialist.md) | Planning Team | `regional_marketing` | Research Team, Review Team | high | Sylvester Roxas |
| [Civil Engineer](civil-engineer.md) | Planning Team | `civil_engineering` | Review Team, Verification Team | critical | Sylvester Roxas |
| [Corporate Trainer](corporate-trainer.md) | Planning Team | `learning_design` | Research Team, Verification Team | medium | Sylvester Roxas |
| [Cross-Border Ecommerce](cross-border-ecommerce.md) | Planning Team | `ecommerce_strategy` | Research Team, Review Team | high | Sylvester Roxas |
| [Customer Success](customer-success.md) | Planning Team | `customer_success` | Research Team, Mission Control | medium | Sylvester Roxas |
| [Image Prompt Engineer](image-prompt-engineer.md) | Planning Team | `generative_media` | Research Team, Review Team | medium | Sylvester Roxas |
| [Paid Search Strategist](paid-search-strategist.md) | Planning Team | `paid_search` | Research Team, Verification Team | medium | Sylvester Roxas |
| [Paid Social Strategist](paid-social-strategist.md) | Planning Team | `paid_social` | Research Team, Verification Team | medium | Sylvester Roxas |
| [Product Manager](product-manager.md) | Planning Team | `product_strategy` | Research Team, Engineering Team, Review Team | high | Sylvester Roxas |
| [Programmatic Buyer](programmatic-buyer.md) | Planning Team | `programmatic_media` | Research Team, Verification Team | medium | Sylvester Roxas |
| [Sales Coach](sales-coach.md) | Planning Team | `sales_enablement` | Research Team, Verification Team | medium | Sylvester Roxas |
| [Sales Engineer](sales-engineer.md) | Planning Team | `solution_engineering` | Engineering Team, Research Team, Review Team | high | Sylvester Roxas |
| [Sales Strategist](sales-strategist.md) | Planning Team | `sales_strategy` | Research Team, Review Team | medium | Sylvester Roxas |
| [Social Media Strategist](social-media-strategist.md) | Planning Team | `social_strategy` | Research Team, Verification Team | medium | Sylvester Roxas |
| [Supply Chain Strategist](supply-chain-strategist.md) | Planning Team | `supply_chain` | Research Team, Review Team, Verification Team | high | Sylvester Roxas |
| [AI Engineer](ai-engineer.md) | Engineering Team | `ai_engineering` | Planning Team, Review Team, Verification Team | high | Sylvester Roxas |
| [Backend Engineer](backend-engineer.md) | Engineering Team | `backend` | Planning Team, Review Team, Verification Team | medium | Sylvester Roxas |
| [Blockchain Engineer](blockchain-engineer.md) | Engineering Team | `blockchain` | Review Team, Verification Team | critical | Sylvester Roxas |
| [Data Engineer](data-engineer.md) | Engineering Team | `data_engineering` | Planning Team, Review Team, Verification Team | high | Sylvester Roxas |
| [DevOps Engineer](devops-engineer.md) | Engineering Team | `devops` | Planning Team, Review Team, Verification Team | high | Sylvester Roxas |
| [DevSecOps Engineer](devsecops-engineer.md) | Engineering Team | `devsecops` | Review Team, Verification Team | critical | Sylvester Roxas |
| [Embedded Engineer](embedded-engineer.md) | Engineering Team | `embedded` | Planning Team, Review Team, Verification Team | high | Sylvester Roxas |
| [Frontend Engineer](frontend-engineer.md) | Engineering Team | `frontend` | Planning Team, Review Team, Verification Team | medium | Sylvester Roxas |
| [Game Engineer](game-engineer.md) | Engineering Team | `game_engineering` | Planning Team, Review Team, Verification Team | medium | Sylvester Roxas |
| [Rust Engineer](rust-engineer.md) | Engineering Team | `systems_engineering` | Planning Team, Review Team, Verification Team | high | Sylvester Roxas |
| [Spatial Terminal](spatial-terminal.md) | Engineering Team | `terminal_ui` | Planning Team, Review Team, Verification Team | medium | Sylvester Roxas |
| [Workflow Optimizer](workflow-optimizer.md) | Engineering Team | `automation` | Planning Team, Verification Team | medium | Sylvester Roxas |
| [XR Developer](xr-developer.md) | Engineering Team | `xr_engineering` | Planning Team, Review Team, Verification Team | medium | Sylvester Roxas |
| [Content Creator](content-creator.md) | Research Team | `content` | Planning Team, Review Team | medium | Sylvester Roxas |
| [Data Analyst](data-analyst.md) | Research Team | `analytics` | Planning Team, Verification Team | high | Sylvester Roxas |
| [Feedback Synthesizer](feedback-synthesizer.md) | Research Team | `user_research` | Planning Team, Review Team | medium | Sylvester Roxas |
| [Finance Analyst](finance-analyst.md) | Research Team | `financial_analysis` | Planning Team, Review Team, Verification Team | critical | Sylvester Roxas |
| [Market Analyst](market-analyst.md) | Research Team | `market_research` | Planning Team, Review Team | medium | Sylvester Roxas |
| [OSINT Specialist](osint-specialist.md) | Research Team | `osint` | Review Team, Verification Team | high | Sylvester Roxas |
| [Real Estate Agent](real-estate-agent.md) | Research Team | `real_estate` | Planning Team, Review Team | high | Sylvester Roxas |
| [Researcher](researcher.md) | Research Team | `research` | Planning Team, Review Team, Verification Team | medium | Sylvester Roxas |
| [Revenue Analyst](revenue-analyst.md) | Research Team | `revenue_analytics` | Planning Team, Verification Team | high | Sylvester Roxas |
| [ZK Steward](zk-steward.md) | Research Team | `knowledge_management` | Planning Team, Review Team | low | Sylvester Roxas |
| [Code Reviewer](code-reviewer.md) | Review Team | `code_review` | Engineering Team, Verification Team | high | Sylvester Roxas |
| [Compliance Auditor](compliance-auditor.md) | Review Team | `compliance` | Research Team, Verification Team | critical | Sylvester Roxas |
| [Legal Operations](legal-operations.md) | Review Team | `legal` | Research Team, Planning Team | critical | Sylvester Roxas |
| [Loan Officer Assistant](loan-officer-assistant.md) | Review Team | `lending_compliance` | Research Team, Planning Team, Verification Team | critical | Sylvester Roxas |
| [Malware Analyst](malware-analyst.md) | Review Team | `malware_analysis` | Research Team, Engineering Team, Verification Team | critical | Sylvester Roxas |
| [Red Team Advisor](red-team-advisor.md) | Review Team | `security_advisory` | Planning Team, Engineering Team, Verification Team | critical | Sylvester Roxas |
| [Security Engineer](security-engineer.md) | Review Team | `security` | Engineering Team, Research Team, Verification Team | critical | Sylvester Roxas |
| [SEO Specialist](seo-specialist.md) | Review Team | `seo_review` | Research Team, Planning Team, Verification Team | medium | Sylvester Roxas |
| [Tax Strategist](tax-strategist.md) | Review Team | `tax_review` | Research Team, Planning Team | critical | Sylvester Roxas |
| [UX Designer](ux-designer.md) | Review Team | `ux_review` | Planning Team, Research Team, Engineering Team, Verification Team | medium | Sylvester Roxas |
| [QA Engineer](qa-engineer.md) | Verification Team | `qa` | Engineering Team, Review Team | high | Sylvester Roxas |
| [Technical Writer](technical-writer.md) | Verification Team | `documentation_verification` | Research Team, Engineering Team, Review Team | medium | Sylvester Roxas |

## Machine-readable registry

The canonical allocation and binding data is available in [`specialists.yaml`](specialists.yaml).

## Source and credit

Each specialist role card includes the following attribution:

> Original specialist specification created by Sylvester Roxas for the Roxas-Legion specialist roster and integrated into TEO with permission.

This credit must remain in derived specialist files unless the creator requests otherwise.
