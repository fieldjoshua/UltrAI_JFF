"""
PR 02 — User Input & Selection

Handles user input collection and selection for the UltrAI orchestration system.
Users enter:
- QUERY: The question or prompt to analyze
- ANALYSIS: Type of analysis (currently supports "Synthesis")
- COCKTAIL: One of four pre-selected LLM groups
- ADDONS: Optional features to enable

Creates artifact: runs/<RunID>/01_inputs.json
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class UserInputError(Exception):
    """Raised when user input validation fails"""
    pass


# Valid cocktail choices (4 pre-selected options)
VALID_COCKTAILS = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]

# Valid analysis types
VALID_ANALYSES = ["Synthesis"]

# Optional add-ons that users can enable
AVAILABLE_ADDONS = [
    "citation_tracking",
    "cost_monitoring",
    "extended_stats",
    "visualization",
    "confidence_intervals"
]


def collect_user_inputs(
    query: str,
    analysis: str = "Synthesis",
    cocktail: str = "PREMIUM",
    addons: Optional[List[str]] = None,
    run_id: Optional[str] = None
) -> Dict:
    """
    Collect and validate user inputs for the UltrAI system.

    Args:
        query: User's question or prompt (required)
        analysis: Type of analysis to perform (default: "Synthesis")
        cocktail: LLM cocktail selection - one of PREMIUM, SPEEDY, BUDGET, DEPTH
        addons: List of optional features to enable
        run_id: Run ID for this session (auto-generated if not provided)

    Returns:
        Dict containing validated inputs and metadata

    Raises:
        UserInputError: If validation fails

    Example:
        >>> inputs = collect_user_inputs(
        ...     query="What is quantum computing?",
        ...     cocktail="PREMIUM",
        ...     addons=["citation_tracking"]
        ... )
    """
    # Validation
    if not query or not query.strip():
        raise UserInputError("QUERY cannot be empty")

    if analysis not in VALID_ANALYSES:
        raise UserInputError(
            f"ANALYSIS must be one of {VALID_ANALYSES}, got: {analysis}"
        )

    if cocktail not in VALID_COCKTAILS:
        raise UserInputError(
            f"COCKTAIL must be one of {VALID_COCKTAILS}, got: {cocktail}"
        )

    # Validate addons
    if addons is None:
        addons = []

    for addon in addons:
        if addon not in AVAILABLE_ADDONS:
            raise UserInputError(
                f"Invalid addon '{addon}'. Available: {AVAILABLE_ADDONS}"
            )

    # Generate run ID if not provided
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build inputs dictionary
    inputs = {
        "QUERY": query.strip(),
        "ANALYSIS": analysis,
        "COCKTAIL": cocktail,
        "ADDONS": addons,
        "metadata": {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "phase": "01_inputs"
        }
    }

    # Create artifact
    artifact_path = Path(f"runs/{run_id}/01_inputs.json")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    with open(artifact_path, "w", encoding="utf-8") as f:
        json.dump(inputs, f, indent=2, ensure_ascii=False)

    return inputs


def validate_inputs(inputs_dict: Dict) -> bool:
    """
    Validate that an inputs dictionary contains all required fields.

    Args:
        inputs_dict: Dictionary to validate

    Returns:
        True if valid

    Raises:
        UserInputError: If validation fails
    """
    required_fields = ["QUERY", "ANALYSIS", "COCKTAIL", "ADDONS"]

    for field in required_fields:
        if field not in inputs_dict:
            raise UserInputError(f"Missing required field: {field}")

    # Validate field values
    if not inputs_dict["QUERY"].strip():
        raise UserInputError("QUERY cannot be empty")

    if inputs_dict["ANALYSIS"] not in VALID_ANALYSES:
        raise UserInputError(f"Invalid ANALYSIS: {inputs_dict['ANALYSIS']}")

    if inputs_dict["COCKTAIL"] not in VALID_COCKTAILS:
        raise UserInputError(f"Invalid COCKTAIL: {inputs_dict['COCKTAIL']}")

    if not isinstance(inputs_dict["ADDONS"], list):
        raise UserInputError("ADDONS must be a list")

    for addon in inputs_dict["ADDONS"]:
        if addon not in AVAILABLE_ADDONS:
            raise UserInputError(f"Invalid addon: {addon}")

    return True


def load_inputs(run_id: str) -> Dict:
    """
    Load inputs from a previous run.

    Args:
        run_id: The run ID to load inputs from

    Returns:
        Dict containing the inputs

    Raises:
        FileNotFoundError: If the inputs file doesn't exist
        UserInputError: If the inputs file is invalid
    """
    artifact_path = Path(f"runs/{run_id}/01_inputs.json")

    if not artifact_path.exists():
        raise FileNotFoundError(f"No inputs found for run_id: {run_id}")

    with open(artifact_path, "r", encoding="utf-8") as f:
        inputs = json.load(f)

    # Validate loaded inputs
    validate_inputs(inputs)

    return inputs
