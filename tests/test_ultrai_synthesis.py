"""
Tests for PR 06 — UltrAI Synthesis (R3)

REAL tests (NO MOCKS) - uses actual OpenRouter API calls.

Testing Endpoints (from PR 06 template):
1) 05_ultrai.json exists; round=ULTRAI; model and neutralChosen present;
   text non-empty
2) 05_ultrai_status.json confirms neutral and model used
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


skip_if_no_api_key = pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set",
)


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_05_ultrai_json_exists_and_has_required_fields(
    tmp_path, monkeypatch
):
    """Test that 05_ultrai.json exists and has required fields."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    # Setup: PR01→PR05
    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Provide a concise synthesis about multi-LLM benefits.",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    # Execute R3
    await execute_ultrai_synthesis(run_id)

    runs_dir = Path(f"runs/{run_id}")
    synth_path = runs_dir / "05_ultrai.json"
    assert synth_path.exists(), "05_ultrai.json artifact must exist"

    with open(synth_path, "r") as f:
        data = json.load(f)

    assert data.get("round") == "ULTRAI"
    assert isinstance(data.get("model"), str) and len(data["model"]) > 0
    assert data.get("neutralChosen") == data.get("model")
    assert isinstance(data.get("text"), str) and len(data["text"]) > 0


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_05_ultrai_status_confirms_neutral_and_model(
    tmp_path, monkeypatch
):
    """Test that 05_ultrai_status.json confirms neutral and model used."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Summarize the prior meta drafts into one answer.",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    await execute_ultrai_synthesis(run_id)

    status_path = Path(f"runs/{run_id}/05_ultrai_status.json")
    assert status_path.exists(), "05_ultrai_status.json must exist"

    with open(status_path, "r") as f:
        status = json.load(f)

    assert status.get("round") == "R3"
    assert status.get("details", {}).get("neutral") is True
    assert isinstance(status.get("details", {}).get("model"), str)


# Comprehensive Output Validation Tests


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_neutral_model_selected_from_active_list(tmp_path, monkeypatch):
    """Test that neutral model is selected from ACTIVE list only."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test neutral selection",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    active_result = prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    # Neutral model must be from ACTIVE list
    active_set = set(active_result["activeList"])
    neutral_model = result["result"]["model"]

    assert neutral_model in active_set, \
        f"Neutral model {neutral_model} not in ACTIVE list {active_set}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_synthesis_contains_substantial_text(tmp_path, monkeypatch):
    """Test that synthesis produces substantial text content."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="What are the benefits of multi-LLM synthesis?",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    text = result["result"]["text"]
    assert isinstance(text, str), "Synthesis text must be string"
    assert len(text) > 0, "Synthesis text must be non-empty"
    # Substantial synthesis should be at least 50 characters
    assert len(text) >= 50, \
        f"Synthesis text too short: {len(text)} chars (expected >=50)"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_synthesis_stats_match_active_and_meta_counts(
    tmp_path, monkeypatch
):
    """Test that synthesis stats match ACTIVE and META counts."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test stats accuracy",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    active_result = prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    meta_result = await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    stats = result["result"]["stats"]
    assert stats["active_count"] == len(active_result["activeList"]), \
        f"Active count mismatch: {stats['active_count']} != {len(active_result['activeList'])}"
    assert stats["meta_count"] == len(meta_result["responses"]), \
        f"Meta count mismatch: {stats['meta_count']} != {len(meta_result['responses'])}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_model_and_neutral_chosen_match(tmp_path, monkeypatch):
    """Test that model and neutralChosen fields match."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test field consistency",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    synthesis = result["result"]
    assert synthesis["model"] == synthesis["neutralChosen"], \
        f"Model {synthesis['model']} != neutralChosen {synthesis['neutralChosen']}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_synthesis_round_is_ultrai(tmp_path, monkeypatch):
    """Test that synthesis has round=ULTRAI."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test round field",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    assert result["result"]["round"] == "ULTRAI", \
        f"Round should be ULTRAI, got {result['result']['round']}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_synthesis_reflects_meta_concurrency(tmp_path, monkeypatch):
    """Test that synthesis status reflects META concurrency limit."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test concurrency reflection",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    await execute_ultrai_synthesis(run_id)

    # Load META status
    meta_status_path = Path(f"runs/{run_id}/04_meta_status.json")
    with open(meta_status_path, "r") as f:
        meta_status = json.load(f)
    meta_concurrency = meta_status["details"]["concurrency_limit"]

    # Load ULTRAI status
    ultrai_status_path = Path(f"runs/{run_id}/05_ultrai_status.json")
    with open(ultrai_status_path, "r") as f:
        ultrai_status = json.load(f)

    # ULTRAI should reflect META's concurrency
    assert ultrai_status["details"]["concurrency_from_meta"] == meta_concurrency, \
        f"ULTRAI should reflect META concurrency {meta_concurrency}"


# Synthesis Quality Tests


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_synthesis_references_multiple_perspectives(tmp_path, monkeypatch):
    """Test that synthesis integrates multiple META perspectives."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    # Use a query that will produce diverse perspectives
    collect_user_inputs(
        query="What is the best approach to software testing?",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    text = result["result"]["text"].lower()

    # Look for synthesis keywords indicating integration
    synthesis_keywords = [
        'consensus', 'converge', 'agree', 'disagree', 'perspective',
        'synthesis', 'merge', 'combine', 'integrate', 'overall',
        'meta', 'draft', 'model'
    ]

    matches = sum(1 for keyword in synthesis_keywords if keyword in text)

    # Synthesis should show evidence of integration (at least 2 keywords)
    assert matches >= 2, \
        f"Synthesis should reference integration process (found {matches} keywords)"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_preferred_neutral_model_selection(tmp_path, monkeypatch):
    """Test that preferred ULTRA model is chosen when available in ACTIVE."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    # DEPTH cocktail has claude-3.7-sonnet as primary (top preference)
    collect_user_inputs(
        query="Test preferred neutral",
        cocktail="DEPTH",
        addons=[],
        run_id=run_id,
    )
    active_result = prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    result = await execute_ultrai_synthesis(run_id)

    neutral_model = result["result"]["neutralChosen"]

    # Import preference list to verify selection logic
    from ultrai.ultrai_synthesis import PREFERRED_ULTRA

    active_set = set(active_result["activeList"])

    # Find first preferred model in ACTIVE list
    expected_neutral = None
    for preferred in PREFERRED_ULTRA:
        if preferred in active_set:
            expected_neutral = preferred
            break

    # If no preferred model, should be first ACTIVE
    if expected_neutral is None:
        expected_neutral = active_result["activeList"][0]

    assert neutral_model == expected_neutral, \
        f"Expected neutral {expected_neutral}, got {neutral_model}"


# Error Handling Tests


def test_missing_meta_json_raises_error(tmp_path, monkeypatch):
    """Test error when 04_meta.json is missing."""
    monkeypatch.chdir(tmp_path)

    run_id = "test_ultrai_missing_meta"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create activate but no meta file
    activate_data = {
        "activeList": ["openai/gpt-4o-mini", "anthropic/claude-3.7-sonnet"],
        "quorum": 2,
        "cocktail": "SPEEDY"
    }
    with open(runs_dir / "02_activate.json", "w") as f:
        json.dump(activate_data, f)

    async def test():
        from ultrai.ultrai_synthesis import UltraiSynthesisError
        with pytest.raises(UltraiSynthesisError) as exc_info:
            await execute_ultrai_synthesis(run_id)
        assert "Missing 04_meta.json" in str(exc_info.value)

    import asyncio
    asyncio.run(test())


def test_insufficient_active_models_raises_error(tmp_path, monkeypatch):
    """Test error when fewer than 2 ACTIVE models."""
    monkeypatch.chdir(tmp_path)

    run_id = "test_ultrai_insufficient_active"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Only 1 ACTIVE model
    activate_data = {
        "activeList": ["openai/gpt-4o-mini"],
        "quorum": 1,
        "cocktail": "SPEEDY"
    }
    with open(runs_dir / "02_activate.json", "w") as f:
        json.dump(activate_data, f)

    # Create dummy meta file
    with open(runs_dir / "04_meta.json", "w") as f:
        json.dump([{"round": "META", "model": "openai/gpt-4o-mini", "text": "test"}], f)

    async def test():
        from ultrai.ultrai_synthesis import UltraiSynthesisError
        with pytest.raises(UltraiSynthesisError) as exc_info:
            await execute_ultrai_synthesis(run_id)
        assert "Insufficient ACTIVE models" in str(exc_info.value)

    import asyncio
    asyncio.run(test())


# Dynamic Timeout Tests


def test_timeout_calculation_short_context():
    """Test timeout for short META context."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Short context (< 1000 chars)
    context = "Short synthesis context" * 20  # ~460 chars
    timeout = calculate_synthesis_timeout(context, 2)

    assert timeout == 60.0, f"Short context should use 60s timeout, got {timeout}"


def test_timeout_calculation_medium_context():
    """Test timeout for medium META context."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Medium context (1000-3000 chars)
    context = "Medium synthesis context " * 50  # ~1250 chars
    timeout = calculate_synthesis_timeout(context, 2)

    assert timeout == 90.0, f"Medium context should use 90s timeout, got {timeout}"


def test_timeout_calculation_long_context():
    """Test timeout for long META context."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Long context (3000-5000 chars)
    context = "Long synthesis context " * 150  # ~3450 chars
    timeout = calculate_synthesis_timeout(context, 2)

    assert timeout == 120.0, f"Long context should use 120s timeout, got {timeout}"


def test_timeout_calculation_very_long_context():
    """Test timeout for very long META context."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Very long context (> 5000 chars)
    context = "Very long synthesis context " * 200  # ~5600 chars
    timeout = calculate_synthesis_timeout(context, 2)

    assert timeout == 180.0, f"Very long context should use 180s timeout, got {timeout}"


def test_timeout_calculation_many_meta_drafts():
    """Test timeout adjustment for many META drafts."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Long context with 4+ drafts (multiplier applied)
    context = "Long synthesis context " * 150  # ~3450 chars
    timeout = calculate_synthesis_timeout(context, 4)

    # 120s base * 1.2 = 144s
    assert timeout == 144.0, f"4+ drafts should multiply timeout by 1.2, got {timeout}"


def test_timeout_calculation_enforces_minimum():
    """Test that timeout enforces minimum of 60s."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Even with very short context, should be at least 60s
    context = "x"
    timeout = calculate_synthesis_timeout(context, 1)

    assert timeout >= 60.0, f"Timeout should be at least 60s, got {timeout}"


def test_timeout_calculation_enforces_maximum():
    """Test that timeout enforces maximum of 300s."""
    from ultrai.ultrai_synthesis import calculate_synthesis_timeout

    # Very long context with many drafts
    context = "x" * 10000  # 10k chars
    timeout = calculate_synthesis_timeout(context, 5)

    # Should cap at 300s even if calculation exceeds
    assert timeout <= 300.0, f"Timeout should cap at 300s, got {timeout}"


@skip_if_no_api_key
@pytest.mark.asyncio
async def test_synthesis_status_includes_timeout(tmp_path, monkeypatch):
    """Test that synthesis status includes timeout metadata."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY"))

    ready = await check_system_readiness()
    run_id = ready["run_id"]

    collect_user_inputs(
        query="Test timeout tracking",
        cocktail="SPEEDY",
        addons=[],
        run_id=run_id,
    )
    prepare_active_llms(run_id)
    await execute_initial_round(run_id)
    await execute_meta_round(run_id)

    await execute_ultrai_synthesis(run_id)

    # Load status
    status_path = Path(f"runs/{run_id}/05_ultrai_status.json")
    with open(status_path, "r") as f:
        status = json.load(f)

    # Should include timeout details
    assert "timeout" in status["details"], \
        "Status should include timeout"
    assert "context_length" in status["details"], \
        "Status should include context_length"
    assert "num_meta_drafts" in status["details"], \
        "Status should include num_meta_drafts"

    # Timeout should be in valid range
    timeout = status["details"]["timeout"]
    assert 60.0 <= timeout <= 300.0, \
        f"Timeout {timeout} should be in range 60-300s"
