---
name: fbox-memory-get
description: "Retrieve a single memory entry by namespace and key from the Council Library Sanctum."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "memory", "sanctum", "retrieve"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["memory", "sanctum", "retrieve"]
    related_skills: ["fbox-memory-search", "fbox-memory-upsert", "fbox-operations"]
    config: {}
---

# fbox-memory-get

## Description
Retrieve a single memory entry by its namespace and key. Returns the full content, metadata, and timestamps.

## When to Use
- Checking if a specific wolf task completed (`{task_id}:done`)
- Retrieving the full content of a known memory entry
- Verifying a memory write was successful

## API Endpoint
```
GET /v1/sanctum/memory/{namespace}/{key_name}
```

## Usage

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s "$API_URL/sanctum/memory/{namespace}/{key_name}" \
  -H "Authorization: Bearer $API_KEY"
```

## Notes
- Returns `namespace`, `key_name`, `content_text` (full), `tags`, `importance`, `source_type`, `created_at`, `updated_at`.
- Returns 404 if the entry doesn't exist — the skill should handle this gracefully.
