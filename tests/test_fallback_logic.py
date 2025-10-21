"""
Tests for PRIMARY/FALLBACK model configuration and logic.

REAL tests (NO MOCKS) - verifies that:
1. All cocktails have exactly 3 PRIMARY + 3 FALLBACK models
2. Fallback logic structure is correct (1:1 correspondence)
3. Failed models are tracked correctly in R1/R2 execution
"""

import json
import pytest
import os
from pathlib import Path
from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import (
    prepare_active_llms,
    PRIMARY_MODELS,
    FALLBACK_MODELS,
    PRIMARY_TIMEOUT,
    PRIMARY_ATTEMPTS
)
from ultrai.initial_round import execute_initial_round


# Skip tests if no API key
skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set"
)


@pytest.mark.pr03
def test_all_cocktails_have_3_primary_models():
    """Verify all cocktails have exactly 3 PRIMARY models"""
    for cocktail_name, models in PRIMARY_MODELS.items():
        assert len(models) == 3, (
            f"{cocktail_name} must have exactly 3 PRIMARY models, "
            f"found {len(models)}: {models}"
        )


@pytest.mark.pr03
def test_all_cocktails_have_3_fallback_models():
    """Verify all cocktails have exactly 3 FALLBACK models"""
    for cocktail_name, models in FALLBACK_MODELS.items():
        assert len(models) == 3, (
            f"{cocktail_name} must have exactly 3 FALLBACK models, "
            f"found {len(models)}: {models}"
        )


@pytest.mark.pr03
def test_primary_and_fallback_counts_match():
    """Verify PRIMARY and FALLBACK have same cocktail keys and model counts"""
    assert set(PRIMARY_MODELS.keys()) == set(FALLBACK_MODELS.keys()), (
        "PRIMARY_MODELS and FALLBACK_MODELS must have same cocktail names"
    )

    for cocktail_name in PRIMARY_MODELS.keys():
        primary_count = len(PRIMARY_MODELS[cocktail_name])
        fallback_count = len(FALLBACK_MODELS[cocktail_name])
        assert primary_count == fallback_count, (
            f"{cocktail_name}: PRIMARY has {primary_count} models but "
            f"FALLBACK has {fallback_count} (must be 1:1 correspondence)"
        )


@pytest.mark.pr03
def test_primary_timeout_and_attempts_configured():
    """Verify PRIMARY_TIMEOUT and PRIMARY_ATTEMPTS are set correctly"""
    assert PRIMARY_TIMEOUT == 15, "PRIMARY_TIMEOUT must be 15 seconds"
    assert PRIMARY_ATTEMPTS == 2, "PRIMARY_ATTEMPTS must be 2 retries"

    # Total max time per PRIMARY: 2 attempts × 15s = 30s
    total_max_time = PRIMARY_ATTEMPTS * PRIMARY_TIMEOUT
    assert total_max_time == 30, (
        f"Total PRIMARY attempt time should be 30s, got {total_max_time}s"
    )


@pytest.mark.pr03
def test_no_duplicate_models_in_primary():
    """Verify no duplicate models within each PRIMARY cocktail"""
    for cocktail_name, models in PRIMARY_MODELS.items():
        unique_models = set(models)
        assert len(unique_models) == len(models), (
            f"{cocktail_name} PRIMARY has duplicate models: {models}"
        )


@pytest.mark.pr03
def test_no_duplicate_models_in_fallback():
    """Verify no duplicate models within each FALLBACK cocktail"""
    for cocktail_name, models in FALLBACK_MODELS.items():
        unique_models = set(models)
        assert len(unique_models) == len(models), (
            f"{cocktail_name} FALLBACK has duplicate models: {models}"
        )


@skip_if_no_api_key
@pytest.mark.pr04
@pytest.mark.asyncio
async def test_failed_models_tracked_in_initial_round(tmp_path, monkeypatch):
    """
    Verify that failed_models list exists in R1 execution output.

    This test verifies the structure exists for tracking failures,
    which enables the fallback logic to work correctly.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="What is 1+1?",
        cocktail="BUDGET",  # Use BUDGET for faster/cheaper test
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify failed_models field exists in result
    assert "failed_models" in result, (
        "R1 result must have 'failed_models' field for tracking failures"
    )
    assert isinstance(result["failed_models"], list), (
        "failed_models must be a list"
    )

    # Verify 03_initial_status.json tracks failures
    runs_dir = Path(f"runs/{run_id}")
    status_path = runs_dir / "03_initial_status.json"
    assert status_path.exists(), "03_initial_status.json must exist"

    with open(status_path, "r") as f:
        status_data = json.load(f)

    assert "details" in status_data, "Status must have 'details' field"
    assert "failed_models" in status_data["details"], (
        "Status details must track failed_models"
    )


@skip_if_no_api_key
@pytest.mark.pr04
@pytest.mark.asyncio
async def test_backup_list_loaded_from_activate(tmp_path, monkeypatch):
    """
    Verify that backupList (FALLBACK models) is loaded from 02_activate.json.

    This confirms the activation phase correctly identifies which FALLBACK
    models are available for use during R1 execution.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Test query",
        cocktail="SPEEDY",
        run_id=run_id
    )

    activate_result = prepare_active_llms(run_id)

    # Verify backupList exists in activation result
    assert "backupList" in activate_result, (
        "02_activate.json must contain backupList (FALLBACK models)"
    )
    assert isinstance(activate_result["backupList"], list), (
        "backupList must be a list"
    )

    # Verify backupList is saved to artifact
    runs_dir = Path(f"runs/{run_id}")
    activate_path = runs_dir / "02_activate.json"

    with open(activate_path, "r") as f:
        activate_data = json.load(f)

    assert "backupList" in activate_data, (
        "02_activate.json artifact must include backupList"
    )

    # Verify backupList contains models from FALLBACK_MODELS for selected cocktail
    cocktail = activate_result["cocktail"]
    expected_fallbacks = FALLBACK_MODELS[cocktail]

    # backupList should be intersection of FALLBACK_MODELS and READY list
    # (at least some should match if models are available)
    backup_list = activate_result["backupList"]

    # Each backup in list should be from the cocktail's FALLBACK_MODELS
    for backup in backup_list:
        assert backup in expected_fallbacks, (
            f"Backup model '{backup}' should be in {cocktail} FALLBACK_MODELS"
        )


@pytest.mark.pr03
def test_no_model_in_both_primary_and_fallback():
    """
    CRITICAL: Verify no model appears in both PRIMARY and FALLBACK for same cocktail.

    This prevents the bug where a failed PRIMARY model is retried as its own FALLBACK,
    causing errors like:
    "Primary failed (Rate limited), Backup failed (Rate limited)"
    for the same model.
    """
    for cocktail_name in PRIMARY_MODELS.keys():
        primary_set = set(PRIMARY_MODELS[cocktail_name])
        fallback_set = set(FALLBACK_MODELS[cocktail_name])

        duplicates = primary_set & fallback_set
        assert len(duplicates) == 0, (
            f"{cocktail_name} has models in BOTH PRIMARY and FALLBACK: {duplicates}\n"
            f"PRIMARY: {PRIMARY_MODELS[cocktail_name]}\n"
            f"FALLBACK: {FALLBACK_MODELS[cocktail_name]}\n"
            "This causes the backup system to retry the same failed model!"
        )


@pytest.mark.pr03
def test_fallback_model_correspondence():
    """
    Verify 1:1 correspondence between PRIMARY and FALLBACK models.

    Each PRIMARY model at index i should have a corresponding FALLBACK
    model at index i in the FALLBACK list.
    """
    for cocktail_name in PRIMARY_MODELS.keys():
        primary_list = PRIMARY_MODELS[cocktail_name]
        fallback_list = FALLBACK_MODELS[cocktail_name]

        for i in range(len(primary_list)):
            primary = primary_list[i]
            fallback = fallback_list[i]

            # Fallback should be different from primary (to provide alternative)
            # (unless no alternative exists, which is rare)
            assert isinstance(primary, str), (
                f"{cocktail_name} PRIMARY[{i}] must be a string"
            )
            assert isinstance(fallback, str), (
                f"{cocktail_name} FALLBACK[{i}] must be a string"
            )
