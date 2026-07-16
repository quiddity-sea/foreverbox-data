# Wolf Model Routing — Resolved

BluePrint §7: "Wolves are not conversational models, do not have Hermes profiles, and never speak to humans."

## Resolution (2026-07-14)

Wolves now have their own three-tier model routing via the CognitiveRouter's `wolf_select_model()` method. All Wolves share the same tiers — they are task executors with no individual personality.

| Tier | Model | Use |
|------|-------|-----|
| Layer 1 Intuitive Reflex | `google/gemini-3.1-flash-lite` | Status checks, file reads, metadata extraction, tool calls |
| Layer 2 Analytical Engine | `deepseek/deepseek-v4-flash` | Research, searching, summarising, auditing |
| Layer 3 Deep Architect | `deepseek/deepseek-v4-pro` | Synthesis, cross-document correlation, long-form reports |

All cloud via OpenRouter — no GPU contention with Zeon7/Gemma on the single 8 GB RTX 4060.

## Configuration

In `router/router.yaml`:

```yaml
wolf_overrides:
  layer_1_intuitive_reflex:
    model: "google/gemini-3.1-flash-lite"
  layer_2_analytical_engine:
    model: "deepseek/deepseek-v4-flash"
  layer_3_deep_architect:
    model: "deepseek/deepseek-v4-pro"
```

The `CognitiveRouter.wolf_select_model(load: float)` method accepts a cognitive load score and returns the appropriate ModelProfile from wolf_overrides, falling through the main model_profiles as defaults.

## Pitfall

`wolf_select_model()` and `select_model()` both check health on each tier. Without real API keys configured, all cloud tiers fail health checks and only Layer 1 (local/Ollama) returns — exactly what you'd see in test environments. In production with valid OpenRouter keys, the health checks pass and routing works as expected.
