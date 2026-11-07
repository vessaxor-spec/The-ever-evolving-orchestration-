# T6D Deterministic Verifier Calibration Core: Bounded Design

**Status:** approved implementation slice, 2026-11-07. **Authority:** [Issue #197](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues/197), subordinate to [the canonical migration plan](python-clean-architecture-migration.md). **Baseline:** `main@833f37ba0462892eeca009a00072bd1c01037e7a`, CI #1036 PASS.

## Intent and scope

Move exactly the deterministic verifier-calibration policy, gold-case validation, observation evaluation, evidence-readiness calculations and CLI implementation from `teo_reference/verifier_calibration.py` to `teo_reference/adapters/evaluation/verifier_calibration.py`. Retain the old path as a compatibility facade for existing imports and direct `python -m teo_reference.verifier_calibration` usage. Preserve public and private symbol identities, input/output/error semantics and fail-closed authority invariants.

## Approaches and decision

1. **Selected:** source-preserving single-module move with compatibility shim, separate CLI entrypoint. Minimal blast radius and easy revert.
2. All five verifier calibration modules together. Rejected: empirical provider collection, human-review blinding and machine panel private imports multiply risk.
3. Combined calibration + live-scope migration. Rejected: crosses guarded runtime, provider access, staged-only authority and evidence boundaries.

## Implemented boundary

The concrete module's only package dependency remains the existing verification adapter contract, now via `from ...verification_adapter import ...`. There is no new policy authority, registry, provider connection, dependency, feature or schema. The legacy module re-exports all symbols, including private helper aliases, and retains a `__main__` delegation to the concrete `main`. Keep the concrete module runnable as `python -m` too.

## Non-goals and gates

No changes to empirical calibration, reporting, blinded human review, machine panel, staged live-scope candidate/replay, runtime model binding, policy, routing, verifier assignment, quality claims or live scope. High/critical authorization remains closed.

Regression requirements: observe failing namespace-resolution test before implementation; prove legacy/concrete identity equivalence, no legacy class/function implementations, dependency direction, and CLI help and representative deterministic gold-summary JSON output on both paths. Run full canonical CI with evidence/schema/configuration/provider-diverse E2E; review exact diff and verify merged-main CI. Only after this qualification should canonical Progress Tracker and migration plan reflect the tranche.