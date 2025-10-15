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

### Cocktail Definitions
- **PREMIUM**: openai/gpt-4o (primary), x-ai/grok-4, meta-llama/llama-4-maverick, deepseek/deepseek-r1
- **SPEEDY**: openai/gpt-4o-mini (primary), x-ai/grok-4-fast, anthropic/claude-3.7-sonnet, meta-llama/llama-3.3-70b-instruct
- **BUDGET**: openai/gpt-3.5-turbo (primary), mistralai/mistral-large, meta-llama/llama-3.3-70b-instruct, x-ai/grok-4-fast:free
- **DEPTH**: anthropic/claude-3.7-sonnet (primary), openai/gpt-4o, x-ai/grok-4, deepseek/deepseek-r1
- **Source**: UltrAI_OpenRouter.txt (v2.0 CORRECTED)

### Available Add-ons
- **citation_tracking**: Track sources and citations in responses
- **cost_monitoring**: Track token usage and costs per request
- **extended_stats**: Additional statistical analysis beyond standard metrics
- **visualization**: Generate visual representations of results
- **confidence_intervals**: Include confidence scoring for synthesis

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

### Cocktail-to-Model Mapping (COCKTAIL_MODELS constant)
- **Purpose**: Define which specific LLM models belong to each cocktail
- **Usage**: Map user's COCKTAIL choice to list of model identifiers
- **Defined in**: ultrai/active_llms.py
- **Structure**: Dictionary mapping cocktail names to lists of 4 model IDs each
- **Source**: UltrAI_OpenRouter.txt v2.0 CORRECTED specifications

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
- **Concurrency**: Uses async/await with variable semaphore-based rate limiting (1-50 concurrent)
- **Artifacts**: Creates runs/<RunID>/03_initial.json and runs/<RunID>/03_initial_status.json
- **Error Handling**: Implements mid-stream error detection (checks finish_reason)

### Variable Rate Limiting (IMPLEMENTED in PR 04)
- **Purpose**: Optimize performance and cost by adjusting concurrency based on query characteristics
- **Implementation**: `calculate_concurrency_limit()` function in initial_round.py
- **Factors**:
  - **Query Length**: Shorter queries get higher concurrency (faster, cheaper)
    - < 200 chars: 100% concurrency (50 concurrent)
    - 200-1000 chars: 60% concurrency (30 concurrent)
    - 1000-5000 chars: 30% concurrency (15 concurrent)
    - > 5000 chars: 10% concurrency (5 concurrent)
  - **Attachments**: Images/files reduce concurrency (expensive on OpenRouter)
    - Single attachment: -50% (multiply by 0.5)
    - Multiple attachments (2-3): -75% (multiply by 0.25)
    - Many attachments (4+): -90% (multiply by 0.1)
- **Range**: Enforces minimum of 1 and maximum of 50 concurrent requests
- **Benefits**: Prevents timeouts on complex queries, reduces API costs on attachment-heavy queries
- **Future**: Will support attachment detection when attachment feature is implemented
- **Tests**: 11 unit tests verify calculation logic for all scenarios

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
  - 3rd choice: x-ai/grok-4
  - 4th choice: deepseek/deepseek-r1
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

## Future Requirements

### UltrAI Synthesis (PR 06)
- **When**: Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Critical Requirement**: Must check `finish_reason: "error"` in response payload
- **Why**: OpenRouter can return HTTP 200 but include errors in streamed data
- **Implementation**: After receiving response, check `result["choices"][0].get("finish_reason") == "error"`
- **Source**: UltrAI_OpenRouter.txt lines 137-140, marked as CRITICAL
- **Note**: Not applicable to PR 01 (only queries GET /api/v1/models, not POST /chat/completions)
