from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

from ..domain.runtime_binding import EligibilityEvidence, RuntimeImplementation


class RuntimeEligibilityEvidenceAdapterError(RuntimeError):
    """Raised when declared eligibility evidence is structurally invalid."""


class DeclaredRuntimeEligibilityEvidenceAdapter:
    """Provider-neutral adapter for already-observed runtime eligibility evidence.

    Missing entries deliberately return empty evidence so mandatory eligibility checks
    fail closed. This adapter does not perform network probes, authentication, routing,
    calibration, selection, or execution.
    """

    def __init__(
        self,
        evidence_by_implementation_id: Mapping[str, EligibilityEvidence] | None = None,
    ) -> None:
        normalized: dict[str, EligibilityEvidence] = {}
        for implementation_id, evidence in dict(
            evidence_by_implementation_id or {}
        ).items():
            key = str(implementation_id).strip()
            if not key:
                raise RuntimeEligibilityEvidenceAdapterError(
                    "eligibility evidence implementation_id cannot be empty"
                )
            if not isinstance(evidence, EligibilityEvidence):
                raise RuntimeEligibilityEvidenceAdapterError(
                    f"eligibility evidence for {key} must be EligibilityEvidence"
                )
            normalized[key] = evidence
        self._evidence = MappingProxyType(normalized)

    def observe(self, implementation: RuntimeImplementation) -> EligibilityEvidence:
        if not isinstance(implementation, RuntimeImplementation):
            raise RuntimeEligibilityEvidenceAdapterError(
                "eligibility evidence observation requires RuntimeImplementation"
            )
        return self._evidence.get(implementation.implementation_id, EligibilityEvidence())
