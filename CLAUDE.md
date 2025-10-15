# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UltrAI is a multi-LLM synthesis system that orchestrates multiple language models through sequential rounds to produce consensus-driven outputs. The system operates in three core rounds:

1. **R1 (INITIAL)**: All active LLMs independently respond to the user query
2. **R2 (META)**: Each LLM revises its response after reviewing peer outputs, resolving contradictions
3. **R3 (ULTRA)**: A neutral synthesizer LLM merges META drafts into a final synthesis with confidence intervals

## Development Commands

```bash
# Create virtual environment
make venv

# Install dependencies
make install

# Run all tests
make test

# Run full CI pipeline (install + test)
make ci

# Run a single test file
. .venv/bin/activate && pytest tests/test_repo_structure.py

# Run specific test function
. .venv/bin/activate && pytest tests/test_repo_structure.py::test_templates_exist -v
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

Each run creates a directory `runs/<RunID>/` containing:
- `00_ready.json` - List of ready LLMs
- Round outputs for R1, R2, R3
- `stats.json` - Analytics and performance metrics
- `status.json` - Error states and warnings

### Key Terminology

- **READY**: Set of all available/healthy LLMs from OpenRouter
- **ACTIVE**: Subset of READY models selected for R1/R2 rounds
- **ULTRA**: Neutral synthesizer model from READY used for R3
- **INITIAL**: R1 outputs (user-visible after ULTRA completes)
- **META**: R2 outputs (user-visible after ULTRA completes)

## Critical Constraints

### Terminology and Naming (vision/CONTRIBUTING.md)
- No new terminology may be introduced without definition
- All immutable names tracked in `trackers/names.md`
- Use exact terms from flow specifications (R1/R2/R3, READY/ACTIVE/ULTRA, INITIAL/META)

### Testing Requirements
- Every test must be traceable to concrete, reproducible outcomes
- Tests verify existence and content of run artifacts (not mocks)
- Each PR phase has specific testing endpoints (see PR templates)

### Dependency and Change Tracking
- Every PR must update `trackers/dependencies.md` (software dependencies and purpose)
- Every PR must update `trackers/names.md` (immutable identifiers introduced)
- One PR = One clearly defined system change

### Pull Request Process
- Use phase-specific PR templates in `.github/PULL_REQUEST_TEMPLATE/`
- Verify PR index (`pr_index.md`) links match actual template files
- Each PR must specify artifacts produced and testing endpoints

## Model Selection and Prompting

### R1 Prompt Pattern
Each ACTIVE model receives the same user query independently.

### R2 Prompt Pattern
```
Do not assume any response is true.
Revise your answer after reviewing your peers.
List contradictions resolved and what changed.
```

### R3 Prompt Pattern
```
Review all META drafts.
Merge convergent points and resolve contradictions.
Cite which META claims were retained or omitted.
Generate one coherent synthesis with confidence intervals and model statistics.
```

## Error Handling

- `READY < 2 models` → Abort with "low pluralism warning"
- `ULTRA model missing` → Continue in degraded mode, flag run
- Missing `OPENROUTER_API_KEY` → Fail at system readiness phase

## User Visibility Timing

- **ULTRA synthesis**: Shown immediately upon R3 completion
- **INITIAL (R1) outputs**: Revealed after ULTRA completes (background tab)
- **META (R2) outputs**: Revealed after ULTRA completes (background tab)
- **STATS**: Available after run completion
- **Error banners**: Displayed immediately when detected
