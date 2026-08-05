---
name: dynamic-soul-variant-pattern
description: "Worked example: Zeon7 Coder variant via the NOT EXISTS SQL pattern for provider-scoped SOUL assembly."
version: 1.0.0
author: Leon (Layer 2 Producer)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [foreverbox, soul-assembly, dynamic-soul, variant-provider]
    related_skills: [fbox-operations]
---

# Dynamic SOUL Variant Pattern — Zeon7 Coder Worked Example

## What We Built

The Zeon7 Coder variant is a provider-scoped SOUL that replaces FTN-oriented sections with coding directives while keeping Zeon7's core identity, cosmology, and communications protocols intact.

## Architecture

The `soul_components` table at `agent_registry` stores modular SOUL sections. Each row has:

- component_key: section name (e.g. first_truth, communication_protocol, memory_operations)
- agent_slug: which agent this applies to, or NULL for all agents
- provider_filter: which provider this applies to, or NULL for all providers
- section_content: the markdown body of the section

## The NOT EXISTS Pattern

When a provider-specific variant exists, the query must exclude the shared (NULL) fallback for that component to avoid duplicates. The correlated subquery checks: "is there a variant-specific row for this same component_key and agent_slug?" If yes, the shared fallback is excluded.

## get_provider_filter() Function

```python
def get_provider_filter(provider):
    if provider == 'ollama':
        return ['ollama', None]
    elif provider == 'coder':
        return ['coder', None]
    else:
        return ['cloud', 'openrouter', 'deepseek', 'anthropic', None]
```

The first element is the "current filter" for the NOT EXISTS check.

## SQL Insert for Variant Components

INSERT rows with provider_filter = 'variant_name'. Agent-specific overrides use agent_slug, shared overrides (any agent) use agent_slug = NULL.

## Pitfalls Encountered

### Duplicate Sections
If the variant's first_truth includes an embedded section that also exists as a standalone component, the assembled SOUL will have that section twice. Fix: remove the embedded section and let the standalone component handle it.

### Em-dash Prohibition
The user bans em-dashes in Foreverbox content. Use hyphens, commas, or parentheses. Check section_descriptions after inserting rows.

### Double Insertion from Two SQL Paths
If you run inline SQL and file-based SQL, you get duplicates. Delete by ID.

### Hermes Config Duplicates from config set
hermes config set writes to config root level. If a model.context_length already exists in the model: section, you get both. Verify with grep and unset the root-level duplicate.

## Verification

Assemble: python3 /foreverbox_data/bin/assemble_soul.py zeon7 coder
Check for coder-specific content: grep for "CODING FOCUS" or "No FTN".
Verify no bleed into default: assemble with zeon7 only and confirm zero coder markers.
