"""
PR 03 — Active LLMs Preparation

Determines which LLMs are ACTIVE by finding the intersection of:
- READY list (from system readiness check)
- COCKTAIL models (from user selection)

ACTIVE = READY ∩ COCKTAIL

Requires quorum of at least 2 ACTIVE models to proceed.

Creates artifact: runs/<RunID>/02_activate.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict


class ActiveLLMError(Exception):
    """Raised when active LLM preparation fails"""
    pass


# PRIMARY models: Core models per cocktail (exactly 3 per cocktail)
# Each PRIMARY has X seconds to respond or fail before FALLBACK is activated
PRIMARY_MODELS = {
    "LUXE": [
        "openai/gpt-4o",
        "anthropic/claude-sonnet-4.5",
        "google/gemini-2.0-flash-exp:free",
    ],
    "PREMIUM": [
        "anthropic/claude-3.7-sonnet",
        "openai/gpt-4o",
        "google/gemini-2.5-pro",
    ],
    "SPEEDY": [
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku",
        "x-ai/grok-3-mini",  # Updated from grok-2-1212 (no longer available)
    ],
    "BUDGET": [
        "openai/gpt-3.5-turbo",
        "google/gemini-2.0-flash-exp:free",
        "qwen/qwen-2.5-72b-instruct",
    ],
    "DEPTH": [
        "anthropic/claude-3.7-sonnet",
        "openai/gpt-4o",
        "meta-llama/llama-3.3-70b-instruct",
    ],
}

# FALLBACK models: Activated if PRIMARY fails or times out
# 1:1 correspondence with PRIMARY models
# (same index = fallback for that primary)
# Each cocktail has exactly 3 FALLBACK models
# matching the 3 PRIMARY models
# CRITICAL: A model cannot appear in both PRIMARY
# and FALLBACK for the same cocktail
FALLBACK_MODELS = {
    "LUXE": [
        "openai/chatgpt-4o-latest",           # Fallback for gpt-4o
        "anthropic/claude-3.7-sonnet",        # Fallback for sonnet-4.5
        "google/gemini-2.5-pro",              # Fallback for gemini-flash
    ],
    "PREMIUM": [
        "x-ai/grok-3",                        # Fallback for claude-3.7 (updated from grok-2-1212)
        "openai/chatgpt-4o-latest",           # Fallback for gpt-4o
        "meta-llama/llama-3.3-70b-instruct",  # Fallback for gemini-2.5-pro
    ],
    "SPEEDY": [
        "google/gemini-2.0-flash-exp:free",   # Fallback for gpt-4o-mini
        "qwen/qwen-2.5-72b-instruct",         # Fallback for claude-haiku
        "meta-llama/llama-3.3-70b-instruct",  # Fallback for grok-3-mini
    ],
    "BUDGET": [
        "meta-llama/llama-3.3-70b-instruct",  # Fallback for gpt-3.5
        "openai/gpt-4o-mini",                 # Fallback for gemini
        "anthropic/claude-3-haiku",           # Fallback for qwen
    ],
    "DEPTH": [
        "openai/chatgpt-4o-latest",
        # Fallback for claude-3.7
        "anthropic/claude-sonnet-4.5",
        # Fallback for gpt-4o
        "google/gemini-2.0-flash-exp:free",
        # Fallback for llama
    ],
}

# Timeout and retry configuration for PRIMARY models
# Seconds per attempt for PRIMARY model to respond
PRIMARY_TIMEOUT = 15
# Number of retry attempts before FALLBACK activation
# (2 attempts × 15s = 30s max)
PRIMARY_ATTEMPTS = 2

# Legacy aliases for backward compatibility (will be deprecated)
COCKTAIL_MODELS = PRIMARY_MODELS
BACKUP_MODELS = FALLBACK_MODELS

# Minimum quorum for execution
QUORUM = 2


def prepare_active_llms(run_id: str) -> Dict:
    """
    Prepare ACTIVE LLMs by finding intersection of READY and COCKTAIL.

    Reads:
    - runs/<run_id>/00_ready.json (for readyList)
    - runs/<run_id>/01_inputs.json (for COCKTAIL choice)

    Creates:
    - runs/<run_id>/02_activate.json (with activeList)

    Args:
        run_id: The run ID to process

    Returns:
        Dictionary containing:
        - activeList: List of ACTIVE LLM identifiers
        - quorum: Required minimum (always 2)
        - cocktail: Selected cocktail name
        - reasons: Dict explaining status of each cocktail model
        - metadata: Run metadata

    Raises:
        ActiveLLMError: If quorum not met or files missing
    """
    runs_dir = Path(f"runs/{run_id}")

    # Load readyList from 00_ready.json
    ready_path = runs_dir / "00_ready.json"
    if not ready_path.exists():
        raise ActiveLLMError(
            f"Missing 00_ready.json for run_id: {run_id}. "
            "Run system readiness check first."
        )

    with open(ready_path, "r", encoding="utf-8") as f:
        ready_data = json.load(f)
        ready_list = ready_data.get("readyList", [])

    # Load COCKTAIL from 01_inputs.json
    inputs_path = runs_dir / "01_inputs.json"
    if not inputs_path.exists():
        raise ActiveLLMError(
            f"Missing 01_inputs.json for run_id: {run_id}. "
            "Collect user inputs first."
        )

    with open(inputs_path, "r", encoding="utf-8") as f:
        inputs_data = json.load(f)
        cocktail = inputs_data.get("COCKTAIL")

    if not cocktail:
        raise ActiveLLMError("COCKTAIL not found in 01_inputs.json")

    if cocktail not in COCKTAIL_MODELS:
        raise ActiveLLMError(
            f"Unknown COCKTAIL: {cocktail}. "
            f"Valid options: {list(COCKTAIL_MODELS.keys())}"
        )

    # Get cocktail models and backups
    cocktail_models = COCKTAIL_MODELS[cocktail]
    backup_models = BACKUP_MODELS.get(cocktail, [])

    # Convert readyList to set for O(1) lookup
    ready_set = set(ready_list)

    # Resolve PRIMARY list with replacements if needed
    # Goal: ensure 3 PRIMARY slots are filled by READY models
    resolved_primary: list[str] = []
    reasons: dict[str, str] = {}

    # Helper pool: all models from cocktail (PRIMARY + FALLBACK) that are READY
    ready_pool = [
        m for m in (cocktail_models + backup_models)
        if m in ready_set
    ]

    for idx, primary_model in enumerate(cocktail_models):
        # 1) Prefer PRIMARY if READY
        if (
            primary_model in ready_set
            and primary_model not in resolved_primary
        ):
            resolved_primary.append(primary_model)
            reasons[primary_model] = "PRIMARY_READY"
            continue

        # 2) Use aligned FALLBACK (same index) if READY
        fallback_model = (
            backup_models[idx] if idx < len(backup_models) else None
        )
        if (
            fallback_model
            and fallback_model in ready_set
            and fallback_model not in resolved_primary
        ):
            resolved_primary.append(fallback_model)
            reasons[primary_model] = (
                f"REPLACED_FALLBACK:{fallback_model}"
            )
            continue

        # 3) Use any other READY model from cocktail sets not yet chosen
        alternate = next(
            (
                m for m in ready_pool
                if m not in resolved_primary
            ),
            None,
        )
        if alternate is not None:
            resolved_primary.append(alternate)
            reasons[primary_model] = (
                f"REPLACED_ALT:{alternate}"
            )
            continue

        # 4) No replacement available for this slot
        reasons[primary_model] = "NOT READY_NO_REPLACEMENT"

    # Validate we still have 3 resolved primaries; else invalidate cocktail
    if len(resolved_primary) < 3:
        msg = (
            "PRIMARY set cannot be satisfied from READY models. "
            f"Cocktail: {cocktail}. Reasons: {reasons}."
        )
        raise ActiveLLMError(
            msg
        )

    # Active list is the resolved primary set (exactly 3)
    active_list = resolved_primary[:3]

    # Backup list are remaining READY backups not already used
    backup_list = [
        m for m in backup_models
        if (m in ready_set) and (m not in active_list)
    ]

    # Check quorum
    if len(active_list) < QUORUM:
        raise ActiveLLMError(
            "Insufficient ACTIVE LLMs. Found "
            f"{len(active_list)}, need at least {QUORUM}. "
            f"Cocktail: {cocktail}. "
            f"Reasons: {reasons}. "
            "Low pluralism warning."
        )

    # Build result
    result = {
        "activeList": active_list,
        "backupList": backup_list,  # NEW: Backup models for fast-fail recovery
        "quorum": QUORUM,
        "cocktail": cocktail,
        "reasons": reasons,
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "02_activate"
        }
    }

    # Create artifact
    artifact_path = runs_dir / "02_activate.json"
    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result


def load_active_llms(run_id: str) -> Dict:
    """
    Load active LLMs from a previous run.

    Args:
        run_id: The run ID to load from

    Returns:
        Dict containing active LLM data

    Raises:
        FileNotFoundError: If 02_activate.json doesn't exist
    """
    artifact_path = Path(f"runs/{run_id}/02_activate.json")

    if not artifact_path.exists():
        raise FileNotFoundError(
            f"No active LLMs data found for run_id: {run_id}"
        )

    with open(artifact_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    """CLI entry point for active LLMs preparation"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ultrai.active_llms <run_id>")
        sys.exit(1)

    run_id = sys.argv[1]

    try:
        result = prepare_active_llms(run_id)
        print("Active LLMs preparation PASSED")
        print(f"Run ID: {result['metadata']['run_id']}")
        print(f"Cocktail: {result['cocktail']}")
        print(f"Active LLMs: {len(result['activeList'])}")
        print(f"Quorum: {result['quorum']}")
        print(f"Artifact: runs/{run_id}/02_activate.json")
        print("\nActive models:")
        for model in result['activeList']:
            print(f"  - {model}")
        return 0
    except ActiveLLMError as e:
        print(f"Active LLMs preparation FAILED: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
