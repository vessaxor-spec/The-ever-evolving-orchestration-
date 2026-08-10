from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = REPO_ROOT / "policy" / "governance" / "repository-layout.yaml"
ACTIVATION_PATH = (
    REPO_ROOT / "policy" / "routing" / "activation" / "principal-engineering.yaml"
)


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_all_current_routing_authority_is_active() -> None:
    policy = load_yaml(LAYOUT_PATH)
    routing = policy["contracts"]["policy_routing"]

    for subdir, filenames in routing["canonical_subdirectories"].items():
        for filename in filenames:
            path = REPO_ROOT / "policy" / "routing" / subdir / filename
            record = load_yaml(path)
            assert record.get("status") == "active", (
                f"{path.relative_to(REPO_ROOT)} is current routing authority "
                f"but status={record.get('status')!r}"
            )


def test_worker_authority_respects_direct_and_staged_activation() -> None:
    policy = load_yaml(LAYOUT_PATH)
    workers = policy["contracts"]["community_workers"]
    activation = load_yaml(ACTIVATION_PATH)

    assert activation.get("status") == "active"

    base = REPO_ROOT / "community" / "workers" / "workers.yaml"
    assert load_yaml(base).get("status") == "active"

    loaded_staged = set(activation["loaded_staged_workers"])
    canonical_extensions = {
        f"community/workers/extensions/{filename}"
        for filename in workers["canonical_extensions"]
    }
    assert loaded_staged <= canonical_extensions

    activated_teams = set(activation["activated_new_teams"])

    for relative in sorted(canonical_extensions):
        path = REPO_ROOT / relative
        record = load_yaml(path)

        if relative in loaded_staged:
            assert record.get("status") == "public-draft"
            owning_teams = {
                worker["owning_team"] for worker in record["workers"].values()
            }
            assert owning_teams <= activated_teams
        else:
            assert record.get("status") == "active", (
                f"{relative} is direct current worker authority "
                f"but status={record.get('status')!r}"
            )


def test_v1_release_boundary_is_explicit_in_changelog() -> None:
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    unreleased = changelog.index("## Unreleased")
    v1 = changelog.index("## [1.0.0] - 2026-08-09")

    assert unreleased < v1
    assert "teo-reference-router==1.0.0" in changelog[v1:]
