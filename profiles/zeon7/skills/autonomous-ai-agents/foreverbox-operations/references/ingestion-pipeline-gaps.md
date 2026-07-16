# Ingestion Pipeline Gaps — Known Undefined Areas

The Architecture Blueprint (V2.1) defines the Ingestion Pipeline's chunking, embedding,
worker code, and idempotency strategy (§4). But two critical concerns remain undefined
as of 2026-07-14.

## Gap 1: Trigger Mechanism

**What the blueprint says**: The IngestionWorker "reads the filesystem drop folder"
(§4.3 comment). PHP endpoints `POST /v1/commons/files/sync` and `POST /v1/commons/ingest/batch`
exist (§3.2).

**What is undefined**: How does a file landing in `/foreverbox_data/Quiddity_Lore_Sea/`
actually wake up the pipeline? Options:

| Mechanism | Pros | Cons |
|-----------|------|------|
| **inotify filesystem watcher** | Instant, zero polling overhead | Requires a persistent daemon; must handle bursty writes (temp files, partial saves) |
| **Cron job (e.g., every 5 min)** | Simple, no daemon to maintain | Polling overhead; delay between drop and index |
| **Manual API call** (`POST /v1/commons/files/sync`) | Explicit, debuggable | Requires human or agent action; no auto-detection |
| **Agent-initiated tool** (new `commons_ingest` tool) | Agent can trigger on demand | Still requires agent awareness; no background auto-index |

**Recommendation**: inotify watcher as primary (a small PHP or Python daemon watching the
drop folder), with `POST /v1/commons/files/sync` as a manual fallback. The watcher should
debounce (wait for file to stabilise, e.g., 5s of no writes) before triggering ingestion.

## Gap 2: Folder Organisation Convention

**Current state**: `/foreverbox_data/Quiddity_Lore_Sea/` already has numbered subfolders:
```
01_TheForeverbox_Mythos/
02_ReInvigor_Texts/
03_TheInitiative_Audio/
04_FromTheNoise_Archives/
05_Agent_Profiles/
06_QuiddityLtd_Dev_Specs/
```

**What is undefined**: The blueprint never codifies this numbering scheme or defines
rules for adding new folders. The `quiddity_files.relative_path` column stores the
path relative to the root, so the folder structure is preserved in the database.
But without a documented convention:

- New folders may be added ad-hoc, breaking discoverability
- The ingestion worker doesn't know which folders to watch
- There is no rule for whether processed files stay in place or move

**Proposed convention** (to be added to the blueprint):
- Folders use two-digit numeric prefix for ordering: `NN_Descriptive_Name/`
- Numbers are assigned sequentially; gaps are fine (allows future insertion)
- A `00_Inbox/` folder serves as the drop zone for unprocessed files
- After indexing, files stay in their folder (the `indexing_status` column in
  `quiddity_files` tracks state — no filesystem move needed)
- The `_Archive/` suffix designates historical/read-only material

## Gap 3: Post-Processing Lifecycle

**What happens after a file is vectorised?** The `quiddity_files` table tracks
`indexing_status` (`pending` → `processing` → `indexed` / `failed`). But the
filesystem side is undefined:

- Does the file stay in place? (Current assumption: yes — `indexing_status` is the
  source of truth, and the filesystem is the canonical store.)
- Does it move to an `_indexed/` subfolder?
- Does a `.indexed` sidecar file get created?
- How is re-indexing triggered if the file is edited? (The SHA-256 `content_hash`
  in `index_quiddity.py` §8.3 handles this — if the hash changed, re-index. But
  the trigger for re-checking the hash is undefined.)

**Current working assumption**: Files stay in place. The `index_quiddity.py` script
(§8.3) is re-run periodically (or on trigger) and uses `content_hash` to skip
unchanged files. This is idempotent and safe but wastes a filesystem walk on every
run for unchanged files.

## Related Blueprint Sections

- §4 — Ingestion Pipeline ("The Silent Librarian")
- §3.2 — PHP endpoints: `POST /v1/commons/ingest/batch`, `POST /v1/commons/files/sync`
- §8.3 — Phase 3: Quiddity Indexing (`index_quiddity.py`)
- §2.1 — `quiddity_files` and `quiddity_vector_references` DDL
