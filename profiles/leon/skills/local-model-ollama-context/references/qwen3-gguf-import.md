# Qwen3 GGUF Import into Shared Ollama Store (verified 2026-07-31)

Ollama on this host runs as service user `ollama` (home `/usr/share/ollama`);
the SHARED model store is `/usr/share/ollama/.ollama/models/` — never keep
model files in home directories (user directive). To serve a raw GGUF:

```bash
# 1. Move the GGUF into the store (needs sudo; store owned by ollama)
sudo mv /home/<user>/models/Qwen3-8B-Q4_K_M.gguf /usr/share/ollama/.ollama/models/
sudo chown ollama:ollama /usr/share/ollama/.ollama/models/Qwen3-8B-Q4_K_M.gguf

# 2. Write a modelfile (must be executed AS the ollama user; /tmp is not
#    readable by ollama, so stage the file inside the store dir)
sudo -u ollama bash -c 'cat > /usr/share/ollama/.ollama/models/qwen3-8b.modelfile <<EOF
FROM ./Qwen3-8B-Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 32768
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
EOF'

# 3. Create and verify
sudo -u ollama ollama create qwen3-8b-q4km -f /usr/share/ollama/.ollama/models/qwen3-8b.modelfile
curl -s http://localhost:11434/api/tags   # model should appear
```

Notes:
- `ollama create` with a local GGUF prints a long progress spinner
  ("gathering model components / copying file ... / parsing GGUF") then
  `success`. It copies the file into blobs, so the store needs free space.
- Model name must be lowercase, no spaces: `qwen3-8b-q4km:latest`.
- Legacy qwen2.5-coder:7b variants were deleted from Ollama (2026-07); the
  current local model on this host is Qwen3-8B-Q4_K_M served as qwen3-8b-q4km.

## Qwen3 Chain-of-Thought

Qwen3 (Q4_K_M) emits a reasoning preamble: `<think>\n{thinking}\n\n{answer}`
and typically does NOT emit a closing `</think>` tag. Consequences:

1. **Modelfile-level:** do not try to suppress thinking by adding a stop token
   for the content — the model still generates the reasoning tokens.
2. **Server-side stripping** (the reliable fix, in a PHP/JS proxy): the regex
   must remove the WHOLE preamble, not just the tags:
   ```php
   $answer = preg_replace('/^<think>.*\n\n/s', '', $answer);  // greedy to last blank line
   $answer = preg_replace('/<\/?think>/', '', $answer);        // drop stray tags
   ```
   A naive `strip_tags`-style removal leaves the plain-text reasoning behind.
   Verified clean output: `"Say hello"` -> `"Hello! How can I assist you?"`.

## First-inference latency

The first generation after a modelfile recreation can exceed 60s while the
model loads into VRAM (4.7GB GGUF). Retry once the runner is warm
(`ollama ps` shows the model loaded); long curl timeouts (120s+) for the
first call are normal.
