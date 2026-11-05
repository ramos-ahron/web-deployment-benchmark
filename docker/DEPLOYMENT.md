
# SENG 533 — Docker WordPress Deployment

## Overview

This directory contains the Docker implementation for
comparing native WordPress against containerized WordPress.

Both deployments run sequentially on the same Cybera
web VM and connect to the same external MariaDB server.

## Environment

- Web VM: seng533-web (10.1.3.45)
- Database VM: 10.1.5.24
- Operating system: Ubuntu 18.04.5 LTS
- WordPress: 6.9.11
- PHP: 7.2.24
- Apache: 2.4.29
- Docker: 20.10.21
- Docker Compose: 1.17.1

## Dataset

- 10,000 published posts
- 2 comments
- Theme: Twenty Twenty-Four 1.2
- Active plugins: None

The proposed 50,000-comment dataset is deferred.

## Container Configuration

- Image: seng533-wordpress:local
- Container name: seng533-wordpress
- CPU limit: 2 vCPUs
- Memory limit: 3 GB
- Apache with mod_php and prefork MPM
- PHP memory_limit: 128M
- PHP max_execution_time: 30 seconds

The container uses a separate copy of the WordPress
files and connects to the existing MariaDB VM.


The `.env.example` file documents the database connection settings but is not currently consumed by Docker Compose. The experimental deployment uses a private `site/wp-config.php`, excluded from Git, containing the connection settings for the external MariaDB server. A fresh deployment requires provisioning the WordPress files and private database configuration separately.

## Switching to Docker

Coordinate with the team before switching.

1. Confirm the database baseline is backed up.
2. Stop native Apache:

   sudo systemctl stop apache2

3. Start Docker WordPress:

   cd ~/seng533-docker
   sudo docker-compose up -d

4. Verify the deployment:

   sudo docker ps
   sudo systemctl is-active apache2
   curl -I http://10.1.3.45/

## Switching to Native WordPress

1. Stop Docker WordPress:

   cd ~/seng533-docker
   sudo docker-compose down

2. Restart native Apache:

   sudo systemctl start apache2

3. Verify:

   sudo systemctl is-active apache2
   sudo docker ps
   curl -I http://10.1.3.45/

## Experimental Controls

- Both deployments use the same WordPress version.
- Both use matching PHP and Apache versions.
- Both use the same WordPress dataset and MariaDB VM.
- Both use the same web VM and target URL.
- Only one deployment serves traffic during measurements.
- Database state should be restored to baseline as needed.
- Whole-VM CPU and memory usage are measured.

## Limitations

- Ubuntu 18.04 and PHP 7.2 are legacy software.
- Docker has explicit resource limits.
- Native WordPress relies on host-level resources.
- A separate Nginx proxy is not configured.
- Multi-container scaling is deferred.
- The 50,000-comment dataset is deferred.

## Security

Do not commit database passwords, wp-config.php,
private keys, backups, or real environment files.

## Contributor

Adrian — Docker WordPress deployment and configuration.
