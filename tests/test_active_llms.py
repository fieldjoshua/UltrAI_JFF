"""
Tests for PR 03 — Active LLMs Preparation

REAL tests (NO MOCKS) - creates actual artifacts and verifies their existence.

Testing Endpoints (from PR 03 template):
1. 02_activate.json exists
2. active≥2, quorum=2
"""

import json
import pytest
from pathlib import Path
from ultrai.active_llms import (
    prepare_active_llms,
    load_active_llms,
    ActiveLLMError,
    COCKTAIL_MODELS,
    QUORUM
)


def test_02_activate_json_exists(tmp_path, monkeypatch):
    """Test that 02_activate.json artifact is created"""
    monkeypatch.chdir(tmp_path)

    # Create prerequisite artifacts
    run_id = "test_run_001"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create 00_ready.json with sample READY list (includes 2+ PREMIUM models)
    ready_data = {
        "run_id": run_id,
        "readyList": [
            "openai/gpt-4o",  # PREMIUM
            "anthropic/claude-3.7-sonnet",  # PREMIUM
            "meta-llama/llama-4-maverick",  # PREMIUM
            "meta-llama/llama-3.3-70b-instruct",
            "openai/gpt-4o-mini"
        ],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    # Create 01_inputs.json with PREMIUM cocktail
    inputs_data = {
        "QUERY": "Test query",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    # Execute active LLMs preparation
    prepare_active_llms(run_id)

    # Verify artifact exists
    artifact_path = runs_dir / "02_activate.json"
    assert artifact_path.exists(), "02_activate.json artifact must exist"

    # Verify artifact can be parsed
    with open(artifact_path, "r") as f:
        artifact_data = json.load(f)

    assert artifact_data is not None
    assert "activeList" in artifact_data
    assert "quorum" in artifact_data


def test_active_gte_2_quorum_2(tmp_path, monkeypatch):
    """Test that activeList has at least 2 models and quorum is 2"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_002"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create READY list with multiple models from SPEEDY cocktail
    ready_data = {
        "run_id": run_id,
        "readyList": [
            "openai/gpt-4o-mini",  # SPEEDY
            "google/gemini-2.0-flash-exp:free",  # SPEEDY
            "meta-llama/llama-3.3-70b-instruct",  # SPEEDY
            "openai/gpt-4o"  # Not in SPEEDY
        ],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    inputs_data = {
        "QUERY": "Test query",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "SPEEDY",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    result = prepare_active_llms(run_id)

    # Verify quorum
    assert result["quorum"] == 2, "Quorum must be 2"
    assert result["quorum"] == QUORUM, "Quorum must match QUORUM constant"

    # Verify active list has at least 2 models
    assert len(result["activeList"]) >= 2, "activeList must have at least 2 models"
    assert len(result["activeList"]) == 3, "Expected 3 ACTIVE models for this test"


def test_all_four_cocktails(tmp_path, monkeypatch):
    """Test ACTIVE selection for all 4 cocktails"""
    monkeypatch.chdir(tmp_path)

    # Create a comprehensive READY list
    ready_list = [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-3.5-turbo",
        "anthropic/claude-3.7-sonnet",
        "anthropic/claude-3.5-haiku",
        "google/gemini-2.0-flash-exp:free",
        "google/gemini-2.0-flash-thinking-exp:free",
        "meta-llama/llama-3.3-70b-instruct",
        "meta-llama/llama-4-maverick",
        "qwen/qwen-2.5-72b-instruct"
    ]

    cocktails = ["PREMIUM", "SPEEDY", "BUDGET", "DEPTH"]

    for i, cocktail in enumerate(cocktails):
        run_id = f"test_run_00{i+3}"
        runs_dir = Path(f"runs/{run_id}")
        runs_dir.mkdir(parents=True)

        ready_data = {
            "run_id": run_id,
            "readyList": ready_list,
            "status": "READY"
        }
        with open(runs_dir / "00_ready.json", "w") as f:
            json.dump(ready_data, f)

        inputs_data = {
            "QUERY": f"Test query for {cocktail}",
            "ANALYSIS": "Synthesis",
            "COCKTAIL": cocktail,
            "ADDONS": []
        }
        with open(runs_dir / "01_inputs.json", "w") as f:
            json.dump(inputs_data, f)

        result = prepare_active_llms(run_id)

        # Verify results
        assert result["cocktail"] == cocktail
        assert len(result["activeList"]) >= 2, f"{cocktail} must have at least 2 ACTIVE"
        assert result["quorum"] == 2

        # Verify all active models are from the cocktail
        cocktail_models = COCKTAIL_MODELS[cocktail]
        for model in result["activeList"]:
            assert model in cocktail_models, f"{model} not in {cocktail} definition"


def test_intersection_logic(tmp_path, monkeypatch):
    """Test that ACTIVE = READY ∩ COCKTAIL"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_007"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only 2 out of 4 PREMIUM models are READY
    ready_data = {
        "run_id": run_id,
        "readyList": [
            "openai/gpt-4o",  # In PREMIUM
            "anthropic/claude-3.7-sonnet",  # In PREMIUM
            "openai/gpt-3.5-turbo"  # Not in PREMIUM
        ],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    inputs_data = {
        "QUERY": "Test intersection",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    result = prepare_active_llms(run_id)

    # Should only have the intersection
    assert len(result["activeList"]) == 2
    assert "openai/gpt-4o" in result["activeList"]
    assert "anthropic/claude-3.7-sonnet" in result["activeList"]
    assert "meta-llama/llama-4-maverick" not in result["activeList"]  # Not READY
    assert "openai/gpt-3.5-turbo" not in result["activeList"]  # Not in PREMIUM


def test_reasons_field(tmp_path, monkeypatch):
    """Test that reasons field explains status of each cocktail model"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_008"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    ready_data = {
        "run_id": run_id,
        "readyList": ["openai/gpt-4o", "anthropic/claude-3.7-sonnet"],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    inputs_data = {
        "QUERY": "Test reasons",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    result = prepare_active_llms(run_id)

    # Verify reasons dictionary exists
    assert "reasons" in result
    reasons = result["reasons"]

    # All 4 PREMIUM models should be in reasons
    premium_models = COCKTAIL_MODELS["PREMIUM"]
    for model in premium_models:
        assert model in reasons, f"{model} should be in reasons"

    # Check specific statuses
    assert reasons["openai/gpt-4o"] == "ACTIVE"
    assert reasons["anthropic/claude-3.7-sonnet"] == "ACTIVE"
    assert reasons["meta-llama/llama-4-maverick"] == "NOT READY"
    assert reasons["google/gemini-2.0-flash-exp:free"] == "NOT READY"


def test_insufficient_active_raises_error(tmp_path, monkeypatch):
    """Test error when activeList < 2 (quorum not met)"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_009"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only 1 BUDGET model is READY
    ready_data = {
        "run_id": run_id,
        "readyList": ["openai/gpt-3.5-turbo"],  # Only one BUDGET model
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    inputs_data = {
        "QUERY": "Test insufficient",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "BUDGET",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    # Should raise error
    with pytest.raises(ActiveLLMError) as exc_info:
        prepare_active_llms(run_id)

    error_message = str(exc_info.value)
    assert "Insufficient ACTIVE LLMs" in error_message
    assert "Found 1" in error_message
    assert "need at least 2" in error_message


def test_missing_ready_json_raises_error(tmp_path, monkeypatch):
    """Test error when 00_ready.json is missing"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_010"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only create inputs, no ready file
    inputs_data = {
        "QUERY": "Test missing ready",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    with pytest.raises(ActiveLLMError) as exc_info:
        prepare_active_llms(run_id)

    assert "Missing 00_ready.json" in str(exc_info.value)


def test_missing_inputs_json_raises_error(tmp_path, monkeypatch):
    """Test error when 01_inputs.json is missing"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_011"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only create ready, no inputs file
    ready_data = {
        "run_id": run_id,
        "readyList": ["openai/gpt-4o"],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    with pytest.raises(ActiveLLMError) as exc_info:
        prepare_active_llms(run_id)

    assert "Missing 01_inputs.json" in str(exc_info.value)


def test_load_active_llms(tmp_path, monkeypatch):
    """Test loading active LLMs from existing artifact"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_012"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create prerequisites and prepare active LLMs
    ready_data = {
        "run_id": run_id,
        "readyList": ["openai/gpt-4o", "anthropic/claude-3.7-sonnet", "meta-llama/llama-4-maverick"],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    inputs_data = {
        "QUERY": "Test load",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    # Prepare
    original_result = prepare_active_llms(run_id)

    # Load
    loaded_result = load_active_llms(run_id)

    # Verify they match
    assert loaded_result["activeList"] == original_result["activeList"]
    assert loaded_result["cocktail"] == original_result["cocktail"]
    assert loaded_result["quorum"] == original_result["quorum"]


def test_metadata_includes_run_id_and_phase(tmp_path, monkeypatch):
    """Test that metadata includes run_id, timestamp, and phase"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_013"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    ready_data = {
        "run_id": run_id,
        "readyList": ["openai/gpt-4o", "anthropic/claude-3.7-sonnet"],
        "status": "READY"
    }
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump(ready_data, f)

    inputs_data = {
        "QUERY": "Test metadata",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "DEPTH",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    result = prepare_active_llms(run_id)

    # Verify metadata
    assert "metadata" in result
    metadata = result["metadata"]

    assert metadata["run_id"] == run_id
    assert "timestamp" in metadata
    assert metadata["phase"] == "02_activate"


def test_cocktail_models_constant(tmp_path, monkeypatch):
    """Test that COCKTAIL_MODELS constant matches specification"""
    # Verify structure - now 5 cocktails
    assert "PRIME" in COCKTAIL_MODELS
    assert "PREMIUM" in COCKTAIL_MODELS
    assert "SPEEDY" in COCKTAIL_MODELS
    assert "BUDGET" in COCKTAIL_MODELS
    assert "DEPTH" in COCKTAIL_MODELS

    # Verify each has 4 models
    for cocktail, models in COCKTAIL_MODELS.items():
        assert len(models) == 4, f"{cocktail} must have exactly 4 models"

    # Verify specific primary models (verified 2025-10-15)
    assert "openai/gpt-5-pro" in COCKTAIL_MODELS["PRIME"]
    assert "anthropic/claude-opus-4.1" in COCKTAIL_MODELS["PRIME"]
    assert "google/gemini-2.5-pro" in COCKTAIL_MODELS["PRIME"]
    assert "meta-llama/llama-3.1-405b-instruct" in COCKTAIL_MODELS["PRIME"]
    assert "openai/gpt-4o" in COCKTAIL_MODELS["PREMIUM"]
    assert "openai/gpt-4o-mini" in COCKTAIL_MODELS["SPEEDY"]
    assert "openai/gpt-3.5-turbo" in COCKTAIL_MODELS["BUDGET"]
    assert "anthropic/claude-3.7-sonnet" in COCKTAIL_MODELS["DEPTH"]
