# TEO model-routing audit - 2026-08-07

## Purpose

This audit refreshes TEO model-routing evidence against current provider documentation and recent practitioner experience. It covers the model families explicitly used by TEO:

- OpenAI / Codex: GPT-5.6 Sol, Terra, Luna
- Anthropic / Claude: Opus 5, Sonnet 5, Haiku 4.5
- Google / Gemini / Antigravity: Gemini 3.1 Pro Preview, Gemini 3.6 Flash

The goal is not to rank providers globally. The goal is to route each work shape to an implementation whose capability, effort controls, cost, latency, tools, and failure characteristics fit the job, while preserving cross-provider fallback and independent verification.

Community reports are treated as directional evidence only. They do not override provider documentation, TEO conformance results, or workload-specific evaluation.

## Current verified model inventory

| Provider | Model | Current role | Reasoning / thinking control | Context | Output | Current list price, input / output MTok |
|---|---|---|---|---:|---:|---:|
| OpenAI | `gpt-5.6-sol` | frontier complex professional work | `none`, `low`, `medium`, `high`, `xhigh`, `max`; optional Pro mode | 1.05M | 128K | $5 / $30 |
| OpenAI | `gpt-5.6-terra` | balance of intelligence and cost | `none`, `low`, `medium`, `high`, `xhigh`, `max` | 1.05M | 128K | $2.50 / $15 |
| OpenAI | `gpt-5.6-luna` | cost-sensitive high-volume work | `none`, `low`, `medium`, `high`, `xhigh`, `max` | 1.05M | 128K | $1 / $6 |
| Anthropic | `claude-opus-5` | complex agentic coding, enterprise work, deep reasoning | adaptive thinking, effort `low`, `medium`, `high`, `xhigh`, `max` | 1M | 128K | $5 / $25 |
| Anthropic | `claude-sonnet-5` | speed-intelligence balance, coding and agents | adaptive thinking, effort `low`, `medium`, `high`, `xhigh`, `max` | 1M | 128K | $2 / $10 through 2026-08-31, then $3 / $15 |
| Anthropic | `claude-haiku-4-5` | fastest economical Claude tier | extended thinking available; no adaptive-thinking effort ladder | 200K | 64K | $1 / $5 |
| Google | `gemini-3.1-pro-preview` | complex problem solving, grounded synthesis, software engineering, agentic work | `low`, `medium`, `high`; default `high` | 1.048M | 65,536 | $2 / $12 |
| Google | `gemini-3.6-flash` | fast agentic, coding, multimodal and spatial work | `minimal`, `low`, `medium`, `high`; default `medium` | 1.048M | 65,536 | $1.50 / $7.50 |

### Version conclusions

- GPT-5.6 Sol, Terra and Luna are the current OpenAI family relevant to the TEO Codex routes.
- Claude Opus 5 and Sonnet 5 are current. Haiku remains at 4.5.
- Gemini 3.1 Pro Preview is the current Pro route. The older Gemini 3 Pro Preview was shut down on 2026-03-09.
- Gemini 3.6 Flash is the current stable Flash route and became the default model for Google's managed Antigravity agent in July 2026.
- Gemini Pro remains preview software, so its preview status must remain visible and it should not become the sole authority for a critical decision.

## What changed relative to TEO's earlier assumptions

### 1. Reasoning effort is now architecture-relevant

TEO already stored labels such as `reasoning: high`, but the Python dispatch did not preserve them. That is no longer sufficient.

OpenAI, Anthropic and Google now all expose meaningful effort or thinking controls. A model identifier alone does not fully describe the chosen execution profile.

Recommended default principle:

> Select model family first, then select the lowest effort level that has demonstrated acceptable quality for the workload and risk.

Do not assume that maximum effort is automatically the best operational choice.

### 2. Claude Opus 5 is under-used in the current policy

Anthropic positions Opus 5 for complex agentic coding, large-scale refactoring, complex systems engineering, advanced research, long-horizon work and nuanced enterprise reasoning. Its effort ladder now allows Opus to be used at lower effort when full depth is unnecessary and raised to `xhigh` or `max` only where justified.

TEO therefore should not reserve Opus almost exclusively for security and generic escalation.

Opus 5 is now a deliberate primary for specialist work dominated by:

- safety or regulatory interpretation
- cross-system architectural tradeoffs
- difficult formal reasoning
- critical incident command and decision framing
- high-consequence financial, legal, privacy or lending analysis
- hardware, aerospace, robotics, silicon and civil reasoning where multiple constraints and failure modes interact

Human approval and independent verification remain mandatory where risk requires them. A stronger model does not replace accountable authority.

### 3. Sonnet 5 remains the semantic and general agentic workhorse

Sonnet 5 is a strong default where the task needs synthesis, planning, review, communication quality and tool use but does not justify Opus cost or latency. Its adaptive thinking is on by default and effort should normally start at `medium` or `high` depending on consequence.

### 4. Sol should own deep executable engineering, not every coding task

OpenAI recommends Sol for frontier complex reasoning and coding, Terra for the intelligence-cost balance and Luna for high-volume economical work.

Recent practitioner reports broadly support:

- Terra Medium as a strong daily coding baseline
- Sol Medium or High when architecture, migration, authentication, payments, difficult debugging or cross-repository consistency dominate
- Sol `xhigh` or `max` only when additional reasoning produces a measurable quality gain
- Luna at moderate or higher effort for tightly scoped, testable work rather than ambiguous repository-wide work

TEO therefore separates deep engineering reasoning from routine engineering execution.

### 5. Gemini Pro and Flash should not be treated as the same Google route

Gemini 3.1 Pro Preview is optimized for complex reasoning, software engineering, grounded synthesis and agentic tool use. Google provides a separate `customtools` endpoint for workflows centered on bash and custom tools.

Gemini 3.6 Flash is stable and optimized for speed, agentic loops, code generation, computer use, spatial reasoning and multimodal work. Google reports fewer loops, fewer unwanted edits and fewer tool calls than 3.5 Flash.

Community experience is mixed on using Flash for large ambiguous codebases. Positive reports consistently emphasize speed and bounded daily work; negative reports emphasize hallucination, over-engineering or instruction drift on large or poorly scoped coding tasks. TEO therefore uses Flash for bounded agentic and multimodal work, not as the primary deep-systems reasoner.

## Provider-native effort guidance

### GPT-5.6

- `none` or `low`: latency-sensitive deterministic or simple work
- `medium`: balanced default for routine production work
- `high`: complex reasoning or engineering where measured quality improves
- `xhigh`: high-consequence or difficult cross-component work
- `max`: exceptional quality-first work only
- Pro mode: conditional quality-first execution where clear evaluation criteria justify additional model work

### Claude Opus 5 and Sonnet 5

- `low`: simple subagent or speed-sensitive work
- `medium`: balanced agentic work
- `high`: default for complex reasoning and difficult coding
- `xhigh`: demanding long-horizon coding and agentic work
- `max`: deepest reasoning where unconstrained token spending is justified

Opus 5 defaults to `high`. Anthropic specifically recommends stepping to `xhigh` for demanding coding and agentic work and reserving `max` for the strongest capability requirement.

### Claude Haiku 4.5

Haiku 4.5 does not use the modern adaptive-thinking effort ladder. Use it as an economical language and retrieval worker, especially when the answer is mostly contained in retrieved context and the task has strong structure or skills. Escalate synthesis and ambiguity rather than forcing Haiku to become a deep reasoner.

### Gemini 3.1 Pro Preview

- `low`: reduced latency where full reasoning is unnecessary
- `medium`: balanced complex work
- `high`: default and preferred for deep research, complex reasoning and difficult agentic work

### Gemini 3.6 Flash

- `minimal`: simple extraction and throughput
- `low`: latency-sensitive bounded work
- `medium`: default workhorse setting
- `high`: harder bounded coding, multimodal or agentic loops where additional reasoning is useful

## TEO specialist route families

The full specialist allocation is stored in `policy/routing/specialist-model-routing.yaml`. Team and worker selection still happen first.

### Opus critical reasoning

Primary: Claude Opus 5, normally `high`, rising to `xhigh` for critical risk.

Routine fallback: GPT-5.6 Sol, `high` or `xhigh`.

Independent verifier: Gemini 3.1 Pro Preview, `high`.

Specialists:

- Architect
- Civil Engineer
- Compliance Auditor
- Finance Analyst
- Incident Commander
- Legal Operations
- Loan Officer Assistant
- Red Team Advisor
- Security Engineer
- Tax Strategist
- Cloud Architect
- Database Reliability Engineer
- Systems Requirements Engineer
- Hardware Engineer
- Robotics / Autonomous Systems Engineer
- Silicon / ASIC Engineer
- Aerospace / Satellite Engineer
- Privacy Engineer
- Functional Safety Engineer
- Formal Methods Engineer

Conditional effort escalation: Opus 5 `max` only for unresolved material disagreement, critical cross-system ambiguity, or a decision-relevant measured quality gain.

### Sol deep engineering

Primary: GPT-5.6 Sol, `high`, rising to `xhigh` for high and critical specialist work.

Routine fallback: Claude Sonnet 5, `high` or `xhigh`.

Independent verifier: Gemini 3.1 Pro Preview, `high`.

Specialists:

- Agents Orchestrator
- AI Engineer
- Blockchain Engineer
- Code Reviewer
- Data Analyst
- Data Engineer
- DevOps Engineer
- DevSecOps Engineer
- Embedded Engineer
- Malware Analyst
- Revenue Analyst
- Rust Engineer
- Compiler / Toolchain Engineer
- Distributed Systems Engineer
- Network Engineer
- Platform Engineer
- Performance Engineer
- FinOps Engineer
- Site Reliability Engineer
- MLOps Engineer
- Application Security Engineer

Conditional effort escalation: Sol `max` or Pro mode only after repeated execution/reasoning failure, high-value evaluable code/review work, or unresolved cross-repository invariants.

### Terra engineering execution

Primary: GPT-5.6 Terra, `medium` for routine work and `high` for higher-risk execution.

Routine fallback: Gemini 3.6 Flash, `medium` or `high`.

Independent verifier: Claude Sonnet 5, `medium` or `high`.

Specialists:

- Backend Engineer
- Frontend Engineer
- Game Engineer
- QA Engineer
- Spatial Terminal
- Workflow Optimizer
- XR Developer
- Mobile Engineer
- Manufacturing Engineer

Conditional escalation: GPT-5.6 Sol when the task becomes cross-component, architecture-heavy, migration-heavy or repeatedly fails implementation.

### Gemini research

Primary: Gemini 3.1 Pro Preview, normally `high`.

Routine fallback: Claude Sonnet 5, `high`.

Independent verifier: GPT-5.6 Sol, `high` or `xhigh` for consequential work.

Specialists:

- China Marketing Specialist
- Cross-Border Ecommerce
- Market Analyst
- OSINT Specialist
- Paid Search Strategist
- Paid Social Strategist
- Programmatic Buyer
- Real Estate Agent
- Researcher
- SEO Specialist
- Social Media Strategist
- Supply Chain Strategist
- Applied Scientist

Conditional escalation: Claude Opus 5 when authorities or sources materially disagree, the decision is high-consequence, or ambiguity remains after verification.

### Sonnet semantic and planning

Primary: Claude Sonnet 5, `medium` or `high`.

Routine fallback: GPT-5.6 Sol, `medium` or `high`.

Independent verifier: Gemini 3.1 Pro Preview, `high` for consequential work.

Specialists:

- Brand Designer
- Content Creator
- Corporate Trainer
- Customer Success
- Feedback Synthesizer
- Operations Manager
- Product Manager
- Project Manager
- Sales Coach
- Sales Engineer
- Sales Strategist
- Technical Writer
- UX Designer

Conditional escalation: Claude Opus 5 for high-consequence strategy, material ambiguity or disagreement, or long-horizon agentic planning.

### Gemini Flash multimodal

Primary: Gemini 3.6 Flash, normally `medium`, rising to `high` for difficult multimodal work.

Routine fallback: GPT-5.6 Terra.

Independent verifier: Claude Sonnet 5.

Specialist:

- Image Prompt Engineer

Conditional escalation: Gemini 3.1 Pro Preview for ambiguous cross-modal or long-context synthesis.

### Luna throughput

Primary: GPT-5.6 Luna, `low` or `medium` for bounded throughput work.

Routine fallback: Claude Haiku 4.5.

Independent verifier: Gemini 3.6 Flash.

Specialist:

- ZK Steward

This is also the generic pattern for tightly scoped extraction, classification, normalization and transformation subtasks that do not require a stronger specialist default.

## Fallback rules

Fallback is capability-preserving recovery, not a model ranking.

1. Routine fallback should cross provider families whenever an eligible alternative exists.
2. A model-specific failure blocks the model first, not necessarily the entire provider.
3. Provider-scoped failures block the provider family.
4. Fallback redispatch must receive a new independent verifier when the existing verifier would no longer be independent.
5. Claude Opus 5 is not a generic routine fallback. It is a primary or conditional escalation where its depth is justified.
6. Gemini 3.1 Pro Preview must expose preview status. Critical outcomes still require the normal TEO human and verification controls.
7. Luna, Haiku and Flash should not inherit ambiguous or consequential work merely because they are cheaper or faster.
8. Sol, Opus and maximum effort should not be used where a cheaper route has demonstrated equivalent quality.

## Community and independent evidence summary

Recent practitioner discussion is useful but inconsistent. The durable signals are:

- Codex users repeatedly describe Terra as a strong everyday coding tier and Sol as the route for complex architecture, debugging, migrations and cross-repository work. Luna performs well on well-scoped, verifiable tasks but can miss hidden repository invariants.
- Claude users generally position Haiku for search, read, classify and cheap subagent work, Sonnet for routine agentic coding and synthesis, and Opus for planning, difficult coding, complex reasoning and final challenge. Opus 5 reports are mixed on verbosity and workflow migration, reinforcing the need for TEO-specific evals rather than blanket promotion.
- Gemini 3.6 Flash receives strong reports for speed, daily agentic work and fewer loops, but there are also credible reports of hallucination or poor behavior on large ambiguous coding tasks. This supports bounded Flash use with independent verification.
- Harness design matters. Multiple reports across providers note that tool contracts, skills, context management and edit safeguards materially change model quality. TEO should evaluate model plus harness, not model name in isolation.

## Sources checked

### Primary provider documentation

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://developers.openai.com/api/docs/guides/latest-model
- https://openai.com/index/gpt-5-6/
- https://platform.claude.com/docs/en/about-claude/models/overview
- https://platform.claude.com/docs/en/about-claude/models/choosing-a-model
- https://platform.claude.com/docs/en/build-with-claude/effort
- https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking
- https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5
- https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash
- https://ai.google.dev/gemini-api/docs/thinking
- https://ai.google.dev/gemini-api/docs/pricing
- https://ai.google.dev/gemini-api/docs/latest-model

### Independent and community signals

- Artificial Analysis model pages for GPT-5.6 Sol and Gemini 3.1 Pro Preview
- Reddit r/codex discussions on Sol / Terra / Luna production use and effort selection
- Reddit r/ClaudeAI and r/ClaudeCode Opus 5, Sonnet 5 and Haiku 4.5 workflow reports
- Reddit r/google_antigravity and r/GeminiAI Gemini 3.6 Flash and Gemini 3.1 Pro workflow reports

These secondary sources are supporting evidence only. TEO's own conformance and workload evaluations remain the acceptance authority.

## Acceptance requirements

Before this routing policy is considered proven rather than evidence-informed:

- dispatch must preserve selected reasoning effort
- all 78 specialists must resolve to exactly one model-routing template
- each template must have a cross-provider routine fallback
- each template must have an independent verifier
- no specialist route may change team or worker authority
- critical specialists must retain qualified-human approval
- existing specialist role cards must remain byte-for-byte unchanged
- existing regulated-evidence and mutation controls must remain green
- model and effort changes must be measurable through future runtime telemetry and workload-specific evals
