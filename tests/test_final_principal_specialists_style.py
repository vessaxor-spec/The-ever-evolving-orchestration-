from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ARTIFACTS = [
    REPO_ROOT / "community" / "specialists" / "cloud-architect.md",
    REPO_ROOT / "community" / "specialists" / "mobile-engineer.md",
    REPO_ROOT / "community" / "specialists" / "compiler-toolchain-engineer.md",
    REPO_ROOT / "community" / "specialists" / "applied-scientist.md",
    REPO_ROOT / "community" / "workers" / "final-principal-expansion-workers.yaml",
    REPO_ROOT / "policy" / "routing" / "final-principal-specialists-staging.yaml",
    REPO_ROOT / "docs" / "methodology" / "final-principal-specialists-staging-2026-08-06.md",
]


def test_final_principal_artifacts_do_not_use_em_dashes() -> None:
    for path in ARTIFACTS:
        assert path.is_file(), f"Missing expected artifact: {path}"
        assert "—" not in path.read_text(encoding="utf-8"), f"Em dash found in {path}"
