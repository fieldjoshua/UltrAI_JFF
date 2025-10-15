"""
Tests for PR 05 — Meta Round (R2)

REAL tests (NO MOCKS) - uses actual OpenRouter API calls.

Testing Endpoints (from PR 05 template):
1. 04_meta.json exists
2. items have round=META and align with initial LLMs
3. 04_meta_status.json.details.count matches item count
"""

import json
import os
from pathlib import Path
import pytest

from ultrai.system_readiness import check_system_readiness
from ultrai.user_input import collect_user_inputs
from ultrai.active_llms import prepare_active_llms
from ultrai.initial_round import execute_initial_round
from ultrai.meta_round import execute_meta_round, MetaRoundError


skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_04_meta_json_exists(tmp_path, monkeypatch):
    """Test that 04_meta.json artifact is created"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup: PR01→PR04
    ready = await check_system_readiness()
    run_id = ready["run_id"]
    collect_user_inputs(
        query="Meta test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    # Execute R2
    await execute_meta_round(run_id)

    runs_dir = Path(f"runs/{run_id}")
    meta_path = runs_dir / "04_meta.json"
    assert meta_path.exists(), "04_meta.json artifact must exist"

    # Verify parsable and non-empty
    with open(meta_path, "r") as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) > 0


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_items_have_required_fields_and_round_meta(
    tmp_path,
    monkeypatch,
):
    """
    Test that META items have round=META, model, text, ms
    and align with ACTIVE
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]
    collect_user_inputs(
        query="Revise based on peers",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    active = prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    result = await execute_meta_round(run_id)

    # Round & fields
    for item in result["responses"]:
        assert item.get("round") == "META"
        assert isinstance(item.get("model"), str)
        assert isinstance(item.get("text"), str)
        assert isinstance(item.get("ms"), int) and item.get("ms") >= 0

    # Models alignment
    active_models = set(active["activeList"])
    response_models = set(
        i.get("model") for i in result["responses"]
    )
    assert response_models == active_models


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_status_count_matches_meta_count(tmp_path, monkeypatch):
    """Test that 04_meta_status.json.details.count matches item count"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]
    collect_user_inputs(
        query="Check counts",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    meta = await execute_meta_round(run_id)

    status_path = Path(f"runs/{run_id}/04_meta_status.json")
    assert status_path.exists(), "04_meta_status.json must exist"

    with open(status_path, "r") as f:
        status = json.load(f)

    assert status.get("details", {}).get("count") == len(meta["responses"])


# Comprehensive Output Validation Tests (PR 04 consistency)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_exact_output_count_matches_active_count(tmp_path, monkeypatch):
    """Test that number of META outputs exactly matches number of ACTIVE models"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Test META count",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    active_result = prepare_active_llms(run_id)
    active_count = len(active_result['activeList'])

    await execute_initial_round(run_id)

    # Execute R2
    result = await execute_meta_round(run_id)

    # Should have exactly one META response per ACTIVE model
    assert len(result['responses']) == active_count, \
        f"Should have exactly {active_count} META responses, got {len(result['responses'])}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_one_meta_response_per_active_model(tmp_path, monkeypatch):
    """Test that each ACTIVE model produces exactly one META response"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="META test unique",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    active_result = prepare_active_llms(run_id)

    await execute_initial_round(run_id)

    # Execute R2
    result = await execute_meta_round(run_id)

    # Count META responses per model
    model_counts = {}
    for response in result['responses']:
        model = response['model']
        model_counts[model] = model_counts.get(model, 0) + 1

    # Each ACTIVE model should appear exactly once
    for model in active_result['activeList']:
        assert model in model_counts, f"Model {model} missing from META responses"
        assert model_counts[model] == 1, \
            f"Model {model} has {model_counts[model]} META responses, expected 1"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_all_meta_responses_are_from_active_models(tmp_path, monkeypatch):
    """Test that all META responses come from ACTIVE models only"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Verify META sources",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    active_result = prepare_active_llms(run_id)
    active_models = set(active_result['activeList'])

    await execute_initial_round(run_id)

    # Execute R2
    result = await execute_meta_round(run_id)

    # Verify every META response is from an ACTIVE model
    for response in result['responses']:
        assert response['model'] in active_models, \
            f"META response from non-ACTIVE model: {response['model']}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_all_meta_responses_have_meta_round(tmp_path, monkeypatch):
    """Test that all responses have round=META"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="Check META round field",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    # Execute R2
    result = await execute_meta_round(run_id)

    # Every response should have round="META"
    for response in result['responses']:
        assert response.get('round') == 'META', \
            f"Response from {response['model']} has round={response.get('round')}, expected META"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_no_duplicate_meta_model_responses(tmp_path, monkeypatch):
    """Test that no model appears twice in META responses"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="No duplicates test",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    # Execute R2
    result = await execute_meta_round(run_id)

    # Extract all models
    models = [r['model'] for r in result['responses']]

    # Check for duplicates
    unique_models = set(models)
    assert len(models) == len(unique_models), \
        f"Duplicate models found in META: {[m for m in models if models.count(m) > 1]}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_meta_responses_reference_peer_drafts(tmp_path, monkeypatch):
    """Test that META responses actually revise based on peer INITIAL drafts"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup with a query that should produce different perspectives
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    collect_user_inputs(
        query="What is the best programming language?",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    # Execute R2
    result = await execute_meta_round(run_id)

    # Verify META responses show revision behavior
    # Look for keywords that indicate peer review/revision
    revision_keywords = [
        'review', 'peer', 'draft', 'revised', 'contradict',
        'agree', 'disagree', 'other', 'consensus', 'different'
    ]

    meta_with_revision = 0
    for response in result['responses']:
        if not response.get('error'):
            text_lower = response['text'].lower()
            # Check if response references peer review process
            if any(keyword in text_lower for keyword in revision_keywords):
                meta_with_revision += 1

    # At least some META responses should show evidence of peer review
    assert meta_with_revision > 0, \
        "META responses should reference peer drafts or revision process"


# Variable Rate Limiting Integration Tests


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_meta_round_uses_variable_concurrency(tmp_path, monkeypatch):
    """Test that META round uses variable rate limiting based on context"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup
    ready_result = await check_system_readiness()
    run_id = ready_result['run_id']

    # Use a query that will produce lengthy initial responses
    collect_user_inputs(
        query="Explain quantum computing in detail",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id
    )

    prepare_active_llms(run_id)
    await execute_initial_round(run_id)

    # Execute R2
    await execute_meta_round(run_id)

    # Verify concurrency limit in status file
    status_path = Path(f"runs/{run_id}/04_meta_status.json")
    with open(status_path, "r") as f:
        status = json.load(f)

    assert "concurrency_limit" in status["details"], \
        "META status should include concurrency_limit"

    # Concurrency limit should be between 1 and 50
    limit = status["details"]["concurrency_limit"]
    assert 1 <= limit <= 50, \
        f"Concurrency limit should be 1-50, got {limit}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_meta_round_concurrency_varies_with_context(tmp_path, monkeypatch):
    """Test that longer peer contexts result in lower concurrency"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Test 1: Short query (should get higher concurrency)
    ready_result = await check_system_readiness()
    run_id_short = ready_result['run_id']

    collect_user_inputs(
        query="What is 2+2?",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id_short
    )

    prepare_active_llms(run_id_short)
    await execute_initial_round(run_id_short)
    await execute_meta_round(run_id_short)

    status_path_short = Path(f"runs/{run_id_short}/04_meta_status.json")
    with open(status_path_short, "r") as f:
        status_short = json.load(f)
    limit_short = status_short["details"]["concurrency_limit"]

    # Test 2: Long query (should get lower concurrency)
    ready_result = await check_system_readiness()
    run_id_long = ready_result['run_id']

    long_query = "Explain the history of computer science " * 50
    collect_user_inputs(
        query=long_query,
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id_long
    )

    prepare_active_llms(run_id_long)
    await execute_initial_round(run_id_long)
    await execute_meta_round(run_id_long)

    status_path_long = Path(f"runs/{run_id_long}/04_meta_status.json")
    with open(status_path_long, "r") as f:
        status_long = json.load(f)
    limit_long = status_long["details"]["concurrency_limit"]

    # Long query should have lower or equal concurrency
    assert limit_long <= limit_short, \
        f"Long query concurrency ({limit_long}) should be <= short query ({limit_short})"


# Error Handling Tests


def test_missing_initial_json_raises_error(tmp_path, monkeypatch):
    """Test error when 03_initial.json is missing"""
    monkeypatch.chdir(tmp_path)

    run_id = "test_meta_missing_initial"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create activate but no initial file
    activate_data = {
        "activeList": ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"],
        "quorum": 2,
        "cocktail": "SPEEDY"
    }
    with open(runs_dir / "02_activate.json", "w") as f:
        json.dump(activate_data, f)

    async def test():
        with pytest.raises(MetaRoundError) as exc_info:
            await execute_meta_round(run_id)
        assert "Missing 03_initial.json" in str(exc_info.value)

    import asyncio
    asyncio.run(test())
    # End of PR 05 meta round tests

