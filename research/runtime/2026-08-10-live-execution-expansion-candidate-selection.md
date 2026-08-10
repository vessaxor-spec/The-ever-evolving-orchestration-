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

The executable router currently resolves a low-risk documentation probe to:

```text
Primary
  Anthropic / claude-sonnet-5 / medium

Initial fallback recorded on the dispatch
  Anthropic / claude-haiku-4-5

Primary verifier
  OpenAI / gpt-5.6-terra / medium
```

When the primary Sonnet implementation or Anthropic provider is blocked using the guarded runtime's existing redispatch transformation, the current router instead resolves:

```text
Failure redispatch executor
  Google / gemini-3.5-flash-lite

Failure redispatch verifier
  OpenAI / gpt-5.6-terra / medium
```

The repeated Terra verifier is not fresh relative to the primary dispatch verifier and therefore would fail the existing guarded runtime fallback integrity check.

The live-expansion work must not create a second documentation router to hide these facts.

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

Implication for TEO: the documentation route assigns `medium` reasoning effort. Any future live executor support for Sonnet 5 must carry that assignment into the provider request instead of silently using the provider default.

### OpenAI

OpenAI documents GPT-5.6 Sol and GPT-5.6 Terra as current API models. The current model guide states that GPT-5.6 supports `none`, `low`, `medium`, `high`, `xhigh`, and `max` reasoning effort, and the Terra model page lists the Responses API and structured outputs as supported.

Sources:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/guides/latest-model

Implication for TEO: Terra is provider-capability-valid for the primary documentation verifier, but the current guarded OpenAI verifier adapter does not yet include Terra in its supported model set.

### Google

Google documents `gemini-3.6-flash` and `gemini-3.5-flash-lite` as generally available. The existing TEO guarded Google executor already supports both of those stable models.

Sources:

- https://ai.google.dev/gemini-api/docs/latest-model
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash

Implication for TEO: the measured failure redispatch to Gemini 3.5 Flash-Lite is already within the current Google executor's model support, but that does not repair fallback-lineage or fresh-verifier requirements by itself.

## Executable preflight findings

The `live_scope_candidate` preflight uses the normal TEO router and the same redispatch constraint transformation as the guarded runtime. It performs no provider call.

The current candidate state is intentionally **not ready for activation**.

Passing findings:

- active live scope remains only `high_volume_simple`;
- candidate risk is limited to low and medium;
- documentation primary route resolves to Sonnet 5 at medium effort;
- primary verifier resolves to GPT-5.6 Terra at medium effort;
- model- and provider-failure redispatch both resolve to Gemini 3.5 Flash-Lite with Terra verification;
- Gemini 3.5 Flash-Lite already has guarded execution adapter support.

Open blockers:

1. the initial documentation dispatch records Claude Haiku 4.5 as fallback, which is the same provider family as the Sonnet 5 primary;
2. that recorded fallback does not match the executor selected by actual model/provider failure redispatch;
3. guarded Anthropic execution does not yet support Claude Sonnet 5;
4. Sonnet 5 medium effort is not yet propagated by the execution adapter;
5. guarded OpenAI verification does not yet support GPT-5.6 Terra;
6. failure redispatch reuses the primary dispatch's Terra verifier and therefore fails the guarded runtime's fresh-verifier rule;
7. no controlled documentation replay evidence exists;
8. no bounded shadow-evaluation record exists for documentation live replay;
9. rollback and recovery have not yet been proven for this task-class expansion.

## Runtime worker override finding

`community/workers/extensions/runtime-worker-overrides.yaml` is loaded as a worker-level override. Its policy text describes runtime-specific authorization for `high_volume_simple`, but it changes the shared `documentation` worker's `preferred_implementations` and `fallbacks` without a task-type condition.

That means the override affects ordinary `documentation` routing as well as `high_volume_simple` routing.

The observed consequences are:

- the initial documentation fallback is Claude Haiku 4.5, not the route-level Gemini 3.1 Pro Preview and not GPT-5.6 Sol;
- after Sonnet or Anthropic is blocked, preferred-implementation resolution selects Gemini 3.5 Flash-Lite;
- the fallback redispatch keeps GPT-5.6 Terra as verifier, which violates the guarded runtime's requirement for a verifier implementation fresh from the primary dispatch.

This is directly relevant to the expansion candidate. It is not being silently corrected in the candidate-selection slice because changing worker override semantics is a separate routing/control decision that requires its own verification.

## Preview boundary

The route-level documentation fallback remains Gemini 3.1 Pro Preview. It is ineligible unless the task explicitly accepts that preview model.

The candidate-selection work does not weaken this rule and does not add preview acceptance to the probe.

## Activation boundary

Before `documentation` can be added to active live scope, a later implementation must prove all of the following without changing task responsibility:

1. exact primary route remains intentional;
2. initial fallback and actual redispatch semantics are reconciled;
3. routine fallback is provider-diverse;
4. Sonnet 5 execution support preserves assigned medium effort;
5. Terra primary-verifier support is implemented;
6. failure redispatch receives a fresh provider-diverse verifier;
7. current retry, fallback, circuit, telemetry, Route-Outcome Evidence, and artifact-confinement semantics are preserved;
8. controlled live replay produces canonical evidence;
9. shadow evaluation finds no policy or control concern;
10. rollback and recovery behavior is reproducible;
11. low and medium risk only;
12. independent review approves the active-scope policy change.

Until those gates pass, `documentation` remains staged and `activation_authorized: false`.

## Adjacent finding

The Google Interactions API has evolved during 2026. Before any new Google execution behavior is added, the Google adapter surface should be rechecked against the then-current first-party Interactions API contract. This is adjacent to candidate selection and is not silently mixed into this staged-scope change.

## Conclusion

`documentation` remains the correct first candidate because it minimizes new task semantics while exposing the exact routing and runtime gaps that must be repaired before TEO widens live authority.

The appropriate next implementation gate is not activation. It is to reconcile the documentation worker override and fallback/fresh-verifier topology, then add missing Sonnet/Terra adapter support before controlled replay and shadow evaluation.
