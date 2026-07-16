# phpMyAdmin Installation (MariaDB 11.8+, Ubuntu 24/WSL2)

## Problem

`sudo apt install phpmyadmin` hangs on the `dbconfig-common` interactive prompt
("Configure database for phpmyadmin with dbconfig-common?"). Non-interactive
terminals can't answer it.

## Procedure

### 1. Install the package (will fail halfway)

```bash
sudo apt install -y phpmyadmin
# Expect: dpkg hangs at debconf prompt → timeout or Ctrl+C
# Package state will show "iF" (install Failed — half-configured)
```

### 2. Pre-seed debconf to skip dbconfig-common

```bash
echo "phpmyadmin phpmyadmin/dbconfig-install boolean false" | sudo debconf-set-selections
echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2" | sudo debconf-set-selections
```

### 3. Finish dpkg configuration non-interactively

```bash
sudo DEBIAN_FRONTEND=noninteractive dpkg --configure -a
```

### 4. Enable Apache configuration

The package post-install script normally symlinks `/etc/phpmyadmin/apache.conf`
into `/etc/apache2/conf-available/`. If it failed, do it manually:

```bash
sudo ln -s /etc/phpmyadmin/apache.conf /etc/apache2/conf-available/phpmyadmin.conf
sudo a2enconf phpmyadmin
```

### 5. Create blowfish secret (required for cookie auth)

```bash
sudo mkdir -p /var/lib/phpmyadmin
head -c 32 /dev/urandom | base64 | sudo tee /var/lib/phpmyadmin/blowfish_secret.inc.php > /dev/null
echo "<?php \$cfg['blowfish_secret'] = '$(head -c 32 /dev/urandom | base64 | tr -d '\n')';" | sudo tee /var/lib/phpmyadmin/blowfish_secret.inc.php
sudo chown root:www-data /var/lib/phpmyadmin/blowfish_secret.inc.php
sudo chmod 640 /var/lib/phpmyadmin/blowfish_secret.inc.php
```

### 6. Create server config for MariaDB socket connection

```bash
sudo tee /etc/phpmyadmin/conf.d/server_socket.php << 'PHPEOF'
<?php
$dbname = null;
$i = 1;
$cfg['Servers'][$i]['auth_type'] = 'cookie';
$cfg['Servers'][$i]['host'] = 'localhost';
$cfg['Servers'][$i]['socket'] = '/run/mysqld/mysqld.sock';
$cfg['Servers'][$i]['connect_type'] = 'socket';
$cfg['Servers'][$i]['compress'] = false;
$cfg['Servers'][$i]['AllowNoPassword'] = false;
PHPEOF
```

### 7. Reload Apache

```bash
sudo systemctl reload apache2
```

### 8. Verify

```bash
dpkg -l | grep phpmyadmin    # all should show "ii"
curl -s -o /dev/null -w "%{http_code}" http://localhost/phpmyadmin/   # should return 200
```

## Login

phpMyAdmin uses cookie auth — log in with existing MariaDB credentials. Check
available users:

```bash
sudo mariadb -e "SELECT User, Host, Plugin FROM mysql.user;"
```

## Pitfalls

- If sudo password prompts appear, the cached sudo timestamp expired. The user
  must run commands manually in their own terminal.
- dbconfig-common creates `config-db.php` with empty credentials if skipped —
  this is fine; the manual server_socket.php config handles the connection.
- If Apache conf can't be enabled (`a2enconf: Conf phpmyadmin does not exist`),
  the symlink in step 4 wasn't created — check with `ls /etc/apache2/conf-available/`.
