# Apache .htaccess Security Hardening (verified 2026-08-01, Plutus Phase 5.4)

A focused read-only security scan found 3 real exposures on a live Apache/PHP site:
`db.php` (DB credentials!), `.git/config`, and `composer.lock` all returned HTTP 200.
Fix = site-root `.htaccess` + a vhost-scoped uploads guard.

## Site-root .htaccess (only context-valid directives!)

```apache
# Sensitive files - always deny
<FilesMatch "^(db\.php|composer\.(json|lock)|package-lock\.json|\.env|phpunit\.xml|phpstan\.neon|playwright\.config\.js|vite\.config\.js|vitest\.config\.js|tsconfig\.json)$">
    Require all denied
</FilesMatch>

# Block whole directories (404 so existence is not leaked)
RedirectMatch 404 /\.git(/|$)
RedirectMatch 404 /runtime(/|$)
RedirectMatch 404 /vendor(/|$)
RedirectMatch 404 /node_modules(/|$)
RedirectMatch 404 /tests(/|$)
RedirectMatch 404 /e2e(/|$)
RedirectMatch 404 /src(/|$)
RedirectMatch 404 /scripts(/|$)

# Disable directory listing
Options -Indexes
```

## PITFALL: `<DirectoryMatch>` is NOT allowed in .htaccess → site-wide 500

Error log: `core:alert ... .htaccess: <DirectoryMatch not allowed here`.
Result: EVERY page on the site returns HTTP 500 (not just the blocked paths).
Only directives valid in .htaccess context: `<FilesMatch>`, `RedirectMatch`,
`Options`, `RewriteRule`. Directory-scoped rules go in the vhost instead:

```apache
# Vhost block — no PHP execution in uploads (uploaded-webshell defence)
<Directory /var/www/<site>/uploads>
    php_admin_flag engine off
    <FilesMatch "\.(php|phtml|php5|phar)$">
        Require all denied
    </FilesMatch>
</Directory>
```

## Second pitfall: blanket FilesMatch PHP-deny kills the whole app

Do NOT put a bare `<FilesMatch "\.(php|phtml|phar)$"> Require all denied</FilesMatch>`
in the site root — it blocks `index.php` and `api.php` too. PHP-execution denial must
be scoped to the uploads directory (vhost Directory block), never the site root.

## Injecting vhost edits safely

```bash
sudo sed -i '/ErrorLog ${APACHE_LOG_DIR}\/<site>-error.log/r /tmp/block.conf' \
  /etc/apache2/sites-available/<site>.conf
sudo apache2ctl configtest   # MUST print "Syntax OK" before reload
sudo systemctl reload apache2
```

## Verification

```bash
curl -sk -o /dev/null -w "%{http_code}\n" https://site/db.php          # expect 403
curl -sk -o /dev/null -w "%{http_code}\n" https://site/.git/config     # expect 404
curl -sk -o /dev/null -w "%{http_code}\n" https://site/composer.lock   # expect 403
curl -sk -o /dev/null -w "%{http_code}\n" https://site/                # expect 200 (app alive)
```

403 (FilesMatch deny) vs 404 (RedirectMatch) both hide the file — either is fine.
ALWAYS re-check the app root returns 200 after deploying the .htaccess.

## The scan recipe (bash, read-only — replaces a full OWASP ZAP install)

Checks: security headers (nosniff / X-Frame-Options / Referrer-Policy); CSRF guard
(POST without token → 403); SQLi probes (`' OR 1=1--` in query params must NOT 500);
auth guards (export/import without session → 401/403); rate limit (6 rapid logins →
429, then `sudo rm -rf runtime/rate_limit` to unblock real logins); path traversal
(`/../../etc/passwd` → not 200); sensitive-file sweep (the FilesMatch list above).
Record in the plan as "replaced by focused scan" rather than leaving the item unticked.
