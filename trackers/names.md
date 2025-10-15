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

## PR 03 — Active LLMs Preparation

### Terms
- **ACTIVE**: The subset of READY models that match the selected COCKTAIL (ACTIVE = READY ∩ COCKTAIL)
- **ACTIVATE**: The phase/action of determining which LLMs will participate in R1/R2 rounds
- **quorum**: Minimum required ACTIVE models to proceed with synthesis (always 2)

### File Names
- **02_activate.json**: Active LLMs preparation output artifact containing activeList, quorum, and reasons

### Data Structure Fields
- **activeList**: Array of ACTIVE LLM identifiers (intersection of READY and COCKTAIL)
- **reasons**: Dictionary explaining status of each cocktail model (ACTIVE or NOT READY)

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
