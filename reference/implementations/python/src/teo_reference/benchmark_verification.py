"""Legacy benchmark compatibility path; implementation is in adapters.evaluation.benchmark_verification."""

from .adapters.evaluation.benchmark_verification import *  # noqa: F401,F403
from .adapters.evaluation.benchmark_verification import (
    _canonical_sha256,
    _load_schema,
    _validate_schema,
    _validate_panel_semantics,
    _panel_map,
    _active_route,
    _execute_observer,
    _trial_disagreement,
)
