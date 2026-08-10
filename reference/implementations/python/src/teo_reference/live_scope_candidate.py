"""Compatibility surface for the current live-scope candidate preflight."""

from .live_scope_candidate_v2 import (
    LIVE_SCOPE_EXPANSION_POLICY_PATH,
    LiveScopeCandidateEvaluation,
    LiveScopeCandidateGate,
    LiveScopeExpansionPolicy,
    evaluate_live_scope_candidate,
)

__all__ = [
    "LIVE_SCOPE_EXPANSION_POLICY_PATH",
    "LiveScopeCandidateEvaluation",
    "LiveScopeCandidateGate",
    "LiveScopeExpansionPolicy",
    "evaluate_live_scope_candidate",
]
