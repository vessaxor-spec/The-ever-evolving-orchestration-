from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


SPECIALIST_SELECTION_POLICY = "policy/routing/core/specialist-selection-policy.yaml"


class SpecialistSelectionPolicyLoadError(RuntimeError):
    pass


class YamlSpecialistSelectionPolicyAdapter:
    """Filesystem/YAML adapter for the specialist selection policy."""

    def __init__(self, root: str | Path):
        self._root = Path(root)

    def load(self) -> dict[str, Any]:
        path = self._root / SPECIALIST_SELECTION_POLICY
        if not path.is_file():
            raise SpecialistSelectionPolicyLoadError(
                f"Specialist selection policy not found: {path}"
            )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SpecialistSelectionPolicyLoadError(
                "Specialist selection policy root must be a mapping"
            )
        return data
