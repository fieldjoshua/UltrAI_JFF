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

## Future Requirements

### Meta Round (PR 05)
- Will reuse OpenRouter Chat Completions API with different prompt pattern
- Each model reviews peer INITIAL outputs and revises its response
- Must track which INITIAL outputs each META response considered

### UltrAI Synthesis (PR 06)
- **When**: Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Critical Requirement**: Must check `finish_reason: "error"` in response payload
- **Why**: OpenRouter can return HTTP 200 but include errors in streamed data
- **Implementation**: After receiving response, check `result["choices"][0].get("finish_reason") == "error"`
- **Source**: UltrAI_OpenRouter.txt lines 137-140, marked as CRITICAL
- **Note**: Not applicable to PR 01 (only queries GET /api/v1/models, not POST /chat/completions)
