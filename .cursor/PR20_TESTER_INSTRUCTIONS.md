# PR 20: Instructions for Native Cursor Editor (Tester)

## Your Role
You are the **Testing & Quality Assurance Lead** for PR 20 (Frontend Foundation). The general-purpose agent has built the scaffold. Your job is to **verify it works** before the user approves the merge.

---

## What You're Testing

A minimal React application that:
- Installs dependencies without errors
- Runs a dev server on http://localhost:5173
- Shows placeholder UI with Tailwind styling
- Builds production bundle successfully
- Has no console errors

**This is the foundation for all future frontend work.** If it doesn't work, nothing else will.

---

## Testing Checklist (Run in Order)

### ✅ Test 1: Dependencies Install

**Command:**
```bash
cd /Users/joshuafield/projects/UltrAI_JFF/frontend
npm install
```

**Expected:**
- Installation completes without errors
- `node_modules/` directory created
- No `npm ERR!` messages
- Approximately 300-400 packages installed

**If FAIL:**
- Report to agent: "npm install failed with error: [error message]"
- Agent will fix package.json

---

### ✅ Test 2: Dev Server Starts

**Command:**
```bash
npm run dev
```

**Expected:**
- Vite dev server starts
- Console shows: `VITE v6.x.x ready in XXX ms`
- Console shows: `➜  Local:   http://localhost:5173/`
- No errors in terminal

**If FAIL:**
- Report to agent: "Dev server failed to start: [error message]"
- Agent will fix vite.config.js or dependencies

---

### ✅ Test 3: UI Renders in Browser

**Action:**
1. Open browser: http://localhost:5173
2. Look at the page

**Expected:**
- Page loads (no white screen of death)
- Purple/blue gradient background visible
- Text "UltrAI Frontend" appears (large, centered)
- Text "Multi-LLM synthesis system foundation" appears
- Text "React + Vite + Tailwind CSS scaffold" appears

**If FAIL:**
- Report to agent: "UI doesn't render: [description]"
- Agent will fix App.jsx or index.html

---

### ✅ Test 4: Tailwind CSS Works

**Action:**
1. With dev server still running, open browser DevTools (F12)
2. Inspect the `<h1>` element with "UltrAI Frontend" text
3. Check computed styles

**Expected:**
- Background has gradient (purple → blue → black)
- Title text is large (text-5xl = ~48px)
- Text is white
- Tailwind classes apply correctly

**Quick Visual Check:**
- Gradient background? ✅
- Large centered title? ✅
- White text on dark background? ✅

**If FAIL:**
- Report to agent: "Tailwind not working: [description]"
- Agent will fix tailwind.config.js or index.css

---

### ✅ Test 5: No Console Errors

**Action:**
1. With browser still open to http://localhost:5173
2. Open DevTools Console (F12 → Console tab)
3. Look for red error messages

**Expected:**
- No errors in console
- Only Vite/React info messages (blue/gray, not red)

**If FAIL:**
- Report to agent: "Console errors: [copy exact error text]"
- Agent will fix JavaScript issues

---

### ✅ Test 6: Production Build Succeeds

**Command:**
```bash
# Stop dev server first (Ctrl+C if still running)
npm run build
```

**Expected:**
- Build completes successfully
- Terminal shows: `✓ built in XXXms`
- `dist/` directory created in frontend/
- `dist/` contains:
  - `index.html`
  - `assets/` folder with .js and .css files
- No build errors

**If FAIL:**
- Report to agent: "Build failed: [error message]"
- Agent will fix vite.config.js or code issues

---

### ✅ Test 7: Production Build Preview

**Command:**
```bash
npm run preview
```

**Expected:**
- Preview server starts
- Console shows: `➜  Local:   http://localhost:4173/`
- Open http://localhost:4173 in browser
- Same UI appears as dev server (gradient, title, text)
- No console errors

**If FAIL:**
- Report to agent: "Preview failed: [error message]"
- Agent will investigate build output

---

### ✅ Test 8: README Exists

**Command:**
```bash
cat /Users/joshuafield/projects/UltrAI_JFF/frontend/README.md
```

**Expected:**
- File exists
- Contains setup instructions
- Lists npm install, npm run dev, npm run build commands

**If FAIL:**
- Report to agent: "README missing or incomplete"
- Agent will create/update README.md

---

## Final Report

After all 8 tests, create a summary:

### If All Tests PASS ✅

```
✅ PR 20 Testing Complete - ALL TESTS PASS

Test 1: npm install ✅
Test 2: dev server ✅
Test 3: UI renders ✅
Test 4: Tailwind works ✅
Test 5: no console errors ✅
Test 6: production build ✅
Test 7: preview works ✅
Test 8: README exists ✅

Frontend foundation is ready for user approval.
Recommend merging PR 20.
```

**Hand off to USER for final approval and merge.**

---

### If Any Tests FAIL ❌

```
❌ PR 20 Testing - FAILURES DETECTED

Test 1: npm install [PASS/FAIL]
Test 2: dev server [PASS/FAIL]
Test 3: UI renders [PASS/FAIL]
Test 4: Tailwind works [PASS/FAIL]
Test 5: no console errors [PASS/FAIL]
Test 6: production build [PASS/FAIL]
Test 7: preview works [PASS/FAIL]
Test 8: README exists [PASS/FAIL]

Failures:
- [Test name]: [Error description]
- [Test name]: [Error description]

Sending back to general-purpose agent for fixes.
```

**Hand off to AGENT with failure details for debugging.**

---

## Troubleshooting Guide

### Common Issues

**Issue: "npm install" hangs**
- Try: `rm -rf node_modules package-lock.json && npm install`
- Report to agent if persists

**Issue: Dev server shows blank page**
- Check browser console for errors
- Check terminal for Vite errors
- Report exact error message to agent

**Issue: Tailwind classes don't apply**
- Verify `@tailwind` directives in src/index.css
- Check tailwind.config.js content array
- Report to agent with screenshot

**Issue: Build fails with "module not found"**
- Check import paths in App.jsx, main.jsx
- Verify all files exist in src/
- Report missing module name to agent

---

## Important Notes

### ✅ DO:
- Run tests in order (dependencies → dev → build)
- Copy exact error messages when reporting failures
- Check browser console for JavaScript errors
- Take screenshots if UI looks wrong

### ❌ DON'T:
- Modify any code (your job is to TEST, not FIX)
- Skip tests (all 8 must pass)
- Approve if errors exist (send back to agent)
- Install extra packages

---

## Communication Template

**When reporting to agent:**
```
Test [number] failed: [test name]

Error message:
[paste exact error from terminal or console]

Context:
[what you were doing when it failed]

Browser (if relevant): Chrome/Firefox
OS: macOS
Node version: [from node --version]
```

**When reporting to user:**
```
PR 20 Testing Summary:
- [X/8] tests passed
- [List any failures with brief description]
- Recommendation: [Merge / Send back to agent]
```

---

## Success Criteria

All 8 tests must PASS for PR 20 to be approved:
1. ✅ Dependencies install
2. ✅ Dev server runs
3. ✅ UI renders correctly
4. ✅ Tailwind styling works
5. ✅ No console errors
6. ✅ Production build succeeds
7. ✅ Preview server works
8. ✅ README exists

**No partial credit.** If even one test fails, send back to agent.

---

## Timeline

Expected testing time: **15-30 minutes**
- 5 min: npm install
- 5 min: dev server + browser checks
- 5 min: build + preview
- 5-10 min: documentation + reporting

If testing takes >1 hour, something is wrong. Report to user.

---

Ready to start? Run Test 1: `cd frontend && npm install`
