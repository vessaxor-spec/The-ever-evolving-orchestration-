from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class RepositoryConfigurationSourceError(RuntimeError):
    pass


class YamlRepositoryConfigurationAdapter:
    """Filesystem/PyYAML adapter for explicitly named repository configuration files."""

    def load(self, path: Path) -> dict[str, Any]:
        if not path.is_file():
            raise RepositoryConfigurationSourceError(
                f"Required configuration file not found: {path}"
            )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise RepositoryConfigurationSourceError(
                f"Configuration root must be a mapping: {path}"
            )
        return data

    def load_optional(self, path: Path) -> dict[str, Any] | None:
        if not path.is_file():
            return None
        return self.load(path)
