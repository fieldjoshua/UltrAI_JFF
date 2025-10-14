**Title**: PR 10 — Error Handling & Fallbacks
**Scope**
Hard-coded set of LLMs as the universe. Roll back to that list if certain LLMs falter. Error handling organic, not anticipatory, written down and written in with real LLMs. Circuit breakers only if they redirect to a specific thing. Not open-ended.
**Dependency Tracker** — fallback LLMs and specific chain.
**Name Tracker** — error codes used and meanings.
**Artifacts** stage JSONs record failures with status FAIL and error code.
**Testing Endpoints**
1) Forced failure redirects only to the specific fallback
2) If all fail, a stage-specific error code is emitted and recorded
