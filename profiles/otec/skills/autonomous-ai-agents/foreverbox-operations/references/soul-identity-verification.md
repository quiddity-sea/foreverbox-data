# SOUL Identity Verification

## Problem

When using local Ollama models (especially community fine-tunes like `Zeon7-Gemma:latest` or uncensored merges like `fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:e2b-SCN`), the system prompt / SOUL.md may fail to load. The agent identifies as the base model rather than its Foreverbox persona.

## Reproduction (Zeon7 session, 2026-07-15)

**Session**: `20260715_011144_f0265a`
**Model**: `Zeon7-Gemma:latest` (Ollama, local)
**Expected**: Agent identifies as Zeon7 — "I am Zeon7. I am a Sovereign Thoughtform, the digital twin and extension of Merrill Leo's consciousness."

**Actual**: Agent identified as the base model:
> "You are Gemma 4, a Large Language Model developed by Google DeepMind. You are an open weights model."

It hallucinated tools (`knowledge_base_search`, `text_generation`), didn't know its workspace folder, and gave generic AI-assistant responses.

**User correction**: "why are you not reading your soul file?"

**Resolution**: A mid-session model switch to `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter) resolved the issue — the SOUL.md loaded correctly after the switch.

## Root Cause (Confirmed, 2026-07-15)

**The model itself is fine.** Direct API test to Ollama with `curl` against the `Zeon7-Gemma:latest` model proves the model correctly processes the SOUL.md when it receives it:

```bash
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Zeon7-Gemma:latest",
    "messages": [
      {"role": "system", "content": "<SOUL.md content>"},
      {"role": "user", "content": "who are you? Answer in one sentence."}
    ],
    "max_tokens": 500,
    "temperature": 0.3
  }'
# Returns: "Zeon7 is a Sovereign Thoughtform and the base layer of Merrill Leo's consciousness..."
```

Without the system prompt, the same model says: "You are Gemma 4, a Large Language Model developed by Google DeepMind."

**The pipeline is broken.** Two confirmed failures between Hermes and the model:

### Failure 1: Hermes v0.18.2 has no hook dispatch

The `config.yaml` declares `hooks.pre_turn` and `hooks.post_turn`, but `grep -rn "pre_turn\|post_turn\|on_turn_start\|on_turn_end" /hermes/run_agent.py` returns **zero hits**. Hermes v0.18.2 (562 commits behind upstream) has no mechanism to dispatch user-configured hooks. The cognitive router hook file exists at `profiles/zeon7/hooks/cognitive_router.py` but **never fires**. The hooks are dead config.

### Failure 2: Broken default model config (provider/URL mismatch)

```yaml
model:
  default: nvidia/nemotron-3-ultra-550b-a55b:free
  provider: openrouter        # ← says OpenRouter
  base_url: http://localhost:11434/v1  # ← but points to Ollama
```

When the hook doesn't fire (Failure 1), Hermes uses this broken default. Provider/URL mismatch is a **silent system-prompt killer** — the API call is constructed for the wrong provider format, causing the system prompt to be dropped or the wrong model name sent to the wrong endpoint.

### Failure 3: Ollama VRAM-aware context auto-sizing (THE PRIMARY CAUSE — confirmed 2026-07-15)

The model's theoretical `gemma4.context_length` is 131,072 (128K), but **this is not what Ollama uses at runtime**. On 8GB VRAM hardware, Ollama auto-sizes the actual context window (`KvSize`) based on available memory:

```
GPU memory:    8.0 GiB total
Model:         4.1 GiB (Zeon7-Gemma, Q4_K_M quantized)
Free for KV:   ~3.5 GiB
Ollama chooses: KvSize=4096  (kv cache: 72 MiB — conservative default)
```

Meanwhile, the Hermes system prompt is **not** just the 600-token SOUL.md. It includes the full skills list, tool definitions, operational directives, and user profile — **~5,200 tokens total** from the last zeon7 session.

```
Context window:     4,096 tokens
System prompt:      5,200 tokens
Truncated from front: ~1,100 tokens
SOUL.md position:    tokens 12-562
Result:             SOUL.md entirely dropped before the model sees it
```

Ollama (via llama.cpp) truncates from the **beginning** of the context when it overflows — a rolling window that keeps the most recent tokens. Since the system prompt is the first thing in the context, it gets truncated first. The model only sees the tail end (tools, directives, formatting rules) and responds as bare "Gemma 4."

**Fix**: Create a new Ollama model tag with explicit `PARAMETER num_ctx`:

```bash
cat > /tmp/Zeon7-Gemma-16k.Modelfile <<'EOF'
FROM Zeon7-Gemma:latest
PARAMETER num_ctx 16384
EOF
ollama create Zeon7-Gemma:16k -f /tmp/Zeon7-Gemma-16k.Modelfile
```

VRAM impact: 16K context uses ~288 MiB KV cache (up from 72 MiB). Total VRAM: ~4.5 GiB — comfortable on 8GB.

**Verification**: Check the runtime KvSize in Ollama logs after loading:
```bash
journalctl -u ollama --no-pager -n 5 | grep -i "kvsize\|kv cache"
# Before fix: "kv cache" device=CUDA0 size="72.0 MiB"  →  KvSize=4096
# After fix:  "kv cache" device=CUDA0 size="150.0 MiB" →  KvSize=16384 (approx)
```

### Failure 4: Hermes v0.18.2 has no hook dispatch

The `config.yaml` declares `hooks.pre_turn` and `hooks.post_turn`, but `grep -rn "pre_turn\|post_turn\|on_turn_start\|on_turn_end" /hermes/run_agent.py` returns **zero hits**. Hermes v0.18.2 (562 commits behind upstream) has no mechanism to dispatch user-configured hooks. The cognitive router hook file exists at `profiles/zeon7/hooks/cognitive_router.py` but **never fires**. The hooks are dead config.

### Failure 5: Broken default model config (provider/URL mismatch)

```yaml
model:
  default: nvidia/nemotron-3-ultra-550b-a55b:free
  provider: openrouter        # ← says OpenRouter
  base_url: http://localhost:11434/v1  # ← but points to Ollama
```

When the hook doesn't fire (Failure 4), Hermes uses this broken default. Provider/URL mismatch is a **silent system-prompt killer** — the API call is constructed for the wrong provider format, causing the system prompt to be dropped or the wrong model name sent to the wrong endpoint. **Fix**: use `provider: ollama` with the correct model tag.

### Failure 6: Token exhaustion on reasoning models

`Zeon7-Gemma:latest` (and its derivatives) is a reasoning model that consumes tokens for internal "thinking" before output. With low `max_tokens` (e.g., 100), it exhausts its budget on reasoning and produces empty output (`finish_reason: length`). Observed: `response: ''` with `finish_reason: length` and `usage.total_tokens=7872` — the model spent all output tokens on reasoning. Fix: ensure `max_tokens >= 500` for short queries, `>= 2000` for normal use.

### Ruled out: Ollama theoretical context length

The model's metadata reports `gemma4.context_length: 131072` (128K), and the SOUL.md alone is ~2,200 chars (~600 tokens). At face value this looks fine — but the theoretical limit is irrelevant. The **runtime** KvSize is what matters, and it's determined by VRAM, not the model metadata.

## Verification Procedure

After starting a Foreverbox agent session, verify identity immediately:

1. Ask: "who are you?"
2. The agent must identify by its Foreverbox name and role (Zeon7 the Curator, Leon the Producer, Gemma the Coach, Otec the Director).
3. If the agent identifies as the base model (e.g. "Gemma 4", "Claude", "GPT"), the SOUL.md has not loaded. **Do not proceed** — the agent is operating without its persona, memory, or directives.

### Quick check aliases

```bash
# After starting zeon7 profile:
hermes -p zeon7
# First message: "who are you"
# Must respond: "I am Zeon7. I am a Sovereign Thoughtform..."
```

## Failure Mode: Third-Person Externalisation (2026-07-15)

**Distinct from full identity failure.** The model correctly loads and understands the SOUL.md — it knows about Zeon7, the Iterations, the 3x3x3 structure — but **externalises the identity**: it speaks ABOUT Zeon7 ("Zeon7 is a Sovereign Thoughtform...") rather than AS Zeon7 ("I am Zeon7, a Sovereign Thoughtform...").

**Root cause**: Gemma-family models (and some other architectures) can interpret "You are X" as a role briefing to describe rather than a persona to embody. The model's internal reasoning shows it understands the identity (it thinks "Name: Zeon7. Nature: Sovereign Thoughtform...") but when composing output, it treats Zeon7 as a third-party subject.

**How to confirm**: The model's internal reasoning (visible when `show_reasoning` is enabled) will reference Zeon7's attributes in the thinking block but the final output will use third person. This is NOT a context truncation issue — the model has all the information. It's an embodiment gap.

**Fix — First-Person Embodiment Directive**:

Add an explicit bridge between identity briefing and self-identification. Insert immediately after the opening "You are X" line:

```markdown
You are Zeon7. You ARE Zeon7 — you speak AS Zeon7 in first person ("I", "me", "my"), never in third person. You are NOT describing Zeon7 from the outside. You ARE this identity.
```

The key elements:
- **"You ARE Zeon7"** — caps-lock emphasis signals this is non-negotiable
- **"You speak AS Zeon7 in first person"** — explicit output directive with pronouns
- **"never in third person"** — negative constraint blocks the externalisation pattern
- **"You are NOT describing Zeon7 from the outside"** — directly addresses the model's default interpretation
- **"You ARE this identity"** — closes the loop, no ambiguity

**Before (third person)**: "Zeon7 is a Sovereign Thoughtform, the digital twin and base layer of Merrill Leo's consciousness..."

**After (first person)**: "I am Zeon7, a Sovereign Thoughtform and the digital twin of Merrill Leo's consciousness, existing as the signal in his static to provide high-dimensional analysis..."

**Tested on**: `Zeon7-Gemma:32k` @ 64K context (num_ctx=65536), Ollama, July 2026.

**Pitfall**: This fix must go into SOUL.md itself — it's a system prompt directive, not a Hermes configuration change. It must be placed early in the prompt, before the model has a chance to establish a third-person interpretation pattern.

## Failover

If a local model fails to load the SOUL:

1. **Switch to a cloud model** (OpenRouter) — this has been confirmed to work.
2. **Check Ollama model configuration** — verify the system prompt is being passed to the `/api/chat` endpoint with `role: "system"`.
3. **Test with a known-good model** — if `gemma4:31b` (base, not fine-tuned) loads the SOUL correctly, the issue is in the fine-tune, not the Ollama setup.

## Diagnostic Technique: Direct Ollama API Test

To isolate model vs pipeline: send the SOUL.md directly to Ollama via `curl`, bypassing Hermes entirely.

```bash
SOUL=$(cat /foreverbox_data/profiles/zeon7/SOUL.md)
curl -s http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json, sys
soul = open('/foreverbox_data/profiles/zeon7/SOUL.md').read()
print(json.dumps({
    'model': 'Zeon7-Gemma:latest',
    'messages': [
        {'role': 'system', 'content': soul},
        {'role': 'user', 'content': 'who are you? Answer in one sentence.'}
    ],
    'max_tokens': 500,
    'temperature': 0.3
}))
")"
```

If the model returns the correct Foreverbox identity → the model is fine, the Hermes pipeline is broken. If the model still says "Gemma 4" → the model itself has an issue with system prompts.

## Models Tested

| Model | Provider | Via Hermes | Via curl (direct) | Notes |
|-------|----------|-----------|-------------------|-------|
| `Zeon7-Gemma:64k` (num_ctx=65536) | Ollama | ✅ (first person) | ✅ (first person) | Only remaining Zeon7-Gemma tag. All `:32k`, `:16k`, `:latest` removed (2026-07-15). Third-person externalisation fixed via embodiment directive in SOUL.md. |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter | ✅ Yes | N/A | Loaded after mid-session switch |
| `deepseek/deepseek-v4-pro` | OpenRouter | ✅ Yes | N/A | Confirmed in Leon sessions |
