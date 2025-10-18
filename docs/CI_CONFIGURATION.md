# CI Configuration - Smart Dependency Testing

## Overview

UltrAI_JFF uses a **hybrid smart CI system** that combines:
1. **PR marker-based testing** (unique to UltrAI methodology)
2. **Dependency detection** (finds files that import your changes)
3. **Parallel backend/frontend jobs** (both must pass)

This ensures **rigorous testing** while keeping PRs **fast and focused**.

---

## How It Works

### Two Parallel Jobs (Both Must Pass)

#### 1. Backend Tests (`test-backend`)

**Steps:**
1. **Detect changed Python files** in your PR
2. **Find dependencies** via import analysis:
   - Searches for `from ultrai.user_input import ...`
   - Searches for `import ultrai.user_input`
   - Finds all files that use your changed modules
3. **Map to PR markers** (pr01, pr02, ..., pr09)
4. **Run tests** for:
   - ✅ Direct changes (e.g., `test_user_input.py` if you changed `user_input.py`)
   - ✅ Dependencies (e.g., `test_cli.py` if it imports `user_input`)
5. **Fail PR** if any tests fail

#### 2. Frontend Tests (`test-frontend`)

**Steps:**
1. **Detect changed frontend files** (.ts, .tsx, .js, .jsx)
2. **Check if frontend tests exist** (will be added in PR 21+)
3. **Run frontend tests** when they exist
4. **Fail PR** if any tests fail

**Current Status**: Frontend scaffold only (PR 20), tests coming in PR 21+

---

## Real-World Examples

### Example 1: Change a Core Module

**You changed**: `ultrai/user_input.py`

**CI will run**:
- ✅ `tests/test_user_input.py` (direct test, pr02 marker)
- ✅ `tests/test_cli.py` (imports user_input, pr02 marker)
- ✅ Any other file that imports `ultrai.user_input`

**Result**: PR passes ONLY if all these tests pass

---

### Example 2: Change a Test Infrastructure File

**You changed**: `tests/conftest.py`

**CI will run**:
- ✅ **ALL backend tests** (core infrastructure affects everything)

**Result**: Full test suite must pass

---

### Example 3: Change Only Frontend

**You changed**: `frontend/src/App.jsx`

**CI will run**:
- ✅ Frontend tests (when they exist)
- ⏭️ Backend tests SKIPPED (no Python changes)

**Result**: Only frontend tests must pass

---

### Example 4: Change Frontend API Integration

**You changed**: `frontend/src/services/api.js` or `frontend/src/hooks/useUltrAI.js`

**CI will run**:
- ✅ Frontend tests (API client tests)
- ✅ Backend tests (tests for ultrai/api.py, ultrai/system_readiness.py, ultrai/user_input.py, etc.)

**Why**: Frontend API layer depends on backend endpoints - must verify integration

**Result**: Both frontend AND backend tests must pass

---

### Example 5: Change Only Documentation

**You changed**: `README.md`

**CI will run**:
- ⏭️ Backend tests SKIPPED (no .py changes)
- ⏭️ Frontend tests SKIPPED (no .ts/.tsx/.js/.jsx changes)

**Result**: PR auto-passes (no code changed)

---

## Files Modified

### 1. `.github/workflows/ci-enhanced.yml`

**New smart CI workflow** with:
- Lines 16-180: Backend test job with dependency detection
- Lines 182-280: Frontend test job with component awareness
- Both jobs run in parallel
- Both must pass for PR to merge

### 2. `.pre-commit-config.yaml`

**Simplified pre-commit hooks**:
- ✅ Ruff auto-formatting (never blocks commits)
- ✅ Trailing whitespace removal
- ✅ End-of-file fixer
- ✅ YAML syntax validation
- ✅ Merge conflict detection
- ❌ Removed: Secret scanning, security checks (moved to separate workflows if needed)

---

## How Dependency Detection Works

### Backend (Python)

Uses `grep` to search for imports in the entire codebase:

```bash
# If you changed ultrai/user_input.py
# CI searches for:
grep -r "from ultrai.user_input import"
grep -r "import ultrai.user_input"
grep -r "from ultrai import.*user_input"
```

**Result**: Finds all files that depend on `user_input.py`

### Bi-directional Frontend ↔ Backend Dependencies (PR 21+)

When frontend API integration files change, CI automatically tests backend endpoints:

```bash
# If you changed frontend/src/services/api.js or frontend/src/hooks/useUltrAI.js
# CI adds these backend modules to the test list:
- ultrai/api.py
- ultrai/system_readiness.py
- ultrai/user_input.py
- ultrai/active_llms.py
- ultrai/initial_round.py
- ultrai/meta_round.py
- ultrai/ultrai_synthesis.py
- ultrai/statistics.py
```

**Result**: Frontend API changes trigger backend API tests to verify integration

### Frontend (React/TypeScript)

When frontend tests exist (PR 21+), will use similar grep patterns:

```bash
# If you changed src/components/QueryForm.tsx
# CI will search for:
grep -r "from './QueryForm'"
grep -r "from '@/components/QueryForm'"
grep -r "import.*QueryForm"
```

**Result**: Finds all components that use `QueryForm.tsx`

---

## What Gets Tested vs What Doesn't

### ✅ Tests That Run

- Direct tests for files you changed
- Tests for files that **import** your changes
- Tests for files **affected by** your changes
- All dependencies in the dependency chain
- ALL tests if you changed core infrastructure (conftest.py, pyproject.toml)

### ❌ Tests That DON'T Run

- Unrelated modules you didn't touch
- Code that doesn't import your changes
- The entire test suite (unless core infrastructure changed)
- `test_timeout_display.py` (always excluded - intentional timeouts)

---

## PR Marker System (UltrAI Methodology)

UltrAI_JFF uses **phase-based PR markers** that map to the 10-phase structure:

| Marker | Phase | Files |
|--------|-------|-------|
| `pr01` | System Readiness | `ultrai/system_readiness.py` |
| `pr02` | User Input | `ultrai/user_input.py`, `ultrai/cli.py` |
| `pr03` | Active LLMs | `ultrai/active_llms.py` |
| `pr04` | Initial Round (R1) | `ultrai/initial_round.py` |
| `pr05` | Meta Round (R2) | `ultrai/meta_round.py` |
| `pr06` | UltrAI Synthesis (R3) | `ultrai/ultrai_synthesis.py` |
| `pr08` | Statistics | `ultrai/statistics.py` |
| `pr09` | Final Delivery | `ultrai/final_delivery.py` |

**How it works**:
1. CI detects which files changed (including dependencies)
2. Maps changed files → PR markers
3. Runs tests with those markers: `pytest -m "pr02 or pr04"`

---

## Migration from Old CI

### What Changed

**Old CI** (`.github/workflows/ci-tests.yml`):
- ✅ PR marker-based testing
- ❌ No dependency detection
- ❌ No frontend testing
- ❌ No pre-commit hooks

**New CI** (`.github/workflows/ci-enhanced.yml`):
- ✅ PR marker-based testing (kept!)
- ✅ Dependency detection via `grep` (added!)
- ✅ Frontend testing job (added!)
- ✅ Pre-commit hooks with Ruff (added!)

### Transition Plan

1. **Keep both workflows** during transition:
   - `ci-tests.yml` (old, currently active)
   - `ci-enhanced.yml` (new, being tested)

2. **Test new CI** on feature branches

3. **Switch to new CI** when confident:
   ```bash
   mv .github/workflows/ci-tests.yml .github/workflows/ci-tests.yml.disabled
   mv .github/workflows/ci-enhanced.yml .github/workflows/ci.yml
   ```

4. **Install pre-commit hooks**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

---

## Key Benefits

### 1. Rigorous Testing
- Tests all code **affected by your changes**
- Finds breaking changes in dependent modules
- Catches integration issues early

### 2. Fast PRs
- Only tests what **matters**
- Skips unrelated modules entirely
- Parallel backend/frontend jobs

### 3. Fair Accountability
- You're only responsible for what you **actually touched**
- Clear mapping: changed file → affected tests
- No surprise failures from unrelated code

### 4. Smart Detection
- Automatic dependency discovery via import analysis
- No manual test selection needed
- Adapts to your changes automatically

---

## Debugging CI Failures

### Backend Test Failure

**Check**:
1. Which PR markers ran? (shown in CI logs)
2. Which files were detected as changed?
3. Which dependencies were found?

**Common causes**:
- Breaking change in module interface
- Dependency uses old API
- Test expectations outdated

**Fix**:
- Update the changed module to be backward compatible
- OR update all dependent files
- OR update test expectations

### Frontend Test Failure

**Check**:
1. Which frontend files changed?
2. Do frontend tests exist? (PR 21+)
3. Are dependencies installed correctly?

**Common causes**:
- Component props changed
- Missing npm dependencies
- Test snapshots outdated

**Fix**:
- Update component interfaces
- Update test snapshots: `npm test -- -u`
- Install missing deps: `npm install`

---

## Advanced Configuration

### Run All Tests Locally

```bash
# Backend (all tests)
pytest tests/ -v --ignore=tests/test_timeout_display.py

# Backend (specific marker)
pytest tests/ -v -m pr02

# Frontend (when tests exist)
cd frontend && npm test
```

### Run Tests for Changed Files Only

```bash
# Get changed files
CHANGED=$(git diff --name-only main...HEAD | grep '\.py$')

# Run tests for those files
# (CI does this automatically with dependency detection)
```

### Enable Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Disable Pre-commit Hooks Temporarily

```bash
# Skip hooks for one commit
git commit -m "message" --no-verify

# Uninstall hooks
pre-commit uninstall
```

---

## Future Enhancements

### PR 21+ (Frontend Tests)
- Add Jest/Vitest test suite
- Component dependency detection
- Snapshot testing
- Coverage reporting

### PR 25+ (Deployment)
- Deploy previews for PRs
- E2E tests with Playwright
- Performance benchmarks
- Visual regression testing

---

## Troubleshooting

### "No tests run" but PR passes
- **Cause**: No Python or frontend code changed
- **Expected**: Documentation/config-only changes auto-pass
- **Action**: None needed (working as intended)

### "All tests run" instead of targeted subset
- **Cause**: Changed `conftest.py` or `pyproject.toml`
- **Expected**: Core infrastructure affects all tests
- **Action**: Ensure all tests pass before merging

### Dependency detection missed a file
- **Cause**: Non-standard import pattern
- **Fix**: Add import pattern to `grep` command in workflow
- **Example**: `from ultrai import user_input as ui` might be missed

### Pre-commit hook fails
- **Cause**: Ruff formatting or linting issue
- **Fix**: Run `ruff format .` and `ruff check --fix .`
- **Skip**: Use `git commit --no-verify` if urgent

---

## Support

Questions about CI configuration?
- Check CI logs in GitHub Actions tab
- Read this documentation
- Ask in PR comments
- File an issue with `[CI]` prefix

---

**CI Version**: Enhanced v1.0 (PR 20)
**Last Updated**: 2025-10-18
**Maintained By**: UltrAI_JFF Core Team
