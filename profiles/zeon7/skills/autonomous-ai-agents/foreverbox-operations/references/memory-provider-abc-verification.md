# Hermes MemoryProvider ABC Verification

When the Architecture Blueprint defines a Hermes `MemoryProvider` subclass (currently §6.4),
the class spec must match the actual `MemoryProvider` ABC from `agent/memory_provider.py`.
The blueprint is a spec document, not a tested codebase — spec bugs survive until someone
compares against the real interface.

## Source of Truth

The ABC lives at:
```
https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/memory_provider.py
```

A real-world provider implementation (for reference):
```
https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/honcho/__init__.py
```

## Verification Checklist

For each method in the blueprint's provider class, verify:

| Check | What to look for |
|-------|-----------------|
| **Return type** | Does it match the ABC? `prefetch()` returns `str`, not `list`. `handle_tool_call()` returns JSON `str`. |
| **Signature params** | Does every method accept all kwargs the ABC declares? `prefetch()` has `*, session_id: str = ""`. `sync_turn()` has `*, session_id, messages`. Missing kwargs → `TypeError` at runtime. |
| **Required methods** | `name`, `is_available()`, `initialize()`, `get_tool_schemas()`, `shutdown()` — all `@abstractmethod`, all must exist. |
| **Tool schemas** | Are they complete JSON dicts with `name`, `description`, `parameters`? Stubs (`...`) will not activate. |
| **Optional hooks** | `system_prompt_block()`, `queue_prefetch()`, `on_memory_write()`, `on_pre_compress()`, `on_session_end()`, `on_session_switch()`, `on_delegation()`, `backup_paths()` — not required, but absence means silent no-ops. |
| **Config methods** | `get_config_schema()` and `save_config()` exist on the ABC. The blueprint uses them — confirmed they are real. |

## Bugs Found in Blueprint V2.0 §6.4 (Fixed in V2.1)

1. **`prefetch()` returned `list`** — ABC expects `str`. Would inject `[...]` as literal text into system prompt.
2. **`prefetch()` missing `session_id`** — ABC signature is `prefetch(self, query, *, session_id="")`. Blueprint had `prefetch(self, query)`. Would raise `TypeError`.
3. **`get_tool_schemas()` was a stub** — `...` where 9 complete JSON tool schemas should be.
4. **`handle_tool_call()` was a stub** — `...` where a route_map dispatching to PHP endpoints should be.
5. **Missing `system_prompt_block()`** — falls back to `""`, not critical but loses the opportunity to orient the agent.
6. **Missing `queue_prefetch()`** — falls back to no-op, not critical but newer Hermes versions expect it.

## Procedure

```bash
# Pull the ABC
curl -sL "https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/memory_provider.py"

# Pull a reference implementation
curl -sL "https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/honcho/__init__.py" | head -200
```

Then compare method-by-method against the blueprint's provider class. Flag any return type mismatch, signature mismatch, or stub where a complete implementation is needed.
