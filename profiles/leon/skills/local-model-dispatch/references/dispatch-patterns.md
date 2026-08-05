# Dispatch Pattern Reference

## Launch Method Comparison

| Method | Command | Model | GPU | Best For |
|--------|---------|-------|-----|----------|
| One-shot | `-z "task"` | Config-specified | Fans spin | Fire-and-forget execution |
| PTY chat | `--cli chat` | Config-specified | Fans spin | Interactive debugging |
| delegate_task | `delegate_task(goal=...)` | Parent agent (cloud) | Silent | Complex multi-step reasoning |

## Common Dispatch Failure Chain

1. Hermes starts → welcomes → accepts input ✓
2. GPU at 2-5% (model loaded but idle)
3. Chat timer ticks up ("31s | ⏲ 0s") but 0 output tokens
4. Model responds instantly via direct curl (bypassing Hermes)

**Root cause:** Stale gateway (PID weeks old, D-state) blocking API calls, OR model not pre-loaded causing cold-start timeout, OR context too small for system prompt.

## Verified Working Commands

### Pre-load model
```bash
ollama run qwen2.5-coder:7b-ctx "" &
```
Verification: `nvidia-smi` shows 5779+ MB used, `curl localhost:11434/api/ps` shows model loaded.

### Create custom context model
```bash
echo -e "FROM qwen2.5-coder:7b\nPARAMETER num_ctx 32768" | ollama create qwen2.5-coder:7b-ctx -f -
```

### Dispatch redesign task
```bash
cd /foreverbox_data
python3 /foreverbox_data/bin/assemble_soul.py zeon7 coder
hermes --profile zeon7 --provider qwen-local -m qwen2.5-coder:7b-ctx -z \
  "Execute the redesign at /var/www/the-foreverbox-institute/the-project/ following REDESIGN_BLUEPRINT.md. Start Phase 0."
```

### Kill stale gateway
```bash
ps aux | grep gateway | grep -v grep | awk '{print $2}' | xargs kill -9
```

### Proxy health check
```bash
curl -s http://localhost:11435/health
```
