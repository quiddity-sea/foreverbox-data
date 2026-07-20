---
name: fbox-memory-delete
description: "Delete a memory entry from the Council Library Sanctum. Irreversible."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "memory", "sanctum", "delete"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["memory", "sanctum", "delete"]
    related_skills: ["fbox-memory-list", "fbox-memory-search", "fbox-operations"]
    config: {}
---

# fbox-memory-delete

## Description
Delete a single memory entry by namespace and key. **Irreversible** — confirm with the user before executing.

## When to Use
- Cleaning up completed wolf task entries
- Removing outdated or incorrect memories
- Clearing test data

## API Endpoint
```
DELETE /v1/sanctum/memory/{namespace}/{key_name}
```

## Usage

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s -X DELETE \
  "$API_URL/sanctum/memory/{namespace}/{key_name}" \
  -H "Authorization: Bearer $API_KEY"
```

## Warning
This operation is irreversible. Always confirm with the Human Director before deleting production data. Use `fbox-memory-list` first to verify what will be deleted.
