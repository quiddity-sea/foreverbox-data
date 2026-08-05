---
name: php-e2e-playwright-testing
category: web-development
description: Writing Playwright E2E tests against PHP/Apache web apps — browser-context API calls, CSRF, session persistence, and tab-scoped UI assertions. Durable pitfalls from Plutus Phase 2 B1 (planned.spec.js).
version: 1.0
---

# PHP E2E Testing with Playwright

Class-level skill for Playwright specs that exercise a PHP/Apache app end to end:
login, dashboard rendering, and API mutation from the browser context.

## When to Use

- Writing `e2e/*.spec.js` for a PHP app served by Apache (Plutus, Nexus, etc.)
- Calling the app's own PHP API from inside `page.evaluate` rather than only
  clicking UI
- Running specs against a staging copy (anonymised data)

## Browser fetch() vs PHP $_POST — the Content-Type trap

**Symptom**: a `page.evaluate`-based `fetch()` POST to `api.php?action=save_object`
returns `{"success":false,"error":"Invalid entity type"}` (or missing-field 422)
while the SAME call via curl succeeds.

**Root cause**: `fetch()` with a string body defaults to `text/plain`. PHP only
populates `$_POST` for `application/x-www-form-urlencoded` or `multipart/form-data`.
With `text/plain`, `$_POST` is empty → `entity_type` missing.

**Fix** — always set the header in the test's API helper:

```js
async function apiCall(page, csrf, body) {
    return page.evaluate(async ({ token, data }) => {
        const r = await fetch('/api.php?action=save_object', {
            method: 'POST',
            headers: {
                'X-CSRF-Token': token,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams(data).toString()
        });
        return r.json();
    }, { token: csrf, data: body });
}
```

In-app jQuery `$.ajax` calls are unaffected (jQuery sets the header itself);
only hand-rolled `fetch` in tests hits this. Debug tip: capture
`{ status, body: await r.text() }` in the evaluate and log it — the raw error
body is usually enough to tell "empty $_POST" from a real server error.

## page.evaluate takes exactly ONE argument

`await page.evaluate(fn, arg1, arg2)` throws
`Too many arguments. If you need to pass more than 1 argument to the function
wrap them in an object.`

Fix: pass a single object and destructure inside:
`await page.evaluate(fn, { a, b })`.

## CSRF token regenerates on page.reload()

After ANY `page.reload()` the server issues a NEW csrf token in the meta tag.
The `csrf` you read pre-reload is stale: mutating API calls made with it fail
with a silent 403 (`CSRF validation failed`), so cleanup deletes appear to work
but actually do nothing — test rows accumulate in staging. Re-read the token
after every reload before further API calls:

```js
await page.reload();
await expect(page.locator('#dashboard-content')).toBeVisible({ timeout: 20000 });
const csrf2 = await page.evaluate(() => document.querySelector('meta[name="csrf-token"]').content);
// use csrf2 for all subsequent fetch() mutations
```

## get_objects response shape is `data`, not `objects`/`items`

`api.php?action=get_objects&entity_type=X` returns
`{"success":true,"data":[{...rows...}]}`. A cleanup filter written against
`data.objects || data.items` matches nothing (silently → 0 rows → no cleanup).
Use `(data.data || [])`:

```js
const data = await r.json();
const rows = (data.data || []).filter(t => t.name === '__e2e_spend__');
```

When a spec's final cleanup assertion keeps returning 0 while the DB clearly
has the rows, check the response-key assumption before suspecting the mutation
failed. Same trap applies to any response-shape guess — log the raw JSON once
(`console.log(JSON.stringify(resp))`) instead of guessing.

## Session persists across page.reload()

After `page.reload()` the PHPSESSID cookie is still valid — the login form does
NOT render and `page.fill('input[name="username"]', ...)` times out. After a
reload, wait directly for `#dashboard-content`; do NOT re-fill login.

## Tab-scoped UI assertions

Sidebar action buttons (PLAN TRANSACTION, IMPORT FROM BANK, SCAN RECEIPT) only
exist on the personal/household transaction tabs, NOT the default overview tab.
Navigate first: `page.locator('.nav-tab[data-target="personal"]').click()` before
asserting such a button is visible.

## Standard login + CSRF recipe

```js
await page.goto('/');
await page.fill('input[name="username"]', 'Staging User 1');
await page.fill('input[name="password"]', 'StagingPass123!');
await page.click('button[type="submit"], #login-btn');
await expect(page.locator('#dashboard-content')).toBeVisible({ timeout: 20000 });
const csrf = await page.evaluate(() => document.querySelector('meta[name="csrf-token"]').content);
```

Send `csrf` as the `X-CSRF-Token` header on every mutating request.

## Running against staging

- Sync code live → staging first (see `service-user-webapp-operations` for the
  rsync + db.php re-point pitfall).
- `PLUTUS_BASE_URL="https://<site>-staging.invigor.com" npx playwright test <spec>`
- Playwright config: `ignoreHTTPSErrors: true` (self-signed wildcard certs).

## Spec file lives in TWO places

Specs are developed in the node build dir (e.g. `/tmp/plutus_vite/e2e/`) so the
runner has its deps, BUT they must ALSO be copied into the site repo
(`sudo cp e2e/planned.spec.js /var/www/<site>/e2e/ && sudo chown www-data:www-data`)
so the spec is version-controlled with the app and survives the build dir being
cleaned. Commit the site copy with the feature. (`node --check` validates the
spec syntax; `test-results/` from runs is transient.)

## Pitfalls

- Budget IDs differ between live and staging (anonymisation renumbers) — query
  the staging DB for a real budget id before hard-coding one in a spec.
- Keep specs self-cleaning: delete the created rows via API in a final
  `page.evaluate` so staging data does not accumulate `__`-prefixed test rows.
- A `waitForTimeout` after tab/filter clicks lets loadPeriods-style async option
  population finish before asserting on populated dropdowns.
- **Stale CSRF after reload leaves orphan rows**: if a spec reloads mid-run, the
  pre-reload token silently 403s the cleanup deletes; rows accumulate in staging.
  Re-read the token after every reload (see CSRF section above) and always sweep
  staging for `__`-prefixed leftovers before declaring a pass.
- **`get_objects` may paginate**: the response `data` array is not guaranteed to
  contain every row. A cleanup assertion that expects to find exactly the rows it
  created can return 0 if the list is truncated — verify against the DB or use
  the dashboard endpoint for existence checks instead.

## Related Skills

- `service-user-webapp-operations` — www-data editing, staging sync, verification
- `foreverbox-project-development` — app architecture and schema patterns
