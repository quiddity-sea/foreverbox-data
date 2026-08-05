---
name: apache-vhost-checklist
description: "Checklist for validating Apache VirtualHost configuration for PHP sites"
tags: ["apache", "virtualhost", "ssl", "php", "deployment"]
---

# Apache VirtualHost Validation Checklist

## Prerequisites
- [ ] Apache installed and running (`systemctl status apache2`)
- [ ] PHP-FPM or mod_php enabled (`php -v`, `a2enmod php8.x`)
- [ ] SSL certificate and key exist and are readable
- [ ] DNS resolves to server IP

## HTTP VirtualHost (Port 80) — Redirect to HTTPS
```apache
<VirtualHost *:80>
    ServerName example.com
    Redirect permanent / https://example.com/
</VirtualHost>
```
- [ ] `ServerName` matches domain
- [ ] `Redirect permanent / https://...` preserves path

## HTTPS VirtualHost (Port 443) — Main Configuration
```apache
<VirtualHost *:443>
    ServerName example.com
    DocumentRoot /var/www/example.com/public
    
    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/example.com.crt
    SSLCertificateKeyFile /etc/apache2/ssl/example.com.key
    
    <Directory /var/www/example.com/public>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    
    ErrorLog ${APACHE_LOG_DIR}/example.com-error.log
    CustomLog ${APACHE_LOG_DIR}/example.com-access.log combined
</VirtualHost>
```

### Required Checks
- [ ] `ServerName` matches certificate CN/SAN
- [ ] `DocumentRoot` exists and contains `index.php`
- [ ] `SSLCertificateFile` and `SSLCertificateKeyFile` paths exist, readable by `www-data`
- [ ] `<Directory>` block has `AllowOverride All` (for `.htaccess` / rewrites)
- [ ] `<Directory>` block has `Require all granted`
- [ ] Error/Custom log paths writable by `www-data`
- [ ] SSL protocols/ciphers hardened (optional but recommended)

## Enable Site & Modules
```bash
a2ensite example.com-ssl.conf
a2enmod ssl rewrite headers ssl php8.x
systemctl reload apache2
```

## SSL Certificate Validation
```bash
# Check certificate
openssl x509 -in /etc/apache2/ssl/example.com.crt -text -noout

# Test TLS
openssl s_client -connect example.com:443 -servername example.com
```

## Common Issues

| Symptom | Likely Cause |
|---------|--------------|
| 404 on all pages | Wrong `DocumentRoot` |
| 500 on PHP pages | `mod_php` not enabled / PHP version mismatch |
| Assets 404 | Wrong `DocumentRoot` or missing `AllowOverride` |
| SSL handshake fail | Cert/key mismatch, wrong paths, permissions |
| Mixed content warnings | Hardcoded `http://` in HTML |
| `SSLEngine on` ignored | `mod_ssl` not enabled |

## Post-Deploy Verification
```bash
# Syntax check
apache2ctl configtest

# Reload
systemctl reload apache2

# Test HTTP redirect
curl -I http://example.com/

# Test HTTPS
curl -k -I https://example.com/
curl -k https://example.com/page.php
```