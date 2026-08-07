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

The connection layer owns only the mechanics required to reach the already-selected provider endpoint, SDK, connector, service, or local runtime.

## Connection methods are not routing capabilities

Examples of connection mechanisms include:

- API keys
- OAuth access
- delegated user identity
- service accounts or workload identity
- enterprise credential brokers
- connector or application sessions
- SDK-managed credentials
- locally resolved credentials
- local runtime sockets or process access

These mechanisms can affect whether a route is currently reachable, but they do not redefine the capability, provider, model, specialist, worker, or verification route.

A missing or invalid connection can produce a normalized provider or request failure. It must not silently cause the adapter to choose another model, provider, fallback, or verifier.

## Runtime interface

The Python reference implementation exposes `ProviderConnection` as a runtime-owned invocation strategy.

A provider adapter receives:

1. a TEO `ProviderExecutionRequest` containing the authorized provider family and model
2. a `ProviderConnection` capable of invoking the already-selected provider operation through any supported connection mechanism

The connection object is not serialized into the dispatch, provider execution request, provider execution response, final outcome, or audit record.

The adapter creates an ephemeral `ProviderConnectionRequest` containing only the provider operation, endpoint or runtime target, protocol metadata, request body, and timeout needed for that one invocation. The connection implementation then decides how to authenticate, authorize, broker, or execute that call.

The reference `HeaderProviderConnection` is only one connection implementation. It supports HTTP transports with externally resolved authorization headers. Future SDK-, connector-, OAuth-session-, local-runtime-, workload-identity-, and broker-backed connection implementations can use different mechanics while preserving the same provider route and adapter contract.

## Security boundary

Credential material must remain outside serialized TEO execution records.

The connection layer must not:

- place credentials into `input_payload`
- place credentials into normalized evidence
- expose raw authorization headers in audit records
- persist provider-native credential objects as execution artifacts
- alter the provider or model authorized by the dispatch

Provider adapters receive only the connection object at runtime. They do not need to know whether the underlying identity came from an API key, OAuth, a connector session, delegated identity, or another supported mechanism.

## Availability and failure semantics

Connection state is runtime evidence, not static model identity.

Examples:

- an expired OAuth token may make the selected provider temporarily unusable
- a missing API key may prevent one deployment from reaching a provider
- a connector session may be unavailable in one environment and present in another
- a service-account or workload-identity exchange may fail
- a local model runtime may be offline while its model registration remains valid

The adapter normalizes these failures and returns control to orchestration. Orchestration then applies the existing failure-scope, retry, fallback, or escalation policy.

The connection layer itself does not perform hidden fallback or choose a replacement model.

## Conformance expectations

Provider implementations should prove that:

1. changing connection mechanism does not change the selected provider or model
2. credentials never enter serialized request or result envelopes
3. a connection for the wrong provider family fails closed
4. connection failure does not trigger hidden provider or model substitution
5. protocol-required request invariants cannot be silently weakened by a connection strategy
6. the same adapter contract can be exercised through different valid connection implementations
7. connection implementations for OpenAI/Codex, Anthropic/Claude, Google/Gemini/Antigravity, local runtimes, and future providers obey the same authority boundary

The first live Anthropic canary uses this shared boundary. Its current HTTP connection fixture is an implementation detail, not a routing requirement and not a restriction on future supported connection mechanisms.
