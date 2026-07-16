---
name: hermes-llm-provider-setup
description: Configure LLM providers and models in Hermes Agent
version: 1.0.0
author: zeon7
license: MIT
---

# Hermes LLM Provider Configuration

Guide for configuring language model providers in Hermes Agent, including Ollama, OpenRouter, and other supported providers.

## When to Use This Skill

Use this skill when you need to:
- Set up or change the LLM provider (Ollama, OpenRouter, Anthropic, etc.)
- Configure a specific model for use with Hermes
- Troubleshoot model provider connectivity issues
- Understand the difference between global and profile-specific configuration

## Configuration Flow

Hermes uses a two-layer configuration system:
1. **Global configuration** (`~/.hermes/config.yaml`) - affects all profiles
2. **Profile configuration** (`~/.hermes/profiles/<name>/config.yaml`) - overrides global settings for specific profiles

The active profile (set with `hermes profile use <name>` or shown with ◆ in `hermes profile list`) determines which configuration takes precedence.

## Step-by-Step: Setting Ollama as Provider

### 1. Check Current Configuration
```bash
hermes config show
```
Look for the `model` section to see current provider, model, and base_url.

### 2. Configure Provider and Model
To use Ollama with a local model:
```bash
# Set provider to ollama
hermes config set model.provider ollama

# Set model to your local model (check with `ollama list`)
hermes config set model.provider ollama
hermes config set model.default <model-name>:<tag>

# Optional: Set base URL if not using default localhost:11434
hermes config set model.base_url http://localhost:11434/v1
```

### 3. Verify Configuration
```bash
hermes config show
# Should show:
#   model:
#     default: <your-model>:<tag>
#     provider: ollama
#     base_url: http://localhost:11434/v1
```

### 4. Test the Connection
```bash
hermes chat -q "Hello, which model are you using?"
```
The response should confirm it's using your specified model.

## Common Patterns and Pitfalls

### ❌ Hybrid Configuration (Problematic)
Avoid mixing OpenRouter format model names with localhost base_url:
```yaml
# PROBLEMATIC - causes confusion and potential issues
model:
  default: nvidia/nemotron-3-super-120b-a12b:free  # OpenRouter format
  provider: openrouter
  base_url: http://localhost:11434/v1              # But pointing to Ollama
```
This creates ambiguity about which service is actually being used.

### ✅ Clean Ollama Configuration
```yaml
# CORRECT - clear intent to use Ollama
model:
  default: Zeon7-Gemma:latest
  provider: ollama
  base_url: http://localhost:11434/v1
```

### ✅ Clean OpenRouter Configuration
```yaml
# CORRECT - clear intent to use OpenRouter
model:
  default: anthropic/claude-sonnet-4
  provider: openrouter
  # base_url omitted (uses OpenRouter's default)
```

### Provider-Specific Notes

**Ollama:**
- Use model names as they appear in `ollama list`
- Default base_url is `http://localhost:11434/v1`
- Provider value: `ollama`

**OpenRouter:**
- Use model names in format `provider/model-name:tag`
- Provider value: `openrouter`
- base_url is optional (defaults to OpenRouter's API)

**Other Providers:**
Consult `hermes model --help` for provider-specific options
Use `hermes model` for interactive provider/model selection

## Troubleshooting

### "Only seeing one model in model selector"
If `/model` shows limited options:
1. Verify you're using the correct profile: `hermes profile list`
2. Check that the provider is set correctly: `hermes config show`
3. Ensure the base_url points to the correct service
4. Try `hermes model` for interactive selection (may show more options)

### Connection Issues
- Verify the service is running (`ollama ps` for Ollama)
- Check network connectivity to the base_url
- Confirm API keys are set for cloud providers (use `hermes auth list`)

## Profile-Specific vs Global Configuration

For most users, **profile-specific configuration** is recommended:
```bash
# Configure for specific profile
hermes profile use zeon7
hermes config set model.provider ollama
# ... other settings
```

This keeps configurations isolated between projects or use cases.

Use **global configuration** only when you want the same settings across all profiles:
```bash
# Affects all profiles (use with caution)
hermes config set model.provider ollama --scope global
```
*Note: The `--scope global` flag may not be available in all Hermes versions; check `hermes config set --help`*

## Verification Checklist

After changing provider/model:
- [ ] `hermes config show` reflects intended settings
- [ ] `hermes model` (if interactive) shows correct provider pre-selected
- [ ] Test query returns expected response from intended model
- [ ] No mixed configuration (e.g., OpenRouter model format with Ollama URL)
- [ ] Correct profile is active (check for ◆ in `hermes profile list`)

## Related Commands

- `hermes config show` - View current configuration
- `hermes config set <key> <value>` - Change configuration setting
- `hermes model` - Interactive model/provider selector
- `hermes profile list` - See all profiles and active one
- `hermes profile use <name>` - Set active/sticky profile
- `hermes auth list` - Configured API keys
- `hermes` - Start chat session with current configuration