# TEO v1 Readiness

TEO v1 is defined as a credible vendor-neutral orchestration specification with a runnable reference control plane. It is not defined as a fully distributed production platform and does not require every future hardening or evidence program to be complete.

## Functional v1 boundary

The v1 reference system is expected to include:

- stable Team -> Worker -> optional Specialist -> Capability -> Implementation routing,
- non-lowerable effective-risk controls,
- provider-aware routine fallback and independent provider-diverse verification,
- guarded live provider execution,
- bounded retry, redispatch, circuit breaking, telemetry, and verification controls,
- runnable calibration and evidence tooling,
- model-freshness governance,
- provider-access separation governance,
- reproducible CI and linked-configuration validation, and
- an executable provisional machine-panel evidence path.

Independent human calibration is intentionally tracked as a stronger post-v1 stewardship tier. Its absence must remain visible and it continues to block human-ground-truth quality claims and any authority expansion that policy requires humans to approve.

## Provider access boundary

TEO v1 owns the decision about which implementation should perform the task. It does not own the user's provider login, API-key provisioning, OAuth token lifecycle, subscription management, billing account, service account, delegated identity, connector session, or credential broker.

The user or integrating runtime is responsible for valid access to the selected implementation. API keys, OAuth or subscription-backed sessions, delegated identity, service accounts, connectors, credential brokers, and other provider-supported mechanisms may satisfy that boundary without changing the TEO route.

Reference API-key helpers and the repository-hosted GitHub Actions evidence workflow are convenience harnesses. They are not an architectural requirement and must not be interpreted as evidence that TEO requires API access rather than OAuth, subscription access, or another provider-supported connection method.

Missing credentials or entitlement are execution-boundary conditions. They do not prove that another model was the correct route and must not become model-fitness signals.

See `policy/governance/provider-access-separation.yaml` and `docs/specification/provider-access-boundary.md`.

## Operational evidence paths

### Provisional path available for v1

`policy/verification/verifier-calibration-machine-panel.yaml` defines a provider-diverse provisional study:

- 8 fixed calibration cases,
- 3 blinded machine-panel judge routes,
- 24 machine-panel judgments,
- 3 provider-diverse verifier routes,
- 3 repeated verifier runs per case per route,
- 72 provisional verifier observations,
- 96 planned live calls in total.

This path exercises the complete collection and evaluation machinery while preserving explicit `provisional_machine_panel` evidence semantics.

It cannot establish human ground truth, authorize verifier-quality claims, broaden live execution, or change routing automatically.

The repository-hosted workflow currently provides an optional API-key convenience harness for this study because GitHub Actions does not inherit an end user's interactive provider session. Other runtimes may execute the same collectors through another injected provider connection.

### Human stewardship path

The stronger independent-human path remains active and is tracked through GitHub Issue #75 and `docs/stewardship/community-human-verification.md`.

Community stewardship can complete that layer after v1 without blocking the functional reference release.

## Later runtime work

The following are useful production-hardening extensions but are not required to define TEO v1:

- distributed circuit-state coordination,
- distributed telemetry export,
- streaming,
- source-backed cost attribution,
- route-outcome learning, and
- integrated qualified-human approval workflows.

These belong to post-v1 runtime evolution unless evidence demonstrates that one is required to preserve an existing v1 invariant.

Provider-specific account provisioning and authentication-product development are outside TEO's routing scope rather than missing post-v1 orchestration features.

## Release labels

`reference_operational` means the architecture, runnable control plane, guarded live paths, verification, CI, and provisional evidence machinery are operational. Access to selected models is supplied by the caller or integrating runtime.

`human_calibrated` is a stronger later state reached only after independent blinded human review, empirical collection, residual-risk review, and explicit human acceptance are complete.

## v1.0.0 release contract

The normative human-readable release contract for the first functional-v1 tag is `docs/releases/v1.0.0.md`.

That contract defines the claims, explicit non-claims, authority boundary, release acceptance gates, tag immutability rule, and semantic-version intent for `v1.0.0` and later v1 releases. The `v1.0.0` tag must not be created unless its acceptance gates are satisfied for the exact release candidate.
