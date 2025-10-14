**Title**: PR 04 — Initial Round
**Scope**
Phase 3 — Every active LLM is ready for input, receives input, acts on input, and produces output. Output stored properly and recallable quickly. Proper data and timing conveyed.
**Dependency Tracker** — initial outputs deps.
**Name Tracker** — add INITIAL, 03_initial.json, 03_initial_status.json.
**Artifacts** runs/<RunID>/03_initial.json
**Artifacts** runs/<RunID>/03_initial_status.json
**Testing Endpoints**
1) 03_initial.json exists
2) items have round=INITIAL, model, text, ms
3) 03_initial_status.json.details.count matches item count
