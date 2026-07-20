---
name: fbox-taxonomy-management
description: Manage the semantic organization and physical layout of the Quiddity Lore Sea, including folder hierarchy and auto-classification rules.
---

# fbox-taxonomy-management

## Purpose
Manage the semantic organization and physical layout of the Quiddity Lore Sea. This skill ensures that documents are not just stored, but categorized according to the 8-domain hierarchy to maintain high-precision discoverability and semantic hygiene.

## Core Principles
- **Flat to Deep**: Move files from the root of `/foreverbox_data/Quiddity_Lore_Sea/` into specific subfolders based on content analysis.
- **Keyword-Driven**: Use `quiddity_folders.yaml` as the authoritative source for classification.
- **Database Synchronization**: Every physical `mv` (move) must be accompanied by an `UPDATE quiddity_files SET relative_path = ...` to prevent broken links in the vector search.

## Implementation Workflow

### 1. Updating Taxonomy
When adding new domains or refining subfolders:
1. Edit `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml`.
2. Define the top-level folder name.
3. Add `keywords` for the root folder.
4. Define `subfolders` with their own specific `keywords` and `purpose`.

### 2. Executing Migration (The "Global Refresh")
To move existing files into the new structure:
1. **Reset Status**: Set all files to `pending` to force a re-evaluation:
   `mariadb -u zeon7_user -p'F0reverb0x#2o26sql' quiddity_commons -e "UPDATE quiddity_files SET indexing_status='pending';"`
2. **Run Worker**: Execute the ingestion worker:
   `php /foreverbox_data/council-library/scripts/ingestion_worker.php --once`
3. **Manual Cleanup**: For high-value documents that fail auto-classification (e.g., fictional narratives that don't hit keyword thresholds), manually `mv` the file and update the database.

## Pitfalls & Lessons
- **The "Root Lingering" Problem**: The worker may mark a file as `indexed` even if it didn't move it. Always verify the root is empty using `find /foreverbox_data/Quiddity_Lore_Sea -maxdepth 1 -type f`.
- **Case Sensitivity**: Ensure keywords in YAML match the semantic intent of the content.
- **Sudo Requirement**: Creating directories in `/var/www` or `/etc/apache2` requires `sudo`.

## Verification
- Check `quiddity_files` for correct `relative_path` entries.
- Run a semantic search (`fbox-commons-search`) to ensure the la-distance/similarity still retrieves the document regardless of its folder.
