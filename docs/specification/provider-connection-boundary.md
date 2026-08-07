# Provider Connection Boundary

## Status

This document defines the runtime connection boundary that sits behind TEO provider and model routing.

The model route is architecture. The connection method is plumbing.

TEO must not change a routing decision because one user reaches a model with an API key while another reaches the same model through OAuth, delegated identity, a service account, a connector session, a credential broker, a local runtime, or another provider-supported mechanism.

## Provider-wide invariant

This rule applies equally to current provider families and agent surfaces, including:

- OpenAI and Codex
- Anthropic and Claude
- Google, Gemini, and Antigravity
- local runtimes
- future provider families and model surfaces

The routing control plane owns:

- capability requirements
- provider-family selection
- model or agent selection
- risk classification
- specialist and worker allocation
- fallback selection
- verifier selection
- escalation policy
- qualified-human approval requirements

The connection layer owns only the mechanics required to reach the already-selected provider endpoint or runtime.

## Connection methods are not routing capabilities

Examples of connection mechanisms include:

- API keys
- OAuth access
- delegated user identity
- service accounts or workload identity
- enterprise credential brokers
- connector or application sessions
- locally resolved credentials
- local runtime sockets or process access

These mechanisms can affect whether a route is currently reachable, but they do not redefine the capability, provider, model, specialist, worker, or verification route.

A missing or invalid connection can produce a normalized provider or request failure. It must not silently cause the adapter to choose another model, provider, fallback, or verifier.

## Runtime interface

The Python reference implementation exposes `ProviderConnection` as a runtime-owned strategy.

A provider adapter receives:

1. a TEO `ProviderExecutionRequest` containing the authorized provider family and model
2. a `ProviderConnection` capable of authorizing or otherwise preparing the provider-specific transport

The connection object is not serialized into the dispatch, provider execution request, provider execution response, final outcome, or audit record.

The reference `HeaderProviderConnection` is intentionally minimal. It can represent externally resolved API-key headers, OAuth-style authorization headers, delegated tokens, or other header-based mechanisms without requiring TEO routing to know how those credentials were obtained.

Future SDK-, connector-, local-runtime-, and broker-backed connection implementations may use different mechanics while preserving the same routing and adapter contracts.

## Security boundary

Credential material must remain outside serialized TEO execution records.

The connection layer must not:

- place credentials into `input_payload`
- place credentials into normalized evidence
- expose raw authorization headers in audit records
- persist provider-native credential objects as execution artifacts
- alter the provider or model authorized by the dispatch

Provider adapters may receive connection material only at runtime and only through the connection boundary.

## Availability and failure semantics

Connection state is runtime evidence, not static model identity.

Examples:

- an expired OAuth token may make the selected provider temporarily unusable
- a missing API key may prevent a local deployment from reaching a provider
- a connector session may be unavailable in one environment and present in another
- a local model runtime may be offline while its model registration remains valid

The adapter normalizes these failures and returns control to orchestration. Orchestration then applies the existing failure-scope, retry, fallback, or escalation policy.

The connection layer itself does not perform hidden fallback.

## Conformance expectations

Provider implementations should prove that:

1. changing connection mechanism does not change the selected provider or model
2. credentials never enter serialized request or result envelopes
3. a connection for the wrong provider family fails closed
4. connection failure does not trigger hidden provider or model substitution
5. protocol-required headers or request invariants cannot be silently weakened by a connection strategy
6. the same adapter contract can be exercised with different valid connection strategies

The first live Anthropic canary is intentionally tested with both API-key-style and OAuth-style authorization headers to demonstrate this separation. Those examples are connection fixtures, not routing policy.
