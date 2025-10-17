"""
Tests for PR 09 — Final Delivery

REAL tests (NO MOCKS) - uses actual OpenRouter API calls for full pipeline.

Testing Endpoints (from PR 09 template):
1. All four JSONs exist under runs/<RunID>/
2. If export add-ons selected, exported files exist
3. Delivery manifest correctly lists all artifacts
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
from ultrai.statistics import generate_statistics
from ultrai.final_delivery import (
    deliver_results,
    load_synthesis,
    load_all_artifacts,
    FinalDeliveryError,
)


skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_all_required_artifacts_exist(tmp_path, monkeypatch):
    """Test that all required artifacts exist after full pipeline."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run full pipeline
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Full pipeline test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)
    generate_statistics(run_id)

    # Deliver results
    delivery = deliver_results(run_id)

    # Verify all required artifacts present
    assert delivery["status"] == "COMPLETED"
    assert len(delivery["missing_required"]) == 0

    # Verify specific artifacts
    runs_dir = Path(f"runs/{run_id}")
    assert (runs_dir / "05_ultrai.json").exists()
    assert (runs_dir / "03_initial.json").exists()
    assert (runs_dir / "04_meta.json").exists()
    assert (runs_dir / "06_final.json").exists()
    assert (runs_dir / "stats.json").exists()
    assert (runs_dir / "delivery.json").exists()


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_delivery_manifest_structure(tmp_path, monkeypatch):
    """Test that delivery manifest has correct structure."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run full pipeline
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Manifest test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)
    generate_statistics(run_id)

    delivery = deliver_results(run_id)

    # Verify manifest structure
    assert "status" in delivery
    assert "message" in delivery
    assert "artifacts" in delivery
    assert "optional_artifacts" in delivery
    assert "missing_required" in delivery
    assert "metadata" in delivery

    # Verify metadata
    assert delivery["metadata"]["run_id"] == run_id
    assert delivery["metadata"]["phase"] == "09_delivery"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_exported_addon_files_exist(tmp_path, monkeypatch):
    """Test that exported add-on files exist when selected."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run full pipeline with add-ons
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Add-ons export test",
        cocktail="SPEEDY",
        addons=["visualization", "citation_tracking"],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)
    generate_statistics(run_id)

    delivery = deliver_results(run_id)

    # Verify exported files in optional_artifacts
    optional_names = [a["name"] for a in delivery["optional_artifacts"]]
    assert "06_visualization.txt" in optional_names
    assert "06_citations.json" in optional_names

    # Verify files actually exist
    runs_dir = Path(f"runs/{run_id}")
    assert (runs_dir / "06_visualization.txt").exists()
    assert (runs_dir / "06_citations.json").exists()


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_load_synthesis_returns_ultrai(tmp_path, monkeypatch):
    """Test that load_synthesis returns the synthesis artifact."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run pipeline
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Load synthesis test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    # Load synthesis
    synthesis = load_synthesis(run_id)

    # Verify synthesis structure
    assert synthesis["round"] == "ULTRAI"
    assert "model" in synthesis
    assert "text" in synthesis
    assert len(synthesis["text"]) > 0


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_load_all_artifacts_returns_complete_package(tmp_path, monkeypatch):
    """Test that load_all_artifacts returns all deliverables."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run full pipeline
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Load all test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)
    generate_statistics(run_id)
    deliver_results(run_id)

    # Load all artifacts
    artifacts = load_all_artifacts(run_id)

    # Verify all artifacts loaded
    assert artifacts["synthesis"] is not None
    assert artifacts["initial"] is not None
    assert artifacts["meta"] is not None
    assert artifacts["final"] is not None
    assert artifacts["stats"] is not None
    assert artifacts["delivery"] is not None

    # Verify synthesis content
    assert artifacts["synthesis"]["round"] == "ULTRAI"
    assert isinstance(artifacts["initial"], list)
    assert isinstance(artifacts["meta"], list)


def test_missing_run_directory_raises_error(tmp_path, monkeypatch):
    """Test error when run directory doesn't exist."""
    monkeypatch.chdir(tmp_path)

    run_id = "nonexistent_run"

    with pytest.raises(FinalDeliveryError) as exc_info:
        deliver_results(run_id)

    assert "Run directory not found" in str(exc_info.value)


def test_missing_synthesis_raises_error(tmp_path, monkeypatch):
    """Test error when synthesis artifact is missing."""
    monkeypatch.chdir(tmp_path)

    run_id = "test_missing_synthesis"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create delivery but no synthesis
    with pytest.raises(FinalDeliveryError) as exc_info:
        load_synthesis(run_id)

    assert "Synthesis not found" in str(exc_info.value)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_delivery_status_incomplete_when_missing_artifacts(
    tmp_path, monkeypatch
):
    """Test that delivery status is INCOMPLETE when artifacts missing."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run partial pipeline (missing final and stats)
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Partial pipeline",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)
    # Intentionally skip addons and stats

    # Deliver (should be incomplete)
    delivery = deliver_results(run_id)

    assert delivery["status"] == "INCOMPLETE"
    assert len(delivery["missing_required"]) > 0
    assert "06_final.json" in delivery["missing_required"]
    assert "stats.json" in delivery["missing_required"]


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_artifact_size_tracking(tmp_path, monkeypatch):
    """Test that artifact sizes are tracked in delivery manifest."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Run full pipeline
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Size tracking test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)
    generate_statistics(run_id)

    delivery = deliver_results(run_id)

    # Verify size tracking for ready artifacts
    for artifact in delivery["artifacts"]:
        if artifact["status"] == "ready":
            assert "size_bytes" in artifact
            assert artifact["size_bytes"] > 0
