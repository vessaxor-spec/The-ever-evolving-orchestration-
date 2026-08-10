# Live Execution Expansion Candidate Selection

**Date:** 2026-08-10  
**Status:** research  
**Authority:** non-normative  
**Repository baseline:** `93f8d7a77945819f6a5d0ac98ccfe3bf58ec0c66`

## Decision

Select `documentation` as the first task class to enter the evidence-governed live-execution expansion process.

This is a **staged candidate decision**, not live-execution authorization.

The active guarded runtime remains limited to `high_volume_simple` at low or medium effective risk. High and critical live execution remain unauthorized.

## Mission Control lenses

The selection was evaluated through:

- Mission Control for task authority and route preservation;
- Engineering for executable adapter and fallback feasibility;
- Assurance for side-effect, credential, preview, and human-authority boundaries;
- Verification for assigned-verifier and provider-diversity requirements;
- Review for route drift and hidden authority expansion;
- `orchestration-evaluation-analyst` for evidence sufficiency and promotion discipline.

## Candidate screening

### Selected: documentation

`documentation` is the smallest currently declared task class that can plausibly reuse the guarded text-execution architecture without requiring repository mutation, external research, multimodal payloads, financial authority, production operations, or tool execution as part of the task itself.

The canonical route currently resolves a low-risk documentation probe to:

```text
Primary
  Anthropic / claude-sonnet-5 / medium

Routine fallback recorded on initial dispatch
  OpenAI / gpt-5.6-sol

Primary verifier
  OpenAI / gpt-5.6-terra / medium
```

This preserves provider diversity between the primary executor and primary verifier. The current worker and routing configuration already define this responsibility and implementation topology. The live-expansion work must not create a separate documentation router.

### Not selected: daily_coding

The `daily_coding` worker requires coding, debugging, and tool execution. The current guarded provider executor is a bounded text-output path and does not provide the repository, shell, patch, test, or stateful tool-execution contract required to treat coding execution as equivalent to normal TEO engineering work.

Expanding coding first would therefore conflate model invocation with actual engineering execution.

### Not selected: deep_research, market_research, and user_research

These routes depend on source retrieval, current evidence, dataset or transcript provenance, privacy considerations, or other research-specific controls that the current bounded text executor does not itself provide.

Their current fallback topology also includes preview-model paths in places where explicit preview acceptance remains mandatory.

### Not selected: analytics

The analytics worker and route explicitly include reproducible calculation, SQL, Python, statistical validation, datasets, and executable checks when available. A text-only provider call is not a sufficient execution environment for the declared responsibility.

### Not selected: multimodal_analysis

The routed Gemini model is multimodal-capable, but the current TEO execution request and guarded adapter path used by the canary sends bounded text. Expanding the task class without adding a governed multimodal input and evidence contract would overstate runtime capability.

### Not selected: operations, project delivery, and incident response

These Mission Control classes can carry organizational commitments, approvals, infrastructure implications, incident authority, or other consequence-bearing actions. They are poor first expansion candidates while a lower-authority text-only class remains available.

## Current provider capability evidence

The candidate models remain current according to first-party provider documentation reviewed on 2026-08-10.

### Anthropic

Claude Sonnet 5 uses API model ID `claude-sonnet-5`. Anthropic documents the effort control for Sonnet 5, including `medium`, and shows `output_config={"effort": "medium"}` as the API mechanism.

Sources:

- https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5
- https://platform.claude.com/docs/en/build-with-claude/effort

Implication for TEO: the documentation route already assigns `medium` reasoning effort. Any future live executor support for Sonnet 5 must carry that assignment into the provider request instead of silently using the provider default.

### OpenAI

OpenAI documents GPT-5.6 Sol and GPT-5.6 Terra as current API models. The current model guide states that GPT-5.6 supports `none`, `low`, `medium`, `high`, `xhigh`, and `max` reasoning effort, and the Terra model page lists the Responses API and structured outputs as supported.

Sources:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/guides/latest-model

Implication for TEO: the canonical Sol fallback and Terra verifier are provider-capability-valid targets, but the current guarded execution/verifier adapters do not yet expose the exact support required by this candidate.

### Google

Google documents `gemini-3.6-flash` as generally available and supports structured outputs and thinking. It is therefore a capability-valid candidate for the fresh provider-diverse verifier needed after an OpenAI fallback execution, subject to TEO routing and verification policy explicitly assigning it.

Sources:

- https://ai.google.dev/gemini-api/docs/latest-model
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash

## Executable preflight findings

The new `live_scope_candidate` preflight uses the normal TEO router and the same redispatch constraint transformation as the guarded runtime. It performs no provider call.

The current candidate state is intentionally **not ready for activation**.

Passing gates:

- active live scope remains only `high_volume_simple`;
- candidate risk is limited to low and medium;
- canonical documentation primary route matches Sonnet 5 at medium effort;
- canonical initial routine fallback matches GPT-5.6 Sol;
- canonical primary verifier matches GPT-5.6 Terra at medium effort;
- the desired fresh fallback verifier, Gemini 3.6 Flash, already has a guarded verifier adapter.

Open blockers:

1. guarded Anthropic execution does not yet support Claude Sonnet 5;
2. Sonnet 5 medium effort is not yet propagated by the execution adapter;
3. guarded OpenAI execution does not yet support GPT-5.6 Sol;
4. guarded OpenAI verification does not yet support GPT-5.6 Terra;
5. model- and provider-failure redispatch cannot yet prove a fresh provider-diverse verifier for the Sol fallback under current canonical routing;
6. no controlled documentation replay evidence exists;
7. no bounded shadow-evaluation record exists for documentation live replay;
8. rollback and recovery have not yet been proven for this task-class expansion.

## Important fallback finding

The current documentation route names Gemini 3.1 Pro Preview as its route-level fallback, but preview models remain ineligible without explicit acceptance. Under the current worker fallback path, a normal low-risk documentation dispatch records GPT-5.6 Sol as its eligible routine fallback.

When the primary Sonnet route is blocked by a model- or provider-scoped failure, the redispatch can reach the OpenAI Sol executor, but current verifier resolution cannot yet guarantee the desired fresh Google Gemini 3.6 Flash verifier. The preflight therefore fails the fallback-redispatch gate.

This is a control finding, not permission to weaken preview acceptance or provider diversity.

## Activation boundary

Before `documentation` can be added to active live scope, a later implementation must prove all of the following without changing task responsibility:

1. exact primary route preserved;
2. exact routine fallback preserved;
3. Sonnet 5 execution support with assigned effort preserved;
4. Sol fallback execution support;
5. Terra primary-verifier support;
6. fresh provider-diverse fallback verifier resolved canonically;
7. current retry, fallback, circuit, telemetry, Route-Outcome Evidence, and artifact-confinement semantics preserved;
8. controlled live replay produces canonical evidence;
9. shadow evaluation finds no policy or control concern;
10. rollback and recovery behavior is reproducible;
11. low and medium risk only;
12. independent review approves the active-scope policy change.

Until those gates pass, `documentation` remains staged and `activation_authorized: false`.

## Adjacent finding

The Google Interactions API has evolved during 2026. Before any new Google execution behavior is added, the Google adapter surface should be rechecked against the then-current first-party Interactions API contract. This is adjacent to candidate selection and is not silently mixed into this staged-scope change.

## Conclusion

`documentation` is the correct first candidate because it minimizes new execution semantics while exposing the exact remaining control gaps that must be closed before TEO widens live authority.

The appropriate next step is not activation. It is to close the adapter and fallback-verifier gaps, then run controlled replay and shadow evaluation while the active live scope remains unchanged.
