# Regulated Specialist Evidence Pilot

Date: 2026-08-06
Status: pilot
Updated: 2026-08-11

## Decision

Evidence-backed freshness begins with six consequential specialist cards:

- `legal-operations`
- `tax-strategist`
- `loan-officer-assistant`
- `compliance-auditor`
- `civil-engineer`
- `embedded-engineer`

No registry-wide rollout is authorized by this pilot. The remaining specialist cards continue under the existing freshness policy until maintainability is demonstrated and a separate pull request explicitly approves expansion.

## Preservation Boundary

The six authoritative specialist cards are not rewritten to host evidence. Their identities, protocols, methods, safety boundaries, responsibilities, outputs, collaborations, and examples remain intact.

The pilot registry records each card path and its canonical Git blob SHA. CI recomputes the blob SHA from the checked-out file and fails if the card changes without an intentional evidence-registry update. This prevents freshness work from silently compressing, generalizing, or weakening specialist capability.

Evidence records are additive and external at `policy/specialists/evidence-pilot.yaml`.

## Evidence Record Contract

Every consequential pilot claim must include:

- a stable claim identifier and substantive statement;
- volatility class;
- jurisdiction and scope applicability;
- a tier-1 declared authority;
- HTTPS source URL, expected authority host, and precise locator;
- a source date with an explicit provenance basis: published, effective, last updated, or observed;
- verification date and expiry date;
- distinct preparer and verifier roles;
- explicit independent-verification status;
- refusal behavior when evidence is stale or unavailable;
- escalation behavior when authoritative sources conflict.

`tools_last_verified` remains useful inventory metadata, but it is not sufficient evidence for consequential use.

## Validation Layers

### Pull-request and main CI

`Reference Implementation CI` performs deterministic validation without depending on external network availability. It checks:

1. exact six-card pilot scope;
2. canonical card preservation;
3. registry structure and required fields;
4. authority tier, declared host, and date provenance;
5. evidence lifetime against the existing volatility policy;
6. non-expiry for consequential use;
7. verification independence;
8. mandatory refusal and conflict behavior;
9. targeted mutation-kill tests;
10. refresh-cycle history structure, sequencing, active-registry binding, claim coverage, maintenance counters, and expansion-gate honesty.

### Scheduled authority resolution

`Specialist Evidence Resolution` runs weekly and can also be dispatched manually. It resolves every declared authority URL, rejects failed HTTP responses, and rejects redirection to an undeclared host.

Network-dependent resolution is separated from pull-request CI so temporary authority outages do not make ordinary development nondeterministic. A failed scheduled run is evidence-maintenance work, not permission to continue asserting the affected consequential claim.

## Mutation Contract

The test suite creates controlled weakened copies of the registry and refresh history. CI must fail when a mutation:

- makes consequential evidence expired;
- removes verification independence or makes the verifier equal the preparer;
- replaces refusal-on-stale behavior with warning-and-continue;
- extends evidence lifetime beyond its volatility-class limit;
- forges the latest refresh record's active-registry blob binding;
- omits an active claim from the latest completed refresh cycle;
- asserts evidence-registry expansion before the declared refresh-cycle and authority-resolution gates are satisfied.

These tests prove that the controls are enforced rather than merely documented.

## Evidence Refresh Procedure

Before a claim expires:

1. resolve the declared authority and inspect the located provision;
2. confirm jurisdiction, scope, edition, source-date basis, effective date, and transition rules;
3. update the claim only when the authoritative basis still supports it;
4. record a new verification date and policy-compliant expiry date;
5. use a verifier role distinct from the preparer;
6. run structural, mutation, refresh-history, and authority-resolution validation;
7. preserve a completed refresh-cycle record under `docs/history/validation/`;
8. submit the refresh through a pull request.

If the authority has moved, replace the URL only after confirming the same authority and provision. If the claim changed, amend the statement and applicability. If support is unavailable or conflicting, preserve refusal or escalation behavior rather than extending the date.

## Refresh-Cycle History

The active registry represents the current evidence state. It must not be used as the sole proof that repeated refreshes occurred because updating `verified_at` and `expires_at` replaces the previous active values.

Every completed formal refresh therefore creates an append-only machine-readable record conforming to `reference/schemas/specialist-evidence-refresh-cycle.schema.json` under `docs/history/validation/`.

A refresh-cycle record must preserve:

- a contiguous cycle sequence and date;
- the repository revision used as the refresh baseline;
- the active registry blob before and after the refresh;
- exact six-card pilot coverage;
- every active claim reviewed during the cycle;
- authority, source-date, resolution, and ownership evidence for each reviewed claim;
- whether a claim was reaffirmed, amended, moved to a new authority, or accompanied by an intentional canonical-card change;
- maintenance counts and conflict outcomes;
- the state of every expansion prerequisite without converting evidence into authority.

The initial creation of the pilot registry is the evidence seed, not a completed refresh cycle. A pre-pilot specialist-content review is also not a refresh cycle. Cycle numbers may advance only when a post-seed refresh follows the procedure above and its completed record passes CI.

Historical refresh records are evidence observations, not active policy. The latest completed record must bind to the current active registry blob and `reviewed_at` date so current evidence cannot silently diverge from the recorded refresh history.

## Expansion Gate

Expansion beyond the six-card pilot requires a separate reviewed decision. The pilot's maintainability milestone is established through the executable qualification defined in `policy/specialists/evidence-stability-qualification.yaml`, not through elapsed calendar time. At minimum, qualification requires:

- two completed evidence-refresh cycles without weakening specialist cards;
- five complete clean authority-resolution replays across every declared pilot claim;
- three independently executed repeatability runs with an identical normalized result;
- all governed expiry, authority, independence, refusal, schema, scope, and specialist-card mutation classes killed;
- a controlled authority-move path that preserves the bound claim statement and verification ownership;
- an external-network observation showing every declared authority resolves through the production evidence resolver;
- documented maintenance effort and ownership for each claim.

The active seven-day source-resolution cadence remains mandatory continuous drift monitoring after qualification. It is not a countdown or a pre-expansion waiting period.

The six-card pilot has completed this current maintainability milestone. Qualification is evidence, not expansion authority. Any registry expansion still requires explicit approval of the next risk-tier batch and a separate bounded reviewed change. Passing qualification, a CI run, or any model-placeholder exercise must never be interpreted as automatic registry expansion.
