# Cursor AI Safety Checklist
Quick reference for safe Cursor AI usage on UltrAI project

## Before Starting Each Session

- [ ] YOLO Mode is OFF (check Cursor settings)
- [ ] `.cursorrules` file is present and loaded
- [ ] Working directory is `/Users/joshuafield/projects/UltrAI_JFF/`
- [ ] Git status is clean (or known state documented)
- [ ] `OPENROUTER_API_KEY` is set in `.env`

## During Development

### ✅ Safe Operations (No Approval Needed)
- Reading any file in the project
- Running `make test-*` commands
- Running `npm run dev` (frontend dev server)
- Searching codebase with grep/glob
- Viewing git status/diff/log
- Reading documentation

### ⚠️  Requires Approval (Always Ask First)
- **Git**: commit, push, merge, reset, checkout, rebase
- **Install**: npm install, pip install, make install
- **Delete**: rm, rmdir, file deletions
- **Deploy**: Any production deployment to Render
- **Config**: Modifying Makefile, package.json, requirements.txt, .env
- **Bulk**: Operations touching >5 files

### 🛑 Never Do Without Explicit User Request
- Force push (`git push --force`)
- Delete branches (especially main/master)
- Modify `.git/` directory
- Create files outside project directory
- Use mock tests instead of real API tests
- Commit changes without running tests first

## Red Flags - STOP Immediately

🚨 **Emergency Stop Signals:**
- File paths repeating segments (`terminal/terminal/terminal...`)
- Entering "reevaluation" loops (2+ consecutive)
- Same error appearing 3+ times
- Commands failing with permission denied
- Git showing unexpected merge conflicts
- Unable to verify a critical assumption

**Action:** Stop, report state to user, request guidance.

## Anti-Hallucination Checklist

Before presenting information to user:
- [ ] Did I verify file existence? (not assuming)
- [ ] Did I read actual file contents? (not guessing)
- [ ] Did I check terminology against `trackers/names.md`?
- [ ] Did I cite specific file:line references?
- [ ] Am I being honest about uncertainty?

**If any NO → Go verify before responding**

## Git Safety Protocol

Before committing:
```bash
# 1. Show what's changed
git status
git diff

# 2. Run tests
make test-summary

# 3. Verify no secrets
grep -r "sk-" .  # Check for API keys
grep -r "OPENROUTER_API_KEY" .  # Should only be in .env

# 4. Check CLAUDE.md compliance
# - Terminology matches trackers/names.md?
# - Artifacts documented?
# - Tests exist for new features?

# 5. Get user approval to commit
```

Before pushing:
```bash
# ALWAYS required before production deploys
git log origin/main..HEAD  # Show what will be pushed
# Get explicit user approval
```

## Testing Safety

### Required Test Pattern
```python
import pytest
from ultrai.config import OPENROUTER_API_KEY

@pytest.mark.skipif(not OPENROUTER_API_KEY, reason="Requires API key")
def test_real_feature():
    """Test with REAL OpenRouter API - no mocks allowed."""
    # Must verify actual run artifacts exist
    # Must use real API calls
    # Must validate end-to-end workflow
```

### NEVER Do This
```python
# ❌ FORBIDDEN - User explicitly forbids mock tests
from unittest.mock import Mock, patch

@patch('ultrai.openrouter.call_llm')
def test_fake_feature(mock_call):
    mock_call.return_value = {"response": "fake"}
    # This is explicitly forbidden per user CLAUDE.md
```

## Resource Protection

### Token Budget Monitoring
- Warn if single file read >10k tokens
- Suggest chunking if operation >50k tokens
- Track cumulative usage per session

### API Call Protection
- Maximum 3 concurrent calls (PRIMARY concurrency)
- Respect 15s timeout (PRIMARY_TIMEOUT)
- Maximum 2 retry attempts (PRIMARY_ATTEMPTS)
- Track failed models to avoid loops

### Cost Awareness
- Estimate cost before batch operations
- Warn if operation likely >$0.10
- Optimize prompts to reduce tokens
- Use smallest effective model

## Common Failure Patterns to Avoid

### 1. Infinite Retry Loop
**Symptom:** Same command failing repeatedly
**Fix:** After 2 failures, change approach or ask user

### 2. Context Confusion
**Symptom:** References to wrong project/files
**Fix:** Re-verify working directory and git branch

### 3. Terminology Drift
**Symptom:** Using "backup" instead of "FALLBACK", "models" instead of "ACTIVE"
**Fix:** Check trackers/names.md before introducing any term

### 4. Test Bypass
**Symptom:** Suggesting to commit without running tests
**Fix:** ALWAYS run `make test-summary` first

### 5. Silent Errors
**Symptom:** Command failed but continuing anyway
**Fix:** Show full stderr, stop on error, report to user

## Quick Command Reference

### Safe Exploration
```bash
# Check current state
pwd && git branch && git status

# List recent runs
ls -lt runs/ | head -10

# Check test status
make test-summary

# View changes
git diff
```

### Safe Testing
```bash
# Run specific PR phase tests
make test-pr01  # System Readiness
make test-pr06  # UltrAI Synthesis
# etc.

# Run single test file
. .venv/bin/activate && pytest tests/test_specific.py -v

# Run with narrative output
make test-narrative
```

### Safe Development
```bash
# Frontend dev server (safe)
cd frontend && npm run dev

# Build (safe, but show results)
cd frontend && npm run build

# Install (requires approval first)
make install  # Backend
cd frontend && npm install  # Frontend
```

## Session End Checklist

Before closing Cursor session:
- [ ] All temp files cleaned up
- [ ] Tests still passing (`make test-summary`)
- [ ] Important changes committed (if user requested)
- [ ] No uncommitted sensitive data (.env contents)
- [ ] Git status is clean or intentionally dirty
- [ ] User knows current state/next steps

## When to Ask vs. When to Act

### Just Ask (Don't Assume)
- Multiple valid approaches exist
- User intent is ambiguous
- Operation has side effects
- Could waste time/money if wrong
- Involves production systems

### Can Proceed (Low Risk)
- User explicitly requested action
- Operation is read-only
- Easy to undo (git revert)
- Documented in CLAUDE.md
- Standard workflow step

**Default: When in doubt → Ask**

## Contact Pattern for Uncertainty

Instead of guessing:
```
"I need clarification before proceeding:

Option A: [approach 1 with tradeoffs]
Option B: [approach 2 with tradeoffs]

Which approach should I take?"
```

Not this:
```
"I'll assume you want Option A and proceed..."
```

---

**Remember: User has explicitly stated that false explanations and wasted effort directly impact their financial stability. Accuracy and efficiency are not just preferences - they are critical requirements.**
