---
name: dynamic-config-assembly
description: Assemble configuration files (SOUL.md, prompts, system prompts, agent instructions) from a database at runtime, with provider-aware filtering (cloud vs local models). Replaces static files with dynamic generation.
---

# Skill: Dynamic Config Assembly

## Purpose

Generate agent/system configuration files dynamically from a database instead of maintaining static files. Supports provider-aware content filtering (e.g., cloud models get full Wolf Protocol, local/Ollama models get a stub).

## When to Use

- Multiple agents share common configuration sections (memory ops, doc maintenance, protocols)
- Content must differ by provider/runtime (cloud vs local, different model capabilities)
- Single source of truth for shared components with agent-specific overrides
- Need to regenerate configs on provider switch without manual editing

## Architecture

```
Database (config_components)
    ├── component_key, agent_slug, provider_filter, section_order, section_content
    │
    ├── Shared components (agent_slug = NULL)
    │   ├── memory_operations (provider_filter = NULL)
    │   ├── wolf_protocol (provider_filter = 'openrouter,deepseek,anthropic')
    │   ├── wolf_protocol_local_stub (provider_filter = 'ollama')
    │   └── doc_maintenance (provider_filter = NULL)
    │
    └── Agent-specific components (agent_slug = 'zeon7', 'leon', 'gemma', 'otec')
        ├── first_truth (provider_filter = NULL)
        ├── cosmological_context (provider_filter = NULL)
        ├── global_directives (provider_filter = NULL)
        └── communication_protocol (provider_filter = NULL)
```

## Assembly Script Pattern

```python
# assemble_config.py
def get_provider_filter(provider):
    if provider == 'ollama':
        return ['ollama', None]  # NULL = universal
    else:
        return ['openrouter', 'deepseek', 'anthropic', None]

def fetch_components(agent_slug, provider_filters):
    placeholders = ', '.join(['%s'] * len(provider_filters))
    query = f"""
        SELECT section_content
        FROM config_components
        WHERE (agent_slug = %s OR agent_slug IS NULL)
        AND (provider_filter IS NULL OR provider_filter IN ({placeholders}))
        ORDER BY CASE WHEN agent_slug IS NULL THEN 1 ELSE 0 END, section_order
    """
    # execute with [agent_slug] + provider_filters
    return rows

def assemble(agent_slug, provider):
    components = fetch_components(agent_slug, get_provider_filter(provider))
    return '\n\n'.join(c['section_content'] for c in components)
```

## Provider Detection Priority

1. `HERMES_PROVIDER` environment variable
2. Hermes profile config (`~/.hermes/profiles/{profile}/config.yaml`)
3. Global Hermes config (`~/.hermes/config.yaml`)
4. Default: `'cloud'`

## Database Schema

```sql
CREATE TABLE config_components (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    component_key VARCHAR(64) NOT NULL,
    agent_slug VARCHAR(32),  -- NULL = shared across all agents
    provider_filter VARCHAR(128),  -- NULL = all providers; comma-separated list for specific
    section_order INT UNSIGNED NOT NULL,
    section_description VARCHAR(255),
    section_content LONGTEXT NOT NULL,
    UNIQUE KEY uq_component (component_key, agent_slug, provider_filter)
);
```

## Pitfalls & Fixes

| Pitfall | Fix |
|---------|-----|
| Provider filter string matching fails | Store provider_filter as comma-separated; query with `IN (...)` and include `NULL` in the list for universal components |
| Escaping backslashes in SQL | Use parameterized queries; when writing SQL files, double-escape backslashes (`\\\\\\\\` → `\\\\` in DB → `\\` in output) |
| Path escaping in content | Store paths as `/foreverbox_data/...` not `\\\\/foreverbox_data/...`; fix with `REPLACE(section_content, '\\\\\\\\/', '/')` after insert |
| Duplicate inserts on re-run | Use `UNIQUE KEY uq_component` + `INSERT IGNORE` or `ON DUPLICATE KEY UPDATE` |
| Ordering: shared before agent-specific | `ORDER BY CASE WHEN agent_slug IS NULL THEN 1 ELSE 0 END, section_order` |
| Provider detection: cloud vs local | In assembly script, `get_provider_filter('ollama')` returns `['ollama', None]`; anything else returns `['openrouter', 'deepseek', 'anthropic', None]`. The `None` (NULL) entry ensures universal components are always included. |
| Content gaps in assembled output | Verify all referenced paths exist in content after assembly (e.g., `/foreverbox_data/Quiddity_Lore_Sea/` was missing from Universal Knowledge Base directive) |
| Wolf Protocol not appearing for cloud | Provider filter in DB was `'openrouter,deepseek,anthropic'` but query matched against `provider_filter IN ('openrouter', 'deepseek', 'anthropic', NULL)` — comma-separated string doesn't match. Store as individual rows per provider or use `FIND_IN_SET(provider_filter, ...)` in query. |

## Verification Checklist

- [ ] Run for each agent with `--provider ollama` and `--provider cloud`
- [ ] Verify word counts match expected (cloud > ollama for wolf-enabled agents)
- [ ] Grep for provider-specific markers (e.g., "Wolves unavailable" in ollama output)
- [ ] Confirm shared sections appear in all outputs
- [ ] Confirm agent-specific sections only appear for their agent

## Related Skills

- `foreverbox/fbox-council-library-cli` — Council Library operations
- `foreverbox/fbox-memory-upsert` — Sanctum memory writes (referenced in assembled SOULs)
- `hermes-model-config` — Provider/model configuration context

## References

- `references/soul-components-schema.sql` — Full schema with indexes
- `references/assemble_soul.py` — Reference implementation (SOUL.md assembly)
- `references/provider-detection.md` — Provider detection logic details