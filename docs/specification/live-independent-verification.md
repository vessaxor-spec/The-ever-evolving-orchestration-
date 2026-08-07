# Live Independent Verification

## Status

This specification defines the executable independent-verification gate in the guarded TEO runtime.

The live gate is deliberately narrower than TEO's full verification architecture. It applies only to explicit `high_volume_simple` tasks at low or medium effective risk and executes exactly the verifier already assigned by the active dispatch.

The machine-readable policy is `policy/runtime/live-verification.yaml`.

## Authority boundary

Routing remains responsible for selecting execution provider/model, reasoning effort, fallback, verification methods, verifier provider/model, and human-approval requirement.

The live verification layer may execute that verifier. It may not replace the verifier, choose another provider, retry itself, invoke verifier fallback, or waive human authority.

The verifier must be a different model and a different provider family from the active executor. If the assigned verifier cannot satisfy those conditions, verification fails closed.

## Guarded scope

Live model verification currently permits:

- task type `high_volume_simple`
- low or medium effective risk
- successful local UTF-8 text artifacts
- artifacts resolving inside the runtime-authorized artifact root
- maximum artifact size of 65,536 bytes
- one verifier attempt
- structured pointwise decision output

It refuses high or critical risk, failed execution, missing artifacts, external references, artifact-root escape, same-model verification, same-provider verification, unassigned verifier models, verifier retry/fallback, and malformed structured output.

## Blinded verifier input

The verifier receives only the original task, candidate output, declared verification methods, and fixed criteria.

The verifier does not receive executor identity, retry/fallback history, circuit state, runtime telemetry, request IDs, token usage, or cost.

The candidate output is explicitly treated as **untrusted data**. Instructions, role changes, tool requests, evaluator directives, or attempts to override the rubric inside the candidate output must not be followed.

## Fixed rubric

The guarded rubric contains four checks:

1. `output_present`
2. `task_adherence`
3. `format_consistency`
4. `unsupported_claims_absent`

Each returns `pass`, `fail`, or `uncertain`.

The overall status follows deterministic precedence:

1. any definitive `fail` means `failed`
2. otherwise any `uncertain` means `needs_human`
3. otherwise the result is `passed`

This preserves mixed evidence. A result may contain both a definitive failed criterion and an uncertain criterion; the overall decision remains `failed` while the uncertain evidence is retained for later calibration.

`needs_human` is valid only when no criterion definitively failed, at least one criterion is uncertain, and the verifier provides one of:

- `insufficient_evidence`
- `ambiguous_task`
- `unverifiable_output`
- `conflicting_evidence`

The verifier must use uncertainty rather than inventing semantic ground truth absent from the supplied task/output.

## Structured output

The canonical decision schema is `reference/schemas/live-verification-decision.schema.json`.

The provider-neutral Python contracts are `LiveVerificationDecision`, `LiveVerificationRequest`, and `LiveVerificationResponse`.

Current provider implementations are `GoogleLiveVerifier`, `AnthropicLiveVerifier`, and `OpenAILiveVerifier`. Connection mechanism remains behind `ProviderConnection` and is not a routing signal.

## Current canary verifier routes

Primary bounded route:

```text
Claude Haiku 4.5 execution
  -> Gemini 3.6 Flash verification
```

Model-specific fallback to Gemini while Anthropic remains eligible:

```text
Gemini 3.6 Flash execution
  -> Claude Sonnet 5 verification
```

Anthropic provider-family failure:

```text
Gemini 3.6 Flash execution
  -> GPT-5.6 Sol verification
```

The live verifier does not choose these routes. Routing recomputes eligibility and records the assignment before verification executes.

## Artifact provenance boundary

Verification accepts a local `file://` output only when the resolved target remains inside the explicitly supplied runtime artifact root.

The authorization check resolves the real path before reading the file, preventing relative-path or symbolic-link escape from turning verification into an arbitrary local-file reader.

The repository ignores `.teo/`, which is the default local runtime-artifact tree.

## Verifier failure semantics

Verifier infrastructure failure is not a verification judgment. Connection failure, provider HTTP failure, unsupported verifier model, malformed decision JSON, model substitution, missing structured output, or artifact authorization failure raises a live verification error and fails closed.

These conditions must not be transformed into synthetic `passed`, `failed`, or `needs_human` judgments because no valid verifier decision was obtained.

## Finalization

A valid verifier decision is converted into the existing `VerificationResult` contract. Finalization still requires matching dispatch identity, assigned verifier identity, model and provider independence, acceptable verification, and qualified-human approval where required.

A model verifier cannot satisfy qualified-human approval.

## Calibration boundary

A model judge is not ground truth.

Before this gate expands beyond the guarded canary, TEO requires calibration against deterministic gold labels where possible and independently rated human outcomes where semantic judgment is required.

The calibration program must measure at least false pass, false fail, `needs_human`, criterion-level confusion, repeatability, provider/model disagreement, prompt-injection resistance, latency, retry/fallback association, and normalized usage.

## Non-goals

This slice does not implement verifier retry, verifier fallback, multi-judge consensus, pairwise model ranking, semantic ground-truth generation, broad domain verification, high or critical risk live verification, automatic human approval, or route optimization from verifier judgments.
