# Technical Architecture Blueprint V2 — Reference Notes

**Source**: `/foreverbox_data/Quiddity_Lore_Sea/ARCHITECTURE_BLUEPRINT_V2 - 2.md`  
**Target Reader**: Qwen Coder (Builder Model) → Leon (Layer 2 Producer)  
**Date**: 2026-07-13  
**Companion**: Master Briefing V5

---

## Version History & Gap Fixes

| Version | Fixed Gaps |
|---------|------------|
| V1 | Invented generic Python plugin shape instead of Hermes `MemoryProvider`; assumed Sanctum tables replace SOUL.md/USER.md (they mirror); row-level locking alone insufficient for Wolf collisions; privacy gate ordering not structurally enforced |
| V2 | Added: authority rule between `wolf_sessions` and `specialist_workers` (§3.5); Director's `directives` → Registry `task_queue` linkage (§3.6); token budget enforcement in Router (§5.2); Wolf-write visibility via `prefetch()` + `wolf_status` tool (§7.4) |
| V2 (post-SOUL.md review) | **Sudo Protocol** enforcement (§12) — privileged actions require Merrill's consent, now a structural gate (mirrors privacy gate + budget gate) |

---

## System Topology — Four Wings (Implements Briefing §4)

| Wing | Database | Purpose | Access Pattern |
|------|----------|---------|----------------|
| Commons | `quiddity_commons` | Shared global repo: vector embeddings, file metadata, semantic index | Read: all agents; Write: Ingestion Pipeline only |
| Sanctums | `agent_curator`, `agent_coach`, `agent_producer` | Sovereign state per Lead: Soul, user context, memory lore, conversation history, Wolf working memory | Read/Write: owning Lead + its 3 Wolves only. Hard isolation via separate DB |
| Throne | `agent_director` | Otec's strategic plans, cross-agent directives, global snapshots | Read/Write: Director only |
| Registry | `agent_registry` | Control plane: agent metadata, API keys, worker mappings, service discovery, rate limits, central Task Queue | Read/Write: orchestrator/admin/claiming workers |

**Naming**: Production DBs use `agent_{slug}`  
**Public mapping**: Zeon7→Curator→`agent_curator`; Leon→Producer→`agent_producer`; Gemma→Coach→`agent_coach`; Otec→Director→`agent_director`

**Wolves**: No separate DBs. Partitioned inside Lead's Sanctum by `wolf_id` + namespaced keys (§7).

---

## Database Schemas (DDL) — MariaDB 11.8+, InnoDB, utf8mb4, native VECTOR + HNSW

### Commons (`quiddity_commons`)
- `quiddity_files` — file metadata, indexing status
- `quiddity_vector_references` — chunks + `embedding VECTOR(1024)` + **HNSW index** (M=16, efConstruction=200, cosine)
- `conversation_vectors` — cross-agent conversation embeddings for shared recall

### Sanctum Template (per Lead)
- `soul` — **mirrors SOUL.md** (canonical file remains SOUL.md; table populated once at migration, then only via `on_memory_write` hook §6.6)
- `user_context` — **mirrors USER.md** (same rule)
- `memory_lore` — long-term memory/lore. **UNIQUE (agent_slug, namespace, key_name)** → Wolf key-collision avoidance mandatory
- `conversation_history` — full message log with `wolf_id` column for Wolf-authored rows. **UNIQUE (agent_slug, session_id, message_seq)** prevents double-insert on bursty sync
- `wolf_sessions` — **Sanctum-local CACHE** of `specialist_workers` state (status, heartbeat, current task). **Authority rule**: `agent_registry.specialist_workers` is source of truth; this table updated in same PHP transaction (§3.5)
- `wolf_working_memory` — transient scratchpad, Wolf-scoped, TTL via `expires_at`

### Registry (`agent_registry`)
- `agents` — agent metadata, API key hash, scopes, rate limits
- `specialist_workers` — **Single source of truth for Wolf live status/heartbeat system-wide**. Registry needs global view for rate-limiting, health monitoring, Director oversight. Dual-write transaction keeps Sanctum `wolf_sessions` in sync.
- `token_budget_ledger` — **Enforces Cognitive Router daily budget**. Incremented by PHP `ConversationController` on cloud-tier messages (reads `tokens_input` + `tokens_output`). Router queries `/v1/registry/budget?tier={tier}` before routing.
- `privileged_action_log` — **Sudo Protocol enforcement** (§14). Every SOUL.md/USER.md asserts "privileged actions require Merrill's consent"; this table makes it a technical gate. Actions: `sql_ddl`, `sudo_command`, `schema_alter`, `production_deploy`, `destructive_file_op`. Flow: request → log `pending` + `confirmation_code` → Merrill reads code → submits `/confirm` → executes.
- `task_queue` — Wolf dispatch. **Atomic claim pattern mandatory** (row-level locking alone fails: two Wolves can read 'queued' before either writes). Must `UPDATE ... SET status='claimed' WHERE status='queued' AND id=... RETURNING *`.
- `api_keys` — credential management

### Director (`agent_director`)
- `strategic_plans` — long-term plans with dependencies, assigned agents
- `directives` — actionable orders. **Critical**: `POST /v1/director/directives` writes to `directives` **AND** dispatches rows into `agent_registry.task_queue` linked by `directive_id` in same request (§3.6). This is the **only path** a directive becomes visible to a Wolf.

---

## PHP 8.1+ REST API Service Contract (Implements Briefing §2 Pillar Three)

**Iron rule**: Python **never touches MariaDB directly**. All access via PHP API. Strict JSON payloads.

### Auth Headers (every request)
- `Authorization: Bearer <key>` → validated vs `agent_registry.api_keys`
- `X-Agent-ID: <agent_slug>` — fixed per deployed profile (§1.2)
- `X-Wolf-ID: <wolf_id>` — optional, when Wolf acts for Lead
- `X-Request-ID: <uuid>` — distributed tracing

### Key Endpoints

| Area | Method | Endpoint | Purpose |
|------|--------|----------|---------|
| Soul | GET/PUT | `/v1/sanctum/soul` | Retrieve/upsert identity mirror (called by `on_memory_write`, not conversational agents) |
| User Context | GET/PUT | `/v1/sanctum/user-context` | Retrieve/upsert human profile mirror |
| Memory/Lore | GET/POST/PUT/DELETE | `/v1/sanctum/memory/...` | CRUD + hybrid search (FTS + vector) |
| Conversations | GET/POST | `/v1/sanctum/conversations/...` | List sessions, get messages, create session, **append message** (`sync_turn()` target) |
| Commons | GET/POST | `/v1/commons/...` | List files, trigger re-index (Pipeline only), semantic search, get chunks |
| Ingestion | POST | `/v1/commons/ingest/batch` | **Pipeline only**. Parallel ingest: chunking config, embedding model, concurrency, callback URL |
| Wolves | GET/POST | `/v1/sanctum/wolves/...` | Status, dispatch task, poll task, Wolf working memory upsert |
| Director | POST | `/v1/director/plans` | Create strategic plan |
| Director | POST | `/v1/director/directives` | **Dual-write**: `agent_director.directives` + `agent_registry.task_queue` (linked by `directive_id`) |
| Director | GET | `/v1/director/status` | Global health |
| Registry | GET | `/v1/registry/budget?tier={tier}` | Router calls before cloud routing. Returns `{tier, usage_date, tokens_used, daily_limit, remaining}` |
| Registry | GET/POST | `/v1/registry/privileged-actions/...` | Sudo Protocol: poll status, submit confirmation code |
| Health | GET | `/v1/healthz`, `/v1/readyz`, `/v1/metrics` | Liveness, readiness (embedding model loaded, indexes warm), Prometheus |

### PHP File Structure
```
php-api/
├── composer.json
├── public/index.php          # FastRoute front controller
├── src/
│   ├── bootstrap.php         # DI container, PDO, JWT
│   ├── Middleware/
│   │   ├── Auth.php          # Bearer → agent_slug + scopes
│   │   ├── AgentContext.php  # Injects X-Agent-ID, X-Wolf-ID
│   │   └── RateLimit.php
│   ├── Controller/
│   │   ├── SoulController.php
│   │   ├── MemoryController.php
│   │   ├── ConversationController.php
│   │   ├── CommonsController.php
│   │   ├── IngestionController.php
│   │   ├── WolfController.php
│   │   ├── DirectorController.php
│   │   └── RegistryController.php
```

---

## Hermes Integration (§6)

### MemoryProvider Interface
Hermes expects a `MemoryProvider` implementation. The skill provides `MariaDBMemoryProvider` implementing:
- `read_soul()`, `write_soul()` → `/v1/sanctum/soul`
- `read_user_context()`, `write_user_context()` → `/v1/sanctum/user-context`
- `search_memory()`, `upsert_memory()`, `delete_memory()` → `/v1/sanctum/memory/...`
- `append_conversation()`, `get_conversation()` → `/v1/sanctum/conversations/...`
- `prefetch()` — **pulls Wolf-written rows from Sanctum into active context** (solves Wolf-write visibility §7.4)

### Profile Binding (Worzel Gummidge)
Each Hermes profile permanently bound to one Sanctum at setup. **No agent-slug switching mechanism needed** — swap profile = swap process.

### Sync Turn Hook
`sync_turn(messages, session_id)` → POST `/v1/sanctum/conversations/{session_id}/messages` with full message array (including `wolf_id` for Wolf-authored). **UNIQUE constraint** on `(agent_slug, session_id, message_seq)` prevents double-insert.

### On Memory Write Hook
`on_memory_write(key, value)` → PUT `/v1/sanctum/soul` or `/v1/sanctum/user-context` **only for those tables**. Other memory writes go to `memory_lore` via standard endpoint.

---

## Cognitive Router Implementation (§5)

### Three Layers (matches Briefing §7)
| Layer | Config Key | Model/Provider | Purpose |
|-------|------------|----------------|---------|
| 1 | `model.system1` | Local (e.g., `ollama/llama3.1:8b`) | Reflex, privacy-gated, free, instant |
| 2 | `model.system2_light` | Cloud light (e.g., `openrouter/google/gemini-flash-1.5`) | Coding, formatting, logic > local RAM |
| 3 | `model.system2_heavy` | Cloud heavy (e.g., `openrouter/anthropic/claude-opus-4`) | Architecture, strategy, vast synthesis |

### Router Logic (in Python core, **before** any LLM call)
1. **Privacy Gate** — scan prompt for: API keys (`sk-`, `ghp_`, `Bearer`), passwords, local paths (`C:\Users`, `/home/`), bank details, medical terms. **Match → force Layer 1**.
2. **Budget Check** — call `GET /v1/registry/budget?tier=system2_light` (or `system2_heavy`). `tokens_used >= daily_limit` → **step down to Layer 1**.
3. **Complexity Score** — heuristic: token count, code blocks, multi-step reasoning keywords. High score → Layer 2/3.
4. **Fail-Safe** — if privacy-gated request hits Layer 1 but local model unavailable → **hard exception, halt, alert**. No silent cloud fallback.

### Config (config.yaml)
```yaml
cognitive_router:
  enabled: true
  privacy_patterns:
    - "sk-[a-zA-Z0-9]{32,}"
    - "ghp_[a-zA-Z0-9]{36}"
    - "C:\\\\Users\\\\"
    - "/home/"
    - "\\b\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}[-\\s]?\\d{4}\\b"  # credit card
  budget_tiers:
    system2_light: 500000   # daily tokens
    system2_heavy: 100000
```

---

## Wolf Operations (§7)

### Dispatch Flow
1. Lead calls `POST /v1/sanctum/wolves/{wolf_id}/task` with `{action, payload_json, priority}`
2. PHP writes to `agent_registry.task_queue` (`status='queued'`, `target_agent_slug`, `target_worker_id`)
3. Wolf (background Python process) polls `GET /v1/sanctum/wolves/{wolf_id}/task` → PHP claims atomically:
   ```sql
   UPDATE task_queue
   SET status='claimed', claimed_by_worker_id=?, claimed_at=NOW()
   WHERE id=? AND status='queued'
   RETURNING *;
   ```
4. Wolf processes, writes results to `result_json`, updates `status='completed'`/`'failed'`
5. Lead polls or receives callback → reads synthesis from Sanctum (`wolf_working_memory` or `memory_lore`)

### Wolf Working Memory
- `wolf_working_memory` table: transient, Wolf-scoped (`UNIQUE (wolf_id, namespace, key_name)`), TTL via `expires_at`
- `memory_lore` for persistent synthesis: `source_type='wolf_synthesis'`, namespaced keys (avoid collision via `UNIQUE (agent_slug, namespace, key_name)`)

### Authority Rule (Critical)
`agent_registry.specialist_workers` = **single source of truth** for Wolf status/heartbeat system-wide.  
Sanctum `wolf_sessions` = **read-optimized cache** for Lead's own 3 Wolves.  
**Dual-write in one PHP transaction** (WolfController) keeps them in sync. Never write `wolf_sessions` independently.

---

## Sudo Protocol Enforcement (§12 / §14)

**Problem**: Every SOUL.md/USER.md asserts "privileged actions require Merrill's consent" — but was only prompt-level convention.

**Solution**: Structural gate at PHP API layer.

### Protected Actions
- `sql_ddl` — `CREATE/ALTER/DROP TABLE`, `CREATE INDEX`
- `sudo_command` — shell commands via `terminal` tool with elevated risk
- `schema_alter` — migration scripts
- `production_deploy` — CI/CD pipeline triggers
- `destructive_file_op` — `rm -rf`, `git reset --hard`, bulk deletions

### Flow
1. Agent/Wolf requests privileged action via tool → PHP logs to `privileged_action_log` with `status='pending'`, generates `confirmation_code` (8-char)
2. Code returned to agent → agent shows Merrill: *"Confirm code `X7K9M2P1` to proceed with DROP TABLE quiddity_files"*
3. Merrill replies with code → agent calls `POST /v1/registry/privileged-actions/{id}/confirm` with code
4. PHP verifies code match → executes original action → logs `status='confirmed'`, `confirmed_by='merrill_leo'`, `executed_at`, `result_json`

**Mirrors privacy gate + budget gate**: enforce upstream, not in model.

---

## Key Operational Checks for Leon

| Check | Command | Expected |
|-------|---------|----------|
| MariaDB version | `mariadb --version` | **11.8+** (current: 10.11.13 — **upgrade required**) |
| Vector index exists | `SHOW INDEX FROM quiddity_vector_references;` | `idx_vector_hnsw` with `index_type=VECTOR` |
| PHP API health | `curl localhost/v1/healthz` | `{"status":"ok","db":"connected"}` |
| Readiness | `curl localhost/v1/readyz` | `{"embedding_model":"loaded","indexes":"warm"}` |
| Token budget | `curl -H "Authorization: Bearer ..." localhost/v1/registry/budget?tier=system2_light` | JSON with `remaining > 0` |
| Wolf heartbeat | `SELECT * FROM specialist_workers WHERE parent_agent_slug='leon';` | 3 rows, `status='idle'`, recent `last_heartbeat` |

---

## Migration Notes (from V1)

- `soul` / `user_context` tables: **do not** replace SOUL.md/USER.md. Hermes reads/writes files directly. Tables are mirrors for SQL tooling/backup.
- `wolf_sessions` is a **cache** — never the authority.
- `directives` table must dual-write to `task_queue` — no separate dispatch step.
- `token_budget_ledger` must be incremented by `ConversationController` on every cloud-tier message append.
- `privileged_action_log` is new — add to PHP API and expose via RegistryController.

---

## Cross-References
- `references/council-library-briefing-v5.md` — philosophy, terminology, Wolves, Router, Skills
- `references/quiddity-lore-sea-index.md` — full document index