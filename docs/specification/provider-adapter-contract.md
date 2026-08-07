# Provider Adapter Contract

## Status

This document defines the runtime-execution boundary for the TEO reference implementation.

The contract establishes how an already-authorized dispatch crosses into a provider adapter without allowing that adapter to acquire routing, retry, fallback, circuit-state, verification, or approval authority.

Contract version: `1`

## Responsibility boundary

Mission Control and the routing control plane remain responsible for:

- task classification
- effective-risk assessment
- team, worker, and specialist selection
- capability resolution
- provider-family and model selection
- reasoning-effort selection
- routine fallback selection
- independent verifier selection
- escalation policy
- qualified-human approval requirements

A provider adapter is responsible for exactly one thing:

> Execute one authorized attempt against the provider family, model, and reasoning effort already selected by the dispatch, then return a normalized result.

An adapter must not:

- select another model
- switch provider family
- silently increase or decrease the selected reasoning effort
- retry itself
- invoke the preselected fallback
- persist or mutate provider circuit state
- select or perform independent verification
- waive or satisfy human approval
- modify the dispatch
- return a provider-native payload as the runtime contract
- serialize credentials, authorization headers, secrets, passwords, or access tokens into the request or normalized result

Provider SDK initialization, connection establishment, credential acquisition, retry control, circuit state, and fallback coordination remain runtime concerns outside the adapter.

## Request envelope

`ProviderExecutionRequest` contains only execution-authorizing information:

- `contract_version`
- `dispatch_id`
- `task_id`
- `provider_family`
- `model`
- `reasoning_effort`
- `risk_level`
- `required_capabilities`
- `input_payload`

`reasoning_effort` is provider-neutral execution metadata selected by routing. Version 1 recognizes the union of current provider effort labels:

- `none`
- `minimal`
- `low`
- `medium`
- `high`
- `xhigh`
- `max`

A provider adapter must map only values supported by its selected model. Unsupported values fail closed before provider invocation rather than being silently translated to a different effort.

The request intentionally excludes:

- fallback implementation
- verifier implementation
- verification methods
- human-approval state
- escalation candidates
- circuit state

Those fields remain control-plane or runtime-coordination authority and are not required to perform the authorized provider attempt.

The reference helper derives provider family, model, and reasoning effort directly from `dispatch.selected_implementation`. An implementation without a declared provider family fails closed.

`input_payload` is provider-neutral execution input. Version 1 defaults to the dispatched task text when no richer runtime payload is supplied. Prompt assembly, tool binding, and context packaging may populate this object without changing provider, model, or effort authority.

## Response envelope

`ProviderExecutionResponse` returns:

- `contract_version`
- `dispatch_id`
- `status`
- `provider_family`
- `model`
- `output_ref`
- `evidence`
- normalized `failure` details when execution fails

A successful response must include an accepted `output_ref` and must not include failure details.

A failed response must not publish an accepted `output_ref` and must include normalized failure details.

The response must echo the active dispatch, provider family, and model. Any change to those values is a contract violation rather than an implicit fallback.

## Current provider implementations

The guarded reference runtime includes single-attempt adapters for the bounded `high_volume_simple` canary path:

- Anthropic Claude Haiku 4.5 through the Messages API
- OpenAI GPT-5.6 Luna through the Responses API
- Google Gemini 3.6 Flash through the Interactions API

All three remain connection-neutral through `ProviderConnection` and are restricted to low or medium risk.

OpenAI and Gemini map the TEO reasoning-effort field directly to their current provider controls. Claude Haiku 4.5 predates Anthropic's newer `output_config.effort` control, so its canary preserves the TEO effort in the request contract without inventing an unsupported provider parameter.

## Failure taxonomy

Version 1 uses the bounded failure scopes established by TEO routing policy:

| Scope | Meaning | Runtime implication |
|---|---|---|
| `request` | The request itself is invalid or cannot be fulfilled as submitted | Correct or reject the request |
| `transient` | A temporary execution condition interrupted the attempt | Guarded canary may apply bounded same-dispatch retry |
| `model` | The selected model is unavailable or unsuitable while the provider may remain usable | Guarded canary may redispatch with the implementation blocked |
| `provider` | The provider family is unavailable or unusable for the request | Guarded canary may redispatch with the provider blocked |
| `capability` | The selected execution path cannot satisfy a required capability | Return to capability and routing resolution |

The adapter reports the failure scope. It does not decide retry, circuit, fallback, or verification action.

Provider-family circuit classification is intentionally stricter than the broad `provider` failure scope. Authentication, billing, permission, quota/rate-limit, and connection failures may be provider-scoped for the active task without being evidence that the provider service itself is unhealthy.

## Single-attempt adapter rule

`execute_provider_once` and each provider adapter perform one provider invocation.

Retry, circuit breaking, and fallback are implemented above this boundary:

- bounded transient retry may invoke the same adapter again under the same dispatch
- provider circuit state may block a known-unhealthy provider before a new canonical dispatch
- model or provider fallback returns to TEO and creates a new dispatch before another provider execution

This separation keeps provider attempts, routing changes, health state, independent verification, and failure transitions observable.

The active runtime specifications are:

- `docs/specification/bounded-transient-retry.md`
- `docs/specification/provider-circuit-breaker.md`
- `docs/specification/guarded-canary-fallback.md`

## Contract validation

The reference implementation fails closed when:

- adapter provider family differs from the dispatch-selected provider
- response provider family differs from the dispatch or request
- response model differs from the selected model
- response dispatch ID differs from the active dispatch
- request and response contract versions differ
- provider reasoning controls cannot represent the selected TEO effort
- a provider-native payload is returned instead of the normalized response type
- success has no output reference
- success includes failure details
- failure has no normalized failure details
- failure publishes an accepted output reference
- a failure scope falls outside the declared taxonomy
- unknown top-level contract fields are supplied through the reference parsers
- credential-bearing field names appear in serialized execution input

The matching JSON Schemas are:

- `reference/schemas/provider-execution-request.schema.json`
- `reference/schemas/provider-execution-response.schema.json`

The reference conformance suites include:

- `tests/test_provider_adapter_contract.py`
- `tests/test_anthropic_live_canary.py`
- `tests/test_multi_provider_live_canary.py`
- `tests/test_guarded_canary_fallback.py`
- `tests/test_bounded_transient_retry.py`
- `tests/test_provider_circuit_breaker.py`

## Current runtime boundaries

The guarded runtime now supports:

- three live provider canaries
- selected reasoning-effort propagation
- at most two attempts for transient failure within one dispatch
- persistent provider-family circuit state with closed/open/half-open recovery
- one model/provider fallback redispatch with a fresh independent verifier

It does not yet implement:

- connection-scoped circuits
- distributed circuit-state coordination
- adaptive or provider-specific retry budgets
- Retry-After header interpretation
- streaming
- cost, latency, reliability, or quality telemetry persistence
- verifier execution
- qualified-human approval integration
- broad high-risk provider execution

Those controls should be added as separate layers rather than weakening the adapter contract.
