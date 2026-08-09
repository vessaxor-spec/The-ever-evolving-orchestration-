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
- reproducible CI and linked-configuration validation, and
- an executable provisional machine-panel evidence path.

Independent human calibration is intentionally tracked as a stronger post-v1 stewardship tier. Its absence must remain visible and it continues to block human-ground-truth quality claims and any authority expansion that policy requires humans to approve.

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

## Release labels

`reference_operational` means the architecture, runnable control plane, guarded live paths, verification, CI, and provisional evidence machinery are operational.

`human_calibrated` is a stronger later state reached only after independent blinded human review, empirical collection, residual-risk review, and explicit human acceptance are complete.
