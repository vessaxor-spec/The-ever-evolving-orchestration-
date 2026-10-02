# Regulated Specialist Evidence Refresh Cycle 3 - 2026-10-02

## Status

Completed bounded refresh cycle for the existing six-card regulated specialist evidence pilot.

This is evidence-maintenance work triggered by the expired fast-moving lending claim. It does not authorize registry expansion, change specialist authority, widen live runtime scope, or alter routing/model/provider policy.

## Baseline

- Repository baseline: `91e37ec0fe7a056d6d8e7e5ef08b3608e7c60301`
- Active registry before refresh: `05811a4e147d9d1de2e59bacb26c5c5084373754`
- Active registry after refresh: `14367c6febe6b0d63d94dd616bc76b041f687aba`
- Pilot specialists: 6
- Consequential claims reviewed: 7
- Specialist cards changed: 0
- Claims amended: 0
- Authority moves: 0
- Authority conflicts: 0

The fast-moving `lending-us-general-qm-dti` evidence expired on 2026-09-15. Scheduled authority-resolution runs on 2026-09-21 and 2026-09-28 therefore failed closed, and current Reference Implementation CI also correctly rejected the stale evidence. Cycle 3 refreshes the full pilot rather than extending one date in isolation.

## Authority review

All seven declared tier-1 authorities were re-inspected on 2026-10-02. Existing claim statements and applicability remain supported.

### Legal operations — Federal Rule of Civil Procedure 37(e)

Authority: Administrative Office of the United States Courts  
Source: https://www.uscourts.gov/forms-rules/current-rules-practice-procedure/federal-rules-civil-procedure

The current official Federal Rules of Civil Procedure are the December 1, 2025 rules. Rule 37(e) continues to apply when electronically stored information that should have been preserved in anticipation or conduct of litigation is lost because reasonable preservation steps were not taken and the information cannot be restored or replaced through additional discovery.

Disposition: claim reaffirmed. Observed source date advanced to 2026-10-02.

### Tax strategist — federal income-tax record retention

Authority: Internal Revenue Service  
Source: https://www.irs.gov/businesses/small-businesses-self-employed/how-long-should-i-keep-records

The IRS continues to state that records supporting income, deductions, or credits generally must be retained until the applicable period of limitations expires, with longer retention periods for specified circumstances.

Disposition: claim reaffirmed. The declared last-updated source date remains 2026-06-30.

### Loan officer assistant — General Qualified Mortgage DTI rule

Authority: Consumer Financial Protection Bureau  
Source: https://www.consumerfinance.gov/rules-policy/regulations/1026/interp-43/

The current Regulation Z interpretation continues to state that the 2021 General QM amendments removed the former universal 43 percent debt-to-income requirement and replaced it with the annual-percentage-rate thresholds in § 1026.43(e)(2)(vi), while ability-to-repay requirements remain applicable.

Disposition: fast-moving claim reaffirmed. The effective source date remains 2021-03-01. New verification date is 2026-10-02 and expiry is 2026-11-01, preserving the 30-day maximum evidence age.

### Compliance auditor — NIST Cybersecurity Framework 2.0

Authority: National Institute of Standards and Technology  
Source: https://www.nist.gov/publications/nist-cybersecurity-framework-csf-20

NIST continues to publish CSF 2.0 as NIST CSWP 29, published February 26, 2024. Current NIST material identifies six Functions — Govern, Identify, Protect, Detect, Respond, and Recover — with Govern added in CSF 2.0.

Disposition: claim reaffirmed.

### Civil engineer — ASCE/SEI 7

Authority: American Society of Civil Engineers  
Source: https://www.asce.org/communities/institutes-and-technical-groups/structural-engineering-institute/asce-7-and-sei-standards

ASCE continues to identify ASCE/SEI 7-22 as the Current Edition of its minimum-design-load standard.

Disposition: claim reaffirmed. Observed source date advanced to 2026-10-02.

### Civil engineer — model-code adoption

Authority: International Code Council  
Source: https://www.iccsafe.org/advocacy/code-adoption-resources/

ICC continues to state that a governmental authority having jurisdiction adopts a designated model code through ordinance, regulation, or law and may include local changes or amendments in the adopting law.

Disposition: claim reaffirmed. Observed source date advanced to 2026-10-02.

### Embedded engineer — C language standard

Authority: International Organization for Standardization  
Source: https://committee.iso.org/ru/standard/82075.html

ISO continues to list ISO/IEC 9899:2024 as published Edition 5, publication stage 60.60 dated 2024-10-31, with ISO/IEC 9899:2018 shown as withdrawn.

Disposition: claim reaffirmed.

## Refresh result

- authorities reviewed/resolved: 7 of 7
- claims reaffirmed: 7
- claims amended: 0
- authority moves: 0
- authoritative conflicts: 0
- specialist-card changes: 0
- active evidence verification date: 2026-10-02
- slow-moving evidence expiry: 2026-12-31
- fast-moving lending evidence expiry: 2026-11-01

Existing preparer/verifier role separation remains unchanged for every consequential claim.

## Expansion gate disposition

This maintenance refresh does not reopen or grant registry-expansion authority.

- completed formal refresh cycles: 3
- executable stability qualification: previously satisfied
- seven-day source-resolution cadence: remains mandatory continuous drift monitoring
- controlled change in this cycle: none
- next risk-tier batch approval: absent
- expansion authorized: false

A passing refresh or CI run is evidence of current pilot maintenance only.
