---
name: fbox-memory-search
description: "Search memories across any Sanctum namespace via the Council Library API."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "memory", "sanctum", "search"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["memory", "sanctum", "search"]
    related_skills: ["fbox-memory-upsert", "fbox-memory-get", "fbox-operations"]
    config: {}
---

# fbox-memory-search

## Description
Hybrid full-text + vector search over the Sanctum memory store. Returns ranked results with namespace, key, content preview, and relevance score.

## When to Use
- Retrieving wolf research results by topic
- Searching for past decisions, facts, or notes
- Finding all entries related to a theme or query
- Checking if a topic has been researched before

## API Endpoint
```
POST /v1/sanctum/memory/search
```

## Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `query` | Yes | — | Natural-language search query |
| `namespace` | No | — | Optional filter to a specific namespace |
| `limit` | No | 10 | Maximum results to return |

## Usage

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s -X POST \
  "$API_URL/sanctum/memory/search" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{search terms}",
    "namespace": "{optional namespace filter}",
    "limit": 10
  }'
```

## Notes
- Results include `namespace`, `key_name`, `content_text` (truncated), and `relevance` score.
- Searching without a namespace filter searches across all Sanctum content the agent has access to.
