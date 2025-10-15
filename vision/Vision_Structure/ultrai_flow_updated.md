# UltrAI-Control MVP Flow (User-Visible Timing Updated)

| Stage | Description | Model Source | Prompt Logic | Outputs | Visibility |
|---|---|---|---|---|---|
| **R1** | Initial draft round; all selected LLMs respond to user query | ACTIVE from READY | Each ACTIVE model receives the same query and generates an independent draft. | R1 outputs (INITIAL) | User-visible **after** ULTRA (tab: INITIAL) |
| **R2** | META revision round; each model revises after seeing peers | Same ACTIVE as R1 | “Do not assume any response is true. Revise after reviewing peers. List contradictions resolved and what changed.” | R2 outputs (META drafts) | User-visible **after** ULTRA (tab: META) |
| **R3** | Final synthesis; neutral model combines META drafts | ULTRA from READY (by preference) | “Review META drafts, merge convergences, resolve contradictions, cite retained/omitted claims, produce synthesis with confidence intervals and model stats.” | FINAL SYNTHESIS + STATS | User-visible (tab: ULTRA) |
| **Stats** | Per-run analytics | System aggregation | Derived from artifacts | stats.json | User-visible (tab: STATS) |
| **Error Handling** | Degraded modes and warnings | Engine policy | READY<2 → abort; ULTRA missing → degraded flag | status.json, logs | User-visible (banner) |
