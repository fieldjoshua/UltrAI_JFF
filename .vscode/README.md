# Cursor/VS Code Configuration

This directory contains configuration for Cursor/VS Code integration with the UltrAI test suite.

## Test Explorer Integration

### Accessing Test Explorer in Cursor

1. **Open Test Explorer Panel**:
   - Click the beaker/flask icon in the left sidebar
   - Or press `Cmd+Shift+P` and search for "Testing: Focus on Test Explorer View"

2. **View Your Tests**:
   - All 8 tests will appear in a tree structure:
     - `test_repo_structure.py` (3 tests) - PR 00
     - `test_system_readiness.py` (5 tests) - PR 01

3. **Run Tests from UI**:
   - Click the ▶️ play button next to any test to run it
   - Click the 🔄 refresh button to discover new tests
   - Right-click on tests for more options (debug, run with coverage, etc.)

### Test Markers Visible

Tests are tagged with markers that show in the explorer:
- `@pytest.mark.pr00` - Repository Structure tests
- `@pytest.mark.pr01` - System Readiness tests
- `@pytest.mark.real_api` - Tests requiring OpenRouter API key

## Tasks (Cmd+Shift+P → "Tasks: Run Task")

Quick access to test commands:
- **Run All Tests** - `make test`
- **Test Summary Dashboard** - `make test-summary`
- **List All Tests** - `make list-tests`
- **Run PR 00 Tests** - `make test-pr00`
- **Run PR 01 Tests** - `make test-pr01`
- **Generate Test Report** - `make test-report`
- **Watch Tests** - `make test-watch` (continuous testing)

## Debug Configurations

Available in the Run & Debug panel (Cmd+Shift+D):
- **Python: Debug Tests** - Debug all tests
- **Python: Debug Current Test File** - Debug the test file you have open
- **Python: Current File** - Run/debug any Python file

## Settings Configured

- Python interpreter: `.venv/bin/python` (auto-selected)
- Pytest enabled and configured for test discovery
- Auto-discover tests on save
- Python path set to workspace folder
- Hidden: `__pycache__`, `.pytest_cache`, `*.egg-info`

## Quick Start

1. Open Cursor
2. Click the test beaker icon (left sidebar)
3. Tests should automatically appear
4. Click play button to run any test
5. See results inline with green ✓ or red ✗

## Troubleshooting

If tests don't appear:
1. Make sure `.venv` is active: `source .venv/bin/activate`
2. Reload window: `Cmd+Shift+P` → "Reload Window"
3. Manually discover tests: `Cmd+Shift+P` → "Testing: Refresh Tests"
4. Check Output panel → "Python Test Log" for errors
