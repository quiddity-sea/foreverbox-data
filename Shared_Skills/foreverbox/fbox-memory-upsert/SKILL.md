---
name: fbox-memory-upsert
description: "Create or update a memory entry in any Sanctum namespace via the Council Library API."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "memory", "sanctum", "upsert"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["memory", "sanctum", "upsert"]
    related_skills: ["fbox-memory-search", "fbox-memory-get", "fbox-operations"]
    config: {}
---

# fbox-memory-upsert

## Description
Create or update a memory entry in the Council Library Sanctum. Writes to any namespace — `wolf_tasks`, `memory`, or custom namespaces. The council-library handles the upsert (insert or update) server-side.

## When to Use
- Writing wolf research findings to the Sanctum
- Saving an agent's own working notes to a custom namespace
- Storing structured data that needs to persist across sessions
- Appending new Story Lead Cards or research notes

## API Endpoint
```
PUT /v1/sanctum/memory/{namespace}/{key_name}
```

## Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `namespace` | Yes | — | Sanctum namespace (e.g. `wolf_tasks`, `memory`) |
| `key_name` | Yes | — | Unique key for this entry (e.g. `lead_search_20260718`) |
| `content` | Yes | — | The memory content as a string |
| `importance` | No | 70 | Integer 1-100, higher = more likely to be surfaced |
| `source_type` | No | `wolf_synthesis` | One of: `user_directive`, `session_extraction`, `document_ingestion`, `wolf_synthesis` |

## Usage

Load the skill and call it:

```
Load fbox-memory-upsert, then upsert namespace=wolf_tasks, key=lead_search_20260718, content="Findings: ...", importance=70
```

Or run the curl command directly via terminal:

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s -X PUT \
  "$API_URL/sanctum/memory/{namespace}/{key_name}" \
  -H "Authorization: Bearer $API_KEY" \
  -H "X-Agent-ID: wolf" \
  -H "Content-Type: application/json" \
  -d '{
    "namespace": "{namespace}",
    "key_name": "{key_name}",
    "content": "{content}",
    "importance": 70,
    "source_type": "wolf_synthesis"
  }'
```

## Verification
After upserting, verify with `fbox-memory-get` or `fbox-memory-search`.

## Notes
- The key_name must be unique within its namespace. Reusing a key_name overwrites the existing entry.
- Content can be plain text or structured markdown — the API stores it as-is.
- The `source_type` field is used for analytics and filtering.
