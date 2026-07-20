---
name: fbox-lore-sea-management
description: Manage the structural organization, classification, and ingestion of the Quiddity Lore Sea shared knowledge base.
---

# fbox-lore-sea-management

## Purpose
Manage the structural organization, classification, and ingestion of the Quiddity Lore Sea shared knowledge base. This skill ensures that the physical filesystem and the database `relative_path` remain synchronized and that content is semantically categorized.

## Operational Workflow

### 1. Taxonomy Definition
The taxonomy is defined in `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml`. 
- Folders are categorized by a numerical prefix (e.g., `01_`, `02_`).
- Each folder and subfolder has a list of `keywords` used by the `FolderRouter` for auto-classification.
- Changes to the taxonomy must be reflected in this YAML file before running ingestion.

### 2. Ingestion and Classification
Ingestion can be triggered via shell wrappers in `/foreverbox_data/bin/` (e.g., `fbox-ingest-file`) or by running the worker directly.
- **The Worker**: `/foreverbox_data/council-library/scripts/ingestion_worker.php`
- **Mechanism**: The worker reads files, generates embeddings (via the service on port 8900), and calls the `FolderRouter` to determine the target directory.
- **Physical Move**: If a match is found, the file is physically moved on disk and the `quiddity_files.relative_path` is updated in the database.

### 3. Global Reclassification (The "Refresh" Pattern)
When the taxonomy is updated, existing files do not move automatically. A global refresh is required:
1. **Reset Status**: Update all files to `pending` in the database.
   `UPDATE quiddity_files SET indexing_status='pending';`
2. **Trigger Worker**: Run the worker with the `--once` flag to force a re-evaluation of every file against the new rules.
3. **Manual Override**: If specific critical files fail to move due to low keyword scores, move them manually via `mv` and update the `relative_path` in the DB immediately to maintain synchronization.

## Pitfalls & Lessons
- **The "Indexed" Trap**: The worker often skips files already marked as `indexed`. Always reset to `pending` when updating the taxonomy.
- **PDF Complexity**: PDFs must be pre-processed via `pdftotext` (handled by the `fbox-ingest-file` wrapper) before being sent to the API.
- **Root Lingering**: Files that don't meet the classification threshold remain in the root. These should be manually audited and moved to the most appropriate category to maintain a clean root.
- **Embedding Service Dependency**: If the service on port 8900 is down, the worker may mark files as `indexed` without actually creating vectors. Always verify vector counts in `quiddity_vector_references` after a bulk run.

## Verification
- **Disk Audit**: `find /foreverbox_data/Quiddity_Lore_Sea -maxdepth 1 -type f` should ideally return zero files.
- **DB Audit**: Query `quiddity_files` to ensure `relative_path` contains the expected folder prefixes.
- **Search Audit**: Use `fbox-commons-search` to verify that the most recently moved files are surfacing with high similarity.
