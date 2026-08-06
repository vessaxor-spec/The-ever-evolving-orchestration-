# Regulated Specialist Evidence Pilot

Date: 2026-08-06
Status: pilot

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
9. targeted mutation-kill tests.

### Scheduled authority resolution

`Specialist Evidence Resolution` runs weekly and can also be dispatched manually. It resolves every declared authority URL, rejects failed HTTP responses, and rejects redirection to an undeclared host.

Network-dependent resolution is separated from pull-request CI so temporary authority outages do not make ordinary development nondeterministic. A failed scheduled run is evidence-maintenance work, not permission to continue asserting the affected consequential claim.

## Mutation Contract

The test suite creates controlled weakened copies of the registry. CI must fail when a mutation:

- makes consequential evidence expired;
- removes verification independence or makes the verifier equal the preparer;
- replaces refusal-on-stale behavior with warning-and-continue;
- extends evidence lifetime beyond its volatility-class limit.

These tests prove that the controls are enforced rather than merely documented.

## Evidence Refresh Procedure

Before a claim expires:

1. resolve the declared authority and inspect the located provision;
2. confirm jurisdiction, scope, edition, source-date basis, effective date, and transition rules;
3. update the claim only when the authoritative basis still supports it;
4. record a new verification date and policy-compliant expiry date;
5. use a verifier role distinct from the preparer;
6. run structural, mutation, and authority-resolution validation;
7. submit the refresh through a pull request.

If the authority has moved, replace the URL only after confirming the same authority and provision. If the claim changed, amend the statement and applicability. If support is unavailable or conflicting, preserve refusal or escalation behavior rather than extending the date.

## Expansion Gate

Expansion beyond the six-card pilot requires a separate reviewed decision. At minimum, the pilot must demonstrate:

- two completed evidence-refresh cycles without weakening specialist cards;
- no surviving expiry, independence, or refusal mutations;
- stable scheduled authority resolution for at least 30 days;
- documented maintenance effort and ownership for each claim;
- successful handling of at least one authority move, claim amendment, or intentional canonical-card change;
- explicit approval of the next risk-tier batch.

Passing the initial CI run proves implementation correctness only. It does not prove maintainability and does not authorize a 56-card registry rollout.
