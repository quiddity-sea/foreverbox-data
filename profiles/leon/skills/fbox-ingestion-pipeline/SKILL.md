---
name: fbox-ingestion-pipeline
description: "Operate and troubleshoot the Quiddity Lore Sea ingestion pipeline: file registration, embedding generation, vector verification, and deadlock recovery."
---

# fbox-ingestion-pipeline

## Purpose
Operate and troubleshoot the full Quiddity Lore Sea ingestion pipeline: from file registration through embedding generation to vector verification. Covers the complete lifecycle and common failure modes.

## Architecture
```
File in Sea -> sync API (register) -> ingestion_worker.php -> embedding_service.py (:8900) -> MariaDB vectors
```

- Embedding Service: `/foreverbox_data/council-library/scripts/embedding_service.py` on port 8900
- Model: all-MiniLM-L6-v2 (384 dimensions, 1536 bytes, 3072 hex chars)
- Worker: `/foreverbox_data/council-library/scripts/ingestion_worker.php`
- API: `http://localhost:8080/v1`
- DB: MariaDB `quiddity_commons`

## Ingestion Steps

### 1. Register via sync API
```bash
curl -s -X POST "http://localhost:8080/v1/commons/files/sync" \
  -H "Authorization: Bearer dev-key-change-in-production" \
  -H "X-Agent-ID: leon" \
  -H "Content-Type: application/json" \
  -d '{"paths": ["path/to/file.md"]}'
```
Full-root sync blocked for agents. Must provide explicit paths.

### 2. Run the worker
```bash
cd /foreverbox_data/council-library/php-api
export DB_PASS='your_db_pass'
php ../scripts/ingestion_worker.php --once
```
Force re-process all files after taxonomy change:
```bash
php ../scripts/ingestion_worker.php --reclassify --once
```

### 3. Verify
```bash
mariadb -u zeon7_user -p'pass' quiddity_commons -e \
  "SELECT COUNT(*) FROM quiddity_vector_references WHERE file_id=XX;"
```

## Embedding Service

Heartbeat:
```bash
curl -s -X POST "http://localhost:8900/embed" -H "Content-Type: application/json" -d '{"texts":["test"]}' | wc -c
```

Restart:
```bash
fuser -k 8900/tcp 2>/dev/null; sleep 1
/usr/bin/python3.12 /foreverbox_data/council-library/scripts/embedding_service.py --port 8900 &
```

## Critical Pitfalls

### UNHEX vs hex2bin
The EmbeddingClient converts hex to binary via hex2bin(). MariaDB VECTOR columns reject direct binary PDO binding with `SQLSTATE[22007]: Incorrect vector value`. The worker MUST use `UNHEX(?)` in INSERT and pass hex strings directly. Never bind binary blobs to VECTOR columns.

### Column name: chunk_token_count
The table uses `chunk_token_count`, not `token_count`. Wrong name = `SQLSTATE[42S22]: Unknown column`.

### MIME type defaults
Files registered via sync default to `text/markdown` even for PDFs. Worker reads raw binary PDF as text instead of using pdftotext. Fix: `UPDATE quiddity_files SET mime_type='application/pdf' WHERE relative_path LIKE '%.pdf';`

### Keyword threshold
FolderRouter threshold was 2 (min 2 keyword matches). Too high for fiction. Lowered to 1 in `FolderRouter.php`.

### Filename classification
Added `filenameClassify()` to FolderRouter. Checks filename against folder keywords first (weighted 3x). Removed "architect" from otec keywords — substring match with "architecture" caused false positives.

### Deadlocks (non-fatal)
Files with 200+ chunks may trigger `SQLSTATE[40001]: 1213 Deadlock`. All vectors written before deadlock on final commit. Verify count and proceed.

### Zone.Identifier cleanup
Windows metadata files registered as DB entries: `DELETE FROM quiddity_files WHERE relative_path LIKE '%:Zone.Identifier';`

### Vector Search LIMIT
Changed from 200 to 5000.

## Verification Checklist
1. File `indexing_status='indexed'` in quiddity_files
2. Vector count > 0 in quiddity_vector_references
3. fbox-commons-search returns results from file
4. File in correct subfolder (not root)
5. No :Zone.Identifier entries in DB

## User Workflow
- Plan -> Approval -> Execution. Never jump to execution.
- UK English. No em/en dashes.
- Honest reporting. Never fabricate success.
