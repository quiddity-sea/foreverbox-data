# Embedding Integration Pattern — Council Library

How the PHP API, ingestion worker, and FolderRouter integrate with a Python embedding microservice for vector search.

## Architecture

```
PHP API ──HTTP──► Python embedding_service.py (Flask-like HTTP server)
                      │
                      ├── Model: all-MiniLM-L6-v2 (384-dim, ~120 MB, fast CPU)
                      ├── Port: 8900 (configurable)
                      ├── POST /embed  {"texts": [...]} → {"embeddings": ["hex...", ...]}
                      └── GET /health   → {"status": "ok"}
```

## Components

### 1. Embedding Service (`scripts/embedding_service.py`)
- Standalone Python HTTP server using `sentence_transformers`
- Loads model once at startup, keeps it warm in memory
- Accepts batch embedding requests via POST /embed
- Returns hex-encoded float32 vectors

### 2. PHP EmbeddingClient (`src/Service/EmbeddingClient.php`)
- Wraps curl calls to the embedding service
- `isAvailable()` — health-checked at construction, cached
- `embed(array $texts): array` — batch embed, returns binary vectors
- `embedOne(string $text): ?string` — single embed, returns binary or null
- Graceful fallback: returns empty array on any failure

### 3. VectorSearch (`src/Service/VectorSearch.php`)
- `search(query, limit)` — dispatches to vectorSearch or fulltextSearch
- `vectorSearch()` — embeds query, loads up to 200 candidates from MariaDB, computes cosine similarity (dot product on L2-normalized vectors) in PHP using `unpack('f*')` and a manual dot-product loop. Returns results ordered by similarity descending.
- `fulltextSearch()` — MATCH AGAINST fallback when embedding service is down or vectorSearch fails
- Auto-detects: if `$this->embedder->isAvailable()`, uses vectors; otherwise FULLTEXT
- **Why PHP-side dot product**: MariaDB 11.8 Community (Ubuntu) has no `VECTOR_DISTANCE` function and no `<->` operator. These are MariaDB features not compiled into the default Ubuntu package. The workaround is fast enough at 384 dimensions × 200 candidates (~60K float multiplications per search).

### 4. Ingestion Worker (`scripts/ingestion_worker.php`)
- Calls `getEmbeddings(texts, embeddingUrl)` before storing chunks
- Stores binary vectors in `quiddity_vector_references.embedding`
- Silent failure: if embedding service is down, chunks stored without embeddings (search degrades to FULLTEXT)

### 5. FolderRouter (`src/Service/FolderRouter.php`)
- `classify()` tries vector classification first, keyword fallback second
- Vector path: embeds document, queries `quiddity_folder_centroids` with `VECTOR_DISTANCE`
- Cosine similarity threshold: 0.3 (below → `_review/`)
- Falls back to keyword scoring when no embeddings or no centroids exist

## Startup
```bash
# Start embedding service
/usr/bin/python3.12 /foreverbox_data/council-library/scripts/embedding_service.py --port 8900 &

# Test
curl -X POST http://127.0.0.1:8900/embed \
  -H "Content-Type: application/json" \
  -d '{"texts":["hello world"]}'
```

## Pitfalls
- **Sentence-transformers install is ~2 GB** (PyTorch + CUDA + NVIDIA libs). Plan for download time on residential connections.
- **Python version matters**: Homebrew Python 3.14 can't see packages installed for 3.12. Use `/usr/bin/python3.12` explicitly.
- **PEP 668 on Ubuntu 24.04** blocks `pip install`. Use `--break-system-packages` flag.
- **VECTOR column dimension must match**: MariaDB enforces exact byte-length match between stored vector and column definition. all-MiniLM-L6-v2 is 384-dim (1,536 bytes). If the column is `VECTOR(1024)` (4,096 bytes), insertion fails. **Fix**: ALTER columns to `VECTOR(384) NOT NULL`. Must drop vector index first, alter column, then re-add index — `ALTER TABLE ... MODIFY COLUMN` with an active vector index returns `ERROR 1252`.
- **Embedding service health check is POST-only**: The `/health` endpoint only handles POST requests. `checkHealth()` must set `CURLOPT_POST => true`, otherwise gets HTTP 501.
- **EmbeddingClient must re-check availability**: The embedding service may start after the PHP API server. Caching `$available = false` from constructor is insufficient. `embed()` re-checks on each call when `$available` is false.
- **PDO cannot bind binary VECTOR data**: Use `UNHEX(:hex)` in SQL and pass hex-encoded strings from PHP. The embedding service returns hex-encoded float32 bytes directly — pass them through to UNHEX without hex2bin conversion.
- **MariaDB 11.8 Community has no VECTOR_DISTANCE**: No standalone function, no `<->` operator. Cosine similarity must be computed in application code.
