"""
Tests for R1/R2 step prepopulation logic.

Verifies that:
- Model steps are prepopulated at the right time
- Steps appear in correct sequence (parents before children)
- Prepopulation handles missing files gracefully
- Prepopulation logs appropriately
"""

import json
from pathlib import Path

import pytest

from ultrai.api import (
    _prepopulate_r1_steps,
    _prepopulate_r2_steps,
    _load_active_models,
    progress_tracker,
)


@pytest.fixture
def mock_run_dir(tmp_path, monkeypatch):
    """Create mock run directory with 02_activate.json"""
    run_id = "test_20250101_120000"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)

    # Create mock 02_activate.json
    activate_data = {
        "activeList": [
            "openai/gpt-4o-mini",
            "anthropic/claude-3-haiku",
            "x-ai/grok-3-mini",
        ],
        "cocktail": "SPEEDY",
        "quorum": 2,
    }
    activate_file = run_dir / "02_activate.json"
    activate_file.write_text(json.dumps(activate_data, indent=2))

    # Monkeypatch Path to use tmp_path
    monkeypatch.setattr(
        "ultrai.api.Path",
        lambda p: tmp_path / p if "runs" in p else Path(p),
    )

    return run_id, run_dir


def test_load_active_models_success(mock_run_dir):
    """Test successful loading of active models"""
    run_id, _ = mock_run_dir
    models = _load_active_models(run_id)

    assert len(models) == 3
    assert "openai/gpt-4o-mini" in models
    assert "anthropic/claude-3-haiku" in models
    assert "x-ai/grok-3-mini" in models


def test_load_active_models_missing_file(tmp_path, monkeypatch, caplog):
    """Test graceful handling of missing 02_activate.json"""
    run_id = "missing_20250101_120000"
    monkeypatch.setattr(
        "ultrai.api.Path",
        lambda p: tmp_path / p if "runs" in p else Path(p),
    )

    models = _load_active_models(run_id)

    assert models == []
    assert "02_activate.json not found" in caplog.text


def test_r1_prepopulation_creates_pending_steps(mock_run_dir):
    """Test R1 prepopulation creates pending steps for all models"""
    run_id, _ = mock_run_dir

    # Clear progress tracker
    if run_id in progress_tracker:
        del progress_tracker[run_id]

    _prepopulate_r1_steps(run_id)

    assert run_id in progress_tracker
    steps = progress_tracker[run_id]["steps"]

    # Should have 3 R1 steps (one per model)
    r1_steps = [s for s in steps if s["text"].startswith("R1:")]
    assert len(r1_steps) == 3

    # All should be pending with 0% progress
    for step in r1_steps:
        assert step["status"] == "pending"
        assert step["progress"] == 0


def test_r2_prepopulation_creates_pending_steps(mock_run_dir):
    """Test R2 prepopulation creates pending steps for all models"""
    run_id, _ = mock_run_dir

    # Clear progress tracker
    if run_id in progress_tracker:
        del progress_tracker[run_id]

    _prepopulate_r2_steps(run_id)

    assert run_id in progress_tracker
    steps = progress_tracker[run_id]["steps"]

    # Should have 3 R2 steps (one per model)
    r2_steps = [s for s in steps if s["text"].startswith("R2:")]
    assert len(r2_steps) == 3

    # All should be pending with 0% progress and include 'revising'
    for step in r2_steps:
        assert step["status"] == "pending"
        assert step["progress"] == 0
        assert "revising" in step["text"]


def test_prepopulation_sequence(mock_run_dir):
    """Test that R1 prepopulation happens before R2"""
    run_id, _ = mock_run_dir

    # Clear progress tracker
    if run_id in progress_tracker:
        del progress_tracker[run_id]

    # Prepopulate R1, then R2 (as in actual pipeline)
    _prepopulate_r1_steps(run_id)
    _prepopulate_r2_steps(run_id)

    steps = progress_tracker[run_id]["steps"]

    # First 3 steps should be R1
    assert all(s["text"].startswith("R1:") for s in steps[:3])
    # Next 3 steps should be R2
    assert all(s["text"].startswith("R2:") for s in steps[3:6])
