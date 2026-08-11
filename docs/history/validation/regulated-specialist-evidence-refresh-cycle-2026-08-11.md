# Regulated Specialist Evidence Refresh Cycle 1 - 2026-08-11

## Status

Completed bounded refresh cycle for the existing six-card regulated specialist evidence pilot.

This record is historical validation evidence. It does not authorize registry expansion, change specialist authority, widen runtime scope, or replace the active evidence registry.

## Baseline

- Repository baseline: `156ff1dab3832eb13ecac57facfce4f1ffeed414`
- Active registry before refresh: `e1ee365020577e2c7af8b17a75c34caf9273b982`
- Active registry after refresh: `21fed55e972c755e7837c3e2c4af11198d243788`
- Pilot specialists: 6
- Consequential claims reviewed: 7
- Specialist cards changed: 0

The initial pilot created by PR #39 is treated as the evidence seed, not as a completed refresh cycle. The 2026-08-05 regulated-specialist content review predates the evidence pilot and is also not counted as a refresh cycle. This is therefore formal refresh cycle 1.

## Authority review

All seven declared tier-1 authorities were re-resolved and the relevant provision or publication status was re-inspected on 2026-08-11.

### Legal operations

Authority: Administrative Office of the United States Courts  
Source: https://www.uscourts.gov/forms-rules/current-rules-practice-procedure/federal-rules-civil-procedure

Finding: the existing Rule 37(e) claim was incomplete. The current rule requires both loss after a failure to take reasonable preservation steps and that the electronically stored information cannot be restored or replaced through additional discovery.

Disposition: claim amended to include the missing restoration-or-replacement condition. Applicability remains United States federal civil litigation and electronically stored information.

### Tax strategist

Authority: Internal Revenue Service  
Source: https://www.irs.gov/businesses/small-businesses-self-employed/how-long-should-i-keep-records

Finding: the source continues to support retaining records that support income, deductions, or credits until the applicable period of limitations expires, with longer periods for specified circumstances. The page remains last reviewed or updated on 2026-06-30.

Disposition: claim reaffirmed.

### Loan officer assistant

Authority: Consumer Financial Protection Bureau  
Source: https://www.consumerfinance.gov/rules-policy/regulations/1026/interp-43/

Finding: the official Regulation Z interpretation continues to state that the former universal 43 percent General QM debt-to-income threshold was removed by the 2021 amendments and replaced with annual-percentage-rate thresholds. Ability-to-repay requirements remain part of Regulation Z.

Disposition: claim reaffirmed. The claim remains `fast_moving` and receives a 30-day evidence window.

### Compliance auditor

Authority: National Institute of Standards and Technology  
Source: https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20

Finding: NIST Cybersecurity Framework 2.0 remains the published framework and organizes outcomes around six functions, including the added Govern function.

Disposition: claim reaffirmed.

### Civil engineer - ASCE 7

Authority: American Society of Civil Engineers  
Source: https://www.asce.org/communities/institutes-and-technical-groups/structural-engineering-institute/asce-7-and-sei-standards

Finding: ASCE/SEI 7-22 remains identified by ASCE as the current edition. Supplements and errata do not change the edition identity asserted by the claim.

Disposition: claim reaffirmed.

### Civil engineer - model-code adoption

Authority: International Code Council  
Source: https://www.iccsafe.org/advocacy/code-adoption-resources/

Finding: ICC continues to describe legal adoption as action by the relevant governmental authority incorporating a designated code edition, with amendments available through the adopting instrument.

Disposition: claim reaffirmed.

### Embedded engineer

Authority: International Organization for Standardization  
Source: https://www.iso.org/standard/82075.html

Finding: ISO/IEC 9899:2024 remains published as edition 5 of the C language standard, while the 2018 edition is withdrawn.

Disposition: claim reaffirmed.

## Refresh result

- authorities resolved: 7 of 7
- claims reaffirmed: 6
- claims amended: 1
- authority moves: 0
- authoritative conflicts: 0
- specialist-card changes: 0
- active evidence verification date: 2026-08-11
- slow-moving evidence expiry: 2026-11-09
- fast-moving lending evidence expiry: 2026-09-10

The refresh preserves the existing independent preparer/verifier role separation for every consequential claim.

## Auditability remediation

The pilot methodology requires two completed evidence-refresh cycles before expansion can even be considered, but the active registry previously stored only the latest `verified_at` and `expires_at` values. Replacing those fields alone would erase evidence that earlier refreshes occurred.

This cycle therefore introduces an append-only machine-readable refresh record:

`docs/history/validation/regulated-specialist-evidence-refresh-cycle-2026-08-11.json`

It is validated against:

`reference/schemas/specialist-evidence-refresh-cycle.schema.json`

The executable refresh-history validator binds the latest completed cycle to the exact active registry blob, requires full active-claim coverage, reconciles maintenance counts, enforces contiguous cycle sequencing, and refuses premature expansion claims.

## Expansion gate disposition

- completed formal refresh cycles: 1 of 2 required
- 30-day stable scheduled authority-resolution gate: not yet satisfied
- controlled source/card change requirement: satisfied by a claim amendment
- next risk-tier batch approval: absent
- expansion authorized: false

No broader evidence registry rollout is justified by this cycle.
