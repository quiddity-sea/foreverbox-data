---
name: php-webapp-security-hardening
category: devops
description: Hardening Apache-hosted PHP webapps — .htaccess vs vhost context rules, sensitive-file blocking, uploads PHP-execution guard, security headers, and the focused security-scan verification pattern. Durable lessons from the Plutus Phase 5.4 security pass.
version: 1.0
---

# PHP Webapp Security Hardening

Class-level skill for hardening Apache-hosted PHP webapps on ForeverBox infrastructure. Covers the .htaccess/vhost context distinction (which caused a full-site 500 during the Plutus Phase 5.4 pass), the file-blocking patterns, uploads hardening, and the focused security-scan verification pattern used when a full OWASP ZAP run is not available.

## When to Use

- Adding security headers, file-blocking, or directory hardening to an Apache PHP site
- Auditing a deployed site for exposed files (db.php, .git, composer.lock, .env)
- Proving a security posture without heavyweight tools (no ZAP / no headless Lighthouse)
- Any task touching `.htaccess` or vhost config on a www-data-owned site

## .htaccess vs vhost context (CRITICAL)

`<DirectoryMatch>` and `<Directory>` are ONLY valid in vhost/server config. Putting them in `.htaccess` produces `500 Internal Server Error` with `core:alert .htaccess: <DirectoryMatch not allowed here` in the Apache error log — the ENTIRE site 500s, not just the guarded path.

Context-valid in .htaccess:
- `<FilesMatch>` — file-name patterns
- `RedirectMatch` — URL rewrites (use for directory blocking)
- `Options -Indexes`
- `Require all denied` inside FilesMatch

Vhost-only:
- `<Directory>` / `<DirectoryMatch>` — directory-scoped blocks

### Sensitive-file blocking (.htaccess)
```apache
<FilesMatch "^(db\.php|composer\.(json|lock)|package-lock\.json|\.env|phpunit\.xml|phpstan\.neon|playwright\.config\.js|vite\.config\.js|vitest\.config\.js|tsconfig\.json)$">
    Require all denied
</FilesMatch>

RedirectMatch 404 /\.git(/|$)
RedirectMatch 404 /runtime(/|$)
RedirectMatch 404 /vendor(/|$)
RedirectMatch 404 /node_modules(/|$)
RedirectMatch 404 /tests(/|$)
RedirectMatch 404 /e2e(/|$)
RedirectMatch 404 /src(/|$)
RedirectMatch 404 /scripts(/|$)

Options -Indexes
```
Results: FilesMatch paths → 403, RedirectMatch paths → 404, app root stays 200.

### Uploads PHP-execution guard (vhost, NOT .htaccess)
```apache
<Directory /var/www/<site>/uploads>
    php_admin_flag engine off
    <FilesMatch "\.(php|phtml|php5|phar)$">
        Require all denied
    </FilesMatch>
</Directory>
```
CRITICAL: a blanket `<FilesMatch "\.php$"> Require all denied </FilesMatch>` in the ROOT .htaccess kills the whole app (index.php, api.php are .php). Always scope PHP-deny to uploads only.

### Security headers (vhost)
```apache
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set Referrer-Policy "strict-origin-when-cross-origin"
```
Requires `a2enmod headers`. Compression via `a2enmod deflate` + `AddOutputFilterByType DEFLATE text/html ... application/javascript application/json`. Caching via `a2enmod expires` + `ExpiresByType` rules.

## Verification: focused security scan (no ZAP needed)

When OWASP ZAP is not installed, run a focused read-only scan covering the same surface. Script: `scripts/security-scan.sh`. Checks:

1. Security headers on index (nosniff, X-Frame-Options, Referrer-Policy)
2. CSRF guard: POST without token → 403
3. SQLi probes on GET endpoints: `' OR 1=1--` → must NOT 500
4. Auth guards: export/import unauthenticated → 401/403
5. Rate limiting: 6 rapid logins → 429 (then CLEAR `runtime/rate_limit` so real logins aren't blocked)
6. Path traversal: `../../etc/passwd` → 404
7. Sensitive files NOT exposed: db.php, .env, .git/config, composer.lock
8. Uploads PHP guard: php file in uploads → 403/denied

## Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Full site 500 after .htaccess | `<DirectoryMatch>` in .htaccess | Move to vhost; .htaccess uses FilesMatch/RedirectMatch |
| db.php exposed (HTTP 200) | No .htaccess / no FilesMatch | Add FilesMatch deny; verify 403 |
| .git/config exposed | Directory listing / no rule | RedirectMatch 404 /\.git(/|$) |
| Whole app dead after hardening | Root-level blanket PHP deny | Scope PHP deny to uploads only |
| Login blocked after scan | Rate-limit state left behind | `sudo rm -rf <site>/runtime/rate_limit` after 429 tests |
| Security scan script MISSing bootstrap path | Wrong path (`api/controllers/bootstrap.php`) | bootstrap is `api/bootstrap.php`, not under controllers/ |

## Related Skills

- `service-user-webapp-operations` — www-data edit workflow, git-as-service-user, verification pattern
- `foreverbox-project-development` — architecture and security patterns (CSRF, rate limiting, audit, soft deletes)

## References

- `references/plutus-security-pass.md` — session detail: exact paths blocked, scan transcript, load-test results

## Scripts

- `scripts/security-scan.sh` — focused 14-check read-only security scan (curl-based, no ZAP)
