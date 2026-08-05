---
name: qwen-proxy
title: Qwen Proxy — Tool-Call Translation Layer
description: Build, run, and maintain the qwen_proxy FastAPI server that translates Qwen 2.5 embedded tool-call JSON into OpenAI-compatible tool_calls.
version: 1.0
---

# Qwen Proxy — Tool-Call Translation Layer

## Problem
Qwen 2.5 Coder (via Ollama) does not implement proper OpenAI `tool_calls` 
response. Instead, when it receives a `tools` parameter, it embeds a JSON 
object in `content` using names derived from the `description` field (not 
the `name` field). Hermes Agent expects proper `tool_calls` with the exact 
function `name`.

## Solution
A FastAPI proxy on port **11435** that:
1. **Strips the `tools` array** from incoming requests
2. **Injects a system prompt** describing the tools with exact names and JSON 
   format instructions
3. **Forwards to Ollama** (port 11434) 
4. **Post-processes the response** to extract embedded JSON and emit proper 
   `tool_calls`

## Files

| File | Purpose |
|------|---------|
| `proxy.py` | Main FastAPI server (500+ lines) |
| `qwen-proxy-watchdog.sh` | Cron watchdog script, restarts proxy if down |
| `watchdog.log` | Restart event log |

All under `/foreverbox_data/profiles/leon/services/qwen_proxy/`.

## Usage

### Start the proxy
```bash
cd /foreverbox_data/profiles/leon/services/qwen_proxy
source .venv/bin/activate
python proxy.py
```

### Health check
```bash
curl -s http://localhost:11435/health
# → {"status":"ok","proxy_port":11435,"upstream":"http://localhost:11434","stats":{"requests":0,"tool_calls_translated":0,"injections":0,"streaming_chunks":0}}
```

### Test non-streaming with tools
```bash
curl -s http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{...}' | python3 -m json.tool
```
Expected: `finish_reason: "tool_calls"` with correct function name.

### Test streaming with tools
```bash
curl -sN http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"stream": true, ...}'
```
Expected SSE: role → tool_call → [DONE].

### Test passthrough (no tools)
```bash
curl -s http://localhost:11435/v1/chat/completions \
  -d '{"model": "qwen2.5-coder:7b", "messages": [{"role": "user", "content": "Say hi"}]}'
```
Should return normal text response.

## Architecture

```
Hermes → port 11435 (proxy.py) → port 11434 (Ollama / Qwen)
```

### Non-streaming flow
1. Request arrives with `tools` array
2. Proxy strips `tools`, injects tool system prompt
3. Forwards modified request to Ollama
4. Ollama returns JSON in `content`
5. Proxy detects JSON with `extract_tool_json_objects()`
6. Proxy validates names, builds `tool_calls`, sets `finish_reason: "tool_calls"`
7. Returns transformed response

### Streaming flow
1. Same tool-stripping + prompt injection
2. Proxy buffers all `content` deltas from SSE stream
3. When `[DONE]` arrives, runs same detection on accumulated text
4. If tool JSON found → emits single tool_call SSE chunk + [DONE]
5. If no tool JSON → flushes buffered text as content chunks + [DONE]

## Cron Watchdog
Runs every 2 minutes (no_agent mode) checking proxy health:
```
cronjob action=list
```
Script at `~/.hermes/scripts/qwen-proxy-watchdog.sh`.

## Configuring Hermes
To route Ollama traffic through the proxy, update a custom provider:
```yaml
custom_providers:
  - name: qwen-local
    base_url: http://localhost:11435/v1
    model: qwen2.5-coder:7b
```

## Key Details
- Proxy uses `httpx.AsyncClient` with 300s timeout
- Streaming path keeps HTTPX client alive via `try/finally` in generator
- Tool name validation performs case-insensitive matching
- Code blocks (```json ... ```) wrapping tool JSON are stripped
- Stats are in-memory (resets on restart)
