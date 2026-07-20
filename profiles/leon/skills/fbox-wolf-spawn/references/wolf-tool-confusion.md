# Wolf Tool Confusion: Shell Scripts vs Native Tools

## Problem
The Wolf (Zeon7-Gemma:64k on Ollama) tries to call `fbox-memory-upsert` as a native Hermes tool instead of a shell script via `terminal()`. This produces:
```
Unknown tool 'fbox-memory-upsert' — sending error to model for agent-correction
```
With 3 retries before the wolf gives up and fails the task.

## Root Cause
The Wolf SOUL.md TOOLS section listed script names without `terminal()` wrapper syntax. The model sees `fbox-memory-upsert` and assumes it's a registered tool.

## Fix
Rewrite the TOOLS section in `/foreverbox_data/profiles/wolf/SOUL.md` to:
1. Explicitly state these are NOT tools
2. Show the `terminal()` wrapper  
3. Add a CRITICAL warning at the end

## Spawn Task Prompt Format
When spawning a wolf, the task prompt must include the full `terminal:` wrapper syntax:
```
hermes chat --profile wolf -q "Research task. Task ID: {id}. {query}. Write findings to Sanctum via terminal: /foreverbox_data/bin/fbox-memory-upsert wolf_tasks {id} \"{findings}\"." -m Zeon7-Gemma:64k --provider ollama --source wolf
```
NOT the short form `via fbox-memory-upsert` — this will cause the wolf to attempt a non-existent tool call and fail.
