# GitHub Branch Protection Rules

## Main Branch Protection

Configure the following protection rules for the `main` branch in GitHub:

### Required Status Checks
- ✅ **Require status checks to pass before merging**
  - Required checks:
    - `ci tests` - All tests must pass (excluding `test_timeout_display.py`)

### Pull Request Requirements
- ✅ **Require a pull request before merging**
  - Required approvals: 0 (since this is a solo project, but can be increased if collaborators join)
  - Dismiss stale pull request approvals when new commits are pushed

### Additional Restrictions
- ✅ **Require conversation resolution before merging**
- ✅ **Do not allow bypassing the above settings**

### Smart Test Selection Policy
CI runs **ONLY tests relevant to changed files** for speed:
- Changed file detection maps to PR markers (pr01-pr09)
- Example: `ultrai/user_input.py` changed → runs only `@pytest.mark.pr02` tests (~12 tests)
- Example: `ultrai/initial_round.py` changed → runs only `@pytest.mark.pr04` tests (~15 tests)
- If test infrastructure changes (`conftest.py`, `pyproject.toml`) → runs ALL 132 tests
- Always excludes `test_timeout_display.py` (intentional 15-120s timeouts for demo)
- This keeps CI fast (10-30 tests per typical PR instead of 132)

### How to Configure
1. Go to repository **Settings** → **Branches**
2. Click **Add branch protection rule**
3. Enter branch name pattern: `main`
4. Check the boxes as listed above
5. Click **Create** or **Save changes**

## Why These Rules?
- **Prevents accidental merges** of broken code
- **Ensures comprehensive testing** - all code paths are validated
- **Maintains code quality** - all tests must pass before merge
- **Fast CI** - only excludes intentional timeout demos, runs all other tests
