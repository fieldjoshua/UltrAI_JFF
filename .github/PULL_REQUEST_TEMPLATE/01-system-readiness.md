**Title**: PR 01 — System Readiness
**Scope**
Phase 0 — System Readiness. Verifies dependency software, code integrity, data availability, OpenRouter connection. Confirms all potentially used LLMs indicate up and ready. Enables user progress updates. Produces populated list of ready LLMs.
**Dependency Tracker** — update trackers/dependencies.md
**Name Tracker** — add READY, Run ID, 00_ready.json, readyList.
**Artifacts** runs/<RunID>/00_ready.json
**Testing Endpoints**
1) 00_ready.json exists
2) readyList ≥2 LLMs
3) Missing OPENROUTER_API_KEY triggers fail
