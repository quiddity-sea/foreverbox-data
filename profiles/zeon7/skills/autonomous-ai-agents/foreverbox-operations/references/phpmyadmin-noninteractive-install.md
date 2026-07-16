# phpMyAdmin — Non-Interactive Install on Ubuntu 24.04

## Context
Foreverbox runs MariaDB 11.8+ on Ubuntu 24.04 (Noble Numbat). phpMyAdmin provides a web GUI at `http://localhost/phpmyadmin` for database administration of the Council Library's Four Wings.

## The Problem
`sudo apt install -y phpmyadmin` **does not work** on Ubuntu 24.04. Despite the `-y` flag, the package's post-install script invokes `dbconfig-common` which spawns an interactive `whiptail` dialog asking:
> "Configure database for phpmyadmin with dbconfig-common?"

In a non-interactive terminal (Hermes agent session), this hangs forever and times out, leaving the package in `iF` (install Failed) state.

## Correct Procedure

### Step 1: Pre-seed debconf answers BEFORE installing
```bash
echo "phpmyadmin phpmyadmin/dbconfig-install boolean false" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2" | sudo debconf-set-selections
```

### Step 2: Install non-interactively
```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y phpmyadmin
```

### Step 3: Enable Apache config
The package's Apache conf lives at `/etc/phpmyadmin/apache.conf`. The postinst script normally symlinks it, but when dbconfig is skipped this may not happen:
```bash
sudo ln -s /etc/phpmyadmin/apache.conf /etc/apache2/conf-available/phpmyadmin.conf
sudo a2enconf phpmyadmin
```

### Step 4: Create blowfish secret
dbconfig-common normally generates this. Without it, phpMyAdmin throws errors on cookie-auth:
```bash
sudo mkdir -p /var/lib/phpmyadmin
head -c 32 /dev/urandom | base64 | sudo tee /var/lib/phpmyadmin/blowfish_secret.inc.php > /dev/null
echo "<?php \$cfg['blowfish_secret'] = '$(head -c 32 /dev/urandom | base64 | tr -d '\n')';" | sudo tee /var/lib/phpmyadmin/blowfish_secret.inc.php
sudo chown root:www-data /var/lib/phpmyadmin/blowfish_secret.inc.php
sudo chmod 640 /var/lib/phpmyadmin/blowfish_secret.inc.php
```

### Step 5: Create server config (socket-based, bypassing dbconfig-common)
Write to `/etc/phpmyadmin/conf.d/server_socket.php`:
```php
<?php
$dbname = null;
$i = 1;
$cfg['Servers'][$i]['auth_type'] = 'cookie';
$cfg['Servers'][$i]['host'] = 'localhost';
$cfg['Servers'][$i]['socket'] = '/run/mysqld/mysqld.sock';
$cfg['Servers'][$i]['connect_type'] = 'socket';
$cfg['Servers'][$i]['compress'] = false;
$cfg['Servers'][$i]['AllowNoPassword'] = false;
```

### Step 6: Reload Apache and verify
```bash
sudo systemctl reload apache2
dpkg -l | grep phpmyadmin   # should show 'ii' (installed)
```

## Recovery from `iF` (half-installed) State
If the install already failed:
```bash
# Pre-seed, then finish configuration
echo "phpmyadmin phpmyadmin/dbconfig-install boolean false" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive dpkg --configure -a
```

## Pitfalls
- **`debconf-set-selections` and `dpkg --configure` must run in the same sudo session** — if sudo password caching expires between them, the pre-seed is lost and the configure will re-prompt.
- **`whiptail` failure error** ("Failed to open terminal") means `DEBIAN_FRONTEND=noninteractive` wasn't set or wasn't honoured.
- **MariaDB socket path**: On Ubuntu 24.04 with MariaDB 11.8, it's `/run/mysqld/mysqld.sock`. Verify with `mariadb -e "SHOW VARIABLES LIKE 'socket';"`.
- **The default `config.inc.php`** tries to `require('/etc/phpmyadmin/config-db.php')` which doesn't exist without dbconfig-common. The `conf.d/server_socket.php` file loads AFTER this include and overrides the server config. If your override doesn't take, check the include order in `/etc/phpmyadmin/config.inc.php` (the `foreach (glob('/etc/phpmyadmin/conf.d/*.php')` loop runs at the very end, so conf.d files have the last word).

## Access
After install: `http://localhost/phpmyadmin` — log in with MariaDB credentials (e.g., root or a dedicated user).
