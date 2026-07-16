# Per-Agent Cognitive Router Model Overrides

The Cognitive Router supports per-agent model overrides — each Lead can have different models for each tier. Wolves have their own tiers via `wolf_overrides`.

## Final Configuration (2026-07-15)

All model names verified against the live OpenRouter API. Free tier variants use the `:free` suffix. `Zeon7-Gemma:16k` was created on 2026-07-15 to fix Ollama VRAM-aware context truncation (num_ctx=16384, KV cache ~150 MiB).

```yaml
agent_overrides:
  curator:
    layer_1_intuitive_reflex:
      model: "Zeon7-Gemma:16k"
    layer_2_analytical_engine:
      model: "deepseek/deepseek-v4-flash"
  producer:
    layer_1_intuitive_reflex:
      model: "deepseek/deepseek-v4-flash"
    layer_2_analytical_engine:
      model: "qwen/qwen3-coder:free"
  coach:
    layer_1_intuitive_reflex:
      model: "Zeon7-Gemma:16k"
    layer_2_analytical_engine:
      model: "deepseek/deepseek-v4-flash"
  director:
    layer_1_intuitive_reflex:
      model: "deepseek/deepseek-v4-flash"
    layer_2_analytical_engine:
      model: "nvidia/nemotron-3-super-120b-a12b:free"

wolf_overrides:
  layer_1_intuitive_reflex:
    model: "google/gemini-3.1-flash-lite"
  layer_2_analytical_engine:
    model: "deepseek/deepseek-v4-flash"
  layer_3_deep_architect:
    model: "deepseek/deepseek-v4-pro"
```

## Full Table

| Agent | Layer 1 — Intuitive Reflex | Layer 2 — Analytical Engine | Layer 3 — Deep Architect |
|-------|------------------------------|-----------------------------|--------------------------|
| **Curator** (Zeon7) | `Zeon7-Gemma:16k` (Ollama) | `deepseek/deepseek-v4-flash` | `deepseek/deepseek-v4-pro` |
| **Producer** (Leon) | `deepseek/deepseek-v4-flash` | `qwen/qwen3-coder:free` | `deepseek/deepseek-v4-pro` |
| **Coach** (Gemma) | `Zeon7-Gemma:16k` (Ollama) | `deepseek/deepseek-v4-flash` | `deepseek/deepseek-v4-pro` |
| **Director** (Otec) | `deepseek/deepseek-v4-flash` | `nemotron-3-super-120b-a12b:free` | `deepseek/deepseek-v4-pro` |
| **Wolves** (all, 3 per Lead) | `gemini-3.1-flash-lite` | `deepseek/deepseek-v4-flash` | `deepseek/deepseek-v4-pro` |

## Design Rationale

- **Layer 1 split**: Zeon7 and Gemma share `Zeon7-Gemma:16k` (4.1 GiB, `num_ctx=16384`, fits single 8 GB RTX 4060 — never concurrent per Worzel Gummidge). The `:16k` tag was necessary because the original `:latest` tag auto-sizes to `KvSize=4096` on 8GB hardware (Ollama VRAM-aware default), which silently truncated the ~5,200-token Hermes system prompt, dropping the SOUL.md from the front of the context window. Leon/Otec use cloud `deepseek-v4-flash` for always-available responses. Wolves get `gemini-3.1-flash-lite` (cheapest/fastest) for mechanical task execution. Leon/Otec use cloud `deepseek-v4-flash` for always-available responses. Wolves get `gemini-3.1-flash-lite` (cheapest/fastest) for mechanical task execution.
- **Layer 2 per-agent**: Leon gets coding-optimised (`qwen3-coder:free`), Otec gets planning specialist (`nemotron-3-super:free`), Zeon7/Gemma use `deepseek-v4-flash` for fast reasoning.
- **Layer 3 uniform**: All agents and Wolves use `deepseek/deepseek-v4-pro` — most capable reasoning model.

## Tier Naming

Canonical names from Blueprint §5 — "The Three Layers of Thought":
- **Layer 1: Intuitive Reflex** (`layer_1_intuitive_reflex`)
- **Layer 2: Analytical Engine** (`layer_2_analytical_engine`)
- **Layer 3: Deep Architect** (`layer_3_deep_architect`)

## Pitfalls

- Always verify OpenRouter model names against live API before writing config. Never guess — `deepseek-v4-fast` doesn't exist (real: `deepseek-v4-flash`), `nemotron-super` doesn't exist (real: `nemotron-3-super-120b-a12b:free`).
- Free tier variants always end with `:free`.
- Wolves use `wolf_overrides` (separate config key), not `agent_overrides` — they share one profile for all Wolves.
