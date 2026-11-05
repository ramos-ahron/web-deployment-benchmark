# Nathan: midterm progress notes

## Completed contribution

Provisioned separate Ubuntu 18.04 VMs for the web application, database, and load generator. Configured network access and verified remote database authentication. Installed Apache/PHP and a native WordPress application connected to MariaDB on a separate VM. Validated the live WordPress version using official checksums, confirmed the schema version, disabled WordPress automatic updates, and recorded the active theme, plugin state, Apache processing mode, and OPcache configuration. Created 9,999 synthetic posts alongside the default post and confirmed a total of 10,000 published posts. Checked the site's HTTP response from the load VM and created private application/database backups.

## Observed evidence

| Check | Supplied result | Meaning |
|---|---|---|
| Web CPU/RAM | nproc=2; free reports approximately 3.9 GiB | Flavor matches baseline |
| DB RAM | approximately 1.9 GiB | Separate DB VM |
| MariaDB status | active (running) | Service started |
| Web-to-DB TCP/auth | connected; wordpress@10.1.3.45 | Remote account works |
| WordPress checksums | success for 6.9.11 | Core matches official checksums |
| DB schema | 60717, already current | Schema check passed |
| Published-post count | 10000 | Seeding reached target |
| Load-to-web HTTP | 200 | Site reachable after seeding |
| Backups | SQL 42 MB, web archive 32 MB | Backup commands completed; restore untested |
| OPcache via HTTP | PHP 7.2.24; loaded yes; enabled 1; 128 MB | Apache runtime setting verified |

This table transcribes supplied outputs; it is not an automated test report. Actual screenshots/logs are not bundled. Add reviewed evidence under `report/figures/` if required, removing credentials and unrelated personal information.

## Changes and constraints to report

- Ubuntu 18.04 and k6 were selected for the implementation.
- The original VM consumed all RAM quota. Resize attempts failed; a snapshot and replacement VMs were used.
- WordPress was initially 6.6.11 and later observed as 6.9.11. Cause unconfirmed; 6.9.11 is now validated and fixed as the comparison version.
- Current 2-vCPU web allocation supports initial tests, not the full planned 2/4/8-vCPU scaling series.
- 50,000 comments have not been generated. Current synthetic content is repetitive and text-only.

## Remaining work

Coordinate Docker parity, k6 runs, monitoring, and team documentation. Gather actual repeated benchmark data and plots. Decide whether the full comment dataset will be completed before measurements; if it changes, rerun both baselines on the same dataset. Test recovery separately. Final report length, rubric, deadline, and ownership should be checked against the course's current instructions; this package is contribution material, not a finished midterm report.
