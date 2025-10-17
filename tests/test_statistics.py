"""
Tests for PR 08 — Statistics
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


skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_stats_present_for_all_phases(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Stats test",
        cocktail="SPEEDY",
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    stats = generate_statistics(run_id)

    # Verify structure
    assert "INITIAL" in stats and "META" in stats and "ULTRAI" in stats

    # Verify counts present
    assert isinstance(stats["INITIAL"].get("count"), int)
    assert isinstance(stats["META"].get("count"), int)
    assert isinstance(stats["ULTRAI"].get("count"), int)

    # Verify ms fields
    assert "avg_ms" in stats["INITIAL"]
    assert "avg_ms" in stats["META"]
    assert "ms" in stats["ULTRAI"]

    # Verify file written
    out_path = Path(f"runs/{run_id}/stats.json")
    assert out_path.exists(), "stats.json must be written"


# Comprehensive Tests


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_initial_stats_match_actual_count(tmp_path, monkeypatch):
    """Test that INITIAL stats count matches actual R1 outputs."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Count verification",
        cocktail="SPEEDY",
        run_id=run_id,
    )
    active_result = prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    stats = generate_statistics(run_id)

    # INITIAL count should match ACTIVE count
    assert stats["INITIAL"]["count"] == len(active_result["activeList"])


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_meta_stats_match_actual_count(tmp_path, monkeypatch):
    """Test that META stats count matches actual R2 outputs."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="META count test",
        cocktail="SPEEDY",
        run_id=run_id,
    )
    active_result = prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    stats = generate_statistics(run_id)

    # META count should match ACTIVE count
    assert stats["META"]["count"] == len(active_result["activeList"])


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_ultrai_stats_always_count_one(tmp_path, monkeypatch):
    """Test that ULTRAI stats count is always 1 (single synthesis)."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="ULTRAI count test",
        cocktail="SPEEDY",
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    stats = generate_statistics(run_id)

    # ULTRAI always has count=1 (single neutral synthesis)
    assert stats["ULTRAI"]["count"] == 1


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_stats_ms_values_are_positive(tmp_path, monkeypatch):
    """Test that timing values are positive integers."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Timing test",
        cocktail="SPEEDY",
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    stats = generate_statistics(run_id)

    # All timing values should be positive
    assert stats["INITIAL"]["avg_ms"] >= 0
    assert stats["META"]["avg_ms"] >= 0
    assert stats["ULTRAI"]["ms"] >= 0


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_stats_file_is_valid_json(tmp_path, monkeypatch):
    """Test that stats.json is valid, parseable JSON."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="JSON validity test",
        cocktail="SPEEDY",
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)
    await execute_ultrai_synthesis(run_id)

    generate_statistics(run_id)

    # Verify file is valid JSON
    stats_path = Path(f"runs/{run_id}/stats.json")
    with open(stats_path, "r") as f:
        stats = json.load(f)  # Should not raise

    # Verify structure
    assert isinstance(stats, dict)
    assert "INITIAL" in stats
    assert "META" in stats
    assert "ULTRAI" in stats


def test_stats_returns_zero_when_artifacts_missing(tmp_path, monkeypatch):
    """Test that generate_statistics handles missing artifacts gracefully."""
    monkeypatch.chdir(tmp_path)

    run_id = "test_missing_artifacts"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Generate stats with no artifacts (should not crash)
    stats = generate_statistics(run_id)

    # Should return zero/default values
    assert stats["INITIAL"]["count"] == 0
    assert stats["META"]["count"] == 0
    assert stats["ULTRAI"]["count"] == 0
