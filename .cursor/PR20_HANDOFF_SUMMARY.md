# PR 20 Frontend Foundation — Handoff Summary

## What Was Created

Three instruction documents for PR 20 (Frontend Foundation):

### 1. PR Template
**File**: `.github/PULL_REQUEST_TEMPLATE/20-frontend-foundation.md`
- Defines scope, artifacts, testing endpoints
- Lists dependencies and terminology
- Acceptance criteria for PR 20

### 2. Agent Instructions (Builder)
**File**: `.cursor/PR20_AGENT_INSTRUCTIONS.md`
- Step-by-step scaffold instructions
- All file contents to create
- Handoff message template

### 3. Tester Instructions (Quality Assurance)
**File**: `.cursor/PR20_TESTER_INSTRUCTIONS.md`
- 8 testing checkpoints
- Expected vs. actual results
- Pass/fail reporting templates

---

## Division of Labor (Finalized)

### Claude Code (Me) ✅ COMPLETE
- [x] Created PR template
- [x] Updated trackers/names.md with frontend terminology
- [x] Updated trackers/dependencies.md with npm packages
- [x] Created agent instructions document
- [x] Created tester instructions document
- [x] This handoff summary

**Status**: Ready to hand off to general-purpose agent

---

### General-Purpose Agent (Next Step)
**Read**: `.cursor/PR20_AGENT_INSTRUCTIONS.md`

**Task**: Create 10 files in `frontend/` directory:
1. package.json (React + Vite + Tailwind)
2. vite.config.js (dev server config)
3. tailwind.config.js (Tailwind config)
4. postcss.config.js (PostCSS for Tailwind)
5. index.html (HTML entry point)
6. src/main.jsx (React entry point)
7. src/App.jsx (placeholder UI with gradient)
8. src/index.css (Tailwind directives)
9. README.md (setup instructions)
10. .gitignore (if needed)

**When done**: Message native editor with handoff template

---

### Native Cursor Editor (After Agent)
**Read**: `.cursor/PR20_TESTER_INSTRUCTIONS.md`

**Task**: Run 8 tests in order:
1. npm install → dependencies resolve?
2. npm run dev → server starts?
3. Browser check → UI renders?
4. DevTools → Tailwind works?
5. Console → no errors?
6. npm run build → dist/ created?
7. npm run preview → production works?
8. README check → instructions exist?

**Report**: All pass ✅ → user approval | Any fail ❌ → back to agent

---

### You (Human) — Final Step
**After native editor confirms all tests pass**:

**Review**:
1. Visit http://localhost:5173 (dev server)
2. See gradient background + "UltrAI Frontend" title
3. Approve visual appearance

**Approve**: If satisfied, merge PR 20 into main

---

## Workflow Diagram

```
┌─────────────┐
│ Claude Code │ Creates instructions ✅ DONE
│ (Me)        │ Updates trackers ✅ DONE
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ General     │ Reads: PR20_AGENT_INSTRUCTIONS.md
│ Purpose     │ Creates: 10 files in frontend/
│ Agent       │ Hands off to tester
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Native      │ Reads: PR20_TESTER_INSTRUCTIONS.md
│ Cursor      │ Runs: 8 test checkpoints
│ Editor      │ Reports: PASS ✅ or FAIL ❌
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ You         │ Reviews: http://localhost:5173
│ (Human)     │ Approves: Merge PR 20
└─────────────┘
```

---

## What Gets Tested (Native Editor)

No mock tests. All REAL tests:

✅ **Real npm install** — Actual package installation
✅ **Real dev server** — Vite running on localhost:5173
✅ **Real browser** — Chrome/Firefox rendering actual UI
✅ **Real build** — Production dist/ output
✅ **Real Tailwind** — CSS utility classes applying
✅ **Real preview** — Production build served on localhost:4173

**Zero mocks**. Everything must actually work.

---

## File Locations

**Instructions for Agent**:
```bash
/Users/joshuafield/projects/UltrAI_JFF/.cursor/PR20_AGENT_INSTRUCTIONS.md
```

**Instructions for Tester**:
```bash
/Users/joshuafield/projects/UltrAI_JFF/.cursor/PR20_TESTER_INSTRUCTIONS.md
```

**PR Template**:
```bash
/Users/joshuafield/projects/UltrAI_JFF/.github/PULL_REQUEST_TEMPLATE/20-frontend-foundation.md
```

**Updated Trackers**:
```bash
/Users/joshuafield/projects/UltrAI_JFF/trackers/names.md (lines 220-240)
/Users/joshuafield/projects/UltrAI_JFF/trackers/dependencies.md (new PR 20 section)
```

---

## Next Steps for You

### Option 1: Use Native Cursor Editor Directly

Open `.cursor/PR20_AGENT_INSTRUCTIONS.md` in Cursor and ask:

```
Follow the instructions in this file to create the frontend scaffold.
Use exact file contents shown. When done, hand off to tester.
```

Then open `.cursor/PR20_TESTER_INSTRUCTIONS.md` and ask:

```
Run the 8 tests in this file and report results.
```

### Option 2: Use General-Purpose Agent

If using Task tool with general-purpose agent:

```
Read .cursor/PR20_AGENT_INSTRUCTIONS.md and implement PR 20
(Frontend Foundation). Create all files exactly as specified.
When complete, notify that testing can begin.
```

---

## Estimated Timeline

- **Agent (build)**: 30-45 minutes
- **Native editor (test)**: 15-30 minutes
- **You (approve)**: 5 minutes

**Total PR 20**: ~1-1.5 hours

---

## Success Criteria

PR 20 is complete when:
- ✅ All 10 files created
- ✅ All 8 tests pass
- ✅ You approve visual appearance
- ✅ Trackers updated (names.md, dependencies.md)
- ✅ Merged to main branch

---

## Questions?

**Agent stuck?** Check PR20_AGENT_INSTRUCTIONS.md step-by-step checklist

**Tests failing?** Native editor reports exact errors to agent for fixes

**Visual issues?** You provide feedback, agent adjusts styling

**Ready to start?** Hand off to your preferred workflow (native editor or agent)

---

**Status**: ✅ Ready for handoff to general-purpose agent or native Cursor editor
