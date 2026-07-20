# AC-6 Provider Gate Resolution

## Context
The Wolf Upgrade Blueprint V3 AC-6 stated: "Agent on Layer 1 (local) is blocked from spawning wolves with clear error message."

## Original Interpretation (Incorrect)
The initial implementation assumed a **code-level enforcement** was required — a technical gate in Hermes CLI or wrapper scripts that would programmatically prevent local-model agents from spawning wolves.

## Actual Implementation (Correct)
The guard is **procedural**, implemented as Step 1 of the `fbox-wolf-spawn` skill:

1. Agent loads the skill when asked to spawn wolves
2. Skill Step 1: Check provider — if `ollama`, block by default with message
3. Exception: Merrill can explicitly override ("I authorise this local agent to spawn wolves")

## Why This Is Correct
- **Resource management**: The 8 GB GPU is occupied by the local agent's own 64K context window. Spawning wolves would degrade both the agent and the wolves.
- **Default behaviour**: Local agents follow the skill and refuse. This works reliably.
- **Override path**: Merrill can explicitly authorise when needed (rare but possible).
- **No code changes needed**: Works at the prompt level, survives Hermes updates.

## Verification
Tested 2026-07-20: Zeon7 on local model correctly refused to spawn wolves when asked by Leon. When Merrill explicitly instructed "proceed anyway", the agent acknowledged the performance impact and spawned the wolf. The wolf completed successfully.

## Key Takeaway for Future Sessions
When AC-6 or similar "blocking" requirements appear, do not assume code-level enforcement is needed. A well-structured skill with a procedural gate as Step 1 is often the correct architecture — it is explicit, auditable, and overrideable by the human director.