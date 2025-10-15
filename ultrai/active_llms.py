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


# Cocktail definitions (verified against OpenRouter as of 2025-10-15)
# All cocktails use 3 models for optimal speed/cost balance
COCKTAIL_MODELS = {
    "LUXE": [
        "openai/gpt-4o",                                    # OpenAI's GPT-4o (fast + premium)
        "anthropic/claude-sonnet-4.5",                      # Anthropic's latest Sonnet 4.5
        "google/gemini-2.0-flash-exp:free"                  # Google's Gemini 2.0 Flash
    ],
    "PREMIUM": [
        "anthropic/claude-3.7-sonnet",                      # Anthropic Claude 3.7
        "openai/chatgpt-4o-latest",                         # OpenAI ChatGPT-4o
        "meta-llama/llama-3.3-70b-instruct"                # Meta Llama 3.3 70B
    ],
    "SPEEDY": [
        "openai/gpt-4o-mini",                               # OpenAI mini (fastest)
        "anthropic/claude-3.5-haiku",                       # Anthropic Haiku (fast)
        "google/gemini-2.0-flash-exp:free"                  # Gemini Flash (fast)
    ],
    "BUDGET": [
        "openai/gpt-3.5-turbo",                             # OpenAI 3.5 (cheap)
        "google/gemini-2.0-flash-exp:free",                 # Gemini (free tier)
        "qwen/qwen-2.5-72b-instruct"                        # Qwen 2.5 (budget)
    ],
    "DEPTH": [
        "anthropic/claude-3.7-sonnet",                      # Claude 3.7 (reasoning)
        "openai/gpt-4o",                                    # GPT-4o (capable)
        "meta-llama/llama-3.3-70b-instruct"                # Llama 70B (deep)
    ]
}

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

    # Get cocktail models
    cocktail_models = COCKTAIL_MODELS[cocktail]

    # Convert readyList to set for O(1) lookup
    ready_set = set(ready_list)

    # Find intersection: ACTIVE = READY ∩ COCKTAIL
    active_list = [model for model in cocktail_models if model in ready_set]

    # Build reasons dictionary
    reasons = {}
    for model in cocktail_models:
        if model in ready_set:
            reasons[model] = "ACTIVE"
        else:
            reasons[model] = "NOT READY"

    # Check quorum
    if len(active_list) < QUORUM:
        raise ActiveLLMError(
            f"Insufficient ACTIVE LLMs. Found {len(active_list)}, need at least {QUORUM}. "
            f"Cocktail: {cocktail}. "
            f"Reasons: {reasons}. "
            "Low pluralism warning."
        )

    # Build result
    result = {
        "activeList": active_list,
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
        raise FileNotFoundError(f"No active LLMs data found for run_id: {run_id}")

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
        print(f"Active LLMs preparation PASSED")
        print(f"Run ID: {result['metadata']['run_id']}")
        print(f"Cocktail: {result['cocktail']}")
        print(f"Active LLMs: {len(result['activeList'])}")
        print(f"Quorum: {result['quorum']}")
        print(f"Artifact: runs/{run_id}/02_activate.json")
        print(f"\nActive models:")
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
