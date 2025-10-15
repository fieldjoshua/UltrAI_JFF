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
make test-pr07               # Add-ons Processing tests
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
7. **Add-ons Processing** - Apply post-processing enhancements
8. **Statistics** - Record and transmit performance metrics
9. **Final Delivery** - Deliver synthesis and all prior round outputs
10. **Error Handling/Fallbacks** - Graceful degradation (READY<2 aborts, missing ULTRA flags degraded mode)

### Run Artifacts

Each run creates a directory `runs/<RunID>/` with the following artifacts:

**Required Artifacts** (verified by PR 09 delivery manifest):
- `00_ready.json` - List of READY LLMs from OpenRouter
- `01_inputs.json` - User QUERY, COCKTAIL, ADDONS, ANALYSIS
- `02_activate.json` - ACTIVE LLMs (READY ∩ COCKTAIL) with quorum validation
- `03_initial.json` - R1 INITIAL responses from all ACTIVE models
- `03_initial_status.json` - R1 execution metadata (concurrency, timing)
- `04_meta.json` - R2 META responses (revisions after peer review)
- `04_meta_status.json` - R2 execution metadata
- `05_ultrai.json` - R3 ULTRA synthesis (final merged output)
- `05_ultrai_status.json` - R3 execution metadata (timeout, context length)
- `06_final.json` - Final output with add-ons applied
- `stats.json` - Performance statistics (R1/R2/R3 timing and counts)
- `delivery.json` - Delivery manifest verifying all artifacts

**Optional Artifacts** (created if add-ons selected):
- `06_visualization.txt` - Visual representation export (visualization add-on)
- `06_citations.json` - Citation tracking export (citation_tracking add-on)

### Key Terminology

All terminology is immutably defined in `trackers/names.md`. Key terms:

- **READY**: Set of all available/healthy LLMs from OpenRouter at system check time
- **ACTIVE**: Subset of READY models selected for R1/R2 rounds (ACTIVE = READY ∩ COCKTAIL)
- **ULTRA**: Neutral synthesizer model selected from ACTIVE for R3 (preference: claude-3.7-sonnet → gpt-4o → grok-4 → deepseek-r1)
- **INITIAL**: R1 outputs (user-visible after ULTRA completes)
- **META**: R2 outputs (user-visible after ULTRA completes)
- **COCKTAIL**: Pre-selected group of LLMs chosen by user (PREMIUM, SPEEDY, BUDGET, or DEPTH)
- **ADDONS**: Optional post-processing features (citation_tracking, cost_monitoring, extended_stats, visualization, confidence_intervals)
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

### Dependency and Change Tracking
- Every PR must update `trackers/dependencies.md` (software dependencies and purpose)
- Every PR must update `trackers/names.md` (immutable identifiers introduced)
- One PR = One clearly defined system change

### Pull Request Process
- Use phase-specific PR templates in `.github/PULL_REQUEST_TEMPLATE/`
- Verify PR index (`pr_index.md`) links match actual template files
- Each PR must specify artifacts produced and testing endpoints

## Cocktail Definitions

Four pre-selected LLM groups (defined in `ultrai/active_llms.py`):

- **PREMIUM**: High-quality models (openai/gpt-4o, x-ai/grok-4, meta-llama/llama-4-maverick, deepseek/deepseek-r1)
- **SPEEDY**: Fast response models (openai/gpt-4o-mini, x-ai/grok-4-fast, anthropic/claude-3.7-sonnet, meta-llama/llama-3.3-70b-instruct)
- **BUDGET**: Cost-effective models (openai/gpt-3.5-turbo, mistralai/mistral-large, meta-llama/llama-3.3-70b-instruct, x-ai/grok-4-fast:free)
- **DEPTH**: Deep reasoning models (anthropic/claude-3.7-sonnet, openai/gpt-4o, x-ai/grok-4, deepseek/deepseek-r1)

## Model Selection and Prompting

### Variable Rate Limiting

R1 and R2 use dynamic concurrency based on query complexity:
- **Base**: 10 concurrent requests
- **Simple query** (< 50 chars, no attachments): 50 concurrent requests
- **Medium query** (50-200 chars): 30 concurrent requests
- **Complex query** (> 200 chars, has attachments): 10 concurrent requests

This prevents API throttling on complex queries while maximizing throughput on simple queries.

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

## Module Structure

Core modules in `ultrai/` directory (sequential execution order):

1. **system_readiness.py** (PR 01) - Verify OpenRouter connection, fetch available LLMs → creates `00_ready.json`
2. **user_input.py** (PR 02) - Collect QUERY, COCKTAIL, ADDONS → creates `01_inputs.json`
3. **active_llms.py** (PR 03) - Calculate ACTIVE = READY ∩ COCKTAIL → creates `02_activate.json`
4. **initial_round.py** (PR 04) - Execute R1 (parallel independent responses) → creates `03_initial.json`, `03_initial_status.json`
5. **meta_round.py** (PR 05) - Execute R2 (revisions with peer review) → creates `04_meta.json`, `04_meta_status.json`
6. **ultrai_synthesis.py** (PR 06) - Execute R3 (neutral synthesis) → creates `05_ultrai.json`, `05_ultrai_status.json`
7. **addons_processing.py** (PR 07) - Apply post-processing add-ons → creates `06_final.json` + optional exports
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
- API failures → Captured in response objects with `error: true` field

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
