**Title**: PR 06 — UltrAI Synthesis
**Scope**
Phase 5 — Neutral LLM employed. Receives input through other threads. Acts on it. Creates output. Requisite data included.
**Dependency Tracker** — record neutral choice rule.
**Name Tracker** — add ULTRAI, 05_ultrai.json, 05_ultrai_status.json, neutralChosen.
**Artifacts** runs/<RunID>/05_ultrai.json
**Artifacts** runs/<RunID>/05_ultrai_status.json
**Testing Endpoints**
1) 05_ultrai.json exists; round=ULTRAI; model and neutralChosen present; text non-empty
2) 05_ultrai_status.json confirms neutral and model used
