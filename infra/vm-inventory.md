# Verified environment

Recorded from Nathan's terminal output and screenshots, November 4, 2026 Edmonton (some VM timestamps are November 5 UTC).

| VM | Private IPv4 | Flavor | vCPUs | RAM | Root disk | Role |
|---|---|---|---|---|---|---|
| seng533-web | 10.1.3.45 | m1.medium | 2 | 4 GB | 40 GB | Native WordPress; same host planned for Docker |
| seng533-db | 10.1.5.24 | m1.small | 2 | 2 GB | 20 GB | Shared MariaDB |
| seng533-load | 10.1.3.86 | m1.small | 2 | 2 GB | 20 GB | Separate k6 generator |

All three use Ubuntu 18.04 in Nathan's Cybera RAC project. Current allocated total: 6 vCPUs and 8 GB RAM. Project quota observed: 8 vCPUs, 8 GB RAM, 8 instances. No RAM headroom remains. Web was rebuilt from `seng533-tutorial-backup`; DB/load were created from the Ubuntu image. Web reports 4 GB swap and DB reports 2 GB swap; record actual swap activity during tests.

## Software

| Component | Observed version/configuration |
|---|---|
| WordPress | 6.9.11; official core checksum verification succeeded |
| WordPress DB schema | 60717; core update-db reported current |
| PHP | 7.2.24-0ubuntu0.18.04.17 |
| Apache | 2.4.29 (Ubuntu), package candidate previously 2.4.29-1ubuntu4.27 |
| Apache processing | mpm_prefork_module and php7_module |
| OPcache | Loaded; enabled=1; memory_consumption=128 MB, checked via HTTP |
| MariaDB | 10.1.48-MariaDB-0ubuntu0.18.04.1 |
| WP-CLI | 2.12.0 |
| Active theme | twentytwentyfour 1.2 |
| Active plugins | None |
| Installed inactive plugins | akismet 5.3.3, hello 1.7.2 |
| WordPress auto-updater | AUTOMATIC_UPDATER_DISABLED=true |
| Published posts | 10,000 |
| k6 on web | 2.3.0 observed; not the intended test runner |
| k6 on load | Version/install confirmation pending from Ahron |

Inactive themes observed: twentytwentyfive 1.4, twentytwentythree 1.5, twentytwentytwo 1.8. Do not infer their activation or updates from availability notices.

## Connections

Load VM -> HTTP port 80 on web VM -> MariaDB TCP port 3306 on DB VM.

Browser access uses the Cybera VPN. The database account is `wordpress` restricted to source `10.1.3.45`, with privileges only on `wordpress.*`. MariaDB binds to `10.1.5.24`. Credentials are supplied privately, never committed.

Observed SSH source inside the VM was `10.1.8.18`, while Windows reported VPN interface IP `10.254.0.14`. Rules using the latter initially failed; use the source actually observed by the server. That source is an observation, not a promise it will remain unchanged after reconnecting. The `default` security group was attached; intra-group traffic was allowed. SSH and HTTP access were configured during setup. Confirm the current effective rules before claiming narrowly restricted DB access: intra-group rules can be broader than an added port-specific rule.

## Version discrepancy

The initial extracted WordPress version was 6.6.11. Later the live installation reported 6.9.11; its official checksums passed and its database schema was current. The cause of the change is unconfirmed. Automatic updating was subsequently disabled. Use 6.9.11 as the recorded baseline and match it in Docker.

These legacy versions are chosen for the course experiment. Do not describe the environment as a current production deployment.
