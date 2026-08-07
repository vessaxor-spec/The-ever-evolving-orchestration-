# Provider Adapter Contract

## Status

This document defines the first runtime-execution boundary for the TEO reference implementation.

The contract is intentionally narrower than a live provider integration. It establishes how an already-authorized dispatch may cross into a provider adapter without allowing that adapter to acquire routing, fallback, verification, or approval authority.

Contract version: `1`

## Responsibility boundary

Mission Control and the routing control plane remain responsible for:

- task classification
- effective-risk assessment
- team, worker, and specialist selection
- capability resolution
- provider-family and model selection
- routine fallback selection
- independent verifier selection
- escalation policy
- qualified-human approval requirements

A provider adapter is responsible for exactly one thing:

> Execute one authorized attempt against the provider family and model already selected by the dispatch, then return a normalized result.

An adapter must not:

- select another model
- switch provider family
- invoke the preselected fallback
- perform an automatic orchestration-level retry
- select or perform independent verification
- waive or satisfy human approval
- modify the dispatch
- return a provider-native payload as the runtime contract
- serialize credentials, authorization headers, secrets, passwords, or access tokens into the request or normalized result

Provider SDK initialization and credential acquisition remain provider-specific implementation concerns outside the serialized contract.

## Request envelope

`ProviderExecutionRequest` contains only execution-authorizing information:

- `contract_version`
- `dispatch_id`
- `task_id`
- `provider_family`
- `model`
- `risk_level`
- `required_capabilities`
- `input_payload`

The request intentionally excludes:

- fallback implementation
- verifier implementation
- verification methods
- human-approval state
- escalation candidates

Those fields are control-plane authority and are not required to perform the authorized provider attempt.

The reference helper derives the provider family and model directly from `dispatch.selected_implementation`. An implementation without a declared provider family fails closed.

`input_payload` is provider-neutral execution input. Version 1 defaults to the dispatched task text when no richer runtime payload is supplied. Future prompt assembly, tool binding, and context packaging may populate this object without changing provider or model authority.

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

## Failure taxonomy

Version 1 uses the same bounded failure scopes already established by TEO routing policy:

| Scope | Meaning | Runtime implication |
|---|---|---|
| `request` | The request itself is invalid or cannot be fulfilled as submitted | Correct or reject the request before another execution attempt |
| `transient` | A temporary execution condition interrupted the attempt | Future runtime may apply bounded retry policy |
| `model` | The selected model is unavailable or unsuitable while the provider may remain usable | Future orchestration may redispatch with the implementation blocked |
| `provider` | The provider family is unavailable or unusable for the request | Future orchestration may redispatch with the provider blocked |
| `capability` | The selected execution path cannot satisfy a required capability | Return to capability and routing resolution |

The adapter reports the failure scope. It does not decide the recovery action.

## Single-attempt rule

`execute_provider_once` performs one adapter call.

If that attempt fails, the returned `ExecutionResult` is failed and records one failed attempt. The adapter layer does not call the fallback. Existing orchestration logic remains responsible for deciding whether another dispatch, fallback, or escalation is required.

This separation is deliberate. A hidden adapter retry or fallback would make provider selection, independent verification, audit history, retry budgets, and failure-scope handling less observable.

## Contract validation

The reference implementation fails closed when:

- adapter provider family differs from the dispatch-selected provider
- response provider family differs from the dispatch or request
- response model differs from the selected model
- response dispatch ID differs from the active dispatch
- request and response contract versions differ
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

The reference conformance suite is:

- `tests/test_provider_adapter_contract.py`

## Non-goals for version 1

This change does not implement:

- OpenAI, Anthropic, Google, local-model, or other live provider clients
- credential storage or secret management
- prompt assembly
- tool execution protocols
- streaming
- retry budgets
- backoff or jitter
- circuit breakers
- live fallback execution
- cost, latency, or quality telemetry
- verifier execution
- qualified-human approval integration

Those runtime layers should be added only after this boundary proves stable under conformance testing.

## Acceptance gate before the first live provider

The first live provider adapter should not be added until the contract demonstrates that:

1. dispatch-selected provider and model authority cannot be silently changed by an adapter
2. failed execution returns to orchestration without hidden fallback
3. failure scope is normalized into the five declared categories
4. provider-native responses cannot leak across the adapter boundary
5. credentials are not part of serialized execution records
6. existing routing, verification, finalization, evidence-pilot, and specialist-preservation tests remain green

The first live provider should then implement this contract rather than changing it to fit one provider SDK.
