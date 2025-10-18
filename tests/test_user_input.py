"""
PR 02 — User Input & Selection Tests

REAL tests (NO MOCKS) that verify user input collection functionality.
Tests the collect_user_inputs() function which creates 01_inputs.json artifacts.

Testing Endpoints:
1. 01_inputs.json exists after collecting inputs
2. includes QUERY, ANALYSIS, COCKTAIL fields
"""

import pytest
import json
from pathlib import Path
from ultrai.user_input import (
    collect_user_inputs,
    validate_inputs,
    load_inputs,
    UserInputError,
    VALID_COCKTAILS
)


@pytest.mark.pr02
def test_01_inputs_json_exists(tmp_path, monkeypatch):
    """
    Testing Endpoint 1: 01_inputs.json exists after collecting inputs

    REAL TEST - Actually creates the inputs artifact file on disk.
    """
    monkeypatch.chdir(tmp_path)

    collect_user_inputs(
        query="What is quantum computing?",
        cocktail="PREMIUM",
        run_id="test_run_001"
    )

    artifact_path = Path("runs/test_run_001/01_inputs.json")
    assert artifact_path.exists(), "01_inputs.json artifact was not created"

    # Verify it's a valid JSON file
    with open(artifact_path, "r") as f:
        data = json.load(f)
    assert isinstance(data, dict)


@pytest.mark.pr02
def test_includes_all_required_fields(tmp_path, monkeypatch):
    """
    Testing Endpoint 2: includes QUERY, ANALYSIS, COCKTAIL

    REAL TEST - Verifies all required fields are present in the artifact.
    """
    monkeypatch.chdir(tmp_path)

    result = collect_user_inputs(
        query="Explain machine learning",
        analysis="Synthesis",
        cocktail="SPEEDY",
        run_id="test_run_002"
    )

    # Check returned dictionary
    assert "QUERY" in result
    assert "ANALYSIS" in result
    assert "COCKTAIL" in result

    # Check artifact file
    artifact_path = Path("runs/test_run_002/01_inputs.json")
    with open(artifact_path, "r") as f:
        data = json.load(f)

    assert data["QUERY"] == "Explain machine learning"
    assert data["ANALYSIS"] == "Synthesis"
    assert data["COCKTAIL"] == "SPEEDY"


@pytest.mark.pr02
def test_all_four_cocktail_choices(tmp_path, monkeypatch):
    """
    Test all 5 pre-selected cocktail choices work correctly

    REAL TEST - Validates LUXE, PREMIUM, SPEEDY, BUDGET, DEPTH cocktails.
    """
    monkeypatch.chdir(tmp_path)

    for cocktail in ["LUXE", "PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]:
        result = collect_user_inputs(
            query=f"Test query for {cocktail}",
            cocktail=cocktail,
            run_id=f"test_{cocktail.lower()}"
        )

        assert result["COCKTAIL"] == cocktail

        artifact_path = Path(f"runs/test_{cocktail.lower()}/01_inputs.json")
        assert artifact_path.exists()

        with open(artifact_path, "r") as f:
            data = json.load(f)
        assert data["COCKTAIL"] == cocktail


@pytest.mark.pr02
def test_empty_query_raises_error(tmp_path, monkeypatch):
    """
    Test that empty query raises UserInputError

    REAL TEST - Validates error handling for missing query.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UserInputError, match="QUERY cannot be empty"):
        collect_user_inputs(
            query="",
            cocktail="PREMIUM"
        )

    with pytest.raises(UserInputError, match="QUERY cannot be empty"):
        collect_user_inputs(
            query="   ",  # Whitespace only
            cocktail="PREMIUM"
        )


@pytest.mark.pr02
def test_invalid_cocktail_raises_error(tmp_path, monkeypatch):
    """
    Test that invalid cocktail choice raises UserInputError

    REAL TEST - Validates cocktail selection constraints.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UserInputError, match="COCKTAIL must be one of"):
        collect_user_inputs(
            query="Test query",
            cocktail="INVALID_COCKTAIL"
        )


@pytest.mark.pr02
def test_invalid_analysis_raises_error(tmp_path, monkeypatch):
    """
    Test that invalid analysis type raises UserInputError

    REAL TEST - Validates analysis type constraints.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(UserInputError, match="ANALYSIS must be one of"):
        collect_user_inputs(
            query="Test query",
            analysis="InvalidAnalysis",
            cocktail="PREMIUM"
        )




@pytest.mark.pr02
def test_run_id_auto_generation(tmp_path, monkeypatch):
    """
    Test that run_id is auto-generated if not provided

    REAL TEST - Validates automatic run ID generation.
    """
    monkeypatch.chdir(tmp_path)

    result = collect_user_inputs(
        query="Test query",
        cocktail="BUDGET"
    )

    assert "metadata" in result
    assert "run_id" in result["metadata"]
    assert result["metadata"]["run_id"]  # Not empty

    # Verify artifact was created with auto-generated run_id
    run_id = result["metadata"]["run_id"]
    artifact_path = Path(f"runs/{run_id}/01_inputs.json")
    assert artifact_path.exists()


@pytest.mark.pr02
def test_load_inputs_from_previous_run(tmp_path, monkeypatch):
    """
    Test loading inputs from a previous run

    REAL TEST - Creates and then loads inputs artifact.
    """
    monkeypatch.chdir(tmp_path)

    # Create inputs
    collect_user_inputs(
        query="Original query",
        cocktail="PREMIUM",
        run_id="test_load_001"
    )

    # Load inputs
    loaded = load_inputs("test_load_001")

    assert loaded["QUERY"] == "Original query"
    assert loaded["COCKTAIL"] == "PREMIUM"


@pytest.mark.pr02
def test_load_nonexistent_run_raises_error(tmp_path, monkeypatch):
    """
    Test that loading non-existent run raises FileNotFoundError

    REAL TEST - Validates error handling for missing runs.
    """
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError, match="No inputs found for run_id"):
        load_inputs("nonexistent_run_id")


@pytest.mark.pr02
def test_validate_inputs_function():
    """
    Test the validate_inputs() function

    REAL TEST - Validates the validation function itself.
    """
    # Valid inputs
    valid_inputs = {
        "QUERY": "Test query",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM"
    }
    assert validate_inputs(valid_inputs) is True

    # Missing field
    invalid_inputs = {
        "QUERY": "Test",
        "ANALYSIS": "Synthesis"
        # Missing COCKTAIL
    }
    with pytest.raises(UserInputError, match="Missing required field"):
        validate_inputs(invalid_inputs)


@pytest.mark.pr02
def test_metadata_includes_timestamp_and_phase(tmp_path, monkeypatch):
    """
    Test that metadata includes timestamp and phase information

    REAL TEST - Validates metadata structure.
    """
    monkeypatch.chdir(tmp_path)

    result = collect_user_inputs(
        query="Test query",
        cocktail="SPEEDY",
        run_id="test_metadata"
    )

    assert "metadata" in result
    assert "timestamp" in result["metadata"]
    assert "phase" in result["metadata"]
    assert result["metadata"]["phase"] == "01_inputs"

    # Verify timestamp is valid ISO format
    from datetime import datetime
    datetime.fromisoformat(result["metadata"]["timestamp"])  # Should not raise


@pytest.mark.pr02
def test_cocktails_constant_matches_spec():
    """
    Test that VALID_COCKTAILS matches the 5 pre-selected choices

    REAL TEST - Validates cocktail configuration matches specification.
    """
    assert len(VALID_COCKTAILS) == 5
    assert "LUXE" in VALID_COCKTAILS
    assert "PREMIUM" in VALID_COCKTAILS
    assert "SPEEDY" in VALID_COCKTAILS
    assert "BUDGET" in VALID_COCKTAILS
    assert "DEPTH" in VALID_COCKTAILS
