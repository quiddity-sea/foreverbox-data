# Two Wolf Protocols — Research vs Forever Fit

There are **two distinct "Wolf Protocol" concepts** in the Foreverbox ecosystem.
They share the name but are completely different systems. Confusing them
will lead to incorrect architectural claims.

## 1. Research Wolf System (Live — Stage 1 Complete)

**Skill:** `fbox-wolf-spawn` (this skill)
**Profile:** `wolf` (Zeon7-Gemma:64k on Ollama, 3.8 GB)
**Spawn:** Ad-hoc via `hermes chat --profile wolf` on terminal(background=True)
**Purpose:** Background research — web search, source verification, parallel fact-finding
**Layer 1 Guard:** Local agents block by default (GPU occupied). Cloud agents allowed.
  Merrill can override.
**Task Dispatch:** `agent_registry.task_queue` with `FOR UPDATE SKIP LOCKED` atomic claim
**Results:** Written to `agent_wolf` Sanctum via shell wrappers at `/foreverbox_data/bin/`
**Concurrency:** Up to 3 wolves sharing one Ollama model load (~7.4 GB on 8 GB GPU)
**Status:** Built, verified, and live. Referenced in all 4 SOUL.md files.

## 2. Forever Fit Wolf Protocol (Not Yet Built)

**Location in old spec:** `history/the-project/part5-the-workflows.html`
  section 19.1 (under Forever Fit)
**Purpose:** Gamification system for the Forever Fit health platform:
  - **The Hunt** — tracking health goals like a pack hunt
  - **Den Integrity** — maintaining personal health commitments
  - **The Pack is Moving** — social accountability mechanics
**AI Context:** Part of the Forever Fit platform, not a research worker system.
  Would use The Wolf (Zeon7's voice) as one of two AI coach personas.
**Status:** Not built. Conceptually designed in the old spec but not documented
  in any current system. Gemma is the Forever Fit lead in her SOUL.md but
  no code, endpoints, or database schema exist for the platform.
**Future:** Will be added to the Quiddity Lore Sea as documentation when the
  Forever Fit project begins implementation.

## Key Distinction

| Aspect | Research Wolf | Forever Fit Wolf |
|--------|---------------|-------------------|
| System | Hermes agent profile | Gamification framework |
| Implementation | Live (July 2026) | Not yet built |
| Creator | Built from scratch for Hermes ecosystem | Described in pre-blueprint spec |
| Relation to old spec | Did not exist in old spec | Existed in old spec §19.1 |
| Wolf name meaning | Research worker | Pack/gamification metaphor |
