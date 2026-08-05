---
capsule_id: TEO-CAPSULE-0001
status: accepted
captured_at: 2026-08-05T20:54:00+02:00
snapshot_commit: 1aec5f651e4b448b5cb2cf0d7e0b1e3d099ee938
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
immutability: accepted capsules are never rewritten
---

# Capsule 0001: The Reference Control Plane Exists

This capsule records the state of **The Ever-Evolving Orchestration** immediately before the capsule itself was added.

It preserves the repository at commit [`1aec5f651e4b448b5cb2cf0d7e0b1e3d099ee938`](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/commit/1aec5f651e4b448b5cb2cf0d7e0b1e3d099ee938), captured on **5 August 2026 at 20:54 CEST**.

This is not a changelog entry. It is a fixed historical record. Future corrections, reinterpretations, and advances must be written in a later capsule rather than applied here.

## Why this moment was preserved

TEO had crossed an important boundary.

It was no longer only a philosophy, architecture, specialist corpus, or routing proposal. It had become a runnable and testable reference control plane with machine-readable policies, deterministic dispatch, provider-aware fallback, independent verification, conformance fixtures, audit output, and continuous integration.

The project had also established a strict preservation rule: specialist capabilities could be allocated into TEO, but never compressed, generalized, weakened, or replaced by a generic agent abstraction.

## Enduring thesis

> **The model is not the architecture.**

At this point in the project, TEO was organized around several related beliefs:

- responsibilities endure longer than model versions
- capability requirements should be resolved before provider selection
- authority boundaries must precede autonomy
- consequential work requires independent verification
- implementation changes must remain visible through routing records and conformance updates
- fallback must account for the scope of failure, not merely select a different model name
- specialist depth must survive orchestration integration intact

## Project state

### Completed phases

The first five phases were considered complete:

1. **Repository credibility** — public identity, architecture, diagrams, foundational documents, and visible structure
2. **Core team completion** — Mission Control, Planning, Engineering, Research, Review, and Verification
3. **Routing validation** — representative task classes, explicit ambiguity handling, and verification-aware dispatch
4. **Registry population** — providers, models, stable capabilities, governance controls, and benchmark evidence structure
5. **Reference control plane** — runnable configuration loading, dispatch, fallback, verification, finalization, schemas, tests, and CI

### Organizational layers

The active architecture contained:

- Mission Control
- Planning Team
- Engineering Team
- Research Team
- Review Team
- Verification Team

A task moved through responsibility and authority before implementation selection:

```text
Task
  -> Risk
  -> Team
  -> Worker
  -> Optional Specialist
  -> Capability
  -> Primary implementation
  -> Routine fallback
  -> Conditional escalation
  -> Independent verification
  -> Evidence-bearing outcome
```

### Specialist corpus

The repository contained **56 public specialist role cards**, created by **Sylvester Roxas**.

Each role card preserved its complete identity, responsibilities, protocols, tools, outputs, collaboration rules, safety boundaries, examples, and TEO allocation. The specialist corpus was treated as authoritative. Core-worker representations were additive routing layers rather than replacements.

## Implemented dedicated workers

### Mission Control

- `orchestration`
- `operations`
- `project_delivery`
- `incident_response`

These represented distinct responsibilities rather than one generic coordinator.

### Research Team

- `research`
- `market_research`
- `analytics`
- `documentation`

The project explicitly separated:

- broad research from documentation
- market intelligence from broad-domain research
- quantitative analytics from research synthesis
- analytics from data-pipeline engineering

### Review Team

- `code_review`

Code review was moved out of the Planning Team's architecture worker and given its own Review Team ownership, specialist activation, risk elevation, and independent verification path.

## Implemented reference routes

The reference router contained first-class routes for:

- `orchestration`
- `operations`
- `project_delivery`
- `incident_response`
- `architecture_design`
- `daily_coding`
- `deep_debugging`
- `repo_wide_refactor`
- `deep_research`
- `market_research`
- `analytics`
- `code_review`
- `security_review`
- `multimodal_analysis`
- `high_volume_simple`
- `documentation`
- `release`

Classification was deterministic. Ambiguous tasks were required to provide an explicit `task_type` instead of allowing the router to invent responsibility.

## Provider-aware fallback policy

A major routing correction had just been completed.

TEO no longer treated any different model as an adequate fallback. It distinguished request-specific, transient, model-specific, provider-scoped, and capability-scoped failure.

The active policy was:

1. prefer a routine fallback from another provider family
2. block only the failed implementation after a model-specific failure
3. block the entire provider family after provider-scoped rate limits, quota exhaustion, authentication failure, billing failure, regional outage, or service outage
4. allow same-provider recovery only when the failure is demonstrably model-specific or no capable cross-provider candidate exists
5. exclude local models from automatic fallback chains
6. keep high-cost escalation capacity outside ordinary availability fallback
7. re-dispatch fallback execution with a newly selected independent verifier
8. reserve retries, backoff, jitter, retry budgets, and circuit breaking for future live adapters

At this moment, Claude Opus was intentionally used as the primary for `security_review` and as evidence-based conditional escalation. It was not part of ordinary worker or global fallback pools.

## Current implementation directions

The following were temporary bindings, not permanent declarations of model superiority:

- engineering execution primarily used Codex Terra
- difficult engineering reasoning primarily used Codex Sol
- broad research and market intelligence primarily used Gemini Pro
- multimodal and rapid collection primarily used Gemini Flash
- general planning and semantic review primarily used Claude Sonnet
- critical security reasoning primarily used Claude Opus
- independent verification was assigned separately according to route and risk

The architecture was intended to survive replacement of every implementation named above.

## Reference implementation

The Python reference router could:

- load linked YAML policy and registry files
- validate team, worker, specialist, route, and implementation references
- classify tasks deterministically
- assess and elevate risk
- select teams, workers, specialists, primary implementations, fallbacks, and verifiers
- produce structured dispatch records
- finalize externally executed and independently verified results
- write audit records
- emit `completed`, `failed`, `escalated`, or `awaiting_human` outcomes

It deliberately did **not** call provider APIs.

The repository CI compiled the Python sources, ran the full test suite, parsed JSON schemas, validated linked configuration, and executed the end-to-end example.

## Conformance discipline

Silent routing drift was treated as a defect.

The repository contained conformance coverage for:

- general routing behavior
- risk-based verification
- Mission Control worker bindings
- Mission Control route behavior
- incident response boundaries
- code-review ownership
- broad research boundaries
- market-research boundaries
- analytics boundaries
- provider-aware fallback
- exact configuration-warning baselines

Intentional behavior changes were expected to update the corresponding fixture and explain the policy reason.

## Unresolved worker bindings

Forty specialist worker bindings still had no dedicated core-worker definition:

```text
automation
blockchain
brand_design
civil_engineering
compliance
content
customer_success
devsecops
documentation_verification
ecommerce_strategy
embedded
financial_analysis
game_engineering
generative_media
knowledge_management
learning_design
legal
lending_compliance
malware_analysis
osint
paid_search
paid_social
product_strategy
programmatic_media
real_estate
regional_marketing
revenue_analytics
sales_enablement
sales_strategy
security_advisory
seo_review
social_strategy
solution_engineering
supply_chain
systems_engineering
tax_review
terminal_ui
user_research
ux_review
xr_engineering
```

These warnings were explicit and CI-controlled. They were not permission to silently route the specialists through weaker generic workers.

## Known limitations

At this moment:

- provider adapters were not implemented
- live provider authentication and credentials were outside the reference boundary
- fallback execution was represented by re-dispatch rather than live automatic execution
- retries, circuit breakers, streaming, and runtime telemetry were not implemented
- no controlled common harness had produced cross-model quality, cost, and latency measurements
- many specialist worker bindings remained unresolved
- no open-source license had been selected
- route quality was supported by configuration and conformance evidence, not yet by large-scale production telemetry

## Immediate next horizon

The next planned addition was the dedicated `user_research` worker derived from the existing `feedback-synthesizer` specialist.

Its purpose was to keep qualitative user evidence separate from:

- quantitative analytics
- market intelligence
- broad research synthesis

The same preservation rule would apply: the specialist specification would remain authoritative and intact, while TEO allocation would add only worker, routing, fallback, verification, and authority context.

## Message to future stewards

Do not mistake the current implementation map for the constitution.

Models will change. Provider limits will change. Benchmarks will change. The names recorded in this capsule may become obsolete quickly.

Preserve the responsibility chain.

Preserve specialist depth.

When evidence changes, update the registry, route, and conformance record. Do not rewrite history to make the past look cleaner than it was.

The system became credible when it could expose its own gaps without weakening the roles it had not yet implemented.

---

**Recorded under the stewardship of Sylvester Roxas.**

**The signal persists.**
