# TEO Specialist Roster

The specialist roster extends TEO with the full, battle-tested Roxas-Legion specifications while preserving the core responsibility chain:

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

The specialists were created by **Sylvester Roxas** for Roxas-Legion and integrated into TEO with the creator's permission.

## Canonical preservation rule

The original Roxas-Legion Markdown file is the canonical capability definition for each specialist. TEO does not summarize, narrow, demote, simplify, or rewrite the Legion role.

Each TEO role card therefore follows this order:

1. The complete original Roxas-Legion specification, unchanged.
2. A separate TEO Allocation appendix containing team placement, supporting teams, worker binding, risk profile, and registry links.

The allocation appendix controls where and how the specialist participates in TEO. It does not reduce or redefine what the specialist can do. See the binding [`Roxas-Legion Preservation Contract`](PRESERVATION.md).

## Integration rules

- The full Roxas-Legion specification remains authoritative for specialist identity, capabilities, protocols, responsibilities, outputs, boundaries, collaboration rules, and examples.
- Mission Control selects the owning team before selecting a specialist.
- The primary team owns routing, task scope, handoff, and acceptance responsibility.
- Supporting teams provide planning, evidence, execution, review, or verification without rewriting the specialist.
- TEO governance adds orchestration and proportional controls around consequential work. It must not silently remove or weaken specialist capability.
- Any capability reduction or behavioral restriction requires explicit written approval from Sylvester Roxas and a versioned migration record.
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

| Specialist | Primary team | Worker binding | Supporting teams | Risk | Description |
|---|---|---|---|---|---|
| [Agents Orchestrator](agents-orchestrator.md) | Mission Control | `orchestration` | Planning Team, Engineering Team, Verification Team | high | Coordinates multi-agent task decomposition, routing, handoffs, and governance. |
| [Incident Commander](incident-commander.md) | Mission Control | `incident_response` | Engineering Team, Review Team, Verification Team | critical | Leads severity-based incident response, communications, recovery, and postmortems. |
| [Operations Manager](operations-manager.md) | Mission Control | `operations` | Planning Team, Review Team, Verification Team | high | Designs operational systems, controls, vendor workflows, and service performance. |
| [Project Manager](project-manager.md) | Mission Control | `project_delivery` | Planning Team, Engineering Team, Verification Team | medium | Plans and governs delivery scope, milestones, dependencies, risks, and execution. |
| [Architect](architect.md) | Planning Team | `architecture` | Engineering Team, Review Team | high | Designs scalable systems, ADRs, C4 models, migrations, and explicit trade-off analysis. |
| [Brand Designer](brand-designer.md) | Planning Team | `brand_design` | Research Team, Review Team | medium | Defines brand strategy, visual identity, design systems, and production guidance. |
| [China Marketing Specialist](china-marketing-specialist.md) | Planning Team | `regional_marketing` | Research Team, Review Team | high | Plans compliant marketing across Chinese platforms, channels, and market conventions. |
| [Civil Engineer](civil-engineer.md) | Planning Team | `civil_engineering` | Review Team, Verification Team | critical | Produces structural and civil analysis, calculations, code checks, and design documentation. |
| [Corporate Trainer](corporate-trainer.md) | Planning Team | `learning_design` | Research Team, Verification Team | medium | Designs measurable adult-learning programs, curricula, facilitation, and assessment. |
| [Cross-Border Ecommerce](cross-border-ecommerce.md) | Planning Team | `ecommerce_strategy` | Research Team, Review Team | high | Plans international marketplace entry, localization, compliance, logistics, and unit economics. |
| [Customer Success](customer-success.md) | Planning Team | `customer_success` | Research Team, Mission Control | medium | Builds onboarding, adoption, health scoring, retention, expansion, and escalation programs. |
| [Image Prompt Engineer](image-prompt-engineer.md) | Planning Team | `generative_media` | Research Team, Review Team | medium | Engineers reproducible image prompts, visual controls, safety checks, and quality evaluation. |
| [Paid Search Strategist](paid-search-strategist.md) | Planning Team | `paid_search` | Research Team, Verification Team | medium | Designs paid-search structure, bidding, query controls, measurement, and optimization. |
| [Paid Social Strategist](paid-social-strategist.md) | Planning Team | `paid_social` | Research Team, Verification Team | medium | Designs paid-social funnels, creative testing, targeting, attribution, and budget optimization. |
| [Product Manager](product-manager.md) | Planning Team | `product_strategy` | Research Team, Engineering Team, Review Team | high | Converts user and business needs into product strategy, prioritization, discovery, and delivery decisions. |
| [Programmatic Buyer](programmatic-buyer.md) | Planning Team | `programmatic_media` | Research Team, Verification Team | medium | Plans and optimizes programmatic media, inventory, targeting, bidding, brand safety, and measurement. |
| [Sales Coach](sales-coach.md) | Planning Team | `sales_enablement` | Research Team, Verification Team | medium | Develops sales skills, discovery quality, pipeline discipline, role plays, and forecast behavior. |
| [Sales Engineer](sales-engineer.md) | Planning Team | `solution_engineering` | Engineering Team, Research Team, Review Team | high | Leads technical discovery, demos, POCs, solution architecture, and competitive proof. |
| [Sales Strategist](sales-strategist.md) | Planning Team | `sales_strategy` | Research Team, Review Team | medium | Builds deal strategy, qualification, account expansion, outbound motions, and proposals. |
| [Social Media Strategist](social-media-strategist.md) | Planning Team | `social_strategy` | Research Team, Verification Team | medium | Designs platform-native organic social strategy, community systems, content cadence, and commerce. |
| [Supply Chain Strategist](supply-chain-strategist.md) | Planning Team | `supply_chain` | Research Team, Review Team, Verification Team | high | Optimizes sourcing, suppliers, logistics, inventory, resilience, and total landed cost. |
| [AI Engineer](ai-engineer.md) | Engineering Team | `ai_engineering` | Planning Team, Review Team, Verification Team | high | Designs and implements AI systems, model integration, evaluation, retrieval, and production controls. |
| [Backend Engineer](backend-engineer.md) | Engineering Team | `backend` | Planning Team, Review Team, Verification Team | medium | Builds secure APIs, services, data access, reliability, and scalable backend architecture. |
| [Blockchain Engineer](blockchain-engineer.md) | Engineering Team | `blockchain` | Review Team, Verification Team | critical | Designs smart contracts, blockchain systems, testing, deployment, and security controls. |
| [Data Engineer](data-engineer.md) | Engineering Team | `data_engineering` | Planning Team, Review Team, Verification Team | high | Builds governed data pipelines, lakehouse layers, contracts, quality controls, and observability. |
| [DevOps Engineer](devops-engineer.md) | Engineering Team | `devops` | Planning Team, Review Team, Verification Team | high | Designs CI/CD, infrastructure, containers, observability, reliability, and disaster recovery. |
| [DevSecOps Engineer](devsecops-engineer.md) | Engineering Team | `devsecops` | Review Team, Verification Team | critical | Integrates security into software supply chains, CI/CD, infrastructure, secrets, and compliance. |
| [Embedded Engineer](embedded-engineer.md) | Engineering Team | `embedded` | Planning Team, Review Team, Verification Team | high | Builds firmware, RTOS systems, hardware interfaces, secure boot, and resource-constrained software. |
| [Frontend Engineer](frontend-engineer.md) | Engineering Team | `frontend` | Planning Team, Review Team, Verification Team | medium | Builds accessible, performant interfaces, design-system components, state management, and web quality. |
| [Game Engineer](game-engineer.md) | Engineering Team | `game_engineering` | Planning Team, Review Team, Verification Team | medium | Designs gameplay systems, engine architecture, performance budgets, multiplayer, and telemetry. |
| [Rust Engineer](rust-engineer.md) | Engineering Team | `systems_engineering` | Planning Team, Review Team, Verification Team | high | Engineers production Rust across ownership, unsafe code, FFI, async, cross-compilation, and performance. |
| [Spatial Terminal](spatial-terminal.md) | Engineering Team | `terminal_ui` | Planning Team, Review Team, Verification Team | medium | Builds Swift terminal emulation, glyph rendering, SwiftTerm integration, and visionOS terminal UX. |
| [Workflow Optimizer](workflow-optimizer.md) | Engineering Team | `automation` | Planning Team, Verification Team | medium | Maps processes, quantifies waste, evaluates automation, calculates ROI, and designs future workflows. |
| [XR Developer](xr-developer.md) | Engineering Team | `xr_engineering` | Planning Team, Review Team, Verification Team | medium | Builds visionOS, WebXR, spatial interfaces, rendering, interaction, accessibility, and comfort systems. |
| [Content Creator](content-creator.md) | Research Team | `content` | Planning Team, Review Team | medium | Develops research-backed content systems, narratives, editorial assets, and multi-format distribution. |
| [Data Analyst](data-analyst.md) | Research Team | `analytics` | Planning Team, Verification Team | high | Performs statistical analysis, metric design, experimentation, visualization, and decision support. |
| [Feedback Synthesizer](feedback-synthesizer.md) | Research Team | `user_research` | Planning Team, Review Team | medium | Converts qualitative and quantitative feedback into themes, evidence, priorities, and product insights. |
| [Finance Analyst](finance-analyst.md) | Research Team | `financial_analysis` | Planning Team, Review Team, Verification Team | critical | Builds financial models, forecasts, valuation, performance analysis, controls, and decision support. |
| [Market Analyst](market-analyst.md) | Research Team | `market_research` | Planning Team, Review Team | medium | Sizes markets, evaluates competitors, tracks signals, and produces evidence-based market strategy. |
| [OSINT Specialist](osint-specialist.md) | Research Team | `osint` | Review Team, Verification Team | high | Conducts authorized passive reconnaissance, infrastructure mapping, source validation, and intelligence synthesis. |
| [Real Estate Agent](real-estate-agent.md) | Research Team | `real_estate` | Planning Team, Review Team | high | Supports property search, valuation, transaction analysis, diligence, and market comparison. |
| [Researcher](researcher.md) | Research Team | `research` | Planning Team, Review Team, Verification Team | medium | Conducts structured research, source evaluation, synthesis, citations, and uncertainty management. |
| [Revenue Analyst](revenue-analyst.md) | Research Team | `revenue_analytics` | Planning Team, Verification Team | high | Analyzes pipeline, forecasting, conversion, retention, unit economics, and revenue performance. |
| [ZK Steward](zk-steward.md) | Research Team | `knowledge_management` | Planning Team, Review Team | low | Builds Zettelkasten knowledge systems, atomic notes, concept links, maps, and long-term synthesis. |
| [Code Reviewer](code-reviewer.md) | Review Team | `code_review` | Engineering Team, Verification Team | high | Performs correctness, maintainability, security, performance, and test-quality review. |
| [Compliance Auditor](compliance-auditor.md) | Review Team | `compliance` | Research Team, Verification Team | critical | Evaluates control design, evidence, regulatory obligations, gaps, and remediation readiness. |
| [Legal Operations](legal-operations.md) | Review Team | `legal` | Research Team, Planning Team | critical | Supports contract lifecycle, legal intake, matter management, holds, spend, and legal process controls. |
| [Loan Officer Assistant](loan-officer-assistant.md) | Review Team | `lending_compliance` | Research Team, Planning Team, Verification Team | critical | Supports lending intake, documentation, qualification, compliance, and decision preparation. |
| [Malware Analyst](malware-analyst.md) | Review Team | `malware_analysis` | Research Team, Engineering Team, Verification Team | critical | Performs authorized defensive malware triage, static and dynamic analysis, detection, and reporting. |
| [Red Team Advisor](red-team-advisor.md) | Review Team | `security_advisory` | Planning Team, Engineering Team, Verification Team | critical | Designs authorized adversary simulations, threat scenarios, control testing, and defensive improvement plans. |
| [Security Engineer](security-engineer.md) | Review Team | `security` | Engineering Team, Research Team, Verification Team | critical | Performs threat modeling, secure SDLC, detection engineering, zero-trust design, and security audits. |
| [SEO Specialist](seo-specialist.md) | Review Team | `seo_review` | Research Team, Planning Team, Verification Team | medium | Audits technical SEO, content architecture, authority, Baidu visibility, and app-store discoverability. |
| [Tax Strategist](tax-strategist.md) | Review Team | `tax_review` | Research Team, Planning Team | critical | Provides multi-jurisdiction tax analysis, structuring, transfer pricing, risk scoring, and audit support. |
| [UX Designer](ux-designer.md) | Review Team | `ux_review` | Planning Team, Research Team, Engineering Team, Verification Team | medium | Conducts UX research, information architecture, design systems, accessibility, and developer handoff. |
| [QA Engineer](qa-engineer.md) | Verification Team | `qa` | Engineering Team, Review Team | high | Designs test strategy, automation, coverage, release gates, defect analysis, and quality evidence. |
| [Technical Writer](technical-writer.md) | Verification Team | `documentation_verification` | Research Team, Engineering Team, Review Team | medium | Produces Divio-typed documentation, API references, tested examples, glossaries, and documentation governance. |

## Machine-readable registry

The canonical TEO allocation and binding data is available in [`specialists.yaml`](specialists.yaml). It records routing metadata only. The linked Roxas-Legion role cards remain the canonical capability specifications.

## Source and credit

Every specialist role card preserves the creator attribution and identifies its original source:

> Creator: Sylvester Roxas  
> Original source: Roxas-Legion specialist roster

This credit and the complete source specification must remain in derived specialist files unless Sylvester Roxas explicitly requests otherwise.
