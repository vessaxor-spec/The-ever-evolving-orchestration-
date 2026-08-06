---
capsule_id: TEO-CAPSULE-0003
status: accepted
captured_at: 2026-08-06T06:55:00+02:00
snapshot_commit: ac15871037df63e1e69bfce80a0e9e549c43a292
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0002
immutability: accepted capsules are never rewritten
---

# Capsule 0003: Qualitative User Evidence Gets Its Own Route

This capsule records the state of **The Ever-Evolving Orchestration** after the dedicated `user_research` worker became part of the reference control plane.

It preserves the repository at commit [`ac15871037df63e1e69bfce80a0e9e549c43a292`](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/commit/ac15871037df63e1e69bfce80a0e9e549c43a292), captured on **6 August 2026 at 06:55 CEST**.

It references [TEO-CAPSULE-0002](0002-2026-08-05-specialist-freshness-architecture.md), whose next stated horizon was to bind the preserved `feedback-synthesizer` specialist into a dedicated worker without collapsing qualitative evidence into analytics, market intelligence, broad research, documentation, or UX review.

That horizon is now complete.

## Why this moment was preserved

TEO already had separate workers for:

- broad research
- market research
- quantitative analytics
- documentation

User evidence was still represented only by the specialist binding `feedback-synthesizer -> user_research`, which produced an explicit configuration warning because no core worker implemented that responsibility.

Without a dedicated worker, interview transcripts, survey responses, usability findings, support tickets, reviews, sentiment trajectories, persona evidence, and mixed-method synthesis could be routed through a neighboring responsibility merely because it was available.

That was structurally wrong.

Qualitative user evidence is not:

- market sizing or competitor intelligence
- statistical analysis or data-pipeline engineering
- final documentation ownership
- product decision authority
- UX design or accessibility judgment
- broad research with user terminology added afterward

The control plane now represents that distinction directly.

## Authoritative specialist preserved

The authoritative role remains:

```text
community/specialists/feedback-synthesizer.md
```

Its creator attribution, identity, responsibilities, methods, safety boundaries, collaboration rules, outputs, examples, and TEO allocation were not edited or compressed.

The new worker is an additive routing representation:

```text
community/workers/user-research-worker.yaml
```

## Worker responsibility

The `user_research` worker owns synthesis of ethically collected user evidence, including:

- research-question and protocol design
- feedback-source inventory
- interview-transcript synthesis
- survey-response synthesis
- usability-finding synthesis
- support-ticket and review synthesis
- atomic-observation extraction
- affinity mapping and theme development
- Jobs-to-be-Done framing
- sentiment and trajectory analysis
- persona and segment evidence
- qualitative and quantitative triangulation
- confidence, limitation, and decision briefing

The worker does not conduct live human interviews. It designs protocols and synthesizes provided or authorized evidence.

## Authority boundaries

The worker explicitly prohibits:

- live human interview execution
- product-decision substitution
- market-research ownership
- analytics-infrastructure ownership
- UX-design or accessibility-verdict substitution
- invented quotes, participants, or observations
- unsupported personas presented as fact
- overgeneralization from small or biased samples
- causal or statistical claims beyond the evidence
- re-identifiable or sensitive row-level evidence in outputs

These boundaries are part of the worker contract and are protected by conformance tests.

## First-class route

The reference control plane now includes the task type:

```text
user_research
```

The team route resolves to:

```text
Research Team -> user_research worker -> optional feedback-synthesizer specialist
```

Deterministic classification recognizes user-evidence tasks before broad research and other neighboring routes. Representative triggers include:

- user research
- feedback synthesis
- interview transcripts
- survey responses
- usability findings
- user pain points
- Voice of Customer
- affinity mapping
- Jobs-to-be-Done
- personas derived from feedback

Quantitative requests such as statistical significance or confidence-interval analysis remain on `analytics`. Market sizing and competitor positioning remain on `market_research`. General source investigation remains on `deep_research`.

## Provider-diverse implementation

The active implementation route at this moment is:

| Responsibility | Implementation | Provider |
|---|---|---|
| Primary qualitative synthesis | `claude-sonnet-5` | Anthropic |
| Routine fallback | `gemini-3.1-pro-preview` | Google |
| Independent verifier | `gpt-5.6-sol` | OpenAI |
| Quantitative verification support | `gpt-5.6-terra` | OpenAI |
| Conditional escalation | `claude-opus-5` | Anthropic |

The routine fallback crosses provider families. The verifier is independent from the primary. Opus remains outside ordinary fallback and is available only through evidence-based conditional escalation.

## Verification requirements

The worker requires evidence for:

- source and collection method
- sample and recruitment limitations
- trace from atomic observation to theme
- quote context and provenance
- contradiction and negative cases
- confidence and uncertainty
- quantitative corroboration where available
- consent, privacy, and re-identification risk
- independent insight review

Escalation is required when evidence involves vulnerable or protected populations, regulated or high-consequence use, unclear consent or authority, sensitive personal data, materially biased samples, unsupported personas, unresolved qualitative-quantitative conflict, or recommendations not supported by the evidence.

## Conformance state

The repository gained:

- `reference/datasets/user-research-worker-conformance.yaml`
- `tests/test_user_research_worker.py`
- provider-fallback coverage for `user_research`
- deterministic classification coverage
- exact boundary and provider-diversity assertions

The configuration warning baseline removed only `user_research`. Every other unresolved specialist binding remained visible.

The merge candidate passed the repository's complete CI pipeline:

- Python source compilation
- automated tests
- JSON-schema parsing
- linked configuration validation
- the end-to-end reference-router example

## Known limitations

At this moment:

- the worker synthesizes evidence but does not provide a live participant-recruitment or interview-execution runtime
- research consent, data retention, and jurisdictional requirements still require task-specific verification and qualified human ownership
- qualitative coding tools, repositories, and participant-management systems are not yet connected to provider adapters
- mixed-method execution remains external to the reference control plane; the router selects and records responsibility but does not call providers or analysis systems
- many other specialist worker bindings remain unresolved and visible in the exact warning baseline

## Next horizon

The next dedicated worker should be selected from the remaining warning baseline through responsibility uniqueness, routing frequency, risk, and verification value—not by arbitrary roster order.

The runtime horizon remains provider adapters, live execution, retry and circuit-breaking behavior, telemetry, cost and latency evidence, and enforcement that volatile claims are verified at task time.

## Message to future stewards

Do not route evidence by file format.

A spreadsheet of survey responses does not automatically make the task analytics. A transcript does not automatically make it broad research. A collection of complaints does not automatically make it product strategy.

Route by the responsibility required to interpret the evidence.

Preserve the distinction between:

- what users said
- what the evidence supports
- what remains uncertain
- what a decision-maker chooses to do

---

**A user voice becomes evidence only when its provenance, limits, contradictions, and implications remain visible.**
