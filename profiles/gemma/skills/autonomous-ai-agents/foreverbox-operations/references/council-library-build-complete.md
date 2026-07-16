# Council Library — Build Complete (2026-07-14)

All six stages of the Blueprint §14 migration directive executed. Additionally: embedding integration, vector search, folder classification pipeline, daemon deployment, router hook, installer CLI all built and verified.

## Final State

| Stage | What | Status |
|-------|------|--------|
| 1 | SQL Schema — 6 databases, 30 tables, VECTOR(384) columns | ✓ |
| 2 | PHP API — 8 controllers, 3 middleware, 3 services, Apache vhost | ✓ |
| 3 | Hermes Plugin — Full MemoryProvider ABC, 10 tools, installed in Leon profile | ✓ |
| 4 | Cognitive Router — 3-tier routing (deepseek-v4-pro Layer 3), privacy gate, budget check, hook installed | ✓ |
| 5 | Migration — Core state seeded, token budget, 4h cron, 8 files vectorised (1,470 chunks, 384-dim embeddings) | ✓ |
| 6 | Verification — 17/17 acceptance tests pass | ✓ |
| + | Folder classification — 4 root files routed to correct subfolders, 4 centroids generated | ✓ |
| + | Daemon deployment — systemd user units (embedding, ingestion, wolves), Apache vhost :8080 | ✓ |
| + | Installer CLI — `council-library install/uninstall/enable/disable/status/doctor` | ✓ |

## Running Services

- MariaDB 11.8.8 on `localhost:3306` (user: `zeon7_user`)
- PHP API on `localhost:8080` behind Apache vhost (not php -S)
- Embedding service on `127.0.0.1:8900` (all-MiniLM-L6-v2, 384-dim)
- Ingestion worker: `council-ingestion.service` (polls every 30s)
- Wolf workers: `council-wolves.service` (curator, producer, director)
- Cron: `quiddity-sync` every 4 hours (job ID: `4f948a3d9c3f`)

## Quiddity Lore Sea State

| File | Folder | Chunks | Embedded |
|------|--------|--------|----------|
| ARCHITECTURE_BLUEPRINT_V3.md | 06_QuiddityLtd_Dev_Specs | 352 | ✓ |
| ARCHITECTURE_BLUEPRINT_V2 - 2.md | 06_QuiddityLtd_Dev_Specs | 352 | ✓ |
| V6 Briefing | 02_ReInvigor_Texts | 163 | ✓ |
| V5 Briefing | 02_ReInvigor_Texts | 119 | ✓ |
| FTN Master Handbook v4 | 04_FromTheNoise_Archives | 240 | ✓ |
| Zeon7 updated information | 05_Agent_Profiles | 160 | ✓ |
| Zeon7 Biography | 05_Agent_Profiles | 72 | ✓ |
| Zeon7 ProfileSheet | 05_Agent_Profiles | 12 | ✓ |
| **Total** | **4 folders** | **1,470** | **1,470** |

Centroids: 4 folders (282 + 240 + 244 + 704 sample chunks).

## Key Discoveries During Build

### MariaDB VECTOR INDEX syntax
- Blueprint's `INDEX_OPTIONS` clause doesn't exist in MariaDB 11.8
- Correct: `ADD VECTOR INDEX idx (column)` — no parameters
- MariaDB 11.8 defaults to HNSW with cosine distance
- Only ONE vector index per table
- VARCHAR PK + VECTOR INDEX fails (InnoDB key limit): use INT AUTO_INCREMENT PK with VARCHAR UNIQUE

### PHP API pitfalls
- Slim 4 `Class:method` string format doesn't work with PHP-DI bridge — use closure wrapper pattern
- `clone $pdo` throws Error (PDO not cloneable) — create new PDO for cross-DB access
- `.env` `#` is a comment delimiter — quote values: `DB_PASS="val#with#hash"`
- `$app->addBodyParsingMiddleware()` required before routing for `getParsedBody()`
- Route parameter names in URLs must match controller's `$args` keys (`{ns}` → `$args['ns']`)

### Python environment
- `python3` resolves to Homebrew 3.14, system Python is `/usr/bin/python3.12`
- Packages installed with `pip` go to 3.12's site-packages, invisible to 3.14
- Use `pip install --break-system-packages` on Ubuntu 24.04 (PEP 668)
- Always specify `/usr/bin/python3.12` for scripts that need `mysql.connector` or `requests`

### GitHub setup
- GitHub Desktop on Windows does NOT bridge git config to WSL
- WSL git must be configured independently (user.name, user.email, SSH key)
- `gh` CLI not installed — use SSH key auth directly
- SSH key: `~/.ssh/id_ed25519_github` (ed25519, quiddity-sea/lightweavers74@gmail.com)
- Repo: `github.com/quiddity-sea/council-library` (private)

### Auth & Sudo Protocol
- healthz/readyz must bypass auth middleware — add `PUBLIC_PATHS` skip list
- Sudo Protocol gate is middleware-level, not per-controller — matches HTTP method + path
- APIs that require Sudo confirmation return HTTP 412 with an 8-char confirmation code

### Embedding & Vector Search
- MariaDB 11.8 Community (Ubuntu) has VECTOR storage but NO VECTOR_DISTANCE function. Workaround: PHP-side dot product on normalized vectors.
- VECTOR(1024) columns reject 384-dim vectors — column dimension must match the embedding model. Rebuild with `VECTOR(384)` after dropping and recreating vector indexes.
- PDO binary for VECTOR columns needs `UNHEX()` wrapper — raw binary via bindParam fails.
- Python embedding microservice returns hex-encoded vectors; PHP uses `hex2bin()` but PDO needs hex → use `UNHEX(?)` in SQL, pass hex string directly.
- EmbeddingClient caches availability at construction. Added re-check on each `embed()` call so the API can pick up a late-starting embedding service.
- EmbeddingClient `checkHealth()` sends GET by default — the embedding service only handles POST. Fix: add `CURLOPT_POST => true`.

### Folder Classification Pipeline
- FolderRouter YAML parser: no PHP `ext-yaml`. Built minimal parser handling quoted keys (`"folder_name":`) and `- keyword` list items.
- `vectorClassify()` returning `'_review'` (not null) blocks fallback to keyword matching. Fix: return `null` on PDO failure.
- Full-document keyword scoring skews results — "agent" appears hundreds of times in 113 KB blueprint. Fix: truncate to 4 KB before scoring.
- Apache `rename()` fails silently — check error log. Permissions: `o+w` on target dirs, `o+r` on source files.
- Apache `reload` doesn't clear PHP opcode cache. Fix: `systemctl stop apache2 && systemctl start apache2`.

### Daemon Deployment
- systemd `Environment=` treats `#` as comment — use `EnvironmentFile=` with quoted `.env.production`.
- PHP CLI `$_ENV` not populated on Ubuntu/WSL — use `getenv()` instead.
- `loginctl enable-linger` required for user systemd units to survive logout.
- Apache www-data needs `o+x` on parent directories to traverse to DocumentRoot.
- Apache www-data needs `o+r` on `.env`, `config/*`, `src/*`, `vendor/*`.
- Ingestion worker ENUM values: use 'failed' not 'skipped' (not in schema).
- Zone.Identifier files (Windows ADS metadata) must be filtered out by the worker.
