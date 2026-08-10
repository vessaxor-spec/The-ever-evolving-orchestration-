# Platform and Reliability Operations Staging

Date: 2026-08-06

## Decision

TEO now has four additional staged Platform and Reliability specialists:

- Performance Engineer
- FinOps Engineer
- Site Reliability Engineer
- MLOps Engineer

Their role cards and worker contracts are complete. They remain non-routable until capability mappings, provider-diverse fallbacks, conformance datasets, and the approved DevOps and DevSecOps allocation changes are implemented.

## Responsibility separation

### Performance Engineering

Owns workload models, benchmark validity, end-to-end latency, profiling, queuing, saturation, capacity, regressions, and cross-stack performance evidence.

QA may execute tests, SRE may own production objectives, and component teams may implement changes. Performance Engineering owns the performance method and conclusion.

### FinOps Engineering

Owns technology cost data, allocation, unit economics, forecasting, anomaly response, commitments, workload placement, tradeoff analysis, and realized-savings verification.

It does not replace Finance, Procurement, Product, Legal, Tax, or technical risk owners.

### Site Reliability Engineering

Owns production SLOs, error budgets, readiness, capacity, dependency resilience, alerting, toil, operational drills, safe change, and systemic reliability learning.

It does not replace DevOps implementation or active Incident Command.

### MLOps Engineering

Owns reproducible ML delivery, lineage, registries, promotion, deployment, monitoring, retraining, rollback, disablement, and retirement.

It does not replace AI Engineering, Data Engineering, Applied Science, Product, or specialist assurance.

## Preservation boundary

The staging manifest records the Git blob SHA for each specialist card and the shared worker-definition file. Regression tests recompute those hashes from repository bytes.

An intentional change requires the role card, staging manifest, and tests to change together in one reviewed pull request.

## Activation boundary

Completed:

- Platform and Reliability Team charter
- four specialist cards
- four worker contracts
- independent verification requirements
- critical human-approval boundaries
- freshness policies
- canonical preservation locks

Pending:

- active routing
- stable capability mappings
- provider-diverse fallbacks
- conformance datasets
- DevOps and DevSecOps allocation changes

Until those gates pass, the specialists and workers remain staged and absent from active routing and the canonical active specialist registry.

## Evidence-pilot boundary

The six-card regulated evidence pilot remains unchanged. None of these staged specialists is added to it.
