# Wolf Upgrade Blueprint V2 — Summary

**Full specification:** `/foreverbox_data/council-library/docs/WOLF_UPGRADE_BLUEPRINT_V2.md`

## Architecture

Wolves are full Hermes agents — one `wolf` profile, spawned as independent processes by Lead agents. Not lightweight LLM prompts, not stripped subagents.

- **Model:** `qwen2.5:3b` (~2 GB, Ollama local)
- **Profile:** `wolf` (SOUL.md, skills, memory provider, tools)
- **Tools:** web search, file access, terminal, memory provider
- **Parallelism:** Up to 3 concurrent wolf processes, one Ollama model load
- **VRAM:** ~2.9 GB total (model + 3 × 16K KV caches)

## Layer Gate

- **Layer 1 agents (local model):** Wolves BLOCKED — GPU occupied
- **Layer 2/3 agents (cloud model):** Wolves AVAILABLE — GPU free

## Spawn Pattern

Agent on Layer 2+ spawns via `terminal(background=True)`:

```bash
hermes chat --profile wolf -q "Task: research. Query: [query]. Target: [agent_slug]. Task ID: [unique_id]. Write results to Sanctum." --source wolf
```

## Results Flow

1. Agent spawns wolves (background)
2. Agent continues own work on cloud model
3. Wolves search → read → synthesise → write to Sanctum → exit
4. Agent retrieves: `memory_search(query="wolf_tasks [task_id]")`

## Build Stages (6)

1. Pull model: `ollama pull qwen2.5:3b`
2. Create profile: `hermes profile create wolf --clone-from zeon7` + SOUL.md + config + skills
3. Create Sanctum: `agent_wolf` database
4. Upgrade `wolf_dispatch` tool handler
5. Verify (12 acceptance criteria)
6. **GATED:** Apply Wolf Protocol to Lead agent SOUL.md files

## Legacy

Original lightweight wolves (`wolf_worker.py`, `council-wolves.service`) remain for simple reasoning tasks. New wolf profile is additive.
