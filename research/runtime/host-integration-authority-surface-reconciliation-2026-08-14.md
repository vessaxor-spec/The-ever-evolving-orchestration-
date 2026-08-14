# Host Integration authority-surface reconciliation research

Date: 2026-08-14  
Status: non-normative research  
Scope: provider-independent runtime-derived reconciliation of statically wired authority configuration and policy surfaces

## Question

Can a Host Integration declaration be checked against the authority-bearing configuration and policy paths actually wired into the TEO Python reference runtime, so an embedding host cannot silently omit, add, alias, misclassify, or retain stale declarations for those statically discoverable surfaces?

This experiment is deliberately narrower than complete authority-surface discovery. It does not claim that static analysis of string literals discovers every executable hook, dynamic plugin, import mechanism, monkey patch, transitive dependency, dynamically constructed path, or compromised-host bypass.

## Mission Control lenses

- Host Integration Architecture
- Authority and Security Boundaries
- Adversarial Verification
- Program and Progress Governance

## Recalibration

Repository truth at the start of this slice:

- current `main` was `8ec04e64adf024fe1a59b72b33b149a40df06b93`;
- stable release remained `v1.0.0` and the development line remained `1.0.1.dev0`;
- guarded live execution remained limited to `high_volume_simple` at low or medium effective risk;
- `documentation` remained staged with no live-execution authority;
- provider-backed controlled `documentation` replay remained deliberately deferred pending legitimate provider access;
- the Host Integration Contract remained non-normative;
- no open pull request owned this research surface;
- the Host Integration roadmap still listed runtime-derived authority-surface reconciliation as an open pre-normative gate.

The current sequencing therefore permitted provider-independent Host Integration adversarial research but did not permit this work to widen runtime or live authority.

## Diagnosis

The Host Integration roadmap already required integrations to identify files, manifests, hooks, scripts, registries, runtime loaders, and other surfaces capable of changing routing, authorization, capability binding, verification, approval, or finalization behavior.

A hand-maintained inventory is not sufficient evidence by itself. It can omit a newly wired authority file, keep a stale entry after runtime wiring changes, or misrepresent a dormant-but-wired path. Conversely, scanning every file under broad repository directories would confuse repository presence with executable authority wiring.

The bounded research question was therefore whether the current reference runtime can derive a useful authority inventory from the configuration and policy paths it actually wires into executable Python source.

## Candidate boundary

The research harness scans Python source under `reference/implementations/python/src/teo_reference` with the Python AST and extracts exact string literals under these authority-oriented repository prefixes:

- `policy/routing/`
- `policy/runtime/`
- `policy/governance/`
- `registry/capabilities/`
- `registry/models/`
- `community/workers/`
- `community/specialists/`
- `reference/schemas/`

Only canonical repository-relative YAML, YML, or JSON paths are accepted.

For each discovered path the harness records:

- canonical path;
- authority-surface category;
- whether the path currently exists;
- SHA-256 of the exact file bytes when present.

A wired path remains in the inventory even when its file is absent. This dormant-path treatment is intentional: if a future file materializes at a path already wired into runtime loading, that state change must invalidate the earlier snapshot rather than silently acquire authority outside the declaration.

Present surfaces must be regular files inside the repository root and may not be symbolic links.

A host declaration must match the runtime-derived inventory exactly. The harness rejects missing paths, extra unwired paths, category mismatch, presence mismatch, digest mismatch, duplicate entries, unknown fields, noncanonical paths, and stale snapshots.

## Executable adversarial matrix

The executable tests cover:

1. deriving known current routing, registry, worker, specialist, and runtime-policy surfaces from the real reference runtime;
2. accepting an exact runtime-derived inventory;
3. rejecting an omitted runtime-wired surface;
4. rejecting an extra file that exists in an authority directory but is not wired by the tested runtime source;
5. rejecting authority-category tampering;
6. rejecting false materialization claims for a synthetic dormant-but-wired path;
7. rejecting digest tampering;
8. rejecting absolute, parent-traversal, dot-segment, and backslash aliases in declared paths;
9. detecting new authority wiring added to runtime source after declaration;
10. invalidating a snapshot when a dormant wired path later materializes;
11. invalidating a snapshot when a present authority file changes content;
12. rejecting a wired authority path that resolves through a symlink outside the repository root;
13. rejecting unknown declaration fields that could act as widening claims;
14. rejecting duplicate declared surfaces.

The path-normalization parameterization exercises four materially distinct alias classes, so the new test module contributes 17 executable cases.

## Repository-truth finding

The first executable run corrected one assumption about the current repository.

`community/workers/extensions/runtime-worker-overrides.yaml` still exists and remains wired by `ConfigBundle`. Its current content intentionally defines empty `workers` and empty `worker_overrides` while recording the policy that runtime-specific task routes must not mutate the shared documentation worker ordering.

The research inventory therefore correctly treats this file as a **present wired authority surface**, even though its current override payload is empty. This is not evidence of an active routing defect. It is evidence that authority-surface inventory must follow runtime wiring and actual repository state rather than remembered lifecycle assumptions.

Dormant-path behavior is tested separately with a synthetic fixture.

## Red-canary evidence

Reference Implementation CI #643 was intentionally preserved as red evidence for the first research head.

Results before the correction:

- repository layout passed with **525 tracked files**;
- Python compilation passed;
- **840 tests passed**;
- **2 tests failed**.

The failures were research-test defects, not production-control failures:

1. the test incorrectly assumed `community/workers/extensions/runtime-worker-overrides.yaml` was absent, while repository truth showed it is present with an empty override payload;
2. the symlink-escape test over-specified the exact error wording even though the harness correctly failed closed on repository-root escape.

The correction changed only those research assumptions. It did not modify production runtime code, policy, routing, authority, or the fail-closed symlink boundary.

## Green executable verification

Corrected exact head `9cc5694474d310bc50bac1aa342b61f45fb17e10` passed Reference Implementation CI #644 with:

- **842 automated tests passed**;
- **525 tracked-file layout checks**;
- regulated specialist evidence structural validation passed;
- **41 JSON Schemas parsed**;
- linked TEO configuration status `valid` with zero issues;
- the provider-diverse artifact-bound end-to-end reference lifecycle passed.

The controlled provider-backed documentation replay workflow remained skipped, as intended. This research run is not provider-backed live-execution evidence.

After the research result, evidence record, Host Integration roadmap, Progress Tracker, README, and documentation-truth canaries were reconciled, CI #651 passed the complete integrated branch with **842 automated tests**, **526 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end reference lifecycle. CI #644 remains the exact executable research proof; CI #651 establishes the fully reconciled repository/documentation scale for this slice.

## What this supports

For the tested Python reference runtime and the declared static prefixes, the evidence supports the following bounded claim:

> A Host Integration declaration can be reconciled against statically wired authority configuration and policy paths derived from executable runtime source; the tested reconciliation fails closed on omission, unwired additions, path aliasing, category/presence/digest mismatch, later authority wiring, dormant-path materialization, content mutation, duplicate entries, unknown widening fields, and repository-root escape.

This reduces reliance on a parallel hand-maintained source of truth for statically discoverable authority files.

## What this does not support

This slice does **not** prove:

- discovery of dynamically constructed configuration paths;
- discovery or integrity of arbitrary executable hooks, import hooks, plugins, dynamic loaders, monkey patches, or generated code;
- transitive dependency or package identity;
- signer, origin, release, or publisher authenticity for a SHA-256-bound file;
- remote or distributed transport authenticity;
- protection against a compromised host that bypasses TEO-controlled execution surfaces;
- OS, filesystem, namespace, resource, credential, account, or tenant containment;
- that every repository file under an authority-oriented directory is authority-bearing;
- that protecting or reconciling authority files proves downstream action or finalization enforcement;
- normative Host Integration conformance or certification;
- any widening of current TEO live execution.

SHA-256 here is content-integrity evidence only. It is not a signature or trust anchor.

## Decision

**Runtime-derived reconciliation of statically wired authority configuration and policy surfaces is supported at the non-normative research layer.**

The broader authority-surface problem remains open for dynamic executable hooks, plugins/loaders, transitive code identity, and production authenticity. Those residuals must remain explicit in any later Host Integration promotion case.

No new specialist is required. Existing Host Integration architecture, security/authority, verification, and governance lenses cover this responsibility.

This research does not supersede the provider-backed controlled `documentation` replay milestone, does not authorize `documentation`, does not change provider/model routing, and does not make the Host Integration Contract normative.
