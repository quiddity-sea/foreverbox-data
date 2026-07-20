---
name: site-deployment
description: Deploy a new Apache-hosted subdomain site for the Foreverbox ecosystem using the connected_sites pattern. Creates web root, PHP markdown renderer, Apache VHost, and symlink to /foreverbox_data/connected_sites/.
---

# Skill: Site Deployment — Connected Sites Pattern

## When to Use

- Merrill asks you to set up a new subdomain site (e.g. `something.invigor.com`)
- Merrill wants a simple markdown-based site served by Apache
- Merrill wants to be able to edit site files from within `/foreverbox_data/`

## Structure

```
/var/www/{subdomain}/                  — Web root (Apache serves from here)
/foreverbox_data/connected_sites/{subdomain}/  — Symlink to web root
```

## Step 1: Create the Web Root

The web root goes in `/var/www/`. This requires sudo for creation:

```bash
sudo mkdir -p /var/www/{subdomain}
sudo chown -R zeon7:zeon7 /var/www/{subdomain}
```

Replace `{subdomain}` with the full subdomain label (e.g. `the-foreverbox-institute`).

## Step 2: Copy the Markdown Renderer

The PHP markdown renderer is a single `index.php` that uses [Parsedown](https://github.com/erusev/parsedown) to render `.md` files as styled HTML on the fly. It automatically lists all `.md` files in the directory on the homepage.

Copy from an existing site or create fresh:

```bash
# Copy from existing site (preferred — preserves the same look)
cp /var/www/the-foreverbox-institute/index.php /var/www/{subdomain}/
cp /var/www/the-foreverbox-institute/Parsedown.php /var/www/{subdomain}/
```

Then edit `index.php` to change the site title in the `<h1>` and footer from `the-foreverbox-institute` to your subdomain name.

**Key features of the renderer:**
- `GET /` — lists all `.md` files sorted by modification time (newest first)
- `GET ?file=filename.md` — renders that file as styled HTML
- Security: only serves `.md` files within the web root (no directory traversal)
- Dark code blocks, styled tables, blockquotes, navigation bar

## Step 3: Set the Apache VirtualHost

Create the site config file at `/tmp/{subdomain}.conf` with this template:

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

Then ask Merrill to run:

```bash
sudo cp /tmp/{subdomain}.conf /etc/apache2/sites-available/
sudo a2ensite {subdomain} && sudo systemctl reload apache2
```

## Step 4: Create the Symlink

```bash
ln -sf /var/www/{subdomain} /foreverbox_data/connected_sites/{subdomain}
```

This lets Merrill edit site files from within the foreverbox_data directory.

## Step 5: Add Content

Drop `.md` files into the web root. The homepage lists them automatically. Each file renders as a styled HTML page when clicked.

## Pitfalls

- **Sudo required**: Creating `/var/www/` directories needs sudo. Write the VHost config to `/tmp/` first and ask Merrill to copy it with sudo.
- **Parsedown dependency**: Download `Parsedown.php` from `https://raw.githubusercontent.com/erusev/parsedown/master/Parsedown.php` if no existing site has a copy.
- **Site title**: After copying `index.php` from an existing site, edit the `<h1>` text and footer to match the new subdomain name.
- **Wildcard SSL**: The `*.invigor.com` wildcard cert already covers all subdomains. Port 80 config is sufficient.
