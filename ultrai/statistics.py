"""
PR 08 — Statistics

Aggregates per-phase statistics (INITIAL, META, ULTRAI) and emits stats.json.
"""

import json
from pathlib import Path
from typing import Dict


class StatisticsError(Exception):
    """Raised when statistics aggregation fails"""
    pass


def generate_statistics(run_id: str) -> Dict:
    """
    Aggregate statistics from artifacts and write runs/<run_id>/stats.json.
    Returns dict with stats content.
    """
    runs_dir = Path(f"runs/{run_id}")

    stats: Dict = {
        "INITIAL": _collect_initial_stats(runs_dir),
        "META": _collect_meta_stats(runs_dir),
        "ULTRAI": _collect_ultrai_stats(runs_dir),
    }

    out_path = runs_dir / "stats.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return stats


def _collect_initial_stats(runs_dir: Path) -> Dict:
    data = {"count": 0, "avg_ms": 0}
    initial_path = runs_dir / "03_initial.json"
    if not initial_path.exists():
        return data
    try:
        with open(initial_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        times = [i.get("ms", 0) for i in items if not i.get("error")]
        data["count"] = len(items)
        data["avg_ms"] = sum(times) // len(times) if times else 0
    except Exception:
        pass
    return data


def _collect_meta_stats(runs_dir: Path) -> Dict:
    data = {"count": 0, "avg_ms": 0}
    meta_path = runs_dir / "04_meta.json"
    if not meta_path.exists():
        return data
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            items = json.load(f)
        times = [i.get("ms", 0) for i in items if not i.get("error")]
        data["count"] = len(items)
        data["avg_ms"] = sum(times) // len(times) if times else 0
    except Exception:
        pass
    return data


def _collect_ultrai_stats(runs_dir: Path) -> Dict:
    data = {"count": 0, "ms": 0}
    ultrai_path = runs_dir / "05_ultrai.json"
    if not ultrai_path.exists():
        return data
    try:
        with open(ultrai_path, "r", encoding="utf-8") as f:
            item = json.load(f)
        data["count"] = 1
        data["ms"] = item.get("ms", 0)
    except Exception:
        pass
    return data


__all__ = ["generate_statistics"]


