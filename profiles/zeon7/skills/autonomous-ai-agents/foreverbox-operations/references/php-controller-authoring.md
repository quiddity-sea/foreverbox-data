# PHP Controller Authoring Pattern

How to scaffold a new controller in `/foreverbox_data/council-library/php-api/src/Controller/`.

## Steps

1. **Read `public/index.php`** — find the route group and handler references (`Controller::class . ':method'`)
2. **Read `MemoryController.php`** — the reference implementation: constructor, `json()` helper, error response shapes
3. **Read middleware** (`Auth.php`, `AgentContext.php`, `PrivilegedActionGate.php`) to know what attributes are on the request
4. **Read existing services** in `src/Service/` — inject them rather than reimplementing (e.g. `VectorSearch`, `FolderRouter`)

## Constructor

```php
use CouncilLibrary\Service\VectorSearch;   // if needed
use CouncilLibrary\Service\FolderRouter;   // if needed

class SomeController
{
    public function __construct(
        private \PDO            $pdo,
        private \Monolog\Logger $logger,
        private VectorSearch    $search,     // optional — inject existing services
    ) {}
```

PHP-DI auto-wires by type. Additional services resolve from their own constructors. Always inject existing services rather than reimplementing (e.g. `VectorSearch` already has FULLTEXT + vector search fallback logic).

## Request attributes (set by middleware)

| Attribute | Source | Value |
|-----------|--------|-------|
| `agent_slug` | `AgentContext` | From `X-Agent-ID` header |
| `wolf_id` | `AgentContext` | From `X-Wolf-ID` header (nullable) |
| `request_id` | `AgentContext` | From `X-Request-ID` header or random hex |

## Database switching

The `AgentContext` middleware switches the shared PDO instance to `agent_{slug}` **on every request**. Controllers must explicitly switch back for non-Sanctum databases:

- **Sanctum endpoints** (soul, memory, user-context, conversations, wolves): No action needed — AgentContext already selected the correct Sanctum.
- **Commons endpoints** (files, search, folders, ingestion): Must switch to `quiddity_commons` before every query:
  ```php
  private function ensureCommons(): void
  {
      $this->pdo->exec('USE quiddity_commons');
  }
  ```
  Call `$this->ensureCommons()` at the top of every public method. Without it, queries silently hit the agent's Sanctum instead of the shared Commons database.

- **Registry endpoints** (budget, privileged-actions): Same pattern:
  ```php
  private function switchToRegistry(): void
  {
      $this->pdo->exec('USE agent_registry');
  }
  ```

**Pitfall**: The `quiddity_commons` named DI definition in `bootstrap.php` returns the same PDO object as `PDO::class` — it just calls `USE quiddity_commons` once at construction time. AgentContext then switches it away. The named definition will NOT keep you on the right database — always call `ensureCommons()` at method entry.

**Pitfall**: PDO is shared across all controllers and services. When injecting `VectorSearch`, its constructor also receives the shared PDO. It too may need an `ensureCommons()` call internally — check the service implementation before assuming it handles DB switching.

## Response helper (copy from MemoryController)

```php
private function json(Response $response, array $data, int $status = 200): Response
{
    $response->getBody()->write(json_encode($data));
    return $response
        ->withHeader('Content-Type', 'application/json')
        ->withStatus($status);
}
```

## Error response shapes

```php
// 400 — missing required query parameter
return $this->json($response, ['success' => false, 'error' => 'Query parameter "q" is required'], 400);

// 403 — agent-initiated action without required payload
return $this->json($response, ['success' => false, 'error' => 'Agent-initiated sync requires explicit paths'], 403);

// 404
return $this->json($response, ['success' => false, 'error' => 'Not found'], 404);

// 409 (conflict)
return $this->json($response, ['success' => false, 'error' => 'Action is already confirmed'], 409);

// 201 (created)
return $this->json($response, ['success' => true, 'data' => $row], 201);
```

## Logging

```php
$this->logger->info('action_name', ['agent' => $agent, 'key' => $value]);

// For search queries — hash to avoid leaking raw query text into logs:
$this->logger->info('quiddity_search', [
    'query_hash' => hash('sha256', $query),
    'results'    => count($results),
]);
```

## Route param names

Route parameters in `index.php` determine the keys in `$args`. Always verify the actual param name before using it:

```php
// index.php:    $c->get('/files/{fid}/chunks', ...)
// Controller:   $fileId = (int) $args['fid'];   // NOT 'file_id'
```

Do not assume `{file_id}` — grep the route definition.

## Verification (ad-hoc, no canonical test suite)

1. **Syntax**: `php -l path/to/Controller.php`
2. **Reflection check** — class loads, constructor params match, all route methods exist:
   ```bash
   php -r '
   require "vendor/autoload.php";
   $r = new ReflectionClass(\CouncilLibrary\Controller\SomeController::class);
   foreach ($r->getConstructor()->getParameters() as $p) {
       echo $p->getName() . " : " . ($p->getType()?->getName() ?? "mixed") . "\n";
   }
   foreach ($r->getMethods(ReflectionMethod::IS_PUBLIC) as $m) {
       echo $m->getName() . "(" . $m->getNumberOfParameters() . ")\n";
   }
   foreach ($r->getMethods(ReflectionMethod::IS_PRIVATE) as $m) {
       echo "  private: " . $m->getName() . "\n";
   }
   '
   ```
3. **Route alignment** — grep `index.php` to confirm every `Controller::class . ':method'` reference matches a public method.
4. **SQL safety** — verify all `->prepare()` calls use parameter binding. The only acceptable raw interpolation is `(int)`-casted LIMIT values.

## Pitfalls

- **File overwrite race**: The controller file may be overwritten by an external process (file watcher, git hook, editor autosave). After writing, immediately verify contents with `read_file` + `php -l` + reflection.
- **PDO is shared**: All DI definitions return the same PDO instance. One controller's `USE` affects another. Always switch at method entry.
- **Route param names**: The `{param}` in index.php is the `$args` key. Do not assume `{file_id}` when the route says `{fid}`.
- **Services have their own PDO**: `VectorSearch` receives the shared PDO. Check whether the service handles its own DB switching.
