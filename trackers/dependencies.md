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

## Future Requirements

### Mid-Stream Error Detection (PR 04+)
- **When**: Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Critical Requirement**: Must check `finish_reason: "error"` in response payload
- **Why**: OpenRouter can return HTTP 200 but include errors in streamed data
- **Implementation**: After receiving response, check `result["choices"][0].get("finish_reason") == "error"`
- **Source**: UltrAI_OpenRouter.txt lines 137-140, marked as CRITICAL
- **Note**: Not applicable to PR 01 (only queries GET /api/v1/models, not POST /chat/completions)
