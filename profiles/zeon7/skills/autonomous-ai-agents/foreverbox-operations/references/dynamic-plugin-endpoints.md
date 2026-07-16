# Dynamic Plugin Endpoints — MemoryController

The `ForeverBoxMemoryProvider` plugin calls PUT endpoints that don't map to the standard `{namespace}/{key_name}` pattern. These are handled by a single `putDynamic()` method.

## Routes Added to index.php

```php
$s->put('/memory/session_summaries/{key}', c(MemoryController::class, 'putDynamic'));
$s->put('/memory/delegation_log/{key}', c(MemoryController::class, 'putDynamic'));
$s->put('/memory/compression_snapshots/{key}', c(MemoryController::class, 'putDynamic'));
$s->put('/memory/hermes_builtin/{action}', c(MemoryController::class, 'putDynamic'));
```

## putDynamic() Method

The method inspects `$args` to determine the namespace:
- `session_summaries`, `delegation_log`, `compression_snapshots` → namespace = prefix, key = `{key}`
- `hermes_builtin` → namespace = `hermes_builtin`, key = `{action}`

Content comes from `$body['content']` (string) or is JSON-encoded if missing. Uses standard INSERT ON DUPLICATE KEY UPDATE pattern — idempotent, same as the regular `upsert()`.

## Plugin-to-API Call Map

| Plugin method | HTTP call | Namespace | Key |
|--------------|-----------|-----------|-----|
| `on_session_end()` | PUT /sanctum/memory/session_summaries/{session_id} | session_summaries | session_id |
| `on_delegation()` | PUT /sanctum/memory/delegation_log/{child_session_id} | delegation_log | child_session_id |
| `on_pre_compress()` | PUT /sanctum/memory/compression_snapshots/{uuid} | compression_snapshots | uuid |
| `on_memory_write()` user target | PUT /sanctum/user-context | (separate endpoint) | — |
| `on_memory_write()` memory target | PUT /sanctum/memory/hermes_builtin/{action} | hermes_builtin | action (add/replace/remove) |

## Verification
```bash
curl -s -X PUT 'http://localhost:8080/v1/sanctum/memory/session_summaries/test' \
  -H "Authorization: Bearer test" -H "X-Agent-ID: curator" \
  -H "Content-Type: application/json" -d '{"content":"test"}'
# → {"success":true,"upserted":true}
```
