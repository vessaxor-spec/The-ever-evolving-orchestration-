# Routing Validation Results

**Run date:** 2026-08-04  
**Case set:** `routing-validation-cases.yaml` version 0.1  
**Baseline policy:** `team-routing.yaml` version 0.1  
**Revised policy:** `team-routing.yaml` version 0.2

## Scope

This run validates policy conformance and dispatch completeness against representative task classes.

It does not evaluate live provider availability, latency, cost, or model output quality.

## Summary

| Run | Accepted | Revised | Rejected | Inconclusive |
|---|---:|---:|---:|---:|
| Baseline | 7 | 4 | 0 | 0 |
| After policy corrections | 11 | 0 | 0 | 0 |

Four cases exposed concrete policy defects. Each defect was corrected with a narrow change, then the full case set was rerun.

## Case results

| Case | Task class | Baseline outcome | Finding | Final outcome | Verification outcome |
|---|---|---|---|---|---|
| RV-001 | architecture design | accepted | Route, ownership, escalation, and independent verification were complete | accepted | high-risk controls present |
| RV-002 | frontend daily coding | accepted | Frontend context correctly overrode the backend default | accepted | build, interaction, and accessibility checks assigned |
| RV-003 | Kubernetes deep debugging | revised | Deployment context still selected backend as the primary worker | accepted | DevOps worker selected with independent high-risk verification |
| RV-004 | frontend repo-wide refactor | revised | Execution worker was fixed to backend regardless of repository context | accepted | Frontend executor selected with phased tests and public behavior comparison |
| RV-005 | security-sensitive review | accepted | Security ownership, independent verification, audit trace, and human approval were present | accepted | critical verification requirements present |
| RV-006 | deep API research | accepted | Research, review, source challenge, and verification paths were complete | accepted | source traceability and contradiction analysis assigned |
| RV-007 | technical documentation | revised | Implementation routing existed, but no team route existed for documentation work | accepted | Research ownership with Engineering, Review, and Verification support |
| RV-008 | destructive database migration | accepted | Database override and high-risk rollback controls were complete | accepted | migration tests, integrity checks, rollback, and independent verification assigned |
| RV-009 | high-volume extraction | revised | Sampled verification was named, but the required verification team field was absent | accepted | Verification Team and sampled review both assigned |
| RV-010 | release | accepted | Release ownership and supporting teams were complete | accepted | release checklist, artifacts, rollback, and audit trace assigned |
| RV-011 | multimodal architecture analysis | accepted | Research ownership and technical implementation follow-up were complete | accepted | source cross-check and repository follow-up assigned |

## Policy corrections

### Context-aware deep debugging

Added worker overrides so frontend, mobile, database, data pipeline, AI system, deployment, and infrastructure failures route to the relevant specialist rather than defaulting unconditionally to backend.

### Context-aware refactor execution

Added execution worker overrides so a repo-wide refactor uses the worker responsible for the affected system.

### Documentation team route

Added an explicit documentation route owned by the Research Team and Documentation worker, with Engineering, Review, and Verification support.

### Complete high-volume verification record

Added the Verification Team to high-volume work while preserving sampled review as the verification method.

## Verification review

Every final route now identifies:

- a responsible team
- a context-appropriate worker
- required supporting roles
- a verification team
- a verification method or control set
- independence requirements where risk is consequential
- enough information to populate the required dispatch record

No unresolved disagreements remained after the full rerun.

## Residual limitations

- This run verifies policy structure, not live implementation performance.
- Provider availability and model capability claims require current registry evidence.
- Actual execution runs may expose additional routing weaknesses.
- Cost and latency were not measured in this run.

Future routing changes should cite a failed case or add a new reproducible case that demonstrates the weakness.
