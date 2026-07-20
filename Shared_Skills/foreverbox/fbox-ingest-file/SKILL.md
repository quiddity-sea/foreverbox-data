---
name: fbox-ingest-file
description: "Trigger ingestion and vectorisation of a file dropped into the Quiddity Lore Sea."
version: "1.0"
author: "Leon (Layer 2 Producer)"
license: "MIT"
tags: ["foreverbox", "commons", "quiddity", "ingest", "vectorise"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["commons", "quiddity", "ingest", "vectorise"]
    related_skills: ["fbox-commons-search", "fbox-operations"]
    config: {}
---

# fbox-ingest-file

## Description
Trigger ingestion and vectorisation of a file in the Quiddity Lore Sea. The council-library API handles chunking, embedding, and indexing server-side. Once ingested, the file becomes searchable via `fbox-commons-search`.

## When to Use
- After dropping a new document into the Quiddity Lore Sea
- When you need to make a recently added file searchable
- After updating a previously ingested file and needing to re-index it

## API Endpoint
```
POST /v1/commons/files/sync
```

## Parameters
| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `filename` | Yes | — | Path relative to Quiddity_Lore_Sea root |
| `organise` | No | true | Auto-organise into subfolders |

## Usage

```bash
API_URL=$(jq -r '.api_url' "$HERMES_HOME/foreverbox.json")
API_KEY="$FOREVERBOX_API_KEY"

curl -s -X POST \
  "$API_URL/commons/files/sync" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["{filename}"],
    "organise": true
  }'
```

## Notes
- Ingestion is asynchronous — the file may take a few seconds to appear in `fbox-commons-search` results.
- Currently 15 files ingested (1470 vector references) from the Sea. Newer files like FTN Handbook V5 are not yet indexed.
- Use this skill immediately after creating or updating a document in the Quiddity Lore Sea.
