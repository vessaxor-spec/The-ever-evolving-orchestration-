from pathlib import Path

from teo_reference.config import ConfigBundle


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TEAM_COUNT = 10
EXPECTED_WORKER_COUNT = 84
EXPECTED_SPECIALIST_COUNT = 82
EXPECTED_MISSION_CONTROL_WORKERS = {
    "orchestration",
    "operations",
    "project_delivery",
    "incident_response",
}


def test_control_plane_roster_matches_current_activation() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    teams = {
        str(worker.get("owning_team"))
        for worker in bundle.worker_registry.values()
    }
    mission_control_workers = {
        name
        for name, worker in bundle.worker_registry.items()
        if worker.get("owning_team") == "mission_control"
    }

    assert len(teams) == EXPECTED_TEAM_COUNT
    assert len(bundle.worker_registry) == EXPECTED_WORKER_COUNT
    assert len(bundle.specialist_registry) == EXPECTED_SPECIALIST_COUNT
    assert mission_control_workers == EXPECTED_MISSION_CONTROL_WORKERS


def test_team_architecture_readme_matches_executable_roster() -> None:
    text = (REPO_ROOT / "community" / "teams" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in (
        "**10 teams**",
        "**84 workers**",
        "**82 specialists**",
        "**4 Mission Control workers**",
    ):
        assert phrase in text

    for worker in EXPECTED_MISSION_CONTROL_WORKERS:
        assert f"`{worker}`" in text

    assert "56 specialist" not in text
    assert "## Core teams" not in text


def test_root_readme_preserves_current_control_plane_truth() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "ten active organizational teams" in text
    assert "82 preserved specialist role cards" in text
    assert "dedicated Mission Control workers for orchestration, operations, project delivery, and incident response" in text
    assert "community/specialists/workforce-expansion-active.yaml" in text

    for worker in EXPECTED_MISSION_CONTROL_WORKERS:
        assert f"`{worker}`" in text


def test_progress_tracker_matches_executable_roster_and_current_priority() -> None:
    text = (
        REPO_ROOT / "docs" / "stewardship" / "progress-tracker.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "| Organizational teams | 10 |",
        "| Workers | 84 |",
        "| Active specialists | 82 |",
        "| Mission Control workers | 4 |",
        "| Latest validated test suite | 546 tests passed |",
        "| Route-outcome evidence | Complete | 100% |",
        "## NOW",
        "### Benchmark and Outcome Lab",
        "## NEXT",
        "### Source-backed cost attribution",
        "### Shadow route evaluation",
        "## LATER",
    ):
        assert phrase in text

    now_section = text.split("## NOW", 1)[1].split("## NEXT", 1)[0]
    assert "### Route-Outcome Evidence Contract" not in now_section
    assert "Direct outcome-to-self-modifying-routing authority" in text
    assert "78 active specialists" not in text


def test_roadmap_links_progress_tracker_and_preserves_current_roster_truth() -> None:
    text = (REPO_ROOT / "docs" / "stewardship" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    assert "[`progress-tracker.md`](progress-tracker.md)" in text
    assert "82 active preserved specialist role cards" in text
    assert "prove all 82 active specialists are deterministically spawnable" in text
    assert "78 preserved specialist" not in text
    assert "78 active specialists" not in text
