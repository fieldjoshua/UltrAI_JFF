**Title**: PR 05 — Meta Round
**Scope**
Phase 4 — Original active LLMs still active and available. Receive proper input (review each other’s work). Act properly on meta round instructions. Produce meta outputs. Stored properly and recallable quickly. Proper data and timing conveyed.
**Dependency Tracker** — inputs from initial outputs.
**Name Tracker** — add META, 04_meta.json, 04_meta_status.json.
**Artifacts** runs/<RunID>/04_meta.json
**Artifacts** runs/<RunID>/04_meta_status.json
**Testing Endpoints**
1) 04_meta.json exists
2) items round=META and align with initial LLMs
3) 04_meta_status.json.details.count matches item count
