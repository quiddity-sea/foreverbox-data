# Blueprint V2.0 → V3.0 — Complete Change Log

## V2.0 → V2.1 (Cross-Reference Realignment)
- Companion doc: V5 → V6 filename
- 6 `Implements Briefing §X` references remapped to V6 numbering
- 4 new cross-references added for V6-only sections (Hermes §10, Sudo §13, Observability §14, Migration §15)
- Closing line updated

## V2.1 (Hermes ABC Compatibility)
- `prefetch()`: return type `list` → `str`, added `session_id` kwarg
- `get_tool_schemas()`: `...` stub → 9 complete OpenAI-format tool schemas
- `handle_tool_call()`: `...` stub → full route_map with GET/POST/PUT/DELETE dispatch
- `system_prompt_block()` and `queue_prefetch()` added
- §6.7 design decision resolved: both auto-inject + tools active

## V2.1 (Ingestion Pipeline)
- §4.5: Three trigger paths (agent-initiated, 4-hour cron, startup hook) + root-as-inbox convention
- §4.6: Content-based folder router using cosine similarity against centroid embeddings
- §4.7-4.8: Endpoint updates + `quiddity_folder_centroids` DDL
- `ingest_file` tool added (10th tool)
- §3.2: `POST /v1/commons/files/sync` updated, `GET /v1/commons/folders` added
- §3.3: `FolderController.php` added to file structure

## V2.1 → V3.0 (Gap Closure)
### Structural gaps filled
- `ingestion_dead_letter` DDL added to §2.1
- `_review/` reclassify endpoint: `POST /v1/commons/folders/reclassify`
- Folder CRUD: `PUT` and `DELETE /v1/commons/folders/{name}`
- Centroid rebuild: `POST /v1/commons/folders/rebuild-centroids`
- §13 acceptance criteria: 12 new test items
- §14 migration directive: updated for FolderController, centroids, cron

### Stubs filled
- `_is_healthy()` — 30s-cached Ollama/cloud health probes
- `queue_prefetch()` — background-threaded search
- `on_pre_compress()` — snapshot persistence before context eviction
- `on_memory_write()` — mirror hook routing to Sanctum endpoints

### Missing methods added
- `backup_paths()`, `on_session_end()`, `on_session_switch()`, `on_delegation()`

### Signature corrections
- `sync_turn()`: added `session_id` and `messages` kwargs
- `on_memory_write()`: added `metadata` kwarg
- `handle_tool_call()`: added `**kwargs`
- Class imports: added `uuid, time`

## Final Metrics
| Metric | V2.0 | V3.0 |
|--------|------|------|
| Lines | 1,642 | 2,320 |
| File size | 79 KB | 114 KB |
| Tool schemas | 0 (stub) | 10 (complete JSON) |
| `...` stubs | 6 | 0 |
| `pass` stubs | 2 | 0 |
| Endpoints | 22 | 28 |
| Acceptance criteria | 23 | 35 |
| ABC method coverage | Partial | Complete |
| Ingestion trigger paths | 0 | 3 |
| DDL tables | 13 | 15 |
