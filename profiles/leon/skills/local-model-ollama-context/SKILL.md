---
name: local-model-ollama-context
title: Local Model Context Management
description: Ollama modelfiles, VRAM budgets, dispatch methods, gateway debugging, and keepalive for local Qwen 2.5 Coder on 8GB GPU.
version: 1.1
---

# Local Model Context Management

## Custom Ollama Modelfiles
Default Ollama num_ctx is often 4096. Always create custom modelfiles.

```
FROM qwen2.5-coder:7b
PARAMETER num_ctx 16384
```
```bash
ollama create qwen2.5-coder:7b-16k -f /tmp/Modelfile.16k
ollama run qwen2.5-coder:7b-16k ""
```

**Modelfile syntax pitfall (hit 2026-07-31):** `STOP "<token>"` is NOT a valid modelfile directive. `ollama create` rejects it with:
`Error: (line N): command must be one of "from", "license", "template", "system", "adapter", "renderer", "parser", "parameter", "message", or "requires"`.
Stop tokens are declared as parameters: `PARAMETER stop "<token>"`. Template errors ("unexpected EOF") usually mean the TEMPLATE string is missing a closing brace or quote — keep the template on one line with `\n` escapes, or verify by running `ollama create` and reading the exact error line.

## Importing a Raw GGUF File into Ollama (shared store)

Ollama's service runs as user `ollama` (home `/usr/share/ollama`); its model store lives at `/usr/share/ollama/.ollama/models/` — that is the SHARED location on this WSL instance; do NOT store model files in `/home/<user>/` (user directive). Import an existing GGUF:

```bash
# 1. Move the GGUF into the shared store and fix ownership
sudo mv ~/models/Qwen3-8B-Q4_K_M.gguf /usr/share/ollama/.ollama/models/
sudo chown ollama:ollama /usr/share/ollama/.ollama/models/Qwen3-8B-Q4_K_M.gguf

# 2. Create a modelfile in the same directory
sudo -u ollama bash -c 'cat > /usr/share/ollama/.ollama/models/qwen3-8b-q4km.modelfile <<EOF
FROM ./Qwen3-8B-Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 32768
PARAMETER num_batch 512
PARAMETER num_thread 6
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
TEMPLATE "{{ if .System }}<|im_start|>system\n{{ .System }}<|im_end|>{{ end }}\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n{{ .Response }}<|im_end|>\n"
EOF'

# 3. Register it (run as the ollama user so files stay owned correctly)
sudo -u ollama ollama create qwen3-8b-q4km -f /usr/share/ollama/.ollama/models/qwen3-8b-q4km.modelfile

# 4. Verify
curl -s http://localhost:11434/api/tags
```

**Qwen3 / thinking-token leakage (hit 2026-07-31):** serving a raw Qwen3 GGUF via a modelfile WITHOUT a proper chat template causes the model to leak its internal reasoning as raw tokens — either escaped Unicode (`\u003cthink\u003e...`) or natural-language narration ("Okay, the user said...") — and it can loop on repeated tokens. The modelfile must supply the ChatML template (above) AND `PARAMETER stop "<|im_start|>"`/`<|im_end|>` AND `PARAMETER repeat_penalty` (1.1+). A system prompt like "Answer directly, do not show your reasoning" further suppresses thinking. If a raw-GGUF import still narrates reasoning after the template fix, the cleanest fallback is pulling the model from the Ollama library (`ollama pull qwen3:8b`), which ships a prebuilt, correct template.

**Permission pitfall:** the store is root-owned; writing with `write_file`/plain tools fails with "Permission denied". Always create/update files as the `ollama` user via `sudo -u ollama`, and `chown ollama:ollama` after `sudo mv`.

After creating a new model variant, update the Hermes custom provider to point to it:
```bash
# In the agent's config.yaml (e.g. /foreverbox_data/profiles/zeon7/config.yaml):
custom_providers:
  - name: qwen-local
    base_url: http://localhost:11435/v1
    model: qwen2.5-coder:7b-16k   # <-- update this line
```
Then unload the old model from GPU before loading the new one:
```bash
curl -s http://localhost:11434/api/generate -d '{"model":"<old-name>","keep_alive":0}' > /dev/null
```

## VRAM Budget (Q4_K_M, 7B params on 8GB)
- 32K: ~7.4GB (DANGER — less than 600MB free, causes silent generation failures)
- 16K: ~6.3GB (recommended, ~1.9GB free)
- 8K: ~5.2GB (comfortable)
VRAM = model weights (~3.8GB Q4_K_M) plus KV cache (~0.2GB per 1K context) plus overhead

**Pitfall:** At 32K on an 8GB card, the model loads into GPU but inference hangs or produces zero output tokens even though the model appears loaded in `ollama ps`. The GPU utilization meter shows 2-3% — the model is alive but has no room to compute. Dropping to 16K frees ~1.1GB and restores normal inference. Always start at 16K and only bump to 32K if the task requires the full context window.

## Dispatch Methods
- **Interactive PTY** (`hermes --cli chat`): Hangs with local Ollama providers. Do not use.
  Symptoms: GPU idle (2-5% util, fans silent), Hermes shows zero output tokens forever. Even --safe-mode and --ignore-rules do not fix. Root cause: interactive mode never sends API call to proxy.
- **One-shot** (`hermes -z`): Works. Responds correctly. Use for autonomous tasks.
  Note: one-shot mode does not register tools array. Tool-calling still works because qwen proxy injects tool descriptions.
- **delegate_task**: Uses parent cloud model, NOT local GPU. Not selectable per call. Do not use for local GPU tasks.
- **Direct proxy curl**: Works perfectly. Proxy to Ollama responds in under 8s. Use for chain testing.

## Gateway Debugging
Check for duplicate gateways when launching with local providers:
```bash
ps aux | grep "gateway" | grep -v grep
```
- Kill stuck gateways: `kill -9 PID` (D-state may need SIGKILL)
- Expected: one gateway per profile
- Restart: `hermes gateway restart --profile zeon7`

## Keepalive
Ollama models unload after about 5 min default. Check expiry:
```bash
curl -s http://localhost:11434/api/ps | python3 -c "import sys,json; [print(f'{m[\"name\"]}: expires={m[\"expires_at\"]}') for m in json.load(sys.stdin).get('models',[])]"
```
Preload with keepalive: `ollama run MODEL ""` (background keeps alive)

## Hermes Config
```bash
hermes config set model.context_length 1048576
```
Check for duplicates: `grep -n "context_length" CONFIG.yaml`
Unset root-level duplicates: `hermes config unset context_length`

## References
- `references/qwen3-gguf-import.md` — GGUF import into the shared store,
  server-side Qwen3 chain-of-thought strip regex (`preg_replace('/^<think>.*\n\n/s', ...)` —
  greedy to the last blank line, since Qwen3 usually omits `</think>`), and
  first-inference latency warning (first call can exceed 60s while the 4.7GB
  model loads into VRAM; retry once warm).
- `references/vram-budget-reference.md` — VRAM sizing details.
