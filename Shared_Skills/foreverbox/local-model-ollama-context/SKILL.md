---
name: local-model-ollama-context
title: Local Model Context Management
description: Managing Ollama custom modelfiles, VRAM budgets, context sizing, and dispatch methods for local Qwen 2.5 Coder models.
version: 1.0
---

# Local Model Context Management

## Custom Ollama Modelfiles
Default Ollama num_ctx is often 4096. Always create custom modelfiles.

```dockerfile
FROM qwen2.5-coder:7b
PARAMETER num_ctx 16384
```
```bash
ollama create qwen2.5-coder:7b-16k -f /tmp/Modelfile.16k
ollama run qwen2.5-coder:7b-16k ""
```

## VRAM Budget (Q4_K_M, 7B params on 8GB)
- 32K: ~7.4GB (tight)
- 16K: ~6.3GB (recommended)
- 8K: ~5.2GB (comfortable)

## Dispatch Methods
- **Interactive PTY** (`--cli chat`): Hangs with local Ollama providers. Do not use.
- **One-shot** (`-z`): Works. Executes tools correctly. Use for autonomous tasks.
- **delegate_task**: Uses parent cloud model, not local GPU. Not for local work.

## Config Notes
Set context in Hermes profile:
```bash
hermes config set model.context_length 1048576
```
Check for duplicates: `grep -n "context_length" <profile>/config.yaml`
Unset root-level duplicates: `hermes config unset context_length`
