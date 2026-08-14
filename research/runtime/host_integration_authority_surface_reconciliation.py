from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

SOURCE_ROOT = Path("reference/implementations/python/src/teo_reference")

_AUTHORITY_PREFIXES = (
    ("policy/routing/", "routing_policy"),
    ("policy/runtime/", "runtime_policy"),
    ("policy/governance/", "governance_policy"),
    ("registry/capabilities/", "capability_registry"),
    ("registry/models/", "model_registry"),
    ("community/workers/", "worker_registry"),
    ("community/specialists/", "specialist_registry"),
    ("reference/schemas/", "schema_boundary"),
)

_ALLOWED_SUFFIXES = (".yaml", ".yml", ".json")


class AuthoritySurfaceError(ValueError):
    """Raised when a declared or derived authority surface is ambiguous or stale."""


@dataclass(frozen=True, slots=True)
class AuthoritySurface:
    path: str
    category: str
    present: bool
    sha256: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "category": self.category,
            "present": self.present,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class AuthoritySurfaceSnapshot:
    fingerprint: str
    surfaces: tuple[AuthoritySurface, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "fingerprint": self.fingerprint,
            "surfaces": [surface.to_dict() for surface in self.surfaces],
        }


def _category_for(path: str) -> str | None:
    for prefix, category in _AUTHORITY_PREFIXES:
        if path.startswith(prefix):
            return category
    return None


def _normalize_path(value: Any, *, field_name: str = "path") -> str:
    if not isinstance(value, str) or not value:
        raise AuthoritySurfaceError(f"{field_name} must be a non-empty string")
    if "\\" in value:
        raise AuthoritySurfaceError(
            f"{field_name} must use repository-relative POSIX separators"
        )
    candidate = PurePosixPath(value)
    normalized = candidate.as_posix()
    if candidate.is_absolute() or ".." in candidate.parts:
        raise AuthoritySurfaceError(f"{field_name} must remain repository-relative")
    if normalized != value or normalized in {"", "."}:
        raise AuthoritySurfaceError(
            f"{field_name} must be canonical repository-relative POSIX text"
        )
    if _category_for(normalized) is None:
        raise AuthoritySurfaceError(
            f"{field_name} is outside the research authority-surface prefixes"
        )
    if not normalized.endswith(_ALLOWED_SUFFIXES):
        raise AuthoritySurfaceError(
            f"{field_name} must identify a YAML or JSON authority surface"
        )
    return normalized


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_surface(repo_root: Path, relative_path: str) -> tuple[bool, str | None]:
    root = repo_root.resolve(strict=True)
    candidate = root / relative_path
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise AuthoritySurfaceError(
            f"authority surface escapes the repository root: {relative_path}"
        )
    if not candidate.exists():
        return False, None
    if candidate.is_symlink():
        raise AuthoritySurfaceError(
            f"authority surface must not be a symbolic link: {relative_path}"
        )
    if not candidate.is_file():
        raise AuthoritySurfaceError(
            f"authority surface must be a regular file when present: {relative_path}"
        )
    strict = candidate.resolve(strict=True)
    if not strict.is_relative_to(root):
        raise AuthoritySurfaceError(
            f"authority surface resolves outside the repository root: {relative_path}"
        )
    return True, _sha256(strict)


def _runtime_wired_paths(repo_root: Path) -> set[str]:
    source_root = repo_root / SOURCE_ROOT
    if not source_root.is_dir():
        raise AuthoritySurfaceError(
            f"reference runtime source root not found: {source_root}"
        )

    paths: set[str] = set()
    for source in sorted(source_root.rglob("*.py")):
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError, UnicodeDecodeError) as exc:
            raise AuthoritySurfaceError(
                f"cannot inspect runtime source {source}: {exc}"
            ) from exc
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            value = node.value
            category = _category_for(value)
            if category is None or not value.endswith(_ALLOWED_SUFFIXES):
                continue
            paths.add(_normalize_path(value))
    if not paths:
        raise AuthoritySurfaceError(
            "reference runtime exposed no authority configuration surfaces"
        )
    return paths


def derive_authority_surfaces(
    repo_root: str | Path,
) -> tuple[AuthoritySurface, ...]:
    """Derive runtime-wired authority configuration/policy surfaces from source.

    Both present and dormant paths are retained. A dormant path is a literal authority
    path wired into the reference runtime whose file does not currently exist. Recording
    dormant wiring prevents a later file addition from silently becoming authority outside
    the declared host inventory.
    """

    root = Path(repo_root)
    surfaces: list[AuthoritySurface] = []
    for relative_path in sorted(_runtime_wired_paths(root)):
        present, digest = _resolve_surface(root, relative_path)
        category = _category_for(relative_path)
        assert category is not None
        surfaces.append(
            AuthoritySurface(
                path=relative_path,
                category=category,
                present=present,
                sha256=digest,
            )
        )
    return tuple(surfaces)


def _surface_fingerprint(surfaces: Iterable[AuthoritySurface]) -> str:
    payload = [surface.to_dict() for surface in surfaces]
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def snapshot_authority_surfaces(
    repo_root: str | Path,
) -> AuthoritySurfaceSnapshot:
    surfaces = derive_authority_surfaces(repo_root)
    return AuthoritySurfaceSnapshot(
        fingerprint=_surface_fingerprint(surfaces),
        surfaces=surfaces,
    )


def _require_digest(value: Any, *, present: bool) -> str | None:
    if not present:
        if value is not None:
            raise AuthoritySurfaceError(
                "dormant authority surface must declare sha256 as null"
            )
        return None
    if not isinstance(value, str):
        raise AuthoritySurfaceError(
            "present authority surface must declare a SHA-256 digest"
        )
    if len(value) != 64 or value.lower() != value:
        raise AuthoritySurfaceError(
            "authority surface SHA-256 must be 64 lowercase hexadecimal characters"
        )
    try:
        int(value, 16)
    except ValueError as exc:
        raise AuthoritySurfaceError(
            "authority surface SHA-256 must be hexadecimal"
        ) from exc
    return value


def _parse_declared_inventory(
    declared_inventory: Iterable[Mapping[str, Any]],
) -> tuple[AuthoritySurface, ...]:
    surfaces: list[AuthoritySurface] = []
    seen: set[str] = set()
    required_fields = {"path", "category", "present", "sha256"}

    for entry in declared_inventory:
        if not isinstance(entry, Mapping):
            raise AuthoritySurfaceError(
                "declared authority inventory entries must be mappings"
            )
        actual = set(entry)
        if actual != required_fields:
            raise AuthoritySurfaceError(
                "declared authority inventory entry fields must be exactly "
                + ", ".join(sorted(required_fields))
            )
        path = _normalize_path(entry.get("path"))
        if path in seen:
            raise AuthoritySurfaceError(
                f"declared authority inventory contains duplicate path: {path}"
            )
        seen.add(path)
        expected_category = _category_for(path)
        category = entry.get("category")
        if category != expected_category:
            raise AuthoritySurfaceError(
                f"declared authority category mismatch for {path}: "
                f"expected {expected_category}, got {category}"
            )
        present = entry.get("present")
        if type(present) is not bool:
            raise AuthoritySurfaceError(
                f"declared authority presence must be boolean for {path}"
            )
        digest = _require_digest(entry.get("sha256"), present=present)
        surfaces.append(
            AuthoritySurface(
                path=path,
                category=str(category),
                present=present,
                sha256=digest,
            )
        )

    return tuple(sorted(surfaces, key=lambda surface: surface.path))


def reconcile_declared_inventory(
    repo_root: str | Path,
    declared_inventory: Iterable[Mapping[str, Any]],
) -> AuthoritySurfaceSnapshot:
    """Require a host declaration to exactly match runtime-derived authority surfaces."""

    derived = derive_authority_surfaces(repo_root)
    declared = _parse_declared_inventory(declared_inventory)

    derived_by_path = {surface.path: surface for surface in derived}
    declared_by_path = {surface.path: surface for surface in declared}

    missing = sorted(set(derived_by_path) - set(declared_by_path))
    extra = sorted(set(declared_by_path) - set(derived_by_path))
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("extra=" + ",".join(extra))
        raise AuthoritySurfaceError(
            "declared authority inventory does not match runtime-derived surfaces: "
            + "; ".join(details)
        )

    mismatched = [
        path
        for path in sorted(derived_by_path)
        if derived_by_path[path] != declared_by_path[path]
    ]
    if mismatched:
        raise AuthoritySurfaceError(
            "declared authority inventory is stale or mismatched: "
            + ",".join(mismatched)
        )

    return AuthoritySurfaceSnapshot(
        fingerprint=_surface_fingerprint(derived),
        surfaces=derived,
    )


def verify_authority_snapshot(
    repo_root: str | Path,
    snapshot: AuthoritySurfaceSnapshot,
) -> None:
    """Fail if runtime wiring, presence, or authority content changed since snapshot."""

    if not isinstance(snapshot, AuthoritySurfaceSnapshot):
        raise AuthoritySurfaceError(
            "authority snapshot must use the research snapshot type"
        )
    current = snapshot_authority_surfaces(repo_root)
    if current != snapshot:
        raise AuthoritySurfaceError(
            "runtime-derived authority surface snapshot changed after reconciliation"
        )
