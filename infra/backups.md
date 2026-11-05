# Private backups

These files remain on the VMs and are NOT included in GitHub.

| VM | Path | Observed size/status |
|---|---|---|
| web | `/home/ubuntu/seng533-backups/wordpress-native-initial.tar.gz` | Initial archive; directory listing verified, version not rechecked |
| db | `/home/ubuntu/seng533-backups/wordpress-initial.sql` | 690 KB; dump-completed footer observed |
| db | `/home/ubuntu/seng533-backups/wordpress-10000-posts.sql` | 42 MB; dump command exited successfully |
| web | `/home/ubuntu/seng533-backups/wordpress-native-6.9.11.tar.gz` | 32 MB; archive command exited successfully |

DB backup mode: 600, ubuntu owned. Latest web archive: 600, root owned. The archives contain credentials and database dumps contain user records/password hashes. Do not commit them, wp-config.php, or private keys. The old and new backup sets are separate; do not mix versions casually.

## Creating future backups

Coordinate a quiet period without application edits or schema changes. On db (timestamp avoids overwriting an earlier snapshot):

```bash
mkdir -p ~/seng533-backups && (umask 077; sudo mysqldump --single-transaction --quick wordpress > ~/seng533-backups/wordpress-$(date -u +%Y%m%dT%H%M%SZ).sql)
```

On web:

```bash
sudo sh -c 'umask 077; mkdir -p /home/ubuntu/seng533-backups; tar -czf /home/ubuntu/seng533-backups/wordpress-native-$(date -u +%Y%m%dT%H%M%SZ).tar.gz -C /var/www/html .'
```

Record version and dataset counts alongside each pair. Single-transaction is intended for transactional tables; it is not a substitute for coordinating DDL/nontransactional changes. These two commands are not an atomic cross-VM snapshot.

## Recovery status

No restore drill has been completed. A successful archive/dump is not proof of recovery. The web-root archive does not include Apache/PHP system configuration; the WordPress-only SQL dump does not include MariaDB accounts/grants. Use the runbook to reconstruct those. VM-local backups are also lost if the VM/disk is deleted; keep an authorized private off-VM copy before destructive work. Restore to an isolated database/site first and verify login, content, version, URLs, and counts before replacing a working experiment.
