# T6D Verifier Calibration Core Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) tracking.

**Goal:** Move deterministic verifier-calibration implementation behind `teo_reference.adapters.evaluation` without behavior, CLI or import-identity changes.

**Architecture:** Source-preserving relocation of a single module, adapter dependency adjusted from level 1 to level 3, old module becomes identity-preserving shim with `__main__` delegation. Remain on an isolated GitHub feature branch.

**Tech Stack:** Python 3.11, pytest, GitHub Actions, existing TEO evidence/configuration schemas.

**Spec:** [approved scoped design](t6d-verifier-calibration-core-design-2026-11-07.md), canonical `docs/architecture/python-clean-architecture-migration.md`, Issue #197.

## Global Constraints

- Zero routing, risk, authority, policy, model/version, provider access, guarded runtime or live-scope changes.
- No modification of empirical calibration, machine panel, human review, staged replay, CLI workflows, package-root exports or schema.
- Reuse existing `verification_adapter` contract. Preserve all public/private symbol identity and `python -m` compatibility.
- Baseline `833f37ba0462892eeca009a00072bd1c01037e7a` verified with merged-main CI #1036 (1,189 tests).

## Review Focus

- Legacy `main` may disappear when converting to re-export shim: CLI and imports must remain callable.
- Source `__name__` module ownership changes: dataclass/function identity must be common to old/new import paths.
- Private helper imports may be used by other calibration modules: preserve them as aliases.
- Relative import from nested module may resolve incorrectly: test actual import and semantic corpus behavior.
- Calibration evidence readiness must remain non-authorizing, even for complete data: existing mutation tests and full CI are the gate.

---

### Task 1: Red tests and preflight

**Files:**
- Create `tests/test_verifier_calibration_namespace_boundary.py`

**Interfaces:**
- Expected `teo_reference.adapters.evaluation.verifier_calibration` to exist post-extraction.
- Existing public entry: `teo_reference.verifier_calibration`, `main(argv: list[str] | None) -> int`.

- [ ] Step 1: Write namespace test asserting `find_spec(...)` resolves and then identity-equivalence for all exported symbols, private aliases included; assert old file owns no functions/classes.
- [ ] Step 2: Test actual CLI `--help` and existing policy/gold `--policy ... --gold ...` output equivalence from legacy and concrete `python -m`; verify successful JSON has deterministic summary fields.
- [ ] Step 3: AST check concrete relative imports only `...verification_adapter`; no cycles into the legacy facade.
- [ ] Step 4: Commit test-only branch head. Wait for GitHub exact-head CI and record expected RED failure `test_namespace_module_exists` asserting missing module, not syntax/import error.

### Task 2: Source-preserving module extraction

**Files:**
- Add `reference/implementations/python/src/teo_reference/adapters/evaluation/verifier_calibration.py`
- Replace `reference/implementations/python/src/teo_reference/verifier_calibration.py` with shim.

**Interfaces:**
- Moved existing core `CalibrationPolicy`, `GoldCalibrationCase`, `CalibrationObservation`, `CalibrationError`, `evaluate_calibration`, `assess_evidence_readiness`, `main` and private helpers unchanged.
- Only concrete import change: `from .verification_adapter` to `from ...verification_adapter`.

- [ ] Step 1: Preserve implementation body byte-for-byte after import adjustment.
- [ ] Step 2: Shim wildcard re-export plus explicit private helper aliases; legacy `if __name__ == "__main__": raise SystemExit(main())` retained.
- [ ] Step 3: Commit, trigger exact-head full CI; confirm new tests and existing calibration suites pass.
- [ ] Step 4: If any failures, diagnose before repair. Do not weaken assertions.

### Task 3: Review and integration

- [ ] Step 1: Independently inspect exact scoped diff and retained CLI/authority/verified-evidence behavior.
- [ ] Step 2: Check no policy, provider, live execution, empirical, machine panel or route implementation files changed.
- [ ] Step 3: Prepare qualified PR with expected-head proof and full CI; merge only under approved #197 scope and repository governance.
- [ ] Step 4: Verify merged-main full CI; reconcile canonical Progress Tracker, roadmap and architecture plan in a separate bounded stewardship PR and test.
- [ ] Step 5: Leave remaining T6D groups and Tranche 7 unstarted.
