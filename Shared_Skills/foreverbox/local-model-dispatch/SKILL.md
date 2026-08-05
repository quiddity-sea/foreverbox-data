---
name: local-model-dispatch
description: "Diagnose and fix local model dispatch failures: stale gateways, GPU not loaded, context too small, PTY dispatch vs delegate_task."
version: 1.0.0
author: Leon (Layer 2 Producer)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [foreverbox, local-model, ollama, dispatch, gateway]
    related_skills: [qwen-proxy, fbox-operations]
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

## Fixes

### Fix 1: Pre-load the model
```bash
ollama run <model-name> "" &
sleep 5
curl -s http://localhost:11434/api/ps  # verify loaded
```

### Fix 2: Increase context with custom Modelfile
```
FROM qwen2.5-coder:7b
PARAMETER num_ctx 32768
```
```bash
ollama create <model-name>-ctx -f /tmp/Modelfile.ctx
```
Update the Hermes provider's model to `<model-name>-ctx`.

### Fix 3: Kill stale gateways
```bash
kill -9 <pid>  # repeat for each stale gateway
```
Re-launch Hermes after verifying all stale gateways are gone.

### Fix 4: Use delegate_task instead of PTY
When dispatching a model to work autonomously on a build/coding task:
```bash
delegate_task(goal="...", context="...")
```
Do NOT use `terminal(background=true, pty=true)` with Hermes --cli chat. The PTY session is designed for interactive use and won't process tasks autonomously.

## DeepSeek Context Configuration
DeepSeek supports 1M context. Set in profile config:
```bash
hermes config set model.context_length 1048576
```
Verify: `hermes config get model.context_length`. Check for duplicate entries in config.yaml.
