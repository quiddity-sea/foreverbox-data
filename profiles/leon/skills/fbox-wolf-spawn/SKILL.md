---
name: fbox-wolf-spawn
description: Spawns 1-3 Wolf research workers via the Hermes CLI. Handles provider checking (cloud required unless Merrill overrides), task ID generation, command construction, and background dispatch.
---

# Skill: fbox-wolf-spawn

## Purpose
Spawns Wolf research workers. See full SKILL.md at `/foreverbox_data/Shared_Skills/foreverbox/fbox-wolf-spawn/SKILL.md`.

## Key Pitfall: Shell Scripts vs Native Tools
Wolves (Zeon7-Gemma:64k on Ollama) will try to call `fbox-memory-upsert` as a native tool unless the spawn prompt explicitly uses `terminal()` wrapper syntax. See `references/wolf-tool-confusion.md` for the fix pattern.
