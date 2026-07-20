---
name: fbox-memory-list
description: "List all memory entries in a Sanctum namespace, optionally filtered."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "memory", "sanctum", "list"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["memory", "sanctum", "list"]
    related_skills: ["fbox-memory-search", "fbox-memory-upsert", "fbox-operations"]
    config: {}
---

# fbox-memory-list

## Description
List memory entries in a Sanctum namespace. Optionally filter by tags or minimum importance.

## When to Use
- Checking all pending wolf tasks
- Auditing what's stored in a namespace
- Finding entries by tag rather than content search

## API Endpoint
```
GET /v1/sanctum/memory?namespace={namespace}&tags={tag1,tag2}&importance_min={n}&limit={n}
```

## Usage

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s "$API_URL/sanctum/memory?namespace={namespace}&limit=20" \
  -H "Authorization: Bearer $API_KEY"
```

## Notes
- Results include `namespace`, `key_name`, `content_text` (truncated), `tags`, `importance`, and `created_at`.
- Use `fbox-memory-get` to retrieve full content of a specific entry.
