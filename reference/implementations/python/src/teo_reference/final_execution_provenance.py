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
    """Attach validated observed runtime identity from Route-Outcome evidence.

    New Route-Outcome records keep intended and observed identity separate. Historical
    records without the RMI-6 identity extension remain readable, but any explicit
    mismatch or unconfirmed live identity is ineligible for verified final provenance.
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
    intended_provider_family = str(implementation.get("provider_family") or "").strip()
    intended_model = str(implementation.get("model") or "").strip()
    executor_identity_status = implementation.get("identity_status")
    observed_executor = implementation.get("observed_identity")
    if executor_identity_status is not None and executor_identity_status != "match":
        raise ProviderAdapterContractError(
            "Final execution provenance refuses non-matching observed executor identity"
        )
    if isinstance(observed_executor, dict):
        provider_family = str(observed_executor.get("provider_family") or "").strip()
        model = str(observed_executor.get("model") or "").strip()
        configuration_identity_observed = bool(observed_executor.get("configuration_observed"))
    else:
        provider_family = intended_provider_family
        model = intended_model
        configuration_identity_observed = False
    if not provider_family or not model:
        raise ProviderAdapterContractError(
            "Final execution provenance requires provider and model identity"
        )
    if model != outcome.selected_model:
        raise ProviderAdapterContractError(
            "Final outcome selected model does not match observed Route-Outcome active model"
        )

    verifier = active_route["verifier"]
    intended_verifier_model = str(verifier.get("model") or "").strip()
    verifier_identity_status = verifier.get("identity_status")
    observed_verifier = verifier.get("observed_identity")
    if verifier_identity_status is not None and observed_verifier is not None and verifier_identity_status != "match":
        raise ProviderAdapterContractError(
            "Final execution provenance refuses non-matching observed verifier identity"
        )
    if isinstance(observed_verifier, dict):
        observed_verifier_provider_family = str(observed_verifier.get("provider_family") or "").strip()
        observed_verifier_model = str(observed_verifier.get("model") or "").strip()
    else:
        observed_verifier_provider_family = None
        observed_verifier_model = None
    verifier_model = observed_verifier_model or intended_verifier_model
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
        intended_provider_family=intended_provider_family or None,
        intended_model=intended_model or None,
        executor_identity_status=str(executor_identity_status) if executor_identity_status is not None else None,
        observed_verifier_provider_family=observed_verifier_provider_family,
        observed_verifier_model=observed_verifier_model,
        verifier_identity_status=str(verifier_identity_status) if verifier_identity_status is not None else None,
        configuration_identity_observed=configuration_identity_observed,
    )
    if outcome.execution_provenance is not None and outcome.execution_provenance != provenance:
        raise ProviderAdapterContractError(
            "Final execution provenance cannot be replaced by different route evidence"
        )
    return replace(outcome, execution_provenance=provenance)