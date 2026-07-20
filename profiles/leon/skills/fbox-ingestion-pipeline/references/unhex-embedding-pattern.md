# UNHEX Embedding Insert Pattern

## Problem

The embedding service returns hex-encoded float32 vectors (e.g. `"859e3d3c..."`). The database column is `VECTOR(384)`. The ingestion worker was crashing with `Incorrect vector value` because it was passing raw binary via `hex2bin()` directly to the prepared statement.

## Root Cause

MariaDB's `VECTOR` type does not accept raw binary via PDO parameter binding. The hex string must be passed to `UNHEX()` inside the SQL query itself.

## Correct Pattern (Worker)

```php
// CORRECT — hex string passed to SQL function:
$stmt = $pdo->prepare("INSERT INTO quiddity_vector_references (...) VALUES (?, ?, ?, ?, ?, UNHEX(?))");
$stmt->execute([..., $hexString]);

// WRONG — raw binary binding fails:
$binary = hex2bin($hexString);
$stmt->execute([..., $binary]); // FAILS: "Incorrect vector value"
```

## The EmbeddingClient Trap

`/foreverbox_data/council-library/php-api/src/Service/EmbeddingClient.php` uses `hex2bin()` to return binary vectors. It is fine for in-memory operations but MUST NOT be used for database inserts. For ingestion, fetch hex directly from the embedding service:

```php
// Fetch hex strings directly from the Python embedding service:
$hexEmbeddings = getEmbeddings($chunks, $embeddingUrl);
// Then pass to UNHEX(?):
$stmt->execute([$fileId, $i, $text, $tokens, $meta, $hexEmbedding]);
```

## Column Name

The DB column is `chunk_token_count`, NOT `token_count`. Mismatch causes `SQLSTATE[42S22]`.

## MIME Type for PDFs

PDFs registered as `text/markdown` will be ingested as raw binary. Fix:
```sql
UPDATE quiddity_files SET mime_type='application/pdf' WHERE relative_path LIKE '%.pdf';
```
