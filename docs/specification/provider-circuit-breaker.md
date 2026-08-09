# Provider Circuit Breaker

## Status

This specification defines the first stateful dependency-health control in the TEO reference runtime.

It applies only to the guarded `high_volume_simple` live path at low or medium risk.

## Purpose

Bounded retry handles short transient faults inside one dispatch. Guarded fallback handles model- or provider-scoped failure by returning to routing and creating a new dispatch.

A circuit breaker solves a different problem: repeated dependency failure across separate executions.

Without persistent provider-health state, every new task can repeat the same retry sequence against a provider that is already known to be unhealthy. This can increase latency, amplify provider overload, and create retry storms.

## Placement

Circuit state belongs above provider adapters and above the single-dispatch retry controller.

Provider adapters remain stateless and perform one provider attempt only.

The circuit layer may:

- persist provider-family health state across executions
- block an open provider before canonical routing
- allow bounded half-open recovery probes
- observe the final provider response after the active retry sequence completes

The circuit layer may not:

- choose a replacement model directly
- change specialist, worker, risk, or approval authority
- alter provider connection or credential mechanics
- execute verification
- satisfy human approval
- convert quota, authentication, billing, permission, or local connection failures into global outages

## States

### Closed

Traffic may route to the provider normally.

Service-health failures are counted inside the configured failure window. Successful responses and non-service-health provider responses clear the current service-health failure streak.

### Open

The provider is added to a copied task's `blocked_providers` constraints before canonical routing.

The original task is not mutated. TEO then selects another eligible provider/model route and verifier under its existing policy.

No provider call is attempted while the circuit remains open.

### Half-open

After the open cooldown expires, the provider becomes eligible for a bounded recovery probe.

The reference implementation permits one half-open probe dispatch at a time. Two successful probes are required before the circuit returns to Closed.

A service-health failure during half-open immediately reopens the circuit. A non-service-health failure, including a local connection error, is inconclusive: it clears the active probe claim but leaves the provider in Half-open because the failure does not establish provider-family unhealthiness and recovery has not been demonstrated.

Half-open probe claims are leased rather than permanent. The guarded reference lease is 30 seconds. If a process crashes or otherwise fails before recording the probe result, the abandoned claim expires and a later task may perform another bounded recovery probe. This lease is a single-process reference safeguard, not distributed coordination.

## Global service-health signals

Provider-family circuits are intentionally conservative.

The guarded policy currently counts only declared service-health codes:

### Anthropic

- `overloaded_error`
- `api_error`
- `timeout_error`

### OpenAI

- `server_error`
- `internal_server_error`
- `internal_error`
- `service_unavailable`
- `overloaded_error`
- `timeout_error`

### Google

- `unavailable`
- `internal`
- `deadline_exceeded`
- `service_unavailable`

Unknown error codes do not open a provider-family circuit automatically.

## Explicit exclusions

The following classes must never open a global provider-family circuit by themselves:

- authentication
- permission
- billing
- account, organization, or project quota
- rate limit exhaustion
- model not found
- invalid request
- local connection failure

These conditions can still fail the active execution and may still trigger existing task-level fallback according to TEO routing policy. They simply do not establish that the provider family itself is unhealthy.

## Trip policy

The guarded reference policy is stored at:

`policy/runtime/provider-circuit-breaker.yaml`

Current defaults:

- 3 service-health failures
- 120-second failure window
- 60-second initial open cooldown
- 2x cooldown multiplier after repeated circuit trips
- 300-second maximum cooldown
- 1 half-open probe dispatch at a time
- 2 successful half-open probes required to close
- 30-second half-open probe lease
- non-service-health half-open failures remain inconclusive rather than reopening provider health

These are canary defaults rather than universal production constants.

## Interaction with retry

Circuit observation occurs after the bounded retry sequence for the active dispatch.

This means a single retryable server error does not immediately poison provider health. If the retry succeeds, the circuit observes success.

If the retry sequence ends in a declared service-health failure, that final result contributes one failure observation to the cross-execution circuit state.

Retry remains the same dispatch. Circuit state does not change dispatch identity.

## Interaction with fallback

An already-open circuit influences a new task before dispatch by adding the provider to copied blocked-provider constraints.

A failure in the active task continues to use existing fallback rules:

- model failure blocks the model and redispatches
- provider failure blocks the provider and redispatches
- exhausted transient retry does not automatically authorize fallback

If a transient service-health failure causes the circuit to trip, the active task still ends according to the transient-failure contract. Subsequent tasks route around the newly open provider.

This preserves the separation introduced by the bounded retry policy.

## Persistence

The reference implementation provides:

- `InMemoryCircuitStateStore` for deterministic tests
- `JsonFileCircuitStateStore` for state that survives separate executions in one runtime

The default guarded runtime persists to:

`.teo/runtime/provider-circuits.json`

or the equivalent parent directory of a custom artifact root.

Malformed persisted state fails closed rather than being silently reset.

A persisted in-flight half-open probe includes the time at which the probe was claimed. An in-flight claim without a claim timestamp is invalid state and fails closed. Claims older than the active probe lease are released during circuit refresh so an interrupted process cannot strand provider recovery indefinitely.

## Concurrency boundary

The JSON state store is a single-process reference mechanism. Atomic file replacement prevents partial writes, but it is not a distributed coordination system.

Multi-process and multi-host runtimes require a shared transactional store that can safely coordinate:

- state transitions
- failure counters
- open deadlines
- half-open probe claims and leases

That production store is outside this runtime slice.

## Connection neutrality

Provider circuit state does not depend on whether the runtime connects through:

- API key
- OAuth
- delegated identity
- service account
- connector session
- SDK-backed credential
- local credential broker
- future connection methods

Connection-scoped health is intentionally not implemented yet. Provider-family health must not be inferred from a single user's credential or quota condition.

## Observability

`CanaryRuntimeOutcome` exposes:

- providers blocked by circuit state before routing
- provider circuit state after the primary execution
- provider circuit state after fallback execution, when present

Persistent state also records:

- circuit state
- failure count and failure-window start
- open and reopen timestamps
- trip count
- half-open success count
- probe-in-flight state and claim timestamp
- last service-health failure code
- last state transition time

No external telemetry backend is introduced in this slice.

## Research basis

The supporting research record is:

`research/runtime/2026-08-07-provider-circuit-breaker.md`

It reviews current OpenAI, Anthropic, Google, AWS, Microsoft Azure, Google Cloud, and practitioner evidence.

## Non-goals

This slice does not implement:

- connection-scoped circuits
- distributed circuit state
- external provider-status ingestion
- adaptive or machine-learned thresholds
- bulkheads
- concurrency limits
- retry-header propagation
- live verifier execution
- human approval integration
- high or critical risk live execution
