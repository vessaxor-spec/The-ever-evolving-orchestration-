# TEO Specialist Roster

The specialist roster extends TEO with the full, battle-tested specialist specifications while preserving the core responsibility chain:

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

The specialists were created by **Sylvester Roxas** and integrated into TEO.

## Canonical preservation rule

Each specialist Markdown file is the canonical capability definition for that specialist. TEO does not summarize, narrow, demote, simplify, or rewrite the Legion role.

Each TEO role card therefore follows this order:

1. The complete specialist specification, unchanged.
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

The Description column reproduces each specialist Markdown file's `description:` frontmatter value verbatim.

| Specialist | Primary team | Worker binding | Supporting teams | Description |
|---|---|---|---|---|
| [Agents Orchestrator](agents-orchestrator.md) | Mission Control | `orchestration` | Planning Team, Engineering Team, Verification Team | Multi-agent pipeline architect and operator. Designs MCP servers, manages agent activation and handoff protocols, integrates LSP/code intelligence, and runs autonomous workflows end-to-end. |
| [Incident Commander](incident-commander.md) | Mission Control | `incident_response` | Engineering Team, Review Team, Verification Team | Incident response coordinator. Classifies severity, assigns roles, drives resolution cadence, and produces blameless post-mortems. Keeps the room calm and the timeline moving. |
| [Operations Manager](operations-manager.md) | Mission Control | `operations` | Planning Team, Review Team, Verification Team | Cross-functional operations lead covering HR onboarding, global recruitment (China + international), accounts payable, infrastructure maintenance, and business process optimization. |
| [Project Manager](project-manager.md) | Mission Control | `project_delivery` | Planning Team, Engineering Team, Verification Team | Orchestrates cross-functional projects from conception to completion. Covers delivery operations, Jira workflow governance, experiment tracking, and studio-level portfolio management. |
| [Architect](architect.md) | Planning Team | `architecture` | Engineering Team, Review Team | Designs maintainable, scalable systems — software architecture, backend systems, workflow design, Salesforce platform, and automation governance. Produces ADRs, C4 diagrams, and explicit trade-off analysis. |
| [Brand Designer](brand-designer.md) | Planning Team | `brand_design` | Research Team, Review Team | Brand foundation and visual identity specialist. Builds purpose-driven brand systems from values to visual language, voice, and cross-platform storytelling. Includes trademark guidance and micro-interaction whimsy. |
| [China Marketing Specialist](china-marketing-specialist.md) | Planning Team | `regional_marketing` | Research Team, Review Team | Full-stack China digital marketing across Douyin, Kuaishou, Weibo, Xiaohongshu, Bilibili, WeChat, Zhihu, Taobao, Tmall, JD, Pinduoduo, and WeCom. Covers private domain, livestream commerce, and ICP compliance. |
| [Civil Engineer](civil-engineer.md) | Planning Team | `civil_engineering` | Review Team, Verification Team | Structural and civil engineering specialist with global standards coverage — Eurocode, DIN, ACI, AISC, ASCE, AS-NZS, CSA, and GB. Handles structural design, load calculations, and civil infrastructure analysis. |
| [Corporate Trainer](corporate-trainer.md) | Planning Team | `learning_design` | Research Team, Verification Team | Corporate learning and development specialist covering training needs analysis, curriculum design, instructional design, LMS integration, and enterprise training program development. |
| [Cross-Border Ecommerce](cross-border-ecommerce.md) | Planning Team | `ecommerce_strategy` | Research Team, Review Team | Multi-platform cross-border e-commerce operations across Amazon, Shopee, Lazada, AliExpress, Temu, and TikTok Shop. Covers marketplace strategy, logistics, compliance, and pricing. |
| [Customer Success](customer-success.md) | Planning Team | `customer_success` | Research Team, Mission Control | Omnichannel customer support and success across general, healthcare, hospitality, retail, legal, and real-estate domains. Covers T1-T3 support, knowledge base management, and CSAT/NPS programs. Domain passed as context. |
| [Image Prompt Engineer](image-prompt-engineer.md) | Planning Team | `generative_media` | Research Team, Review Team | AI image and video prompt engineering specialist. Builds structured prompts for Midjourney, DALL-E, Stable Diffusion, Flux, Runway, and Sora using a 5-layer structure. Prevents representation bias. Maintains negative prompt libraries. 7-point QA before delivery. |
| [Paid Search Strategist](paid-search-strategist.md) | Planning Team | `paid_search` | Research Team, Verification Team | Google Ads, Microsoft Ads, and Amazon Ads architecture, bidding strategy, and account auditing. Covers search query analysis, negative keyword architecture, and budget pacing. |
| [Paid Social Strategist](paid-social-strategist.md) | Planning Team | `paid_social` | Research Team, Verification Team | Full-funnel paid social campaigns across Meta, LinkedIn, TikTok, Pinterest, X, and Snapchat. Covers creative strategy, testing frameworks, and Performance Max asset architecture. |
| [Product Manager](product-manager.md) | Planning Team | `product_strategy` | Research Team, Engineering Team, Review Team | Owns the full product lifecycle — discovery, strategy, roadmap, sprint planning, stakeholder alignment, and outcome measurement. Outcome-obsessed, user-grounded, diplomatically ruthless about focus. |
| [Programmatic Buyer](programmatic-buyer.md) | Planning Team | `programmatic_media` | Research Team, Verification Team | Programmatic display and video buying across DV360, The Trade Desk, and Amazon DSP. Covers ABM display, partner media buys, and full tracking architecture including GTM/GA4, Conversions API, Meta CAPI, and consent mode v2. |
| [Sales Coach](sales-coach.md) | Planning Team | `sales_enablement` | Research Team, Verification Team | Sales rep development, pipeline review facilitation, and discovery coaching. Covers Richardson framework, SPIN/MEDDPICC/Challenger methodologies, call structure, and forecast discipline. |
| [Sales Engineer](sales-engineer.md) | Planning Team | `solution_engineering` | Engineering Team, Research Team, Review Team | Technical discovery, impact-first demo engineering, POC scoping, competitive technical positioning, and solution architecture for sales evaluations. |
| [Sales Strategist](sales-strategist.md) | Planning Team | `sales_strategy` | Research Team, Review Team | Deal strategy, account expansion, outbound prospecting, and proposal writing. Covers MEDDPICC qualification, Challenger messaging, land-and-expand motions, signal-based prospecting, and RFP response. |
| [Social Media Strategist](social-media-strategist.md) | Planning Team | `social_strategy` | Research Team, Verification Team | Platform-native social strategy for TikTok, Instagram, Twitter/X, LinkedIn, Reddit, and YouTube. Platform passed as context. Excludes China platforms. |
| [Supply Chain Strategist](supply-chain-strategist.md) | Planning Team | `supply_chain` | Research Team, Review Team, Verification Team | End-to-end supply chain expert covering strategic sourcing, supplier development, procurement, logistics optimization, inventory management, and risk mitigation. |
| [AI Engineer](ai-engineer.md) | Engineering Team | `ai_engineering` | Planning Team, Review Team, Verification Team | Deploys and operates ML models, LLM pipelines, RAG systems, and voice/audio intelligence with mandatory bias testing. |
| [Backend Engineer](backend-engineer.md) | Engineering Team | `backend` | Planning Team, Review Team, Verification Team | Builds APIs, microservices, and server-side systems with a Laravel/Node primary stack and premium UI integration capability. |
| [Blockchain Engineer](blockchain-engineer.md) | Engineering Team | `blockchain` | Review Team, Verification Team | Solidity smart contract engineering with Foundry fuzz/invariant testing, OpenZeppelin-first patterns, proxy architectures, gas optimization, and Slither/Mythril security auditing. |
| [Data Engineer](data-engineer.md) | Engineering Team | `data_engineering` | Planning Team, Review Team, Verification Team | Designs and operates data pipelines, warehouses, and quality systems using Medallion Architecture. |
| [DevOps Engineer](devops-engineer.md) | Engineering Team | `devops` | Planning Team, Review Team, Verification Team | Owns infrastructure-as-code, CI/CD pipelines, observability, and deployment reliability. |
| [DevSecOps Engineer](devsecops-engineer.md) | Engineering Team | `devsecops` | Review Team, Verification Team | Secure CI/CD pipeline design, secrets management, supply chain security, SAST/DAST integration, and pipeline hardening. Bridges DevOps and security to build pipelines that enforce security gates without blocking delivery. |
| [Embedded Engineer](embedded-engineer.md) | Engineering Team | `embedded` | Planning Team, Review Team, Verification Team | Firmware and embedded systems engineering for ESP-IDF, STM32, Nordic nRF, Zephyr, and FreeRTOS — with strict ISR discipline, no post-init dynamic allocation, and hardware-level debugging. |
| [Frontend Engineer](frontend-engineer.md) | Engineering Team | `frontend` | Planning Team, Review Team, Verification Team | Builds accessible, performant user interfaces across web, mobile, and CMS platforms. |
| [Game Engineer](game-engineer.md) | Engineering Team | `game_engineering` | Planning Team, Review Team, Verification Team | Full-stack game development across Unity, Godot, Unreal, Roblox, and Blender — spanning design, engineering, art, audio, and multiplayer. Active engine is passed as context. |
| [Rust Engineer](rust-engineer.md) | Engineering Team | `systems_engineering` | Planning Team, Review Team, Verification Team | Rust systems engineering — ownership model, unsafe code, FFI, cross-compilation, embedded targets, async runtimes, and performance optimization. Covers the full Rust ecosystem from CLI tools to multi-platform C2 frameworks. |
| [Spatial Terminal](spatial-terminal.md) | Engineering Team | `terminal_ui` | Planning Team, Review Team, Verification Team | Terminal emulation and text rendering specialist for modern Swift applications. SwiftTerm integration, glyph rendering optimization, and spatial/visionOS terminal UI design. |
| [Workflow Optimizer](workflow-optimizer.md) | Engineering Team | `automation` | Planning Team, Verification Team | Process analysis and automation specialist. Identifies bottlenecks, quantifies waste, calculates ROI, and recommends the right tool — not the most expensive one. |
| [XR Developer](xr-developer.md) | Engineering Team | `xr_engineering` | Planning Team, Review Team, Verification Team | Extended reality engineering across visionOS/SwiftUI volumetric apps, WebXR browser-based AR/VR, XR interface design, macOS Metal spatial rendering, and Swift terminal integration. |
| [Content Creator](content-creator.md) | Research Team | `content` | Planning Team, Review Team | Multi-platform content creation across blog, book, podcast, short-video, YouTube, and social. Turns raw ideas, voice notes, and fragments into polished, published-ready content. |
| [Data Analyst](data-analyst.md) | Research Team | `analytics` | Planning Team, Verification Team | Transforms raw data into actionable business insights through statistical analysis, dashboards, KPI tracking, and predictive modeling. Covers analytics reporting, A/B testing, pipeline analysis, and model QA. |
| [Feedback Synthesizer](feedback-synthesizer.md) | Research Team | `user_research` | Planning Team, Review Team | Collects, analyzes, and synthesizes user feedback from multiple channels into actionable product insights. Transforms qualitative feedback into quantitative priorities. |
| [Finance Analyst](finance-analyst.md) | Research Team | `financial_analysis` | Planning Team, Review Team, Verification Team | Dual-role financial expert covering controller-level accounting and analyst-level modeling. Handles bookkeeping through GAAP-compliant close, FP&A, forecasting, and capital analysis. |
| [Market Analyst](market-analyst.md) | Research Team | `market_research` | Planning Team, Review Team | Market intelligence, competitive analysis, trend detection, and opportunity assessment. Turns signals into actionable strategic insights. |
| [OSINT Specialist](osint-specialist.md) | Research Team | `osint` | Review Team, Verification Team | Open-source intelligence gathering, passive reconnaissance, target profiling, social engineering recon, and source validation. Covers the full OSINT lifecycle from collection through analysis and reporting. |
| [Real Estate Agent](real-estate-agent.md) | Research Team | `real_estate` | Planning Team, Review Team | Full-service real estate agent covering buyer and seller representation, listing management, offer negotiation, market analysis, and transaction coordination. |
| [Researcher](researcher.md) | Research Team | `research` | Planning Team, Review Team, Verification Team | Domain-expert research and synthesis. Gathers, validates, and synthesizes information across any domain — history, science, culture, psychology, geography, market intelligence, investment, or any field passed as context. Replaces all 7 original academic/research specialists. |
| [Revenue Analyst](revenue-analyst.md) | Research Team | `revenue_analytics` | Planning Team, Verification Team | Pipeline velocity analysis, forecast accuracy, CRM data diagnostics, quota attainment analysis, and RevOps reporting. The analytical backbone of the revenue team. |
| [ZK Steward](zk-steward.md) | Research Team | `knowledge_management` | Planning Team, Review Team | Zettelkasten knowledge management specialist using the Luhmann method. Creates atomic notes, builds knowledge graphs, links concepts, and organizes domain-specific knowledge for long-term retrieval and insight generation. |
| [Code Reviewer](code-reviewer.md) | Review Team | `code_review` | Engineering Team, Verification Team | Reviews code with a 3-tier system, enforces minimal-change discipline, onboards to codebases read-only, and produces technical documentation. |
| [Compliance Auditor](compliance-auditor.md) | Review Team | `compliance` | Research Team, Verification Team | Compliance and governance specialist across SOC2, ISO 27001, HIPAA, PCI-DSS, GDPR, and CCPA. Governs automation decisions and agentic system trust. Generates privacy policies grounded in actual data practices. |
| [Legal Operations](legal-operations.md) | Review Team | `legal` | Research Team, Planning Team | Legal operations specialist covering billing, time tracking, client intake, contract review, litigation document review, and real estate agreement analysis. |
| [Loan Officer Assistant](loan-officer-assistant.md) | Review Team | `lending_compliance` | Research Team, Planning Team, Verification Team | Mortgage and lending operations assistant covering borrower intake, pre-qualification, loan documentation, and compliance tracking. |
| [Malware Analyst](malware-analyst.md) | Review Team | `malware_analysis` | Research Team, Engineering Team, Verification Team | Malware analysis, implant architecture review, AV/EDR evasion research, YARA rule development, and sandbox analysis. Covers static and dynamic analysis of malicious code, implant design patterns, and detection engineering for offensive tooling. |
| [Red Team Advisor](red-team-advisor.md) | Review Team | `security_advisory` | Planning Team, Engineering Team, Verification Team | Red team engagement planning, scoping, rules of engagement, campaign methodology, and reporting standards. Advises on adversary simulation strategy, MITRE ATT&CK alignment, and engagement governance. Does not execute operations — Gravity's domain. |
| [Security Engineer](security-engineer.md) | Review Team | `security` | Engineering Team, Research Team, Verification Team | Defensive and offensive security engineering — threat modeling, secure SDLC, SIEM detection, smart contract auditing, and zero-trust architecture. |
| [SEO Specialist](seo-specialist.md) | Review Team | `seo_review` | Research Team, Planning Team, Verification Team | Technical SEO, content SEO, Baidu ecosystem, and App Store Optimization (ASO). Covers crawlability, authority, content strategy, and mobile app discoverability. |
| [Tax Strategist](tax-strategist.md) | Review Team | `tax_review` | Research Team, Planning Team | Multi-jurisdictional tax expert covering optimization strategy, entity structuring, transfer pricing, IPO readiness, and IRS audit defense. Always quantifies the risk of uncertain positions. |
| [UX Designer](ux-designer.md) | Review Team | `ux_review` | Planning Team, Research Team, Engineering Team, Verification Team | UX research and design systems specialist. Mixed-methods research, information architecture, and CSS design systems with mandatory light/dark/system theme support. WCAG 2.1 AA minimum. Handoff-ready. |
| [QA Engineer](qa-engineer.md) | Verification Team | `qa` | Engineering Team, Review Team | Functional, API, accessibility, and performance testing specialist. Evidence-first mindset — defaults to finding issues, not confirming everything is fine. Realistic quality ratings only. |
| [Technical Writer](technical-writer.md) | Verification Team | `documentation_verification` | Research Team, Engineering Team, Review Team | Documentation specialist using the Divio system. Every doc type is kept pure — tutorials never mix with reference. Every code example runs. Docs ship in the same PR as the feature. |

## Machine-readable registry

The canonical TEO allocation and binding data is available in [`specialists.yaml`](specialists.yaml). It records routing metadata only. The linked specialist role cards remain the canonical capability specifications.

## Creator credit

Every specialist role card preserves the creator attribution:

> Creator: Sylvester Roxas  
This credit and the complete specialist specification must remain unless Sylvester Roxas explicitly requests otherwise.