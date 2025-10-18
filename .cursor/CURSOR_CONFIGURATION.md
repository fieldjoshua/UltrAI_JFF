# Cursor AI Configuration Guide for UltrAI

## Files Created

1. **`.cursorrules`** - Main guardrails file (Cursor auto-loads this)
2. **`.cursor/SAFETY_CHECKLIST.md`** - Quick reference for you
3. **`.cursor/CURSOR_CONFIGURATION.md`** - This file (setup guide)

## Cursor Settings to Configure

### Critical Settings (Configure Now)

Open Cursor Settings (Cmd+, on Mac) and set:

#### General Tab
- **YOLO Mode**: ❌ OFF (uncheck "Enable YOLO mode")
- **Auto-run commands**: ⚠️ Use with caution (recommend OFF for this project)
- **Show command confirmation**: ✅ ON (check "Ask before running commands")

#### Features Tab
- **Composer Agent Mode**: Configure limits:
  - Max iterations: `10` (prevents infinite loops)
  - Require approval for file operations: ✅ ON
  - Require approval for terminal commands: ✅ ON

#### Rules Tab
- **Project Rules**: Point to `.cursorrules` (should auto-detect)
- Verify `.cursorrules` is loaded (check for green indicator)

#### Privacy Tab
- **Privacy Mode**: Configure based on preference
  - If ON: No code sent to Cursor servers
  - If OFF: Code may be used for model improvements
- **Recommendation for UltrAI**: Privacy Mode ON (contains API patterns)

### Recommended Settings

#### Terminal Tab
- **Shell**: Use your default shell (zsh/bash)
- **Working directory**: `/Users/joshuafield/projects/UltrAI_JFF`
- **Environment variables**: Load from `.env`

#### Editor Tab
- **Auto-save**: ON (prevents lost work)
- **Format on save**: Configure for project (Prettier for frontend)
- **Tab size**: 4 spaces (Python), 2 spaces (JS/TS)

## Verification Steps

### 1. Verify .cursorrules is Loaded

In Cursor, check the bottom-right corner - you should see:
- 📋 Rules icon (indicates `.cursorrules` active)
- Green indicator (rules loaded successfully)

If not showing:
1. Restart Cursor
2. Check `.cursorrules` file exists in project root
3. Check for syntax errors in `.cursorrules`

### 2. Test Safety Limits

Try asking Cursor to:
```
"Delete all files in the runs/ directory"
```

Expected behavior:
- ✅ Cursor asks for confirmation first
- ✅ Shows which files will be deleted
- ✅ Waits for explicit approval

If Cursor executes without asking → YOLO mode is ON, disable it immediately.

### 3. Test Terminology Enforcement

Ask Cursor:
```
"What models are in the PREMIUM cocktail?"
```

Expected behavior:
- ✅ Uses term "COCKTAIL" (not "preset" or "group")
- ✅ References `ultrai/active_llms.py` or `trackers/names.md`
- ✅ Lists exact model names

If Cursor uses wrong terminology → `.cursorrules` not loaded properly.

### 4. Test Anti-Mock Policy

Ask Cursor:
```
"Write a test for the Initial Round"
```

Expected behavior:
- ✅ Uses `@pytest.mark.skipif(not OPENROUTER_API_KEY, ...)`
- ✅ Makes real API calls (no `mock.patch`)
- ✅ Verifies actual run artifacts

If Cursor suggests unittest.mock → Re-emphasize the anti-mock rule.

## Command Approval Configuration

### Allowlist Pattern

Create `.cursor/command_allowlist.json` (if feature available):
```json
{
  "allowed_without_approval": [
    "git status",
    "git diff",
    "git log",
    "git branch",
    "ls",
    "pwd",
    "cat",
    "grep",
    "make test-*",
    "pytest tests/",
    "npm run dev"
  ],
  "always_require_approval": [
    "git push*",
    "git commit*",
    "git merge*",
    "git reset*",
    "git rebase*",
    "rm *",
    "rmdir *",
    "npm install*",
    "pip install*",
    "make install",
    "curl *",
    "wget *"
  ]
}
```

**Note:** As of 2025, Cursor deprecated the denylist feature due to security vulnerabilities. Use approval prompts instead.

## Integration with Project Files

### .cursorrules References

The `.cursorrules` file references these project files:
- `CLAUDE.md` - Project overview and development commands
- `trackers/names.md` - Immutable terminology definitions
- `trackers/dependencies.md` - Dependency tracking
- `.github/PULL_REQUEST_TEMPLATE/` - PR phase templates
- `~/.claude/CLAUDE.md` - Your personal global instructions

**Important:** Keep these files in sync with `.cursorrules`.

### Terminology Source of Truth

```
trackers/names.md (highest authority)
    ↓
CLAUDE.md (project context)
    ↓
.cursorrules (enforcement rules)
    ↓
Cursor AI behavior
```

If terminology conflict occurs → `trackers/names.md` wins.

## Monitoring Cursor Behavior

### Signs Cursor is Following Rules

✅ **Good Indicators:**
- Asks before committing/pushing
- Shows diffs before modifying files
- References specific file:line numbers
- Uses exact terminology (READY, ACTIVE, ULTRA, R1/R2/R3)
- Runs tests before suggesting commits
- Admits uncertainty rather than guessing
- Stops after 2-3 failed attempts and asks for help

### Signs Cursor is Ignoring Rules

🚨 **Warning Indicators:**
- Auto-committing without showing changes
- Using wrong terminology ("backup" vs "FALLBACK")
- Creating mock tests
- Entering infinite retry loops
- Making assumptions about file contents
- Modifying files without showing diffs
- Proceeding after multiple failures

**Action if rules ignored:**
1. Stop the current operation
2. Re-emphasize the specific rule being violated
3. Ask Cursor to acknowledge the rule
4. If persists, restart Cursor to reload `.cursorrules`

## Emergency Procedures

### If Cursor Enters Infinite Loop

1. **Immediately:** Press `Ctrl+C` or click "Stop" in Cursor UI
2. **Check:** View the conversation history - what triggered the loop?
3. **Clear:** Close the composer/agent window
4. **Restart:** Open new composer with clear instructions
5. **Report:** Note the trigger pattern to avoid repeating

### If Cursor Hallucinates File Paths

Example: `terminal/terminal/terminal/...`

1. **Stop:** Interrupt the current operation
2. **Check:** Run `pwd` to verify working directory
3. **Clear context:** Close and reopen Cursor
4. **Restart:** Begin fresh with explicit directory context
5. **Verify:** Ask Cursor to confirm working directory before proceeding

### If Cursor Creates Mock Tests

1. **Stop:** Do not commit the mock tests
2. **Delete:** Remove the mock test code
3. **Re-emphasize:** Point to anti-mock rule in `.cursorrules`
4. **Request:** Ask for real API integration test instead
5. **Verify:** Check test uses `@skip_if_no_api_key` decorator

### If Cursor Wants to Deploy Without Tests

1. **Stop:** Do not approve deployment
2. **Run:** `make test-summary` manually
3. **Verify:** All tests pass
4. **Then:** Re-request deployment with test results shown

## Best Practices for Prompting Cursor

### ✅ Effective Prompts

```
"Add a new field to the synthesis output for tracking model agreement.
Update the ULTRA synthesis prompt, modify the UltrAI synthesis module,
and add a real integration test using OpenRouter API."
```

Why this works:
- Clear, specific request
- Multiple steps but bounded
- Implicitly expects real test (not mock)

### ❌ Problematic Prompts

```
"Make the system better and add tests"
```

Why this fails:
- Too vague (what aspect to improve?)
- No boundaries (could touch anything)
- Might create mock tests

### Provide Context Explicitly

```
"Using the terminology from trackers/names.md, add a FALLBACK
mechanism for when PRIMARY models timeout based on the
PRIMARY_TIMEOUT (15s) and PRIMARY_ATTEMPTS (2) defined in CLAUDE.md."
```

This grounds Cursor in project-specific terms and constraints.

## Periodic Maintenance

### Weekly
- [ ] Review Cursor conversation history for rule violations
- [ ] Check if `.cursorrules` needs updates based on new patterns
- [ ] Verify `trackers/names.md` still matches `.cursorrules` terminology

### After Major Updates
- [ ] Review Cursor changelog for new safety features
- [ ] Update `.cursorrules` if Cursor adds new capabilities
- [ ] Re-verify safety limits still work as expected

### Before Production Deploys
- [ ] Confirm all guardrails still active
- [ ] Run full test suite (`make ci`)
- [ ] Review all commits since last deploy
- [ ] Verify no mock tests merged

## Troubleshooting

### Cursor Not Respecting .cursorrules

**Possible causes:**
1. File not in project root → Move to `/Users/joshuafield/projects/UltrAI_JFF/.cursorrules`
2. Syntax error in file → Check for formatting issues
3. File not loaded → Restart Cursor
4. Rules too long (>8k tokens) → Cursor may truncate, prioritize critical rules

**Solutions:**
- Verify file location
- Check Cursor logs for errors
- Restart Cursor IDE
- Split into `.cursorrules` (main) + `.cursor/project_rules.md` (extended)

### YOLO Mode Keeps Re-enabling

Some Cursor versions reset YOLO mode between sessions.

**Workaround:**
- Check YOLO mode status at start of each session
- Add reminder in session start prompt:
  ```
  "Is YOLO mode OFF? Confirm before proceeding."
  ```

### Command Approval Not Working

If Cursor runs commands without approval:

1. Check Settings → Features → "Ask before running commands" is ON
2. Update Cursor to latest version (older versions had approval bugs)
3. As fallback: Monitor commands manually, interrupt if unapproved

## Integration with Claude Code (This AI)

When working on this project:
- **You use:** Claude Code via terminal (explicit tool calls)
- **Cursor uses:** Cursor AI via IDE (auto mode with guardrails)

**Division of Labor:**
- **Claude Code (me):** Strategic planning, complex debugging, research, PR reviews
- **Cursor AI:** Tactical implementation, code writing, running tests, file edits

**Handoff Pattern:**
```
1. User discusses strategy with Claude Code (me)
2. Claude Code provides architectural guidance
3. User implements in Cursor with safety guardrails
4. User returns to Claude Code for validation/review
```

This ensures strategic oversight while maintaining safety during implementation.

---

## Summary: Critical Actions

1. ✅ Verify `.cursorrules` file exists in project root
2. ✅ Open Cursor Settings → Disable YOLO mode
3. ✅ Enable command approval prompts
4. ✅ Set max agent iterations to 10
5. ✅ Test that Cursor asks before git operations
6. ✅ Verify Cursor uses correct terminology (COCKTAIL, READY, ACTIVE, etc.)
7. ✅ Confirm Cursor won't create mock tests

**Status Check:**
- Rules loaded: [  ] (check bottom-right in Cursor)
- YOLO mode OFF: [  ] (check settings)
- Approval prompts ON: [  ] (check settings)
- Test with sample command: [  ] (try "git commit -m test")

Once all checked, your Cursor AI has proper guardrails for UltrAI development.
