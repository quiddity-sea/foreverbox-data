---
name: delegation-model-inheritance
description: Understanding model inheritance in Hermes Agent delegation
version: 1.0.0
---
# Delegation Model Inheritance

## Overview
When using the `delegate_task` tool, child agents inherit the parent agent's model configuration by default. This skill documents the behavior, common pitfalls, and best practices for managing model delegation in Hermes Agent.

## Trigger Conditions
Use this knowledge and patterns when:
- Using the `delegate_task` tool to spawn subagents
- Observing unexpected model behavior in delegated tasks
- Debugging why a delegated task is not using a specific model
- Planning to delegate tasks requiring specific model capabilities

## Key Concepts

### Model Inheritance
By default, delegated child agents inherit:
- The parent agent's provider (e.g., `ollama`, `openrouter`)
- The parent agent's model name (e.g., `gemma4:31b`, `nemotron-3-super-120b-a12b:free`)
- The parent agent's fallback chain and context settings

This inheritance happens automatically unless explicitly overridden.

### Common Pitfalls

### Assuming Child Agents Use Different Models
A frequent mistake is believing that delegated tasks (e.g., wolf research workers) use specialized or different models. In reality, unless configured otherwise, they use the exact same model as the parent agent.

**Example of incorrect assumption:**
```python
# INCORRECT: Assuming wolf research uses a different model
delegate_task(
    goal="Research the latest delegation patterns",
    role="orchestrator"
    # Mistakenly thinking this will use a wolf-specific model
)
```

### Overestimating Delegated Task Capabilities
Another common error is assuming delegated tasks can handle interactive or complex iterative work. Delegated agents:
- Cannot use `clarify` to ask questions
- Cannot interact with the user during execution
- Have limited context beyond what's passed in the `context` parameter
- May appear unresponsive if the inherited model is unsuitable for the task

**Example from session:** When delegating the reconstruction of Part VII and Appendices, the task appeared stalled because the inherited model (Gemma 4) struggled with the complex HTML restructuring task within the delegation constraints. Direct agent action was more effective for this iterative, detail-oriented work.

### Overlooking Configuration Overrides
The delegation system allows overriding the inherited model via `delegation.provider` and `delegation.model` in the agent's `config.yaml`, but these must be set explicitly.
- Cannot use `clarify` to ask questions
- Cannot interact with the user during execution
- Have limited context beyond what's passed in the `context` parameter
- May appear unresponsive if the inherited model is unsuitable for the task

**Example from session:** When delegating the reconstruction of Part VII and Appendices, the task appeared stalled because the inherited model (Gemma 4) struggled with the complex HTML restructuring task within the delegation constraints. Direct agent action was more effective for this iterative, detail-oriented work.

### Misattributing Model Switches
When the parent agent's model changes (e.g., via `hermes config set model.name`), newly delegated tasks will inherit the new model, but already-running delegated tasks continue with the original model. Do not assume mid-delegation model changes affect active children.

## When to Avoid Delegation
Based on session experience, avoid delegation for:
- Tasks requiring iterative refinement or multiple feedback loops
- Complex HTML/DOM manipulation requiring precise visual adjustments
- Work needing frequent tool alternation (read_file → edit → verify → repeat)
- Any task where you need to see intermediate results to guide next steps

Use delegation instead for:
- Self-contained research tasks with clear endpoints
- Batch processing of similar items
- Background monitoring or data collection
- Tasks where a single pass-through is sufficient

## Best Practices

### 1. Explicitly Configure When Needed
If a delegated task requires a specific model, configure it in your agent's `config.yaml`:

```yaml
delegation:
  provider: ollama
  model: "nemotron-3-super-120b-a12b:free:latest"  # or whatever you need
```

### 2. Verify Model Usage
To confirm which model a delegated task is using:
- Check the agent's `config.yaml` for `delegation.*` settings
- Observe model-specific behavior (e.g., tool usage patterns, response styles)
- For Ollama models, monitor GPU usage via `nvidia-smi` if local

### 3. Prefer Direct Action for Interactive Tasks
Remember that delegated tasks:
- Cannot use `clarify` to ask questions
- Cannot interact with the user during execution
- Cannot access the parent's conversation context beyond what's passed in `context`
- Should be used for self-contained, non-interactive workloads

For tasks requiring iteration or user feedback, consider direct action instead of delegation.

### 4. Document Assumptions
When delegating, always document in your task description or notes which model you expect to be used, and verify it aligns with the inheritance or override configuration.

### Related Concepts

- **Wolf Protocol**: Wolf research workers (`fbox-wolf-spawn`) also inherit the parent's model unless otherwise configured. They are subject to the same inheritance rules.
- **Context Inheritance**: Beyond models, delegated agents inherit the parent's toolset, permissions, and working directory (unless overridden).

## Session-Specific Insights

During the Foreverbox site reconstruction session (July 2025), we observed that delegated complex HTML restructuring tasks appeared to stall when using inherited model configurations. Specifically:

- When attempting to rebuild Part VII (Build Manual) and Appendices via delegation with the inherited Gemma 4 model, progress seemed to halt after significant time investment
- Direct agent action (non-delegated) proved more effective for this iterative, detail-oriented work requiring frequent tool alternation (read_file → edit → verify → repeat)
- The delegated task wasn't making visible progress on the intricate requirements: adding hero sections, converting content to HUD panels with corner accents, preserving anchor IDs, and formatting code blocks with "COPY CODE" labels

This reinforced the principle that delegation is best suited for self-contained, well-defined tasks with clear endpoints, rather than iterative refinement work requiring ongoing visibility and adjustment.

## Example Configuration (Updated)

To delegate tasks using a specific Ollama model with a 32K context window:

```yaml
# In your agent's config.yaml
delegation:
  provider: ollama
  model: "qwen2.5-coder:7b-ctx"  # Custom model with 32K context
```

## Troubleshooting (Enhanced)

- **Symptom**: Delegated task appears stalled or makes no visible progress
  **Check**: Consider whether the task requires iterative refinement or frequent visibility of intermediate results
  **Action**: For complex, detail-oriented work, try direct action instead of delegation
- **Symptom**: Unexpected behavior in delegated task
  **Check**: Confirm no unintended model inheritance is occurring; verify the delegated model matches task complexity requirements
- **Symptom**: Performance differs from expectation
  **Check**: Ensure the delegated model matches performance assumptions (VRAM, context size, etc.) and that the task isn't better suited to direct interaction