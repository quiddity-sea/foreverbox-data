# PHP API Security Hardening — Verified Implementations (Plutus Phase 1, 2026-07-31)

Verified end-to-end against the live HTTPS API. All patterns are generic PHP +
Apache + MariaDB; backend edits applied as www-data (see SKILL.md for the
www-data edit workflow). This file is the verified-detail companion to the
`foreverbox-project-development` skill's Security Patterns section.

## 1. CSRF Protection

### Server side (`api.php` — top of file, after `session_start`)
```php
if (empty($_SESSION['csrf_token'])) {
    $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
$action = $_GET['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];
$csrfExempt = in_array($action, ['login', 'check_session'], true);
if (in_array($method, ['POST', 'PUT', 'DELETE'], true) && !$csrfExempt) {
    $sentToken = $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
    if ($sentToken === '' || !hash_equals($_SESSION['csrf_token'], $sentToken)) {
        http_response_code(403);
        echo json_encode(['success' => false, 'error' => 'CSRF validation failed']);
        exit;
    }
}
```

### Token rotation on login
Regenerate the token on every successful login AND return it in the response:
```php
$_SESSION['csrf_token'] = bin2hex(random_bytes(32));
response(['success' => true, 'csrf_token' => $_SESSION['csrf_token']]);
```
Pitfall hit in session: if the frontend only reads the meta tag once, the token
goes stale after login and every subsequent mutating call 403s. Wrap `$.ajax`
to refresh the meta tag from any response carrying `csrf_token`.

### Client side (`app.js`)
```javascript
$.ajaxSetup({
    beforeSend: function(xhr) {
        var token = $('meta[name="csrf-token"]').attr('content');
        if (token) xhr.setRequestHeader('X-CSRF-Token', token);
    }
});
```

### HTML (`index.php`)
```html
<meta name="csrf-token" content="<?php echo $_SESSION['csrf_token'] ?? ''; ?>">
```

### Verified behaviour
- POST without token -> 403 `{"success":false,"error":"CSRF validation failed"}`
- POST with token -> passes (create/update/delete succeed)
- `login` / `check_session` remain exempt

## 2. Rate Limiting (file-based, fixed window + token bucket)

### CRITICAL path pitfall (hit in session)
`__DIR__ . '/../../runtime/rate_limit'` from a class at the **web root**
(`/var/www/site/RateLimiter.php`) resolves to `/var/runtime/rate_limit` — two
levels up, outside the site, unwritable. The correct default is
`__DIR__ . '/runtime/rate_limit'` (one level down from the web root). Always
resolve `__DIR__` relative to where the class actually lives.

### Class essentials (`RateLimiter.php`)
- Per-key JSON state file under the store dir.
- `mode='window'`: max N hits per T seconds (login).
- `mode='bucket'`: capacity + refill tokens/sec (generic API).
- `allow($record)` -> bool; `retryAfter()` -> seconds; `reset()` clears window (call on successful auth).

### Wiring into login
```php
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$limiter = new RateLimiter('login_' . $ip, ['mode' => 'window', 'max' => 5, 'window' => 900]);
if (!$limiter->allow(false)) {
    http_response_code(429);
    header('Retry-After: ' . $limiter->retryAfter());
    echo json_encode(['success' => false, 'error' => 'Too many login attempts. Try again later.']);
    exit;
}
// ... on success:  $limiter->reset();
// ... on failure:  $limiter->allow(true);  // record the attempt
```

### Verified behaviour
- Attempts 1–5 with wrong password -> 401
- Attempt 6 -> 429 with `Retry-After: 900` header
- Success resets the window so a legitimate user who fumbled a few times is not locked out
- Add `runtime/` to .gitignore

## 3. Audit Trail

### Migration (`001_audit_log.sql`)
```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id INT UNSIGNED NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_action (user_id, action),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Class (`AuditLog.php`)
- `AuditLog::log($pdo, $userId, $action, $entityType, $entityId, $old, $new)`.
- Wrap in try/catch + `error_log` — audit failures must never break the primary request.
- Capture `$_SERVER['REMOTE_ADDR']` and `HTTP_USER_AGENT` server-side.

### create-vs-update pitfall (hit in session)
`save_object` does `$id = $pdo->lastInsertId()` on insert, so testing `$id` at
the END of the handler always says "update". Capture `$isNew = !$id` BEFORE the
INSERT/UPDATE branch and audit with `$isNew ? 'create' : 'update'`.

## 4. Soft Deletes

### Migration (`002_soft_deletes.sql`)
Add `deleted_at TIMESTAMP NULL DEFAULT NULL` to every entity table:
budgets, categories, transactions, transaction_items, items, vendors, projects,
project_zones, improvements. (Not users/tasks/audit_log per plan.)

### API changes
- `delete_object` -> `UPDATE ... SET deleted_at = NOW() WHERE id = ?` instead of DELETE.
- `get_objects` and `get_metadata` -> `WHERE deleted_at IS NULL`.
- New `restore_object` action -> `UPDATE ... SET deleted_at = NULL`.
- `get_objects` honours `show_deleted=1`: `$showDeleted = !empty($_GET['show_deleted']) ? 'WHERE deleted_at IS NOT NULL' : 'WHERE deleted_at IS NULL';`
- Dashboard budget query also filters `deleted_at IS NULL` on budgets AND joined transactions.

### Frontend (`app.js`)
- "SHOW DELETED / HIDE DELETED" toggle in the list header -> refetches `get_objects&show_deleted=1`, repopulates metadata.
- Row actions: when `item.deleted_at` is set, show restore button instead of edit/delete.

### Verified behaviour
delete -> row still in DB with `deleted_at` set -> hidden from normal list -> restore -> visible again.

## 5. Verification Recipe (HTTPS + self-signed cert)

```bash
curl -sk -c /tmp/cookies.txt -X POST "https://site/api.php?action=login" \
  -d "username=test&password=pass" -o /tmp/login.json -w "HTTP %{http_code}\n"
TOKEN=$(python3 -c "import json;print(json.load(open('/tmp/login.json')).get('csrf_token',''))")
curl -sk -b /tmp/cookies.txt -X POST "https://site/api.php?action=save_object" \
  -H "X-CSRF-Token: $TOKEN" -d "entity_type=zone&name=__test__"
```

- Always use `-k` (self-signed cert) — without it curl returns HTTP 000 / connect failure.
- Always pass `-c`/`-b` cookie jar so the session (and its CSRF token) persists between calls.
- Use a distinctive `__` prefix for test rows so cleanup is unambiguous; clean test users/rows before reporting.
