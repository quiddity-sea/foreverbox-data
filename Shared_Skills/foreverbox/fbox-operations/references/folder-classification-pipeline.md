# Folder Classification Pipeline — End-to-End

The full pipeline from raw file to organised, centroided document.

## Three Stages

| Stage | What | Entry Point |
|-------|------|-------------|
| 1. Sync + Register | Discover files, upsert into `quiddity_files` | `POST /v1/commons/files/sync` |
| 2. Classify + Route | Determine target folder, `rename()` on disk | `FolderRouter::classify()` → `QuiddityController::sync()` line 155-171 |
| 3. Centroids | Build folder centroids for vector-based routing | `generate_folder_centroids.py` |

## Stage 2 Detail: Classify + Route

### Entry conditions
The organise block (QuiddityController line 155) fires when:
- `$organise` is true (passed in request body)
- `$router` is non-null (FolderRouter constructed)
- `$relativePath` contains no `/` (root-level file only — already-classified files in subfolders are not re-routed)

### Classification logic (FolderRouter)
1. **Vector path** (primary): if embedding service is available, embed first 2,000 chars, query `quiddity_folder_centroids` via `VECTOR_DISTANCE`. Returns folder name if similarity > 0.3. Falls back to keyword path if PDO is unavailable or centroid table is empty.
2. **Keyword path** (fallback): truncate to first 4 KB, count case-insensitive keyword matches per folder. Threshold: best score ≥ 2. Below threshold → `_review`.

### Move logic
```php
$targetDir = $rootDir . '/' . $folder;
if (!is_dir($targetDir)) mkdir($targetDir, 0755, true);
$targetPath = $targetDir . '/' . basename($fullPath);
if (rename($fullPath, $targetPath)) { /* update DB */ }
```

### Permission requirements
For Apache (www-data) to execute `rename()` and `mkdir()`:
- Source file: `o+r` (readable by other)
- Source parent directory: `o+w` (writable by other — for unlink during rename)
- Target directory: `o+w` (writable by other — for creating the new file)
- YAML config: `o+r` (FolderRouter reads `quiddity_folders.yaml`)

**Commands:**
```bash
sudo chmod o+r /foreverbox_data/Quiddity_Lore_Sea/*.md
sudo chmod o+w /foreverbox_data/Quiddity_Lore_Sea/
sudo chmod o+w /foreverbox_data/Quiddity_Lore_Sea/*/
sudo chmod o+r /foreverbox_data/council-library/php-api/config/quiddity_folders.yaml
```

## Pitfalls

### vectorClassify returns '_review' not null
The `vectorClassify()` method originally returned `'_review'` on failure. In `classify()`, the check `if ($result !== null)` passed, returning `'_review'` immediately without falling through to keyword matching. **Fix**: make `vectorClassify()` return `null` on failure so the caller proceeds to `keywordClassify()`.

### Full-document keyword skew
Keyword matching on a 113 KB document counts "agent" hundreds of times, drowning out "blueprint" matches. **Fix**: truncate to first 4 KB (`substr($contentText, 0, 4096)`) before keyword scoring.

### YAML parsing without ext-yaml
PHP's `yaml_parse_file()` requires the YAML extension, which is not installed by default. **Fix**: custom parser in `FolderRouter::parseYamlFolders()` that handles quoted keys (`"folder_name":`) and `- item` list syntax for keywords.

### Apache opcode cache on reload
`sudo systemctl reload apache2` does NOT clear PHP opcode cache. Code changes to PHP files are invisible. **Fix**: `sudo systemctl stop apache2 && sudo systemctl start apache2`. Full stop-restart cycle.

### Previous subagent dropped keywords from YAML
The FolderController subagent rewrote `quiddity_folders.yaml` with only `purpose` fields — no `keywords`. The FolderRouter had nothing to match against. **Fix**: restore keyword arrays to the YAML config. See `/foreverbox_data/council-library/php-api/config/quiddity_folders.yaml` for the current version.

### rename() reports "Permission denied" silently
The sync response shows `organised:0` with no error message in the JSON body. The actual error only appears in Apache's error log (`/var/log/apache2/council-library-error.log`). Always check logs when `organised` is unexpectedly zero.
