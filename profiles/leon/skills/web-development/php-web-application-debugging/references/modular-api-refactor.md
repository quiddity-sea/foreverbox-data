# Modular API Refactor — Verified Patterns (Plutus Phase 3, 2026-07-31)

Phase 3 split a monolithic `api.php` (single file, action switch) into an
`api/` tree while keeping the legacy entry point backward compatible with the
existing frontend (`app.js` calls `api.php?action=...`).

## Target structure

```
api/
├── bootstrap.php          # session, headers, requires, CSRF token seed
├── api.php                # NEW slim entry: bootstrap -> route -> dispatch
├── routes.php             # action => [method, controller, handler, middleware]
├── middleware/
│   ├── Middleware.php     # interface: handle(array &$ctx, callable $next)
│   ├── CsrfMiddleware.php
│   └── RateLimitMiddleware.php
├── controllers/
│   ├── AuthController.php
│   ├── ObjectController.php     # universal CRUD over a schema map
│   └── DashboardController.php
└── utils/
    ├── Response.php             # response() / errorResponse()
    ├── Validator.php            # chainable rules -> 422 on failure
    └── AuditLog.php
```

Legacy `api.php` at the web root becomes a one-line wrapper:
```php
<?php require_once __DIR__ . '/api/api.php';
```

## Middleware chain dispatch (array_reduce pipeline)

```php
$ctx = ['action' => $action];
$stack = [new CsrfMiddleware()];
foreach ($route['middleware'] ?? [] as [$mwClass, $mwCfg]) {
    $stack[] = new $mwClass($mwCfg);
}
$controller = new $route['controller']($pdo);
$dispatch = fn($ctx) => $controller->{$route['handler']}($ctx);
$pipeline = array_reduce(array_reverse($stack),
    fn($next, $mw) => fn($ctx) => $mw->handle($ctx, $next),
    $dispatch);
$pipeline($ctx);
```

Route table pattern:
```php
'login' => ['method' => 'POST', 'controller' => 'AuthController',
            'handler' => 'login',
            'middleware' => [['RateLimitMiddleware', ['key' => 'login', 'max' => 5, 'window' => 900]]]],
```

## Validation layer (Phase 3.4)

- `Validator` class: `rule('required', $f)` / `rule('numeric', $f)` / `enum` / `date`.
- In `save_object`, run required-field rules per entity BEFORE the INSERT/UPDATE branch.
- On failure return 422, not 400, with structured errors:
```php
http_response_code(422);
echo json_encode(['success' => false, 'error' => 'VALIDATION_FAILED', 'fields' => $vErrors]);
exit;
```
Verified: missing `name` on zone -> `422 {"error":"VALIDATION_FAILED","fields":{"name":"FIELD_REQUIRED"}}`.

## API versioning (Phase 3.5)

- Accept header check at the top of the entry point:
```php
$accept = $_SERVER['HTTP_ACCEPT'] ?? '';
if ($accept !== '' && !str_contains($accept, 'application/vnd.plutus.v1+json') && !str_contains($accept, '*/*')) {
    http_response_code(406);
    echo json_encode(['success' => false, 'error' => 'UNSUPPORTED_API_VERSION']);
    exit;
}
header('X-API-Version: v1');
header('Deprecation: version="0"; date="Tue, 31 Jul 2029 00:00:00 GMT"');
```
- Verified: `Accept: application/vnd.plutus.v1+json` -> 200 with `X-API-Version: v1`;
  `Accept: application/vnd.plutus.v2+json` -> 406.
- Be lenient: a bare `Accept: */*` (or absent header) must keep working.

## PITFALL: deleted_at filter vs non-soft-deletable tables (hit in session)

After adding `deleted_at` to entity tables (Phase 1.4), `get_metadata` and
`get_objects` applied `WHERE deleted_at IS NULL` to EVERY schema table —
but `users` (and `audit_log`) never got the column. Result: `get_metadata`
500s with `Unknown column 'deleted_at' in 'WHERE'`.

Fix: a `hasDeletedAt($table)` helper that caches an
information_schema lookup, and only applies the filter when the column exists:
```php
private function hasDeletedAt(string $table): bool
{
    static $cache = [];
    if (!isset($cache[$table])) {
        $stmt = $this->pdo->prepare(
            "SELECT COUNT(*) FROM information_schema.columns
             WHERE table_schema = DATABASE() AND table_name = ? AND column_name = 'deleted_at'");
        $stmt->execute([$table]);
        $cache[$table] = (int)$stmt->fetchColumn() > 0;
    }
    return $cache[$table];
}
// $filter = $this->hasDeletedAt($table) ? "WHERE deleted_at IS NULL" : "";
```

General rule: whenever a soft-delete migration touches SOME tables, any
generic list/metadata endpoint that iterates ALL schemas must guard the
`deleted_at` filter per table.

## Frontend modularisation (Phase 3.2/3.3)

- Vite scaffold at the web root: `package.json` + `vite.config.js`
  (`build.rollupOptions.input = src/main.js`, outDir `dist/`).
- Extract pure modules incrementally: `src/state/appState.js`,
  `src/api/api.js` (fetch wrapper, not jQuery), `src/utils/format.js`.
- `src/main.js` exposes them on `window` (`window.plutusApi = {...}`) so the
  legacy jQuery `app.js` keeps working unchanged until renderers are extracted.
- index.php loads `<script type="module" src="dist/assets/js/main.js">` BEFORE
  the legacy `app.js`.
- JSDoc `@typedef` schema file (`src/types/schema.js`) + `tsconfig.json` with
  `checkJs: true`, `allowJs: true`, `noEmit: true`, include `src/**/*.js` only.
  Exclude `vite.config.js` from checkJs unless `@types/node` is installed.
- Verification: `npm run build` must pass; `npx tsc --noEmit` must pass for src/.
- Gitignore: `node_modules/`, `dist/`, `runtime/` (rate-limiter state dir).
- Build server-side quirk: if the web root is www-data-owned, run npm in a
  user-writable scratch dir (e.g. /tmp) and `sudo cp -r dist/*` into the site,
  then chown www-data and chmod 644.
