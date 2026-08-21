from __future__ import annotations

from dataclasses import dataclass

from ..domain.runtime_binding import (
    AuthorityScope,
    DiscoveredImplementation,
    EligibilityDecision,
    EligibilityEvidence,
    EligibilityRequirements,
    RuntimeImplementation,
    discover,
    evaluate_eligibility,
)
from ..ports.runtime_eligibility import (
    RuntimeEligibilityEvidencePort,
    RuntimeEligibilityEvidenceUnavailable,
)
from ..ports.runtime_inventory import RuntimeInventoryPort


class RuntimeEligibilityEvaluationError(RuntimeError):
    """Raised when eligibility inputs are structurally ambiguous or invalid."""


@dataclass(frozen=True, slots=True)
class RuntimeEligibilityAssessment:
    discovered: DiscoveredImplementation
    evidence: EligibilityEvidence
    decision: EligibilityDecision
    evidence_error: str | None = None

    @property
    def implementation(self) -> RuntimeImplementation:
        return self.discovered.implementation

    @property
    def permitted(self) -> bool:
        return self.decision.permitted


@dataclass(frozen=True, slots=True)
class RuntimeEligibilitySnapshot:
    """Deterministic eligibility result for one inventory snapshot and policy input."""

    assessments: tuple[RuntimeEligibilityAssessment, ...]

    def __post_init__(self) -> None:
        implementation_ids = [
            assessment.implementation.implementation_id
            for assessment in self.assessments
        ]
        if len(implementation_ids) != len(set(implementation_ids)):
            raise RuntimeEligibilityEvaluationError(
                "eligibility snapshot cannot contain duplicate implementation ids"
            )

    @property
    def eligible(self) -> tuple[RuntimeEligibilityAssessment, ...]:
        return tuple(item for item in self.assessments if item.permitted)

    @property
    def rejected(self) -> tuple[RuntimeEligibilityAssessment, ...]:
        return tuple(item for item in self.assessments if not item.permitted)

    def get(self, implementation_id: str) -> RuntimeEligibilityAssessment | None:
        for assessment in self.assessments:
            if assessment.implementation.implementation_id == implementation_id:
                return assessment
        return None


class RuntimeEligibilityService:
    """Evaluate runtime inventory against explicit authority and eligibility policy.

    The service consumes discovery and evidence ports. It does not calibrate, rank,
    select, execute, or widen authority. Evidence-source unavailability becomes empty
    evidence so mandatory policy checks fail closed.
    """

    def __init__(
        self,
        inventory: RuntimeInventoryPort,
        evidence: RuntimeEligibilityEvidencePort,
    ) -> None:
        self._inventory = inventory
        self._evidence = evidence

    def evaluate(
        self,
        *,
        authority: AuthorityScope,
        requirements: EligibilityRequirements,
    ) -> RuntimeEligibilitySnapshot:
        discovered_inventory = tuple(self._inventory.discover())
        by_id: dict[str, RuntimeImplementation] = {}

        for implementation in discovered_inventory:
            if not isinstance(implementation, RuntimeImplementation):
                raise RuntimeEligibilityEvaluationError(
                    "runtime inventory returned a non-RuntimeImplementation value"
                )
            implementation_id = implementation.implementation_id
            if implementation_id in by_id:
                raise RuntimeEligibilityEvaluationError(
                    "runtime eligibility evaluation requires unique implementation ids: "
                    f"{implementation_id}"
                )
            by_id[implementation_id] = implementation

        assessments: list[RuntimeEligibilityAssessment] = []
        for implementation_id in sorted(by_id):
            implementation = by_id[implementation_id]
            discovered = discover(implementation)
            evidence_error: str | None = None
            try:
                eligibility_evidence = self._evidence.observe(implementation)
            except RuntimeEligibilityEvidenceUnavailable as exc:
                eligibility_evidence = EligibilityEvidence()
                evidence_error = str(exc).strip() or "eligibility evidence unavailable"

            if not isinstance(eligibility_evidence, EligibilityEvidence):
                raise RuntimeEligibilityEvaluationError(
                    "eligibility evidence source returned a non-EligibilityEvidence value "
                    f"for {implementation_id}"
                )

            decision = evaluate_eligibility(
                discovered,
                authority=authority,
                requirements=requirements,
                evidence=eligibility_evidence,
            )
            assessments.append(
                RuntimeEligibilityAssessment(
                    discovered=discovered,
                    evidence=eligibility_evidence,
                    decision=decision,
                    evidence_error=evidence_error,
                )
            )

        return RuntimeEligibilitySnapshot(assessments=tuple(assessments))
