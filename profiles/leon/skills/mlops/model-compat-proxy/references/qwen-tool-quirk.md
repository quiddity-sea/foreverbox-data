# Qwen 2.5 Coder Tool-Call Quirk Reference

## The Problem
Qwen 2.5 Coder (tested: `qwen2.5-coder:7b` via Ollama) emits tool calls as embedded JSON in the `content` field rather than the OpenAI-standard `tool_calls` array. Two specific issues:

1. **Name field uses description**: `"name": "Run a shell command"` instead of `"name": "terminal"`
2. **JSON wrapped in code blocks**: ````json {"name": "terminal", "arguments": {...}} ````

## Raw Qwen Output (non-streaming)
```json
{
  "choices": [{
    "message": {
      "content": "```json\n{\"name\":\"Run a shell command\",\"arguments\":{\"command\":\"ls /home\"}}\n```",
      "role": "assistant"
    },
    "finish_reason": "stop"
  }]
}
```

## Raw Qwen Output (streaming)
Each SSE chunk = 1 character:
```
data: {"choices":[{"delta":{"content":"{"}}]}
data: {"choices":[{"delta":{"content":"\""}}]}
data: {"choices":[{"delta":{"content":"n"}}]}
... (hundreds of chunks) ...
data: {"choices":[{"delta":{"content":"}"}}]}
data: [DONE]
```

## Working System Prompt Injection
The proxy injects this system prompt when `tools` is present in the request:

```json
{
  "role": "system",
  "content": "You are a helpful assistant with access to tools. When you need to use a tool, you MUST output the tool call in the following JSON format (no markdown, no extra text):\n\n{\"name\": \"exact_tool_name\", \"arguments\": {\"param\": \"value\"}}\n\nAvailable tools:\n- terminal: Run a shell command. Parameters: {\"command\": \"string\"}\n\nUse the exact tool names listed above."
}
```

This forces Qwen to:
- Use exact tool name `terminal` (not description)
- Output raw JSON without code fences
- Still embed in `content` field (handled by proxy extraction)

## Extraction Logic (proxy side)

### Non-streaming
```python
def extract_tool_json_objects(text: str, known_names: set) -> list[dict]:
    # 1. Strip ```json ... ``` code fences
    text = re.sub(r'```json\s*\{.*?\}\s*```', '', text, flags=re.DOTALL)
    # 2. Find balanced {...} objects containing "name"
    # 3. Parse JSON, validate name in known_names
    # 4. Return [{"name": "...", "arguments": {...}}]
```

### Streaming (buffer-then-detect)
```python
async def stream_with_translation(resp, known_names):
    buffer = ""
    async for chunk in resp.aiter_bytes():
        buffer += chunk.decode()
        # Passthrough non-tool content
    # At [DONE]: run extract_tool_json_objects(buffer)
    # If found: emit tool_calls SSE event, then [DONE]
```

## Verified Working Configuration
- **Proxy port**: 11435
- **Upstream**: http://localhost:11434 (Ollama)
- **Model**: qwen2.5-coder:7b
- **Hermes provider**: `qwen-local` (base_url: http://localhost:11435/v1, model: qwen2.5-coder:7b)
- **Test command**: `hermes chat --provider qwen-local -m qwen2.5-coder:7b -q "Use terminal to list /home"`

## Files in This Proxy Build
- `/foreverbox_data/profiles/leon/services/qwen_proxy/proxy.py` - full FastAPI implementation
- `/foreverbox_data/profiles/leon/services/qwen_proxy/qwen-proxy-watchdog.sh` - cron restart script
- Cron job: `qwen-proxy-watchdog` (every 2 min)

## Key Implementation Details
- `httpx.AsyncClient` created **outside** stream generator (lifespan = stream lifetime)
- Stats tracking: `requests`, `tool_calls_translated`, `injections`, `streaming_chunks`
- Health endpoint: `GET /health` returns stats
- Model list passthrough: `GET /api/tags` proxies to Ollama