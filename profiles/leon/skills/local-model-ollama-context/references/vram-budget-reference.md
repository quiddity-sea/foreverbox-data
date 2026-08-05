# Ollama Context & VRAM Quick Reference

> Updated 2026-07-23

## Model: qwen2.5-coder:7b (Q4_K_M quant, 7.6B params)

| Context | VRAM | Free (8GB card) | Verdict |
|---------|------|-----------------|---------|
| 32K | 7.4 GB | ~0.6 GB | Too tight — inference sluggish |
| 16K | 6.3 GB | ~1.9 GB | Recommended |
| 8K | 5.2 GB | ~2.8 GB | Comfortable |

## Model Disk Size vs VRAM
- 4.7 GB on disk (4,683,087,561 bytes)
- VRAM includes weights (~3.8 GB Q4) + KV cache (~1.5-3.2 GB depending on context) + overhead
- Do not confuse parameter count (7.6B) with file size

## Custom Modelfile Pattern
```bash
echo 'FROM qwen2.5-coder:7b
PARAMETER num_ctx 16384' > /tmp/Modelfile.16k
ollama create qwen2.5-coder:7b-16k -f /tmp/Modelfile.16k
```

## Why Modelfile is Required
The qwen proxy does NOT pass `num_ctx` to Ollama. Ollama defaults to 4096 for this model. A custom modelfile with PARAMETER num_ctx is the only way to set context at load time.

## Verify Context
```bash
curl -s http://localhost:11434/api/ps | python3 -c "import sys,json; print(json.load(sys.stdin)['models'][0].get('context_length','?'))"
```

## Update Provider
After creating new model, update the Hermes profile's provider model name:
```yaml
custom_providers:
  - name: qwen-local
    base_url: http://localhost:11435/v1
    model: qwen2.5-coder:7b-16k    # <- update this
```
