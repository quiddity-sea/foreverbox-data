# Phase 4 Features & Testing Patterns (Plutus, verified 2026-07-31)

## Testing Infrastructure (composer + PHPUnit + PHPStan)

- composer.json requires-dev: `phpunit/phpunit ^10.5`, `phpstan/phpstan ^1.11`,
  `friendsofphp/php-cs-fixer ^3.59`. Scripts: `composer test` / `composer analyse` / `composer cs-fix`.
- Install composer binary once: `php -r "copy('https://getcomposer.org/installer','composer-setup.php');" && php composer-setup.php --quiet && sudo mv composer.phar /usr/local/bin/composer`.
- Run `composer install` as the site owner (`sudo -u www-data composer install` in the site dir) so `vendor/` is readable by Apache's user.
- Tests live in `tests/` as plain class names extending `PHPUnit\Framework\TestCase`.
  Composer PSR-4 warnings ("Class X located in ./tests/... does not comply with psr-4 autoloading")
  are HARMLESS — PHPUnit discovers by directory. Add `require_once __DIR__ . '/../RateLimiter.php'`
  inside each test file (no autoload for bare classes).
- phpunit.xml: `bootstrap="vendor/autoload.php"`, `<source>` includes `api/` + `src/`.
- phpstan.neon: `level: 5`, `paths: [api, src]`, `tmpDir: /tmp/<project>-phpstan-cache`
  (keeps cache out of the site), `excludePaths: [tests]`.

### PHPStan is a real bug finder, not just style
Level 5 flagged: `Result of method MinimalPdf::headerBlock() (void) is used` — the code
concatenated a void method return into a PDF stream string (silently malformed PDF).
Fix pattern: call the void method first, then build the string from the mutated buffer.
Also flagged `Variable $pdo might not be defined` in `api/api.php` — `$pdo` is defined by
`require db.php` inside bootstrap, which PHPStan cannot see. Silence with a docblock:
```php
/** @var PDO $pdo */
$action = $_GET['action'] ?? '';
```
Third: `Property X::$pdo is never read, only written` — drop the unused constructor property.

### RateLimiter unit test gotcha
Constructing a limiter only creates the store dir; the JSON state file is written on the
first `allow()` call. To test key sanitisation, call `$rl->allow(true)` first, then glob
the store dir for `*.json` files.

## CI Workflow (`.github/workflows/ci.yml`)
- PHP job: setup-php 8.3 → composer install → lint (`find api src tests -name '*.php' -print0 | xargs -0 -n1 php -l`) → phpstan → phpunit.
- JS job: setup-node → npm ci → eslint → tsc --noEmit → vite build → upload dist/ artifact.

## Staging Environment (provision a same-server staging vhost)
- Wildcard cert `*.invigor.com` covers any new subdomain — no new cert needed.
  Verify with `openssl x509 -in /etc/apache2/ssl/invigor.com.crt -noout -text | grep -A1 "Subject Alternative Name"`.
- Vhost pattern: `:80` → permanent redirect to `:443`; `:443` → DocumentRoot + same cert/key +
  `AllowOverride All` + separate `plutus-staging-error.log`/`access.log`.
- Provision: `sudo a2ensite <name>` + `systemctl reload apache2`.
- Windows hosts entry needed for local testing (WSL mirrored networking): elevated PowerShell
  appends `127.0.0.1 <subdomain>` to `C:\Windows\System32\drivers\etc\hosts`; user must approve
  the UAC prompt. Verify from WSL with `getent hosts <name>`.
- **Staging DB anonymisation** (`scripts/anonymize_for_staging.php`): clone live DB to
  `<live>_staging`, then rewrite PII — usernames → `Staging User N` (reset password hash to
  known value), budgets → `Budget N`, transactions/vendors/items/projects/zones → anonymised,
  `TRUNCATE audit_log`. Login for testing: `Staging User 1 / StagingPass123!`.
- **Smoke test** (`scripts/smoke_staging.sh`): curl status checks (index 200, dashboard 200,
  metadata 200, unauth login 401, vite bundle 200, CSRF guard 403) PLUS an anonymisation
  leak guard (`grep -q "Budget 1"` on dashboard output). Exit nonzero on any failure.

### PITFALL: code sync clobbers env-specific config (hit 2026-07-31)
`rsync /var/www/plutus.invigor.com/ /var/www/plutus-staging.invigor.com/` copied production
`db.php` OVER staging's — silently re-pointing staging at the LIVE database. The smoke test's
anonymisation guard caught it (`FAIL: staging data not anonymised (leak?)`), which is exactly
why that guard exists. Lessons:
1. Exclude env-config from prod→staging sync, or re-patch it after every sync.
2. NEVER trust "staging shows data" as success — verify it shows ANONYMISED data.
3. Re-run the smoke test after every deploy/sync.
Also: applying the same ALTER migration to staging that was already applied gives a harmless
`Duplicate column` error — check `information_schema` before assuming a failure.

## Multi-Currency (ECB rates)
- Migration: `currency CHAR(3) NOT NULL DEFAULT 'GBP'` on budgets + transactions.
- `CurrencyService`: fetch ECB daily XML (`eurofxref-daily.xml`, EUR-base), cache as JSON with
  24h TTL. Convert: `amount / rate(from) * rate(to)` (EUR base). Unknown currency → passthrough.
- **Cache dir permission pitfall**: `/foreverbox_data/cache` is owned by zeon7 — `www-data`
  CANNOT write there (silent cache-miss, live fetch every request). Put the cache inside the
  site's own `runtime/` dir (already www-data-writable, gitignored): `__DIR__ . '/runtime/...'`.
  Test writability: `sudo -u www-data touch <dir>/.write_test`.
- Dashboard conversion: pass `?currency=USD`; convert totals server-side, return
  `display_currency` in the payload. UI: currency select in budget/transaction schemas.
- **CHECK constraint overspend pitfall (hit 2026-07-31)**: a Phase-2 CHECK
  (`cost_remaining >= 0`) breaks legitimate budget overspend tracking — a budget with
  target 0 gets `cost_remaining = -100` the moment any transaction links to it, so saves fail
  with `CONSTRAINT chk_budgets_cost_remaining failed`. Keep CHECKs on raw inputs
  (`amount > 0`, `target_amount >= 0`) but DROP checks on derived columns
  (`cost_remaining`). Apply the drop to live AND staging.

## PWA (manifest + service worker)
- `manifest.json`: name/short_name, `display: standalone`, theme/background `#0b141c`,
  icons 192+512 (generate with PHP GD — a simple pound-glyph is enough for a dev icon).
- `sw.js`: install → pre-cache static shell; activate → purge old caches; fetch →
  network-only for `api.php` (offline JSON error response), cache-first for GET static.
- index.php: `<link rel="manifest">` in head + registration snippet +
  `beforeinstallprompt` capture exposing `window.plutusInstallApp()`.
- Verify: manifest/sw.js/icons all 200; markers present in served HTML.

## Bank Import (CSV parse → dup detect → preview → confirm)
- Two endpoints: `import_parse` (multipart file upload → parsed rows + duplicate flags +
  suggested category) and `import_confirm` (JSON rows → inserts).
- CSV shape: `date,amount,name,description`. Normalise: strip `£`/commas from amount,
  `strtotime` date.
- Duplicate detection: date-prefix match + amount within 0.01 + `similar_text(name) > 70`.
- Category suggestion: keyword `stripos` against level-1 category names.
- **PITFALL: numeric vs associative row keys (hit 2026-07-31)** — after normalising CSV rows
  into associative arrays, a duplicate-check loop that indexes `$r[0]`/`$r[1]`/`$r[2]`
  silently compares NULLs and finds zero duplicates. Always key off `$r['date']`/`$r['amount']`/`$r['name']`.
- **PITFALL: NOT NULL columns in import** — transactions require `budget_id`; import must
  refuse (422-style `errorResponse`) when no budget selected rather than letting PDO throw.
- Verify flow: login with CSRF token header (`-H "X-CSRF-Token: $TOKEN"`), parse a CSV
  containing one real duplicate + new rows, confirm, check DB, clean up.
- UI: modal with file input + budget select + preview table (checkbox per row, duplicates
  pre-unchecked) + confirm button.

## Receipt OCR (tesseract)
- Install: `sudo apt-get install -y tesseract-ocr` (5.x).
- Controller: accept image upload (jpg/png/gif/webp/pdf whitelist by extension), store in
  `uploads/receipts/`, run `tesseract <file> stdout 2>/dev/null` via `exec()` with
  `escapeshellarg` (never interpolate raw), then heuristic-parse the text:
  - vendor: first non-empty line that isn't numeric/date/too-short
  - date: regex `\d{1,4}[-\/.]\d{1,2}[-\/.]\d{1,4}`
  - total: line containing `total` + a money pattern
- Test without a scanner: generate a synthetic receipt with PHP GD (`imagestring` + built-in
  font, white bg/black text, 600x400) — tesseract reads it cleanly.
- UI: modal with file input, SCAN button, parsed vendor/date/total cards + raw OCR text `<pre>`.

## Export Endpoints (CSV / JSON / PDF)
- One filtered `dataset()` method builds the shared query (filters: timeframe, budget_id, category_id), three handlers render it.
- Auth guard: `requireAuth()` → HTTP 401 when `$_SESSION['user_id']` is empty.
- CSV: `fputcsv(fopen('php://output','w'), ...)` + `Content-Disposition: attachment`.
- JSON: `json_encode(..., JSON_PRETTY_PRINT)` with exported_at + count.
- PDF: dependency-free `MinimalPdf` class — raw PDF 1.4 objects (catalog/pages/page/fonts/content
  stream), Helvetica + Helvetica-Bold, escape `(`, `)`, `\` in text. No dompdf dependency needed.
- UI: three btn-icon buttons in the transaction log header call a global `exportData(fmt)`
  that builds `?action=export_<fmt>&timeframe=...` (+ budget_id from `#tx-filter-select`)
  and sets `window.location.href` to trigger the download.
- Verify: unauth request → 401; authed → 200 with correct Content-Type per format.

## Keyboard Shortcuts (jQuery SPA)
- Namespaced handler so re-renders don't stack listeners:
  `$(document).off('keydown.plutus').on('keydown.plutus', function(e) {...})`.
- Skip when typing: check `e.target.tagName` in INPUT/TEXTAREA/SELECT or
  `e.target.contentEditable === 'true'`, and ignore Ctrl/Meta/Alt.
- `N` → openObjectManager('transaction'); `/` → focus `#ref-search-input`;
  `?` → show `#help-modal`; `Escape` → hide all open modals via a selector list + reset form.
- Help modal: static `#help-modal` div in index.php (glass-panel style), `#help-modal-close` button.

## Verification Script Pattern (Hermes loop)
When asked for "fresh passing verification evidence", write a read-only
`/tmp/hermes-verify-<topic>.sh` covering: `php -l` on every deployed PHP file,
`node --check` on JS, phpunit suite green, phpstan error count, HTTP GET status
codes, and feature markers in served assets. Report pass/fail counts explicitly
as ad-hoc verification, then delete the script. Avoid DB-writing test flows in
the script (creating test users triggers approval prompts) — keep it read-only.
For full-loop verification that DOES need a login (OCR/import/export), use a
temporary `__<name>_test__` user with a known password hash created via
`php -r "echo password_hash('TestPass123!', PASSWORD_DEFAULT);"`, then delete
it and its audit rows afterwards. Remember: `LIKE '__%'` is a wildcard trap —
escape as `\_\_%` when cleaning up `__`-prefixed test rows.
