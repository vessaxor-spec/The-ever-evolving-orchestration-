# TEO Python Reference Router

This is the runnable reference control plane for The Ever-Evolving Orchestration. It reads TEO's YAML policy and registries, creates a structured dispatch, assigns an independent verifier, and records a final evidence-bearing outcome.

The router itself remains provider-neutral. Live provider execution is optional and occurs only through the provider-adapter boundary after routing has already selected the authorized provider family, model, and reasoning effort.

The current bounded `high_volume_simple` live canary at low or medium effective risk uses the following governed topology:

- primary executor: Google Gemini 3.5 Flash-Lite
- primary verifier: Anthropic Claude Sonnet 5
- first cross-provider recovery executor after eligible Flash-Lite/model or Google/provider failure: Anthropic Claude Haiku 4.5
- fresh verifier after Haiku execution when Google remains eligible: Google Gemini 3.6 Flash
- fresh verifier after Haiku execution when Google is provider-blocked: OpenAI GPT-5.6 Sol
- independent economical OpenAI alternative: GPT-5.6 Luna

The provider-adapter layer also implements the exact staged capabilities needed by the `documentation` evaluation candidate: Claude Sonnet 5 execution, GPT-5.6 Sol execution, and GPT-5.6 Terra verification. Those capabilities are **not** documentation live-execution authority. The guarded runtime and live-verification task scope remain limited to `high_volume_simple` until a separate reviewed activation change satisfies every live-expansion gate.

Each provider adapter performs one provider attempt only. Adapters do not own retry, fallback, circuit state, telemetry persistence, verification, escalation, or human approval.

The runtime coordinator may retry a `transient` failure once under the same dispatch. The retry preserves provider, model, reasoning effort, verifier, specialist, worker, and risk authority. The current policy uses bounded backoff with jitter and permits at most two provider attempts per dispatch.

Provider adapters may normalize a provider-requested minimum wait into `retry_after_seconds`. The retry controller treats that value only as a timing hint for an already-authorized transient retry. It uses the greater of TEO's local backoff and an in-budget provider hint. A provider request above the guarded 60-second wait budget stops the retry sequence rather than causing TEO to retry early. Provider timing never creates another attempt or changes failure scope.

The runtime coordinator can also perform one guarded automatic fallback after a `model` or `provider` failure. It returns the failure to TEO, applies the failed model or provider block, creates a new dispatch ID, assigns a fresh independent verifier, and then executes the newly selected provider. Request, capability, and exhausted transient failures do not directly trigger fallback, and a failed fallback never chains automatically to a third provider.

Provider-family circuit state persists across separate canary executions. Repeated declared service-health failures can open a provider circuit. An open provider is added to copied blocked-provider constraints before canonical routing, so TEO itself selects the alternate implementation and verifier. Authentication, billing, permission, quota/rate-limit, model-not-found, bad-request, and local connection failures never open a provider-family circuit by themselves.

After cooldown an open circuit becomes half-open. The reference runtime allows one recovery probe at a time and requires two successful probes before restoring normal routing. Repeated trips progressively increase cooldown within a bounded policy limit.

Every actual provider attempt is recorded as persistent content-free runtime telemetry. The default JSONL record captures dispatch/provider/model/effort identity, primary or fallback role, attempt number, latency, normalized failure state, retry timing, assigned verifier, and provider-reported token usage. It does not persist prompts, task text, model output, provider-native payloads, credentials, authorization headers, or connection mechanism.

A successful guarded execution can be submitted to the dispatch-assigned live verifier. The verifier is required to use a different model and provider family from the active executor, receives a blinded task/output rubric, and returns structured `passed`, `failed`, or `needs_human` evidence. Verifier retry and verifier fallback remain disabled in this first slice. Verification infrastructure failure fails closed and is not converted into a model judgment.

Connection method is deliberately separate from routing, telemetry, verification, and provider-health classification. API keys, OAuth, delegated identity, service accounts, connector sessions, local credentials, and future connection mechanisms belong behind `ProviderConnection`; they do not change the selected model route.

## Install

```bash
python -m pip install -e '.[test]'
```

## Validate linked configuration

```bash
teo --repo-root . validate
```

Warnings expose current registry gaps without rewriting or weakening canonical team, worker, or specialist definitions.

## Create a dispatch

```bash
teo --repo-root . plan reference/examples/phase5-task.yaml \
  --output /tmp/teo-dispatch.json \
  --audit-log /tmp/teo-audit.jsonl
```

## Provider execution boundary

Provider execution is split into independent concerns:

1. TEO routing authorizes a provider family, model, and reasoning effort through `ProviderExecutionRequest`.
2. Runtime supplies a provider-specific `ProviderConnection` without exposing credential material to the dispatch or audit record.
3. Provider adapters may normalize provider-native retry timing and usage without retrying or persisting telemetry themselves.
4. Provider circuit state may block a known-unhealthy provider before a new canonical dispatch.
5. The retry controller may repeat only a transient failure under the same dispatch and remains bound by the attempt budget.
6. The telemetry layer records each completed provider attempt before later retry or fallback action.
7. The fallback coordinator may redispatch only after eligible model or provider failure.
8. The live verification layer executes only the verifier assigned by the active dispatch and returns evidence through the existing `VerificationResult` contract.
9. Finalization may optionally revalidate canonical Route-Outcome Evidence and project the observed active execution route into `FinalOutcome.execution_provenance`; that projection is evidence only and never routing or execution authority.

The general contracts are documented in:

- `docs/specification/provider-adapter-contract.md`
- `docs/specification/provider-connection-boundary.md`
- `docs/specification/provider-directed-retry-timing.md`
- `docs/specification/bounded-transient-retry.md`
- `docs/specification/guarded-canary-fallback.md`
- `docs/specification/provider-circuit-breaker.md`
- `docs/specification/runtime-telemetry.md`
- `docs/specification/live-independent-verification.md`
- `docs/specification/final-execution-provenance.md`

The runtime research records include:

- `research/runtime/2026-08-07-provider-circuit-breaker.md`
- `research/runtime/2026-08-07-provider-directed-retry-timing.md`
- `research/runtime/2026-08-07-persistent-runtime-telemetry.md`
- `research/runtime/2026-08-07-live-independent-verification.md`
- `research/runtime/2026-08-11-documentation-live-topology-adapter-readiness.md`
- `research/runtime/2026-08-11-documentation-controlled-replay.md`

Current provider execution implementations are:

- `teo_reference.anthropic_adapter.AnthropicMessagesAdapter`
- `teo_reference.openai_adapter.OpenAIResponsesAdapter`
- `teo_reference.google_adapter.GeminiInteractionsAdapter`

Current guarded verifier implementations are:

- `teo_reference.google_verifier.GoogleLiveVerifier`
- `teo_reference.anthropic_verifier.AnthropicLiveVerifier`
- `teo_reference.openai_verifier.OpenAILiveVerifier`

Single-attempt execution helpers are:

- `execute_anthropic_canary_once`
- `execute_openai_canary_once`
- `execute_gemini_canary_once`

Runtime coordination is exposed through:

- `RetryPolicy`
- `execute_with_transient_retry`
- `ProviderCircuitPolicy`
- `ProviderCircuitBreaker`
- `InMemoryCircuitStateStore`
- `JsonFileCircuitStateStore`
- `RuntimeTelemetryEvent`
- `InMemoryRuntimeTelemetrySink`
- `JsonlRuntimeTelemetrySink`
- `LiveVerificationPolicy`
- `execute_live_verification`
- `verify_guarded_canary_outcome`
- `execute_guarded_canary`

OpenAI maps TEO effort to Responses API `reasoning.effort`. Gemini maps it to Interactions API `generation_config.thinking_level`. Claude Haiku 4.5 does not support Anthropic's newer `output_config.effort` parameter, so the adapter does not invent one. The staged Sonnet 5 execution path preserves assigned effort through Anthropic `output_config.effort` where supported.

Anthropic's documented numeric `retry-after`, generic numeric `Retry-After` headers when present, and standard Google `RetryInfo` when present are normalized to seconds. Raw provider headers and provider-specific retry structures do not cross the adapter boundary.

Provider-reported usage is normalized into input, output, cached input, cache creation, reasoning/thought, tool-use, and total token fields where available. TEO does not calculate monetary cost in telemetry v1 because pricing is a separate time-sensitive evidence source. Source-backed cost attribution is performed by the separate cost-evidence contract rather than inferred inside telemetry.

The default guarded runtime writes attempt telemetry to:

- `.teo/runtime/artifacts/runtime-telemetry.jsonl`

The JSONL telemetry and JSON circuit-state stores are single-process reference implementations. Multi-process or distributed runtimes require shared persistence with appropriate concurrency, access control, retention, and export behavior.

All guarded live execution canaries and the live verifier refuse high or critical risk.

A successful provider execution is not a completed TEO outcome. Live independent verification can satisfy the model-verification gate for the guarded canary, but qualified human approval remains separate whenever policy requires it.

## Finalize an executed and verified result

Standard finalization remains:

```bash
teo --repo-root . finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --audit-log /tmp/teo-audit.jsonl
```

Execution and verification records must reference the dispatch ID. The verifier must match the assigned verification implementation and must remain independent from the selected worker implementation.

When the caller also has the canonical Route-Outcome Evidence record for the final active dispatch, it may request the compatible execution-provenance projection:

```bash
teo --repo-root . finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --route-outcome route-outcome-record.json \
  --audit-log /tmp/teo-audit.jsonl
```

The supplied route record is revalidated before attachment. It must agree with the final dispatch, successful active route, selected model, verifier model, verification status, and final disposition. A caller cannot use `--route-outcome` to nominate or override provider/model identity. The optional `execution_provenance` projection is read-only evidence and does not replace the complete Route-Outcome Evidence record.

## Staged documentation replay

The `documentation` candidate has a separate controlled replay harness and operator path. It preserves the exact staged route, assigned Terra verifier, retry policy, per-trial circuit isolation, in-memory replay telemetry, and canonical Route-Outcome Evidence while requiring explicit operator acknowledgement before live provider calls.

Automatic fallback is intentionally disabled in this replay milestone. A model/provider failure is recorded rather than becoming a hidden alternate live runtime. Provider-backed replay evidence remains pending and `documentation` remains `activation_authorized: false`.

## Regulated evidence stability qualification

The reference package includes `teo_reference.evidence_stability`, an executable qualification harness for the bounded six-card regulated-specialist evidence pilot. The governing requirements live in `policy/specialists/evidence-stability-qualification.yaml`.

The current qualification requires five complete clean authority-resolution replays, three independently executed repeatability runs, all 15 governed fail-closed mutation classes to be killed, a controlled authority-move path, and a successful external-network authority-resolution observation. The harness does not convert deterministic fixtures into a claim of live network success; the external observation is validated separately.

The active seven-day authority-resolution cadence remains continuous monitoring after qualification. The qualification result is evidence only and never auto-authorizes registry expansion. Any next risk-tier batch requires explicit approval and a separate reviewed change.

Historical qualification evidence is recorded in `docs/history/validation/regulated-specialist-evidence-stability-qualification-2026-08-16.md`.

## End-to-end demonstration

```bash
python reference/examples/run_example.py
```

## Tests

```bash
pytest
```

The documentation-reconciliation baseline CI #602 passed 802 automated tests. The canonical current state and historical validation milestones are tracked in `docs/stewardship/progress-tracker.md`.
