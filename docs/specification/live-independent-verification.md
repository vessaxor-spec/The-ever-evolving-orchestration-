# Live Independent Verification

## Status

This specification defines the first executable independent-verification gate in the guarded TEO runtime.

The live gate is deliberately narrower than TEO's full verification architecture. It applies only to explicit `high_volume_simple` tasks at low or medium risk and executes exactly the verifier already assigned by the active dispatch.

The machine-readable policy is:

- `policy/runtime/live-verification.yaml`

The implementation research record is:

- `research/runtime/2026-08-07-live-independent-verification.md`

## Authority boundary

Routing remains responsible for selecting:

- execution provider and model
- reasoning effort
- fallback implementation
- verification methods
- verifier provider and model
- human-approval requirement

The live verification layer may execute that verifier. It may not replace it with a preferred judge, choose another provider, or waive human authority.

The verifier must be:

- a different model from the active executor
- from a different provider family from the active executor
- the verifier recorded in the active dispatch

If those conditions cannot be satisfied, verification fails closed.

## Guarded scope

Live model verification currently permits:

- task type `high_volume_simple`
- risk `low` or `medium`
- successful local text output artifacts only
- one verifier attempt
- structured pointwise decision output

It refuses:

- high or critical risk
- failed execution
- missing output artifacts
- non-local output references
- same-model verification
- same-provider verification
- unassigned verifier models
- verifier retry
- verifier fallback
- malformed structured verifier output

## Blinded verifier input

The verifier receives only information needed to judge the active result:

- original task
- candidate output
- declared verification methods
- fixed verification criteria

The verifier does not receive:

- executor provider
- executor model
- retry history
- fallback history
- circuit state
- runtime telemetry
- provider request IDs
- token usage
- cost

This reduces avoidable evaluator bias and keeps runtime recovery history separate from result quality.

## Fixed rubric

The guarded rubric contains four observable checks:

1. `output_present`
2. `task_adherence`
3. `format_consistency`
4. `unsupported_claims_absent`

Each check must return one of:

- `pass`
- `fail`
- `uncertain`

The verifier also returns one overall status:

- `passed`
- `failed`
- `needs_human`

### Passed

`passed` requires all four checks to be `pass` and `human_reason` to be `none`.

### Failed

`failed` requires at least one definitive `fail`, no `uncertain` result, and `human_reason` to be `none`.

### Needs human

`needs_human` requires at least one `uncertain` check, no definitive failed check, and one explicit reason:

- `insufficient_evidence`
- `ambiguous_task`
- `unverifiable_output`
- `conflicting_evidence`

The verifier must use uncertainty rather than inventing semantic ground truth that is absent from the task and candidate output.

## Structured output

All provider verifier adapters use constrained structured output.

The canonical decision schema is:

- `reference/schemas/live-verification-decision.schema.json`

The provider-neutral Python contract is:

- `teo_reference.verification_adapter.LiveVerificationDecision`
- `teo_reference.verification_adapter.LiveVerificationRequest`
- `teo_reference.verification_adapter.LiveVerificationResponse`

Current provider implementations are:

- `GoogleLiveVerifier`
- `AnthropicLiveVerifier`
- `OpenAILiveVerifier`

The connection mechanism remains behind `ProviderConnection` and is not part of verifier selection.

## Current canary verifier routes

The primary bounded route is:

```text
Claude Haiku 4.5 execution
  -> Gemini 3.6 Flash verification
```

When a model-specific failure moves execution to Gemini while Anthropic remains eligible:

```text
Gemini 3.6 Flash execution
  -> Claude Sonnet 5 verification
```

When an Anthropic provider failure blocks the provider family:

```text
Gemini 3.6 Flash execution
  -> GPT-5.6 Sol verification
```

The runtime does not choose these replacements. The routing layer re-evaluates verifier eligibility under the active task constraints.

## Verifier failure semantics

Verifier infrastructure failure is not a verification judgment.

Examples include:

- verifier connection unavailable
- verifier HTTP failure
- unsupported assigned verifier model
- malformed JSON decision
- provider-reported model substitution
- missing structured output

These conditions raise a live verification error and fail closed.

They must not be transformed into a synthetic `passed`, `failed`, or `needs_human` model verdict, because no valid verification judgment was obtained.

## Finalization

A valid live verifier decision is converted into the existing TEO `VerificationResult` contract.

The normal `finalize` gate remains authoritative:

- execution and verification must reference the same dispatch
- the verifier model must match the dispatch assignment
- independent verification cannot use the execution model
- failed verification prevents completion
- `needs_human` produces an awaiting-human state
- a dispatch requiring qualified human approval remains awaiting human even if model verification passes

Live verification therefore activates an existing gate rather than creating a parallel completion mechanism.

## Calibration boundary

A model judge is not treated as ground truth.

Before this mechanism expands beyond the guarded canary, TEO should create a human-rated calibration set and measure false-pass, false-fail, uncertainty, and agreement behavior for the rubric and verifier implementations.

Provider/model changes to the live verification default should be evidence-backed in the same way as execution routing changes.

## Non-goals

This slice does not implement:

- verifier retry
- verifier fallback
- multi-judge consensus
- pairwise model ranking
- semantic ground-truth generation
- broad domain verification
- high or critical risk live verification
- verification telemetry persistence
- automatic human-approval completion
- route learning from verifier judgments
