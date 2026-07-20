---
name: fbox-ingestion-pipeline
description: "Operate and troubleshoot the Quiddity Lore Sea ingestion pipeline: file registration, embedding generation, vector verification, and deadlock recovery."
version: "1.0"
author: "Leon (Layer 2 Producer)"
tags: ["foreverbox", "ingestion", "embedding", "vector", "pipeline"]
metadata:
  hermes:
    category: "foreverbox"
    tags: ["ingestion", "embedding", "vector", "pipeline"]
    related_skills: ["fbox-ingest-file", "fbox-lore-sea-management", "fbox-commons-search"]
---

# fbox-ingestion-pipeline

## Purpose
Operate and troubleshoot the full Quiddity Lore Sea ingestion pipeline: from file registration through embedding generation to vector verification. This skill covers the complete lifecycle and the common failure modes encountered during ingestion.

## Architecture
```
File in Sea -> sync API (register) -> ingestion_worker.php -> embedding_service.py (:8900) -> MariaDB vectors
```

- **Embedding Service**: `/foreverbox_data/council-library/scripts/embedding_service.py` on port 8900
- **Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Worker**: `/foreverbox_data/council-library/scripts/ingestion_worker.php`
- **API**: `http://localhost:8080/v1` (Council Library PHP API)
- **DB**: MariaDB `quiddity_commons` database

## The Two-Step Ingestion Process

### Step 1: Register the file via sync API
The sync endpoint ONLY creates a database entry with `indexing_status='pending'`. It does NOT create vectors.

```bash
curl -s -X POST "http://localhost:8080/v1/commons/files/sync" \
  -H "Authorization: Bearer dev-key-change-in-production" \
  -H "X-Agent-ID: leon" \
  -H "Content-Type: application/json" \
  -d '{"paths": ["01_TheForeverbox_Mythos/origin_story/THE_FIRST_TEACHER.md"]}'
```

**Pitfall**: Full-root sync is BLOCKED for agents. You MUST provide explicit paths.
Response must include `"summary":{"new":1}`.

### Step 2: Run the ingestion worker
```bash
cd /foreverbox_data/council-library/php-api
export DB_PASS='your_db_pass'
php ../scripts/ingestion_worker.php --once
```

### Step 3: VERIFY vectors were created
```bash
mariadb -u zeon7_user -p'your_pass' quiddity_commons -e \
  "SELECT COUNT(*) FROM quiddity_vector_references WHERE file_id=(SELECT id FROM quiddity_files WHERE relative_path='YOUR_PATH');"
```
If count is 0, the embedding service may have been down. Check it and re-run.

## Embedding Service Management

### Heartbeat Check
```bash
curl -s -X POST "http://localhost:8900/embed" \
  -H "Content-Type: application/json" \
  -d '{"texts":["test"]}' | wc -c
```
Returns > 0 if service is alive.

### Restart the Service
```bash
fuser -k 8900/tcp 2>/dev/null; sleep 1
/usr/bin/python3.12 /foreverbox_data/council-library/scripts/embedding_service.py --port 8900 &
```
Wait ~10 seconds for model loading before testing.

## Pitfalls & Lessons

### Large File Deadlocks
Files generating 200+ chunks may trigger:
```
PHP Fatal error: Uncaught PDOException: SQLSTATE[40001]: Serialization failure: 1213 Deadlock
```
**This is NON-FATAL.** All vectors are written before the deadlock occurs on the final commit. Verify the count and proceed.

### Embedding Dimension Confusion
The service returns hex-encoded float32 vectors.
- 384 dimensions = 1536 bytes = 3072 hex characters
- Do NOT confuse byte count (1536) with vector dimension count (384)
- The DB stores hex; `LENGTH(embedding)/8` gives the float count

### Unregistered Files
A file physically present in the Sea but NOT registered via the sync API will NOT be processed by the worker. The worker only processes files that exist in `quiddity_files` with `indexing_status='pending'`.

### Zone.Identifier Files
Windows metadata files (`filename:Zone.Identifier`) will be registered as separate DB entries and will fail to ingest. These can be safely ignored or deleted.

### The "Indexed" Trap
The worker skips files marked as `indexed`. To force re-processing:
```sql
UPDATE quiddity_files SET indexing_status='pending' WHERE relative_path='YOUR_PATH';
```

### PDF Handling
PDFs must be pre-processed via `pdftotext` (handled by the `/foreverbox_data/bin/fbox-ingest-file` wrapper) before being sent to the API. The API cannot natively chunk PDF binaries.

### Vector Search LIMIT
The `VectorSearch.php` had `LIMIT 200` which caused newer files to not surface in search results. This was changed to `LIMIT 5000` to ensure all vectors are candidates for similarity matching.

## Verification Checklist
After any ingestion operation:
1. **DB Check**: File exists in `quiddity_files` with `indexing_status='indexed'`
2. **Vector Count**: `SELECT COUNT(*) FROM quiddity_vector_references WHERE file_id=XX` returns > 0
3. **Search Test**: `fbox-commons-search "unique phrase from document" 5` returns results from the file
4. **Disk Check**: File is in the correct subfolder (not lingering in root)

## User Workflow Preferences
- **Plan Before Execution**: The user strictly requires a "Plan -> Approval -> Execution" workflow. NEVER execute a fix immediately after proposing it. Present the plan, wait for explicit approval, then execute.
- **No Em/En Dashes**: UK English only. Use commas, colons, semicolons, or rewrite.
- **Report Honestly**: If a tool fails or a step doesn't work, report the blocker directly. Never fabricate success.
