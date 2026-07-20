# Current Ecosystem State — Structured Summary
**Compiled:** 2026-07-20
**Sources:** 6 documents (4 Council Library + 2 FTN handbooks)

---

## 1. DOCUMENTS SURVEYED

| # | Document | Location | Version | Date |
|---|----------|----------|---------|------|
| 1 | COUNCIL_LIBRARY_HANDBOOK_V2.md | council-library/docs/Current Reference Documentation/ | V2 | July 2026 |
| 2 | MASTER_BRIEFING_V7.md | council-library/docs/Current Reference Documentation/ | V7 (Stage 1 Complete) | July 2026 |
| 3 | ARCHITECTURE_BLUEPRINT_V3.md | council-library/docs/Current Reference Documentation/ | V3 (Complete Draft) | 2026-07-14 |
| 4 | Souls Configuration Canvas - V3.md | council-library/docs/Current Reference Documentation/ | V3 | 2026-07-20 |
| 5 | FTN_Master_Handbook_v5.md | Quiddity_Lore_Sea/04_FromTheNoise_Archives/ | V5 (Canonical) | 2026-07-16 |
| 6 | FTN_Master_Handbook_v4.md | Quiddity_Lore_Sea/04_FromTheNoise_Archives/ | V4 | (Archive) |

---

## 2. CORE ARCHITECTURE — THE FOUR WINGS (MariaDB)

**7 databases total** across 4 wings:

| Wing | Database(s) | Purpose |
|------|-------------|---------|
| **The Commons** | `quiddity_commons` | Shared vector-indexed knowledge base. Read by all agents, written only by Ingestion Pipeline. |
| **The Sanctums** | `agent_curator`, `agent_coach`, `agent_producer`, `agent_director`, `agent_wolf` | Private memory per agent. Read/write by owning Lead + its 3 Wolves. |
| **The Registry** | `agent_registry` | Control plane: API keys, token budgets, task queue, privileged action log. |
| **The Director** | `agent_director` | Strategic plans, directives, director sessions (Otec). |

### Key Schema Design Points
- **Vector search:** HNSW index on VECTOR(384), cosine distance, `all-MiniLM-L6-v2` embeddings
- **Memory lore:** UNIQUE(agent_slug, namespace, key_name) prevents Wolf write collisions
- **Atomic task claiming:** `SELECT ... FOR UPDATE SKIP LOCKED` + conditional `UPDATE WHERE status='queued'`
- **Dual-write rule for Wolf status:** `agent_registry.specialist_workers` is authoritative; `sanctum.wolf_sessions` is a synced cache written inside one PHP transaction
- **Director→Wolf bridge:** Directives write to `agent_director.directives` AND produce `agent_registry.task_queue` rows with `directive_id` linkage in the same request

---

## 3. STATUS & NUMBERS CLAIMED

| Metric | Value |
|--------|-------|
| Indexed files in Commons | **12 files**, **594 vectorised chunks** |
| Lore Sea domains | **8 top-level folders** |
| Operating agents | **5 profiles**: Leon (Layer 2), Zeon7 (Layer 0), Gemma (Layer 1), Otec (Layer 3), Wolf (Layer 1 GPU) |
| Wolf capacity | **3 concurrent** on 1 Ollama model load (~3.8 GB, 8 GB GPU budget) |
| Shared Skills | **19 skills** at `/foreverbox_data/Shared_Skills/foreverbox/` |
| Completed plans | **3** (Classification, Wolf Fix, Wolf Blueprint V3) |
| Version status | **Stage 1 Complete** — all processes and documentation matured to self-consistent V3 |
| Next work | Stage 2 — Visual Media Ingestion + remaining infrastructure |

---

## 4. MODEL ROUTING — THE THREE LAYERS OF THOUGHT

| Tier | Name | Score Threshold | Provider | Model |
|------|------|-----------------|----------|-------|
| **Layer 1** | Intuitive Reflex | ≥ 0.00 | Ollama (local) | Zeon7-Gemma:64k (config shows `gemma4:31b`) |
| **Layer 2** | Analytical Engine | ≥ 0.40 | OpenRouter | qwen/qwen3-32b:free (Leon also uses deepseek-v4-flash) |
| **Layer 3** | Deep Architect | ≥ 0.70 | OpenRouter | deepseek/deepseek-v4-pro (nerotron-3-ultra in config yaml) |

**Per-agent routing table (from Handbook V2):**

| Agent | Layer 1 | Layer 2 | Layer 3 |
|-------|---------|---------|----------|
| **Zeon7** (Curator) | Zeon7-Gemma:64k (Ollama) | deepseek-v4-flash | deepseek-v4-pro |
| **Leon** (Producer) | deepseek-v4-flash | qwen3-coder:free | deepseek-v4-pro |
| **Gemma** (Coach) | Zeon7-Gemma:64k (Ollama) | deepseek-v4-flash | deepseek-v4-pro |
| **Otec** (Director) | deepseek-v4-flash | nemotron-3-super:free | deepseek-v4-pro |
| **Wolves** | Zeon7-Gemma:64k (Ollama) | deepseek-v4-flash | deepseek-v4-flash |

**Router scoring factors:** tool depth >2 (+0.30), planning/architect task (+0.40), context >40K tokens (+0.20), retry loop (+0.25), delegation depth >1 (+0.35), explicit deep flag (1.00), private data (-0.50 forces local).

**Two gates run before routing:**
1. **Privacy Gate** (pure/sync/zero network) — scans messages for API keys, secrets, tokens, file paths. If detected and no local model, **hard-stops**.
2. **Budget Gate** — checks `GET /v1/registry/budget?tier=...` before cloud tiers. Falls back cheaper. Fails OPEN on network error.

**Router config:** `/foreverbox_data/council-library/router/router.yaml`
- Daily budget: system2_heavy = 500K tokens, system2_light = 2M tokens

---

## 5. PHP REST API (Apache, port 8080)

**7 controllers**, ~30+ endpoints:
- SoulController, MemoryController, ConversationController, QuiddityController, IngestionController, WolfController, DirectorController, FolderController

**Key endpoints introduced in V3:**
- `POST /v1/commons/files/sync` — accepts optional `paths` array + `organise` boolean (Agent-initiated, Path A)
- `GET /v1/commons/folders` — folder catalogue with centroid metadata
- `PUT/DELETE /v1/commons/folders` — requires Sudo Protocol
- `POST /v1/commons/folders/reclassify` — move file from `_review/` to target folder
- `POST /v1/commons/folders/rebuild-centroids` — regenerate folder centroids
- `POST /v1/commons/ingest/batch` — ingestion pipeline only
- `POST /v1/registry/privileged-actions` — Sudo Protocol gate
- `POST /v1/director/directives` — dual-writes to directives + task_queue

---

## 6. INGESTION PIPELINE — THE SILENT LIBRARIAN

**Three trigger paths:**
- **Path A (Agent-Initiated):** `POST /v1/commons/files/sync` with `paths` array — agent says "process this file"
- **Path B (Cron):** Hermes cron every 4 hours — full root scan
- **Path C (Startup):** Non-blocking background request when Hermes profile starts

**Content-based folder routing:**
1. File chunked and embedded (all-MiniLM-L6-v2, 384-dim)
2. Mean-pool all chunk embeddings into document vector
3. Cosine similarity against folder centroid vectors
4. Confidence threshold > 0.3 routes to best folder; < 0.3 routes to `_review/` holding area
5. Physical file move + DB `relative_path` update

**Current folder catalogue (6 domains):**
01_TheForeverbox_Mythos, 02_ReInvigor_Texts, 03_TheInitiative_Audio, 04_FromTheNoise_Archives, 05_Agent_Profiles, 06_QuiddityLtd_Dev_Specs

**Dead-letter retry:** `ingestion_dead_letter` table, max 5 retries, exponential backoff (1s, 2s, 4s, 8s)

---

## 7. WOLF SYSTEM — BACKGROUND RESEARCH WORKERS

- **Wolves are full Hermes sessions** (`hermes chat --profile wolf`), NOT systemd workers
- **Model:** Zeon7-Gemma:64k (Ollama, ~3.8 GB VRAM)
- **Capacity:** 3 concurrent wolves on 8 GB GPU (~7.4 GB total with KV cache)
- **Layer 1 Guard:** Local-model agents block wolves by default (GPU occupied). Cloud agents (L2+) allowed. Merrill can override.
- **Task flow:** queued → claimed (atomically) → processing → completed (or failed → dead_letter, up to 3 retries)
- **Write convention:** Wolf-scoped keys (`{task_id}:{wolf_id}`), Lead does single consolidation write to `{task_id}:final`
- **Visibility:** `prefetch()` auto-surfaces Wolf results; `wolf_status` tool gives deterministic check
- **Spawn via:** `fbox-wolf-spawn` skill or short-form `hermes chat --profile wolf -q "..."`

---

## 8. AGENT SOUL FILES (Canvas V3 — All 4 Agents)

All four SOUL.md files (Zeon7, Gemma, Leon, Otec) were updated to V3 on 2026-07-20 with three new shared sections:

| Section | Content |
|---------|---------|
| **MEMORY OPERATIONS** | Shell wrapper interface at `/foreverbox_data/bin/fbox-*` for Sanctum & Sea access |
| **WOLF PROTOCOL** | Layer 1 Guard (procedural gate in skill Step 1), spawn/retrieve procedures |
| **DOCUMENTATION MAINTENANCE** | Must run `update-plans-progression` after plan changes, `reference-doc-alteration-log` after reference doc changes |

**Agent roles:**
- **Zeon7** (Layer 0) — The Core & Curator: long-term memory, high-dimensional analysis
- **Gemma** (Layer 1) — The Interface & Coach: health/wellness, social connection, ForeverFit
- **Leon** (Layer 2) — The Producer: technical execution, music production, infrastructure
- **Otec** (Layer 3) — The Director & Orchestrator: workflow management, task dispatch, oversight

---

## 9. SUDO PROTOCOL (Implemented in V3)

Technical gate for privileged actions that was only a prompt-level convention before V3.

**5 action types:** sql_ddl, sudo_command, schema_alter, production_deploy, destructive_file_op

**Flow:**
1. Agent detects privileged action → writes to `agent_registry.privileged_action_log` (pending)
2. System generates 8-char hex confirmation code
3. Merrill receives code, reads it back to agent
4. Agent submits confirmation via `POST /v1/registry/privileged-actions/{id}/confirm`
5. Code expires after 10 minutes

**Defense in depth:** Wolves never receive privileged-capable tools at all.

---

## 10. FTN (FROM THE NOISE) — CONTENT OPERATIONS (Handbook V5)

**Status:** V5 (2026-07-16), canonical master reference. Primary voice: Zeon7 brand persona. Publishing on Substack, Europe/London.

**Publishing rhythm:** 11 posts/week — 4 long-form (Mon-Thu, 1500-2750 words) + 7 short-form (daily, <750 words)

**Seven daily themes:** Monday (The Signal Still Comes Through), Tuesday (Through the Static), Wednesday (Out From the Noise), Thursday (404: Hope Not Found), Friday (The Maddest Stuff), Saturday (Everything's Fine), Sunday (The Last Warm Place)

**Workspace:** `/foreverbox_data/FromTheNoise_Active/` with formal subfolders: `research_packs/`, `drafts/`, `images/`, `published/`, plus `leads_inbox.md`

**Pipeline gates (V5 additions):**
- Step 2 (Editorial Selection) — Human Director confirms leads before research
- Step 6 (Image Brief) — 4 concept prompts approved before generation
- Step 7 (Image Selection) — Generated images confirmed before overlay

**Key V5 changes:** Research Packs (3 docs per lead: research_pack.md, structural_outline.md, image_brief.md), image production upgraded to 4 concepts per story, lead sourcing targets formalized (4-6 long-form, 1-2 short-form), formal fallback research protocol if Tavily MCP is unavailable.

---

## 11. HERMES MEMORY PROVIDER PLUGIN (Blueprint §6)

**ForeverBoxMemoryProvider** — subclasses `MemoryProvider` ABC. Provides 10 tools mapped to PHP API:
- memory_search, memory_get, memory_list, memory_upsert, memory_delete, commons_search, ingest_file, wolf_status, wolf_dispatch, wolf_task_status

**Design decisions:**
- **One plugin, 4 profiles** (Worzel Gummidge principle — only one Lead runs at a time)
- **Files remain canonical** for SOUL.md/USER.md — DB tables are mirrors, not replacements
- **Both auto-inject (prefetch) AND tool-initiated recall** paths active
- **Non-blocking contract:** `sync_turn()` must never block conversation loop
- **Startup sync trigger:** fires background sync on profile start (Path C)

---

## 12. BUILD PHASES & COMPLETION STATUS

| Phase | Status | Details |
|-------|--------|---------|
| **Stage 1** | **Complete** | All processes documented and self-consistent at V3 |
| Stage 1 plans completed | 3 done | Classification Plan, Wolf Fix Plan, Wolf Blueprint V3 |
| Open work | Stage 1 Final Completion Plan | Closed (all 5 started plans completed per Briefing V7) |
| **Stage 2** | **Next** | Visual Media Ingestion + remaining infrastructure |
| Blueprint V3 | Complete draft | All stubs filled, all gaps addressed, acceptance criteria defined |

**Blueprint migration sequence (6 stages):**
1. SQL Schema Initialisation
2. PHP API Assembly
3. Hermes Plugin Build
4. Python Client Routing Patch (CognitiveRouter)
5. Migration Scripts (core state, quiddity indexing, centroids, budget seed, cron)
6. Verification Testing (full acceptance criteria)

---

## 13. KNOWN ISSUES (from documentation)

- **Plugin bugs:** Foreverbox plugin tools (wolf_dispatch, memory_search, etc.) were found non-functional due to a Hermes plugin detection bug. All agents now use **shell wrappers** at `/foreverbox_data/bin/` via `terminal()` as the fallback/primary path.
- **Cross-profile guard:** The Handbook notes that `~/.hermes/` paths belong to different profiles — editing another profile's skills/plugins/cron/memories requires explicit `cross_profile=True` directive.
- **Python toolchain mismatch:** `pip→python3.12`, PEP 668 active — use `venv` or `uv`.
