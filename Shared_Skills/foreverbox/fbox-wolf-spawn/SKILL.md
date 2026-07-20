---
name: fbox-wolf-spawn
description: Spawns 1-3 Wolf research workers via the Hermes CLI. Handles provider checking (cloud required unless Merrill overrides), task ID generation, command construction, and background dispatch. Load this skill when spawning wolves.
---

# Skill: fbox-wolf-spawn

## Purpose

Spawns Wolf research workers as background Hermes processes. Wolves run on the local GPU (`Zeon7-Gemma:64k` via Ollama) and write their findings to the `agent_wolf` Sanctum. The spawning agent continues working while wolves research in parallel.

## When to Use

- Complex multi-source research (3+ sources needed)
- Parallel searches on different topics
- Background research while the agent drafts, writes, codes, or plans
- Any task better suited to a dedicated research worker

## Step 1: Provider Gate

Check what model you are running on:

- **Cloud model (openrouter, anthropic, deepseek, etc.)**: Proceed to Step 2. The GPU is free for wolves.
- **Local model (provider: ollama)**: Wolves are BLOCKED by default. Report: "Wolves unavailable — GPU occupied by my local model. Switch me to Layer 2 or 3 to spawn wolves, or explicitly instruct me to proceed."
  - **Exception**: If Merrill has explicitly instructed you to spawn wolves despite being on a local model, you may proceed. This is rare and will degrade both your context and the wolves' performance.

## Step 2: Determine Wolf Parameters

Decide how many wolves to spawn (1-3), and for each wolf:

- `task_id`: Unique identifier, prefixed by agent. Use format `{agent_prefix}_{descriptive_slug}`.
  - zeon7: `z7_` / leon: `ln_` / gemma: `gm_` / otec: `ot_`
- `research_question`: The specific research query for this wolf.
- Example: `ln_audit_sql` or `z7_leads_20260720`

## Step 3: Construct the Spawn Command

For each wolf, use the following command format via `terminal(background=True)`:

```
hermes chat --profile wolf -q "Research task. Task ID: {task_id}. {research_question}. Write findings to Sanctum via terminal: /foreverbox_data/bin/fbox-memory-upsert wolf_tasks {task_id} \"{findings}\". Then signal completion via terminal: /foreverbox_data/bin/fbox-memory-upsert wolf_tasks {task_id}:done \"{\"status\": \"completed\"}\"." -m Zeon7-Gemma:64k --provider ollama --source wolf
```

## Step 4: Spawn Wolves

Use `terminal(background=True)` for each wolf. They run independently. You can continue working immediately.

```
terminal(command="hermes chat --profile wolf -q '...task A...' -m Zeon7-Gemma:64k --provider ollama --source wolf", background=True)
terminal(command="hermes chat --profile wolf -q '...task B...' -m Zeon7-Gemma:64k --provider ollama --source wolf", background=True)
terminal(command="hermes chat --profile wolf -q '...task C...' -m Zeon7-Gemma:64k --provider ollama --source wolf", background=True)
```

Up to 3 wolves can run concurrently. All share one Ollama model load.

## Step 5: Report Task IDs

After spawning, tell Merrill which wolves are running and how to retrieve results:

"For each wolf, check completion:
terminal(\"/foreverbox_data/bin/fbox-memory-get wolf_tasks {task_id}:done\")
Read findings:
terminal(\"/foreverbox_data/bin/fbox-memory-get wolf_tasks {task_id}\")
Browse all:
terminal(\"/foreverbox_data/bin/fbox-memory-list wolf_tasks\")"

## Pitfalls

- The Wolf SOUL.md instructs wolves to use `terminal()` with shell scripts at `/foreverbox_data/bin/`, NOT to call fbox-memory-upsert as a native tool. The spawn command must include the full `terminal()` syntax in the wolf's task prompt so the wolf knows to use the shell wrapper.
- 3 concurrent wolves at 64K context on an 8 GB GPU is tight (~7.4 GB). If wolves fail to spawn, reduce context or run fewer wolves.
- Wolves are stateless. Do not rely on conversation history being carried over between wolf invocations.
