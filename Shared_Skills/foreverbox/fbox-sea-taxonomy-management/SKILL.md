---
name: fbox-sea-taxonomy-management
description: Manage the semantic organization, folder hierarchy, and physical relocation of assets within the Quiddity Lore Sea.
tags: [taxonomy, organization, lore-sea, classification]
---

# fbox-sea-taxonomy-management

## PURPOSE
Manage the semantic organization, folder hierarchy, and physical relocation of assets within the Quiddity Lore Sea. This skill ensures that the physical filesystem and the database `relative_path` remain synchronized and that files are categorized according to the official taxonomy in `quiddity_folders.yaml`.

## OPERATIONAL WORKFLOW

### 1. Taxonomy Modification
When updating the folder structure or adding new categories (e.g., adding a personal creative works section):
- Update `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml`.
- Ensure every new folder has a clear `purpose` and a comprehensive list of `keywords`.
- Use a numbered prefix (e.g., `07_...`) to maintain top-level order.

### 2. Physical Implementation
- Pre-create the directory tree using `mkdir -p` to avoid permission errors during bulk moves.
- Use the `ingestion_worker.php` to perform the actual migration.

### 3. Forced Re-classification (The "Deep Refresh")
If files are not moving automatically or the taxonomy has changed significantly:
- **Reset Status**: Set all files to `pending` via SQL:
  `UPDATE quiddity_files SET indexing_status='pending';`
- **Trigger Worker**: Run the worker with the `--once` flag:
  `php ../scripts/ingestion_worker.php --once`
- **Manual Override**: If the `FolderRouter` fails to classify a critical file due to low keyword density, move the file manually via `mv` and immediately update the `relative_path` in the `quiddity_files` table.

### 4. Verification
- **Root Audit**: Confirm the root of `/foreverbox_data/Quiddity_Lore_Sea/` is empty of data files.
- **Path Audit**: Compare physical location with the `relative_path` in the database.
- **Semantic Test**: Run `fbox-commons-search` on a known-moved file to verify the vector link is still active.

## PITFALLS & LESSONS
- **The "Indexed" Trap**: The ingestion worker often skips files already marked as `indexed`. A global status reset to `pending` is required for a full taxonomy migration.
- **Keyword Thresholds**: Some high-value documents may not trigger auto-movement if they lack specific keywords in the first 4096 characters. Manual relocation is the correct fallback.
- **Sudo Requirements**: Creating folders in `/var/www` or modifying system configs requires `sudo` but should be handled as non-interactive commands.

## REFERENCE COMMANDS
- **Reset Status**: `mariadb -u zeon7_user -p'PASSWORD' quiddity_commons -e "UPDATE quiddity_files SET indexing_status='pending';"`
- **Run Worker**: `php /foreverbox_data/council-library/scripts/ingestion_worker.php --once`
- **Verify Root**: `find /foreverbox_data/Quiddity_Lore_Sea -maxdepth 1 -type f`
