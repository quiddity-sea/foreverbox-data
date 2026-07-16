# MariaDB VECTOR INDEX — Actual Syntax vs. Blueprint Spec

Blueprint V2.0 specified vector indexes with `INDEX_OPTIONS` JSON syntax:

```sql
ALTER TABLE quiddity_vector_references
    ADD VECTOR INDEX idx_vector_hnsw (embedding)
    INDEX_OPTIONS '{"type": "hnsw", "M": 16, "efConstruction": 200, "distance_metric": "cosine"}';
```

**This does not work in MariaDB 11.8.8.** The actual syntax is:

```sql
ALTER TABLE quiddity_vector_references
    ADD VECTOR INDEX idx_vector_hnsw (embedding);
```

No algorithm, distance metric, M, or efConstruction parameters are accepted. MariaDB 11.8 defaults to HNSW with cosine distance internally. The `INDEX_OPTIONS` clause causes a syntax error at the `{` character.

## Discovered Limits

1. **One vector index per table.** Trying to add a second vector index returns: `ERROR 1235: This version of MariaDB doesn't yet support 'multiple VECTOR indexes'`

2. **VARCHAR primary keys conflict with vector indexes.** When a table has `folder_name VARCHAR(128) PRIMARY KEY` and a vector column, `ADD VECTOR INDEX` fails with: `ERROR 1071: Primary key was too long for vector indexes, max length is 256 bytes`. This is because InnoDB concatenates the primary key with the vector index key internally, and VARCHAR(128) in utf8mb4 = 512 bytes, exceeding the 256-byte limit. **Fix**: use `INT UNSIGNED AUTO_INCREMENT PRIMARY KEY` with `folder_name VARCHAR(128) NOT NULL UNIQUE` as a separate column.

3. **Maximum dimension: tested up to 1024** (BAAI/bge-m3 output). MariaDB 11.8.8 accepts VECTOR(1024) columns and creates indexes on them — the dimension itself is not the bottleneck.

4. **No `VECTOR_DISTANCE` function.** MariaDB 11.8 does not provide a standalone `VECTOR_DISTANCE()` SQL function. `SELECT VECTOR_DISTANCE(a.embedding, :vec)` returns `ERROR 1305: FUNCTION quiddity_commons.VECTOR_DISTANCE does not exist`. The `<->` operator also does not exist. HNSW index search works internally but explicit distance computation between two arbitrary vectors is not available as a SQL function. **Impact**: the `VectorSearch::vectorSearch()` method must fall back to FULLTEXT. Cosine similarity must be computed in application code (PHP or embedding service), not SQL.

5. **PDO binary insertion fails for VECTOR columns.** Direct PDO binding of binary vector data to a VECTOR column fails with `SQLSTATE[22007]: Incorrect vector value`. **Fix**: use `UNHEX()` in SQL — convert binary to hex in PHP, pass as string: `INSERT INTO ... VALUES (..., UNHEX(:hex_vector))`. CLI accepts `X'...'` hex literals but PDO mangles raw binary through prepared statements.

4. **PHP-side vector similarity (the VECTOR_DISTANCE workaround)**. Since MariaDB 11.8 has no `VECTOR_DISTANCE` or `<->`, compute cosine similarity in PHP with dot product on normalized vectors. See `references/php-vector-similarity-pattern.md`.

## Blueprint V3.0 Fix

The blueprint's `INDEX_OPTIONS` clauses were replaced with plain `ADD VECTOR INDEX` in all three tables:
- `quiddity_vector_references.embedding`
- `conversation_vectors.embedding`  
- `quiddity_folder_centroids.id` (INT primary key, centroid as separate column)

## Verification

```sql
-- Test vector index creation
DROP TABLE IF EXISTS _vtest;
CREATE TABLE _vtest (id INT PRIMARY KEY, v VECTOR(3) NOT NULL);
INSERT INTO _vtest VALUES (1, X'0000803F0000803F0000803F');
ALTER TABLE _vtest ADD VECTOR INDEX (v);
SHOW CREATE TABLE _vtest\G
-- Should show: VECTOR KEY `v` (`v`)
DROP TABLE _vtest;
```
