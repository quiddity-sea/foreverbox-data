---
name: fbox-commons-search
description: "Semantic vector search over the Quiddity Lore Sea shared knowledge base."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "commons", "quiddity", "search", "vector"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["commons", "quiddity", "search", "vector"]
    related_skills: ["fbox-ingest-file", "fbox-memory-search", "fbox-operations"]
    config: {}
---

# fbox-commons-search

## Description
Semantic vector search over the Quiddity Lore Sea — the Foreverbox shared knowledge base. Searches ingested files, archived documents, blueprints, and handbooks. Returns ranked results with content snippets and source file paths.

## When to Use
- Looking up Foreverbox architecture, protocols, or blueprints
- Searching the handbook collection for a specific rule or procedure
- Finding which documents discuss a given topic
- Cross-referencing knowledge stored in the Sea

## API Endpoint
```
GET /v1/commons/search?query={query}&limit={n}
```

## Usage

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s "$API_URL/commons/search?query={search terms}&limit=10" \
  -H "Authorization: Bearer $API_KEY"
```

## Notes
- The Quiddity Lore Sea contains agent handbooks, blueprints, Master Briefings, and other Foreverbox documentation.
- Results include source file paths — use these to locate the original document.
- Useless if files haven't been ingested yet — run `fbox-ingest-file` first.
