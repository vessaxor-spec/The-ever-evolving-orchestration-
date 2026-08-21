from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from ..domain.runtime_binding import RuntimeImplementation


class RuntimeInventoryPort(Protocol):
    """Provider-independent inventory source for concrete runtime implementations.

    Implementations may obtain inventory from local runtimes, configured remote
    endpoints, manifests, process lists, provider list APIs, user declarations,
    or other installation-valid surfaces. Discovery reports what exists; it does
    not grant eligibility, calibration, selection, or execution authority.
    """

    def discover(self) -> Sequence[RuntimeImplementation]:
        """Return the installation's currently known implementation inventory."""
        ...
