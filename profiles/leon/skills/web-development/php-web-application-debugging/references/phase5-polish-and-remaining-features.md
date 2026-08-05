# Phase 4 Completion + Phase 5 Polish Patterns (Plutus, verified 2026-08-01)

Extends `phase4-features-and-testing.md`. Covers the remaining Phase 4 plan items
(receipt pre-fill, category mapping, scheduled exports, background sync, versioned
API entry, type generation, Vitest/Playwright) and all of Phase 5 (performance,
accessibility, documentation/OpenAPI, final verification).

## Receipt Pre-fill into the Transaction Form (P4.3)

The OCR endpoint already returns parsed `{vendor, date, total}`. To turn it into a
transaction without re-typing:

- Do NOT hack the `openObjectManager(entityType, entityId)` signature — the second
  arg is the entity id and prefill objects passed there corrupt edit behaviour.
- Use a dedicated helper that mirrors `editObject`'s prefill mechanism:
  `openObjectManager('transaction')` then in a `setTimeout(..., 150)` call a
  `prefillObjectManager(overrides)` that does:
  ```js
  Object.keys(overrides).forEach(k => {
      const field = $('#universal-form [name="' + k + '"]');
      if (field.length) {
          field.val(overrides[k]).trigger('change');
          if (field[0]._flatpickr) field[0]._flatpickr.setDate(overrides[k]);
      }
  });
  ```
- Keyed off `[name=...]` selectors so it works for every field type incl. flatpickr
  dates (the `_flatpickr` instance lives on the DOM node).
- Gotcha: `window.openTransactionModal` is *referenced* but never defined in app.js,
  so `typeof window.openTransactionModal === 'function'` is false and transactions
  fall through to the universal modal. Don't add a missing modal — the universal one
  is the real path.
- UI: show a hidden `#ocr-create-btn` after a successful scan.

## Category Mapping UI (P4.4)

- `import_parse` response should include the level-1 `categories` array alongside
  `rows` and `duplicate_count`.
- Each preview row gets a `<select class="import-row-cat" data-idx="N">` populated
  with categories; pre-select the server-suggested `suggested_category_id` by
  string-replacing the option tag.
- `import_confirm` already reads `r.category_id`; the UI maps each row's select value
  into `r.category_id` before POSTing JSON.
- Verify: parse a CSV and confirm `categories` is in the JSON response.

## Scheduled Exports (P4.5)

- `scripts/scheduled_export.php [timeframe] [format]` — timeframe day|week|month|year|all,
  format csv|json. Builds a filtered dataset (same date-filter logic as dashboard),
  writes to `/foreverbox_data/exports/plutus/plutus_<tf>_<stamp>.<fmt>`, chmod 0640.
- Delivery is env-driven (no MTA on the box):
  `PLUTUS_EXPORT_WEBHOOK` (JSON POST with base64 content) and `PLUTUS_EXPORT_EMAIL`
  (`mail()` — fails gracefully when no MTA).
- Cron: `0 4 * * 0 php ... scheduled_export.php week csv >> .../scheduled.log 2>&1`.
- `all` timeframe yields the full dataset (540 rows in this DB) — use it to verify
  data-bearing output since `month` can legitimately return 0 rows on the 1st.

## Background Sync for Pending Transactions (P4.6)

- Service worker gains a message listener: `QUEUE_TRANSACTION` appends to a JSON
  array cached under key `plutus-pending` (caches API + `Response` round-trip);
  `FLUSH_QUEUE` replays it.
- `flushPending()` POSTs each queued tx to `save_object` with stored CSRF token,
  keeps failures in the queue, notifies clients via `postMessage({type:'SYNC_DONE'})`.
- `periodicsync` tag `plutus-sync` triggers the flush where PeriodicSyncManager exists.
- app.js: `queuePendingTransaction(txData)` posts to the controller if
  `navigator.serviceWorker.controller` exists; `window.online` fires FLUSH_QUEUE.
- Register `reg.periodicSync.register('plutus-sync', {minInterval: 15*60*1000})`.

## Versioned API Entry Point (P3.5)

- Legacy `api.php` stays a thin wrapper (backward compat). Add `api/v1.php` — a copy
  of the dispatcher with the version gate inlined:
  - Reject non-v1 `Accept` headers with 406 (except generic `*/*`).
  - Emit `X-API-Version: v1` + `Deprecation` headers.
- `api/.htaccess`: `RewriteRule ^v1/([a-z_]+)$ /api/v1.php?action=$1 [L,QSA]` gives
  `/api/v1/<action>` path-prefix style.
- Verify: `/api/v1/get_dashboard` 200 with v1 header; `Accept: v2` → 406; legacy
  `api.php?action=...` still 200.

## Schema-to-JSDoc Type Generation (P3.3)

- `scripts/generate_types.php` reads `information_schema.columns` for every table
  (skip internal `audit_log`), maps SQL types to JSDoc (`int→number`, `decimal→string`,
  `varchar→string`, `json→Object`, nullable → `|null`), writes `src/types/schema.js`
  with `@typedef {Object} <UcFirst(table)>` blocks + `export {};`.
- Run as the site owner after every migration; the file header says "do not edit by hand".
- Keep `tsc --noEmit` clean afterwards.

## Inline Validation Errors (P3.4)

- API already returns `{error:'VALIDATION_FAILED', fields:{name:'FIELD_REQUIRED'}}` (422).
- Frontend submit handler: on that error shape, remove `.field-error` elements, then for
  each field name add `border-error` to the input and inject a
  `<div class="field-error text-error ...">MSG</div>` after it.
- Clear the error classes on next open/submit.

## Vitest + Playwright (P4.1 JS test stack)

- `vitest.config.js`: `test.include: ['src/**/*.test.js']`, `environment: 'node'`,
  coverage provider `v8` with thresholds lines/functions 50.
- **Coverage exclusions are essential**: exclude `src/main.js` (entry bootstrap,
  window wiring only) AND `src/types/**` (pure JSDoc typedefs, 0% executable). Without
  both exclusions the global threshold fails even when every logic module is at 100%.
- Coverage gotcha: v8 counts ALL included files; a types-only `schema.js` (190 lines)
  drags global % down to ~26 even when `format.js`/`api.js`/`appState.js` are 100%.
- Vitest picks up `e2e/*.spec.js` as test files if `test.include` isn't restricted —
  keep the glob tight.
- `playwright.config.js`: `baseURL` from `process.env.PLUTUS_BASE_URL` (default
  staging), `ignoreHTTPSErrors: true` for the self-signed invigor cert.
- **Selector strict-mode pitfall (hit 2026-08-01)**: `locator('#login-form, form')`
  resolves to 2 elements (the visible login form + hidden `#universal-form`) and
  Playwright throws a strict-mode violation. Target `#login-form` alone.
- Install browsers: `npx playwright install chromium --with-deps` (~115 MB headless shell).
- CI already runs `npx tsc --noEmit` and `npm run build`; add `npm test` (vitest)
  and `npm run e2e` to the JS job when a runner is available.

## Backup Failure Alert (P2.1)

- `verify_backup.php` failure path: after `VERIFY FAILED` to stderr, read
  `PLUTUS_BACKUP_WEBHOOK` env; if set, JSON-POST `{text: '[PLUTUS] Backup verification
  FAILED: ...'}` via curl. Best-effort — never changes the exit code.

## Performance (P5.2)

- **Indexes**: add covering indexes for dashboard queries — transactions
  `(budget_id, date)`, `(category_id)`, `(date)`; budgets `(type)`; items `(type)`,
  `(category_id)`; improvements `(status)`, `(project_id)`; projects `(status)`;
  audit_log `(created_at)`. Apply to live AND staging. 16 `idx_%` in this DB.
- **OPcache**: check `php -r "var_dump(ini_get('opcache.enable'), ...)"` — was already
  on (128MB / 10000 files); don't assume it's missing.
- **Apache**: `a2enmod expires headers` (deflate was already on); add per-vhost block:
  `AddOutputFilterByType DEFLATE ...`, `ExpiresByType` rules (css/js 1 week, png/svg
  1 month), and security headers `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`.
  Inject into a vhost with `sudo sed -i '/ErrorLog <pattern>/r /tmp/block.conf'`.
  Verify: `curl -sk -D - -o /dev/null <url> -H "Accept-Encoding: gzip"` shows
  `Content-Encoding: gzip` + headers; `apache2ctl configtest` before reload.
- **Chart.js N/A**: the plan says "destroy before recreate" but the SPA loads Chart.js
  and never instantiates a chart (`grep -c "new Chart"` = 0, no canvas elements).
  Record as N/A rather than writing dead destroy code.

## Accessibility (P5.3)

- All 6 modals in index.php get `role="dialog" aria-modal="true" aria-label="<Title>"`.
- Focus management helpers (app.js): `plutusOpenModal(id)` saves
  `document.activeElement`, focuses the first visible focusable; `plutusCloseModal(id)`
  restores focus; `plutusFocusTrap(e, id)` wraps Tab between first/last focusables
  (Shift+Tab wraps backwards). A single `$(document).on('keydown')` loop applies the
  trap to every modal id.
- Keyboard nav was already covered by the P4.7 shortcuts; contrast is inherited from
  the HUD design system (bright green on near-black) — note it rather than re-auditing.

## Documentation + OpenAPI (P5.1)

- User manual + build blueprint live in the Council Library
  (`.../Current Started Plans/plutus_*.md`). Append a "What's New — <year> Update"
  chapter rather than rewriting; the blueprint gets an "Architecture Update" section
  (directory tree, request flow, testing stack, migrations, env vars, operations).
- `docs/openapi.json`: hand-written OpenAPI 3.0 spec covering all actions
  (security: session cookie + X-CSRF-Token header; 401/403/406/422/429 responses).
- `api/docs.php`: `?spec=1` serves the spec (with CORS allow), no-arg serves an
  endpoint index built from `routes.php` (`{name, version, endpoints:[{action,method,handler}]}`).
- Onboarding guide: environment map, first-run commands, code map, "adding an endpoint"
  recipe, migrations, staging deploy (INCLUDING the db.php re-point step), conventions,
  troubleshooting table.
- **Documentation-after-plan convention**: user prefers docs updated LAST, and prefers
  appending update chapters + preserving history over "superseded" rewrites.

## Final Verification (P5.4)

- Load test: `seq 1 100 | xargs -P 20 -I {} curl -sk -o /dev/null -w "%{http_code} %{time_total}\n" <url>`
  → all 200; timing via `sort -n | awk` min/avg/p95/max. This box: p95 0.034s —
  massively under the plan's <200ms target.
- OWASP ZAP is not installed and heavy; the security posture is covered by verified
  headers (nosniff/X-Frame-Options/Referrer-Policy), CSRF, rate limiting, soft deletes.
  Propose "manual security check + headers" and let the user decide on ZAP — don't
  install a large toolchain unprompted.
- Ad-hoc verification script pattern still applies (see phase4 reference); extend with
  new markers (v1.php, docs.php, a11y dialogs, focus trap) and the `grep -q
  "plutus_thoughts_staging"` staging db.php check.
