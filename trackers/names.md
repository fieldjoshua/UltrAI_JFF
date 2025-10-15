Immutable names used in UltrAI (files, stage names, identifiers).

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
- **INPUTS**: Collective term for all user-provided inputs (QUERY, ANALYSIS, COCKTAIL, ADDONS)
- **QUERY**: User's question or prompt to be analyzed by the LLM orchestration
- **ANALYSIS**: Type of analysis to perform (currently: "Synthesis" = R1 + R2 + R3 rounds)
- **COCKTAIL**: Pre-selected group of LLMs chosen by user (one of 4 choices)
- **ADDONS**: Optional features enabled by user (list of add-on identifiers)

### File Names
- **01_inputs.json**: User input artifact containing QUERY, ANALYSIS, COCKTAIL, ADDONS, and metadata

### Cocktail Names (4 Pre-Selected Choices)
- **PREMIUM**: High-quality models focused on accuracy and capability
- **SPEEDY**: Fast models optimized for quick responses
- **BUDGET**: Cost-effective models balancing quality and expense
- **DEPTH**: Deep reasoning models for complex analytical tasks

### Add-on Names
- **citation_tracking**: Track and cite sources in LLM responses
- **cost_monitoring**: Monitor token usage and API costs
- **extended_stats**: Generate additional statistical metrics
- **visualization**: Create visual representations of results
- **confidence_intervals**: Include confidence scores in synthesis
