"""
PR 07 — Add-ons Processing

Applies selected add-ons to the final synthesis product and records results.

Reads:
- runs/<run_id>/01_inputs.json (for ADDONS list)
- runs/<run_id>/05_ultrai.json (final synthesis text)

Creates:
- runs/<run_id>/06_final.json (with addOnsApplied)
- Optional export files for certain add-ons (recorded in addOnsApplied)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class AddonsProcessingError(Exception):
    """Raised when add-ons processing fails"""
    pass


EXPORT_ADDONS = {
    # addon_name: (relative filename, generator function name)
    "visualization": "06_visualization.txt",
    "citation_tracking": "06_citations.json",
}


def apply_addons(run_id: str) -> Dict:
    """
    Apply selected add-ons and produce 06_final.json.

    Returns:
        Dict with result (final), status, metadata

    Raises:
        AddonsProcessingError: If required inputs are missing
    """
    runs_dir = Path(f"runs/{run_id}")

    inputs_path = runs_dir / "01_inputs.json"
    if not inputs_path.exists():
        raise AddonsProcessingError(
            f"Missing 01_inputs.json for run_id: {run_id}"
        )

    with open(inputs_path, "r", encoding="utf-8") as f:
        inputs = json.load(f)
        addons: List[str] = inputs.get("ADDONS", [])

    ultrai_path = runs_dir / "05_ultrai.json"
    if not ultrai_path.exists():
        raise AddonsProcessingError(
            f"Missing 05_ultrai.json for run_id: {run_id}"
        )

    with open(ultrai_path, "r", encoding="utf-8") as f:
        ultrai = json.load(f)
        final_text = ultrai.get("text", "")

    add_on_records: List[Dict] = []

    # Process each add-on (minimal processing; record success and paths)
    for addon in addons:
        record = {"name": addon, "ok": True}

        if addon in EXPORT_ADDONS:
            rel_name = EXPORT_ADDONS[addon]
            export_path = runs_dir / rel_name

            try:
                if addon == "visualization":
                    _generate_visualization(export_path, final_text)
                elif addon == "citation_tracking":
                    _generate_citations(export_path, final_text)
                else:
                    # Unknown export add-on mapping
                    record["ok"] = False
                record["path"] = str(export_path)
            except Exception as e:
                record["ok"] = False
                record["error"] = str(e)

        add_on_records.append(record)

    # Build final artifact
    final_result = {
        "round": "FINAL",
        "text": final_text,
        "addOnsApplied": add_on_records,
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "06_final",
        },
    }

    final_path = runs_dir / "06_final.json"
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)

    status = {
        "status": "COMPLETED",
        "details": {
            "add_on_count": len(add_on_records),
            "exports": [
                r.get("path") for r in add_on_records if r.get("path")
            ],
        },
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "06_final",
        },
    }

    # Return a compact response (no separate status file in PR07 template)
    return {
        "result": final_result,
        "status": status["status"],
        "metadata": status["metadata"],
    }


def _generate_visualization(path: Path, text: str) -> None:
    """Create a minimal visualization artifact (text snapshot)."""
    viz = [
        "# UltrAI Visualization Snapshot",
        "",
        "This is a minimal representation of the final synthesis.",
        "",
        text[:2000],  # Truncate to keep it small
        "",
        "-- END --",
    ]
    path.write_text("\n".join(viz), encoding="utf-8")


def _generate_citations(path: Path, text: str) -> None:
    """Emit a placeholder citations file (no extraction, just schema)."""
    # Minimal schema to support future extraction
    citations = {
        "citations": [],
        "note": "No citations extracted in PR07. Placeholder file.",
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(citations, f, indent=2, ensure_ascii=False)
