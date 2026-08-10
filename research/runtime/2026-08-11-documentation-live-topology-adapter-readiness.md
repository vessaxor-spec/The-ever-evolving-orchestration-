# Documentation Live Topology and Adapter Readiness

**Date:** 2026-08-11  
**Status:** research  
**Authority:** non-normative  
**Repository baseline:** `ca9c81f0e0228a7c510bbc39ec20a24d2eefe4f1`

## Decision

Repair the staged `documentation` candidate by restoring the canonical documentation worker's general-purpose model ordering, adding a provider-diverse fresh-verifier recovery path for canonical documentation redispatch, and implementing the exact provider adapter capabilities required by the resulting route.

This is an adapter-readiness and routing-integrity milestone. It does **not** authorize `documentation` live execution.

The active guarded runtime remains limited to `high_volume_simple` at low or medium effective risk. High and critical live execution remain unauthorized.

## Mission Control lenses

- Mission Control for scope and authority boundaries;
- Engineering for routing and adapter implementation;
- Assurance for preview, credential, side-effect, and human-authority controls;
- Review for hidden route drift and scope expansion;
- Verification for provider diversity, fresh-verifier behavior, and structured evidence;
- `orchestration-evaluation-analyst` for evidence sufficiency and promotion discipline.

## Root cause

`community/workers/extensions/runtime-worker-overrides.yaml` described itself as runtime-specific, but `ConfigBundle._load_workers()` applies `worker_overrides` directly to the shared worker registry with no task-type condition.

The former override therefore changed the `documentation` worker for every task using that worker. It caused ordinary documentation dispatches to record Claude Haiku 4.5 as the initial fallback and caused model/provider failure redispatch to enter the throughput-oriented worker ordering.

The repair removes that unconditional worker mutation rather than adding another route-specific bypass.

`high_volume_simple` does not require the global worker override. Its primary, fallback, alternatives, and verifier topology are already declared explicitly in `policy/routing/core/routing.yaml`, and every required model is already present in the canonical documentation worker's model set.

## Repaired canonical topology

Without explicit preview acceptance, the staged documentation probe resolves to:

```text
Primary executor
  Anthropic / claude-sonnet-5 / medium

Initial routine fallback
  OpenAI / gpt-5.6-sol

Primary verifier
  OpenAI / gpt-5.6-terra / medium
```

The route-level Gemini 3.1 Pro Preview fallback remains blocked unless that exact preview model is explicitly accepted.

When Sonnet 5 or the Anthropic provider is blocked through the guarded runtime's canonical redispatch constraint transformation, the route resolves to:

```text
Recovery executor
  OpenAI / gpt-5.6-sol

Fresh recovery verifier
  Google / gemini-3.6-flash / medium
```

The recovery verifier is selected from the canonical documentation worker model pool only when the base verifier route cannot preserve provider diversity after redispatch. The recovery path does not select the executor, lower risk, accept preview models, or alter human-approval requirements.

## Adapter readiness is not execution authority

The reference adapters now distinguish implemented model capability from active live authorization.

### Anthropic execution

The Anthropic Messages adapter implements Claude Sonnet 5 for low or medium risk bounded text execution. Sonnet 5 requires an explicit supported TEO effort and carries the assigned effort through Anthropic `output_config.effort`.

The active Anthropic canary wrapper remains restricted to `high_volume_simple` and Claude Haiku 4.5. Adding Sonnet 5 implementation support does not authorize documentation execution.

Authoritative provider evidence reviewed for this change:

- https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5
- https://platform.claude.com/docs/en/build-with-claude/effort

### OpenAI execution

The OpenAI Responses adapter implements GPT-5.6 Sol while preserving the existing reasoning-effort request contract.

The active OpenAI canary wrapper remains restricted to `high_volume_simple` and GPT-5.6 Luna. Adding Sol implementation support does not authorize documentation execution.

Authoritative provider evidence reviewed for this change:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/docs/guides/latest-model

### OpenAI verification

The guarded OpenAI verifier implements GPT-5.6 Terra using the existing Responses API structured-output verification contract and assigned reasoning effort.

Live verification remains constrained by `policy/runtime/live-verification.yaml`. Adding Terra to verifier implementation support does not widen the live verification task scope.

Authoritative provider evidence reviewed for this change:

- https://developers.openai.com/api/docs/models/gpt-5.6-terra
- https://developers.openai.com/api/docs/guides/latest-model

### Google recovery verification

Gemini 3.6 Flash is already implemented by the guarded Google verifier and supports the medium effort assigned by the repaired documentation recovery topology.

Authoritative provider evidence reviewed for this change:

- https://ai.google.dev/gemini-api/docs/latest-model
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash

## Preserved controls

This milestone preserves:

- active live scope limited to `high_volume_simple`;
- low and medium risk only for the current guarded runtime;
- explicit preview-model acceptance;
- provider access and authentication outside routing;
- provider-diverse initial fallback for the staged documentation candidate;
- fresh provider-diverse verification after documentation redispatch;
- one assigned live verifier with no verifier retry or fallback;
- existing qualified-human approval semantics;
- retry, circuit-state, telemetry, and Route-Outcome Evidence authority boundaries;
- no direct policy-write or live-scope authority from candidate evaluation.

## Remaining gates

After this topology and adapter-readiness milestone is validated, `documentation` still cannot be activated until later evidence proves:

1. controlled live replay for the exact staged topology;
2. canonical Route-Outcome Evidence for those replay runs;
3. governed Shadow Route Evaluation of the replay evidence;
4. rollback and recovery behavior under the candidate scope;
5. independent review of the eventual active-scope policy change.

## Conclusion

The correct repair is to remove the unintended global worker mutation, preserve the canonical documentation route, and make the exact staged models executable or verifiable at the adapter layer without granting them live authority.

Controlled replay is the next evidence gate only after CI validates this topology and adapter-readiness slice.
