# Wolf LLM Routing

Wolves are background task executors with model access via the CognitiveRouter. No SOUL.md, no Hermes profiles, no conversation loop. Three per Lead agent.

## Model Tiers

```yaml
wolf_overrides:
  layer_1_intuitive_reflex:
    model: "google/gemini-3.1-flash-lite"
  layer_2_analytical_engine:
    model: "deepseek/deepseek-v4-flash"
  layer_3_deep_architect:
    model: "deepseek/deepseek-v4-flash"  # capped at Layer 2
```

Wolves never touch deepseek-v4-pro. Layer 3 is intentionally the same as Layer 2 — a safety cap.

## Task Load Estimation

The `estimate_task_load()` function scores incoming tasks:

| Signal | Weight |
|--------|--------|
| Action is research/audit/analyse | +0.50 |
| Action is synthesise | +0.25 (cumulative) |
| Payload > 2,000 chars | +0.20 |
| Payload has deep_reasoning flag | +0.30 |

The score is capped at 1.0 and routed through thresholds: ≥0.00 → Layer 1, ≥0.40 → Layer 2.

## Execution Flow

1. Wolf polls `agent_registry.task_queue` with `SELECT ... FOR UPDATE SKIP LOCKED`
2. Atomic claim: `UPDATE ... SET status='claimed' WHERE status='queued' LIMIT 1`
3. `execute_with_llm()` scores the task, calls `router.wolf_select_model(load)`
4. Builds system prompt ("You are {wolf_id}, a Wolf background worker...") + user message from payload
5. Calls `https://openrouter.ai/api/v1/chat/completions` with the selected model
6. Writes result to `memory_lore` under namespace `wolf_tasks`, key `{task_id}:{wolf_id}`
7. Updates task_queue to `completed` with result_json

## Memory Namespacing

- namespace: `wolf_tasks`
- key_name: `{task_id}:{wolf_id}` (e.g., `a1b2c3d4e5f6:wolf_1`)
- source_type: `wolf_synthesis`
- tags: `["wolf", "task:{task_id}"]`

Once all Wolves sharing a directive_id complete, the Lead performs a single consolidation write to `{task_id}:final`. Only the final key is read by `prefetch()`.

## Systemd Configuration

```
EnvironmentFile=/foreverbox_data/council-library/.env.production
```

The env file must contain:

```
OPENROUTER_API_KEY=***
DB_PASS="***"
```

Never put `OPENROUTER_API_KEY` directly in the systemd unit — `#` in values is a comment delimiter.

## Dispatch (from an agent)

Use the `wolf_dispatch` tool:

```json
{
  "wolf_id": "wolf_1",
  "action": "research",
  "payload": {"query": "audit all SQL schemas for inconsistencies"},
  "priority": "normal"
}
```

Plugin route: `POST /sanctum/wolves/{wolf_id}/task` → `WolfController::dispatch()` → inserts into `task_queue`.

## Pitfalls

- Wolves have no `OPENROUTER_API_KEY` by default — must be added to `.env.production`
- Systemd `Environment=` truncates at `#` — always use `EnvironmentFile=`
- Wolves cap at Layer 2 (v4-flash) — never v4-pro
- Task load estimation is heuristic — tune weights based on actual task patterns
- `mysql.connector` needs `use USE agent_{slug}` before Sanctum writes
- Wolf writes use `ON DUPLICATE KEY UPDATE` — safe to re-run
