#!/usr/bin/env python3
"""Measure the static specialist-card payload economics of the candidate Host Integration Contract.

This is non-normative research evidence. It measures only the specialist-card component
of prompt construction. It does not measure provider token usage, inference latency,
or task adherence and therefore cannot close the full context-economics gate by itself.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_SRC = REPO_ROOT / "reference" / "implementations" / "python" / "src"
if str(REFERENCE_SRC) not in sys.path:
    sys.path.insert(0, str(REFERENCE_SRC))

from teo_reference.config import ConfigBundle  # noqa: E402


def _contained_role_card(root: Path, raw_path: str) -> Path:
    specialist_root = (root / "community" / "specialists").resolve()
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(specialist_root)
    except ValueError as exc:
        raise RuntimeError(
            f"Role card escapes the specialist namespace: {raw_path}"
        ) from exc
    if not candidate.is_file():
        raise RuntimeError(f"Role card does not exist: {raw_path}")
    return candidate


def measure_context_economics(root: Path = REPO_ROOT) -> dict[str, Any]:
    """Return provider-neutral byte measurements for active specialist-card projection."""
    root = root.resolve()
    bundle = ConfigBundle.load(root)
    specialists = bundle.specialists.get("specialists")
    if not isinstance(specialists, dict) or not specialists:
        raise RuntimeError("ConfigBundle resolved no active specialists")

    card_rows: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    for specialist_id, metadata in sorted(specialists.items()):
        if not isinstance(metadata, dict):
            raise RuntimeError(f"Invalid specialist metadata: {specialist_id}")
        raw_role_card = metadata.get("role_card")
        if not isinstance(raw_role_card, str) or not raw_role_card:
            raise RuntimeError(f"Specialist has no role_card: {specialist_id}")
        card_path = _contained_role_card(root, raw_role_card)
        if card_path in seen_paths:
            raise RuntimeError(f"Role card is reused by multiple active specialists: {raw_role_card}")
        seen_paths.add(card_path)
        card_rows.append(
            {
                "specialist": str(specialist_id),
                "role_card": raw_role_card,
                "bytes": len(card_path.read_bytes()),
            }
        )

    sizes = [int(row["bytes"]) for row in card_rows]
    naive_bytes = sum(sizes)
    largest = max(card_rows, key=lambda row: int(row["bytes"]))
    smallest = min(card_rows, key=lambda row: int(row["bytes"]))
    mean_bytes = statistics.mean(sizes)
    median_bytes = statistics.median(sizes)
    worst_share = int(largest["bytes"]) / naive_bytes
    mean_share = mean_bytes / naive_bytes

    return {
        "measurement_scope": "active_specialist_role_cards_only",
        "authority": "non_normative_research",
        "active_specialist_count": len(card_rows),
        "naive_all_cards_bytes": naive_bytes,
        "bounded_one_card_mean_bytes": round(mean_bytes, 2),
        "bounded_one_card_median_bytes": round(median_bytes, 2),
        "bounded_one_card_min_bytes": int(smallest["bytes"]),
        "bounded_one_card_max_bytes": int(largest["bytes"]),
        "largest_role_card": largest["role_card"],
        "mean_payload_share_percent": round(mean_share * 100, 4),
        "worst_case_payload_share_percent": round(worst_share * 100, 4),
        "mean_payload_reduction_percent": round((1 - mean_share) * 100, 4),
        "worst_case_payload_reduction_percent": round((1 - worst_share) * 100, 4),
        "unmeasured": [
            "provider_token_usage",
            "provider_inference_latency",
            "task_adherence",
            "non_specialist_prompt_components",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--require-min-reduction-percent",
        type=float,
        default=None,
        help="Exit non-zero if the worst-case one-card reduction is below this research threshold.",
    )
    args = parser.parse_args()

    result = measure_context_economics()
    print(json.dumps(result, indent=2, sort_keys=True))

    threshold = args.require_min_reduction_percent
    if threshold is not None and result["worst_case_payload_reduction_percent"] < threshold:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
