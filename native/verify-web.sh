#!/usr/bin/env bash
# Read-only checks; run on seng533-web from an ubuntu shell.
set -euo pipefail
wp_path=/var/www/html
hostname
nproc
free -h
php -v
apache2 -v
sudo apache2ctl -M 2>/dev/null | grep -E 'mpm_|php'
sudo -u www-data wp --path="$wp_path" core version
sudo -u www-data wp --path="$wp_path" core verify-checksums --version=6.9.11
sudo -u www-data wp --path="$wp_path" config get AUTOMATIC_UPDATER_DISABLED
sudo -u www-data wp --path="$wp_path" theme list
sudo -u www-data wp --path="$wp_path" plugin list
sudo -u www-data wp --path="$wp_path" post list --post_type=post --post_status=publish --format=count
printf '\n'
# No wp-config.php dump: it contains credentials.
