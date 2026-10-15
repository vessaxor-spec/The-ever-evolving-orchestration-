"""Legacy evidence evaluation import path; implementation lives in adapters.evaluation.shadow_evaluation."""

from .adapters.evaluation.shadow_evaluation import *  # noqa: F401,F403
from .adapters.evaluation.shadow_evaluation import (
    _canonical_sha256,
    _load_schema,
    _validate_schema,
    _require_text,
    _authority_denials,
    _validate_input_semantics,
    _validate_recommendation_semantics,
    _validate_verification_semantics,
    _validate_handoff_semantics,
    _ref,
    _outcome_map,
    _cost_map,
    _candidate_map,
    _candidate_outcome_ids,
    _validate_core_bindings,
    _validate_cost_bindings,
    _validate_consequential_chain,
    _expected_refs,
    _metric_map,
    _delta,
    _cost_summary,
    _assert_independent_verifier,
)
