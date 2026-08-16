# Regulated Specialist Evidence Refresh Cycle 2 - 2026-08-16

## Status

Completed bounded refresh cycle for the existing six-card regulated specialist evidence pilot.

This record is historical validation evidence. It does not authorize registry expansion, change specialist authority, widen runtime scope, or replace the active evidence registry.

## Baseline

- Repository baseline: `bd1bc84a0b41f01ce1fdae086a7d4a46cb60df26`
- Active registry before refresh: `21fed55e972c755e7837c3e2c4af11198d243788`
- Active registry after refresh: `05811a4e147d9d1de2e59bacb26c5c5084373754`
- Pilot specialists: 6
- Consequential claims reviewed: 7
- Specialist cards changed: 0

Cycle 2 was triggered by an evidence-maintenance failure rather than by expiry. The weekly `Specialist Evidence Resolution` run on 2026-08-10 failed closed because the declared ISO authority page returned HTTP 403 to the GitHub-hosted resolver. Re-running the exact failed job on 2026-08-16 reproduced the same ISO-only failure on a different runner. This refresh therefore treats the incident as evidence-maintenance work rather than weakening the resolver or accepting an unresolved authority.

## Authority review

All seven declared tier-1 authorities were re-inspected on 2026-08-16. The six non-ISO authorities continued to support their existing claims. The ISO claim remained substantively supported, but its declared machine-resolution endpoint required an authority move within the same standards body.

### Legal operations

Authority: Administrative Office of the United States Courts  
Source: https://www.uscourts.gov/forms-rules/current-rules-practice-procedure/federal-rules-civil-procedure

Finding: the current Federal Rules of Civil Procedure remain in force and the current rules page records Civil Rules as last amended in 2025. The Rule 37(e) preservation/loss condition carried forward from cycle 1 remains supported; the 2025 civil amendments affect Rules 16 and 26 rather than Rule 37(e).

Disposition: claim reaffirmed.

### Tax strategist

Authority: Internal Revenue Service  
Source: https://www.irs.gov/businesses/small-businesses-self-employed/how-long-should-i-keep-records

Finding: the IRS continues to state that records supporting income, deductions, or credits are generally retained until the applicable period of limitations expires, with longer periods for specified circumstances. The page remains last reviewed or updated on 2026-06-30.

Disposition: claim reaffirmed.

### Loan officer assistant

Authority: Consumer Financial Protection Bureau  
Source: https://www.consumerfinance.gov/rules-policy/regulations/1026/interp-43/

Finding: the official Regulation Z interpretation continues to state that the former universal 43 percent General QM debt-to-income requirement was removed by the 2021 amendments and replaced with annual-percentage-rate thresholds. The claim remains `fast_moving` and receives a 30-day evidence window.

Disposition: claim reaffirmed.

### Compliance auditor

Authority: National Institute of Standards and Technology  
Source: https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20

Finding: NIST Cybersecurity Framework 2.0 remains the published framework. Current NIST guidance continues to define six CSF functions: Govern, Identify, Protect, Detect, Respond, and Recover, with Govern added in CSF 2.0.

Disposition: claim reaffirmed.

### Civil engineer - ASCE 7

Authority: American Society of Civil Engineers  
Source: https://www.asce.org/communities/institutes-and-technical-groups/structural-engineering-institute/asce-7-and-sei-standards

Finding: ASCE continues to identify ASCE/SEI 7-22 as the current edition of its minimum-design-load standard. Supplements and errata remain associated with that edition rather than replacing its edition identity.

Disposition: claim reaffirmed.

### Civil engineer - model-code adoption

Authority: International Code Council  
Source: https://www.iccsafe.org/advocacy/code-adoption-resources/

Finding: ICC continues to state that an authority having jurisdiction adopts a designated model-code edition through law, ordinance, or regulation and may include amendments in the adopting instrument.

Disposition: claim reaffirmed.

### Embedded engineer

Authority: International Organization for Standardization  
Previous source: https://www.iso.org/standard/82075.html  
Current source: https://committee.iso.org/ru/standard/82075.html

Finding: ISO/IEC 9899:2024 remains published as edition 5 of the C programming-language standard, with publication stage 60.60 dated 2024-10-31 and the 2018 edition withdrawn. The previous `www.iso.org` catalog endpoint returned HTTP 403 to the GitHub-runner resolver both on the original scheduled run and on a 2026-08-16 rerun. A controlled GitHub-runner probe using the same request semantics showed the official `committee.iso.org` page for the exact standard returns HTTP 200, while the tested `www.iso.org` variants return 403.

Disposition: authority moved to the official `committee.iso.org` endpoint. Claim statement, applicability, standard identity, source date, verification ownership, and specialist card remain unchanged. Resolver semantics remain fail-closed and unchanged.

## Refresh result

- authorities resolved: 7 of 7
- claims reaffirmed: 6
- claims amended: 0
- authority moves: 1
- authoritative conflicts: 0
- specialist-card changes: 0
- active evidence verification date: 2026-08-16
- slow-moving evidence expiry: 2026-11-14
- fast-moving lending evidence expiry: 2026-09-15

The refresh preserves the existing independent preparer/verifier role separation for every consequential claim.

## Scheduled-resolution finding

The repository's 30-day stable scheduled authority-resolution prerequisite is not satisfied. Before this repair, the only scheduled run on record failed on the ISO endpoint, and the 2026-08-16 rerun reproduced that failure. Formal refresh cycle 2 therefore must not be interpreted as scheduled-resolution stability.

The stability period can begin only after the repaired active registry completes a successful authority-resolution run and subsequent scheduled observations preserve that success for the required period. This event-triggered maintenance cycle does not backdate or waive that requirement.

## Expansion gate disposition

- completed formal refresh cycles: 2 of 2 required
- 30-day stable scheduled authority-resolution gate: not satisfied
- controlled source/card change requirement: satisfied by the cycle-1 claim amendment and cycle-2 authority move
- next risk-tier batch approval: absent
- expansion authorized: false

No broader evidence registry rollout is authorized by completion of cycle 2. The remaining stability and explicit-approval gates stay binding.
