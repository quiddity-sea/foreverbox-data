# Dispatch Method Limitations

> Added 2026-07-23 after Zeon7 Coder local dispatch session

## One-shot (-z)
- Works for text generation. Model responds.
- Does NOT register tools. Hermes sends plain text without `tools` array. Model generates text describing actions but never executes them.
- Use only for quick checks, not autonomous task execution.

## Interactive PTY (`--cli chat`)
- Hangs with local Ollama providers. Shows "⏲ 0s" indefinitely.
- May be caused by cognitive_router hooks, gateway conflicts, or plugin overhead.
- Try with `--safe-mode --ignore-rules --ignore-user-config` to strip overhead. Even then, may hang.
- Not suitable for autonomous task dispatch.

## delegate_task
- Always inherits the PARENT model, not the target profile's model. If the parent is on DeepSeek API, the subagent runs on DeepSeek, not local qwen.
- Do NOT use when the goal is to run a task on a local GPU model.

## DeepSeek Context
- Set to 1M: `hermes config set model.context_length 1048576`
- Check for duplicates after setting: `grep -n "context_length" <profile>/config.yaml`
- Unset root-level duplicates: `hermes config unset context_length`
