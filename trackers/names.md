Immutable names used in UltrAI (files, stage names, identifiers).

## PR 01 — System Readiness

### Terms
- **READY**: The complete set of LLMs available and healthy from OpenRouter at system check time
- **Run ID**: Unique identifier for each UltrAI execution (format: timestamp-based UUID or ISO datetime)

### File Names
- **00_ready.json**: System readiness output artifact containing readyList and metadata

### Data Structure Fields
- **readyList**: Array of LLM identifiers that passed health checks (minimum 2 required for execution)
