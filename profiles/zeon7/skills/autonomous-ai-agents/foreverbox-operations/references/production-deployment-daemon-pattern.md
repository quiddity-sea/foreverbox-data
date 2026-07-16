# Council Library Production Deployment — Daemon Pattern

## Overview

After the PHP API, embedding service, ingestion worker, and wolf workers are built and verified, they must run persistently — surviving reboots, logout, and crashes.

## Architecture

```
                    ┌─────────────────────────────────┐
                    │        Apache 2.4 (:8080)        │
                    │  vhost: council-library.conf     │
                    │  DocumentRoot: php-api/public/    │
                    └──────────────┬──────────────────┘
                                   │ PHP-FPM / mod_php
                    ┌──────────────▼──────────────────┐
                    │         PHP API (Slim 4)         │
                    │  8 controllers, 3 middleware      │
                    │  connects to MariaDB via PDO      │
                    └──────────────┬──────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                         │
  ┌───────▼──────┐   ┌────────────▼────────┐   ┌───────────▼──────────┐
  │ Embedding    │   │ Ingestion Worker     │   │ Wolf Workers (×3)    │
  │ :8900        │   │ (PHP CLI daemon)     │   │ (curator, producer,  │
  │ all-MiniLM   │   │ polls pending files  │   │  director)            │
  │ L6-v2        │   │ chunks + embeds      │   │ poll task_queue       │
  └──────────────┘   └─────────────────────┘   └──────────────────────┘
```

## Step 1: Apache Vhost

Replace `php -S localhost:8080` with a proper Apache vhost:

```apache
# /etc/apache2/sites-available/council-library.conf
<VirtualHost *:8080>
    ServerName localhost
    DocumentRoot /foreverbox_data/council-library/php-api/public

    <Directory /foreverbox_data/council-library/php-api/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        RewriteEngine On
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule ^ index.php [QSA,L]
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/council-library-error.log
    CustomLog ${APACHE_LOG_DIR}/council-library-access.log combined
</VirtualHost>
```

Deploy:

```bash
sudo cp vhost.conf /etc/apache2/sites-available/council-library.conf
echo 'Listen 8080' | sudo tee -a /etc/apache2/ports.conf
sudo a2enmod rewrite
sudo a2ensite council-library
sudo systemctl restart apache2
```

**Pitfall**: Apache's `www-data` user must be able to traverse the directory tree to reach `index.php`. Fix:

```bash
sudo chmod o+x /foreverbox_data /foreverbox_data/council-library /foreverbox_data/council-library/php-api /foreverbox_data/council-library/php-api/public
sudo chmod -R o+r /foreverbox_data/council-library/php-api/src
sudo chmod -R o+r /foreverbox_data/council-library/php-api/vendor
sudo chmod -R o+r /foreverbox_data/council-library/php-api/config
```

## Step 2: Systemd User Units

Create user-scoped systemd units in `~/.config/systemd/user/`. User units survive logout when lingering is enabled.

### council-embedding.service

```ini
[Unit]
Description=Council Library Embedding Service (all-MiniLM-L6-v2)
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3.12 /foreverbox_data/council-library/scripts/embedding_service.py --port 8900
Restart=on-failure
RestartSec=10
Environment=DB_PASS=<password>
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

### council-ingestion.service

```ini
[Unit]
Description=Council Library Ingestion Worker
After=network.target council-embedding.service

[Service]
Type=simple
ExecStart=/usr/bin/php8.3 /foreverbox_data/council-library/scripts/ingestion_worker.php
Restart=on-failure
RestartSec=30
Environment=DB_PASS=<password>
Environment=QUIDDITY_ROOT=/foreverbox_data/Quiddity_Lore_Sea
Environment=EMBEDDING_URL=http://127.0.0.1:8900
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

### council-wolves.service

```ini
[Unit]
Description=Council Library Wolf Workers (3 agents)
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c '\
  /usr/bin/python3.12 /foreverbox_data/council-library/scripts/wolf_worker.py --agent=curator --wolf-id=wolf_1 & \
  /usr/bin/python3.12 /foreverbox_data/council-library/scripts/wolf_worker.py --agent=producer --wolf-id=wolf_2 & \
  /usr/bin/python3.12 /foreverbox_data/council-library/scripts/wolf_worker.py --agent=director --wolf-id=wolf_3 & \
  wait'
Restart=on-failure
RestartSec=15
Environment=DB_PASS=<password>
Environment=FOREVERBOX_API_URL=http://localhost:8080/v1
Environment=FOREVERBOX_API_KEY=dev-key-change-in-production
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

## Step 3: Enable Lingering

User units normally stop when the user logs out. `loginctl enable-linger` keeps them running:

```bash
loginctl enable-linger zeon7
systemctl --user daemon-reload
systemctl --user enable council-embedding council-ingestion council-wolves
systemctl --user start council-embedding council-ingestion council-wolves
```

## Verification

```bash
systemctl --user is-active council-embedding council-ingestion council-wolves
# Expected: active active active

curl -s http://localhost:8080/v1/healthz
# Expected: {"status":"ok"}

systemctl --user status council-embedding --no-pager -l
# Should show: Active: active (running), Memory: ~400M
```

## Pitfall: Python Version Mismatch

The system has two Python interpreters:
- `python3` → Homebrew 3.14 (doesn't have `requests`, `yaml`, `sentence_transformers`)
- `/usr/bin/python3.12` → system Python (has all dependencies)

**Always use `/usr/bin/python3.12`** in ExecStart for Council Library services. Homebrew Python 3.14 cannot import `mysql.connector` or `sentence_transformers`.
