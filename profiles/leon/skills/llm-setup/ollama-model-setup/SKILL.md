---
name: ollama-model-setup
description: Configure Ollama to serve Qwen3 GGUF model without leaking internal thinking tokens.
category: llm-setup
---

# Ollama Model Setup for Qwen3 Series

## When to Use
- Importing a raw GGUF file (e.g. `Qwen3-8B-Q4_K_M.gguf`) into Ollama so it can be served via the Ollama API/CLI
- Fixing a Qwen3 model that loops, repeats tokens, or leaks internal thinking tokens (`<think>` output)
- Any "model works in llama.cpp but Ollama output is garbage" situation

## Why This Exists
A raw GGUF loaded by Ollama with no modelfile (or a modelfile with no stop tokens / no chat template) will:
- Emit internal thinking markers (e.g. `\u003cthink\u003e` / `<think>`) as literal output
- Loop on a single token or short sequence (`hello hello hello...`) because generation never hits a stop condition
- Treat the prompt as a continuation instead of a chat turn

## Proven Procedure (this session)

### 1. Place the GGUF in the shared Ollama model store
Ollama service runs as the `ollama` system user with home `/usr/share/ollama`. Models live in `/usr/share/ollama/.ollama/models/`. The service user must own the file:

```bash
sudo mv /home/<user>/models/Qwen3-8B-Q4_K_M.gguf /usr/share/ollama/.ollama/models/
sudo chown ollama:ollama /usr/share/ollama/.ollama/models/Qwen3-8B-Q4_K_M.gguf
```

### 2. Write the modelfile (CORRECT syntax)
```text
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
```

### 3. Create and test the model
```bash
sudo -u ollama ollama create qwen3-8b-q4km -f /usr/share/ollama/.ollama/models/qwen3-8b-q4km.modelfile
ollama run qwen3-8b-q4km:latest
```

## Serving the Model from an HTTPS Web Page (PHP proxy pattern)

A browser page served over HTTPS **cannot** call `http://localhost:11434` directly (mixed-content block + CORS). The working pattern (used for the FBOX SELF page) is a server-side PHP proxy:

- The page POSTs JSON to itself (`fetch('self.php', {method:'POST', body: JSON.stringify({message, history})})`).
- PHP forwards to `http://localhost:11434/api/chat` with `curl`, `stream:false`, and returns JSON.

```php
// self.php — POST branch
$payload = json_encode([
  'model'    => 'qwen3-8b-q4km',
  'messages' => $messages,            // [{role, content}, ...] history + new user msg
  'stream'   => false,
  'options'  => ['temperature' => 0.7, 'num_ctx' => 32768],
]);
$ch = curl_init('http://localhost:11434/api/chat');
curl_setopt_array($ch, [
  CURLOPT_RETURNTRANSFER => true, CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => $payload,
  CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
  CURLOPT_TIMEOUT => 120,
]);
$resp = curl_exec($ch);
```

## Critical Pitfalls (all hit in session)

1. **`STOP` is NOT a valid modelfile directive.** Using `STOP "..."` fails with:
   `Error: (line 8): command must be one of "from", "license", "template", "system", "adapter", "renderer", "parser", "parameter", "message", or "requires"`
   The correct form is `PARAMETER stop "..."` — one PARAMETER line per stop token.

2. **Never use an empty stop token.** `PARAMETER stop ""` matches at position 0 of every string, so generation stops immediately and the API returns an empty response (`"response":""`, `"done_reason":"stop"`). Only add stop tokens with real content.

3. **Qwen3 needs the ChatML markers in the template.** A template using bare role labels (`system\n...user\n...assistant\n...`) is NOT enough. The model was trained on `<|im_start|>system ... <|im_end|>` style markers. Without them the model produces raw role text / thinking narration. Use the exact TEMPLATE in step 2.

4. **Looping = missing stop tokens.** If the model repeats a token indefinitely, it is not seeing any stop condition. Add `PARAMETER stop "<|im_start|>"` and `PARAMETER stop "<|im_end|>"` (and, for thinking-token leakage, `PARAMETER stop "<think>"` / `PARAMETER stop "</think>"`).

5. **Stripping the Qwen3 thinking block — the model emits `<think>` with NO closing tag.** A naive `preg_replace('/<think>.*?<\/think>/s', ...)` does nothing because Qwen3's raw output is `<think>\n{reasoning}\n\n{answer}` — no `</think>` exists. The working strip removes from the opening tag through the **last blank line**, then drops any surviving tags:
   ```php
   $answer = preg_replace('/^<think>.*\n\n/s', '', $answer);
   $answer = preg_replace('/<\/?think>/', '', $answer);
   ```
   (Verified end-to-end: raw 376-char response with thinking preamble → clean `"Hello! How can I assist you?"`.)

6. **Write the modelfile as the ollama user** (`sudo -u ollama bash -c 'cat > ...'`) or it ends up unreadable/undeletable by the service. The write_file tool cannot write into `/usr/share/ollama/.ollama/models/` directly (permission denied) — route through sudo.

7. **Don't create placeholder dirs in the user's home.** A dry-run `mkdir -p /home/<user>/ollama_models/...` leaves clutter the user will later find and ask to delete. If you only need the modelfile, keep it in the model store or /tmp.

## Notes
- The model name in Ollama is `qwen3-8b-q4km:latest` (auto-suffixed with `:latest`).
- Verify with `curl -s http://localhost:11434/api/tags` — the model should appear with `"family":"qwen3"`, `"quantization_level":"Q4_K_M"`.
- If generation still narrates thinking in English (no `<think>` token), add a system prompt: `You are a helpful assistant. Answer directly and concisely without narrating your thought process.`
- On this machine Ollama service is systemd-enabled (`ollama.service`) and starts on WSL boot. To start it immediately: `sudo systemctl start ollama.service`.
- HTTP status sanity check used for the SELF page: `GET self.php -> 200`, chat proxy POST returns clean `{response}` JSON with no think preamble (verified end-to-end via curl in the browser-absent CLI).

## References
- Ollama modelfile documentation: https://github.com/ollama/ollama/blob/main/docs/modelfile.md
- Qwen3 tokenizer special tokens: inspection of tokenizer.json on Hugging Face
