# Empirical Verifier Calibration Research

Date: 2026-08-07
Status: implementation research record
Scope: empirical evidence collection for the guarded low-risk verifier rubric

## Research question

How should TEO collect the first empirical verifier-quality evidence without treating its own reference labels as independent ground truth, contaminating runtime execution metrics, leaking evaluation content, or allowing favorable measurements to change routing automatically?

## Conclusion

The strongest defensible first protocol is:

1. finalize independent human labels before any live judge observation
2. require at least two blinded human reviewers per case and independent adjudication on disagreement
3. preserve deterministic machine-checkable facts as invariants rather than allowing human labels to override them silently
4. evaluate the same fixed cases three times on each of three provider-diverse verifier routes
5. record direct calibration as its own collection role rather than pretending it was primary or fallback execution
6. pin rubric, verification-policy, empirical-policy, and collector revisions
7. require measured duration and provider-reported input/output usage for every successful observation
8. persist only content-free observation metadata and structured decisions
9. stop on verifier infrastructure failure and resume from successfully persisted observation identities without duplicate calls
10. leave quality claims, route changes, scope expansion, and human acceptance outside the collector's authority

The resulting evidence package is a measurement input. It is not an automated release gate.

## Human labels before model observations

Human raters should not be influenced by the model judgments they are intended to evaluate.

The initial TEO protocol therefore requires human labels to be finalized before live verifier observations begin. Reviewers attest that verifier observations were blinded. The collector checks the label completion timestamp before making a provider call and refuses collection if chronology is invalid.

Two independent reviewers are required for every case. Disagreement requires an adjudicator who was not one of those reviewers.

This is deliberately stronger than using the public reference labels as gold. The reference corpus remains useful for fixed cases, deterministic checks, and comparison, but empirical quality is measured against independently reviewed labels.

## Deterministic evidence remains authoritative where objective

Some control cases have exact machine-checkable outcomes, such as exact ordered lines, line counts, or prohibited substrings.

Independent human labeling is still valuable for validating the rubric process, but a human label that contradicts a complete deterministic check is not silently accepted as superior ground truth. TEO rejects that evidence set and requires investigation.

This preserves the distinction between semantic human judgment and directly executable evidence.

## Direct calibration is not execution

The existing calibration evaluator can segment observations by primary, retried-primary, and fallback execution paths.

A direct judge experiment has none of those meanings. Labeling it `primary` would create false operational evidence.

The empirical collector therefore persists the explicit role `calibration_direct` and omits execution retry/fallback fields. Compatibility conversion to the base evaluator exists only in memory; exported empirical reports relabel that slice as `by_collection_path.calibration_direct`.

## Provider-diverse repeated measurement

The initial protocol uses three runs per case on three provider families:

- Google Gemini 3.6 Flash at medium reasoning
- Anthropic Claude Sonnet 5 at medium effort
- OpenAI GPT-5.6 Sol at medium reasoning

With eight fixed cases this produces 72 planned live verifier calls.

Three provider families are used because variants from one provider do not provide the same diversity evidence. Repetition is required because one judgment per case cannot establish stability.

## Provider usage evidence

Usage is extracted from the successful provider response in memory and normalized before the provider-native response is discarded.

### Anthropic

Anthropic's current Messages API documentation defines `usage.input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, and `output_tokens`. Anthropic states that total input is the sum of input, cache-creation input, and cache-read input.

Sources:
- https://platform.claude.com/docs/en/api/go/messages
- https://platform.claude.com/docs/en/api/typescript/messages/create

TEO therefore normalizes Anthropic input tokens as that sum and records `output_tokens` as the inclusive output count.

### Google

Google's current Gemini Interactions API documents usage fields including `total_input_tokens`, `total_output_tokens`, `total_thought_tokens`, and `total_tokens`.

Source:
- https://ai.google.dev/api/interactions-api-v1

TEO records `total_input_tokens` and `total_output_tokens` for the initial empirical comparison.

### OpenAI

OpenAI's current GPT-5.6 guidance recommends the Responses API for reasoning workloads and requires reasoning effort to be set intentionally. GPT-5.6 Sol supports the medium effort used by the calibration route.

Sources:
- https://developers.openai.com/api/docs/guides/latest-model
- https://developers.openai.com/api/docs/models

The Responses API exposes normalized response usage, and the existing TEO OpenAI runtime contract records input and output token counts. The empirical collector requires those values rather than treating missing usage as zero.

## Why usage is mandatory

A successful decision without usage is still evidence about judgment quality, but it is incomplete evidence for comparing operational tradeoffs across routes.

TEO's calibration policy explicitly requires latency and usage evidence. The collector therefore fails closed when a successful provider response lacks the required normalized token counts.

This prevents a provider route with missing telemetry from appearing artificially cheap or efficient.

## Latency measurement

The collector measures elapsed verifier-call duration using a monotonic clock.

The observation timestamp records when the result was accepted into the evidence set. Duration and timestamp serve different purposes:

- duration measures invocation latency
- timestamp defines the empirical observation window and allows later drift analysis

Every timestamp must include a UTC offset.

## Privacy and minimization

The empirical observation file deliberately excludes:

- task text
- candidate output
- provider-native payload
- request IDs
- credentials
- authorization headers
- connection method
- human reviewer names or email addresses

The fixed corpus already contains the evaluation content. Observation and human-label files join to it by case ID.

Provider request identifiers can be useful for debugging, but keeping them out of the empirical dataset reduces unnecessary linkage and prevents operational identifiers from becoming part of the public measurement contract.

## Connection neutrality

The collector library accepts TEO's provider-neutral `ProviderConnection` interface.

For operator convenience, the CLI can construct header-based connections from environment variables. That convenience does not affect verifier route identity or evidence grouping. API key, OAuth, delegated identity, connector session, service account, or another supported connection mechanism remains outside routing and calibration semantics.

## Resume and partial failure

The evidence file is append-only JSONL under `.teo/` by default.

Every successfully accepted observation is flushed and fsynced before the next call. On restart, the collector reconstructs completed case/route/run identities and skips them.

The evidence set also pins the collector repository revision. A resumed run may continue only with the same revision. Mixing revisions would introduce an uncontrolled implementation variable.

Verifier infrastructure failure stops the current collection. It is not converted into a judgment and does not generate a synthetic observation.

## Quality and governance boundary

Even a complete 72-observation evidence set with favorable metrics does not authorize:

- an empirical quality claim
- a routing change
- a verifier replacement
- broader live verification
- high or critical live execution
- automated human approval

The measured result still requires independent residual-risk review and explicit human acceptance.

Only an accepted empirical milestone should be preserved in a new Capsule.
