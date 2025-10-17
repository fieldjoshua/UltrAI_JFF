"""
PR 09 — Final Delivery

Verifies all artifacts exist and delivers the complete UltrAI synthesis report.

User receives:
- 05_ultrai.json (UltrAI synthesis - the main result)
- 03_initial.json (R1 INITIAL drafts)
- 04_meta.json (R2 META revisions)
- 06_final.json (Add-ons applied)
- stats.json (Performance statistics)

Reads:
- runs/<run_id>/05_ultrai.json (synthesis)
- runs/<run_id>/03_initial.json (initial drafts)
- runs/<run_id>/04_meta.json (meta drafts)
- runs/<run_id>/06_final.json (final with add-ons)
- runs/<run_id>/stats.json (statistics)

Creates:
- runs/<run_id>/delivery.json (delivery manifest with paths and status)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class FinalDeliveryError(Exception):
    """Raised when final delivery fails"""
    pass


# Required artifacts for delivery
REQUIRED_ARTIFACTS = [
    "05_ultrai.json",   # Main synthesis result
    "03_initial.json",  # R1 INITIAL responses
    "04_meta.json",     # R2 META revisions
    "06_final.json",    # Add-ons applied
    "stats.json",       # Performance statistics
]

# Optional artifacts (exported files from add-ons)
OPTIONAL_ARTIFACTS = [
    "06_visualization.txt",
    "06_citations.json",
]


def deliver_results(run_id: str) -> Dict:
    """
    Verify all artifacts exist and create delivery manifest.

    Returns:
        Dict with delivery manifest containing:
        - artifacts: List of delivered artifact paths
        - missing: List of missing required artifacts (if any)
        - optional: List of optional artifacts found
        - status: COMPLETED or INCOMPLETE

    Raises:
        FinalDeliveryError: If critical artifacts are missing
    """
    runs_dir = Path(f"runs/{run_id}")

    if not runs_dir.exists():
        raise FinalDeliveryError(
            f"Run directory not found: runs/{run_id}"
        )

    # Verify required artifacts
    artifacts: List[Dict] = []
    missing: List[str] = []

    for artifact_name in REQUIRED_ARTIFACTS:
        artifact_path = runs_dir / artifact_name
        if artifact_path.exists():
            # Load artifact to verify it's valid JSON
            try:
                with open(artifact_path, "r", encoding="utf-8") as f:
                    json.load(f)  # Validate JSON format

                artifacts.append({
                    "name": artifact_name,
                    "path": str(artifact_path),
                    "status": "ready",
                    "size_bytes": artifact_path.stat().st_size,
                })
            except Exception as e:
                artifacts.append({
                    "name": artifact_name,
                    "path": str(artifact_path),
                    "status": "error",
                    "error": f"Invalid JSON: {str(e)}",
                })
                missing.append(artifact_name)
        else:
            missing.append(artifact_name)
            artifacts.append({
                "name": artifact_name,
                "path": str(artifact_path),
                "status": "missing",
            })

    # Check optional artifacts (exported add-ons)
    optional_found: List[Dict] = []
    # Look for all exported add-on files (06_*.txt, 06_*.json, etc.)
    for file_path in runs_dir.glob("06_*"):
        if file_path.is_file() and file_path.name not in REQUIRED_ARTIFACTS:
            optional_found.append({
                "name": file_path.name,
                "path": str(file_path),
                "size_bytes": file_path.stat().st_size,
            })

    # Determine delivery status
    if missing:
        status = "INCOMPLETE"
        status_message = f"Missing {len(missing)} required artifact(s)"
    else:
        status = "COMPLETED"
        status_message = "All required artifacts delivered"

    # Create delivery manifest
    delivery = {
        "status": status,
        "message": status_message,
        "artifacts": artifacts,
        "optional_artifacts": optional_found,
        "missing_required": missing,
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "09_delivery",
            "total_artifacts": len(artifacts) + len(optional_found),
        },
    }

    # Write delivery manifest
    delivery_path = runs_dir / "delivery.json"
    with open(delivery_path, "w", encoding="utf-8") as f:
        json.dump(delivery, f, indent=2, ensure_ascii=False)

    return delivery


def load_synthesis(run_id: str) -> Dict:
    """
    Load the final UltrAI synthesis (primary result).

    Returns:
        Dict containing synthesis from 05_ultrai.json
    """
    runs_dir = Path(f"runs/{run_id}")
    ultrai_path = runs_dir / "05_ultrai.json"

    if not ultrai_path.exists():
        raise FinalDeliveryError(
            f"Synthesis not found: {ultrai_path}"
        )

    with open(ultrai_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_artifacts(run_id: str) -> Dict:
    """
    Load all artifacts for complete delivery package.

    Returns:
        Dict containing all artifacts:
        - synthesis: 05_ultrai.json
        - initial: 03_initial.json
        - meta: 04_meta.json
        - final: 06_final.json
        - stats: stats.json
        - delivery: delivery.json (manifest)
    """
    runs_dir = Path(f"runs/{run_id}")

    artifacts = {}

    # Load each artifact
    artifact_files = {
        "synthesis": "05_ultrai.json",
        "initial": "03_initial.json",
        "meta": "04_meta.json",
        "final": "06_final.json",
        "stats": "stats.json",
        "delivery": "delivery.json",
    }

    for key, filename in artifact_files.items():
        artifact_path = runs_dir / filename
        if artifact_path.exists():
            with open(artifact_path, "r", encoding="utf-8") as f:
                artifacts[key] = json.load(f)
        else:
            artifacts[key] = None

    return artifacts


def main():
    """CLI entry point for final delivery."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ultrai.final_delivery <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]

    try:
        delivery = deliver_results(run_id)

        print("Final Delivery COMPLETED")
        print(f"Run ID: {run_id}")
        print(f"Status: {delivery['status']}")
        print(f"Message: {delivery['message']}")
        print(f"\nArtifacts delivered: {len(delivery['artifacts'])}")

        for artifact in delivery['artifacts']:
            status_icon = "✓" if artifact['status'] == "ready" else "✗"
            print(f"  {status_icon} {artifact['name']}: {artifact['status']}")

        if delivery['optional_artifacts']:
            print(f"\nOptional artifacts: {len(delivery['optional_artifacts'])}")
            for opt in delivery['optional_artifacts']:
                print(f"  ✓ {opt['name']}")

        print(f"\nDelivery manifest: runs/{run_id}/delivery.json")

        return 0 if delivery['status'] == "COMPLETED" else 1

    except FinalDeliveryError as e:
        print(f"Final Delivery FAILED: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
