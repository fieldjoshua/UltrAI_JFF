# Codebase Analysis Fixes - Tasks for Cursor AI

## Overview
Complete the remaining codebase fixes. Tasks 1-3 have been completed by Claude. Total estimated time for remaining tasks: 1 hour.

---

## ✅ COMPLETED BY CLAUDE

- ✅ **Task 1**: Fixed CLAUDE.md Model IDs (grok-2-1212 → grok-3-mini)
- ✅ **Task 2**: Fixed CLAUDE.md Polling Interval (2s → 100ms)
- ✅ **Task 3**: Added logging to prepopulation failures + split into _prepopulate_r1_steps() and _prepopulate_r2_steps()

---

## TASK 4: Fix meta_round.py Model Identity Loss (20 minutes)
**Priority**: MEDIUM
**Files**: `ultrai/meta_round.py`

### Current Issue
Uses `asyncio.as_completed()` which loses model identity when errors occur. Error responses show `"model": "unknown"`.

### Required Changes

Find lines ~244-265 in `ultrai/meta_round.py` and replace the `asyncio.as_completed()` pattern with `asyncio.gather()`:

**BEFORE:**
```python
tasks = {
    asyncio.create_task(query_openrouter_async(...)): model
    for model in active_models
}

results = []
for coro in asyncio.as_completed(tasks.keys()):
    try:
        response = await coro
        model = tasks[coro]
        # ... process response ...
    except Exception as e:
        model = tasks.get(coro, "unknown")  # <-- LOSES IDENTITY
        # ...
```

**AFTER:**
```python
# Create tasks with model identity preserved
tasks = [
    (model, query_openrouter_async(...))
    for model in active_models
]

# Execute all tasks and preserve model identity even on error
gathered = await asyncio.gather(
    *[task for _, task in tasks],
    return_exceptions=True
)

results = []
for (model, _), result in zip(tasks, gathered):
    if isinstance(result, Exception):
        logger.error(f"[{run_id}] R2: {model} failed: {result}")
        if model not in failed_models:
            failed_models.append(model)
        results.append({
            "model": model,  # <-- IDENTITY PRESERVED
            "round": "META",
            "text": f"Error: {type(result).__name__}",
            "ms": 0,
        })
    else:
        # Success case - process result normally
        # Calculate timing
        time_sec = ...  # get from existing code
        results.append({
            "model": model,
            "round": "META",
            "text": result,
            "ms": int(time_sec * 1000),
        })
```

### Important Notes
- Preserve all existing timing logic
- Keep the progress callback functionality
- Make sure `failed_models` list is still updated correctly
- Don't break the existing error handling for retries

### Verification
After making changes, search for `"unknown"` in meta_round.py - should not appear in model assignments.

---

## TASK 5: Extract Duplicate Model Loading Code (10 minutes)
**Priority**: LOW
**Files**: `ultrai/api.py`

### Current Issue
`_prepopulate_r1_steps()` and `_prepopulate_r2_steps()` both have identical logic for loading `02_activate.json`.

### Required Changes

**Add new helper function BEFORE `_prepopulate_r1_steps()` (around line 287):**

```python
def _load_active_models(run_id: str) -> list:
    """
    Load ACTIVE models from 02_activate.json.
    Returns empty list if file doesn't exist or activeList is empty.
    Logs warnings/errors appropriately.
    """
    from datetime import datetime
    import json
    from pathlib import Path
    import logging

    logger = logging.getLogger("uvicorn.error")

    activate_path = Path(f"runs/{run_id}/02_activate.json")
    if not activate_path.exists():
        logger.warning(f"[{run_id}] Model loading skipped: 02_activate.json not found")
        return []

    try:
        with open(activate_path, "r", encoding="utf-8") as f:
            activate_data = json.load(f)
            active_models = activate_data.get("activeList", [])

        if not active_models:
            logger.warning(f"[{run_id}] activeList is empty")
            return []

        logger.info(f"[{run_id}] Loaded {len(active_models)} ACTIVE models")
        return active_models

    except Exception as e:
        logger.error(f"[{run_id}] Failed to load active models: {e}")
        return []
```

**Then simplify both `_prepopulate_r1_steps()` and `_prepopulate_r2_steps()`:**

Replace the entire model loading section (from `import logging` through `return # Skip on error`) with just:

```python
    from datetime import datetime

    # Use shared helper
    active_models = _load_active_models(run_id)
    if not active_models:
        return  # Already logged by helper
```

This removes ~20 lines of duplicated code from each function.

### Verification
Run a quick test to ensure prepopulation still works after refactoring.

---

## TASK 6: Add Prepopulation Tests (30 minutes)
**Priority**: MEDIUM
**Files**: Create `tests/test_prepopulation.py`

### Required Test Coverage

Create comprehensive test file with these tests:

```python
"""
Tests for R1/R2 step prepopulation logic.

Verifies that:
- Model steps are prepopulated at the right time
- Steps appear in correct sequence (parents before children)
- Prepopulation handles missing files gracefully
- Prepopulation logs appropriately
"""

import pytest
import json
from pathlib import Path
from ultrai.api import _prepopulate_r1_steps, _prepopulate_r2_steps, _load_active_models, progress_tracker


@pytest.fixture
def mock_run_dir(tmp_path, monkeypatch):
    """Create mock run directory with 02_activate.json"""
    run_id = "test_20250101_120000"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True)

    # Create mock 02_activate.json
    activate_data = {
        "activeList": ["openai/gpt-4o-mini", "anthropic/claude-3-haiku", "x-ai/grok-3-mini"],
        "cocktail": "SPEEDY",
        "quorum": 2,
    }
    activate_file = run_dir / "02_activate.json"
    activate_file.write_text(json.dumps(activate_data, indent=2))

    # Monkeypatch Path to use tmp_path
    original_path = Path
    def patched_path(p):
        if isinstance(p, str) and "runs" in p:
            return tmp_path / p
        return original_path(p)
    monkeypatch.setattr("ultrai.api.Path", patched_path)

    return run_id, run_dir


def test_load_active_models_success(mock_run_dir):
    """Test successful loading of active models"""
    run_id, run_dir = mock_run_dir
    models = _load_active_models(run_id)

    assert len(models) == 3
    assert "openai/gpt-4o-mini" in models
    assert "anthropic/claude-3-haiku" in models
    assert "x-ai/grok-3-mini" in models


def test_load_active_models_missing_file(tmp_path, monkeypatch, caplog):
    """Test graceful handling of missing 02_activate.json"""
    run_id = "missing_20250101_120000"
    original_path = Path
    def patched_path(p):
        if isinstance(p, str) and "runs" in p:
            return tmp_path / p
        return original_path(p)
    monkeypatch.setattr("ultrai.api.Path", patched_path)

    models = _load_active_models(run_id)

    assert models == []
    assert "02_activate.json not found" in caplog.text


def test_r1_prepopulation_creates_pending_steps(mock_run_dir):
    """Test R1 prepopulation creates pending steps for all models"""
    run_id, run_dir = mock_run_dir

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
    run_id, run_dir = mock_run_dir

    # Clear progress tracker
    if run_id in progress_tracker:
        del progress_tracker[run_id]

    _prepopulate_r2_steps(run_id)

    assert run_id in progress_tracker
    steps = progress_tracker[run_id]["steps"]

    # Should have 3 R2 steps (one per model)
    r2_steps = [s for s in steps if s["text"].startswith("R2:")]
    assert len(r2_steps) == 3

    # All should be pending with 0% progress
    for step in r2_steps:
        assert step["status"] == "pending"
        assert step["progress"] == 0
        assert "revising" in step["text"]


def test_prepopulation_sequence(mock_run_dir):
    """Test that R1 prepopulation happens before R2 in logical sequence"""
    run_id, run_dir = mock_run_dir

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
```

### Notes
- Import `progress_tracker` from `ultrai.api`
- Use `caplog` fixture for log assertion tests
- Use `tmp_path` and `monkeypatch` fixtures from pytest
- Make sure to clear `progress_tracker` between tests

### Verification
Run: `pytest tests/test_prepopulation.py -v`

All tests should pass.

---

## Success Criteria

After completing tasks 4-6:

- [ ] Meta round errors now show actual model name (not "unknown")
- [ ] No duplicated model loading code in api.py
- [ ] All prepopulation tests pass
- [ ] No regressions in existing tests

---

## Notes for Cursor AI

- **Task 4** requires careful async refactoring - preserve existing timing logic
- **Task 5** is straightforward DRY refactoring
- **Task 6** requires pytest knowledge - follow existing test patterns
- **Test after each task** - don't break existing functionality
- **If unsure**, stop and ask for clarification

---

## After Cursor Completes

Claude will:
1. Run **code-integrity-enforcer agent** to review all changes
2. Create comprehensive **PR** with all fixes (1-6)
3. Ensure all tests pass
4. Deploy to production

---

## Estimated Time

| Task | Time |
|------|------|
| 4. Fix meta_round identity | 20 min |
| 5. Extract duplicate code | 10 min |
| 6. Add prepopulation tests | 30 min |
| **TOTAL** | **60 min** |
