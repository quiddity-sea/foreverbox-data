---
name: site-deployment
description: Deploy a new Apache-hosted subdomain site for the Foreverbox ecosystem using the connected_sites pattern. Creates web root, PHP markdown renderer, Apache VHost, symlink, and database registration. Optionally configures SSL.
category: foreverbox
---

# Skill: Site Deployment — Connected Sites Pattern

## When to Use

- Merrill asks you to set up a new subdomain site (e.g. something.invigor.com)
- Merrill wants a simple markdown-based site served by Apache
- Merrill wants to be able to edit site files from within /foreverbox_data/

## Structure

```
/var/www/{subdomain}/                  — Web root (Apache serves from here)
/foreverbox_data/connected_sites/{subdomain}/  — Symlink to web root
quiddity_commons.connected_sites       — Database registration for Nexus Manager
```

## Step 1: Create the Web Root

The web root goes in /var/www/. This requires sudo for creation:

```
sudo mkdir -p /var/www/{subdomain}
sudo chown -R zeon7:zeon7 /var/www/{subdomain}
```

Replace {subdomain} with the full subdomain label (e.g. the-foreverbox-institute).

## Step 2: Copy the Markdown Renderer

The PHP markdown renderer is a single index.php that uses Parsedown to render .md files as styled HTML on the fly. It automatically lists all .md files in the directory on the homepage.

Copy from an existing site or create fresh:

```
cp /var/www/the-foreverbox-institute/index.php /var/www/{subdomain}/
cp /var/www/the-foreverbox-institute/Parsedown.php /var/www/{subdomain}/
```

Then edit index.php to change the site title and footer to match the new subdomain.

Key features of the renderer:
- GET / lists all .md files sorted by modification time (newest first)
- GET ?file=filename.md renders that file as styled HTML
- Security: only serves .md files within the web root (no directory traversal)
- Dark code blocks, styled tables, blockquotes, navigation bar with Dashboard and History links

## Step 3: Set the Apache VirtualHost

Create the site config file at /tmp/{subdomain}.conf with this template:

```
<VirtualHost *:80>
    ServerName {subdomain}.invigor.com
    DocumentRoot /var/www/{subdomain}
    <Directory /var/www/{subdomain}>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/{subdomain}-error.log
    CustomLog ${APACHE_LOG_DIR}/{subdomain}-access.log combined
</VirtualHost>
```

Then ask Merrill:

```
sudo cp /tmp/{subdomain}.conf /etc/apache2/sites-available/
sudo a2ensite {subdomain} && sudo systemctl reload apache2
```

## Step 4: Create the Symlink

```
ln -sf /var/www/{subdomain} /foreverbox_data/connected_sites/{subdomain}
```

## Step 5: Register in the Connected Sites Database

Register in quiddity_commons.connected_sites so it appears on the Nexus Manager dashboard:

```
curl -X POST http://localhost:8080/v1/commons/sites \
  -H "X-Agent-ID: leon" \
  -H "Content-Type: application/json" \
  -d '{"slug":"SUBDOMAIN","domain":"SUBDOMAIN.invigor.com","title":"Site Title","description":"Short description","purpose":"Why this site exists","main_vectors":["vector1","vector2"],"filter_tags":["active"]}'
```

## Step 6: Optional — SSL VirtualHost

If HTTPS is needed, create an SSL config that redirects HTTP. The wildcard *.invigor.com cert covers all subdomains.

Save to /tmp/{subdomain}-ssl.conf with port 80 (redirect) and port 443 (SSL) blocks.
SSLCertificateFile: /etc/apache2/ssl/invigor.com.crt
SSLCertificateKeyFile: /etc/apache2/ssl/invigor.com.key

Then ask Merrill:

```
sudo cp /tmp/{subdomain}-ssl.conf /etc/apache2/sites-available/
sudo a2ensite {subdomain}-ssl
sudo a2dissite {subdomain}
sudo systemctl reload apache2
```

## Step 7: Add Content

Drop .md files into the web root. The homepage lists them automatically.

## Pitfalls

- Sudo required for /var/www/ creation and Apache config. Write files to /tmp/ first.
- Parsedown dependency: wget https://raw.githubusercontent.com/erusev/parsedown/master/Parsedown.php
- Site title: Edit h1 and footer in index.php after copying.
- SSL cert file is invigor.com.crt, not invigor_wildcard.crt.
- Database registration is required for Nexus Manager visibility.
