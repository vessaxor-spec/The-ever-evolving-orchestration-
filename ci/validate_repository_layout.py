#!/usr/bin/env python3
"""Validate tracked repository paths against TEO repository layout governance."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

import yaml


class LayoutPolicyError(RuntimeError):
    """Raised when the repository layout policy is structurally invalid."""


def _mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LayoutPolicyError(f"{context} must be a mapping")
    return value


def _string_list(value: Any, context: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise LayoutPolicyError(f"{context} must be a non-empty-string list")
    return value


def load_policy(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    policy = _mapping(data, str(path))
    if policy.get("status") != "active":
        raise LayoutPolicyError(f"Repository layout policy must be active: {path}")

    root = _mapping(policy.get("root"), "root")
    _string_list(root.get("allowed_files"), "root.allowed_files")
    _string_list(root.get("allowed_directories"), "root.allowed_directories")
    _mapping(root.get("temporary_exceptions"), "root.temporary_exceptions")

    contracts = _mapping(policy.get("contracts"), "contracts")
    required_contracts = {
        "policy_routing",
        "community_workers",
        "docs_methodology",
        "docs_history",
        "research",
        "specialists",
        "capsules",
        "reference_datasets",
    }
    missing = sorted(required_contracts.difference(contracts))
    if missing:
        raise LayoutPolicyError("Missing repository layout contracts: " + ", ".join(missing))
    return policy


def collect_tracked_files(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    return sorted(
        path
        for path in result.stdout.decode("utf-8").split("\0")
        if path
    )


def _direct_files(paths: set[PurePosixPath], directory: str) -> set[str]:
    base = PurePosixPath(directory)
    depth = len(base.parts) + 1
    return {
        path.name
        for path in paths
        if len(path.parts) == depth and path.parts[: len(base.parts)] == base.parts
    }


def _validate_declared_direct_files(
    paths: set[PurePosixPath],
    *,
    directory: str,
    allowed: set[str],
    label: str,
) -> list[str]:
    errors: list[str] = []
    for filename in sorted(_direct_files(paths, directory)):
        if filename not in allowed:
            errors.append(
                f"{label} contains undeclared direct file {directory}/{filename}; "
                "place it in the canonical subdirectory or update repository layout governance intentionally"
            )
    return errors


def validate_layout(tracked_files: Iterable[str], policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    paths = {PurePosixPath(path) for path in tracked_files}

    root = _mapping(policy["root"], "root")
    allowed_root_files = set(_string_list(root["allowed_files"], "root.allowed_files"))
    root_exceptions = set(_mapping(root["temporary_exceptions"], "root.temporary_exceptions"))
    allowed_top_level = set(
        _string_list(root["allowed_directories"], "root.allowed_directories")
    )

    for path in sorted(paths, key=str):
        if len(path.parts) == 1:
            if path.name not in allowed_root_files and path.name not in root_exceptions:
                errors.append(
                    f"Undeclared root file {path}; root is reserved for durable entrypoints and build metadata"
                )
            continue
        if path.parts[0] not in allowed_top_level:
            errors.append(
                f"Unknown top-level zone {path.parts[0]} from {path}; add a canonical zone only through governance"
            )

    contracts = _mapping(policy["contracts"], "contracts")

    routing = _mapping(contracts["policy_routing"], "contracts.policy_routing")
    routing_path = str(routing["path"])
    routing_allowed = set(
        _string_list(routing["active_direct_files"], "policy_routing.active_direct_files")
    ) | set(
        _string_list(
            routing["temporary_direct_exceptions"],
            "policy_routing.temporary_direct_exceptions",
        )
    )
    for filename in sorted(_direct_files(paths, routing_path)):
        if filename.endswith(".yaml") and filename not in routing_allowed:
            errors.append(
                f"Undeclared direct routing policy {routing_path}/{filename}; "
                "new direct YAML policy requires an intentional layout-policy update"
            )
    routing_subdirs = set(
        _string_list(routing["approved_subdirectories"], "policy_routing.approved_subdirectories")
    )
    routing_contents = _mapping(
        routing.get("canonical_subdirectories"),
        "policy_routing.canonical_subdirectories",
    )
    if set(routing_contents) != routing_subdirs:
        raise LayoutPolicyError(
            "policy_routing.canonical_subdirectories must exactly match approved_subdirectories"
        )
    allowed_routing_files = {
        subdir: set(_string_list(filenames, f"policy_routing.canonical_subdirectories.{subdir}"))
        for subdir, filenames in routing_contents.items()
    }
    for path in sorted(paths, key=str):
        if len(path.parts) >= 4 and path.parts[:2] == ("policy", "routing"):
            subdir = path.parts[2]
            if subdir not in routing_subdirs:
                errors.append(f"Unknown routing subdirectory {subdir} from {path}")
                continue
            if len(path.parts) != 4:
                errors.append(f"Nested routing path is not allowed below {subdir}: {path}")
                continue
            if path.name not in allowed_routing_files[subdir]:
                errors.append(
                    f"Undeclared routing file policy/routing/{subdir}/{path.name}; "
                    "update routing topology governance intentionally before adding policy"
                )

    workers = _mapping(contracts["community_workers"], "contracts.community_workers")
    worker_path = str(workers["path"])
    worker_allowed = set(
        _string_list(workers["canonical_direct_files"], "community_workers.canonical_direct_files")
    ) | set(
        _string_list(
            workers["temporary_direct_extensions"],
            "community_workers.temporary_direct_extensions",
        )
    )
    errors.extend(
        _validate_declared_direct_files(
            paths,
            directory=worker_path,
            allowed=worker_allowed,
            label="Worker namespace",
        )
    )
    worker_subdirs = set(
        _string_list(workers["approved_subdirectories"], "community_workers.approved_subdirectories")
    )
    for path in sorted(paths, key=str):
        if len(path.parts) >= 4 and path.parts[:2] == ("community", "workers"):
            if path.parts[2] not in worker_subdirs:
                errors.append(f"Unknown worker subdirectory {path.parts[2]} from {path}")

    methodology = _mapping(contracts["docs_methodology"], "contracts.docs_methodology")
    methodology_path = str(methodology["path"])
    methodology_allowed = set(
        _string_list(
            methodology["evergreen_direct_files"],
            "docs_methodology.evergreen_direct_files",
        )
    ) | set(
        _string_list(
            methodology["temporary_history_exceptions"],
            "docs_methodology.temporary_history_exceptions",
        )
    )
    errors.extend(
        _validate_declared_direct_files(
            paths,
            directory=methodology_path,
            allowed=methodology_allowed,
            label="Methodology namespace",
        )
    )
    for path in sorted(paths, key=str):
        if len(path.parts) >= 4 and path.parts[:2] == ("docs", "methodology"):
            errors.append(
                f"Methodology namespace is intentionally flat in R1; undeclared nested path {path}"
            )

    history = _mapping(contracts["docs_history"], "contracts.docs_history")
    history_path = str(history["path"])
    history_allowed = set(
        _string_list(history["canonical_direct_files"], "docs_history.canonical_direct_files")
    ) | set(
        _string_list(
            history["temporary_direct_exceptions"],
            "docs_history.temporary_direct_exceptions",
        )
    )
    errors.extend(
        _validate_declared_direct_files(
            paths,
            directory=history_path,
            allowed=history_allowed,
            label="History namespace",
        )
    )
    history_subdirs = set(
        _string_list(history["approved_subdirectories"], "docs_history.approved_subdirectories")
    )
    for path in sorted(paths, key=str):
        if len(path.parts) >= 4 and path.parts[:2] == ("docs", "history"):
            if path.parts[2] not in history_subdirs:
                errors.append(f"Unknown history subdirectory {path.parts[2]} from {path}")

    research = _mapping(contracts["research"], "contracts.research")
    research_exceptions = set(
        _string_list(
            research["temporary_direct_exceptions"],
            "research.temporary_direct_exceptions",
        )
    )
    research_subdirs = set(
        _string_list(research["approved_subdirectories"], "research.approved_subdirectories")
    )
    for path in sorted(paths, key=str):
        if not path.parts or path.parts[0] != "research":
            continue
        if len(path.parts) == 2 and path.name not in research_exceptions:
            errors.append(
                f"Undeclared direct research file {path}; new research must be topic-scoped"
            )
        elif len(path.parts) >= 3 and path.parts[1] not in research_subdirs:
            errors.append(f"Unknown research subdirectory {path.parts[1]} from {path}")

    specialists = _mapping(contracts["specialists"], "contracts.specialists")
    specialist_path = PurePosixPath(str(specialists["path"]))
    if specialists.get("flat_identity_namespace") is not True:
        raise LayoutPolicyError("specialists.flat_identity_namespace must remain true")
    for path in sorted(paths, key=str):
        if path.parts[: len(specialist_path.parts)] != specialist_path.parts:
            continue
        if len(path.parts) > len(specialist_path.parts) + 1:
            errors.append(
                f"Nested specialist path {path}; specialist identity must remain independent of team allocation"
            )

    capsules = _mapping(contracts["capsules"], "contracts.capsules")
    capsule_path = PurePosixPath(str(capsules["path"]))
    capsule_index = str(capsules["index_file"])
    capsule_pattern = re.compile(str(capsules["filename_pattern"]))
    for path in sorted(paths, key=str):
        if path.parts[: len(capsule_path.parts)] != capsule_path.parts:
            continue
        if len(path.parts) > len(capsule_path.parts) + 1:
            errors.append(f"Nested capsule path {path}; accepted capsules use a flat immutable namespace")
            continue
        if path.name != capsule_index and not capsule_pattern.fullmatch(path.name):
            errors.append(f"Capsule filename violates naming contract: {path}")

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate TEO repository layout governance")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--policy",
        default="policy/governance/repository-layout.yaml",
        help="Repository-relative layout policy path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    policy_path = repo_root / args.policy
    try:
        policy = load_policy(policy_path)
        tracked_files = collect_tracked_files(repo_root)
        errors = validate_layout(tracked_files, policy)
    except (LayoutPolicyError, OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
        print(f"Repository layout validation could not run: {exc}")
        return 2

    if errors:
        print("Repository layout validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Repository layout valid: {len(tracked_files)} tracked files checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
