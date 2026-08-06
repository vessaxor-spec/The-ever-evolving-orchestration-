from pathlib import Path


README = Path("README.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one {label} block, found {count}")
    return text.replace(old, new, 1)


text = README.read_text(encoding="utf-8")

text = replace_once(
    text,
    """The repository now contains:

- six stable organizational layers: Mission Control, Planning, Engineering, Research, Review, and Verification
- a public roster of 56 preserved specialist role cards
- machine-readable team, worker, specialist, capability, model, fallback, and verification policies
- dedicated Mission Control workers for orchestration, operations, project delivery, and incident response
- dedicated Research Team workers for broad research, user research, market research, analytics, and documentation
- dedicated Review Team workers for code review and compliance review
- deterministic task classification for the active reference routes
- risk elevation from specialist profiles
- provider-aware routine fallbacks
- conditional escalation separated from ordinary availability fallback
- exact configuration-warning baselines
- worker and routing conformance datasets
- a runnable Python reference router with validation, planning, finalization, and audit output
- CI that compiles the implementation, runs the tests, parses schemas, validates linked configuration, and executes the end-to-end example
""",
    """The repository now contains:

- ten active organizational teams: Mission Control, Planning, Engineering, Platform and Reliability, Systems Engineering, Physical Systems, Research, Assurance, Review, and Verification
- a public roster of 78 preserved specialist role cards
- machine-readable team, worker, specialist, capability, model, fallback, and verification policies
- dedicated Mission Control workers for orchestration, operations, project delivery, and incident response
- dedicated Platform and Reliability workers for distributed systems, database reliability, networks, platforms, performance, FinOps, SRE, MLOps, DevOps, and DevSecOps
- dedicated Systems Engineering responsibility for requirements, interfaces, baselines, integration, and lifecycle coherence
- dedicated Physical Systems workers for hardware, embedded, civil, robotics, silicon, aerospace, and manufacturing
- dedicated Research Team workers for broad research, user research, market research, analytics, applied science, and documentation
- dedicated Assurance workers for privacy engineering, functional safety, formal methods, and application security
- dedicated Review Team workers for code review and compliance review
- deterministic task classification for established routes and explicit task types for principal-engineering routes
- specialist-driven risk elevation and qualified human approval for critical effective risk
- provider-aware routine fallbacks and independent provider-diverse verification
- conditional escalation separated from ordinary availability fallback
- exact configuration-warning baselines
- worker and routing conformance datasets, including 27 principal-engineering cases
- a runnable Python reference router with validation, planning, finalization, and audit output
- CI that compiles the implementation, runs the tests, validates regulated evidence, parses schemas, validates linked configuration, and executes the end-to-end example
""",
    "current project state",
)

text = replace_once(
    text,
    """### Engineering Team

The Engineering Team handles implementation, debugging, testing, refactoring, migrations, infrastructure work, and tool execution.

Its workers remain separated by stable responsibility, including backend, frontend, mobile, DevOps, infrastructure, performance, database, data engineering, and AI engineering.

Data engineering builds and maintains data movement and transformation systems. It does not own analytical interpretation merely because the input is data.

### Research Team
""",
    """### Engineering Team

The Engineering Team handles application and product implementation, debugging, testing, refactoring, migrations, language-specific engineering, and tool execution.

Its active responsibilities include backend, frontend, mobile, compiler and toolchain engineering, database application work, data engineering, AI engineering, Rust systems programming, game engineering, and XR development.

Data engineering builds and maintains data movement and transformation systems. It does not own analytical interpretation merely because the input is data.

### Platform and Reliability Team

The Platform and Reliability Team owns the shared technical foundations on which software and services are built and operated.

Its active responsibilities include distributed systems, database reliability, network engineering, platform engineering, performance engineering, FinOps, site reliability, MLOps, DevOps, and DevSecOps.

Platform and Reliability does not absorb application implementation, system requirements, security approval, or incident-command authority.

### Systems Engineering Team

The Systems Engineering Team maintains lifecycle coherence across software, hardware, people, data, processes, facilities, suppliers, and operations.

It owns stakeholder needs, system requirements, allocation, interfaces, technical baselines, integration strategy, change impact, and system verification and validation planning.

Systems engineering is not systems programming. Rust remains an Engineering Team language specialty through the `rust_systems_programming` worker.

### Physical Systems Team

The Physical Systems Team owns engineering whose correctness depends on physical behavior and real-world integration.

Its active responsibilities include hardware, embedded systems, civil engineering, robotics and autonomy, silicon and ASIC engineering, aerospace and satellite systems, manufacturing, and physical integration.

Critical physical-system decisions remain subject to Systems Engineering handoff, independent verification, and qualified human approval.

### Assurance Team

The Assurance Team builds technical assurance requirements, controls, analyses, and evidence for privacy engineering, functional safety, selected formal correctness, and application security.

Assurance does not approve its own consequential claims. Review challenges the argument, Verification checks the evidence, and qualified humans retain critical release and residual-risk authority.

### Research Team
""",
    "team architecture",
)

text = replace_once(
    text,
    """| `release` | release readiness, artifacts, versioning, and rollback confirmation |

Task classification is deterministic in the reference implementation. Ambiguous work must provide an explicit `task_type` instead of allowing the router to invent a route.
""",
    """| `release` | release readiness, artifacts, versioning, and rollback confirmation |

Principal-engineering routes are also active through explicit task types:

| Route | Primary responsibility |
|---|---|
| `cloud_architecture` | cloud placement, landing zones, migration, governance, economics, and exit |
| `mobile_engineering` | production mobile implementation, lifecycle, accessibility, security, and release |
| `compiler_toolchain` | compilers, build systems, targets, compatibility, reproducibility, and provenance |
| `applied_science` | experiments, models, uncertainty, reproducibility, and engineering handoff |
| `systems_requirements` | stakeholder needs, requirements, interfaces, baselines, integration, and V&V strategy |
| `distributed_systems` | distributed invariants, consistency, coordination, replication, and recovery |
| `database_reliability` | database durability, failover, restoration, migration, capacity, and integrity |
| `network_engineering` | routing, DNS, connectivity, segmentation, load balancing, and observability |
| `platform_engineering` | internal platforms, service catalogs, self-service, golden paths, and developer experience |
| `performance_engineering` | workloads, benchmarks, profiling, latency, saturation, capacity, and regressions |
| `finops_engineering` | allocation, unit economics, forecasting, commitments, anomalies, and realized savings |
| `site_reliability` | SLOs, error budgets, readiness, capacity, toil, and reliability learning |
| `mlops` | model and data lineage, deployment, monitoring, retraining, rollback, and retirement |
| `devops_engineering` | delivery, infrastructure automation, deployment, observability, rollback, and recovery |
| `devsecops_engineering` | secure builds, dependencies, secrets, provenance, artifacts, and deployment controls |
| `hardware_engineering` | electronics, PCB, power, signal, thermal, EMC, DFM, DFT, and qualification |
| `robotics_autonomy` | sensing, estimation, planning, control, degraded behavior, and human override |
| `silicon_engineering` | microarchitecture, RTL, timing, CDC, DFT, characterization, and yield |
| `aerospace_systems` | mission, spacecraft, payload, orbit, avionics, environment, launch, and operations |
| `manufacturing_engineering` | process flow, tooling, measurement, capability, yield, controls, and readiness |
| `embedded_engineering` | deterministic firmware, drivers, RTOS behavior, timing, memory, and target evidence |
| `civil_engineering` | governing codes, site conditions, loads, constructability, and inspection evidence |
| `privacy_engineering` | minimization, purpose controls, de-identification, retention, deletion, and privacy evidence |
| `functional_safety` | hazards, safety requirements, integrity, fault evidence, independence, and safety cases |
| `formal_methods` | precise properties, assumptions, model checking, proofs, and implementation linkage |
| `application_security` | application trust, identity, authorization, input, abuse resistance, and remediation |
| `rust_systems_programming` | production Rust, unsafe invariants, FFI, async, targets, and performance |

Established classification remains deterministic. Principal-engineering work requires an explicit `task_type`; ambiguous work is refused instead of being forced into a high-consequence specialty.
""",
    "implemented route table",
)

text = replace_once(
    text,
    """- [`policy/routing/review-routing.yaml`](policy/routing/review-routing.yaml)
- [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml)
- [`models.yaml`](models.yaml)
""",
    """- [`policy/routing/review-routing.yaml`](policy/routing/review-routing.yaml)
- [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml)
- [`policy/routing/principal-engineering-team-routing.yaml`](policy/routing/principal-engineering-team-routing.yaml)
- [`policy/routing/principal-engineering-routing.yaml`](policy/routing/principal-engineering-routing.yaml)
- [`policy/routing/principal-engineering-activation.yaml`](policy/routing/principal-engineering-activation.yaml)
- [`models.yaml`](models.yaml)
""",
    "routing policy index",
)

text = replace_once(
    text,
    """TEO includes **56 public specialist role cards** created by **Sylvester Roxas**.
""",
    """TEO includes **78 public specialist role cards** created by **Sylvester Roxas**.
""",
    "specialist count",
)

text = replace_once(
    text,
    """| Primary team | Specialists |
|---|---:|
| Mission Control | 4 |
| Planning Team | 17 |
| Engineering Team | 13 |
| Research Team | 10 |
| Review Team | 10 |
| Verification Team | 2 |
| **Total** | **56** |
""",
    """| Primary team | Specialists |
|---|---:|
| Mission Control | 4 |
| Planning Team | 17 |
| Engineering Team | 12 |
| Platform and Reliability Team | 10 |
| Systems Engineering Team | 1 |
| Physical Systems Team | 7 |
| Research Team | 11 |
| Assurance Team | 4 |
| Review Team | 10 |
| Verification Team | 2 |
| **Total** | **78** |
""",
    "specialist allocation table",
)

text = replace_once(
    text,
    """The machine-readable allocation registry is available in [`community/specialists/specialists.yaml`](community/specialists/specialists.yaml).
""",
    """The preserved base allocation registry is available in [`community/specialists/specialists.yaml`](community/specialists/specialists.yaml). The active principal-engineering extension is available in [`community/specialists/principal-engineering-active.yaml`](community/specialists/principal-engineering-active.yaml).
""",
    "specialist registry links",
)

text = replace_once(
    text,
    """- compliance worker boundaries and critical-risk human approval
- exact configuration-warning baselines
- provider-aware fallback behavior
""",
    """- compliance worker boundaries and critical-risk human approval
- 27 principal-engineering team, worker, specialist, risk, fallback, verifier, and human-approval cases
- exact configuration-warning baselines
- provider-aware fallback behavior
- refusal of ambiguous implicit principal-specialist routing
""",
    "conformance summary",
)

text = replace_once(
    text,
    """### Phase 2: Core team completion — complete

- Mission Control
- Planning, Engineering, Research, Review, and Verification teams
- standardized team inputs, outputs, escalation, and success criteria
""",
    """### Phase 2: Core team completion - complete

- Mission Control
- six founding teams: Planning, Engineering, Research, Review, Verification, and Mission Control coordination
- four principal-engineering extensions: Platform and Reliability, Systems Engineering, Physical Systems, and Assurance
- standardized team inputs, outputs, escalation, independence, and success criteria
""",
    "phase two status",
)

text = replace_once(
    text,
    """### Current expansion

The active work now expands dedicated workers from the preserved specialist corpus and improves route precision without weakening existing specialists.

Completed dedicated additions include:

- Mission Control: orchestration, operations, project delivery, incident response
- Research Team: broad research, user research, market research, analytics
- Review Team: code review, compliance review

The next dedicated worker will be selected from the remaining exact warning baseline using responsibility uniqueness, routing value, risk, and verification needs rather than arbitrary roster order.

Later runtime work includes provider adapters, live retry execution, circuit breakers, telemetry, cost and latency measurement, and evidence-backed route optimization.
""",
    """### Current expansion

The principal-engineering expansion is active.

Completed additions include:

- 10 accountable teams
- 78 preserved specialist role cards
- 22 newly added principal-grade specialists
- 27 explicit principal-engineering routes
- corrected DevOps, DevSecOps, Embedded, Civil, and Rust allocations
- provider-diverse routine fallback and independent verification
- specialist-driven risk elevation and qualified human approval for critical work
- exact conformance and warning-baseline controls

The next horizon is operational evidence rather than immediate roster growth: provider adapters, live retry execution, circuit breakers, telemetry, cost and latency measurement, qualified-human approval integration, route outcome evaluation, and continued observation of the six-card regulated evidence pilot.
""",
    "current expansion status",
)

README.write_text(text, encoding="utf-8")
print("README principal-engineering reconciliation completed")
