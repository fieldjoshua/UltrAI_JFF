"""
Real API test for R1 (INITIAL round) - NO MOCKS
Tests actual OpenRouter API calls with PREMIUM COCKTAIL models.

This test verifies:
1. Real OpenRouter API integration
2. PREMIUM COCKTAIL model responses
3. Actual artifact generation in runs/<RunID>/
4. Proper INITIAL round data structure
"""

import pytest
import json
import os
from pathlib import Path
from ultrai.initial_round import execute_initial_round
from ultrai.user_input import collect_user_inputs
from ultrai.system_readiness import check_system_readiness
from ultrai.active_llms import prepare_active_llms


@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
async def test_real_r1_premium_cocktail():
    """
    Test R1 (INITIAL round) with real OpenRouter API calls using
    PREMIUM COCKTAIL.

    This test:
    - Uses real OpenRouter API (no mocks)
    - Tests PREMIUM COCKTAIL models
    - Verifies actual artifact generation
    - Confirms proper INITIAL round structure
    """
    # Skip if no API key
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip(
            "OPENROUTER_API_KEY not set - skipping real API test"
        )

    # Test query
    test_query = (
        "What are the key principles of effective software architecture?"
    )

    # Step 1: Collect user inputs (PREMIUM COCKTAIL)
    inputs = collect_user_inputs(
        query=test_query,
        analysis="Synthesis",
        cocktail="PREMIUM"
    )
    run_id = inputs["run_id"]

    # Verify inputs were created
    inputs_path = Path(f"runs/{run_id}/01_inputs.json")
    assert inputs_path.exists(), (
        f"01_inputs.json not created for run {run_id}"
    )

    with open(inputs_path, "r") as f:
        inputs_data = json.load(f)
        assert inputs_data["COCKTAIL"] == "PREMIUM"
        assert inputs_data["QUERY"] == test_query

    # Step 2: System readiness check
    readiness_result = await check_system_readiness(run_id)
    assert readiness_result["status"] == "ready"
    assert len(readiness_result["readyList"]) >= 2, (
        "Need at least 2 READY models"
    )

    # Verify 00_ready.json was created
    ready_path = Path(f"runs/{run_id}/00_ready.json")
    assert ready_path.exists(), (
        f"00_ready.json not created for run {run_id}"
    )

    # Step 3: Prepare ACTIVE LLMs
    active_result = prepare_active_llms(run_id)
    assert active_result["quorum"] == 2
    assert len(active_result["activeList"]) >= 2, (
        "Need at least 2 ACTIVE models"
    )

    # Verify PREMIUM COCKTAIL models are in activeList
    premium_models = [
        "anthropic/claude-3.7-sonnet",
        "openai/chatgpt-4o-latest",
        "meta-llama/llama-3.3-70b-instruct"
    ]

    # At least one PREMIUM model should be ACTIVE
    active_models = active_result["activeList"]
    premium_active = [
        model for model in premium_models if model in active_models
    ]
    assert len(premium_active) > 0, (
        f"No PREMIUM models ACTIVE. Active: {active_models}"
    )

    # Verify 02_activate.json was created
    activate_path = Path(f"runs/{run_id}/02_activate.json")
    assert activate_path.exists(), (
        f"02_activate.json not created for run {run_id}"
    )

    # Step 4: Execute R1 (INITIAL round) with real API calls
    print("\n🧪 Testing R1 with real OpenRouter API calls...")
    print(f"Run ID: {run_id}")
    print(f"Active models: {active_models}")
    print(f"Query: {test_query}")

    initial_result = await execute_initial_round(run_id)

    # Verify R1 execution results
    assert initial_result["status"] == "completed"
    assert initial_result["count"] >= 2, (
        "Need at least 2 INITIAL responses"
    )
    assert initial_result["avg_ms"] > 0, (
        "Response time should be positive"
    )

    # Verify 03_initial.json was created
    initial_path = Path(f"runs/{run_id}/03_initial.json")
    assert initial_path.exists(), (
        f"03_initial.json not created for run {run_id}"
    )

    # Verify 03_initial_status.json was created
    initial_status_path = Path(f"runs/{run_id}/03_initial_status.json")
    assert initial_status_path.exists(), (
        f"03_initial_status.json not created for run {run_id}"
    )

    # Verify INITIAL responses structure
    with open(initial_path, "r") as f:
        initial_responses = json.load(f)

    assert isinstance(initial_responses, list), (
        "INITIAL responses should be a list"
    )
    assert len(initial_responses) >= 2, (
        "Need at least 2 INITIAL responses"
    )

    for response in initial_responses:
        # Verify required fields
        assert "round" in response, "Missing 'round' field"
        assert response["round"] == "INITIAL", (
            f"Expected 'INITIAL', got '{response['round']}'"
        )
        assert "model" in response, "Missing 'model' field"
        assert "text" in response, "Missing 'text' field"
        assert "ms" in response, "Missing 'ms' field"

        # Verify model is in activeList
        assert response["model"] in active_models, (
            f"Model {response['model']} not in activeList"
        )

        # Verify response text is not empty
        assert len(response["text"].strip()) > 0, (
            "Response text should not be empty"
        )

        # Verify response time is reasonable (less than 60 seconds)
        assert response["ms"] < 60000, (
            f"Response time too long: {response['ms']}ms"
        )

        print(
            f"✅ {response['model']}: {response['ms']}ms, "
            f"{len(response['text'])} chars"
        )

    # Verify INITIAL status structure
    with open(initial_status_path, "r") as f:
        initial_status = json.load(f)

    assert "concurrency_limit" in initial_status, (
        "Missing 'concurrency_limit' in status"
    )
    assert initial_status["concurrency_limit"] > 0, (
        "Concurrency limit should be positive"
    )

    print("\n✅ R1 (INITIAL round) test completed successfully!")
    print(f"   - Run ID: {run_id}")
    print(f"   - Responses: {len(initial_responses)}")
    print(f"   - Avg time: {initial_result['avg_ms']:.0f}ms")
    print(f"   - Concurrency: {initial_status['concurrency_limit']}")

    # Cleanup: Remove test run directory
    import shutil
    runs_dir = Path(f"runs/{run_id}")
    if runs_dir.exists():
        shutil.rmtree(runs_dir)
        print(f"🧹 Cleaned up test run: {run_id}")


@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
async def test_real_r1_premium_models_availability():
    """
    Test that PREMIUM COCKTAIL models are actually available via
    OpenRouter.

    This verifies the specific models in PREMIUM COCKTAIL can be
    reached.
    """
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip(
            "OPENROUTER_API_KEY not set - skipping real API test"
        )

    # Test with a simple query to verify model availability
    test_query = "Hello, respond with 'API test successful'"

    inputs = collect_user_inputs(
        query=test_query,
        cocktail="PREMIUM"
    )
    run_id = inputs["run_id"]

    # System readiness
    await check_system_readiness(run_id)

    # Prepare active LLMs
    active_result = prepare_active_llms(run_id)
    active_models = active_result["activeList"]

    # Execute R1
    initial_result = await execute_initial_round(run_id)

    # Verify at least one PREMIUM model responded
    assert initial_result["count"] > 0, "No models responded"

    # Check responses
    initial_path = Path(f"runs/{run_id}/03_initial.json")
    with open(initial_path, "r") as f:
        responses = json.load(f)

    # Verify at least one response contains expected text
    success_responses = [
        resp for resp in responses
        if "API test successful" in resp["text"]
    ]
    assert len(success_responses) > 0, (
        "No successful API responses found"
    )

    print("✅ PREMIUM models API test successful!")
    print(f"   - Active models: {active_models}")
    print(f"   - Successful responses: {len(success_responses)}")

    # Cleanup
    import shutil
    runs_dir = Path(f"runs/{run_id}")
    if runs_dir.exists():
        shutil.rmtree(runs_dir)
