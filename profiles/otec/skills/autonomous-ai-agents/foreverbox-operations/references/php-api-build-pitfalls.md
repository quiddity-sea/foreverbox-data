# PHP API Build Pitfalls — Slim 4, PDO, dotenv

Captured during the Council Library PHP API build (Stage 2, 2026-07-14). PHP 8.3.6, Slim 4.12, PHP-DI 7.0.

## Pitfall 1: Slim 4 + PHP-DI Bridge — Callable Resolution

**Problem**: `$app->get('/path', \Controller::class . ':method')` — the `ClassName:method` string syntax does not work with Slim 4's PHP-DI bridge. Neither does the array callable `[ClassName::class, 'method']`. Both produce:
```
Unable to invoke the callable because no value was given for parameter 1 ($req)
```

**Root cause**: PHP-DI's `ControllerInvoker` intercepts the callable but can't resolve Slim's `$request`/`$response`/`$args` parameters through the DI container alone.

**Fix**: Drop `php-di/slim-bridge`. Use `Slim\Factory\AppFactory::create()` with `AppFactory::setContainer($container)`. Wrap controller calls in a closure that resolves from the container:

```php
$app = AppFactory::create();
AppFactory::setContainer($container);

function c(string $class, string $method): callable {
    return function (Request $req, Response $res, array $args) use ($class, $method) {
        $agent = $req->getAttribute('agent_slug') ?? 'curator';
        $pdo = $this->get(PDO::class);
        try { $pdo->exec("USE agent_{$agent}"); } catch (\PDOException $e) {}
        return $this->get($class)->$method($req, $res, $args);
    };
}

$app->get('/v1/sanctum/memory', c(MemoryController::class, 'list'));
```

Also required: `$app->addBodyParsingMiddleware()` — without it, `$request->getParsedBody()` returns null for JSON POST/PUT bodies.

## Pitfall 2: PDO Is Not Cloneable

**Problem**: `clone $this->pdo` throws `Error: Trying to clone an uncloneable object of class PDO`.

**Fix**: Create a new PDO instance for cross-database access:

```php
private function getRegistryPdo(): \PDO
{
    $host = $_ENV['DB_HOST'] ?? 'localhost';
    $user = $_ENV['DB_USER'] ?? 'zeon7_user';
    $pass = $_ENV['DB_PASS'] ?? '';
    return new \PDO(
        "mysql:host={$host};dbname=agent_registry;charset=utf8mb4",
        $user, $pass,
        [\PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION]
    );
}
```

## Pitfall 3: dotenv `#` Comment Delimiter Truncates Passwords

**Problem**: `.env` file containing `DB_PASS=F0reverb0x#2o26sql` — the `#` is treated as a comment delimiter by vlucas/phpdotenv. The loaded value is `F0reverb0x`, truncating everything after `#`. This causes `Access denied for user` errors.

**Fix**: Quote values containing `#`:
```
DB_PASS="F0reverb0x#2o26sql"
```

## Pitfall 4: `getParsedBody()` Returns Null Without Body Parsing Middleware

**Problem**: `$request->getParsedBody()` returns `null` for JSON POST/PUT bodies even with correct `Content-Type: application/json` headers.

**Fix**: Add `$app->addBodyParsingMiddleware()` before `$app->addRoutingMiddleware()`.

## Pitfall 5: Route Parameter Name Mismatch

**Problem**: Route defines `{ns}/{key}` but controller accesses `$args['namespace']` and `$args['key_name']`. These don't match — Slim passes the route parameter names as keys.

**Fix**: Use null-coalescing to accept both naming conventions:
```php
$ns = $args['ns'] ?? $args['namespace'] ?? '';
$key = $args['key'] ?? $args['key_name'] ?? '';
```

## DB Switching Pattern

Sanctum controllers need `agent_{slug}` selected. Two approaches:

1. **In the route wrapper** (used in index.php `c()` function): `$pdo->exec("USE agent_{$agent}")` before every controller call. Simple but uses one connection.

2. **Per-controller helper**: Each controller has a private method that switches DB context. More explicit but repetitive.

For Commons controllers (QuiddityController, FolderController, IngestionController), switch to `quiddity_commons` instead.
