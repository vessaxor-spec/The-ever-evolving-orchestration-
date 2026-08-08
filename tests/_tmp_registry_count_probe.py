from pathlib import Path
from teo_reference.config import ConfigBundle


def test_registry_count_probe() -> None:
    root = Path(__file__).resolve().parents[1]
    bundle = ConfigBundle.load(root)
    teams = {str(worker.get("owning_team")) for worker in bundle.worker_registry.values()}
    mission_control_workers = sorted(
        name for name, worker in bundle.worker_registry.items()
        if worker.get("owning_team") == "mission_control"
    )
    raise AssertionError(
        f"REGISTRY_COUNTS teams={len(teams)} workers={len(bundle.worker_registry)} "
        f"specialists={len(bundle.specialist_registry)} mission_control_workers={mission_control_workers}"
    )
