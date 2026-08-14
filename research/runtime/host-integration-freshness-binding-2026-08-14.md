# Host Integration Freshness Binding Research

**Date:** 2026-08-14  
**Status:** executable non-normative research  
**Scope:** TEO-side classification of pinned or vendorized host-integration snapshots against authority-owned executable repository truth

## Question

Can an external host prove whether its pinned TEO integration state is current, explicitly compatible, superseded with an update available, known stale/unsupported, or mismatched without trusting a host-supplied freshness label?

## Research claim

A TEO-side freshness authority can derive one exact integration binding from executable repository truth and classify a host snapshot only against an authority-owned current binding plus explicitly recorded historical bindings.

The binding includes:

- stable release identifier supplied by the TEO-side authority context;
- runtime package version from `pyproject.toml`;
- exact 40-character repository revision;
- runtime-derived authority-surface fingerprint from the existing Host Integration authority-surface research;
- effective Team routing fingerprint;
- effective implementation-routing fingerprint;
- effective Worker registry fingerprint;
- effective Specialist registry fingerprint;
- effective Capability registry fingerprint;
- effective model-policy registry fingerprint;
- effective model-evidence registry fingerprint;
- one executable-composition identifier derived from the runtime version, authority-surface fingerprint, and effective component fingerprints.

The host does not determine the freshness disposition. A host may state a claimed status, but the TEO-side assessment recomputes the status from exact binding evidence and records whether the claim matches.

## Classification semantics

- `PINNED_CURRENT`: exact match to the authority-owned current binding.
- `PINNED_COMPATIBLE`: exact match to a historical binding explicitly recorded as compatible.
- `UPDATE_AVAILABLE`: exact match to a historical binding explicitly recorded as supported but superseded.
- `STALE_UNSUPPORTED`: exact match to a historical binding explicitly recorded as unsupported.
- `MISMATCHED`: any unrecognized snapshot or any snapshot whose revision is mixed with different release, policy, registry, authority-surface, model, or executable-composition evidence.

Unknown states fail closed as `MISMATCHED`. The research does not infer compatibility from version-number proximity, timestamps, file counts, host claims, or semantic similarity.

## Adversarial cases

The test matrix includes:

- exact current binding;
- exact compatible historical binding;
- exact update-available historical binding;
- exact unsupported historical binding;
- unknown revision claiming compatibility;
- current revision with altered release or runtime version;
- current revision with altered authority-surface fingerprint;
- current revision with altered Team, implementation, Worker, Specialist, Capability, model, or model-evidence fingerprints;
- current revision with altered executable-composition identity;
- known historical revision combined with a different component fingerprint;
- host claim that contradicts the authority-owned disposition;
- missing binding fields;
- unknown or widening fields such as a host-injected `freshness_state` inside the bound snapshot;
- malformed digest or revision values;
- duplicate historical revision records;
- malformed historical binding types;
- attempted historical reuse of the current revision;
- typed YAML date scalars versus ordinary strings with the same visible text.

## Executable evidence

Reference Implementation CI #676 was intentionally retained as red evidence. Repository layout and Python compilation passed, while pytest reported **863 passed and 26 errors** because the first fingerprint encoder assumed every effective `ConfigBundle` value was directly JSON serializable. A YAML date scalar loaded as `datetime.date(2026, 2, 16)` falsified that assumption.

The correction did not flatten values with `str()`. The freshness harness now canonicalizes supported configuration values into deterministic typed JSON data, explicitly type-tagging dates and datetimes so a typed YAML date cannot collide with an ordinary string containing the same characters. Unsupported value types fail closed. The Security and Authority Boundaries review also added an explicit type guard for historical catalog bindings.

Corrected head `7c16324c9f1fbf620df605d7b5bbde90bc9efed5` passed Reference Implementation CI #678 with **891 tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end reference lifecycle.

This is evidence only for the exact local research classification slice. It does not prove a production compatibility catalog or remote freshness authenticity.

## Authority boundary

This slice is research only. It does not:

- create a normative Host Integration schema;
- authorize or refuse live execution;
- change routing, specialist selection, model/provider selection, retry, recovery, verification, finalization, or qualified-human authority;
- define which historical TEO revisions are actually compatible in production;
- fetch or trust remote Git state;
- create automatic upgrade authority;
- make a host's claimed freshness state authoritative.

Any production compatibility catalog would itself be an authority surface and would require governed provenance, review, update/revocation semantics, downgrade resistance, and appropriate independent verification.

## Residual limits

This research does not close:

- remote repository/signature authenticity;
- package provenance or transitive-code identity;
- dynamic executable-hook/plugin discovery;
- distributed or restart-durable freshness coordination;
- downgrade attacks against a production compatibility catalog;
- compromised-host bypass;
- automated update or migration correctness;
- provider-backed token/latency/adherence evidence.

## Roadmap relationship

This slice narrows two Host Integration promotion gates:

- registry freshness; and
- integration freshness state.

The exact local classification semantics and stale/mismatch detection slice are now executable. Production compatibility-catalog provenance, remote authenticity, downgrade resistance, and distributed freshness coordination remain open. This evidence does not authorize normative promotion of the Host Integration Contract.
