# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UltrAI is a multi-LLM synthesis system that orchestrates multiple language models through sequential rounds to produce consensus-driven outputs. The system operates in three core rounds:

1. **R1 (INITIAL)**: All active LLMs independently respond to the user query
2. **R2 (META)**: Each LLM revises its response after reviewing peer outputs, resolving contradictions
3. **R3 (ULTRA)**: A neutral synthesizer LLM merges META drafts into a final synthesis with confidence intervals

## Development Commands

```bash
# Setup
make venv                    # Create virtual environment
make install                 # Install dependencies
make ci                      # Full CI pipeline (install + test)

# Run the interactive CLI
make run                     # Launches UltrAI CLI
python3 -m ultrai.cli        # Alternative CLI launch

# Benchmarking
make timings                 # Benchmark all cocktails and generate CSV report

# Testing
make test                    # Run all tests (quick summary)
make test-verbose            # Detailed output (-vv)
make test-narrative          # Narrative summary (--narrative flag)
make test-summary            # Clean summary by PR phase

# Test by PR phase
make test-pr01               # System Readiness tests
make test-pr02               # User Input tests
make test-pr03               # Active LLMs tests
make test-pr04               # Initial Round (R1) tests
make test-pr05               # Meta Round (R2) tests
make test-pr06               # UltrAI Synthesis (R3) tests
make test-pr08               # Statistics tests
make test-pr09               # Final Delivery tests

# Run a single test file
. .venv/bin/activate && pytest tests/test_repo_structure.py

# Run specific test function
. .venv/bin/activate && pytest tests/test_repo_structure.py::test_templates_exist -v

# Specialized testing
make test-real-api           # Only tests requiring OpenRouter API
make test-integration        # Integration tests
make list-tests              # List all tests with descriptions
```

## Architecture

### Sequential Phase Structure

The system follows a 10-phase PR template structure corresponding to the synthesis sequence:

1. **System Readiness** - Verify dependencies, OpenRouter connection, LLM availability (produces `00_ready.json` with readyList)
2. **User Input Selection** - Validate and prepare user query
3. **Active LLMs Preparation** - Select ACTIVE models from READY list
4. **Initial Round (R1)** - Execute parallel independent responses
5. **Meta Round (R2)** - Execute revision round with peer review
6. **UltrAI Synthesis (R3)** - Neutral ULTRA model produces final synthesis
8. **Statistics** - Record and transmit performance metrics
9. **Final Delivery** - Deliver synthesis and all prior round outputs
10. **Error Handling/Fallbacks** - Graceful degradation (READY<2 aborts, missing ULTRA flags degraded mode)

### Run Artifacts

Each run creates a directory `runs/<RunID>/` with the following artifacts:

**Required Artifacts** (verified by PR 09 delivery manifest):
- `00_ready.json` - List of READY LLMs from OpenRouter
- `01_inputs.json` - User QUERY, COCKTAIL, ANALYSIS
- `02_activate.json` - ACTIVE LLMs (READY ∩ COCKTAIL) with quorum validation and backup models
- `03_initial.json` - R1 INITIAL responses from all ACTIVE models
- `03_initial_status.json` - R1 execution metadata (concurrency, timing)
- `04_meta.json` - R2 META responses (revisions after peer review)
- `04_meta_status.json` - R2 execution metadata
- `05_ultrai.json` - R3 ULTRA synthesis (final merged output)
- `05_ultrai_status.json` - R3 execution metadata (timeout, context length)
- `stats.json` - Performance statistics (R1/R2/R3 timing and counts)
- `delivery.json` - Delivery manifest verifying all artifacts

### Key Terminology

All terminology is immutably defined in `trackers/names.md`. Key terms:

- **READY**: Set of all available/healthy LLMs from OpenRouter at system check time
- **ACTIVE**: Subset of READY models selected for R1/R2 rounds (ACTIVE = READY ∩ COCKTAIL)
- **PRIMARY**: Core 3 models per cocktail tried first (33x faster than previous 10-model config)
- **FALLBACK**: 3 backup models per cocktail activated if PRIMARY fails or times out
- **PRIMARY_TIMEOUT**: 15 seconds allowed per attempt for PRIMARY model to respond
- **PRIMARY_ATTEMPTS**: 2 retry attempts before FALLBACK activation (2 × 15s = 30s max)
- **CONCURRENCY**: Maximum simultaneous async tasks (semaphore-based, set to 3 for PRIMARY models)
- **UVICORN_WORKER**: OS-level process handling individual user requests (3 workers in production)
- **ULTRA**: Neutral synthesizer model selected from ACTIVE for R3 (preference: claude-3.7-sonnet → gpt-4o → gemini-2.0-thinking → llama-3.3-70b)
- **INITIAL**: R1 outputs (user-visible after ULTRA completes)
- **META**: R2 outputs (user-visible after ULTRA completes)
- **COCKTAIL**: Pre-selected group of LLMs chosen by user (LUXE, PREMIUM, SPEEDY, BUDGET, or DEPTH)
- **Run ID**: Unique identifier for each execution (timestamp-based format: YYYYMMDD_HHMMSS)
- **quorum**: Minimum required ACTIVE models to proceed (always 2)

## Critical Constraints

### Terminology and Naming (vision/CONTRIBUTING.md)
- No new terminology may be introduced without definition
- All immutable names tracked in `trackers/names.md`
- Use exact terms from flow specifications (R1/R2/R3, READY/ACTIVE/ULTRA, INITIAL/META)

### Testing Requirements
- **CRITICAL**: NEVER use mock tests - all tests must use real OpenRouter API calls
- Every test must be traceable to concrete, reproducible outcomes
- Tests verify existence and content of run artifacts (JSON files in runs/<RunID>/)
- Each PR phase has specific testing endpoints (see PR templates in `.github/PULL_REQUEST_TEMPLATE/`)
- Tests requiring OpenRouter API use `@skip_if_no_api_key` decorator
- Test pattern: run full pipeline → verify artifacts exist → validate artifact contents

### CI/CD Testing Policy - Smart Test Selection
- **CI runs ONLY tests relevant to changed files** - not all 132 tests
- Changed file detection maps to PR markers (pr01, pr02, pr03, etc.)
- Example: If `ultrai/user_input.py` changed → runs `@pytest.mark.pr02` tests only
- If test infrastructure changes (`conftest.py`, `pyproject.toml`) → runs ALL tests
- `test_timeout_display.py` always excluded (intentional 15-120s timeouts for demo)
- This keeps CI fast (10-30 tests per PR instead of 132) while ensuring quality
- Run locally: `pytest tests/ -m pr02` (replace pr02 with your PR number)

### Dependency and Change Tracking
- Every PR must update `trackers/dependencies.md` (software dependencies and purpose)
- Every PR must update `trackers/names.md` (immutable identifiers introduced)
- One PR = One clearly defined system change

### Pull Request Process
- Use phase-specific PR templates in `.github/PULL_REQUEST_TEMPLATE/`
- Verify PR index (`pr_index.md`) links match actual template files
- Each PR must specify artifacts produced and testing endpoints

## Cocktail Definitions

Five pre-selected LLM groups (defined in `ultrai/active_llms.py`). All cocktails use exactly 3 models for optimal speed/cost balance (33x faster than previous 10-model configuration):

- **LUXE**: Flagship premium models (openai/gpt-4o, anthropic/claude-sonnet-4.5, google/gemini-2.0-flash-exp:free)
- **PREMIUM**: High-quality models (anthropic/claude-3.7-sonnet, openai/chatgpt-4o-latest, meta-llama/llama-3.3-70b-instruct)
- **SPEEDY**: Fast response models (openai/gpt-4o-mini, anthropic/claude-3.5-haiku, google/gemini-2.0-flash-exp:free)
- **BUDGET**: Cost-effective models (openai/gpt-3.5-turbo, google/gemini-2.0-flash-exp:free, qwen/qwen-2.5-72b-instruct)
- **DEPTH**: Deep reasoning models (anthropic/claude-3.7-sonnet, openai/gpt-4o, meta-llama/llama-3.3-70b-instruct)

## Model Selection and Prompting

### Fast-Fail System with PRIMARY and FALLBACK Models

Each cocktail has 3 PRIMARY models and 3 corresponding FALLBACK models (1:1 correspondence). When a PRIMARY model fails during R1 or R2:
1. System makes PRIMARY_ATTEMPTS (2 attempts × PRIMARY_TIMEOUT 15s = 30s max) before giving up
2. If PRIMARY fails after all attempts, system immediately tries the corresponding FALLBACK model
3. FALLBACK model is selected from the same cocktail tier (same index position)
4. Failed models are tracked and excluded from R2 retry attempts
5. This ensures resilience without sacrificing speed

### Optimized Concurrency for PRIMARY Models

R1 and R2 use optimized concurrency matching the PRIMARY model count:
- **Base Concurrency**: 3 concurrent (matches PRIMARY count)
- **FALLBACK Execution**: Sequential (only after PRIMARY fails/times out)
- **PRIMARY_TIMEOUT**: 15 seconds per attempt
- **PRIMARY_ATTEMPTS**: 2 attempts before FALLBACK (total: 30s max per PRIMARY)
- **With attachments**: Reduced concurrency based on attachment count:
  - Single attachment: 2 concurrent
  - Multiple attachments (2-3): 2 concurrent
  - Many attachments (4+): 1 concurrent (serialized)
- **Connection Pooling**: httpx.Limits with max_connections=3, max_keepalive_connections=3

This optimization provides lower memory footprint, faster connection reuse, and simpler code compared to previous variable 1-50 range.

### R1 Prompt Pattern
Each ACTIVE model receives the same user query independently (no peer context).

### R2 Prompt Pattern
Each ACTIVE model receives:
1. Original user query
2. Concatenated INITIAL (R1) responses from ALL ACTIVE models (peer context)
3. Instructions:
```
Do not assume any response is true.
Revise your answer after reviewing your peers.
List contradictions resolved and what changed.
```

### R3 Prompt Pattern (CRITICAL CONSTRAINTS)

ULTRA model receives:
1. Original user QUERY
2. Concatenated META (R2) responses (dynamically truncated 500-2000 chars per draft based on synthesis timeout)
3. **Four critical constraints**:
   - DO NOT introduce new information beyond META drafts
   - DO NOT use your own knowledge - rely ONLY on META drafts and query
   - DO NOT include data that evokes low confidence (omit claims where models disagree/uncertain)
   - Your role is to MERGE and SYNTHESIZE, not contribute new content

Instructions:
```
Review all META drafts.
Merge convergent points and resolve contradictions.
Cite which META claims were retained or omitted.
Generate one coherent synthesis with confidence notes and basic stats.
```

**Dynamic META Truncation**: Based on synthesis timeout (calculated from context length):
- Timeout >= 180s: 2000 chars/draft (complex queries)
- Timeout >= 120s: 1200 chars/draft
- Timeout >= 90s: 800 chars/draft
- Timeout < 90s: 500 chars/draft (simple queries)

**Smart Timeout Logic**:
- Fast-fail timeouts for connection (10s connect, 15s read per chunk)
- Exponential backoff with PRIMARY_ATTEMPTS (2 attempts) before FALLBACK
- Rate limit errors (429) count as failed attempts, trigger FALLBACK after PRIMARY_ATTEMPTS

## Module Structure

Core modules in `ultrai/` directory (sequential execution order):

1. **system_readiness.py** (PR 01) - Verify OpenRouter connection, fetch available LLMs → creates `00_ready.json`
2. **user_input.py** (PR 02) - Collect QUERY, COCKTAIL → creates `01_inputs.json`
3. **active_llms.py** (PR 03) - Calculate ACTIVE = READY ∩ COCKTAIL, prepare backups → creates `02_activate.json`
4. **initial_round.py** (PR 04) - Execute R1 (parallel independent responses) → creates `03_initial.json`, `03_initial_status.json`
5. **meta_round.py** (PR 05) - Execute R2 (revisions with peer review) → creates `04_meta.json`, `04_meta_status.json`
6. **ultrai_synthesis.py** (PR 06) - Execute R3 (neutral synthesis) → creates `05_ultrai.json`, `05_ultrai_status.json`
8. **statistics.py** (PR 08) - Aggregate timing/count data → creates `stats.json`
9. **final_delivery.py** (PR 09) - Verify artifacts, create manifest → creates `delivery.json`
10. **cli.py** - Interactive command-line interface for UltrAI

Each module defines:
- Custom exception class (e.g., `SystemReadinessError`, `UserInputError`)
- Main function for phase execution
- Load function for reading previous artifacts
- CLI entry point (`if __name__ == "__main__"`)

## Error Handling

- `READY < 2 models` → Abort with "low pluralism warning" (insufficient quorum)
- `ULTRA model missing from ACTIVE` → Continue in degraded mode, flag run (use first ACTIVE model as fallback)
- Missing `OPENROUTER_API_KEY` → Fail at system readiness phase (cannot connect to API)
- `quorum < 2` → Abort execution (need at least 2 ACTIVE models for synthesis)
- Missing artifacts → Raise phase-specific error (e.g., `ActiveLLMError` if `00_ready.json` missing)
- Invalid JSON → delivery.json marks artifact as "error" status
- API failures → Backup model attempted immediately, failures tracked in `failed_models` field
- Failed models in R1 → Excluded from R2 retry attempts to prevent repeated failures

## User Visibility Timing

- **ULTRA synthesis**: Shown immediately upon R3 completion
- **INITIAL (R1) outputs**: Revealed after ULTRA completes (background tab)
- **META (R2) outputs**: Revealed after ULTRA completes (background tab)
- **STATS**: Available after run completion
- **Error banners**: Displayed immediately when detected
- **Add-ons**: Applied after synthesis, exported files listed in delivery manifest

## Environment Setup

Required environment variable:
```bash
# Create .env file in project root
OPENROUTER_API_KEY=your_key_here
```

The system will fail at PR 01 (system readiness) if this key is not set or invalid.
