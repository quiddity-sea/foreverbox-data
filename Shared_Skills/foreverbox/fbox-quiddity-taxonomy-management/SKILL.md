---
name: fbox-quiddity-taxonomy-management
description: Manage and evolve the folder taxonomy of the Quiddity Lore Sea, including subfolder creation and automated file migration via FolderRouter.
category: foreverbox
---

# fbox-quiddity-taxonomy-management

## Purpose
Manage and evolve the folder taxonomy of the Quiddity Lore Sea. This skill ensures that as the ecosystem grows, documents are not just "dumped" into root folders but are classified into a deep, semantic hierarchy using the `FolderRouter` logic.

## Implementation Logic
The Quiddity Lore Sea uses a keyword-based classification system defined in `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml`. 

### The Classification Flow:
1. **Ingestion**: File is added via `fbox-ingest-file` or sync.
2. **Classification**: `FolderRouter::classify()` analyzes the first 4096 characters of the text.
3. **Mapping**: 
   - If keywords match a top-level folder $\rightarrow$ the file is moved to that folder.
   - If keywords match a subfolder within that folder $\rightarrow$ the file is moved to the specific subfolder.
   - If no high-confidence match is found $\rightarrow$ file remains in root or moves to `_review`.
4. **Persistence**: The physical move is paired with a database update to `quiddity_files.relative_path`.

## Procedural Workflow for Taxonomy Updates

### 1. Analysis & Design
- Identify "flat" areas of the Sea where files are piling up in root directories.
- Define new top-level domains (e.g., `07_MerrillLeo_CreativeWorks`, `08_VisualMedia`).
- Design subfolder hierarchies based on content types (e.g., `stories`, `comics`, `essays`, `music`).
- Define precise keyword lists for each level (Root $\rightarrow$ Subfolder).

### 2. Execution Steps
1. **Backup**: Always backup `quiddity_folders.yaml` before editing.
2. **YAML Update**: Edit the YAML config. Ensure numbering is sequential and keywords are specific to avoid "collision".
3. **Dir Creation**: Pre-create the directory tree on disk (`mkdir -p`) to ensure permission consistency.
4. **Force Reclassification**: 
   - To move existing "indexed" files into new folders, they must be reset to `pending`.
   - Command: `mariadb -u zeon7_user -p'PASSWORD' quiddity_commons -e "UPDATE quiddity_files SET indexing_status='pending';"`
5. **Process**: Run the ingestion worker: `php ../scripts/ingestion_worker.php --once`.

### 3. Verification
- **Physical Check**: `ls -R /foreverbox_data/Quiddity_Lore_Sea/` to verify files moved.
- **Database Check**: `SELECT relative_path FROM quiddity_files` to verify paths updated.
- **Search Check**: Run `fbox-commons-search` to ensure the file is still discoverable via vectors regardless of its new path.

## Pitfalls & Lessons
- **Flat-Root Persistence**: Files already marked as `indexed` will NOT be moved by the worker unless their status is reset to `pending`.
- **Keyword Collision**: Generic keywords (e.g., "story") can cause misrouting. Use specific combinations.
- **Case Sensitivity**: Consistent lowercase keywords in the YAML are recommended.
- **PDF Extraction**: Visual or PDF files require text extraction before they can be classified by keywords.

## References
- Taxonomy Config: `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml`
- Ingestion Worker: `/foreverbox_data/council-library/scripts/ingestion_worker.php`
- Router Logic: `/foreverbox_data/council-library/php-api/src/Service/FolderRouter.php`
