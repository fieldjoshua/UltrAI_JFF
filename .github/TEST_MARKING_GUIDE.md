# Test Marking Guide for PR Phases

This guide shows exactly how to mark tests for each PR phase so they run correctly in CI.

## Quick Reference

| PR Phase | Marker | Files Changed | Example Test Count |
|----------|--------|---------------|-------------------|
| PR 00 | `@pytest.mark.pr00` | Repository structure | ~5 tests |
| PR 01 | `@pytest.mark.pr01` | `ultrai/system_readiness.py` | ~12 tests |
| PR 02 | `@pytest.mark.pr02` | `ultrai/user_input.py`, `ultrai/cli.py` | ~18 tests |
| PR 03 | `@pytest.mark.pr03` | `ultrai/active_llms.py` | ~11 tests |
| PR 04 | `@pytest.mark.pr04` | `ultrai/initial_round.py` | ~15 tests |
| PR 05 | `@pytest.mark.pr05` | `ultrai/meta_round.py` | ~10 tests |
| PR 06 | `@pytest.mark.pr06` | `ultrai/ultrai_synthesis.py` | ~8 tests |
| PR 08 | `@pytest.mark.pr08` | `ultrai/statistics.py` | ~6 tests |
| PR 09 | `@pytest.mark.pr09` | `ultrai/final_delivery.py` | ~7 tests |
| PR 10 | `@pytest.mark.pr10` | Error handling across modules | ~10 tests |

## How to Mark Tests

### Basic Test Marking

```python
import pytest

@pytest.mark.pr02  # <-- Add this marker
def test_user_input_validation():
    """Test that validates user input"""
    # Your test code here
    pass
```

### Multiple Markers

If a test covers multiple PR phases:

```python
@pytest.mark.pr02
@pytest.mark.integration  # Also mark as integration if applicable
def test_full_input_flow():
    """Test complete input collection flow"""
    pass
```

### API-Requiring Tests

For tests that need the OpenRouter API:

```python
@pytest.mark.pr04
@pytest.mark.skip_if_no_api_key  # Skip if no API key
@pytest.mark.asyncio  # If it's async
async def test_real_initial_round():
    """Test R1 with real API calls"""
    pass
```

### Timeout Tests

For tests with designated timeouts:

```python
@pytest.mark.pr04
@pytest.mark.t15  # Shows "TO-15" instead of "FAILED" if timeout
@pytest.mark.timeout(15)  # Actual 15s timeout
async def test_slow_api_endpoint():
    """Test that may timeout at 15 seconds"""
    pass
```

## Complete Examples by PR Phase

### PR 01: System Readiness

File: `tests/test_system_readiness.py`

```python
import pytest
import os

@pytest.mark.pr01
@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
async def test_openrouter_connection():
    """Test real OpenRouter API connection"""
    from ultrai.system_readiness import check_system_readiness

    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    result = await check_system_readiness()
    assert result['status'] == 'READY'
    assert result['llm_count'] >= 2


@pytest.mark.pr01
def test_missing_api_key_raises_error(monkeypatch):
    """Test error handling for missing API key"""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    from ultrai.system_readiness import SystemReadinessError, check_system_readiness

    with pytest.raises(SystemReadinessError):
        asyncio.run(check_system_readiness())
```

### PR 02: User Input Selection

File: `tests/test_user_input.py`

```python
import pytest
from pathlib import Path

@pytest.mark.pr02
def test_collect_user_inputs(tmp_path, monkeypatch):
    """Test collecting user inputs creates artifact"""
    monkeypatch.chdir(tmp_path)

    from ultrai.user_input import collect_user_inputs

    result = collect_user_inputs(
        query="Test query",
        cocktail="PREMIUM",
        run_id="test_001"
    )

    assert result["QUERY"] == "Test query"
    assert result["COCKTAIL"] == "PREMIUM"
    assert Path("runs/test_001/01_inputs.json").exists()


@pytest.mark.pr02
def test_invalid_cocktail_rejected(tmp_path, monkeypatch):
    """Test invalid cocktail raises error"""
    monkeypatch.chdir(tmp_path)

    from ultrai.user_input import collect_user_inputs, UserInputError

    with pytest.raises(UserInputError, match="COCKTAIL must be one of"):
        collect_user_inputs(
            query="Test",
            cocktail="INVALID"
        )
```

### PR 03: Active LLMs Preparation

File: `tests/test_active_llms.py`

```python
import pytest
import json
from pathlib import Path

@pytest.mark.pr03
def test_prepare_active_llms(tmp_path, monkeypatch):
    """Test active LLM preparation"""
    monkeypatch.chdir(tmp_path)

    # Setup prerequisite artifacts
    run_id = "test_003"
    runs_dir = Path(f"runs/{run_id}")
    runs_dir.mkdir(parents=True)

    # Create 00_ready.json
    with open(runs_dir / "00_ready.json", "w") as f:
        json.dump({
            "run_id": run_id,
            "readyList": ["openai/gpt-4o", "anthropic/claude-3.7-sonnet"],
            "status": "READY"
        }, f)

    # Create 01_inputs.json
    with open(runs_dir / "01_inputs.json", "w") as f:
        json.dump({
            "QUERY": "Test",
            "COCKTAIL": "PREMIUM"
        }, f)

    from ultrai.active_llms import prepare_active_llms

    result = prepare_active_llms(run_id)
    assert len(result['activeList']) >= 2
    assert result['quorum'] == 2
```

### PR 04: Initial Round (R1)

File: `tests/test_initial_round.py`

```python
import pytest

@pytest.mark.pr04
@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
@pytest.mark.t30  # May timeout at 30s
@pytest.mark.timeout(30)
async def test_execute_initial_round():
    """Test R1 execution with real API"""
    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    from ultrai.initial_round import execute_initial_round

    # Assumes run artifacts exist from previous phases
    run_id = "test_r1_001"
    result = await execute_initial_round(run_id)

    assert 'responses' in result
    assert len(result['responses']) >= 2
```

### PR 05: Meta Round (R2)

File: `tests/test_meta_round.py`

```python
import pytest

@pytest.mark.pr05
@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
async def test_meta_round_with_peer_context():
    """Test R2 includes peer context from R1"""
    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    from ultrai.meta_round import execute_meta_round

    run_id = "test_r2_001"
    result = await execute_meta_round(run_id)

    assert 'responses' in result
    # Verify META responses reference INITIAL responses
    for response in result['responses']:
        assert 'model' in response
```

### PR 06: UltrAI Synthesis (R3)

File: `tests/test_ultrai_synthesis.py`

```python
import pytest

@pytest.mark.pr06
@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
async def test_ultrai_synthesis():
    """Test R3 synthesis with neutral model"""
    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    from ultrai.ultrai_synthesis import execute_ultrai_synthesis

    run_id = "test_r3_001"
    result = await execute_ultrai_synthesis(run_id)

    assert 'result' in result
    assert 'text' in result['result']
    assert 'model' in result['result']
```

### PR 08: Statistics

File: `tests/test_statistics.py`

```python
import pytest

@pytest.mark.pr08
def test_generate_statistics(tmp_path, monkeypatch):
    """Test statistics generation"""
    monkeypatch.chdir(tmp_path)

    from ultrai.statistics import generate_statistics

    # Assumes run artifacts exist
    run_id = "test_stats_001"
    result = generate_statistics(run_id)

    assert 'INITIAL' in result
    assert 'META' in result
    assert 'ULTRAI' in result
```

### PR 09: Final Delivery

File: `tests/test_final_delivery.py`

```python
import pytest

@pytest.mark.pr09
def test_deliver_results(tmp_path, monkeypatch):
    """Test final delivery creates manifest"""
    monkeypatch.chdir(tmp_path)

    from ultrai.final_delivery import deliver_results

    run_id = "test_delivery_001"
    result = deliver_results(run_id)

    assert result['status'] == 'delivered'
    assert 'metadata' in result
```

### Integration Tests

File: `tests/test_integration.py`

```python
import pytest

@pytest.mark.integration
@pytest.mark.pr02
@pytest.mark.pr03
@pytest.mark.pr04  # Mark all phases this test covers
@pytest.mark.skip_if_no_api_key
@pytest.mark.asyncio
async def test_full_pipeline():
    """Test complete pipeline from input to delivery"""
    import os
    if not os.getenv("OPENROUTER_API_KEY"):
        pytest.skip("OPENROUTER_API_KEY not set")

    # Run full pipeline
    from ultrai.system_readiness import check_system_readiness
    from ultrai.user_input import collect_user_inputs
    # ... etc

    # Verify complete flow
    assert True  # Replace with actual assertions
```

## Running Tests Locally

### Run tests for specific PR:
```bash
# PR 02 tests only
pytest tests/ -m pr02 -v

# PR 04 tests only
pytest tests/ -m pr04 -v

# Multiple PR phases
pytest tests/ -m "pr02 or pr04" -v
```

### Run without API tests:
```bash
pytest tests/ -m "pr02 and not skip_if_no_api_key" -v
```

### Run only API tests:
```bash
pytest tests/ -m skip_if_no_api_key -v
```

## CI Behavior

When you change a file, CI automatically runs relevant tests:

| File Changed | Tests Run | Approximate Count |
|--------------|-----------|-------------------|
| `ultrai/user_input.py` | All `@pytest.mark.pr02` tests | ~18 tests |
| `ultrai/initial_round.py` | All `@pytest.mark.pr04` tests | ~15 tests |
| `tests/conftest.py` | ALL tests (safety) | ~132 tests |
| `pyproject.toml` | ALL tests (safety) | ~132 tests |

This keeps CI fast while ensuring comprehensive testing!
