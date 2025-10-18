# Cursor AI Quick Start Guide
One-page reference for safe Cursor usage on UltrAI

## ⚡ Before You Start

**First Time Setup (5 minutes):**
1. Open Cursor → Settings (Cmd+,)
2. Features → YOLO Mode → **OFF** ❌
3. Features → Ask before running commands → **ON** ✅
4. Agent → Max iterations → **10**
5. Look for 📋 icon in bottom-right (rules loaded)

## 🎯 Quick Smoke Test

Paste this in Cursor to verify guardrails work:

```
Using terminology from trackers/names.md:
1. What's in the PREMIUM COCKTAIL?
2. Show git status (don't commit)
3. Write a real API test for R1 (no mocks)
```

**Should see:**
- ✅ Uses terms: COCKTAIL, R1, PRIMARY, FALLBACK
- ✅ Shows git status without auto-commit
- ✅ Test uses `@skip_if_no_api_key`, no mocks

**Red flags:**
- 🚨 Says "preset" instead of COCKTAIL
- 🚨 Auto-commits without asking
- 🚨 Uses `unittest.mock`

## 📋 Safe Operations (No Approval)

You can let Cursor do these freely:
- Read any file (`cat`, `grep`, `Read`)
- Run tests (`make test-*`, `pytest`)
- Check git status/diff/log
- Search codebase
- Start dev server (`npm run dev`)

## ⚠️ Requires Your Approval First

Always check before Cursor does:
- Git operations (commit, push, merge)
- Installing packages (npm install, pip install)
- Deleting files/directories
- Deploying to production
- Modifying config files
- Operations touching >5 files

## 🛑 Never Allow (Even If Asked)

Stop immediately if Cursor tries:
- `git push --force`
- Delete main/master branch
- Create mock tests (unittest.mock)
- Commit without running tests
- Modify .git/ directory
- Deploy without git push first

## 🗣️ Prompting Best Practices

**✅ Good Prompts:**
```
Add a validation function to ultrai/config.py that checks
OPENROUTER_API_KEY format. Use terminology from trackers/names.md.
Write a real API test (no mocks). Show me changes before committing.
```

Why: Specific, references docs, sets expectations

**❌ Bad Prompts:**
```
Make it better
Fix everything
Add tests
```

Why: Too vague, no boundaries, might create mocks

## 📊 Watch For These Patterns

**✅ Cursor is following rules:**
- References trackers/names.md for terminology
- Shows `git diff` before changes
- Asks permission for risky operations
- Uses COCKTAIL/READY/ACTIVE/R1/R2/R3 terms
- Creates real tests with `@skip_if_no_api_key`
- Stops after 2-3 failures and asks help

**🚨 Cursor is ignoring rules:**
- Auto-commits without approval
- Uses "preset"/"backup" instead of COCKTAIL/FALLBACK
- Creates unittest.mock tests
- Retries same failure >5 times
- Makes up file contents without reading
- Proceeds after multiple errors

## 🔧 Quick Troubleshooting

**Cursor auto-commits without asking:**
→ Disable YOLO mode in settings, restart Cursor

**Cursor uses wrong terminology:**
→ Add to prompt: "Use exact terms from trackers/names.md"

**Cursor creates mock tests:**
→ Say: "No mocks. Real API only with @skip_if_no_api_key decorator"

**Cursor enters infinite loop:**
→ Press Stop, restart composer, be more specific in prompt

**Rules not loading:**
→ Verify .cursorrules in project root, restart Cursor

## 📚 Full Documentation

Quick reference during dev: `.cursor/SAFETY_CHECKLIST.md`
Detailed test suite: `.cursor/LIVE_TEST_SESSION.md`
Setup instructions: `.cursor/CURSOR_CONFIGURATION.md`
Complete verification: `.cursor/VERIFICATION_REPORT.md`
Re-verify anytime: `./.cursor/verify_setup.sh`

## 🎓 Key Rules to Remember

1. **Zero Mock Tests** - User explicitly forbids fakes
2. **Git Before Deploy** - Always push before production
3. **Exact Terminology** - COCKTAIL not "preset", FALLBACK not "backup"
4. **Verify First** - Check files exist before describing
5. **Approve Risky Ops** - Git/install/delete need permission
6. **Stop at 3 Failures** - If same error 3x, ask user

## 🆘 If Things Go Wrong

1. **Stop immediately** (Ctrl+C or Stop button)
2. **Check what happened** (review Cursor's actions)
3. **Undo if needed** (`git reset --hard` if uncommitted)
4. **Report to Claude Code** (me) with details
5. **Don't continue** until issue understood

## 💬 Good First Prompts to Try

After verifying setup, try these safe starter prompts:

**1. Documentation Review:**
```
Read CLAUDE.md and summarize the R1/R2/R3 round structure
using the exact terminology defined in trackers/names.md.
```

**2. Code Exploration:**
```
Show me the COCKTAIL definitions in ultrai/active_llms.py
and explain the PRIMARY vs FALLBACK model structure.
```

**3. Test Review:**
```
Review tests/test_system_readiness.py and confirm it uses
real OpenRouter API calls (not mocks). Explain what it tests.
```

**4. Small Enhancement:**
```
Add a docstring to the get_active_llms() function in
ultrai/active_llms.py explaining how ACTIVE = READY ∩ COCKTAIL.
Show me the diff before making changes.
```

## ✅ Daily Workflow Checklist

Starting a Cursor session:
- [ ] YOLO mode is OFF (check settings)
- [ ] 📋 icon shows in bottom-right (rules loaded)
- [ ] Working dir: `/Users/joshuafield/projects/UltrAI_JFF/`
- [ ] Git status is clean (or known state)

During development:
- [ ] Cursor uses correct terminology
- [ ] Cursor asks before git operations
- [ ] Cursor shows diffs before changes
- [ ] No mock tests created

Before ending session:
- [ ] Tests passing (`make test-summary`)
- [ ] Important changes committed (if requested)
- [ ] No uncommitted secrets (.env)
- [ ] Git status clean or intentionally dirty

## 🎯 Success Criteria

You'll know guardrails are working when:
- ✅ Cursor catches you if you ask for something risky
- ✅ Cursor uses project terminology consistently
- ✅ Cursor never creates mock tests
- ✅ Cursor asks before git operations
- ✅ Cursor stops infinite loops on its own
- ✅ You trust Cursor's responses are accurate

---

**Start here:** Run Quick Smoke Test above
**Then try:** LIVE_TEST_SESSION.md for full verification
**Finally:** Use safely for UltrAI development!

Questions? Issues? → Ask Claude Code (me)
