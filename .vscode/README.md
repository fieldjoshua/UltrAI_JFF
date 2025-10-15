# Cursor/VS Code Configuration

This directory contains configuration for Cursor/VS Code integration with the UltrAI test suite.

## Quick Access Guide

### 🔬 Test Explorer (Individual Tests)
**Access:** Click the **beaker icon** 🧪 in left sidebar
- View all tests in tree structure
- Click ▶️ to run any individual test
- See ✓ (pass) or ✗ (fail) inline
- Filter by PR phase using test markers

### ⚙️ Tasks Menu (Test Commands)
**Access:** `Cmd+Shift+P` → type "Tasks: Run Task"
- Run entire test suite or specific PR phases
- Get narrative summaries or dashboards
- Generate HTML reports
- Watch tests continuously

### 🐛 Debug Panel (Debugging)
**Access:** `Cmd+Shift+D` or click debug icon in left sidebar
- Set breakpoints and step through code
- Debug specific PR phases
- Debug with narrative output
- Inspect variables during test execution

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

### Quick Access Test Commands

**General Test Commands:**
- **Run All Tests** - Run entire test suite
- **Test Summary Dashboard** - Color-coded status by PR phase
- **List All Tests** - See all test descriptions
- **Test with Narrative** - Story-like test summaries
- **Test Verbose** - Detailed output with full context
- **Test Real API Only** - Run only tests requiring OpenRouter API
- **Show Failed Tests Only** - Stop on first failure
- **Generate Test Report** - Create HTML test report
- **Watch Tests** - Continuous testing on file changes

**Run Tests by PR Phase:**
- **Run PR 00 Tests** - Repository Structure
- **Run PR 01 Tests** - System Readiness
- **Run PR 02 Tests** - User Input Selection
- **Run PR 03 Tests** - Active LLMs Preparation
- **Run PR 04 Tests** - Initial Round
- **Run PR 05 Tests** - Meta Round
- **Run PR 06 Tests** - UltrAI Synthesis
- **Run PR 07 Tests** - Add-ons Processing
- **Run PR 08 Tests** - Statistics
- **Run PR 09 Tests** - Final Delivery
- **Run PR 10 Tests** - Error Handling

## Debug Configurations (Cmd+Shift+D → Run & Debug panel)

**General Debugging:**
- **Python: Current File** - Run/debug any Python file
- **Python: Debug Tests** - Debug all tests with breakpoints
- **Python: Debug Current Test File** - Debug the test file you have open

**Specialized Test Debugging:**
- **Python: Debug Tests with Narrative** - Debug with story-like summaries
- **Python: Debug PR 00 Tests** - Debug Repository Structure tests
- **Python: Debug PR 01 Tests** - Debug System Readiness tests
- **Python: Debug Real API Tests** - Debug tests hitting OpenRouter API

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
