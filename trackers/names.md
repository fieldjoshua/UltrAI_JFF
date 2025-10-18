Immutable names used in UltrAI (files, stage names, identifiers).

## Test Timeout Classification System

### Timeout Categories
- **TO_5**: Unit tests (0-5 seconds) - Configuration, validation, file operations
- **TO_15**: Fast integration (5-15 seconds) - Basic API calls, simple operations  
- **TO_30**: Medium integration (15-30 seconds) - Real API calls, single LLM tests
- **TO_60**: Full integration (30-60 seconds) - Complete pipelines, multi-model tests
- **TO_120**: Complex integration (60-120 seconds) - Stress tests, benchmarking

### Timeout Classification Terms
- **TimeoutResult**: Data structure containing test name, duration, reason, file, timestamp
- **TO_15 Class**: Collection of tests that exceeded timeout threshold for re-examination
- **Timeout Threshold**: Maximum allowed execution time before categorization (not failure)
- **Timeout Categorization**: Process of classifying slow tests instead of failing them

## PR 01 — System Readiness

### Terms
- **READY**: The complete set of LLMs available and healthy from OpenRouter at system check time
- **Run ID**: Unique identifier for each UltrAI execution (format: timestamp-based UUID or ISO datetime)

### File Names
- **00_ready.json**: System readiness output artifact containing readyList and metadata

### Data Structure Fields
- **readyList**: Array of LLM identifiers that passed health checks (minimum 2 required for execution)

## PR 02 — User Input & Selection

### Terms
- **QUERY**: User's question or prompt to be analyzed by the LLM orchestration
- **ANALYSIS**: Type of analysis to perform (currently: "Synthesis" = R1 + R2 + R3 rounds)
- **COCKTAIL**: Pre-selected group of LLMs chosen by user (one of 4 public choices)

### File Names

### Public Cocktail Names (4 Choices)
- **PREMIUM**: High-quality models focused on accuracy and capability
- **SPEEDY**: Fast models optimized for quick responses
- **BUDGET**: Cost-effective models balancing quality and expense
- **DEPTH**: Deep reasoning models for complex analytical tasks

### INACTIVE Structural Attachment Points (Architecture-Required Only)
- **INACTIVE_ADDON1**: Structural attachment point #1 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON2**: Structural attachment point #2 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON3**: Structural attachment point #3 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON4**: Structural attachment point #4 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON5**: Structural attachment point #5 (preserves addon architecture for FUTURE deployment)

Note: INACTIVE placeholders exist ONLY to preserve architectural attachment points where no active elements exist. Cocktails have 4 active choices, so no INACTIVE cocktail placeholders are needed.

## PR 03 — Active LLMs Preparation

### Terms
- **PRIMARY**: Core 3 models per cocktail that are tried first (33x faster than previous 10-model config)
- **FALLBACK**: 3 backup models per cocktail, activated if PRIMARY fails or times out
- **PRIMARY_TIMEOUT**: Seconds allowed per attempt for PRIMARY model to respond (15 seconds per attempt)
- **PRIMARY_ATTEMPTS**: Number of retry attempts for PRIMARY model before activating FALLBACK (2 attempts = 30s total)
- **CONCURRENCY**: Maximum number of simultaneous async tasks (semaphore-based rate limiting, set to 3 for PRIMARY models)
- **UVICORN_WORKER**: OS-level process handling individual user requests (3 workers = 3 concurrent users)
- **ACTIVE**: The subset of READY models that match the selected COCKTAIL (ACTIVE = READY ∩ COCKTAIL)
- **ACTIVATE**: The phase/action of determining which LLMs will participate in R1/R2 rounds
- **quorum**: Minimum required ACTIVE models to proceed with synthesis (always 2)

### File Names
- **02_activate.json**: Active LLMs preparation output artifact containing activeList, backupList (now fallbackList), quorum, and reasons

### Data Structure Fields
- **activeList**: Array of ACTIVE LLM identifiers (PRIMARY models from READY ∩ COCKTAIL)
- **backupList** (legacy) / **fallbackList**: Array of FALLBACK LLM identifiers (sequential activation after PRIMARY timeout)
- **reasons**: Dictionary explaining status of each PRIMARY model (ACTIVE or NOT READY)
- **PRIMARY_MODELS**: Dictionary mapping each cocktail to its 3 PRIMARY models
- **FALLBACK_MODELS**: Dictionary mapping each cocktail to its 3 FALLBACK models (1:1 correspondence with PRIMARY)

## PR 04 — Initial Round (R1)

### Terms
- **R1**: The first round of the synthesis sequence where ACTIVE models independently respond
- **INITIAL**: The term used to identify R1 outputs (not "initial_round" or "round1", specifically "INITIAL")

### File Names
- **03_initial.json**: Array of response objects from R1 execution
- **03_initial_status.json**: Metadata and status information for R1 execution

### Data Structure Fields
- **round**: Field identifying which round produced the response (value: "INITIAL" for R1)
- **model**: Model identifier that produced the response
- **text**: The actual text content of the model's response
- **ms**: Elapsed time in milliseconds for the model to respond
- **concurrency_limit**: Concurrency limit used for R1 execution (recorded in status file)

## PR 05 — Meta Round (R2)

### Terms
- **R2**: The second round of the synthesis sequence where ACTIVE models revise after peer review
- **META**: The term used to identify R2 outputs (not "meta_round" or "round2", specifically "META")
- **Peer Context**: Concatenated INITIAL drafts from all ACTIVE models for review
- **Revision**: Process of updating response after reviewing peer INITIAL outputs

### File Names
- **04_meta.json**: Array of META response objects from R2 execution
- **04_meta_status.json**: Metadata and status information for R2 execution

### Data Structure Fields
- **round**: Field identifying which round produced the response (value: "META" for R2)
- **model**: Model identifier that produced the META response
- **text**: The revised response text after peer review
- **ms**: Elapsed time in milliseconds for the model to respond
- **error**: Boolean flag indicating if the query failed
- **concurrency_limit**: Concurrency limit used for R2 execution (recorded in status file)

## PR 06 — UltrAI Synthesis (R3)

### Terms
- **R3**: The third and final round where a neutral ULTRA model synthesizes META drafts
- **ULTRAI**: Term to identify R3 synthesis output (not "ultrai_round", "round3", specifically "ULTRAI")
- **ULTRA**: Neutral synthesizer model selected from ACTIVE list by preference order
- **Synthesis**: Final integrated output merging convergent META points and resolving contradictions
- **Neutral Model**: Model chosen to perform synthesis without bias (not a participant in R1/R2)

### File Names
- **05_ultrai.json**: Final synthesis output artifact containing synthesis object
- **05_ultrai_status.json**: Metadata and status information for R3 execution

### Data Structure Fields (05_ultrai.json)
- **round**: Always "ULTRAI" (distinguishes from INITIAL/META)
- **model**: Model identifier that produced the synthesis
- **neutralChosen**: Confirms which neutral model was selected (matches model field)
- **text**: Final synthesis text merging META drafts
- **ms**: Response time in milliseconds for synthesis
- **stats**: Object containing active_count (number of ACTIVE models) and meta_count (number of META drafts)

### Neutral Model Selection (PREFERRED_ULTRA)
- **Preference Order**: claude-3.7-sonnet → gpt-4o → gemini-2.0-thinking → llama-3.3-70b
- **Selection Logic**: First preferred model found in ACTIVE list
- **Fallback**: If no preferred model in ACTIVE, use first ACTIVE model

### Data Structure Fields (05_ultrai_status.json)
- **timeout**: Dynamic timeout calculated for synthesis (60-300 seconds)
- **context_length**: Length of META context being synthesized
- **num_meta_drafts**: Number of META drafts integrated into synthesis
- **max_chars_per_draft**: Maximum characters per META draft (500-2000, varies with complexity)


### Terms

### File Names
- **06_visualization.txt**: Visualization export file (if visualization add-on selected)
- **06_citations.json**: Citations export file (if citation_tracking add-on selected)

### Data Structure Fields (06_final.json)
- **round**: Always "FINAL"
- **text**: Final synthesis text (from 05_ultrai.json)
- **metadata**: run_id, timestamp, phase

### Add-on Record Fields
- **name**: Add-on identifier (e.g., "visualization", "citation_tracking")
- **ok**: Boolean indicating success (true) or failure (false)
- **path**: Export file path (present if add-on generates export file)
- **error**: Error message (present if ok=false)

## PR 08 — Statistics

### Terms
- **stats.json**: Performance statistics artifact aggregating timing and count data
- **avg_ms**: Average response time in milliseconds (used for R1 and R2)
- **count**: Number of responses per round

### File Names
- **stats.json**: Statistics artifact containing INITIAL, META, ULTRAI stats

### Data Structure Fields (stats.json)
- **INITIAL**: Object with count (number of R1 responses) and avg_ms (average time)
- **META**: Object with count (number of R2 responses) and avg_ms (average time)
- **ULTRAI**: Object with count (always 1) and ms (synthesis time)

## PR 09 — Final Delivery

### Terms
- **delivery.json**: Delivery manifest listing all artifacts and their status
- **Required Artifacts**: 5 mandatory files (05_ultrai, 03_initial, 04_meta, 06_final, stats)
- **Delivery Status**: COMPLETED (all required present) or INCOMPLETE (missing artifacts)

### File Names
- **delivery.json**: Delivery manifest artifact verifying all deliverables

### Data Structure Fields (delivery.json)
- **status**: "COMPLETED" or "INCOMPLETE"
- **message**: Status message describing delivery state
- **artifacts**: Array of required artifact records
- **optional_artifacts**: Array of optional export files found
- **missing_required**: List of missing required artifact names
- **metadata**: run_id, timestamp, phase, total_artifacts

### Artifact Record Fields
- **name**: Artifact filename (e.g., "05_ultrai.json")
- **path**: Full path to artifact file
- **status**: "ready" (valid), "missing" (not found), or "error" (invalid JSON)
- **size_bytes**: File size in bytes (present if status=ready)
- **error**: Error message (present if status=error)

## PR 11 — Public API (FastAPI) + Render Blueprint

### Terms
- **API**: HTTP interface exposing UltrAI orchestration
- **RUN_START**: Action to start PR01→PR06 pipeline for a run
- **RUN_STATUS**: JSON status describing current phase and artifacts
- **RUN_ARTIFACTS**: Listing of artifact files for a run
- **RENDER_WEB_SERVICE**: Render service for API/UI

### File Names
- **render.yaml**: Render Blueprint defining Web Service
- **ultrai/api.py**: FastAPI app exposing endpoints

### Data Structure Fields (RUN_STATUS response)
- **run_id**: Unique run identifier
- **phase**: Current phase (00_ready.json … 06_final.json)
- **round**: R1/R2/R3 or null
- **completed**: Boolean indicating if pipeline is finished
- **artifacts**: Array of artifact filenames present
- **error**: Null or error message

## PR 20 — Frontend Foundation

### Terms
- **FRONTEND**: React-based web interface for UltrAI user interaction
- **UI_SCAFFOLD**: Foundation structure with React + Vite + Tailwind (no functionality)
- **VITE_CONFIG**: Build configuration for development and production bundles
- **TAILWIND_CONFIG**: Utility-first CSS framework configuration
- **DEV_SERVER**: Local development server for frontend (port 5173)

### File Names
- **frontend/package.json**: NPM dependencies and scripts
- **frontend/vite.config.js**: Vite build configuration
- **frontend/tailwind.config.js**: Tailwind CSS configuration
- **frontend/src/App.jsx**: Root React component
- **frontend/src/main.jsx**: React entry point
- **frontend/src/index.html**: HTML template
- **frontend/src/index.css**: Global styles with Tailwind directives
- **frontend/README.md**: Frontend setup instructions

### Data Structure Fields
No data structures in this phase (scaffold only)
