# Post-v1 Hard Audit - 2026-08-10

## Authority

This record documents a TEO hard audit of the post-v1 control plane after completion of repository information-architecture phases R1 through R5.

It is historical audit evidence. It does not replace current policy, registries, runtime code, release contracts, or the immutable `v1.0.0` tag.

## TEO review lenses

- Mission Control
- Principal Engineering
- Architecture
- Platform and Reliability
- Assurance
- Verification
- Configuration and Governance
- Model Freshness
- Repository and CI Integrity

## Executive result

No critical control-plane defect was found in routing order, effective-risk preservation, capability eligibility, provider-diverse fallback, verifier independence, regulated-evidence structure, specialist preservation, current repository topology, or guarded live-execution authority.

The audit identified four actionable metadata or process alignment defects and one non-authoritative repository-hygiene debt.

## Actionable findings

### 1. Active authority retained legacy `public-draft` metadata

Eighteen files that are explicitly loaded as current routing or worker authority still declared `status: public-draft` even though the repository is released in `reference_operational` state and those files are part of the active control plane.

Disposition: corrected to `status: active` without changing routing, worker responsibilities, model selection, fallbacks, verification, risk, or specialist role-card content. Regression tests now enforce the active lifecycle state.

### 2. Changelog lacked the immutable v1.0.0 boundary

The changelog placed released v1 work and later post-v1 repository restructuring under the same `Unreleased` section.

Disposition: created an explicit `v1.0.0` section dated 2026-08-09 and retained later R1 through R5 work under `Unreleased`.

### 3. Post-release main still built as exact package version 1.0.0

At audit time, `main` was twelve commits ahead of the immutable `v1.0.0` tag while `pyproject.toml` still declared version `1.0.0`.

Disposition: current development source now identifies as `1.0.1.dev0`. The immutable tag and stable release package remain `1.0.0`.

### 4. Gemini 3.1 Flash-Lite compatibility note was stale

The registry still described Gemini 3.1 Flash-Lite as retained while Gemini 3.5 Flash-Lite was being evaluated, although Gemini 3.5 Flash-Lite is already the routed economical throughput implementation.

Current Google documentation lists May 7, 2027 as the announced Gemini 3.1 Flash-Lite shutdown date and Gemini 3.5 Flash-Lite as the recommended replacement.

Disposition: refreshed the lifecycle note and registry review date. No route change was required.

## Verified aligned areas

- `v1.0.0` remains the immutable `reference_operational` release boundary.
- Main branch requires pull requests and the `Validate reference router` status check.
- R1 through R5 repository information-architecture migration is complete.
- The active reference configuration resolves 10 teams, 84 workers, and 78 preserved specialists.
- Team -> Worker -> optional Specialist -> Capability -> Implementation ordering remains explicit.
- Effective risk cannot be lowered by caller declaration.
- Preview implementations remain subject to explicit acceptance.
- Routine fallback and independent verification preserve provider diversity where required.
- Guarded live execution remains restricted to explicit `high_volume_simple` work at low or medium effective risk.
- High and critical live execution remain unauthorized.
- The six-card regulated specialist evidence pilot remains bounded and structurally enforced.
- The weekly authority-resolution workflow remains configured for the regulated pilot.
- Provisional machine-panel evidence remains explicitly non-human and non-authoritative for scope or route changes.
- Provider-access mechanism remains separate from model fitness and routing.
- Current first-party model documentation was rechecked for OpenAI GPT-5.6 Sol, Terra, and Luna; Anthropic Claude Fable 5, Opus 5, Sonnet 5, and Haiku 4.5; and Google Gemini 3.6 Flash, Gemini 3.5 Flash-Lite, and Gemini 3.1 Pro Preview. No current route replacement was required.
- The Gemini live adapter does not send the sampling parameters deprecated for the current Gemini API behavior.
- Licensing remains intentionally restrictive until a permanent license is selected.

## Intentionally deferred program

GitHub Issue #75 remains the canonical open program for independent blinded human calibration.

It is not a functional-v1 blocker. It remains required before human-ground-truth verifier-quality claims, policy-governed live-scope expansion, or route changes that require explicit human acceptance.

## Repository hygiene debt

The audit observed 102 retained `agent/*` branches from completed, superseded, or historical workstreams.

These branches are not runtime or policy authority and do not change protected `main`. GitHub Issue #100 tracks a separate branch-hygiene review so deletion occurs only after each branch is mapped to completed, merged, closed, superseded, or intentionally retained work.

## Observability limitation

The audit verified that the weekly regulated-evidence authority-resolution workflow is configured and that normal CI validates evidence structure. The connector used for this audit did not expose general scheduled-run history, so this record does not claim that the latest scheduled network-resolution run completed.

## Final classification

- Architecture and control invariants: aligned
- Routing and runtime behavior: aligned
- Specialist and worker responsibility model: aligned after status metadata correction
- Repository lifecycle topology: aligned
- Model freshness: aligned after one compatibility-note refresh
- Release and process metadata: aligned after remediation
- Human calibration: intentionally incomplete and correctly tracked
- Branch hygiene: non-blocking cleanup debt
