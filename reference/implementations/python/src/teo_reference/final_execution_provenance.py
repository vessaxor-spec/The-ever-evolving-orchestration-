from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .provider_adapter import ProviderAdapterContractError
from .route_outcome import RouteOutcomeRecord
from .schemas import ExecutionProvenance, FinalOutcome


_FINAL_DISPOSITION_TO_OUTCOME_STATUS = {
    "completed": "completed",
    "verification_failed": "failed",
    "awaiting_human": "awaiting_human",
}


def attach_execution_provenance(
    outcome: FinalOutcome,
    route_outcome: RouteOutcomeRecord | dict,
    *,
    repo_root: str | Path,
) -> FinalOutcome:
    """Attach a compact read-only projection of validated Route-Outcome Evidence.

    The projection proves the successful active execution route that TEO observed. It
    never selects a provider, widens authority, or substitutes dispatch intent for
    runtime evidence. Existing FinalOutcome values remain valid without this optional
    projection.
    """

    raw = route_outcome.to_dict() if isinstance(route_outcome, RouteOutcomeRecord) else dict(route_outcome)
    validated = RouteOutcomeRecord.from_dict(raw, repo_root=repo_root).to_dict()

    active_role = validated["active_route_role"]
    if active_role not in {"primary", "fallback"}:
        raise ProviderAdapterContractError(
            "Final execution provenance requires a successful active route"
        )
    active_route = validated["primary_route"] if active_role == "primary" else validated["fallback_route"]
    if not isinstance(active_route, dict) or active_route["execution_status"] != "succeeded":
        raise ProviderAdapterContractError(
            "Final execution provenance active route must have succeeded"
        )

    active_dispatch_id = str(active_route["dispatch_id"])
    if active_dispatch_id != outcome.dispatch_id:
        raise ProviderAdapterContractError(
            "Final outcome dispatch does not match Route-Outcome active dispatch"
        )
    if outcome.execution_status != "succeeded":
        raise ProviderAdapterContractError(
            "Final execution provenance cannot attach to a failed execution outcome"
        )

    implementation = active_route["implementation"]
    provider_family = str(implementation.get("provider_family") or "").strip()
    model = str(implementation.get("model") or "").strip()
    if not provider_family or not model:
        raise ProviderAdapterContractError(
            "Final execution provenance requires provider and model identity"
        )
    if model != outcome.selected_model:
        raise ProviderAdapterContractError(
            "Final outcome selected model does not match Route-Outcome active model"
        )

    verifier = active_route["verifier"]
    verifier_model = str(verifier.get("model") or "").strip()
    if not verifier_model or verifier_model != outcome.verifier_model:
        raise ProviderAdapterContractError(
            "Final outcome verifier model does not match Route-Outcome evidence"
        )

    verification_dispatch_id = validated["provenance"]["verification_dispatch_id"]
    if verification_dispatch_id != outcome.dispatch_id:
        raise ProviderAdapterContractError(
            "Final outcome verification does not match Route-Outcome active dispatch"
        )
    if validated["verification_status"] != outcome.verification_status:
        raise ProviderAdapterContractError(
            "Final outcome verification status does not match Route-Outcome evidence"
        )

    disposition = str(validated["final_disposition"])
    expected_status = _FINAL_DISPOSITION_TO_OUTCOME_STATUS.get(disposition)
    if expected_status is None:
        raise ProviderAdapterContractError(
            "Route-Outcome disposition cannot support verified final execution provenance"
        )
    if outcome.status != expected_status:
        raise ProviderAdapterContractError(
            "Final outcome status does not match Route-Outcome disposition"
        )

    provenance = ExecutionProvenance(
        source="route_outcome",
        route_outcome_id=str(validated["outcome_id"]),
        route_outcome_integrity_sha256=str(validated["integrity_sha256"]),
        active_dispatch_id=active_dispatch_id,
        active_route_role=active_role,
        provider_family=provider_family,
        model=model,
        reasoning_effort=implementation.get("reasoning_effort"),
        verification_dispatch_id=str(verification_dispatch_id),
        final_disposition=disposition,
        fallback_assisted=bool(validated["fallback_assisted"]),
        retry_assisted=bool(validated["retry_assisted"]),
    )
    if outcome.execution_provenance is not None and outcome.execution_provenance != provenance:
        raise ProviderAdapterContractError(
            "Final execution provenance cannot be replaced by different route evidence"
        )
    return replace(outcome, execution_provenance=provenance)
