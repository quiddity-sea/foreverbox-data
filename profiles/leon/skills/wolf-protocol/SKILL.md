---
name: wolf-protocol
description: Complete Wolf Protocol knowledge — Layer 1 Guard resource management, ad-hoc spawning lifecycle, task queue dispatch, and result retrieval. Aggregates the fbox-wolf-spawn skill's provider gate rationale with the broader wolf ecosystem context.
---

# Skill: Wolf Protocol

## Purpose

Governs all wolf-related operations: spawning, resource management, task lifecycle, and result retrieval. Wolves are background Hermes research workers that share a single Ollama model load.

## Layer 1 Guard — Resource Management Gate

This is a **resource management** gate, not a security feature. The intent is to conserve the 8 GB GPU for the agent's own 64K context window.

### Why it exists
- The 8 GB GPU runs Zeon7-Gemma:64k at ~3.8 GB model + ~3.6 GB KV cache
- 3 concurrent wolves at 64K each add ~3.6 GB more
- Agent + wolves side by side exceeds 8 GB → OOM or severe throttling
- Cloud models use the provider's GPU, not the local one, so they can orchestrate wolves freely

### Rules
- **Cloud agent (openrouter, anthropic, deepseek, etc.)**: Wolves allowed. GPU is free.
- **Local agent (provider: ollama)**: Wolves blocked by default. Report the reason: "GPU occupied by my local model. Switch me to Layer 2 or 3 to spawn wolves, or explicitly instruct me to proceed."
- **Merrill override**: Can authorise a local agent to spawn wolves. This degrades both sides — warn Merrill before proceeding.

## Spawning Lifecycle

1. **Load `fbox-wolf-spawn` skill** — handles provider checking, task ID construction, and background dispatch
2. **Determine parameters** — how many wolves (1-3), task IDs with agent prefix, research queries
3. **Construct spawn command** — uses `hermes chat --profile wolf` with `terminal()` wrapper syntax
4. **Spawn via `terminal(background=True)`** — each wolf runs independently
5. **Report task IDs** — so Merrill can retrieve results

## Task Queue Dispatch

Tasks are dispatched via `POST /v1/sanctum/wolves/{wid}/task` and flow:
```
queued → claimed (SKIP LOCKED) → processing → completed
                                                └→ failed → dead_letter (3 retries max)
```

## Retrieving Results

```bash
terminal("/foreverbox_data/bin/fbox-memory-get wolf_tasks {task_id}:done")
terminal("/foreverbox_data/bin/fbox-memory-get wolf_tasks {task_id}")
terminal("/foreverbox_data/bin/fbox-memory-list wolf_tasks")
terminal("/foreverbox_data/bin/fbox-memory-search \"{topic}\" wolf_tasks")
```

## Pitfalls

- Wolves use `terminal()` with shell scripts, NOT native tools. The spawn prompt must tell them to use `terminal("/foreverbox_data/bin/fbox-memory-upsert ...")`.
- 3 concurrent wolves + agent on 8 GB GPU is tight (~7.4 GB for wolves alone). Reduce wolves or context if OOM occurs.
- Wolves are stateless — no conversation history between invocations.
