# Ollama Model Context Rebuild

When an Ollama model's `num_ctx` needs increasing (Hermes minimums change, larger system prompts, tool-use requirements), rebuild the model with a new tag rather than relying on runtime config overrides. Runtime overrides are fragile — they can silently revert if the Hermes config key is dropped or if the model is reloaded without the override.

## Procedure

### 1. Export the existing modelfile

```bash
ollama show <model>:<tag> --modelfile > /tmp/<model>-<new_ctx>.modelfile
```

### 2. Edit `PARAMETER num_ctx`

Change the value to the new context size. Hermes currently requires **65,536** minimum for tool use.

```
PARAMETER num_ctx 65536
```

### 3. Create the new model tag

```bash
ollama create <model>:<new_tag> -f /tmp/<model>-<new_ctx>.modelfile
```

This reuses the existing model layers (no re-download) and only creates a new manifest.

### 4. Verify

```bash
ollama show <model>:<new_tag> | grep num_ctx
# Must show: num_ctx   65536
```

### 5. Update Hermes profile config

```bash
hermes config set model.default <model>:<new_tag> --profile <profile>
hermes config set model.ollama_num_ctx 65536 --profile <profile>
hermes config set model.context_length 65536 --profile <profile>
```

### 6. Restart the gateway

```bash
hermes gateway restart --profile <profile>
```

## Worked Example: Zeon7-Gemma 32k → 64k

**Context:** Hermes introduced a 64,000-token minimum for tool use. `Zeon7-Gemma:32k` had `num_ctx=32768`, causing Hermes to refuse initialisation with:

```
Ollama runtime context is too small for Hermes tool use
Ollama loaded Zeon7-Gemma:32k with only 32,768 tokens of runtime context,
but Hermes needs at least 64,000 tokens for reliable tool use.
```

**Fix (2026-07-15):**

```bash
# Export
ollama show Zeon7-Gemma:32k --modelfile > /tmp/Zeon7-Gemma-64k.modelfile

# Edit: PARAMETER num_ctx 32768 → 65536

# Create
ollama create Zeon7-Gemma:64k -f /tmp/Zeon7-Gemma-64k.modelfile

# Verify
ollama show Zeon7-Gemma:64k | grep num_ctx
# → num_ctx   65536

# Config
hermes config set model.default Zeon7-Gemma:64k --profile zeon7
hermes config set model.ollama_num_ctx 65536 --profile zeon7
hermes config set model.context_length 65536 --profile zeon7

# Restart
hermes gateway restart --profile zeon7
```

## VRAM Budget

At Q4_K_M quantisation, 4.8B parameters, the VRAM footprint scales as:

| Context | KV Cache | Model | Total | Fits 8GB? |
|---------|----------|-------|-------|-----------|
| 16k | ~150 MiB | ~4.1 GiB | ~4.25 GiB | Yes |
| 32k | ~576 MiB | ~4.1 GiB | ~4.75 GiB | Yes |
| 64k | ~1.15 GiB | ~4.1 GiB | ~5.25 GiB | Yes |
| 128k | ~2.3 GiB | ~4.1 GiB | ~6.4 GiB | Tight (output adds more) |

64k is safe on 8GB VRAM. 128k is possible but leaves little headroom for generated output tokens.

## Why Not Just `hermes config set model.ollama_num_ctx`?

Setting only the Hermes config key is a *runtime override* — it works but:

- Doesn't survive a config reset or profile migration
- The Ollama model metadata still reports the old `num_ctx`
- If the config key is accidentally dropped, the model silently reverts

Rebuilding the model with the new `num_ctx` parameter makes the change **persistent at the model level**. The Hermes config keys then serve as a belt-and-suspenders confirmation rather than the sole source of truth.

**User preference (2026-07-15):** Always rebuild the Ollama model with a new tag rather than relying solely on Hermes runtime overrides. Present both options in troubleshooting but execute the rebuild path.
