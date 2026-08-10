# Platform and Reliability Core Staging

Date: 2026-08-06

## Decision

TEO now has four staged Platform and Reliability specialists:

- Distributed Systems Engineer
- Database Reliability Engineer
- Network Engineer
- Platform Engineer

The matching worker contracts are defined, but the team remains non-routable until capability mappings, provider-diverse fallbacks, conformance datasets, and the approved DevOps and DevSecOps allocation changes are complete.

## Responsibility separation

### Distributed Systems Engineering

Owns distributed invariants, consistency, consensus and coordination, replication, messaging semantics, distributed transactions, partitioning, overload, recovery, and reconciliation.

It does not replace whole-system architecture, database fleet operations, network engineering, or ordinary application implementation.

### Database Reliability Engineering

Owns operational database durability, replication, promotion, backup, restore, schema change, transaction behavior, query plans, capacity, workload isolation, repair, and recovery evidence.

It does not replace Data Engineering. Data Engineering continues to own pipelines, transformations, warehouses, streaming, lineage, and analytical data products.

### Network Engineering

Owns topology, addressing, routing, DNS, load balancing, hybrid connectivity, service networking, segmentation, traffic engineering, capacity, packet diagnosis, and network change control.

Network reachability is not application authorization and does not prove distributed-state or application correctness.

### Platform Engineering

Owns internal platform products, self-service workflows, service catalogs, platform APIs, golden paths, guardrails, tenancy, adoption evidence, support contracts, and lifecycle management.

It does not replace DevOps implementation, Site Reliability Engineering, service-team ownership, or external product management.

## Preservation boundary

The staging manifest records the Git blob SHA for each specialist card and the shared worker-definition file. Regression tests recompute those hashes from repository bytes.

An intentional role change therefore requires the role card, staging manifest, and preservation tests to change together in one reviewed pull request.

## Activation boundary

The following are complete:

- Platform and Reliability Team charter
- four specialist cards
- four worker contracts
- independent verification requirements
- critical human-approval boundaries
- freshness policies
- canonical preservation locks

The following remain pending:

- active team and task routing
- stable capability mappings
- provider-diverse routine fallbacks
- worker and route conformance datasets
- DevOps and DevSecOps allocation changes

Until those gates pass:

- no active task route may select `platform_reliability`
- no active task route may select the four new workers
- the four specialists must not enter the canonical active specialist registry
- existing DevOps and DevSecOps cards remain unchanged

## Evidence-pilot boundary

The regulated evidence pilot remains limited to its existing six specialists. None of these four staged specialists is added to that pilot.

Consequential current-product, service, protocol, or vendor claims still require current authoritative evidence. That requirement does not expand the pilot registry.
