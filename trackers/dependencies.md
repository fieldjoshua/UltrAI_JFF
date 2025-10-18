Software deps and their purpose.

## Core Dependencies

### httpx
- **Purpose**: Async HTTP client for OpenRouter API calls
- **Usage**: Connect to OpenRouter service, query available models with async/await patterns
- **Phase**: System Readiness (PR 01), Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Why httpx**: CORRECTED doc v2.0 requires truly async HTTP libraries (not synchronous requests)
- **Features**: Semaphore-based rate limiting, exponential backoff, proper error handling

### python-dotenv
- **Purpose**: Environment variable management
- **Usage**: Load OPENROUTER_API_KEY from .env file
- **Phase**: System Readiness (PR 01)
- **Security**: Ensures API keys never hardcoded in source

### pytest
- **Purpose**: Testing framework
- **Usage**: Run test suite for all phases, verify artifacts and endpoints
- **Phase**: All phases (testing endpoints)
- **Critical**: NO MOCKS ALLOWED - all tests use real API calls

### pytest-asyncio
- **Purpose**: Async test support for pytest
- **Usage**: Enable async test functions with @pytest.mark.asyncio decorator
- **Phase**: System Readiness (PR 01) and all async implementations
- **Why**: Required for testing async/await code paths

### pytest-html
- **Purpose**: HTML test report generation
- **Usage**: Generate visual test reports with `make test-report`
- **Phase**: All phases (test infrastructure)
- **Features**: Self-contained HTML reports with pass/fail visualization

### pytest-watch
- **Purpose**: Continuous test execution on file changes
- **Usage**: Watch mode testing with `make test-watch`
- **Phase**: Development workflow
- **Features**: Auto-rerun tests when source files change

### pytest-timeout
- **Purpose**: Individual test timeout management
- **Usage**: Prevent infinite loops and catch slow tests
- **Phase**: All phases (test infrastructure)
- **Features**: Per-test timeout enforcement, timeout categorization
- **Configuration**: Multi-tier timeout system (TO_5, TO_15, TO_30, TO_60, TO_120)

## Multi-Tier Timeout System

### Timeout Categories (tests/to_15_class.py)
- **Purpose**: Categorize tests by execution time instead of failing on timeout
- **Usage**: Classify slow tests for optimization rather than blocking CI
- **Phase**: All phases (test infrastructure)
- **Classes**:
  - **TO_5**: Unit tests (0-5 seconds) - Configuration, validation, file operations
  - **TO_15**: Fast integration (5-15 seconds) - Basic API calls, simple operations
  - **TO_30**: Medium integration (15-30 seconds) - Real API calls, single LLM tests
  - **TO_60**: Full integration (30-60 seconds) - Complete pipelines, multi-model tests
  - **TO_120**: Complex integration (60-120 seconds) - Stress tests, benchmarking

### Timeout Classification Logic
- **TO_5 Tests**: Configuration validation, input processing, file structure checks
- **TO_15 Tests**: Single API endpoint tests, basic file operations, CLI functionality
- **TO_30 Tests**: Real OpenRouter API calls, individual LLM response tests, statistics collection
- **TO_60 Tests**: End-to-end pipeline tests, multi-model synthesis, complete delivery
- **TO_120 Tests**: Full cocktail testing, stress testing, performance benchmarking

### CI Pipeline Integration
- **Unit Tests**: `pytest --timeout=5 -m "unit"` (TO_5 class)
- **Fast Integration**: `pytest --timeout=15 -m "fast_integration"` (TO_15 class)
- **Medium Integration**: `pytest --timeout=30 -m "medium_integration"` (TO_30 class)
- **Full Integration**: `pytest --timeout=60 -m "full_integration"` (TO_60 class)
- **Complex Integration**: `pytest --timeout=120 -m "complex_integration"` (TO_120 class)

### Benefits
- **Prevents False Failures**: Network latency doesn't fail CI
- **Categorizes for Optimization**: Slow tests identified for improvement
- **Maintains Quality**: Still catches infinite loops and deadlocks
- **Flexible CI**: Different timeout strategies for different test types

## PR 02 — User Input & Selection

### Input Handler Module (ultrai/user_input.py)
- **Purpose**: Collect and validate user inputs for UltrAI execution
- **Usage**: Handle QUERY, ANALYSIS, COCKTAIL, ADDONS selections
- **Phase**: User Input & Selection (PR 02)
- **Functions**:
  - `collect_user_inputs()`: Main input collection with validation
  - `validate_inputs()`: Validate input dictionaries
  - `load_inputs()`: Load inputs from previous runs
- **Validation**: Enforces 4 pre-selected cocktails (PREMIUM, SPEEDY, BUDGET, DEPTH)
- **Artifact**: Creates runs/<RunID>/01_inputs.json

### Cocktail Definitions (Updated - removed unavailable models)
- **PREMIUM**: openai/gpt-4o (primary), anthropic/claude-3.7-sonnet, meta-llama/llama-4-maverick, google/gemini-2.0-flash-exp:free
- **SPEEDY**: openai/gpt-4o-mini (primary), anthropic/claude-3.5-haiku, google/gemini-2.0-flash-exp:free, meta-llama/llama-3.3-70b-instruct
- **BUDGET**: openai/gpt-3.5-turbo (primary), google/gemini-2.0-flash-exp:free, meta-llama/llama-3.3-70b-instruct, qwen/qwen-2.5-72b-instruct
- **DEPTH**: anthropic/claude-3.7-sonnet (primary), openai/gpt-4o, google/gemini-2.0-flash-thinking-exp:free, meta-llama/llama-3.3-70b-instruct
- **Source**: Updated based on OpenRouter availability (grok-4 and deepseek-r1 removed due to 404 errors)

### INACTIVE Structural Attachment Points (Architecture-Required Only)
- **INACTIVE_ADDON1**: Structural attachment point #1 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON2**: Structural attachment point #2 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON3**: Structural attachment point #3 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON4**: Structural attachment point #4 (preserves addon architecture for FUTURE deployment)
- **INACTIVE_ADDON5**: Structural attachment point #5 (preserves addon architecture for FUTURE deployment)


## PR 03 — Active LLMs Preparation

### Active LLMs Module (ultrai/active_llms.py)
- **Purpose**: Determine ACTIVE models by intersecting READY list with COCKTAIL selection
- **Usage**: Select which LLMs will participate in R1/R2 rounds (ACTIVE = READY ∩ COCKTAIL)
- **Phase**: Active LLMs Preparation (PR 03)
- **Functions**:
  - `prepare_active_llms()`: Main function to find intersection and create activeList
  - `load_active_llms()`: Load active LLMs from previous runs
- **Health Checks**: Verifies quorum of at least 2 ACTIVE models
- **Artifact**: Creates runs/<RunID>/02_activate.json
- **Error Handling**: Raises ActiveLLMError if quorum not met (low pluralism warning)

### PRIMARY and FALLBACK Model Mapping
- **PRIMARY_MODELS**: Core 3 models per cocktail (tried first, 33x faster than 10-model config)
- **FALLBACK_MODELS**: 3 backup models per cocktail (1:1 correspondence with PRIMARY, activated on timeout/failure)
- **PRIMARY_TIMEOUT**: 15 seconds allowed per attempt for PRIMARY model to respond
- **PRIMARY_ATTEMPTS**: 2 retry attempts before FALLBACK activation (total: 2 attempts × 15s = 30s max)
- **CONCURRENCY**: Semaphore-based async task limiting (set to 3 for PRIMARY models)
- **UVICORN_WORKER**: OS-level process handling individual user requests (3 workers in production)
- **Defined in**: ultrai/active_llms.py
- **Structure**: Dictionaries mapping cocktail names to lists of 3 model IDs each
- **Legacy Aliases**: COCKTAIL_MODELS=PRIMARY_MODELS, BACKUP_MODELS=FALLBACK_MODELS (for backward compatibility)

### Health Check Logic
- **Quorum Requirement**: At least 2 ACTIVE models required to proceed
- **Validation**: Verifies both 00_ready.json and 01_inputs.json exist
- **Intersection Logic**: Only models present in both READY and COCKTAIL become ACTIVE
- **Reasons Tracking**: Explains why each cocktail model is ACTIVE or NOT READY
- **Error Cases**: Missing prerequisites, insufficient ACTIVE models, invalid cocktail choice

## PR 04 — Initial Round (R1)

### Initial Round Module (ultrai/initial_round.py)
- **Purpose**: Execute R1 where each ACTIVE model independently responds to user query
- **Usage**: Orchestrate parallel API calls to all ACTIVE models
- **Phase**: Initial Round (PR 04)
- **Functions**:
  - `execute_initial_round()`: Main function to execute R1 for all ACTIVE models
  - `_execute_parallel_queries()`: Coordinate parallel API calls with rate limiting
  - `_query_single_model()`: Query individual model with retry logic
  - `calculate_concurrency_limit()`: Calculate dynamic rate limit based on query characteristics
- **Concurrency**: Uses async/await with semaphore-based rate limiting (1-3 concurrent, matching PRIMARY count)
- **Artifacts**: Creates runs/<RunID>/03_initial.json and runs/<RunID>/03_initial_status.json
- **Error Handling**: Implements mid-stream error detection (checks finish_reason)

### Optimized Concurrency for PRIMARY Models (IMPLEMENTED in PR 04)
- **Purpose**: Match concurrency to PRIMARY model count (3 per cocktail)
- **Implementation**: `calculate_concurrency_limit()` function in initial_round.py
- **Base Limit**: 3 concurrent (matches PRIMARY count)
- **FALLBACK Activation**: Sequential (only called after PRIMARY fails or times out)
  - **PRIMARY_TIMEOUT**: 15s per attempt
  - **PRIMARY_ATTEMPTS**: 2 attempts before FALLBACK (total: 30s max per PRIMARY)
- **Factors**:
  - **Attachments**: Images/files reduce concurrency (expensive on OpenRouter)
    - Single attachment: 2 concurrent
    - Multiple attachments (2-3): 2 concurrent
    - Many attachments (4+): 1 concurrent (serialized)
- **Range**: 1-3 concurrent requests (no longer dynamic 1-50 range)
- **Benefits**: Lower memory footprint, faster connection reuse, simpler code
- **Connection Pooling**: httpx.Limits with max_connections=3, max_keepalive_connections=3
- **Optimization**: Removes unnecessary query length calculations (negligible impact with only 3 calls)

### OpenRouter Chat Completions API
- **Endpoint**: POST https://openrouter.ai/api/v1/chat/completions
- **Usage**: Send user query to each ACTIVE model
- **Phase**: Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Headers**: Authorization (Bearer token), HTTP-Referer, X-Title, Content-Type
- **Payload**: {model: str, messages: [{role: str, content: str}]}
- **Response**: {choices: [{message: {content: str}, finish_reason: str}]}
- **Retry Logic**: Exponential backoff (3 attempts max), handles 401, 402, 429, 5xx errors
- **Timeout**: 60 seconds per request

### Mid-Stream Error Detection (IMPLEMENTED in PR 04)
- **Critical Requirement**: Check `finish_reason: "error"` in response payload
- **Why**: OpenRouter can return HTTP 200 but include errors in streamed data
- **Implementation**: After receiving response, check `result["choices"][0].get("finish_reason") == "error"`
- **Source**: UltrAI_OpenRouter.txt lines 137-140, marked as CRITICAL
- **Applied in**: initial_round.py line 271 (inside _query_single_model function)
- **Error Handling**: Raise InitialRoundError if finish_reason == "error"

### Response Timing
- **Measurement**: Record elapsed time in milliseconds for each model response
- **Purpose**: Track performance and compare model speeds
- **Storage**: Each response object includes "ms" field with integer milliseconds
- **Implementation**: Uses time.time() before/after API call

## PR 05 — Meta Round (R2)

### Meta Round Module (ultrai/meta_round.py)
- **Purpose**: Execute R2 where each ACTIVE model revises after reviewing peer INITIAL drafts
- **Usage**: Orchestrate parallel META queries with peer context
- **Phase**: Meta Round (PR 05)
- **Functions**:
  - `execute_meta_round()`: Main function to execute R2 for all ACTIVE models
  - `_execute_parallel_meta()`: Coordinate parallel API calls with rate limiting
  - `_query_meta_single()`: Query individual model with peer context and retry logic
- **Concurrency**: Uses async/await with variable semaphore-based rate limiting (1-50 concurrent)
- **Artifacts**: Creates runs/<RunID>/04_meta.json and runs/<RunID>/04_meta_status.json
- **Error Handling**: Implements mid-stream error detection (checks finish_reason)

### Variable Rate Limiting in R2 (IMPLEMENTED in PR 05)
- **Purpose**: Same as PR 04, but applied to META queries with peer context
- **Implementation**: Reuses `calculate_concurrency_limit()` from initial_round.py
- **Input**: Peer context length (concatenated INITIAL drafts for review)
- **Behavior**: META queries typically longer than INITIAL queries → lower concurrency
- **Range**: 1-50 concurrent requests based on peer context characteristics
- **Benefits**: Prevents timeouts on lengthy peer reviews, optimizes API usage

### Peer Review Prompt Pattern
- **Instruction**: "Do not assume any response is true. Review your peers' INITIAL drafts. Revise your answer accordingly. List contradictions you resolved and what changed."
- **System Message**: "You are in the META revision round (R2)."
- **Context Format**: Peer drafts presented as `- {model_id}: {text_snippet}` (truncated to 500 chars each)
- **Purpose**: Encourage models to critically evaluate peer outputs and revise

### META Response Structure
- **round**: Always "META" (distinguishes from INITIAL)
- **model**: Model identifier that produced the META response
- **text**: Revised response after peer review
- **ms**: Response time in milliseconds
- **error**: Boolean flag if query failed

## PR 06 — UltrAI Synthesis (R3)

### UltrAI Synthesis Module (ultrai/ultrai_synthesis.py)
- **Purpose**: Execute R3 where a neutral ULTRA model synthesizes META drafts into final output
- **Usage**: Select neutral model, merge META perspectives, generate synthesis with stats
- **Phase**: UltrAI Synthesis (PR 06)
- **Functions**:
  - `execute_ultrai_synthesis()`: Main function to execute R3 synthesis
  - `_select_ultra_model()`: Choose neutral model from ACTIVE list by preference
- **Concurrency**: Single API call (no parallelism) - queries one neutral model
- **Artifacts**: Creates runs/<RunID>/05_ultrai.json and runs/<RunID>/05_ultrai_status.json
- **Error Handling**: Implements mid-stream error detection (checks finish_reason)

### Neutral Model Selection Logic
- **PREFERRED_ULTRA**: Ordered list defining neutral model preferences
  - 1st choice: anthropic/claude-3.7-sonnet
  - 2nd choice: openai/gpt-4o
  - 3rd choice: google/gemini-2.0-flash-thinking-exp:free
  - 4th choice: meta-llama/llama-3.3-70b-instruct
- **Selection Algorithm**: Choose first preferred model found in ACTIVE list
- **Fallback**: If no preferred model in ACTIVE, use first ACTIVE model
- **Constraint**: Neutral model must be from ACTIVE list (ensures it's healthy and available)
- **Purpose**: Avoid bias by selecting model not biased toward any particular perspective

### Synthesis Prompt Pattern (UPDATED with critical fixes)
- **System Message**: "You are the ULTRAI neutral synthesis model (R3)."
- **Instruction Structure**:
  1. **Original Query**: 'The user asked: "{original_query}"'
  2. **Context**: "Multiple LLM models provided META responses to this query."
  3. **Critical Constraints**:
     - DO NOT introduce new information beyond what META models provided
     - DO NOT use own knowledge - rely ONLY on META drafts and query
     - DO NOT include data that evokes low confidence (omit claims where models strongly disagree or express uncertainty)
     - Role is to MERGE and SYNTHESIZE, not contribute new content
  4. **Task**: "Review all META drafts. Merge convergent points and resolve contradictions. Cite which META claims were retained or omitted. Generate one coherent synthesis with confidence notes and basic stats."
- **Context Format**: META drafts presented as `- {model_id}: {text_snippet}` (dynamic truncation)
- **Why Original Query Critical**: ULTRA model needs to know what question to answer (synthesis must address user's actual query)
- **Why Constraints Critical**:
  - ULTRA is a synthesizer, not an information contributor (prevents introducing content beyond multi-LLM consensus)
  - Low-confidence data filtering ensures synthesis only includes high-confidence convergent points
- **Purpose**: Produce unbiased, high-confidence synthesis integrating multiple META perspectives to answer the original query

### ULTRAI Response Structure (05_ultrai.json)
- **round**: Always "ULTRAI" (distinguishes from INITIAL/META)
- **model**: Model identifier that produced synthesis
- **neutralChosen**: Confirms neutral model selected (matches model field)
- **text**: Final synthesis text
- **ms**: Response time in milliseconds
- **stats**: Object with active_count and meta_count

### Status Metadata (05_ultrai_status.json)
- **status**: "COMPLETED"
- **round**: "R3"
- **details**: Contains model, neutral=true, concurrency_from_meta (reflects PR 05)
- **metadata**: run_id, timestamp, phase

### Dynamic Timeout (IMPLEMENTED in PR 06)
- **Purpose**: Adjust timeout based on synthesis complexity (input + output)
- **Implementation**: `calculate_synthesis_timeout()` function in ultrai_synthesis.py
- **Factors**:
  - **META Context Length**: Longer context requires more processing time
    - < 1000 chars: 60s (short synthesis)
    - 1000-3000 chars: 90s (medium synthesis)
    - 3000-5000 chars: 120s (long synthesis)
    - > 5000 chars: 180s (comprehensive synthesis)
  - **Number of META Drafts**: More drafts require more integration work
    - 4+ drafts: Multiply timeout by 1.2
- **Range**: Enforces minimum 60s, maximum 300s (5 minutes)
- **Rationale**: Complex queries → long META drafts → long synthesis input → long synthesis output
- **Benefits**: Prevents timeouts on comprehensive synthesis, allows thorough integration
- **Tests**: 8 unit tests verify calculation logic for all scenarios

### Dynamic META Truncation (IMPLEMENTED in PR 06)
- **Purpose**: Adjust max characters per META draft based on synthesis complexity
- **Implementation**: Calculated before building peer context in execute_ultrai_synthesis()
- **Scaling**:
  - **Timeout >= 180s** (complex query): 2000 chars per draft
  - **Timeout >= 120s** (medium complexity): 1200 chars per draft
  - **Timeout >= 90s** (moderate): 800 chars per draft
  - **Timeout < 90s** (simple): 500 chars per draft
- **Rationale**: Complex queries need more META context for thorough synthesis; simple queries need less
- **Benefits**: Balances comprehensiveness (long context) with API efficiency (shorter for simple queries)
- **Tracked**: max_chars_per_draft recorded in 05_ultrai_status.json
- **Tests**: Integration test verifies truncation varies with query complexity

### R3 Architecture Differences
- **No Variable Rate Limiting**: R3 queries single neutral model (not parallel like R1/R2)
- **Dynamic Timeout Instead**: Adjusts timeout based on META context length and complexity
- **No Concurrency Control**: Single API call doesn't require semaphore
- **Reflects META Concurrency**: Status includes concurrency_from_meta for observability
- **Sequential Execution**: R3 runs after R1 and R2 complete (depends on META drafts)


- **Purpose**: Structural module preserving addon architecture for FUTURE deployment
- **Functions**:
  - `_generate_inactive_addon1()`: INACTIVE placeholder for FUTURE implementation
  - `_generate_inactive_addon4()`: INACTIVE placeholder for FUTURE implementation
- **Artifacts**: Creates runs/<RunID>/06_final.json (no optional export files)
- **No API Calls**: Pure post-processing (no LLM queries in PR 07)

### INACTIVE Export Placeholders (Not User-Facing)
- **INACTIVE_ADDON1**: Structural placeholder for FUTURE export functionality
- **INACTIVE_ADDON4**: Structural placeholder for FUTURE export functionality
- **INACTIVE_ADDON2, INACTIVE_ADDON3, INACTIVE_ADDON5**: No export files (internal-only placeholders)

### 06_final.json Structure
- **round**: Always "FINAL"
- **text**: Final synthesis text (copied from 05_ultrai.json)
- **metadata**: run_id, timestamp, phase

## PR 08 — Statistics

### Statistics Module (ultrai/statistics.py)
- **Purpose**: Aggregate performance statistics from all phases into stats.json
- **Usage**: Collect timing and count data from R1, R2, R3 artifacts
- **Phase**: Statistics (PR 08)
- **Functions**:
  - `generate_statistics()`: Main function to aggregate and write stats.json
  - `_collect_initial_stats()`: Extract R1 statistics from 03_initial.json
  - `_collect_meta_stats()`: Extract R2 statistics from 04_meta.json
  - `_collect_ultrai_stats()`: Extract R3 statistics from 05_ultrai.json
- **Artifacts**: Creates runs/<RunID>/stats.json
- **Graceful Degradation**: Returns zero values if artifacts missing (doesn't crash)

### stats.json Structure
- **INITIAL**: {count: N, avg_ms: average response time}
- **META**: {count: N, avg_ms: average response time}
- **ULTRAI**: {count: 1, ms: synthesis response time}

### Statistics Calculation
- **INITIAL avg_ms**: Average of all INITIAL responses (excluding errors)
- **META avg_ms**: Average of all META responses (excluding errors)
- **ULTRAI ms**: Single synthesis response time
- **Count Fields**: Number of responses per round

## PR 09 — Final Delivery

### Final Delivery Module (ultrai/final_delivery.py)
- **Purpose**: Verify all artifacts exist and create delivery manifest for user
- **Usage**: Check artifact integrity, generate delivery.json manifest
- **Phase**: Final Delivery (PR 09)
- **Functions**:
  - `deliver_results()`: Verify artifacts and create delivery manifest
  - `load_synthesis()`: Load primary result (05_ultrai.json)
  - `load_all_artifacts()`: Load complete package for delivery
- **Artifacts**: Creates runs/<RunID>/delivery.json (manifest)
- **No Modifications**: Read-only verification (doesn't modify existing artifacts)

### Required Artifacts
- **05_ultrai.json**: UltrAI synthesis (main result)
- **03_initial.json**: R1 INITIAL responses
- **04_meta.json**: R2 META revisions
- **stats.json**: Performance statistics


### delivery.json Structure
- **status**: "COMPLETED" or "INCOMPLETE"
- **message**: Status message
- **artifacts**: Array of required artifacts with status (ready/missing/error)
- **optional_artifacts**: Array of export files found
- **missing_required**: List of missing required artifacts
- **metadata**: run_id, timestamp, phase, total_artifacts

### Delivery Status Logic
- **COMPLETED**: All 5 required artifacts present and valid JSON
- **INCOMPLETE**: One or more required artifacts missing
- **Artifact Verification**: Loads each JSON to verify validity (not just file existence)

## PR 20 — Frontend Foundation

### react
- **Purpose**: UI framework for building interactive web interfaces
- **Usage**: Component-based architecture for UltrAI frontend
- **Phase**: Frontend Foundation (PR 20+)
- **Version**: ^18.3.1

### react-dom
- **Purpose**: React rendering for web browsers
- **Usage**: Mount React components to DOM
- **Phase**: Frontend Foundation (PR 20+)
- **Version**: ^18.3.1

### vite
- **Purpose**: Build tool and development server
- **Usage**: Fast HMR dev server, optimized production builds
- **Phase**: Frontend Foundation (PR 20+)
- **Features**: ESM-based, instant server start, optimized bundling
- **Version**: ^6.0.1

### @vitejs/plugin-react
- **Purpose**: Vite plugin for React support
- **Usage**: Enable React Fast Refresh, JSX transformation
- **Phase**: Frontend Foundation (PR 20+)
- **Version**: ^4.3.4

### tailwindcss
- **Purpose**: Utility-first CSS framework
- **Usage**: Rapid styling with utility classes
- **Phase**: Frontend Foundation (PR 20+)
- **Version**: ^3.4.17

### postcss
- **Purpose**: CSS processing tool
- **Usage**: Required for Tailwind CSS processing
- **Phase**: Frontend Foundation (PR 20+)
- **Version**: ^8.4.49

### autoprefixer
- **Purpose**: PostCSS plugin for vendor prefixes
- **Usage**: Automatically add browser-specific CSS prefixes
- **Phase**: Frontend Foundation (PR 20+)
- **Version**: ^10.4.20

## PR 21 — API Integration Layer

### Native Fetch API
- **Purpose**: HTTP client for backend communication
- **Usage**: Zero-dependency API calls using browser's native fetch
- **Phase**: API Integration (PR 21+)
- **Why native fetch**: No axios dependency - keeps bundle small and simple
- **Features**: Custom APIError class, JSON parsing, error handling

### vitest
- **Purpose**: Frontend testing framework
- **Usage**: Unit and integration tests for React hooks and API client
- **Phase**: API Integration (PR 21+)
- **Version**: ^3.2.4
- **Features**: Vite integration, fast execution, ESM support

### @testing-library/react
- **Purpose**: React component and hook testing utilities
- **Usage**: Test React hooks with renderHook(), waitFor(), act()
- **Phase**: API Integration (PR 21+)
- **Version**: ^16.3.0
- **Critical**: Tests use REAL timers (not vi.useFakeTimers) to verify actual polling behavior

### @testing-library/jest-dom
- **Purpose**: Custom matchers for DOM testing
- **Usage**: Enhanced assertions for testing library
- **Phase**: API Integration (PR 21+)
- **Version**: ^6.9.1

### @testing-library/user-event
- **Purpose**: User interaction simulation
- **Usage**: Simulate user actions in component tests
- **Phase**: API Integration (PR 21+)
- **Version**: ^14.6.1

### jsdom
- **Purpose**: DOM implementation for testing
- **Usage**: Provides browser-like environment for tests
- **Phase**: API Integration (PR 21+)
- **Version**: ^27.0.1

### happy-dom
- **Purpose**: Alternative DOM implementation (lightweight)
- **Usage**: Optional faster DOM for simple tests
- **Phase**: API Integration (PR 21+)
- **Version**: ^20.0.5

## PR 22 — UI Components (Functional Basics)

### OrderReceipt Component (frontend/src/components/OrderReceipt.jsx)
- **Purpose**: Running summary panel showing user's selections as they progress through wizard
- **Usage**: Right-side panel (1/3 width) displaying query, cocktail, and completion status
- **Phase**: UI Components (PR 22+)
- **Features**: Status icons (✓ completed, ⏳ active, ○ pending), truncates long queries to 60 chars, shows "Ready to Activate" badge at step 4+
- **Props**: order (query, cocktail, cocktailDescription), currentStep (1-5)

### StepIndicator Component (frontend/src/components/StepIndicator.jsx)
- **Purpose**: Visual progress bar at top showing current wizard step
- **Usage**: Display 3-step wizard progress (Enter Query → Choose Cocktail → Confirm & Activate)
- **Phase**: UI Components (PR 22+)
- **Features**: Circles with checkmarks for completed steps, pulse animation for current step, connector lines between steps
- **Props**: currentStep (1-3), totalSteps (default: 3)

### StatusDisplay Component (frontend/src/components/StatusDisplay.jsx)
- **Purpose**: Real-time run status display during synthesis execution
- **Usage**: Shows current phase, round (R1/R2/R3), artifacts generated, error handling
- **Phase**: UI Components (PR 22+)
- **Features**: Maps phase files to human-readable names, displays artifact list, error banners
- **Props**: run (run_id, phase, round, completed, artifacts, error)

### ResultsDisplay Component (frontend/src/components/ResultsDisplay.jsx)
- **Purpose**: Final synthesis results viewer after run completes
- **Usage**: Fetches and displays synthesis from backend, shows stats, download artifacts link
- **Phase**: UI Components (PR 22+)
- **Features**: Loads 05_ultrai.json artifact, displays synthesis text and metadata
- **Props**: run (run object), onNewQuery (callback for new query button)

### Step1QueryInput Component (frontend/src/components/steps/Step1QueryInput.jsx)
- **Purpose**: Query input form (step 1 of wizard)
- **Usage**: Large 8-row textarea for user query with example queries and validation
- **Phase**: UI Components (PR 22+)
- **Features**: Character count, validation, example queries users can click, "Next" button disabled when empty
- **Props**: initialValue (existing query), onNext (callback with query text)

### Step2CocktailSelector Component (frontend/src/components/steps/Step2CocktailSelector.jsx)
- **Purpose**: Cocktail selection cards (step 2 of wizard)
- **Usage**: Visual cards for 5 cocktails (LUXE, PREMIUM, SPEEDY, BUDGET, DEPTH) with icons and model lists
- **Phase**: UI Components (PR 22+)
- **Features**: Icons (👑 LUXE, ⭐ PREMIUM, ⚡ SPEEDY, 💰 BUDGET, 🧠 DEPTH), shows models per cocktail, back/next navigation
- **Props**: initialValue (selected cocktail), onNext (callback with cocktail ID), onBack (callback)

### Step3Confirm Component (frontend/src/components/steps/Step3Confirm.jsx)
- **Purpose**: Confirmation and activation (step 3 of wizard)
- **Usage**: Review all selections, explain R1→R2→R3 process, BIG "Activate UltrAI" button
- **Phase**: UI Components (PR 22+)
- **Features**: Gradient blue→purple activate button, loading state, R1/R2/R3 process explanation
- **Props**: order (query, cocktail, cocktailDescription), onActivate (callback), onBack (callback), isActivating (boolean)

### App.jsx Updates (frontend/src/App.jsx)
- **Purpose**: Main app with wizard orchestration
- **Usage**: State management for 5-step wizard flow (Query → Cocktail → Confirm → Activate → Status → Results)
- **Phase**: UI Components (PR 22+)
- **Features**: Grid layout (2/3 main content + 1/3 receipt panel), health check banner, step transitions
- **State**: currentStep (1-5), order (query, cocktail, cocktailDescription), run management via useUltrAI hook

### Render Static Site Deployment (render.yaml)
- **Purpose**: Deploy frontend as static site on Render
- **Usage**: Build and serve React app on Render's CDN
- **Phase**: UI Components (PR 22+)
- **Configuration**:
  - Service type: web (static)
  - Build: `cd frontend && npm install && npm run build`
  - Publish: frontend/dist (Vite build output)
  - Environment: VITE_API_URL=https://ultrai-api.onrender.com
- **Benefits**: Free static hosting, CDN delivery, automatic HTTPS, zero-downtime deploys

### CORS Middleware (ultrai/api.py)
- **Purpose**: Allow frontend to make API requests from different origin
- **Usage**: Enable cross-origin requests from frontend domain
- **Phase**: UI Components (PR 22+)
- **Configuration**:
  - Allowed origins: http://localhost:3000 (dev), https://ultrai-frontend.onrender.com (prod)
  - Allow credentials: true
  - Allow methods: all
  - Allow headers: all
- **Security**: Restricts CORS to specific trusted frontend domains only

## Future Requirements

### UltrAI Synthesis (PR 06)
- **When**: Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Critical Requirement**: Must check `finish_reason: "error"` in response payload
- **Why**: OpenRouter can return HTTP 200 but include errors in streamed data
- **Implementation**: After receiving response, check `result["choices"][0].get("finish_reason") == "error"`
- **Source**: UltrAI_OpenRouter.txt lines 137-140, marked as CRITICAL
- **Note**: Not applicable to PR 01 (only queries GET /api/v1/models, not POST /chat/completions)

## PR 11 — Public API (FastAPI) + Render Blueprint

### fastapi
- **Purpose**: Public API server
- **Usage**: Expose /runs, /runs/{run_id}/status, /runs/{run_id}/artifacts, /health endpoints
- **Phase**: PR 11+ (deployment)
- **Features**: Async endpoints, background task orchestration, JSON responses

### uvicorn[standard]
- **Purpose**: ASGI server for FastAPI
- **Usage**: Run FastAPI in development and production (Render)
- **Phase**: PR 11+ (deployment)
- **Features**: Auto-reload, performance monitoring, production-ready HTTP server

### Public API Module (ultrai/api.py)
- **Purpose**: HTTP interface for UltrAI orchestration
- **Usage**: Expose REST endpoints for starting runs, checking status, listing artifacts
- **Phase**: PR 11 (Public API)
- **Functions**:
  - `start_run()`: POST /runs - Start orchestration (PR01→PR06), return run_id
  - `run_status()`: GET /runs/{run_id}/status - Current phase, artifacts, completion
  - `list_artifacts()`: GET /runs/{run_id}/artifacts - List artifact files
  - `health()`: GET /health - Health check (200 OK)
- **Non-blocking**: Uses asyncio.create_task to run pipeline in background
- **Artifacts**: Creates run directories and JSON files via existing modules

### Render Blueprint (render.yaml)
- **Purpose**: Infrastructure-as-code for Render deployment
- **Usage**: Define Web Service, build/start commands, environment variables
- **Phase**: PR 11+ (deployment)
- **Configuration**:
  - Service type: web (Python runtime)
  - Build: pip install -U pip && pip install -r requirements.txt
  - Start: uvicorn ultrai.api:app --host 0.0.0.0 --port $PORT
  - Health check: /health
  - Environment: OPENROUTER_API_KEY, YOUR_SITE_URL, YOUR_SITE_NAME
