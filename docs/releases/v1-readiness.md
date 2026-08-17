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

Independent human calibration is an optional post-v1 evidence-enhancement study. Its absence must remain visible whenever a claim could otherwise be mistaken for independently human-validated verifier evidence, but it does not block releases, routing changes, model selection, live-scope decisions, or architectural evolution. Qualified human approval remains mandatory wherever the underlying task or effective-risk policy independently requires it.

## Provider access boundary

TEO v1 owns the decision about which implementation should perform the task. It does not own the user's provider login, API-key provisioning, OAuth token lifecycle, subscription management, billing account, service account, delegated identity, connector session, or credential broker.

The user or integrating runtime is responsible for valid access to the selected implementation. API keys, OAuth or subscription-backed sessions, delegated identity, service accounts, connectors, credential brokers, and other provider-supported mechanisms may satisfy that boundary without changing the TEO route.

Reference API-key helpers and the repository-hosted GitHub Actions evidence workflow are convenience harnesses. They are not an architectural requirement and must not be interpreted as evidence that TEO requires API access rather than OAuth, subscription access, or another provider-supported connection method.

Missing credentials or entitlement are execution-boundary conditions. They do not prove that another model was the correct route and must not become model-fitness signals.

See `policy/governance/provider-access-separation.yaml` and `docs/specification/provider-access-boundary.md`.

## Regulated specialist evidence boundary

The bounded six-card regulated specialist evidence pilot is a post-v1 evidence-maintenance program. Its current maintainability milestone is complete: two formal refresh cycles are preserved in validation history and the executable stability qualification has passed.

The qualification requires five complete clean authority-resolution replays, three independently executed repeatability runs, all 15 governed fail-closed mutation classes to be killed, a controlled authority-move path, and an external-network observation resolving every declared authority. The seven-day source-resolution cadence remains continuous drift monitoring after qualification.

This evidence state does not expand routing or execution authority and does not auto-authorize a larger specialist registry. Any next risk-tier batch requires explicit approval and a separate bounded reviewed change. Test-only one-provider or Codex placeholder lanes may exercise the qualification topology, but they must not be represented as provider-diverse verification.

See `policy/specialists/evidence-pilot.yaml`, `policy/specialists/evidence-stability-qualification.yaml`, and `docs/history/validation/regulated-specialist-evidence-stability-qualification-2026-08-16.md`.

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

### Optional independent human calibration path

The independent-human study is available as optional research and is tracked through GitHub Issue #75 and `docs/stewardship/community-human-verification.md`.

Maintainers may run that study when independently human-labeled comparison would materially strengthen a specific published claim. Participation does not confer approval authority over TEO releases, routing, architecture, or maintainer decisions.

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

`human_calibrated` is an optional stronger evidence state used only when an independent blinded human calibration study has actually been completed and can support specifically scoped human-validation claims.

## v1.0.0 release contract

The normative human-readable release contract for the first functional-v1 tag is `docs/releases/v1.0.0.md`.

That contract defines the claims, explicit non-claims, authority boundary, release acceptance gates, tag immutability rule, and semantic-version intent for `v1.0.0` and later v1 releases. The historical `v1.0.0` tag remains immutable; current governance may evolve through reviewed post-release changes without rewriting that tagged source state.
