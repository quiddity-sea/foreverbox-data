---
name: foreverbox-project-development
category: foreverbox
description: Class-level skill for developing, maintaining, and documenting ForeverBox ecosystem projects (Plutus, Institute, Nexus, Forever Fit, etc.) using the ForeverBox design system and architecture patterns.
version: 1.1
---

# ForeverBox Project Development

Class-level skill for developing, maintaining, and documenting ForeverBox ecosystem projects (Plutus, Institute, Nexus, Forever Fit, etc.) using the ForeverBox design system and architecture patterns.

## When to Use

- Building or maintaining any ForeverBox project site (Plutus, Institute, Nexus, Forever Fit, History section, etc.)
- Creating documentation for ForeverBox projects (user manuals, build blueprints, update plans)
- Working with the ForeverBox design system (HUD components, Tailwind config, scanlines, glass panels)
- Developing database-driven content rendering with PHP/JS (api.php, app.js, engine.php patterns)
- Implementing security hardening (CSRF, rate limiting, audit trails, soft deletes)
- Database schema management and migrations for ForeverBox projects

## Core Principles

1. **Component-Based Design System** — Reuse HUD components (`hud-border`, `glass-panel`, `hud-glow`, `corner-accent`, `scanline-overlay`, `data-node-label`) across all projects for visual consistency
2. **Shared Component Injection** — Use `fb-header`, `fb-sidenav`, `fb-footer` injection divs + `nav.js` for consistent navigation across all pages
3. **Database-Driven Content** — Store content in MariaDB, render via PHP engine (`engine.php` + `renderComponent`) + JS renderer (`ContentRenderer`)
4. **Security First** — CSRF tokens, rate limiting, audit trails, soft deletes, prepared statements
5. **Database-Driven Migrations** — Schema changes via numbered SQL migrations, never direct schema edits
6. **Self-Hosted, Privacy-First** — No external dependencies for core functionality; data never leaves infrastructure

## Architecture Patterns

### SPA Shell (`index.php`)
- Auth gate: session check → `renderLogin()` or `initApp()`
- Shared injection points: `fb-header`, `fb-sidenav`, `fb-footer`, `nav.js`
- Tailwind CDN + custom config in `<head>`
- Global scanline overlay + GSAP animations

### API Layer (`api.php`)
- Single entry point with action-based routing
- Actions: `check_session`, `login`, `logout`, `get_metadata`, `get_dashboard`, `save_object`, `delete_object`
- JSON request/response, session-based auth
- **Modular layout (Phase 3.1)**: `api/bootstrap.php` + `api/middleware/` + `api/controllers/` + `api/routes.php`; legacy root `api.php` is a thin `require_once __DIR__ . '/api/api.php'` wrapper so `?action=` calls stay backward compatible

### Database-Driven Rendering
- `engine.php` → `ForeverBoxEngine` → `renderComponent(loomId, variables)`
- Looms stored in `the_looms` table with `html_template` + `token_manifest`
- `ContentRenderer` maps `section_type` → render method → `renderComponent(loomId, vars)`

### Frontend State (`app.js`)
```javascript
window.appState = {
  metadata: {},           // Full metadata from get_metadata
  currentTab: 'overview',
  currentTimeframe: 'month',
  currentListEntity: null,
  transactionFilter: 'tab'
}
```

### Schemas (`schemas` object)
Defines form fields for universal modal:
```javascript
const schemas = {
  'budget': [{name: 'type', type: 'select', ...}, ...],
  'category': [...],
  'transaction': [...],
  // etc.
}
```

## Security Patterns

### CSRF Protection
```php
// On login
$_SESSION['csrf_token'] = bin2hex(random_bytes(32));

// In api.php middleware
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
  $token = $_SERVER['HTTP_X_CSRF_TOKEN'] ?? '';
  if (!hash_equals($_SESSION['csrf_token'], $token)) {
    http_response_code(403); exit('CSRF token mismatch');
  }
}
```
- Attach via `$.ajaxSetup({headers: {'X-CSRF-Token': $('meta[name="csrf-token"]').attr('content')}})`
- Exempt `login` and `check_session` from CSRF (no session yet / login creates session)
- Rotate the token in the login success response and re-sync the meta tag client-side

### Rate Limiting
```php
class RateLimiter {
  // Token bucket algorithm, file-based or Redis
  // Apply to login: 5 attempts / 15 min per IP
}
```
- Store dir must be `__DIR__ . '/runtime/rate_limit'` (site-local) — `'/../../runtime'` from the site root climbs OUT into `/var` and becomes unwritable
- On block: HTTP 429 + `Retry-After: <seconds>` header
- `allow(false)` probes without recording; successful auth should `reset()` the window
- Unit test both modes (window + bucket) with an isolated temp store dir

### Audit Trail
```php
AuditLog::log($userId, $action, $entityType, $entityId, $oldValues, $newValues);
// Creates entry in audit_log table with before/after JSON
```
- Never let audit failures break the primary request — wrap in try/catch + error_log
- Distinguish create vs update by capturing `$isNew = !$id` BEFORE the INSERT mutates `$id` via `lastInsertId()`

### Soft Deletes
- Add `deleted_at TIMESTAMP NULL` to all entity tables (NOT `users` — auth rows are never soft-deleted)
- All SELECTs: `WHERE deleted_at IS NULL` — but ONLY on tables that have the column. `get_metadata`-style queries that loop over ALL schemas will 500 (`Unknown column 'deleted_at'`) on tables without it. Guard with a column-existence check, cached per table:
  ```php
  private function hasDeletedAt(string $table): bool {
      static $cache = [];
      if (!isset($cache[$table])) {
          $stmt = $this->pdo->prepare("SELECT COUNT(*) FROM information_schema.columns
              WHERE table_schema = DATABASE() AND table_name = ? AND column_name = 'deleted_at'");
          $stmt->execute([$table]);
          $cache[$table] = (int)$stmt->fetchColumn() > 0;
      }
      return $cache[$table];
  }
  ```
- `delete_object` → `UPDATE ... SET deleted_at = NOW()` (not DELETE)
- Restore endpoint + UI toggle (`show_deleted` param on `get_objects`)
- When deleting test rows from `audit_log` during verification cleanup, scope by `entity_type`/`action`, NOT a time window — a `created_at > NOW() - INTERVAL` sweep also wipes legitimate backfill rows (re-run `scripts/backfill_audit.php` to restore)

### JSON Unescaping (Critical for DB Content)
```php
private function unescapeJsonString(string $value): string {
  $decoded = json_decode('"' . $value . '"');
  if (json_last_error() === JSON_ERROR_NONE) return $decoded;
  return str_replace(
    ['\\n', '\\r', '\\t', '\\"', '\\\\', '\\/'],
    ["\n", "\r", "\t", '"', '\\', '/'],
    $value
  );
}
```

## Database Patterns

### Core Tables (Plutus Example)
| Table | Purpose |
|-------|---------|
| `users` | Auth, OAuth tokens |
| `budgets` | Budget definitions (personal/household/improvement) |
| `categories` | Hierarchical, scoped (global/personal/household/improvements) |
| `transactions` | Financial entries + `sub_items` JSON |
| `items` | Reference data (products/services/custom) |
| `vendors` | Makers & suppliers |
| `projects` | Improvement projects |
| `project_zones` | Hierarchical zones |
| `improvements` | Work items |
| `tasks` | Reminders |

### Migration Pattern
```
migrations/
├── 001_audit_log.sql
├── 002_soft_deletes.sql
├── 003_audit_backfill.sql
```
- Never edit `schema.sql` directly for production changes
- Run migrations manually, update `schema.sql` for fresh installs
- MariaDB enforces CHECK constraints since 10.2; verify with `information_schema.table_constraints`
- Check `SHOW INDEX` before adding UNIQUE — `users.username` already had one and adding another made the migration exit 1
- Test constraints with a deliberately bad INSERT and grep the error (`CONSTRAINT ... failed` ERROR 4025, `Duplicate entry` ERROR 1062). A NOT NULL violation (ERROR 1364) can mask a CHECK test — supply all NOT NULL columns first

## Documentation Standards

### User Manual Structure
1. Welcome / Getting Started
2. Core Concepts (budgets, categories, transactions, etc.)
3. Navigation Guide (all tabs)
4. Common Workflows (step-by-step)
5. Data Health & Maintenance
6. Keyboard Shortcuts
7. Tips & Best Practices
8. Troubleshooting
9. Privacy & Security
10. Extending the System
11. Appendix: Entity Fields, API Endpoints

### Build Blueprint Structure
1. System Overview (stack, purpose, architecture)
2. Database Schema (tables, relationships, key columns)
3. API Specification (actions, params, responses)
4. Frontend Architecture (state, functions, schemas, components)
5. Deployment & Operations (requirements, install, cron, env)
6. Database Maintenance (backup, restore, migrations, queries)
7. Frontend Dev Guide (entities, widgets, styling, JS conventions)
8. Testing Checklist
9. Troubleshooting
10. Reconstruction Checklist (from zero)
11. File Reference

### Update Plan Structure
1. Executive Summary
2. Phase breakdown with dependencies
3. Task tracking template
4. Dependency graph
5. Rollback plan
6. Communication protocol
7. Success metrics
8. File inventory (core files, new files)
9. Sign-off table

## Common Pitfalls & Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| "FETCHING DATA..." hangs | API error / DB connection | Check `api.php` response, `db.php` credentials |
| Literal `\n` in output | Double-escaped JSON in DB | Use `unescapeJsonString()` in `renderComponent` |
| Charts blank | Chart.js not loaded / not destroyed | Call `chart.destroy()` before recreate |
| Date picker broken | Flatpickr not initialised | Verify `flatpickr.min.js` loaded, call `flatpickr()` |
| Sub-items not expanding | JS error in `renderTransactionTab` | Check `t.sub_items` exists, console errors |
| Footer scripts 404 | `$basePath` wrong | Fix `$basePath` logic in `footer.php`/`header.php` |
| Login fails | Wrong credentials / DB | Check `users` table, `password_hash()` |
| Session drops | PHP session config | Check `session.gc_maxlifetime`, cookie domain |
| `get_metadata` 500 `Unknown column 'deleted_at'` | Soft-delete filter applied to `users` | Guard SELECTs with `hasDeletedAt()` column check |
| Python patch prints `MISS` on app.js | app.js uses CRLF line endings | Normalise `\r\n`→`\n`, patch, restore `\r\n` (see references) |
| Direct patch/write_file Permission denied | Site dir owned by `www-data`, zeon7 not in group | Route edits through `sudo -u www-data python3` (see references) |
| Rate limiter never triggers | Store dir resolved to `/var/runtime` | Use `__DIR__ . '/runtime/rate_limit'` |
| Duplicate UNIQUE index | Original schema already had one | `SHOW INDEX` before `ADD CONSTRAINT` |
| npm not found as www-data | npm not in service user PATH | Build as zeon7 in /tmp, copy dist/ into site |

## Development Workflow

1. **Environment**: Ubuntu + Apache + PHP 8.1+ + MariaDB 11+
2. **Local Dev**: Copy files to `/var/www/project/`, configure Apache vhost
3. **DB**: Run `schema.sql` → create user → grant privileges
4. **Test**: Login → all tabs → CRUD → cron → mobile responsive
5. **Deploy**: `rsync` to server, set permissions, reload Apache
6. **Monitor**: Apache error log, MariaDB slow query log
7. **Git**: init as `www-data` (`sudo -u www-data git init`), identity `quiddity-sea <lightweavers74@gmail.com>`, branch `main`, `.gitignore` includes `dist/`, `node_modules/`, `runtime/`

## Editing www-data-owned site files (CRITICAL)

Plutus site files are owned by `www-data:www-data` and `zeon7` is NOT in the www-data group. Direct `patch`/`write_file` calls fail with Permission denied. Proven workflow:

1. Write the patch as a Python string-replace script in `/tmp`
2. `sudo cp /tmp/patch.py /var/www/plutus.invigor.com/.patch.py && sudo chown www-data:www-data .patch.py`
3. `sudo -u www-data python3 /var/www/plutus.invigor.com/.patch.py`
4. `sudo rm .patch.py` — /tmp is unreadable to www-data, so the script must live in the site dir while running

CRLF pitfall: `assets/js/app.js` uses CRLF. Python `\n`-only old-strings silently MISS. Normalise first, patch, restore.

## Key Files Reference (Plutus Example)

| File | Purpose |
|------|---------|
| `index.php` | SPA shell, auth gate, modals |
| `api.php` | Legacy entry (delegates to `api/api.php`) |
| `api/bootstrap.php` | Session, CSRF, includes |
| `api/routes.php` | Declarative route table + middleware config |
| `api/controllers/` | Auth, Object (universal CRUD), Dashboard, Export |
| `api/middleware/` | CsrfMiddleware, RateLimitMiddleware |
| `db.php` | PDO connection singleton |
| `RateLimiter.php` | Token bucket + fixed window limiter |
| `AuditLog.php` | Audit trail writer |
| `cron.php` | Recurring transaction processor |
| `schema.sql` | Canonical schema |
| `assets/js/app.js` | Core SPA logic |
| `assets/js/transaction_ui.js` | Transaction UI helpers |
| `assets/js/tailwind-config.js` | Tailwind theme |
| `assets/css/pages.css` | Page styles |
| `assets/css/components.css` | HUD component utilities |
| `scripts/verify_backup.php` | Backup restore + integrity verification |
| `scripts/backfill_audit.php` | Idempotent audit backfill |
| `tests/rate_limiter_test.php` | Standalone RateLimiter unit tests |
| `src/` + `vite.config.js` | Vite ES-module extraction (incremental) |

## Related Skills

- `stich-design-workflow` — Stich project conventions
- `fbox-ftn-production` — FTN content production workflow
- `fbox-wolf-spawn` — Wolf research worker spawning
- `hud-site-construction` — General site building patterns

## References

- `references/plutus_architecture.md` — Detailed architecture notes
- `references/plutus_schema.md` — Schema documentation
- `references/plutus_api.md` — API specification
- `references/foreverbox_design_system.md` — Design system component library
- `references/security_patterns.md` — CSRF, rate limiting, audit trail implementations
- `references/plutus-operational-patterns.md` — www-data edit workflow, CRLF patch, modular API, export endpoints, backup/audit lifecycle

## Templates

- `templates/migration.sql` — Migration boilerplate
- `templates/api_controller.php` — Controller boilerplate
- `templates/entity_schema.js` — Frontend schema boilerplate
- `templates/user_manual.md` — User manual structure
- `templates/build_blueprint.md` — Build blueprint structure
- `templates/update_plan.md` — Update plan structure

## Scripts

- `scripts/verify_backup.php` — Backup integrity verification
- `scripts/anonymize_for_staging.php` — Production data anonymization
- `scripts/migrate_schema.php`
