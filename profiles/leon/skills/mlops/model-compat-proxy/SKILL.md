---
name: model-compat-proxy
category: mlops
description: Build and operate FastAPI translation proxies for local model compatibility - strip embedded tool-call JSON, inject tool schemas, translate streaming responses to OpenAI tool_calls format.
triggers:
  - Local model returns function-call JSON in content field instead of tool_calls
  - Model uses description as function name (Qwen 2.5: Run a shell command vs terminal)
  - Streaming chunks arrive character-by-character, breaking per-chunk detection
  - Need OpenAI-compatible endpoint for Hermes/custom providers
---

# Model Compatibility Proxy - Class Skill

## When to Use
- A local model (Ollama, vLLM, llama.cpp) emits tool calls as embedded JSON in content rather than tool_calls array
- Model uses function description as the name field (Qwen 2.5 Coder, others)
- Streaming responses break tool detection because each chunk is one character
- Hermes or other OpenAI-API consumers need standard tool_calls format

## Architecture
```
Client (Hermes) -> proxy:PORT/v1/chat/completions -> upstream:PORT/v1/chat/completions (Ollama)
                          |
                          +- Strip tools from request
                          +- Inject system prompt with exact JSON schema + names
                          +- Non-stream: extract JSON objects from content, emit tool_calls
                          +- Stream: buffer ALL chunks, on [DONE] detect & emit tool_calls
```

## Core Patterns

### 1. Request Preprocessing
```python
# Remove tools array so model doesn't see it (prevents double emission)
if "tools" in body:
    known_tools = {t["function"]["name"] for t in body["tools"]}
    body.pop("tools", None)
    # Inject system prompt with canonical schema
    body["messages"].insert(0, {"role": "system", "content": build_tool_prompt(original_tools)})
```

### 2. Non-Streaming Response Translation
```python
def extract_tool_json_objects(text: str) -> list[dict]:
    # Find balanced {...} objects, validate against known tool names
    # Return list of {"name": "...", "arguments": {...}}
```

### 3. Streaming: Buffer-Then-Detect (Critical)
Do NOT try per-chunk detection - Qwen streams one character per SSE event.
```python
async def stream_through_with_translation(response, known_tools):
    buffer = ""
    async for chunk in response.aiter_bytes():
        buffer += chunk.decode()
        # Pass through non-tool content immediately (SSE passthrough)
        # On "[DONE]": run extract_tool_json_objects(buffer)
        # If found: emit tool_calls SSE event, then [DONE]
        # Else: pass through accumulated content
```

### 4. Code-Block Stripping
Qwen wraps tool JSON in ```json ... ``` - strip before parsing:
```python
def remove_tool_json_from_text(text: str) -> str:
    text = re.sub(r'```json\s*\{.*?\}\s*```', '', text, flags=re.DOTALL)
    text = re.sub(r'\{[^}]*"name"\s*:\s*"[^"]+"[^}]*\}', '', text)
    return text.strip()
```

## Common Pitfalls
| Pitfall | Fix |
|---------|-----|
| async with httpx.AsyncClient() closes before stream ends | Create client OUTSIDE generator, keep alive for stream lifetime |
| Per-chunk if '"name"' in chunk never matches single chars | Buffer full response, detect at [DONE] |
| Double [DONE] emitted | continue after passthrough branch |
| Tool name = description (Run a shell command) | Inject system prompt with exact name: terminal schema |

## Deployment
- Port: 11435 (proxy) -> 11434 (Ollama)
- Health: GET /health -> {"status":"ok", "stats": {...}}
- Model list passthrough: GET /api/tags -> upstream
- Cron watchdog every 2 min: curl health, restart on failure

## Hermes Integration Commands
```bash
# One-shot test
curl -sN http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:7b","messages":[{"role":"user","content":"List /home"}],"tools":[{"type":"function","function":{"name":"terminal","description":"Run shell","parameters":{"type":"object","properties":{"command":{"type":"string"}}}}]}'

# Verify tool_calls in response
```

## Support Files
- references/qwen-tool-quirk.md - Qwen 2.5 Coder embedded JSON behavior, exact prompts that work
- scripts/verify-proxy.sh - end-to-end verification (health, models, passthrough, tool translation, streaming)
- templates/proxy.py - minimal FastAPI proxy skeleton (copy & extend)
- templates/watchdog.sh - cron restart script template