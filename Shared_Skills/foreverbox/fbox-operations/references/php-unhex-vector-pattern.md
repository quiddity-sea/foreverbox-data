# PHP UNHEX Pattern for MariaDB VECTOR Storage

## Problem

MariaDB's VECTOR column type stores binary float32 data. PDO mangles binary
data when using prepared statements — the `?` placeholder treats binary as
a string and introduces escape characters, corrupting the vector.

## Pattern

Never pass raw binary to PDO for VECTOR columns. Instead:

1. **Embedding service** returns vectors as hex strings: `numpy_array.tobytes().hex()`
2. **PHP code** passes the hex string to PDO, using `UNHEX()` in the SQL:

```php
// Correct
$stmt = $pdo->prepare(
    "INSERT INTO quiddity_vector_references
     (file_id, chunk_index, chunk_text, chunk_token_count, chunk_metadata, embedding)
     VALUES (?, ?, ?, ?, ?, UNHEX(?))"
);
$stmt->execute([
    $fileId, $chunkIndex, $chunkText, $tokenCount,
    json_encode($metadata), $hexString,  // ← hex, not binary
]);
```

## Ingestion Worker Flow

1. `getEmbeddings()` returns hex strings directly from the embedding service
2. Worker passes hex to `UNHEX(?)` in the INSERT
3. No `hex2bin()` or `bin2hex()` round-trips — straight hex path

```php
function getEmbeddings(array $texts, string $url): array
{
    // curl POST to embedding service
    $data = json_decode($response, true);
    return $data['embeddings'] ?? [];  // hex strings
}
```

## Centroid Generator (Python)

Same pattern in Python with mysql.connector:

```python
centroid_hex = centroid.astype(np.float32).tobytes().hex()

cursor.execute(
    "INSERT INTO quiddity_folder_centroids "
    "(folder_name, centroid, sample_count) "
    "VALUES (%s, UNHEX(%s), %s) "
    "ON DUPLICATE KEY UPDATE centroid=UNHEX(VALUES(centroid)), "
    "sample_count=VALUES(sample_count), rebuilt_at=NOW()",
    (folder, centroid_hex, len(rows)),
)
```

## PHP-Side Vector Similarity

When computing cosine similarity, convert the hex back to binary with
`hex2bin()` then unpack to floats:

```php
$queryFloats = array_values(unpack('f*', $queryVec));  // direct binary
$candFloats = array_values(unpack('f*', hex2bin($row['emb_hex'])));  // from hex
$similarity = self::dotProduct($queryFloats, $candFloats);
```

## Verification

```bash
# Test directly: hex → UNHEX → stored vector
mariadb -e "INSERT INTO _v384 VALUES (1, UNHEX('00000000...'));"
# 1 row inserted — no "Incorrect vector value" error
```

## Pitfalls

- `bin2hex()` + `hex2bin()` round-trip is wasteful — keep hex all the way
- PDO::PARAM_LOB does NOT help — MariaDB still rejects the binary
- MariaDB CLI accepts hex directly via `X'...'` syntax, but PDO doesn't
- `UNHEX()` in SQL is universal — works in CLI, PDO, and mysql.connector
