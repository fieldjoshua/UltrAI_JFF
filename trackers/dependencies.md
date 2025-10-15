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

## Future Requirements

### Mid-Stream Error Detection (PR 04+)
- **When**: Initial Round (PR 04), Meta Round (PR 05), UltrAI Synthesis (PR 06)
- **Critical Requirement**: Must check `finish_reason: "error"` in response payload
- **Why**: OpenRouter can return HTTP 200 but include errors in streamed data
- **Implementation**: After receiving response, check `result["choices"][0].get("finish_reason") == "error"`
- **Source**: UltrAI_OpenRouter.txt lines 137-140, marked as CRITICAL
- **Note**: Not applicable to PR 01 (only queries GET /api/v1/models, not POST /chat/completions)
