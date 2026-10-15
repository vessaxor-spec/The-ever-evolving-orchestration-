"""Legacy benchmark compatibility path; implementation is in adapters.evaluation.benchmark_replay."""

from .adapters.evaluation.benchmark_replay import *  # noqa: F401,F403
from .adapters.evaluation.benchmark_replay import (
    _canonical_sha256,
    _load_schema,
    _validate_plan_schema,
    _validate_plan_semantics,
    _safe_fragment,
    _fixture_map,
    _task_for_trial,
    _dispatch_mismatches,
    _assert_dispatch_matches,
    _manifest_candidate,
    _version_context,
    _validate_replay_bundle,
    _resolved_evaluation_fixtures,
)
