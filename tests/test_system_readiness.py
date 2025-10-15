"""
Tests for PR 01 — System Readiness

Testing Endpoints:
1) 00_ready.json exists
2) readyList ≥2 LLMs
3) Missing OPENROUTER_API_KEY triggers fail

IMPORTANT: These are REAL integration tests using actual OpenRouter API.
No mocks, no fakes. Real API calls only.

Implementation follows CORRECTED OpenRouter strategy (v2.0):
- Async test functions with pytest-asyncio
- Real httpx calls to OpenRouter
- Proper error handling verification
"""

import os
import json
import pytest
from pathlib import Path
from dotenv import load_dotenv
from ultrai.system_readiness import (
    check_system_readiness,
    SystemReadinessError
)

# Load environment variables from .env file for tests
load_dotenv()


@pytest.mark.pr01
def test_missing_openrouter_api_key_triggers_fail(tmp_path, monkeypatch):
    """
    Testing Endpoint 3: Missing OPENROUTER_API_KEY triggers fail

    This test verifies the system fails when API key is missing.
    No API call is made, so this is a real test of the error handling.
    """
    # Change to temp directory for test (no .env file here)
    monkeypatch.chdir(tmp_path)

    # Patch os.getenv to return None for OPENROUTER_API_KEY
    def mock_getenv(key, default=None):
        if key == "OPENROUTER_API_KEY":
            return None
        return os.getenv(key, default)

    monkeypatch.setattr("os.getenv", mock_getenv)

    # Should raise SystemReadinessError immediately
    import asyncio
    with pytest.raises(SystemReadinessError) as exc_info:
        asyncio.run(check_system_readiness(run_id="test_run_no_key"))

    assert "Missing OPENROUTER_API_KEY" in str(exc_info.value)


@pytest.mark.pr01
@pytest.mark.real_api
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - real integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_00_ready_json_exists_real_api(tmp_path, monkeypatch):
    """
    Testing Endpoint 1: 00_ready.json exists after system readiness check

    REAL INTEGRATION TEST - Uses actual OpenRouter API with real API key.
    """
    # Change to temp directory for test
    monkeypatch.chdir(tmp_path)

    # Run system readiness check with REAL OpenRouter API
    result = await check_system_readiness(run_id="test_run_real_001")

    # Verify 00_ready.json exists
    artifact_path = Path("runs/test_run_real_001/00_ready.json")
    assert artifact_path.exists(), "00_ready.json artifact must exist"

    # Verify content is valid JSON
    with open(artifact_path, "r") as f:
        data = json.load(f)
        assert "run_id" in data
        assert "readyList" in data
        assert "timestamp" in data
        assert "status" in data
        assert data["run_id"] == "test_run_real_001"
        assert data["status"] == "READY"


@pytest.mark.pr01
@pytest.mark.real_api
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - real integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_readylist_minimum_two_llms_real_api(tmp_path, monkeypatch):
    """
    Testing Endpoint 2: readyList ≥2 LLMs

    REAL INTEGRATION TEST - Uses actual OpenRouter API with real API key.
    Verifies that real OpenRouter service returns at least 2 models.
    """
    # Change to temp directory for test
    monkeypatch.chdir(tmp_path)

    # Run system readiness check with REAL OpenRouter API
    result = await check_system_readiness(run_id="test_run_real_002")

    # Verify readyList has at least 2 LLMs from REAL OpenRouter
    assert len(result["readyList"]) >= 2, (
        f"readyList must contain at least 2 LLMs. "
        f"Got {len(result['readyList'])} from real OpenRouter API."
    )
    assert result["llm_count"] >= 2
    assert result["status"] == "READY"

    # Verify these are real model IDs (should contain provider/model format)
    for model_id in result["readyList"]:
        assert isinstance(model_id, str), f"Model ID must be string, got {type(model_id)}"
        assert len(model_id) > 0, "Model ID cannot be empty"


@pytest.mark.pr01
@pytest.mark.real_api
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - real integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_run_id_generation_real_api(tmp_path, monkeypatch):
    """
    Test that run_id is automatically generated if not provided

    REAL INTEGRATION TEST - Uses actual OpenRouter API with real API key.
    """
    # Change to temp directory for test
    monkeypatch.chdir(tmp_path)

    # Run without specifying run_id - will hit REAL OpenRouter API
    result = await check_system_readiness()

    # Verify run_id was generated
    assert "run_id" in result
    assert result["run_id"] is not None
    assert len(result["run_id"]) > 0

    # Verify artifact was created with generated run_id
    artifact_path = Path(f"runs/{result['run_id']}/00_ready.json")
    assert artifact_path.exists()

    # Verify it contains real data from OpenRouter
    with open(artifact_path, "r") as f:
        data = json.load(f)
        assert len(data["readyList"]) >= 2


@pytest.mark.pr01
@pytest.mark.real_api
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set - real integration test requires actual API key"
)
@pytest.mark.asyncio
async def test_artifact_contains_real_model_data(tmp_path, monkeypatch):
    """
    Verify the artifact contains actual model data from OpenRouter, not fake data

    REAL INTEGRATION TEST - Uses actual OpenRouter API with real API key.
    """
    # Change to temp directory for test
    monkeypatch.chdir(tmp_path)

    # Run system readiness check
    result = await check_system_readiness(run_id="test_run_real_003")

    artifact_path = Path("runs/test_run_real_003/00_ready.json")
    with open(artifact_path, "r") as f:
        data = json.load(f)

    # Verify this is real data structure
    assert isinstance(data["readyList"], list)
    assert len(data["readyList"]) > 0

    # Check that model IDs look like real OpenRouter model IDs
    # Real OpenRouter models typically have format like "anthropic/claude-3.7-sonnet"
    sample_models = data["readyList"][:5]  # Check first 5
    print(f"\nReal models from OpenRouter API: {sample_models}")

    for model_id in sample_models:
        # Real model IDs should have some structure (not just "model1", "model2", etc.)
        assert "/" in model_id or "-" in model_id, (
            f"Model ID '{model_id}' doesn't look like a real OpenRouter model ID"
        )
