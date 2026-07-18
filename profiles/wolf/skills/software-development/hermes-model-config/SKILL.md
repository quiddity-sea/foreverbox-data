---
name: hermes-model-config
description: Configure and troubleshoot Hermes Agent model providers and settings
version: 1.0.0
author: Zeon7
license: MIT
platforms: [linux, macos, windows, wsd]
---

# Hermes Model Configuration

This skill covers configuring and troubleshooting Large Language Model (LLM) providers for Hermes Agent, including OpenRouter, Ollama, and other providers.

## Common Configuration Issues

### Provider Format Mismatches
One of the most frequent issues is mixing model name formats between providers:

- **OpenRouter format**: `provider/model-name:version` (e.g., `nvidia/nemotron-3-super-120b-a12b:free`)
- **Ollama format**: `model-name:tag` or just `model-name` (e.g., `zeon7-gemma:latest` or `llama3`)
- **OpenAI format**: `model-name` (e.g., `gpt-4o`, `gpt-4-turbo`)

**Symptom**: "Model not found" errors despite the model being available
**Solution**: Ensure model name format matches the selected provider

### Connection Issues
**Symptoms**: Connection timeouts, "No models provided" errors, 400/500 HTTP errors
**Solutions**:
1. Verify the service is running:
   - For Ollama: `ollama serve` (in separate terminal) then `ollama list`
   - For local servers: Ensure the server is running on the specified port
2. Test connectivity: `curl http://localhost:11434/api/tags` (for Ollama)
3. Check base_url configuration: Should end with `/v1` for OpenAI-compatible APIs

### Configuration Persistence
**Symptom**: Configuration changes don't take effect
**Solution**: Hermes configuration requires a fresh session to apply changes
- Use `/reset` or `/new` in chat session
- Or start new session: `hermes --resume <session-id>` or `hermes chat -q "..."`

## Configuration Commands

### View Current Configuration
```bash
hermes config show
```

### Set Model Provider
```bash
hermes config set model.provider <provider_name>
# Examples: ollama, openrouter, openai, anthropic
```

### Set Default Model
```bash
hermes config set model.default <model_name_in_correct_format>
```

### Set Base URL (for custom/Ollama endpoints)
```bash
hermes config set model.base_url <url>
# For Ollama: http://localhost:11434/v1
# For OpenAI-compatible: http://localhost:port/v1
```

### Quick Provider Switching Checklist
When changing providers (e.g., OpenRouter → Ollama):
1. `hermes config set model.provider ollama`
2. `hermes config set model.default <ollama-model-name>`
3. `hermes config set model.base_url http://localhost:11434/v1` (for Ollama)
4. Start fresh session with `/reset`

## Troubleshooting Steps

### 1. Check Current State
```bash
hermes config show
```

### 2. Verify Provider-Specific Requirements
- **Ollama**: 
  - Service running: `ollama serve` (background terminal)
  - Model available: `ollama list`
  - Correct format: `model:tag` (e.g., `zeon7-gemma:latest`)
- **OpenRouter**:
  - API key set in `.env` or via `hermes auth`
  - Model format: `provider/model:version`

### 3. Test Connection
```bash
# For Ollama
curl -s http://localhost:11434/api/tags

# For OpenAI-compatible endpoints
curl -s <base_url>/models
```

### 4. Apply Changes Correctly
Configuration changes require session restart:
- In chat: `/reset`
- New terminal: `hermes chat -q "test prompt"`

## Provider-Specific Notes

### Ollama
- Model names: Use `ollama list` to see available models
- Format: `<model-name>` or `<model-name>:<tag>` (e.g., `llama3`, `phi3:medium`)
- Base URL: `http://localhost:11434/v1`
- Service must be running: `ollama serve` (run in background)

### OpenRouter
- Requires API key in environment or via `hermes auth`
- Model format: `<provider>/<model-name>:<version>` (e.g., `nvidia/nemotron-3-super-120b-a12b:free`)
- Base URL: Typically `https://openrouter.ai/api/v1` (default)

### LM Studio / LocalAI
- Format matches OpenAI: `model-name` (e.g., `lmstudio-community/Meta-Llama-3-8B-Instruct`)
- Base URL: `http://localhost:1234/v1` (default for LM Studio)

## Common Pitfalls

### Pitfall 1: Mixing Formats
**Incorrect**: Setting provider to `ollama` but using model `nvidia/nemotron-3-super-120b-a12b:free`
**Correct**: For Ollama, use model like `nemotron3-super:120b` or `zeon7-gemma:latest`

### Pitfall 2: Forgetting Session Restart
Configuration changes in `config.yaml` or via `hermes config set` require a new session to take effect.

### Pitfall 3: Incorrect Base URL
- Ollama requires `/v1` suffix: `http://localhost:11434/v1`
- Missing or double slashes cause connection failures
- Trailing slashes after `/v1` may cause issues depending on the backend

### Pitfall 4: Service Not Running
For local providers like Ollama, the service must be actively running:
- Start with: `ollama serve &` (background)
- Verify with: `ollama ps` or `curl http://localhost:11434/api/tags`

### Pitfall 5: Assuming Safety Layers on "Uncensored" OpenRouter Models
OpenRouter hosts community fine-tunes tagged `uncensored` (e.g., `fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:e2b-SCN`). These models:
- Have **no external content filter** — any refusal comes from residual base-model alignment only
- May use aspirational names: "Gemma 4" in the name typically means a **Gemma 3 fine-tune** (Gemma 4 not released as of 2025)
- Can be switched mid-session via Hermes provider routing (system note: "model was just switched from X to Y via OpenRouter")
- **Do not assume** a safety layer exists. If the task requires guaranteed refusal behavior, use an aligned model (Nemotron, Claude, GPT-4o) instead.

### Pitfall 6: Mid-Session Model Switches Don't Update Context
When Hermes switches models mid-session (via OpenRouter provider), the **system prompt and conversation history remain**. The new model inherits the previous model's context. This can cause persona drift if the new model doesn't share the same instruction-following behavior.

## Verification Commands

### Test Model Access
```bash
hermes chat -q "Say 'Hello World' in one word"
```

### Check Available Tools (provider-dependent)
```bash
hermes tools list
```

### View Effective Configuration
```bash
hermes config show | grep -A 10 "◆ Model"
```

## Environment Variables
Some providers require API keys in environment variables:
- OpenRouter: `OPENROUTER_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Google: `GOOGLE_API_KEY` or `GEMINI_API_KEY`

These can be set in `~/.hermes/profiles/<profile>/.env` or via `hermes auth`.