# Native setup runbook

Owner: Nathan. This records the completed manual setup and provides recreation guidance. Do not rerun it on working VMs. Repository commands do not configure RAC automatically. Installation from today's repositories may not reproduce the recorded package versions: compare installed versions against `../infra/vm-inventory.md` and record any deviations.

## 1. RAC and SSH

Create the VMs with flavors listed in `../infra/vm-inventory.md`, Ubuntu 18.04, your own key pair, and the appropriate security group. Keep the private key on your workstation. Connect the Cybera VPN, then run from PowerShell in the directory containing your key (separate terminal for each VM):

```powershell
ssh -i ./cloud.key ubuntu@10.1.3.45
ssh -i ./cloud.key ubuntu@10.1.5.24
ssh -i ./cloud.key ubuntu@10.1.3.86
```

Use each teammate's public key for their authorized VM access. Do not share private keys. Verify `hostname`, `nproc`, and `free -h`. Addresses must be updated if recreated instances receive new IPs.

## 2. MariaDB on seng533-db

```bash
sudo apt-get update
sudo apt-get install mariadb-server
sudo systemctl status mariadb --no-pager
sudo mysql
```

Inside the SQL console, replace the password placeholder privately before executing:

```sql
CREATE DATABASE wordpress CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wordpress'@'10.1.3.45' IDENTIFIED BY 'REPLACE_WITH_PRIVATE_PASSWORD';
GRANT ALL PRIVILEGES ON wordpress.* TO 'wordpress'@'10.1.3.45';
EXIT;
```

Set `bind-address = 10.1.5.24` in `/etc/mysql/mariadb.conf.d/50-server.cnf`, then:

```bash
sudo systemctl restart mariadb
sudo ss -lntp | grep ':3306'
```

Allow the required web-to-DB traffic in RAC. Do not open the DB to every source merely to troubleshoot.

## 3. Apache/PHP on seng533-web

```bash
sudo apt-get update
sudo apt-get install apache2 php7.2 libapache2-mod-php7.2 php7.2-cli php7.2-mysql php7.2-curl php7.2-gd php7.2-mbstring php7.2-xml php7.2-zip mariadb-client curl
```

Check `php -v`, `apache2 -v`, and `curl -I http://localhost/`. Verify DB authentication with the password prompt:

```bash
mysql -h 10.1.5.24 -u wordpress -p wordpress
```

```sql
SELECT DATABASE(), CURRENT_USER();
EXIT;
```

Expected identity: `wordpress@10.1.3.45`.

## 4. WordPress files and browser installation

The original install downloaded 6.6.11; the validated baseline is now 6.9.11. For recreation, obtain the exact target release from the official release archive and verify checksums. Do not silently use `latest`.

```bash
mkdir -p ~/seng533-setup
cd ~/seng533-setup
curl -fLO https://wordpress.org/wordpress-6.9.11.tar.gz
tar -xzf wordpress-6.9.11.tar.gz
sudo cp -a wordpress/. /var/www/html/
```

On a fresh Apache install, move its default index page if present:

```bash
if [ -f /var/www/html/index.html ]; then sudo mv /var/www/html/index.html ~/seng533-setup/apache-default-index.html; fi
sudo chown -R www-data:www-data /var/www/html
```

Allow HTTP from the intended browser/load-generator sources. Open `http://10.1.3.45/` and supply DB name/user `wordpress`, DB host `10.1.5.24`, the private DB password, and table prefix `wp_`. Site title: SENG 533 Performance Test. Admin login used: seng533admin; choose a private password. No passwords belong in this runbook.

## 5. WP-CLI and baseline settings

Install WP-CLI using its official installation guide. The observed installed version is 2.12.0; avoid silently changing that version when recreating the experiment. The executable is `/usr/local/bin/wp`. Then:

```bash
sudo -u www-data wp --path=/var/www/html core version
sudo -u www-data wp --path=/var/www/html core verify-checksums --version=6.9.11
sudo -u www-data wp --path=/var/www/html core update-db
sudo -u www-data wp --path=/var/www/html config set AUTOMATIC_UPDATER_DISABLED true --raw
```

Use Twenty Twenty-Four version 1.2, no active plugins, and the same URL/permalink settings as the existing baseline. A fresh release archive might bundle different themes: match the recorded theme explicitly rather than assuming it is present. Preserve the existing theme directory in the private web backup when replicating. Existing URLs include `/index.php/2026/11/04/hello-world/`.

Run `bash native/verify-web.sh` from the repository checkout on web. OPcache values in `../infra/vm-inventory.md` were verified through Apache, not inferred from the CLI configuration. A CLI PHP setting alone cannot prove the HTTP runtime setting.

## 6. Dataset, smoke check, backups

Follow `dataset.md` for fresh-site population. Run `bash native/check-from-load.sh` from the repository checkout on load. Preserve the resulting files/database as described in `../infra/backups.md`. A successful HTTP request is a functionality check, not a performance result.

## References

- https://wordpress.org/download/releases/
- https://make.wordpress.org/cli/handbook/guides/installing/
- https://developer.wordpress.org/cli/commands/post/generate/
- https://developer.wordpress.org/cli/commands/core/verify-checksums/
