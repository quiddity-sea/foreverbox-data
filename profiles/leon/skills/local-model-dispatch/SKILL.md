---
name: local-model-dispatch
description: "Diagnose and fix local model dispatch failures: stale gateways, GPU not loaded, context too small, PTY dispatch vs one-shot vs delegate_task."
version: 1.0.0
author: Leon (Layer 2 Producer)
license: MIT
platforms: [linux]
---

# Local Model Dispatch

## When to Use

When a local Ollama model won't generate output despite Hermes starting successfully, or when trying to dispatch a local model to work autonomously on a task.

## Symptoms

- Hermes starts, shows welcome banner, accepts input
- GPU stays at 2-5% utilization (idle)
- Chat shows elapsed time (e.g. "31s | ⏲ 0s") but 0 output tokens
- Gateway already-running messages in journal

## Diagnosis

### 1. Check if model is in VRAM
```bash
curl -s http://localhost:11434/api/ps
```
If empty, the model needs pre-loading.

### 2. Check model context
```bash
curl -s http://localhost:11434/api/show -d '{"model":"<name>"}' | grep num_ctx
```
Default Ollama num_ctx is often 4096 — too small for SOUL-based sessions.

### 3. Check for stale gateways
```bash
ps aux | grep gateway
```
A process weeks old with ~0 CPU means a stale gateway is blocking API calls.

### 4. Check network connection
```bash
ss -tnp | grep -E "11434|11435"
```
If empty, no connection between Hermes and the model.

### 5. Test model directly (bypass Hermes)
```bash
curl -s -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"<name>","messages":[{"role":"user","content":"ok"}],"max_tokens":5}'
```
If this returns a response, the model and proxy work — the issue is in Hermes dispatch.

### 6. Test proxy tool-calling translation
Verify the qwen proxy correctly translates tools array into proper tool_calls:
```bash
curl -s -X POST http://localhost:11435/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model":"<name>",
    "messages":[
      {"role":"system","content":"You have tool access."},
      {"role":"user","content":"Run terminal(\"echo ok\")"}
    ],
    "tools":[{"type":"function","function":{"name":"terminal","description":"Run shell cmd","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}}]
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print('tool_calls' if 'tool_calls' in d['choices'][0]['message'] else 'text only')"
```
Should print `tool_calls`. If it prints `text only`, the proxy injection is broken.

### 7. Check VRAM headroom

## Fixes

### Fix 1: Pre-load the model
```bash
ollama run <model-name> "" &
sleep 5
curl -s http://localhost:11434/api/ps
```

### Fix 2: Increase context with custom Modelfile
Create a model variant with larger context:
```
FROM qwen2.5-coder:7b
PARAMETER num_ctx 32768
```
```bash
ollama create <model-name>-ctx -f /tmp/Modelfile.ctx
```
Then update the Hermes custom provider to use `<model-name>-ctx`.

### Fix 3: Kill stale gateways
```bash
kill -9 <pid>
```
Re-launch after verifying all are gone. A stale gateway in D-state (uninterruptible sleep) blocks API calls from new Hermes sessions.

### Fix 4: Use one-shot dispatch (-z) not PTY
For fire-and-forget execution tasks, the one-shot flag is most reliable:
```bash
hermes --profile <agent> --provider <custom> -m <model> -z "task instructions"
```
The `-z` flag bypasses the interactive TUI and sends the prompt directly to the API. PTY chat hangs with large SOULs on slow local 7B models.

### Fix 5: Use delegate_task (cloud model)
For complex reasoning tasks that need cloud intelligence but tool access:
```python
delegate_task(goal="...", context="...")
```
**Caveat:** Subagents inherit the parent agent's model (cloud), not the local model. GPU stays idle.

### Fix 6: Assemble the variant SOUL first
If using a variant (e.g. Zeon7 Coder), assemble before dispatch:
```bash
python3 /foreverbox_data/bin/assemble_soul.py zeon7 coder
hermes --profile zeon7 --provider qwen-local -m qwen2.5-coder:7b-ctx -z "task"
```

### Fix 7: Verify GPU activity after dispatch
```bash
nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits -l 1
```
Should spike to 50-100% during inference. Below 5% = model not running.
