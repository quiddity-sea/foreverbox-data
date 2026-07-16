# Blueprint Gap Audit Methodology

Used during V2.0→V3.0 blueprint completion (2026-07-14). This taxonomy
categorises every finding so nothing is missed and the fix order is
systematic.

## Step 1: List All Sections

```bash
grep -n '^## ' BLUEPRINT.md
```

Get the full section map. You need to know what exists before you can
audit what's missing.

## Step 2: Find All Stubs

```bash
# Implementation stubs — code blocks with placeholder intent but no code
grep -n '\.\.\.' BLUEPRINT.md | grep -v '# ...'

# pass stubs — methods with a pass and a comment describing intent
grep -n 'pass$' BLUEPRINT.md
```

Both should return zero for a complete blueprint. V2.0 had six `...` and
two `pass` stubs.

## Step 3: Categorise Findings

Every gap falls into one of three categories. Fix them in this order:

### Type A: Structural Gaps (fix first)
Something is referenced in prose but never defined in DDL, endpoint
tables, or configuration. Examples from V2.0:
- `ingestion_dead_letter` table referenced in §4.4 but missing from §2.1
- No trigger mechanism for the ingestion pipeline (just "reads the
  filesystem drop folder" with no when/how)
- `_review/` mentioned as a destination but no reclassify endpoint
- Folder catalogue referenced but no CRUD endpoints

### Type B: Implementation Stubs (fix second)
A method or function exists with a comment describing intent but the
body is `...` or `pass`. The contract is understood; the code is
missing. Examples from V2.0:
- `get_tool_schemas()` — comment says "memory_search, memory_upsert..."
  but body is `...`
- `handle_tool_call()` — comment says "Route to matching PHP endpoint"
  but body is `...`
- `_is_healthy()` — comment describes health check intent, body is
  `pass`
- `on_pre_compress()` — comment describes snapshot intent, body is `...`
- `on_memory_write()` — comment describes mirror hook, body is `...`

### Type C: Stale Sections (fix third)
Sections that were written against an earlier version of the system and
haven't been updated to reflect new features or removed stubs. Examples
from V2.0:
- §13 Acceptance Criteria — predates ingestion triggers, folder routing,
  stub fills, method signature fixes
- §14 Migration Directive — predates FolderController, centroid
  seeding, cron job registration

## Step 4: Verify the Fix

After all patches:

```bash
# No stale references to old versions
grep -n "V5\|Master_Briefing_V5" BLUEPRINT.md
# Must return zero hits

# No remaining stubs
grep -c '\.\.\.$' BLUEPRINT.md
grep -c 'pass$' BLUEPRINT.md
# Both must return 0

# Closing line matches header version
head -1 BLUEPRINT.md
tail -3 BLUEPRINT.md
```

## V2.0→V3.0 Gap Audit Results (Reference)

| # | Type | Location | Description | Resolution |
|---|------|----------|-------------|------------|
| 1 | A | §2.1 | `ingestion_dead_letter` table missing | Added DDL |
| 2 | A | §3.2 | No `_review/` reclassify endpoint | Added `POST /v1/commons/folders/reclassify` |
| 3 | A | §3.2 | No folder CRUD endpoints | Added `PUT` and `DELETE /v1/commons/folders` |
| 4 | A | §3.2 | No centroid rebuild trigger | Added `POST /v1/commons/folders/rebuild-centroids` |
| 5 | A | §4 | No ingestion trigger mechanism | Added §4.5 (three paths) and §4.6 (folder router) |
| 6 | B | §5.2 | `_is_healthy()` is `pass` | Implemented with 30s-cached health probes |
| 7 | B | §6.4 | `queue_prefetch()` is `pass` | Implemented with background-threaded search |
| 8 | B | §6.4 | `on_pre_compress()` is `...` | Implemented with snapshot persistence |
| 9 | B | §6.4 | `on_memory_write()` is `...` | Implemented with mirror-hook routing |
| 10 | B | §6.4 | Missing `backup_paths()` | Added (returns `[]`) |
| 11 | B | §6.4 | Missing `on_session_end()` | Added with background summary extraction |
| 12 | B | §6.4 | Missing `on_session_switch()` | Added with session_id update |
| 13 | B | §6.4 | Missing `on_delegation()` | Added with delegation logging |
| 14 | B | §6.4 | `sync_turn()` missing kwargs | Added `session_id` and `messages` |
| 15 | B | §6.4 | `on_memory_write()` missing `metadata` | Added `metadata=None` |
| 16 | C | §13 | Acceptance criteria stale | Added 12 new criteria |
| 17 | C | §14 | Migration directive stale | Updated all 6 stages |
