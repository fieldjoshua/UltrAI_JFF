"""
Tests for PR 04 — Initial Round (R1)

REAL tests (NO MOCKS) - uses actual OpenRouter API calls.

Testing Endpoints (from PR 04 template):
1. 03_initial.json exists
2. items have round=INITIAL, model, text, ms
3. 03_initial_status.json.details.count matches item count
"""

import json
import pytest
import os
from pathlib import Path
from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import (
    execute_initial_round,
    InitialRoundError,
    calculate_concurrency_limit
)


# Skip tests if no API key
skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set"
)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_03_initial_json_exists(tmp_path, monkeypatch):
    """Test that 03_initial.json artifact is created"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup: Run through all prerequisite phases
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="What is 2+2?",
        cocktail="SPEEDY",  # Use SPEEDY for faster responses
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify artifact exists
    runs_dir = Path(f"runs/{run_id}")
    artifact_path = runs_dir / "03_initial.json"
    assert artifact_path.exists(), "03_initial.json artifact must exist"

    # Verify artifact can be parsed
    with open(artifact_path, "r") as f:
        artifact_data = json.load(f)

    assert isinstance(artifact_data, list), "03_initial.json must be an array"
    assert len(artifact_data) > 0, "Must have at least one response"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_items_have_required_fields(tmp_path, monkeypatch):
    """Test that response items have round=INITIAL, model, text, ms"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Say 'hello'",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify each response has required fields
    for response in result['responses']:
        assert "round" in response, "Response must have 'round' field"
        assert response["round"] == "INITIAL", "round must be 'INITIAL'"

        assert "model" in response, "Response must have 'model' field"
        assert isinstance(response["model"], str), "model must be a string"

        assert "text" in response, "Response must have 'text' field"
        assert isinstance(response["text"], str), "text must be a string"

        assert "ms" in response, "Response must have 'ms' field"
        assert isinstance(response["ms"], int), "ms must be an integer"
        assert response["ms"] >= 0, "ms must be non-negative"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_status_count_matches_response_count(tmp_path, monkeypatch):
    """Test that 03_initial_status.json.details.count matches item count"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Count to 3",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Load status file
    runs_dir = Path(f"runs/{run_id}")
    status_path = runs_dir / "03_initial_status.json"
    assert status_path.exists(), "03_initial_status.json must exist"

    with open(status_path, "r") as f:
        status_data = json.load(f)

    # Verify count matches
    assert "details" in status_data, "Status must have 'details' field"
    assert "count" in status_data["details"], "details must have 'count' field"

    actual_count = len(result['responses'])
    status_count = status_data["details"]["count"]

    assert status_count == actual_count, \
        f"Status count ({status_count}) must match response count ({actual_count})"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_multiple_models_respond(tmp_path, monkeypatch):
    """Test that multiple ACTIVE models all respond"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="What is your name?",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    active_result = prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify we got responses from all ACTIVE models
    active_models = set(active_result['activeList'])
    response_models = set(r['model'] for r in result['responses'] if not r.get('error'))

    # Should have at least 2 responses (quorum)
    assert len(result['responses']) >= 2, "Must have at least 2 responses"

    # Each active model should have responded (or errored)
    all_response_models = set(r['model'] for r in result['responses'])
    assert all_response_models == active_models, \
        "Should have response (or error) from each ACTIVE model"


def test_missing_activate_json_raises_error(tmp_path, monkeypatch):
    """Test error when 02_activate.json is missing"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_missing"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only create inputs, no activate file
    inputs_data = {
        "QUERY": "Test",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "PREMIUM",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    async def test():
        with pytest.raises(InitialRoundError) as exc_info:
            await execute_initial_round(run_id)
        assert "Missing 02_activate.json" in str(exc_info.value)

    import asyncio
    asyncio.run(test())


def test_missing_inputs_json_raises_error(tmp_path, monkeypatch):
    """Test error when 01_inputs.json is missing"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_missing_inputs"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only create activate, no inputs file
    activate_data = {
        "activeList": ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"],
        "quorum": 2,
        "cocktail": "SPEEDY"
    }
    with open(runs_dir / "02_activate.json", "w") as f:
        json.dump(activate_data, f)

    async def test():
        with pytest.raises(InitialRoundError) as exc_info:
            await execute_initial_round(run_id)
        assert "Missing 01_inputs.json" in str(exc_info.value)

    import asyncio
    asyncio.run(test())


def test_insufficient_active_models_raises_error(tmp_path, monkeypatch):
    """Test error when activeList has < 2 models"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_run_insufficient"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create activate with only 1 model
    activate_data = {
        "activeList": ["openai/gpt-4o-mini"],
        "quorum": 2,
        "cocktail": "SPEEDY"
    }
    with open(runs_dir / "02_activate.json", "w") as f:
        json.dump(activate_data, f)

    # Create inputs
    inputs_data = {
        "QUERY": "Test",
        "ANALYSIS": "Synthesis",
        "COCKTAIL": "SPEEDY",
        "ADDONS": []
    }
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump(inputs_data, f)

    async def test():
        with pytest.raises(InitialRoundError) as exc_info:
            await execute_initial_round(run_id)
        assert "Insufficient ACTIVE models" in str(exc_info.value)

    import asyncio
    asyncio.run(test())


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_responses_contain_text(tmp_path, monkeypatch):
    """Test that responses contain actual text content"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Say exactly: HELLO",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify responses contain text
    for response in result['responses']:
        if not response.get('error'):
            assert len(response["text"]) > 0, "Response text must not be empty"
            # Should contain some form of hello
            assert any(word in response["text"].lower() for word in ["hello", "hi"]), \
                "Response should acknowledge the query"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_timing_is_recorded(tmp_path, monkeypatch):
    """Test that response timing is recorded in milliseconds"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Quick test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify timing
    for response in result['responses']:
        if not response.get('error'):
            # Should have reasonable timing (> 0ms, < 60000ms for a simple query)
            assert response["ms"] > 0, "Response time must be positive"
            assert response["ms"] < 60000, "Response time should be under 60 seconds"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_metadata_includes_round_r1(tmp_path, monkeypatch):
    """Test that metadata includes round=R1"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Test query",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    result = await execute_initial_round(run_id)

    # Verify metadata
    assert "metadata" in result
    assert result["metadata"]["round"] == "R1"
    assert result["metadata"]["phase"] == "03_initial"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_status_file_structure(tmp_path, monkeypatch):
    """Test that status file has correct structure"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)

    # Execute R1
    await execute_initial_round(run_id)

    # Load and verify status file
    status_path = Path(f"runs/{run_id}/03_initial_status.json")
    with open(status_path, "r") as f:
        status = json.load(f)

    assert "status" in status
    assert status["status"] == "COMPLETED"

    assert "round" in status
    assert status["round"] == "R1"

    assert "details" in status
    assert "count" in status["details"]
    assert "models" in status["details"]
    assert isinstance(status["details"]["models"], list)

    assert "metadata" in status
    assert "run_id" in status["metadata"]
    assert "timestamp" in status["metadata"]


# Variable Rate Limiting Tests


def test_concurrency_limit_short_query():
    """Test that short queries get maximum concurrency"""
    short_query = "What is 2+2?"
    limit = calculate_concurrency_limit(short_query)
    assert limit == 50, "Short queries should get full concurrency (50)"


def test_concurrency_limit_medium_query():
    """Test that medium queries get reduced concurrency"""
    # Create a medium query (500 chars)
    medium_query = "x" * 500
    limit = calculate_concurrency_limit(medium_query)
    assert limit == 30, "Medium queries should get 60% concurrency (30)"


def test_concurrency_limit_long_query():
    """Test that long queries get low concurrency"""
    # Create a long query (2000 chars)
    long_query = "x" * 2000
    limit = calculate_concurrency_limit(long_query)
    assert limit == 15, "Long queries should get 30% concurrency (15)"


def test_concurrency_limit_very_long_query():
    """Test that very long queries get very low concurrency"""
    # Create a very long query (6000 chars)
    very_long_query = "x" * 6000
    limit = calculate_concurrency_limit(very_long_query)
    assert limit == 5, "Very long queries should get 10% concurrency (5)"


def test_concurrency_limit_with_single_attachment():
    """Test that queries with attachments get reduced concurrency"""
    query = "What is this image?"
    limit = calculate_concurrency_limit(
        query,
        has_attachments=True,
        attachment_count=1
    )
    # Short query (50) * attachment factor (0.5) = 25
    assert limit == 25, "Single attachment should reduce concurrency by 50%"


def test_concurrency_limit_with_multiple_attachments():
    """Test that queries with multiple attachments get very low concurrency"""
    query = "Compare these images"
    limit = calculate_concurrency_limit(
        query,
        has_attachments=True,
        attachment_count=3
    )
    # Short query (50) * attachment factor (0.25) = 12
    assert limit == 12, "Multiple attachments should reduce concurrency by 75%"


def test_concurrency_limit_with_many_attachments():
    """Test that queries with many attachments get minimal concurrency"""
    query = "Analyze all these documents"
    limit = calculate_concurrency_limit(
        query,
        has_attachments=True,
        attachment_count=5
    )
    # Short query (50) * attachment factor (0.1) = 5
    assert limit == 5, "Many attachments should reduce concurrency by 90%"


def test_concurrency_limit_long_query_with_attachments():
    """Test combined effect of long query and attachments"""
    long_query = "x" * 2000  # Long query
    limit = calculate_concurrency_limit(
        long_query,
        has_attachments=True,
        attachment_count=2
    )
    # Long query (15) * attachment factor (0.25) = 3.75 -> 3
    assert limit == 3, "Long query + attachments should have very low concurrency"


def test_concurrency_limit_minimum_value():
    """Test that concurrency limit never goes below 1"""
    very_long_query = "x" * 10000
    limit = calculate_concurrency_limit(
        very_long_query,
        has_attachments=True,
        attachment_count=10
    )
    assert limit >= 1, "Concurrency limit must be at least 1"


def test_concurrency_limit_maximum_value():
    """Test that concurrency limit never exceeds 50"""
    short_query = "Hi"
    limit = calculate_concurrency_limit(short_query)
    assert limit <= 50, "Concurrency limit must not exceed 50"


def test_concurrency_limit_empty_query():
    """Test that empty query gets full concurrency"""
    empty_query = ""
    limit = calculate_concurrency_limit(empty_query)
    assert limit == 50, "Empty query should get full concurrency"
