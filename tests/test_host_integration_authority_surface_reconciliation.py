from __future__ import annotations

import runpy
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = (
    ROOT
    / "research"
    / "runtime"
    / "host_integration_authority_surface_reconciliation.py"
)
MODULE = runpy.run_path(str(HARNESS))
AuthoritySurfaceError = MODULE["AuthoritySurfaceError"]
derive_authority_surfaces = MODULE["derive_authority_surfaces"]
snapshot_authority_surfaces = MODULE["snapshot_authority_surfaces"]
reconcile_declared_inventory = MODULE["reconcile_declared_inventory"]
verify_authority_snapshot = MODULE["verify_authority_snapshot"]

SOURCE_ROOT = Path("reference/implementations/python/src/teo_reference")


def as_inventory(surfaces):
    return [surface.to_dict() for surface in surfaces]


def write_fixture(root: Path) -> None:
    source = root / SOURCE_ROOT
    source.mkdir(parents=True)
    (source / "config.py").write_text(
        "\n".join(
            [
                'ROUTING = "policy/routing/core/routing.yaml"',
                'RETRY = "policy/runtime/canary-retry.yaml"',
                'CAPABILITIES = "registry/capabilities/capabilities.yaml"',
                'DORMANT = "community/workers/extensions/optional-worker.yaml"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    for relative, content in (
        ("policy/routing/core/routing.yaml", "routing: {}\n"),
        ("policy/runtime/canary-retry.yaml", "status: active\n"),
        ("registry/capabilities/capabilities.yaml", "capabilities: {}\n"),
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def test_current_runtime_derives_known_authority_surfaces() -> None:
    surfaces = derive_authority_surfaces(ROOT)
    by_path = {surface.path: surface for surface in surfaces}

    for path in (
        "policy/routing/core/team-routing.yaml",
        "policy/routing/core/routing.yaml",
        "policy/routing/core/implementation-defaults.yaml",
        "registry/capabilities/capabilities.yaml",
        "registry/models/models.yaml",
        "community/workers/workers.yaml",
        "community/specialists/specialists.yaml",
        "policy/runtime/canary-retry.yaml",
    ):
        assert path in by_path
        assert by_path[path].present is True
        assert by_path[path].sha256 is not None

    dormant = by_path["community/workers/extensions/runtime-worker-overrides.yaml"]
    assert dormant.present is False
    assert dormant.sha256 is None


def test_exact_runtime_derived_inventory_reconciles() -> None:
    surfaces = derive_authority_surfaces(ROOT)
    snapshot = reconcile_declared_inventory(ROOT, as_inventory(surfaces))
    assert snapshot.surfaces == surfaces
    assert len(snapshot.fingerprint) == 64


def test_omitted_runtime_wired_surface_fails_closed() -> None:
    surfaces = derive_authority_surfaces(ROOT)
    declared = as_inventory(surfaces)[1:]
    with pytest.raises(AuthoritySurfaceError, match="missing="):
        reconcile_declared_inventory(ROOT, declared)


def test_unwired_extra_surface_fails_closed(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    surfaces = derive_authority_surfaces(tmp_path)
    extra = tmp_path / "policy/runtime/not-wired.yaml"
    extra.write_text("status: active\n", encoding="utf-8")
    declared = as_inventory(surfaces)
    declared.append(
        {
            "path": "policy/runtime/not-wired.yaml",
            "category": "runtime_policy",
            "present": True,
            "sha256": "0" * 64,
        }
    )
    with pytest.raises(AuthoritySurfaceError, match="extra="):
        reconcile_declared_inventory(tmp_path, declared)


def test_category_tampering_is_rejected() -> None:
    surfaces = derive_authority_surfaces(ROOT)
    declared = as_inventory(surfaces)
    declared[0] = dict(declared[0])
    declared[0]["category"] = "runtime_policy"
    with pytest.raises(AuthoritySurfaceError, match="category mismatch"):
        reconcile_declared_inventory(ROOT, declared)


def test_presence_tampering_of_dormant_surface_is_rejected() -> None:
    surfaces = derive_authority_surfaces(ROOT)
    declared = as_inventory(surfaces)
    index = next(
        index
        for index, entry in enumerate(declared)
        if entry["path"] == "community/workers/extensions/runtime-worker-overrides.yaml"
    )
    declared[index] = dict(declared[index])
    declared[index]["present"] = True
    declared[index]["sha256"] = "0" * 64
    with pytest.raises(AuthoritySurfaceError, match="stale or mismatched"):
        reconcile_declared_inventory(ROOT, declared)


def test_digest_tampering_is_rejected() -> None:
    surfaces = derive_authority_surfaces(ROOT)
    declared = as_inventory(surfaces)
    index = next(index for index, entry in enumerate(declared) if entry["present"])
    declared[index] = dict(declared[index])
    declared[index]["sha256"] = "0" * 64
    with pytest.raises(AuthoritySurfaceError, match="stale or mismatched"):
        reconcile_declared_inventory(ROOT, declared)


@pytest.mark.parametrize(
    "tampered",
    [
        "/policy/runtime/canary-retry.yaml",
        "policy/runtime/../runtime/canary-retry.yaml",
        "policy/runtime/./canary-retry.yaml",
        r"policy\runtime\canary-retry.yaml",
    ],
)
def test_noncanonical_or_escaping_declared_paths_are_rejected(
    tmp_path: Path,
    tampered: str,
) -> None:
    write_fixture(tmp_path)
    declared = as_inventory(derive_authority_surfaces(tmp_path))
    declared[0] = dict(declared[0])
    declared[0]["path"] = tampered
    with pytest.raises(AuthoritySurfaceError):
        reconcile_declared_inventory(tmp_path, declared)


def test_new_runtime_wiring_after_declaration_is_detected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    surfaces = derive_authority_surfaces(tmp_path)
    declared = as_inventory(surfaces)

    source = tmp_path / SOURCE_ROOT / "extra.py"
    source.write_text(
        'NEW_AUTHORITY = "policy/governance/host-control.yaml"\n',
        encoding="utf-8",
    )
    policy = tmp_path / "policy/governance/host-control.yaml"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text("status: active\n", encoding="utf-8")

    with pytest.raises(
        AuthoritySurfaceError,
        match="missing=policy/governance/host-control.yaml",
    ):
        reconcile_declared_inventory(tmp_path, declared)


def test_dormant_authority_path_materialization_invalidates_snapshot(
    tmp_path: Path,
) -> None:
    write_fixture(tmp_path)
    snapshot = snapshot_authority_surfaces(tmp_path)

    dormant = tmp_path / "community/workers/extensions/optional-worker.yaml"
    dormant.parent.mkdir(parents=True, exist_ok=True)
    dormant.write_text("workers: {}\n", encoding="utf-8")

    with pytest.raises(AuthoritySurfaceError, match="snapshot changed"):
        verify_authority_snapshot(tmp_path, snapshot)


def test_present_authority_content_mutation_invalidates_snapshot(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    snapshot = snapshot_authority_surfaces(tmp_path)

    policy = tmp_path / "policy/runtime/canary-retry.yaml"
    policy.write_text("status: changed\n", encoding="utf-8")

    with pytest.raises(AuthoritySurfaceError, match="snapshot changed"):
        verify_authority_snapshot(tmp_path, snapshot)


def test_symlink_escape_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    write_fixture(root)
    outside = tmp_path / "outside.yaml"
    outside.write_text("status: active\n", encoding="utf-8")
    escaped = root / "policy/runtime/escaped.yaml"
    escaped.symlink_to(outside)
    source = root / SOURCE_ROOT / "escape.py"
    source.write_text(
        'ESCAPE = "policy/runtime/escaped.yaml"\n',
        encoding="utf-8",
    )

    with pytest.raises(AuthoritySurfaceError, match="outside the repository root"):
        derive_authority_surfaces(root)


def test_unknown_inventory_fields_are_rejected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    declared = as_inventory(derive_authority_surfaces(tmp_path))
    declared[0] = dict(declared[0])
    declared[0]["allow_widening"] = True

    with pytest.raises(AuthoritySurfaceError, match="fields must be exactly"):
        reconcile_declared_inventory(tmp_path, declared)


def test_duplicate_declared_surface_is_rejected(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    declared = as_inventory(derive_authority_surfaces(tmp_path))
    declared.append(deepcopy(declared[0]))

    with pytest.raises(AuthoritySurfaceError, match="duplicate path"):
        reconcile_declared_inventory(tmp_path, declared)
