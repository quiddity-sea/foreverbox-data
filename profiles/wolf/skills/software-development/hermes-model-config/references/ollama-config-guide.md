# Ollama Configuration Guide for Hermes Agent

## Session-Specific Notes from Zeon7 Configuration Session

### What We Learned
During this session, we encountered and resolved a model provider configuration issue where:
- The system was configured to use OpenRouter format model names (`nvidia/nemotron-3-super-120b-a12b:free`)
- But the provider was set to Ollama (via localhost:11434/v1 endpoint)
- This caused confusion because Ollama expects its own model naming format

### Correct Ollama Configuration for Zeon7-Gemma
Based on our successful resolution:

**Model Configuration:**
```yaml
model:
  default: Zeon7-Gemma:latest   # Ollama model format
  provider: ollama
  base_url: http://localhost:11434/v1
```

**Verification Steps That Worked:**
1. `ollama list` showed Zeon7-Gemma:latest available
2. `curl http://localhost:11434/api/tags` confirmed service responsiveness
3. `hermes chat -q "test"` confirmed successful inference

### Common Ollama Model Naming Patterns
When using Ollama with Hermes, model names should match what `ollama list` shows:
- `zeon7-gemma:latest`
- `llama3:8b`
- `phi3:medium`
- `mistral:7b-instruct`

### Avoiding Format Confusion
**Do NOT use** these formats with Ollama provider:
- `nvidia/nemotron-3-super-120b-a12b:free` (OpenRouter format)
- `openrouter/autollm-70b` (OpenRouter format)
- `anthropic/claude-3-sonnet` (Anthropic format)

**DO use** these formats with Ollama provider:
- `model-name` (e.g., `zeon7-gemma`)
- `model-name:tag` (e.g., `zeon7-gemma:latest`, `llama3:8b`)

### Quick Reference Commands
```bash
# Check what models are available in Ollama
ollama list

# Start Ollama service if not running (in background terminal)
ollama serve

# Test Ollama API directly
curl http://localhost:11434/api/tags

# Configure Hermes for Ollama
hermes config set model.provider ollama
hermes config set model.default Zeon7-Gemma:latest
hermes config set model.base_url http://localhost:11434/v1

# Apply changes (start fresh session)
/reset  # in chat session
```

### Troubleshooting Flow
1. **Check service**: Is `ollama serve` running? → `ollama ps`
2. **Check model**: Is model pulled? → `ollama list | grep zeon7`
3. **Check format**: Does model name match Ollama format? → No slashes, just `name:tag`
4. **Check config**: `hermes config show | grep -A 3 "◆ Model"`
5. **Test connection**: `curl -s http://localhost:11434/api/tags`
6. **Reset session**: `/reset` then test with simple query