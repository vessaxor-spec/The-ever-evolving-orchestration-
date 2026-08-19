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

It refuses high or critical risk, failed execution, missing artifacts, external references, artifact-root escape, same-model verification, same-provider verification, unassigned verifier models, verifier retry/fallback, malformed structured output, and artifact-backed PASS finalization that cannot prove the exact verifier-observed artifact still exists unchanged.

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

The provider-neutral Python contracts are `LiveVerificationDecision`, `LiveVerificationRequest`, and `LiveVerificationResponse`. The canonical `VerificationResult` may additionally carry `verified_artifact` when verification examined a concrete local execution artifact.

Current provider implementations are `GoogleLiveVerifier`, `AnthropicLiveVerifier`, and `OpenAILiveVerifier`. Connection mechanism remains behind `ProviderConnection` and is not a routing signal.

## Current canary verifier routes

Primary bounded route:

```text
Gemini 3.7 Flash execution
  -> Claude Sonnet 5 verification
```

Model-specific fallback after Gemini 3.7 Flash is blocked while Anthropic remains eligible:

```text
Claude Haiku 4.5 execution
  -> GPT-5.6 Sol verification
```

Google provider-family failure:

```text
Claude Haiku 4.5 execution
  -> GPT-5.6 Sol verification
```

The live verifier does not choose these routes. Routing recomputes eligibility and records the assignment before verification executes.

## Artifact provenance boundary

Verification accepts a local `file://` output only when the resolved target remains inside the explicitly supplied runtime artifact root.

The authorization check resolves the real path before reading the file, preventing relative-path or symbolic-link escape from turning verification into an arbitrary local-file reader.

When the artifact is read, the runtime binds the exact verifier-observed bytes into `VerificationResult.verified_artifact` using:

- the canonical resolved `file://` identity;
- SHA-256 of the exact bytes supplied to verification; and
- the exact byte length.

This binding is content-integrity evidence. It is not a digital signature, origin authentication, non-repudiation mechanism, or proof that another process could not replace both an artifact and all associated evidence.

The repository ignores `.teo/`, which is the default local runtime-artifact tree.

## Verifier failure semantics

Verifier infrastructure failure is not a verification judgment. Connection failure, provider HTTP failure, unsupported verifier model, malformed decision JSON, model substitution, missing structured output, or artifact authorization failure raises a live verification error and fails closed.

These conditions must not be transformed into synthetic `passed`, `failed`, or `needs_human` judgments because no valid verifier decision was obtained.

## Finalization

A valid verifier decision is converted into the canonical `VerificationResult` contract. Finalization still requires matching dispatch identity, assigned verifier identity, model and provider independence, acceptable verification, and qualified-human approval where required.

For a successful execution with an artifact-backed `passed` verification, finalization additionally requires:

1. a `VerificationResult.verified_artifact` produced from the verifier-observed artifact;
2. an explicit authorized artifact root supplied to finalization;
3. re-resolution of the current execution `output_ref` inside that root;
4. re-reading of the current artifact bytes; and
5. exact equality of canonical artifact identity, SHA-256 digest, and byte length with the verifier-bound record.

Finalization fails closed if the artifact was mutated after verification, replaced by a sibling artifact, moved outside the authorized root, changed to an unsupported or non-revalidatable scheme, or supplied without the exact verifier binding. The finalizer does not infer an authorization root from a user-provided artifact identity.

An execution that does not publish an artifact reference remains compatible with the legacy non-artifact finalization path. This compatibility does not authorize an artifact-backed PASS without exact binding.

A model verifier cannot satisfy qualified-human approval.

## Calibration boundary

A model judge is not ground truth.

Before this gate expands beyond the guarded canary, TEO requires calibration against deterministic gold labels where possible and independently rated human outcomes where semantic judgment is required.

The calibration program must measure at least false pass, false fail, `needs_human`, criterion-level confusion, repeatability, provider/model disagreement, prompt-injection resistance, latency, retry/fallback association, and normalized usage.

## Non-goals

This slice does not implement verifier retry, verifier fallback, multi-judge consensus, pairwise model ranking, semantic ground-truth generation, broad domain verification, high or critical risk live verification, automatic human approval, route optimization from verifier judgments, remote artifact provenance, signed artifact attestations, or cross-process artifact authenticity.
