#!/usr/bin/env python3
"""Restore every TEO specialist from the canonical Roxas-Legion source.

The original specialist Markdown is copied byte-for-byte. TEO routing metadata is
appended after the source specification and is never allowed to replace it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


TEAM_LABELS = {
    "mission_control": "Mission Control",
    "planning": "Planning Team",
    "engineering": "Engineering Team",
    "research": "Research Team",
    "review": "Review Team",
    "verification": "Verification Team",
}

REQUIRED_REGISTRY_RULES = (
    "preserve_original_specification_verbatim",
    "teo_allocation_is_additive_only",
    "capability_reduction_requires_explicit_creator_approval",
)

PRESERVATION_POLICY = """# Roxas-Legion Preservation Contract

The Roxas-Legion specialist specifications are the canonical capability definitions for the Legion roles represented in TEO.

1. Each TEO specialist role card must contain the corresponding Roxas-Legion source specification verbatim.
2. TEO may append allocation metadata, routing context, registry links, and verification requirements after the original specification.
3. TEO must never summarize, compress, weaken, generalize, replace, or override the original identity, protocols, capabilities, responsibilities, boundaries, outputs, collaboration rules, examples, or domain doctrine.
4. A capability reduction or behavioral restriction requires explicit written approval from the creator, Sylvester Roxas, together with a versioned rationale and migration record.
5. Validation must fail when a TEO role card does not begin with the complete canonical source file byte-for-byte.

The allocation registry describes where a specialist participates in TEO. It does not redefine what that specialist is capable of doing.
"""


def parse_registry(text: str) -> dict[str, dict[str, object]]:
    entries: dict[str, dict[str, object]] = {}
    current: str | None = None
    list_key: str | None = None
    in_specialists = False

    for raw_line in text.splitlines():
        if raw_line == "specialists:":
            in_specialists = True
            current = None
            list_key = None
            continue
        if not in_specialists:
            continue

        specialist_match = re.match(r"^  ([a-z0-9-]+):\s*$", raw_line)
        if specialist_match:
            current = specialist_match.group(1)
            entries[current] = {"supporting_teams": []}
            list_key = None
            continue

        if current is None:
            continue

        key_match = re.match(r"^    ([a-z_]+):(?:\s*(.*))?$", raw_line)
        if key_match:
            key, value = key_match.groups()
            if key == "supporting_teams":
                entries[current][key] = []
                list_key = key
            else:
                entries[current][key] = (value or "").strip().strip('"\'')
                list_key = None
            continue

        item_match = re.match(r"^\s{4,6}-\s+(.+?)\s*$", raw_line)
        if item_match and list_key:
            value = item_match.group(1).strip().strip('"\'')
            cast_list = entries[current][list_key]
            if not isinstance(cast_list, list):
                raise ValueError(f"Registry field {current}.{list_key} is not a list")
            cast_list.append(value)

    required = {
        "primary_team",
        "supporting_teams",
        "worker_binding",
        "risk_profile",
        "role_card",
    }
    for name, metadata in entries.items():
        missing = required.difference(metadata)
        if missing:
            raise ValueError(f"Registry entry {name} is missing: {sorted(missing)}")

    if not entries:
        raise ValueError("No specialist entries found in registry")
    return entries


def allocation_block(name: str, metadata: dict[str, object]) -> str:
    primary_key = str(metadata["primary_team"])
    supporting_keys = [str(value) for value in metadata["supporting_teams"]]

    try:
        primary = TEAM_LABELS[primary_key]
        supporting = ", ".join(TEAM_LABELS[key] for key in supporting_keys)
    except KeyError as exc:
        raise ValueError(f"Unknown TEO team key for {name}: {exc.args[0]}") from exc

    return (
        "---\n\n"
        "## TEO Allocation\n\n"
        "- **Creator:** Sylvester Roxas\n"
        f"- **Original source:** `Roxas-Legion/specialists/{name}.md`\n"
        f"- **Primary team:** {primary}\n"
        f"- **Supporting teams:** {supporting or 'None'}\n"
        f"- **Worker binding:** `{metadata['worker_binding']}`\n"
        f"- **Risk profile:** {metadata['risk_profile']}\n"
        "- **Canonical allocation:** [`specialists.yaml`](specialists.yaml)\n\n"
        "### Preservation rule\n\n"
        "The original Roxas-Legion specification above is authoritative and must remain intact. "
        "TEO allocation adds routing context only. It must never remove, compress, weaken, "
        "generalize, or override the specialist's identity, protocols, capabilities, "
        "responsibilities, safety boundaries, collaboration rules, outputs, or example tasks.\n"
    )


def join_original_and_allocation(original: str, allocation: str) -> str:
    if original.endswith("\n\n"):
        separator = ""
    elif original.endswith("\n"):
        separator = "\n"
    else:
        separator = "\n\n"
    return original + separator + allocation


def ensure_registry_rules(registry_path: Path, text: str) -> str:
    missing = [rule for rule in REQUIRED_REGISTRY_RULES if f"- {rule}\n" not in text]
    if not missing:
        return text

    marker = "specialists:\n"
    if marker not in text:
        raise ValueError("Registry is missing the specialists section")
    additions = "".join(f"- {rule}\n" for rule in missing)
    updated = text.replace(marker, additions + marker, 1)
    registry_path.write_text(updated, encoding="utf-8")
    return updated


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: restore_legion.py /path/to/Roxas-Legion")

    repository_root = Path.cwd().resolve()
    source_root = Path(sys.argv[1]).resolve()
    source_specialists = source_root / "specialists"
    registry_path = repository_root / "community/specialists/specialists.yaml"

    if not source_specialists.is_dir():
        raise FileNotFoundError(f"Canonical specialist directory not found: {source_specialists}")
    if not registry_path.is_file():
        raise FileNotFoundError(f"TEO specialist registry not found: {registry_path}")

    registry_text = registry_path.read_text(encoding="utf-8")
    entries = parse_registry(registry_text)
    ensure_registry_rules(registry_path, registry_text)

    changed: list[str] = []
    failures: list[str] = []

    for name, metadata in sorted(entries.items()):
        source_path = source_specialists / f"{name}.md"
        if not source_path.is_file():
            failures.append(f"Missing canonical source: {source_path}")
            continue

        destination = repository_root / str(metadata["role_card"])
        original = source_path.read_text(encoding="utf-8")
        final = join_original_and_allocation(original, allocation_block(name, metadata))

        if not final.startswith(original):
            failures.append(f"Prefix preservation failed before writing: {name}")
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        existing = destination.read_text(encoding="utf-8") if destination.exists() else ""
        if existing != final:
            destination.write_text(final, encoding="utf-8")
            changed.append(str(destination.relative_to(repository_root)))

        written = destination.read_text(encoding="utf-8")
        if written[: len(original)] != original:
            failures.append(f"Canonical source differs after writing: {name}")
        if "## TEO Allocation" not in written[len(original) :]:
            failures.append(f"TEO allocation missing after canonical source: {name}")

    policy_path = repository_root / "community/specialists/PRESERVATION.md"
    if not policy_path.exists() or policy_path.read_text(encoding="utf-8") != PRESERVATION_POLICY:
        policy_path.write_text(PRESERVATION_POLICY, encoding="utf-8")
        changed.append(str(policy_path.relative_to(repository_root)))

    if failures:
        print("Preservation validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    source_commit = subprocess.check_output(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True
    ).strip()
    print(f"Validated {len(entries)} specialists against Roxas-Legion {source_commit}.")
    print(f"Changed {len(changed)} paths.")
    for path in changed:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
