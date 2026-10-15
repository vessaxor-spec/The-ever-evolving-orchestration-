"""Legacy benchmark compatibility path; implementation is in adapters.evaluation.benchmark_lab."""

from .adapters.evaluation.benchmark_lab import *  # noqa: F401,F403
from .adapters.evaluation.benchmark_lab import (
    _require_text,
    _canonical_sha256,
    _load_schema,
    _validate_schema,
    _validate_manifest_semantics,
    _read_jsonl,
    _total_duration_ms,
    _token_observation,
    _wilson_interval,
    _fixture_map,
    _outcome_map,
    _candidate_map,
    _validate_fixture_suite,
    _validate_binding_and_outcome,
    _balanced_bindings,
    _candidate_metrics,
    _regression_signals,
)
