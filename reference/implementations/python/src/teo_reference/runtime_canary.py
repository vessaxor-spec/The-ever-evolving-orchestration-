"""Backward-compatible runtime path; implementation lives in adapters.runtime.canary."""

from .adapters.runtime.canary import *  # noqa: F401,F403
from .adapters.runtime.canary import _copy_task_for_redispatch, _execute_dispatch, _execute_with_retry, _circuit_block_delta, _telemetry_observer
