"""Pure domain policies for the TEO Python reference implementation.

This package must remain free of filesystem, network, provider, runtime, and
configuration-loading dependencies. Application services may depend on these
policies; outer adapters must not leak into them.
"""

from .routing import RISK_PATTERNS, TASK_PATTERNS, RoutingError, assess_risk, classify_task

__all__ = [
    "RISK_PATTERNS",
    "TASK_PATTERNS",
    "RoutingError",
    "assess_risk",
    "classify_task",
]
