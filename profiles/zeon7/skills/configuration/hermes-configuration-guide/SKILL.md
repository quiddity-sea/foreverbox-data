---
name: hermes-configuration-guide
description: "Guide to understanding Hermes configuration precedence, profiles, and troubleshooting"
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Configuration Guide

## Configuration Hierarchy

Hermes uses a layered configuration system where settings can be defined at multiple levels. Understanding this hierarchy is key to troubleshooting configuration issues.

### 1. Global Configuration (Applies to all profiles unless overridden)
- **Location**: `~/.hermes/config.yaml` (or `$HERMES_HOME/.hermes/config.yaml` if `HERMES_HOME` is set)
- **Purpose**: Default settings for all profiles
- **Contains**: Default model/provider settings, display preferences, tool configurations, etc.
- **File example**:
  ```yaml
  model:
    default: anthropic/claude-sonnet-4
    provider: openrouter
  display:
    skin: default
    reasoning: medium
  ```

### 2. Profile-Specific Configuration (Overrides global settings for that profile)
- **Location**: `~/.hermes/profiles/<profile-name>/config.yaml`
- **Purpose**: Settings specific to a named profile
- **Precedence**: Overrides global configuration settings
- **File example** (from your zeon7 profile):
  ```yaml
  model:
    default: Zeon7-Gemma:latest
    provider: ollama
    base_url: http://localhost:11434/v1
  custom_providers:
    - name: g4
      base_url: http://localhost:11434/v1
      model: fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:e2b-SCN
  ```

### 3. Runtime Overrides (Temporary, highest priority)
- **Command-line flags**: `--model`, `--provider`, `--profile`, etc.
- **Environment variables**: Can override specific settings
- **Session commands**: `/model`, `/profile`, etc. during an active session

## How the Model Selector Works

When you run `/model` or `hermes model`:
1. The **default model/provider** from your *active profile's config* is shown as the primary option
2. Each entry in the `custom_providers` array appears as an additional selectable option
3. Selecting an option temporarily overrides your profile's default for that session
4. The selection does NOT permanently change your profile's configuration

## Common Configuration Issues & Solutions

### Issue: "I don't see my expected model in the model selector"
**Possible causes:**
- You're looking at custom providers but missing the default option (it's usually listed first)
- Your profile's config is being overridden by global settings
- You're accidentally using a different profile than intended
- The model name doesn't match what's actually available at the endpoint

**Diagnosis steps:**
1. Check which profile is active: `hermes profile list` (look for ◆ indicator)
2. Verify your profile's config: `hermes config show` (check the file path in the output)
3. Confirm the model exists at your endpoint: `curl -s http://localhost:11434/api/tags`
4. Check if you're seeing the default option or only custom providers

### Issue: "My settings aren't taking effect"
**Possible causes:**
- Editing the wrong config file (global vs profile-specific)
- A higher-priority override is active (command-line flag, environment variable, session command)
- The Hermes process needs to be restarted after config changes

**Solution:**
- Always verify you're editing the correct file: check the path shown in `hermes config show`
- Restart Hermes after making configuration changes
- Check for conflicting environment variables or command-line aliases

## Profile Management Commands

- `hermes profile list` - Shows all profiles with active indicators
- `hermes profile use <name>` - Sets sticky default profile
- `hermes profile show <name>` - Displays profile details (including config path)
- `hermes --profile <name> <command>` - Runs a command using a specific profile

## Environment Variables That Affect Configuration

- `HERMES_HOME`: Changes the base directory for all Hermes data (config, sessions, etc.)
- `HERMES_PROFILE`: Sets the default profile to use
- Provider-specific API key variables (e.g., `OPENROUTER_API_KEY`, `OLLAMA_API_KEY`)

## Best Practices

1. **Use profiles for different environments** - Keep development, testing, and production configurations separate
2. **Keep global config minimal** - Put truly universal settings in global, profile-specific in profile configs
3. **Verify active configuration** - Always check `hermes config show` to confirm which file is being read
4. **Document custom providers** - Use descriptive names in `custom_providers` for easy identification in the selector
5. **Restart after changes** - Configuration changes require a restart to take effect

## Troubleshooting Workflow

When configuration isn't behaving as expected:
1. `hermes profile list` → Confirm which profile is active
2. `hermes config show` → Note the config file path being used
3. `hermes model` → Check what options appear in the selector
4. Verify the actual endpoint: `curl -s <base_url>/api/tags`
5. Check for overrides: Review shell aliases, environment variables, command history
6. Restart Hermes and test again

## Your Specific Situation (Based on Conversation)

From our discussion, your **zeon7 profile** appears to be configured correctly:
- Config file: `/foreverbox_data/profiles/zeon7/config.yaml`
- Model: `Zeon7-Gemma:latest`
- Provider: `ollama`
- Base URL: `http://localhost:11434/v1`
- Custom provider defined for the fredrezones55 model

If you're only seeing the fredrezones55 model in the selector, it's likely that:
- The zeon7-Gemma model is the default option (appearing first or labeled differently)
- There may be a display or sorting issue in the model selector UI
- Verify by checking if `Zeon7-Gemma:latest` appears in your Ollama model list

Remember: The model selector shows your profile's default PLUS any custom providers. Your zeon7-Gemma model should be visible as the primary/default option.