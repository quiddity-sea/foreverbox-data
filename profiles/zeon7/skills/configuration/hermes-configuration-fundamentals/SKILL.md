---
name: hermes-configuration-fundamentals
description: Understand Hermes configuration system, profiles, and environment variables
version: 1.0.0
author: zeon7
license: MIT
---

# Hermes Configuration Fundamentals

Guide to understanding Hermes' configuration system, including profiles, environment variables, and file locations.

## When to Use This Skill

Use this skill when you need to:
- Understand where Hermes stores configuration and data
- Configure HERMES_ENVIRONMENT or HERMES_HOME
- Manage profiles (list, switch, set default)
- Troubleshoot configuration loading issues
- Understand the configuration precedence hierarchy

## Core Concepts

### 1. Configuration Hierarchy

Hermes uses a layered configuration system:
```
Global Config (lowest priority)
    ↓
Profile Config (overrides global)
    ↓
Session/Runtime Overrides (highest priority)
```

### 2. Environment Variables

Key environment variables that affect Hermes behavior:

| Variable | Purpose | Example |
|----------|---------|---------|
| `HERMES_HOME` | Base directory for all Hermes data | `/my/custom/path` |
| `HERMES_PROFILE` | Default profile to use | `zeon7` |
| `HERMES_DEBUG` | Enable debug logging | `true` |

**Important**: When `HERMES_HOME` is set, **all** Hermes data (config, sessions, skills, etc.) is stored under this path instead of the default `~/.hermes/`.

### 3. Profiles

Profiles provide isolated configurations for different use cases. Each profile has its own:
- Configuration file (`config.yaml`)
- Encrypted credentials (`auth.json`)
- Session history
- Skills and memory
- Cache directories

## File Locations

### When HERMES_HOME is NOT set (default):
- Config: `~/.hermes/config.yaml`
- Secrets: `~/.hermes/.env`
- Profiles: `~/.hermes/profiles/<profile_name>/`
- Sessions: `~/.hermes/sessions/`
- Skills: `~/.hermes/skills/`
- Logs: `~/.hermes/logs/`
- etc.

### When HERMES_HOME IS set (e.g., `HERMES_HOME=/my/path`):
- Config: `/my/path/config.yaml`
- Secrets: `/my/path/.env`
- Profiles: `/my/path/profiles/<profile_name>/`
- Sessions: `/my/path/sessions/`
- Skills: `/my/path/skills/`
- Logs: `/my/path/logs/`
- etc.

## Working with Profiles

### List Profiles
```bash
hermes profile list
```
Output shows:
- Profile name
- Current model/gateway status
- Alias (if set)
- Distribution type
- **◆** indicates the active/sticky profile

### Set Default/Sticky Profile
```bash
hermes profile use <profile-name>
```
This sets the profile that will be used by default when no `-p` flag is specified.
The ◆ marker in `hermes profile list` shows which profile is currently sticky.

### Create Profile
```bash
# Create new profile
hermes profile create <name>

# Create as copy of existing profile
hermes profile create <name> --clone <source-profile>

# Create empty profile
hermes profile create <name> --empty
```

### Delete Profile
```bash
hermes profile delete <profile-name>
```
*Note: Cannot delete the currently active profile*

### Show Profile Details
```bash
hermes profile show <profile-name>
```
Displays full configuration for the specified profile.

## Configuration Files Explained

### config.yaml
Contains non-secret configuration:
```yaml
model:
  default: <model-name>
  provider: <provider-name>
  base_url: <optional-base-url>

display:
  skin: <theme-name>
  reasoning: <level>

terminal:
  timeout: <seconds>

# ... other sections
```

### .env (or auth.json)
Secrets are stored in encrypted format:
- Older versions: `.env` file (plaintext - not recommended)
- Current versions: `auth.json` (encrypted credential store)

Manage secrets with:
```bash
hermes auth list          # View configured providers
hermes auth add <provider> # Add credentials for provider
hermes auth remove <provider> <index> # Remove credentials
```

## Configuration Precedence

When resolving a configuration value, Hermes checks in this order:
1. **Command-line flags** (e.g., `hermes -m <model>`)
2. **Session/runtime overrides** (set during session)
3. **Profile-specific config** (`$HERMES_HOME/profiles/<active>/config.yaml`)
4. **Global config** (`$HERMES_HOME/config.yaml`)
5. **Built-in defaults**

## Common Scenarios and Solutions

### Scenario: "Where is my config file?"
If you've set `HERMES_HOME`:
```bash
echo $HERMES_HOME  # Shows your custom path
hermes config path # Shows exact config.yaml location
```

### Scenario: "My changes aren't taking effect"
1. Verify you're editing the correct profile's config:
   ```bash
   hermes profile list  # Check which has ◆
   hermes -p <profile> config path
   ```
2. Remember that profile config overrides global config
3. Restart Hermes after config changes (they're loaded on startup)

### Scenario: "I want to use different models for different projects"
1. Create separate profiles:
   ```bash
   hermes profile create project-a --clone zeon7
   hermes profile create project-b --clone zeon7
   ```
2. Configure each profile differently:
   ```bash
   hermes profile use project-a
   hermes config set model.provider ollama
   hermes config set model.default model-a:latest
   
   hermes profile use project-b
   hermes config set model.provider openrouter
   hermes config set model.default anthropic/claude-3-opus
   ```
3. Switch between projects:
   ```bash
   hermes -p project-a  # Uses project-a's config
   hermes -p project-b  # Uses project-b's config
   ```

### Scenario: "After setting HERMES_HOME, I see empty directories in ~/.hermes/"
This is normal. The `~/.hermes/` directory may contain:
- Legacy data from before HERMES_HOME was set
- Empty directory structure created by Hermes on first run
- **Solution**: You can safely remove or ignore `~/.hermes/` contents if HERMES_HOME is properly set and your data is appearing in the correct location.

## Verification Checklist

After configuring HERMES_HOME or profiles:
- [ ] `echo $HERMES_HOME` shows expected path (if set)
- [ ] `hermes --version` runs without path errors
- [ ] `hermes profile list` shows profiles in expected location
- [ ] `hermes config path` points to expected config.yaml
- [ ] `hermes config show` reflects your intended settings
- [ ] New sessions create data in `$HERMES_HOME/` not `~/.hermes/`
- [ ] The active profile shows ◆ in `hermes profile list`

## Related Commands

- `hermes config show` - View effective configuration
- `hermes config path` - Show config.yaml location
- `hermes config env-path` - Show .env/auth.json location
- `hermes profile list` - List all profiles with active marker
- `hermes profile use <name>` - Set default/sticky profile
- `hermes profile show <name>` - View profile details
- `hermes model` - Interactive model/provider selector
- `hermes auth list` - View configured API keys
- `hermes` - Start chat session (uses active profile)
- `hermes -p <name>` - Start chat with specific profile
- `hermes --resume <session-id>` - Resume specific session