# Cognitive Router Hook Integration — Hermes Profiles

## Philosophy

Rather than patching Hermes core (`conversation_loop.py`, `run_agent.py`), the Cognitive Router integrates as a **Hermes profile hook**. This keeps the router decoupled from Hermes internals and makes it installable per-profile.

## Architecture

```
Profile hooks/ directory
    └── cognitive_router.py
            ├── on_turn_start()  → overrides agent.model/provider
            └── on_turn_end()    → restores originals

Router module (council-library/router/)
    └── __init__.py        → CognitiveRouter class
    └── router.yaml        → model profiles, thresholds
    └── hook.py            → Hermes hook implementations
```

## Hook Lifecycle

```
User sends message
    │
    ▼
on_turn_start(agent, messages, enabled_toolsets)
    │
    ├── scan_for_private_data(messages)
    │   └── privacy gate: force Layer 1 or hard-stop
    │
    ├── AgentRequestContext(complexity, tokens, task_type)
    │
    ├── router.select_model(ctx)
    │   ├── estimate_load()
    │   ├── health check (30s cache)
    │   ├── budget gate (token_budget_ledger)
    │   └── return ModelProfile
    │
    ├── agent.model = profile.model       # temporary override
    ├── agent.provider = profile.provider
    └── agent.base_url = profile.base_url

[LLM call happens with overridden model]

on_turn_end(agent)
    └── restore agent.model/provider/base_url to originals
```

## Installation

```bash
cp council-library/router/hook.py profiles/<name>/hooks/cognitive_router.py
cp council-library/router/router.yaml profiles/<name>/router.yaml
```

**The hook auto-loads on next profile start** — but only if Hermes supports `pre_turn`/`post_turn` hook dispatch.

### CRITICAL: Hermes Version Requirement

**Hermes v0.18.2 does NOT support `pre_turn`/`post_turn` hooks.** Confirmed 2026-07-15: `grep -rn "pre_turn\|post_turn\|on_turn_start\|on_turn_end" /hermes/run_agent.py` returns zero hits. The hooks declared in `config.yaml` are dead config — the cognitive router never fires.

**Three fix paths:**

1. **Quick fix (no routing):** Fix the default model in `config.yaml` to use correct provider/URL. The SOUL.md will load. No dynamic tier routing.
   ```yaml
   model:
     default: Zeon7-Gemma:latest
     provider: ollama
     base_url: http://localhost:11434/v1
   ```

2. **Update Hermes:** Run `hermes update` (currently 562 commits behind). Later versions may have hook dispatch built in.

3. **Manual wiring:** Patch `run_agent.py` to call the cognitive router before each LLM API call. This is Stage 4 of the Council Library blueprint — the only remaining incomplete stage.

To verify whether your Hermes version supports hooks:
```bash
grep -rn "pre_turn\|post_turn" /hermes/run_agent.py /hermes/agent/
# If zero hits → hooks are not supported → paths 1, 2, or 3 above
```

## Model Profiles

| Tier | Model | Where |
|------|-------|-------|
| System1 Local | gemma4:31b | Ollama, free |
| System2 Light | qwen3-32b | OpenRouter, free tier |
| System2 Heavy | deepseek-v4-pro | OpenRouter, paid |

## Pitfalls

- **Hermes version**: v0.18.2 has no hook dispatch. Verify with grep before assuming hooks work.
- **Provider/URL mismatch is a silent system-prompt killer**: If `provider: openrouter` but `base_url: http://localhost:11434/v1`, the API call construction uses the wrong format. The system prompt may be silently dropped. Always ensure provider and base_url are consistent.
- **Python version**: Hook imports `requests` — must run under `/usr/bin/python3.12` (Homebrew 3.14 lacks it).
- **Budget check**: Calls `GET /v1/registry/budget` — endpoint must exist.
- **Health check**: Pings each tier. Unreachable tiers are skipped, not failed.
- **Reasoning models + low max_tokens**: Models like `Zeon7-Gemma:latest` use tokens for internal reasoning. With `max_tokens < 500`, the model exhausts its budget on thinking and produces empty output. Always set `max_tokens >= 500` for reasoning-capable local models.
