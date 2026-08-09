# Provider Access Boundary

TEO routes to implementations. It does not provision access to them.

## Architectural boundary

The orchestration decision ends with the selected implementation, reasoning effort, fallback, and independent verifier. Authentication, subscription, credentials, account entitlement, and transport are resolved outside that decision by the caller or integrating runtime.

This means the same TEO route remains the same route whether the selected model is reached through:

- an API key,
- OAuth or subscription-backed login,
- delegated identity,
- a service account,
- a connector session,
- a credential broker,
- an SDK-managed identity flow, or
- another provider-supported access mechanism.

TEO must not prefer, demote, or replace a model merely because one connection method is easier to provision than another.

## What remains routing-relevant

Model and provider facts remain relevant when they describe the implementation itself: canonical model identity, lifecycle, provider availability, capability fit, supported reasoning controls, preview status, fallback independence, verifier independence, and evidence of route fitness.

User-specific access state is different. API-key presence, OAuth login state, subscription tier, account billing, credential format, and connector type are not model-fitness signals.

## Runtime contract

The reference implementation expresses this separation through `ProviderConnection`.

A runtime first receives a dispatch that has already selected the model. It then supplies a provider connection capable of invoking that already-selected provider operation. The connection may obtain authorization through any provider-supported mechanism.

`HeaderProviderConnection` and environment-backed API-key helpers are reference conveniences. They demonstrate one way to satisfy the runtime boundary. They are not the TEO architecture and do not imply that API access is required by TEO.

A production integration may instead use OAuth or subscription-backed clients, delegated identity, managed credentials, connector sessions, local runtimes, or other access mechanisms without changing the routing policy.

## Failure semantics

Missing credentials, expired OAuth state, insufficient subscription entitlement, billing problems, permission failures, and local connection failures are access or execution-boundary conditions.

They must not:

- reclassify the task,
- alter the selected model because of authentication style,
- be treated as evidence that another model is intrinsically better suited,
- poison provider-family health, or
- be persisted as routing metadata.

Existing retry, redispatch, fallback, and refusal policies may handle a runtime failure when their conditions are met. That handling remains policy-governed and must not create an implicit preference for API keys, OAuth, subscriptions, or any other connection method.

## Evidence workflows

Repository-hosted GitHub Actions cannot inherit an end user's interactive subscription session. Therefore an Actions workflow may use repository API-key secrets as a convenience harness for automated evidence collection.

That is a property of that workflow environment, not a requirement of TEO. The same evidence collectors can be called by another runtime that injects a different `ProviderConnection` implementation.

## Ownership

TEO owns routing correctness.

The user or integrating system owns valid access to the selected implementation.
