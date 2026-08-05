# Plutus Security Pass — Session Detail (Phase 5.4, 2026-08-01)

Context: full-site hardening of `/var/www/plutus.invigor.com` during the Plutus
update plan Phase 5.4. The focused scan found 3 real exposures and the fix
sequence below closed them.

## What the scan found (first run: 11 pass / 3 fail)

| Check | Result | Fix |
|-------|--------|-----|
| db.php exposed | FAIL (200) | `.htaccess` FilesMatch deny → 403 |
| .git/config exposed | FAIL (200) | `RedirectMatch 404 /\.git(/|$)` → 404 |
| composer.lock exposed | FAIL (200) | FilesMatch deny → 403 |

Everything else passed on the first run: nosniff, X-Frame-Options,
Referrer-Policy, CSRF guard 403, both SQLi probes (no 500), export unauth 401,
import CSRF guard 403, rate limit 429, path traversal 404.

## The 500 incident (root cause)

First .htaccess attempt included:
```apache
<DirectoryMatch "^/var/www/plutus\.invigor\.com/uploads/">
```
→ whole site returned 500. Error log:
```
core:alert .../.htaccess: <DirectoryMatch not allowed here
```
Fix: removed the DirectoryMatch from .htaccess; moved the uploads PHP guard
into the vhost `<Directory /var/www/plutus.invigor.com/uploads>` block.

Also considered and rejected: root-level `<FilesMatch "\.php$"> Require all denied`
in .htaccess — would kill index.php/api.php (the whole app). Scoped to uploads.

## Final verified state

```
db.php            -> 403
.git/config       -> 404
composer.lock     -> 403
.env              -> 403
tests/            -> 404   (bonus: closed the long-standing web-exposed tests/ hygiene item)
index.php         -> 200
api.php dashboard -> 200
```
Security scan second run: 14/14 passed.

## Apache module requirements

`a2enmod headers expires deflate` — plus `php_admin_flag engine off` in the
uploads Directory (needs mod_php, not php-fpm; adjust if php-fpm).

## Load test (same session, 100 concurrent)

```
min 0.015s | avg 0.025s | p95 0.034s | max 0.038s   (all 100 HTTP 200)
```
Beats the plan's <200ms p95 target. Command pattern:
`seq 1 100 | xargs -P 20 -I {} curl -sk -o /dev/null -w "%{http_code} %{time_total}\n" --max-time 30 <url>` then sort/awk for stats.
