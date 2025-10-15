"""
Tests for PR 07 — Add-ons Processing
"""

import json
import os
from pathlib import Path
import pytest

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round
from ultrai.ultrai_synthesis import execute_ultrai_synthesis
from ultrai.addons_processing import apply_addons, AddonsProcessingError


skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_06_final_json_exists_and_addons_recorded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test add-ons",
        cocktail="SPEEDY",
        addons=["visualization", "citation_tracking"],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    apply_addons(run_id)

    final_path = Path(f"runs/{run_id}/06_final.json")
    assert final_path.exists(), "06_final.json must exist"

    with open(final_path, "r") as f:
        final = json.load(f)

    records = final.get("addOnsApplied", [])
    assert isinstance(records, list)
    assert any(r.get("name") == "visualization" for r in records)
    assert any(r.get("name") == "citation_tracking" for r in records)

    # Check exported files exist when ok
    for r in records:
        if r.get("ok") and r.get("path"):
            assert Path(r["path"]).exists()


def test_missing_ultrai_json_raises_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    run_id = "test_final_missing_ultrai"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create inputs only
    inputs = {
        "QUERY": "x",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "SPEEDY",
        "ADDONS": [],
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs, f)

    with pytest.raises(AddonsProcessingError):
        apply_addons(run_id)


# Comprehensive Tests


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_final_json_has_correct_round(tmp_path, monkeypatch):
    """Test that 06_final.json has round=FINAL."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Round test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    apply_addons(run_id)

    final_path = Path(f"runs/{run_id}/06_final.json")
    with open(final_path, "r") as f:
        final = json.load(f)

    assert final.get("round") == "FINAL"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_final_text_matches_ultrai_text(tmp_path, monkeypatch):
    """Test that final text comes from UltrAI synthesis."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Text match test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    ultrai_result = await execute_ultrai_synthesis(run_id)

    apply_addons(run_id)

    final_path = Path(f"runs/{run_id}/06_final.json")
    with open(final_path, "r") as f:
        final = json.load(f)

    # Final text should match UltrAI synthesis text
    assert final["text"] == ultrai_result["result"]["text"]


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_addon_records_have_required_fields(tmp_path, monkeypatch):
    """Test that each add-on record has required fields."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Add-on fields test",
        cocktail="SPEEDY",
        addons=["visualization", "citation_tracking"],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    apply_addons(run_id)

    final_path = Path(f"runs/{run_id}/06_final.json")
    with open(final_path, "r") as f:
        final = json.load(f)

    records = final["addOnsApplied"]
    for record in records:
        assert "name" in record
        assert "ok" in record
        assert isinstance(record["ok"], bool)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_no_addons_results_in_empty_list(tmp_path, monkeypatch):
    """Test that no add-ons selected results in empty addOnsApplied list."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="No add-ons test",
        cocktail="SPEEDY",
        addons=[],  # No add-ons
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    apply_addons(run_id)

    final_path = Path(f"runs/{run_id}/06_final.json")
    with open(final_path, "r") as f:
        final = json.load(f)

    assert final["addOnsApplied"] == []


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_export_addon_path_recorded(tmp_path, monkeypatch):
    """Test that export add-ons record their file paths."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Path recording test",
        cocktail="SPEEDY",
        addons=["visualization"],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    apply_addons(run_id)

    final_path = Path(f"runs/{run_id}/06_final.json")
    with open(final_path, "r") as f:
        final = json.load(f)

    viz_record = next(
        (r for r in final["addOnsApplied"] if r["name"] == "visualization"),
        None
    )
    assert viz_record is not None
    assert "path" in viz_record
    assert "06_visualization.txt" in viz_record["path"]


# End PR 07 tests
