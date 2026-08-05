---
name: php-web-application-debugging
description: "Class-level skill for debugging PHP database-driven web applications (Apache/Nginx, MariaDB/MySQL/PostgreSQL, PHP 7/8)"
tags: ["php", "debugging", "web-development", "apache", "mariadb", "pdo", "json"]
---

# PHP Web Application Debugging

A class-level skill for debugging PHP database-driven web applications (Apache/Nginx, MariaDB/MySQL/PostgreSQL, PHP 7/8).

## Scope
Covers the full stack of traditional PHP web applications:
- Apache/Nginx configuration & virtual hosts
- PHP runtime errors, parse errors, undefined variables
- Database connection issues (PDO, credentials, socket vs TCP)
- JSON/encoding problems from database content
- Template rendering & component systems
- Session/authentication problems
- Asset loading (CSS, JS, images) with base path resolution

## Core Techniques

### 1. JSON Double-Escape Recovery
When database content contains double-escaped JSON (`\\n`, `\\"`, `\\\\`):

```php
private function unescapeJsonString(string $value): string {
    // Try JSON decode first (handles \" \n \t etc.)
    $decoded = json_decode('"' . $value . '"');
    if (json_last_error() === JSON_ERROR_NONE) {
        return $decoded;
    }
    // Fallback: manual unescape
    return str_replace(
        ['\\n', '\\r', '\\t', '\\"', '\\\\', '\\/'],
        ["\n", "\r", "\t", '"', '\\', '/'],
        $value
    );
}
```

**Use when**: Database stores HTML/JSON with escaped newlines/quotes that render literally.

### 2. Undefined Variable Fallbacks in Templates
When variables may not be set in all code paths:

```php
$basePath = $basePath ?? ((basename(dirname($_SERVER['PHP_SELF'])) === 'pages') ? '../' : '');
```

**Use when**: Template includes are shared across pages at different depths.

### 3. Database Connection Debugging
Priority order for connection failures:
1. Check PDO error mode (`ERRMODE_EXCEPTION`)
2. Verify credentials in `.env` / environment variables
3. Test TCP (`localhost`) vs Unix socket (`/var/run/mysqld/mysqld.sock`)
4. Verify database exists and user has permissions
5. Check `bind-address` in MariaDB config

### 4. Apache VirtualHost Debugging
- `DocumentRoot` must point to public directory
- `AllowOverride All` for `.htaccess` / rewrite rules
- Check both `:80` (redirect) and `:443` (SSL) VirtualHosts
- SSL cert/key paths must be readable by `www-data`

**File permission 500 (hit 2026-07-31):** Apache runs PHP as `www-data`, so a PHP file created by another user with default restrictive perms (`-rw-------` 600) yields **HTTP 500** with:
```
PHP Warning: Unknown: Failed to open stream: Permission denied
PHP Fatal error: Failed opening required '/var/www/.../page.php' ... in Unknown on line 0
```
Fix: `chmod 644 /var/www/.../page.php` (owner-write, world-read). Files created via WSL-side `write_file` land with 600 by default when the umask restricts — always verify `ls -la` on newly deployed PHP files and chmod to 644. Also note the difference between vhost routing errors (404 when the file is under a different DocumentRoot — see `wsl-environment-setup` for stale Windows hosts entries) and permission errors (500 with the fatal-open error above).

**Editing www-data-owned files (hit 2026-07-31):** when the site root is owned by `www-data:www-data` (e.g. `/var/www/plutus.invigor.com/`), the `patch`/`write_file` tools fail with `Permission denied` because the agent runs as a different user, and `/tmp` is NOT readable by www-data. The working pattern is a Python patch script executed as www-data, staged inside the web root:

```bash
# 1. Write the patch script with write_file to /tmp (surgical string replacements)
# 2. Stage it in the web root (www-data can't read /tmp), run as www-data, remove
sudo cp /tmp/patch.py /var/www/site/.patch.py
sudo chown www-data:www-data /var/www/site/.patch.py
sudo -u www-data python3 /var/www/site/.patch.py
sudo rm -f /var/www/site/.patch.py
```

**www-data patch scripts cannot copy files from /tmp (hit 2026-08-01):** a script
that internally does `shutil.copy('/tmp/newfile.php', site_dir/...)` raises
`PermissionError: [Errno 13] Permission denied: '/tmp/...'` because www-data
cannot read /tmp at all. Copy NEW files with `sudo cp` (as the agent user) BEFORE
running the www-data script, and keep the www-data script to pure string
replacements. Watch output carefully: the script exits non-zero on the copy
failure but its later PATCH steps still run, so a partial apply can look like a
full one.

The script uses `io.open(path, 'r', encoding='utf-8', errors='replace')`, does exact `content.replace(old, new, 1)` per edit, prints `MISS in <path>` when an anchor isn't found (so you can see a stale anchor rather than silently skipping), and rewrites the file. Always `php -l` after PHP edits and `node --check` after JS edits. `sudo -u www-data bash -c '...'` works too for small heredoc-based edits (e.g. appending to .gitignore) but the Python script is safer for multi-anchor patches.

**CRLF trap in patch scripts (hit 2026-07-31):** files that originated on Windows (e.g. `assets/js/app.js` served from a Windows-origin project) may use CRLF line endings. A patch anchor written with `\n` will then print `MISS` even though the text looks identical in the editor — the file literally contains `\r\n`. Always check first: `file <path>` or `head -c 200 <path> | od -c | grep -m1 '\r'`. If CRLF, normalise before patching and restore after:
```python
had_crlf = '\r\n' in content
content = content.replace('\r\n', '\n')
# ... apply replacements with \n anchors ...
if had_crlf:
    content = content.replace('\n', '\r\n')
```
This also applies to `patch` tool calls — they fail on CRLF files with confusing diffs; the python-normalise path is the reliable route.

**LIKE wildcard gotcha (hit 2026-07-31):** in MariaDB `LIKE '__%'` treats `_` as a single-char wildcard, so a "find test rows" query with `username LIKE '__%'` matches ANY two-character+ username (e.g. real users "James Leo", "Merrill Leo") — a false "test residue" alarm. Escape the underscore: `LIKE '\\\\_\\\\_%'` or use `REGEXP '^__'`.

**Bad .htaccess directive = site-wide 500 (hit 2026-08-01):** an invalid directive in a vhost that has `AllowOverride All` takes down EVERY page with HTTP 500, not just the blocked paths. Classic: `<DirectoryMatch>` in .htaccess — it is only valid in server/vhost context and the error log shows `core:alert ... .htaccess: <DirectoryMatch not allowed here`. Recovery: fix/remove the .htaccess and the site returns immediately. When the security scan reports `db.php`, `.git/config`, or `composer.lock` as HTTP 200, block them with FilesMatch/RedirectMatch in the site-root .htaccess and scope the uploads PHP-execution guard to the vhost (see `references/security-hardening-htaccess.md` for the exact blocklists and the two associated pitfalls: a blanket root-level PHP FilesMatch deny also blocks index.php/api.php).

### 5. PHP Parse Error Detection
- `PHP Parse error: Unmatched '}'` → count braces, check heredoc/nowdoc
- `Undefined variable` → trace include chain, add null coalescing
- `Call to undefined function` → check extensions (`pdo_mysql`, `gd`, `mbstring`)

## Playwright E2E against PHP APIs (hit 2026-08-01)

When Playwright specs call the PHP API directly via `page.evaluate(fetch(...))`, three
traps bite — all cost real debugging time in the Phase 2 planned/spend-task specs:

- **Browser `fetch` leaves PHP `$_POST` empty**: raw `fetch(url, {method:'POST', body: new URLSearchParams(...)})` sends `Content-Type: text/plain;charset=UTF-8` by default. PHP only populates `$_POST` for `application/x-www-form-urlencoded` or `multipart/form-data`, so the request arrives with every field missing — symptoms are `Invalid entity type` (empty `entity_type`) or `FIELD_REQUIRED` errors that curl does NOT reproduce (curl works because the header is set by default). Fix: always set `'Content-Type': 'application/x-www-form-urlencoded'` on the fetch headers. jQuery `$.ajax`/`$.post` set it automatically — this only affects raw `fetch` in `page.evaluate`.
- **CSRF token regenerates on `page.reload()`**: the app rotates the session CSRF token after a reload, so a token captured pre-reload silently 403s every POST afterwards — including the cleanup `delete_object` calls, which then fail and leak test rows into the DB (duplicate `__e2e_*` rows on the next run). Fix: re-read `document.querySelector('meta[name="csrf-token"]').content` AFTER any reload before doing post-reload API calls, and verify cleanup actually ran (row count returns to baseline).
- **`get_objects` response shape is `data`**: `api.php?action=get_objects&entity_type=transaction` returns `{success:true, data:[...]}`, NOT `objects`/`items`. Filter `(resp.data || [])` or you get an empty array and the cleanup loop silently does nothing.
- **`page.evaluate` takes ONE argument**: pass multiple values wrapped in an object (`page.evaluate(fn, {a, b})`), not as separate args — extra args throw `Too many arguments`.
- Recreate-after-reload login: after `page.reload()` the session persists, so do NOT re-fill the login form — wait for `#dashboard-content` directly.

## Verification Checklist
After fixes, verify:
- [ ] `curl -k https://domain/page.php` returns 200
- [ ] No errors in `/var/log/apache2/error.log`
- [ ] Database queries return expected rows
- [ ] No `\n`, `\"`, `\\` literals in rendered HTML
- [ ] Assets (CSS/JS/images) load with correct paths

## Static Analysis & Testing Infrastructure (Phase 4.1)

PHPStan at level 5 catches real bugs, not just style:
- `Result of method X() (void) is used` — code concatenated a void method return into a string (silently malformed output). Fix: call the void method first, build the string from the mutated buffer.
- `Variable $pdo might not be defined` when `$pdo` comes from a `require`d file — silence with `/** @var PDO $pdo */` on the line before first use.
- `Function response invoked with N parameters, 1 required` — a project's `response($data)` helper takes ONE argument (no status code). Passing `response([...], 404)` is a PHPStan error AND silently ignores the code. Fix: `http_response_code(404); response([...]);`.
- `Constant PLUTUS_GOOGLE_CLIENT_ID not found` — the `defined('X') ? X : ''` pattern trips PHPStan because the constant name is unresolvable in the false branch. Fix: private accessor methods returning env values (`getenv('X') === false ? '' : trim(getenv('X'))`), then use `$this->clientId()` everywhere.
- Composer PSR-4 warnings for bare test classes are harmless — PHPUnit discovers `tests/` by directory.

Full composer/phpunit/phpstan/CI setup, export endpoints, keyboard shortcuts, and the read-only verification-script pattern: see `references/phase4-features-and-testing.md`. The same reference also covers: staging environment provision (wildcard cert, anonymised DB, smoke test) + the prod→staging sync db.php clobber pitfall, multi-currency ECB rates with the www-data cache-dir permission trap, PWA manifest/service-worker, bank import CSV duplicate detection, and receipt OCR via tesseract.

Phase 4 completion items + all of Phase 5 (receipt pre-fill via `prefillObjectManager`, bank-import category mapping UI, scheduled exports with webhook/email delivery, SW background sync, `/api/v1` versioned entry + rewrite, schema→JSDoc type generation, Vitest coverage exclusions + Playwright strict-mode selector pitfall, backup failure webhook, performance indexes/gzip/headers, modal ARIA + focus trap, OpenAPI spec served at `/api/docs`, docs-update-last convention, load-test recipe): see `references/phase5-polish-and-remaining-features.md`.

Phase 2 upgrades (planned-transaction system with projected-vs-actual, spend-based task manager with Google Calendar OAuth/RRULE sync — verified schema, API wiring, create-only validation, spend-only budget totals, degrade-gracefully GoogleCalendarService, TaskController complete/pause/resume/stop + next-instance generation, composer google/apiclient): see `references/phase2-upgrades-planned-tasks-gcal.md`.

## Plan Completion & Council Library Closeout

After executing a multi-phase plan, close it out in the Council Library (see the shared `council-library-plan-completion` / `update-plans-progression` skills for the full workflow — they describe the engine but ship no runnable script):

- **Runnable dashboard engine**: `scripts/regenerate_progression.py` in this skill's directory implements the detection rules (checkbox + inline `- DONE` header counting, template-line exclusion). Copy it out and run with plain `python3` whenever a planning document changes. It is also the only executable copy — the Shared_Skills versions reference scripts that do not exist there.
- **NO auto-relocation to Completed (user correction 2026-08-01)**: the engine must NOT move 100% plans Started → Completed on its own. Merrill's correction after the Phase 2 plan was auto-moved before he tested it: "why have you moved it to compleated before I have tested it". Implementation-complete (tickboxes ticked, tests pass) is NOT reviewed-complete. Keep the plan in Started Plans until Merrill signs off — see `plan-lifecycle-governance` for the full rule. The `update-plans-progression` / `plans-progression-dashboard` shared skills still describe auto-relocation in their descriptions; treat that as stale and never let it fire.
- **Template lines**: the Task Tracking Template's example checkboxes (`Criterion 1`, `Test command / manual steps`, `Expected output`) are NOT tasks; excluding them is required for template-bearing plans to reach 100% and relocate.
- **Honest exceptions**: keep genuinely-impossible items unticked and explain why in a Completion Note (e.g. "OWASP ZAP" when replaced by a focused security scan, "Lighthouse > 90" with no headless Chrome). Never silently tick something not done.
- **Check the hostname before declaring infrastructure items unverifiable** (hit 2026-08-01): an item like "Verify server access (SSH to Wales Hub)" was kept unticked as "external infra" — then the user revealed this host (hostname `Foreverbox`) IS the Wales Hub, so it was tickable all along. Run `hostname` first; if the item is about the machine you are on, tick it.
- **Folder taxonomy for completed work** (confirmed 2026-08-01): "Completed" is for SIGNED-OFF plans, not every doc that stopped being worked on. User manuals / build blueprints / onboarding guides are living reference → `Current Reference Documentation/`; superseded versions (e.g. blueprint v1–v5 when v6 is current) → `archives/`; signed-off plans → `Current Completed Plans/`; 100%-ticked plans awaiting review stay in `Current Started Plans/`. Run `reference-doc-alteration-log` after reference-doc moves and regenerate the dashboard.
- **Sign-off table**: fill Reviewed-by / Approved-by rows with real dates + ✓ after user confirmation.
- **Docs are a git repo too**: commit the updated plan/manual/blueprint to the Council Library repo (identity `quiddity-sea <lightweavers74@gmail.com>`), and only stage YOUR files — the repo often carries unrelated pre-existing modifications.

Runnable helpers (in this skill's `scripts/` — copy out and run, no deps):
- `scripts/regenerate_progression.py` — regenerates the Plans Progression dashboard after any plan change (the Shared_Skills skills reference this script but do not ship it)
- `scripts/update_plan_ticks.py` — ticks completed checkboxes, preserves template lines + honest exceptions, fills sign-off, appends Completion Note

## Related Skills
- `local-model-ollama-context` — for local LLM debugging context
## References
- `references/json-unescape-pattern.md` — detailed unescape implementation
- `references/basepath-fallback-pattern.md` — template variable fallback
- `references/apache-vhost-checklist.md` — VirtualHost validation steps
- `references/security-hardening-patterns.md` — verified CSRF / rate limiting / audit trail / soft-delete implementations (Plutus Phase 1, includes the `__DIR__.'/../../runtime'` path bug, CSRF token rotation on login, create-vs-update audit pitfall, and a curl verification recipe)
- `references/modular-api-refactor.md` — Phase 3 verified patterns: splitting a monolithic api.php into an api/ tree (middleware chain, routes, controllers), Validator 422 responses, Accept-header versioning (406), the `hasDeletedAt` per-table guard pitfall for soft-delete schemas, and incremental Vite/TypeScript frontend modularisation
- `references/phase5-polish-and-remaining-features.md` — Phase 4 completion + Phase 5: receipt pre-fill, category mapping, scheduled exports, background sync, /api/v1 entry, type generation, Vitest/Playwright, performance, accessibility, OpenAPI docs, load testing
- `references/security-hardening-htaccess.md` — site-root .htaccess FilesMatch/RedirectMatch blocklists for sensitive files (db.php, .git, composer.lock), the `<DirectoryMatch not allowed here` site-wide-500 pitfall, vhost-scoped uploads PHP-execution guard, and the read-only security scan recipe