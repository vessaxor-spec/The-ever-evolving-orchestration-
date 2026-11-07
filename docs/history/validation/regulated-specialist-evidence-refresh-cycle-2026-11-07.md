# Regulated Specialist Evidence Refresh Cycle 4 - 2026-11-07

## Scope and diagnosis

Bounded **six-card, seven-claim** refresh only, restoring the evidence gate that correctly failed closed in [scheduled authority resolution #13](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/actions/runs/41449174772) on 2026-11-02. The specific expiry was `lending-us-general-qm-dti` at 2026-11-01. No specialist cards, capability scope, routing, models, verification policy, or production permissions changed.

Baseline: `main@4ce3c731d9e9ab770d094418d9e4298067818086`. Active registry before: `14367c6febe6b0d63d94dd616bc76b041f687aba`; after: `2a56343fa37af318fdea69cdb7e3166c51d6bf71`. The original claim statements and applicability have not been expanded. This is **evidence maintenance**, not authority to extend production live execution or expand the six-card pilot.

## Tier-1 source review (2026-11-07)

| Claim | Official authority and provision | Result |
| --- | --- | --- |
| `legal-us-frcp-37e-preservation` | [US Courts, current Federal Rules of Civil Procedure](https://www.uscourts.gov/forms-rules/current-rules-practice-procedure/federal-rules-civil-procedure), Rule 37(e) (last amended 2025) | Reaffirmed: loss of ESI that should have been preserved due to failure to take reasonable steps, unrecoverable by discovery |
| `tax-us-record-retention` | [IRS record-retention guidance](https://www.irs.gov/businesses/small-businesses-self-employed/how-long-should-i-keep-records), periods of limitation | Reaffirmed: retain tax-supporting records until relevant limitations period, subject to longer special cases |
| `lending-us-general-qm-dti` | [CFPB Regulation Z official interpretation, comment 43(e)(2)-1](https://www.consumerfinance.gov/rules-policy/regulations/1026/interp-43/) | Reaffirmed: 2021 General QM amendments removed universal 43% DTI and introduced APR thresholds; March 1 2021 effective date, October 1 2022 mandatory-compliance date |
| `compliance-nist-csf-2-govern` | [NIST CSF 2.0, CSWP 29](https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20) and [NIST CSF FAQ](https://www.nist.gov/cyberframework/faqs) | Reaffirmed: six functions including Govern |
| `civil-asce-7-current-publication` | [ASCE SEI standards: Current Edition](https://www.asce.org/communities/institutes-and-technical-groups/structural-engineering-institute/asce-7-and-sei-standards) | Reaffirmed: ASCE/SEI 7-22 remains current published edition; specific jurisdiction adoption still separate |
| `civil-model-code-adoption` | [ICC Code Adoption Resources, FAQs](https://www.iccsafe.org/advocacy/code-adoption-resources/) | Reaffirmed: AHJ enactment by law incorporating designated code and local changes |
| `embedded-c-language-current-standard` | [ISO/IEC 9899:2024 official standard page](https://committee.iso.org/ru/standard/82075.html) | Reaffirmed: published fifth edition of C, 2018 edition withdrawn |

The declared source-date **basis** is retained. Observed source dates advance to the actual reinspection date; the source publication/effective dates for other claims remain unchanged. Prepared/verified role bindings remain the existing distinct governance roles. This record is a source-and-contract review, **not an assertion of additional named human sign-off**.

## Controls and post-change gates

- All seven `verified_at` values: 2026-11-07.
- Lending expiry: **2026-12-07** (30 days). Other slow-moving expiry: **2027-02-05** (90 days).
- Seven statements reaffirmed, zero amendments, zero authority moves, zero conflicts, zero specialist-card changes.
- Stale/unavailable refusal, conflicts escalation, independent role separation and six-card pilot boundary unchanged.
- No expansion authorized. Cycle four is the latest append-only history record and its after SHA binds the active registry.
- Verify exact-head Reference Implementation CI (including mutation gates, refresh-history binding and provider-diverse E2E), then rerun scheduled authority resolution and qualify merged-main CI. Never treat previous green CI runs as current freshness evidence.
