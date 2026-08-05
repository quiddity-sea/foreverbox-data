---
name: delegation-best-practices
description: Best practices for using delegate_task in Hermes Agent, including model inheritance and task suitability
version: 1.0.0
---
# Delegation Best Practices

## Overview
This skill documents effective patterns for using the `delegate_task` tool in Hermes Agent, based on session experience. It covers model inheritance, task suitability, and when to prefer direct action over delegation.

## Trigger Conditions
Apply this knowledge when:
- Considering using `delegate_task` to spawn subagents
- Deciding whether a task should be delegated or performed directly
- Observing unexpected behavior in delegated tasks
- Needing to override default model inheritance for delegated work

## Core Principles

### Model Inheritance
By default, delegated child agents inherit the parent agent's complete model configuration:
- Provider (ollama, openrouter, etc.)
- Model name (gemma4:31b, nemotron-3-super-120b-a12b:free, etc.)
- Context settings and fallback chains

**Critical Insight**: Unless explicitly overridden via `delegation.provider` and `delegation.model` in config.yaml, delegated tasks use the **exact same model** as the parent agent. This applies to all delegation types, including wolf research workers (`fbox-wolf-spawn`).

### Delegation Limitations
Delegated agents have significant constraints:
- ❌ Cannot use `clarify` to ask questions
- ❌ Cannot interact with the user during execution
- ❌ Cannot access conversation history beyond the `context` parameter
- ❌ Cannot iterate based on intermediate results
- ❌ Cannot show work-in-progress for feedback
- ✅ Best for: Self-contained, batch-oriented, non-interactive tasks

## When to Use Delegation

### Ideal Use Cases
1. **Research tasks**: "Find all instances of X in documentation"
2. **Data transformation**: "Convert CSV format Y to JSON format Z"
3. **Verification scripts**: "Check that all files meet criteria A, B, C"
4. **Background monitoring**: "Watch for changes in directory D"
5. **Simple report generation**: "Summarize the contents of file F"

### Poor Use Cases (Prefer Direct Action)
1. **Iterative design work**: "Refactor this HTML to match a visual mockup"
2. **Troubleshooting**: "Why isn't this feature working?"
3. **Creative writing with feedback**: "Write a paragraph, then improve it based on my notes"
4. **UI/UX adjustments**: "Make this button more prominent"
5. **Any task requiring you to see intermediate results**

**Session Example**: Attempting to delegate the reconstruction of Part VII (Build Manual) and Appendices appeared to stall because:
- The task required iterative HTML refinement
- Needed frequent visual checks against design specifications
- Involved alternating between reading source files, editing structure, and verifying output
- Better suited to direct agent action where I could see progress and adjust in real-time

## Best Practices

### 1. Match Task Type to Delegation Suitability
Before delegating, ask:
- "Does this require user feedback at any point?"
- "Do I need to see intermediate results to decide next steps?"
- "Is this a single-pass transformation or an iterative process?"
If yes to any of the first two, consider direct action.

### 2. Explicitly Configure Model When Needed
To override inherited model in `config.yaml`:
```yaml
delegation:
  provider: ollama  # or openrouter, etc.
  model: "your-specific-model:tag"  # e.g., "nemotron-3-super-120b-a12b:free"
```

### 3. Set Clear, Self-Contained Goals
Delegated tasks should have:
- A definitive completion criterion
- No need for mid-task adjustments
- Clear success/failure conditions
- Example ❌: "Make the website look better"
  Example ✅: "Convert all markdown files in /docs to HTML with frontmatter"

### 4. Provide Complete Context
Since delegated agents can't ask follow-up questions:
- Include all necessary files, paths, and references in `context`
- Specify exact expected outputs
- Define any constraints or requirements upfront
- Example: "Use only the files in /source/images, ignore subdirectories"

### 5. Verify Before Trusting
After delegation completes:
- Check outputs against requirements
- Verify no assumptions were made about available tools/data
- Confirm the inherited model was appropriate for the task
- Consider doing a spot-check with direct action for complex tasks

## Configuration Examples

### Default Inheritance (Most Common)
```yaml
# No delegation section needed - uses parent's model
```
Delegated tasks will use whatever model the parent is currently using.

### Explicit Override
```yaml
delegation:
  provider: openrouter
  model: "google/gemini-pro-1.5"
```
All delegated tasks will use this model regardless of parent's current model.

### Model-Specific Delegation Profiles
For different types of work:
```yaml
delegation:
  research:
    provider: ollama
    model: "mistral-small:22b"
  coding:
    provider: ollama
    model: "qwen2.5-coder:32b"
  # Note: This requires custom implementation - standard delegation uses a single profile
```

## Troubleshooting Guide

### Symptom: Delegated task appears inactive or stalled
**Check**: Is the task requiring iteration or user feedback?
**Action**: For design/troubleshooting work, switch to direct action.

### Symptom: Unexpected errors about missing tools/features
**Check**: Does the inherited model support the required tools?
**Action**: Either select a model with those capabilities or use direct action.

### Symptom: Output doesn't match expectations despite clear prompt
**Check**: Was sufficient context provided? Did the model have necessary capabilities?
**Action**: Enhance context package or consider direct action for nuanced work.

### Symptom: Performance much slower than expected
**Check**: Verify the delegated model matches performance assumptions (VRAM, context size, speed).
**Action**: Adjust model selection or use direct action for time-sensitive work.

## Related Skills
- `hermes-agent`: Core agent configuration and tool usage
- `autonomous-ai-agents`: General principles of agent delegation
- `wolf-protocol`: Specifics about wolf research workers (which also follow inheritance rules)

## Key Takeaway
Delegation excels at offloading well-defined, independent tasks but is poorly suited for work requiring creativity, iteration, or user collaboration. Always evaluate task characteristics before choosing between delegation and direct action.