---
name: fbox-wolf-spawn
description: Spawns 1-3 Wolf research workers via the Hermes CLI. Handles provider checking (cloud required unless Merrill overrides), task ID generation, command construction, and background dispatch.
---

# Skill: fbox-wolf-spawn

## Purpose
Spawns Wolf research workers. See full SKILL.md at `/foreverbox_data/Shared_Skills/foreverbox/fbox-wolf-spawn/SKILL.md`.

## Key Pitfall: Shell Scripts vs Native Tools
**Resource rationale:** The 8 GB GPU runs one model at full 64K context. Three concurrent wolves need ~7.4 GB (3.8 GB model + 3 × 1.2 GB KV). Local agents block wolves by default because spawning would split VRAM between agent and wolves, degrading both. The guard is a resource management rule, not a security block. Merrill can override when he accepts the trade-off.
