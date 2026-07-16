# PHP-Side Vector Similarity — Dot Product on Normalized Vectors

MariaDB 11.8 Community (Ubuntu build) has VECTOR storage but no `VECTOR_DISTANCE` function or `<->` operator. The fix: compute cosine similarity in PHP using the dot product on L2-normalized vectors.

## Architecture

```
Query text → EmbeddingClient (Python μservice) → hex-encoded vector → PHP
Candidate vectors → MariaDB SELECT HEX(embedding) → hex strings → PHP unpack('f*', hex2bin(...))
PHP: dotProduct(queryFloats, candFloats) → sort → top-K
```

## PHP Implementation

```php
private function vectorSearch(string $query, int $limit): array
{
    $queryVec = $this->embedder->embedOne($query);
    if (!$queryVec) return $this->fulltextSearch($query, $limit);

    // Load candidates (limit to ~200 for acceptable latency)
    $stmt = $this->pdo->query(
        "SELECT qvr.id, qvr.chunk_text, HEX(qvr.embedding) as emb_hex, ...
         FROM quiddity_vector_references qvr
         WHERE qvr.embedding IS NOT NULL
         LIMIT 200"
    );
    $candidates = $stmt->fetchAll();

    $queryFloats = self::bytesToFloats($queryVec);
    foreach ($candidates as &$row) {
        $row['similarity'] = self::dotProduct(
            $queryFloats,
            self::bytesToFloats(hex2bin($row['emb_hex']))
        );
    }
    usort($candidates, fn($a, $b) => $b['similarity'] <=> $a['similarity']);
    return array_slice($candidates, 0, $limit);
}

// PHP unpack('f*', $bytes) decodes 4-byte float32 little-endian values
private static function bytesToFloats(string $bytes): array
{
    return array_values(unpack('f*', $bytes));
}

// Cosine similarity = dot product for L2-normalized vectors
private static function dotProduct(array $a, array $b): float
{
    $sum = 0.0;
    for ($i = 0, $n = min(count($a), count($b)); $i < $n; $i++)
        $sum += $a[$i] * $b[$i];
    return $sum;
}
```

## Performance

- 384 dimensions × 200 candidates = ~77K float multiplications
- PHP handles this in < 5ms
- Results carry `similarity` key in [0, 1] range
- Higher = more similar (cosine similarity on normalized vectors)

## Verified Results

All queries tested against 163 chunks of the V6 Master Briefing:

| Query | Top Result | Similarity |
|-------|-----------|------------|
| quantum lattice consciousness | "The Quantum Lattice Connection" | 0.65 |
| privacy sanctum | "The Sanctums are the private memory chambers" | 0.76 |
| memory architecture | "durable intelligence requires durable memory" | 0.65 |

## Pitfalls

1. **Candidate limit**: Loading all vectors gets slow above ~500. Keep the LIMIT at 200.
2. **HEX() overhead**: MariaDB's `HEX(embedding)` serialises 1,536 bytes to 3,072 hex chars per row — fine at 200 rows but expensive at scale.
3. **Embedding service must be up**: If unavailable, falls back to FULLTEXT. Results carry `relevance` key instead of `similarity`.
4. **Single-threaded PHP**: The built-in server can only handle one request at a time. Under Apache/FPM, multiple workers can score in parallel.
