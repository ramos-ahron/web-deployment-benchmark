# SENG 533 WordPress performance comparison

This repository holds the setup instructions, configuration, scripts, and results for our SENG 533 project. For the midterm, we compare WordPress installed directly on Ubuntu against WordPress running in a single Docker container, using the same load, the same data, and the same database.

The midterm report is due November 6 at 11:59 PM.

## Scope of the midterm

The midterm compares two deployments:

- Native WordPress on Ubuntu 18.04.
- WordPress in one Docker container on the same web VM.

Multi-container testing and the full 2, 4, and 8 vCPU scaling study come after the midterm, unless we finish early and obtain the necessary resources.

### Changes from the proposal

These differ from the original proposal and will be documented in the report:

- Ubuntu 18.04 instead of 22.04.
- k6 instead of Locust.
- Both deployments run on the same web VM, one at a time.
- A reduced pilot: fewer user levels and repetitions than the full study.
- The Nginx proxy VM may be deferred. The current dataset has 10,000 published posts; the planned 50,000 comments remain pending. The report must record the actual dataset used in both deployments.

## Architecture

Three VMs, with an optional fourth for the Nginx proxy if quota allows. The load generator sends HTTP requests to the web VM, which connects to MariaDB on the database VM. With the optional proxy, the generator sends requests to Nginx, which forwards them to the web VM. Both deployments must use the same request path.

| VM | Private IPv4 | Flavor | vCPUs | RAM | Root disk |
|---|---|---|---|---|---|
| seng533-web | 10.1.3.45 | m1.medium | 2 | 4 GB | 40 GB |
| seng533-db | 10.1.5.24 | m1.small | 2 | 2 GB | 20 GB |
| seng533-load | 10.1.3.86 | m1.small | 2 | 2 GB | 20 GB |

- Only one deployment runs on the web VM during any measurement. The other is stopped.
- Both deployments use the same MariaDB VM. The Docker deployment does not run its own database.
- k6 runs on its own VM so load generation does not compete with the application for CPU or memory.
- WordPress files, theme, plugins, and data must be identical for both deployments. Match PHP, web server, and relevant runtime settings as well, or document remaining differences as limitations.
- The Docker image must be pinned to a specific tag. We do not use `latest`.

Current allocations consume 6 vCPUs and all 8 GB of the observed RAM quota. The present web VM has 2 vCPUs; larger scaling experiments require additional resources or a documented design change.

Exact VM roles, resource allocations, and software versions are recorded in [infra/vm-inventory.md](infra/vm-inventory.md).

## Verified native baseline

The following reflects Nathan's supplied checks from November 4, 2026 (Edmonton). This establishes setup functionality, not measured performance.

| Component | Verified configuration |
|---|---|
| WordPress | 6.9.11; official core checksums passed |
| WordPress database schema | 60717; already current |
| PHP | 7.2.24-0ubuntu0.18.04.17 |
| Apache | 2.4.29; prefork with mod_php |
| OPcache through Apache | Loaded and enabled; 128 MB |
| MariaDB | 10.1.48 on the separate DB VM |
| Active theme | Twenty Twenty-Four 1.2 |
| Active plugins | None |
| Published posts | 10,000 |
| WordPress automatic updates | Disabled |
| Load VM to native site | HTTP 200 after dataset generation |
| Private backups | Populated database dump and matching web files created; restore drill pending |

WordPress was initially installed as 6.6.11 and later observed as 6.9.11. The cause is unconfirmed. Version 6.9.11 was subsequently verified and is the current comparison baseline. Docker parity, k6 smoke tests against both deployments, and monitoring readiness still need verification; this README does not claim they are complete.

### Native setup documentation

- [Native installation procedure](native/setup.md)
- [Dataset composition and regeneration](native/dataset.md)
- [Private backup inventory and recovery status](infra/backups.md)
- [Deployment and testing handoff](infra/handoff.md)
- [Nathan's midterm infrastructure contribution](report/nathan_infrastructure_section.md)

The existing site already contains the 10,000-post dataset. Do not regenerate it just to add these files to GitHub. The native helper scripts were assembled after the manual setup and syntax-checked locally; they have not yet been executed on RAC.

## Repository layout

| Folder | Owner | Contents |
|---|---|---|
| `infra/` | Nathan | VM inventory, SSH access notes, connectivity checks, MariaDB setup, backup inventory |
| `native/` | Nathan | Native WordPress setup, dataset, verification scripts, restore and start/stop instructions as completed |
| `docker/` | Adrian | Dockerfile or compose file, `.env.example`, start/stop/check instructions |
| `nginx/` | Adrian | Proxy configuration, or a note that the proxy was deferred |
| `load-tests/` | Ahron | k6 scripts, run instructions, run schedule |
| `monitoring/` | Aaron | Scripts that collect CPU and memory at about one-second intervals |
| `analysis/` | Aaron | Scripts that turn results into graphs and tables |
| `results/` | Ahron, Aaron | One folder per run, named by run ID |
| `report/` | Aaron coordinates; everyone contributes | Report outline, sections from each member, figures, final PDF |

Each folder has its own README with details. If you need to change a file in someone else's folder, tell them first.

## Setup order

1. Create the repository and add everyone as a collaborator (Ahron).
2. Check RAC quotas for instances, vCPUs, and RAM, then confirm which VM hosts the web app, database, and generator (Nathan).
3. Create the Ubuntu 18.04 VMs and arrange SSH access (Nathan).
4. Verify connectivity: generator to web, web to database, and, if present, generator to proxy and proxy to web (Nathan).
5. Install MariaDB, then create the WordPress database and a dedicated user (Nathan).
6. Agree on WordPress, PHP, web server, and database versions (Nathan and Adrian).
7. Install native WordPress and load the test dataset. Save a baseline database backup (Nathan).
8. Install Docker and run WordPress in one container against the same database (Adrian).
9. Test switching between deployments (Nathan and Adrian).
10. Install k6 on the load generator, record its version, and run a 1 to 2 user smoke test against both deployments (Ahron).
11. Start monitoring scripts on all three VMs (Aaron).
12. Run the pilot experiment (Ahron, with the others).
13. Generate graphs and tables, then assemble the report (Aaron).

Do not create extra RAC instances until we confirm quota and where the machines will live. Separate RAC projects are fine only if we verify the network connectivity we need.

## Pilot experiment

The following is the proposed pilot plan, not a record of completed runs. Finalize it after smoke tests and keep `load-tests/run_matrix.csv` consistent with the agreed settings.

| Setting | Value |
|---|---|
| Deployments | Native, single Docker container |
| User levels | 10, 25, 50 (adjust after the smoke test, then keep the same for both) |
| Repetitions | 3 per deployment and user level |
| Warm-up | 2 minutes, excluded from reported statistics |
| Measurement | 5 minutes |
| Think time | 1 to 3 seconds |
| Total runs | 18 |

For every run:

1. Activate the correct deployment and confirm the other is stopped.
2. Restore the baseline dataset using a validated recovery procedure.
3. Start monitoring.
4. Warm up, then measure.
5. Save results under a unique run ID.

Deployment order is interleaved or randomized, not all native first. Nobody changes the application while a measurement is running. Validate the restore procedure before the first experiment; creating backups alone does not establish that recovery works. Use the same workload, cache policy, and total CPU/memory budget for each comparison.

### Run IDs

Run IDs follow `<deployment>_<users>users_rep<n>`, for example `native_25users_rep1` or `docker_50users_rep3`. The same ID names the folder in `results/` and appears in monitoring output. Ahron and Aaron may refine the format, but it must be settled before the first run.

For each run, record deployment, user count, repetition, start/end timestamps and timezone, workload version or Git commit, and any issues.

## Rules

- Never commit passwords, private SSH keys, VPN files, or real `.env` files. `.gitignore` helps with untracked files but does not protect already tracked files or manual web uploads. Review `git status` and the staged diff before committing.
- Share database credentials privately. Commit `.env.example` with placeholders only.
- Each person provides their own public SSH key and keeps their private key.
- Do not use an unpinned `latest` Docker image.
- Only the deployment under test runs on the web VM during measurements.
- Record setup instructions, configuration, and results here.
- Everyone writes their own report material and records their actual contributions.
- If something blocks you, post the exact error and what you tried in the group chat, removing credentials first.

Database dumps, application backup archives, and raw point-by-point k6 output are excluded by `.gitignore` because of size and sensitivity. Keep private backups outside GitHub and document their locations and reviewed recovery procedure in `native/` or `infra/`. VM-local backups should also have an authorized private off-VM copy before destructive changes. Commit benchmark summaries and monitoring CSVs under `results/`; do not put them in ignored `raw/` folders.

## Schedule

| When | Goal |
|---|---|
| November 4 | Repository, quota and architecture decisions, access, initial setup, scripts, report outline |
| November 5, morning | Working deployments, dataset, smoke tests, monitoring |
| November 5, afternoon and evening | Pilot runs and graphs |
| November 6, morning | Finish writing and results discussion |
| November 6, afternoon | Group review and submission, with time to spare |

If we run short on time, we reduce the pilot scope and report the limitation instead of rushing inconsistent tests.

## Report requirements

The report must stay within eight pages and cover:

1. Status against the proposal's original milestones.
2. Plan adjustments listed above.
3. Preliminary results with graphs or tables.
4. Infrastructure details: hosting locations, VM specifications, where k6 and other scripts run, and confirmation that generation is separate from the web server.
5. Updated milestones.
6. Individual contribution breakdown.

Claims must separate completed work from planned work. We do not claim maximum capacity or a clear winner unless measurements support it. The native deployment runs within a VM; it is not physical bare metal.

## Cloning and contributing

Replace `<repository-url>` with this repository's clone URL:

```bash
git clone <repository-url> web-deployment-benchmark
cd web-deployment-benchmark
```

Pull before you start working, use a branch, keep commits small, and write commit messages that say what changed. Before committing, run `git status` and `git diff --cached` and check that no credentials, keys, or `.env` files are staged. Committing files does not automatically deploy them to the VMs.

## Team

- Nathan: infrastructure, database, native WordPress, dataset preparation
- Adrian: Docker WordPress, proxy configuration
- Ahron: GitHub repository, k6 workload, experiment execution
- Aaron: monitoring, analysis, report assembly
