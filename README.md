# SENG 533 WordPress performance comparison

This repository holds the setup instructions, configuration, scripts, and results for our SENG 533 midterm project. We compare WordPress installed directly on Ubuntu against WordPress running in a single Docker container, using the same load, the same data, and the same database.

The midterm report is due November 6 at 11:59 PM.

## Scope of the midterm

The midterm compares two deployments:

- Native WordPress on Ubuntu 18.04.
- WordPress in one Docker container on the same web VM.

Multi-container testing and the full 2, 4, and 8 vCPU scaling study come after the midterm, unless we finish early.

### Changes from the proposal

These differ from the original proposal and will be documented in the report:

- Ubuntu 18.04 instead of 22.04.
- k6 instead of Locust.
- Both deployments run on the same web VM, one at a time.
- A reduced pilot: fewer user levels and repetitions than the full study.
- The Nginx proxy VM and the full 10,000 post / 50,000 comment dataset may be deferred. If so, the report says what was used instead and records the actual counts.

## Architecture

Three VMs, with an optional fourth for the Nginx proxy if quota allows.

```
  +-----------------+        +----------------------+        +-----------------+
  | Load generator  | -----> | Web VM               | -----> | Database VM     |
  | k6              |  HTTP  | native WordPress  OR |  SQL   | MariaDB         |
  |                 |        | Docker WordPress     |        |                 |
  +-----------------+        +----------------------+        +-----------------+

  With the optional proxy VM, the load generator talks to Nginx instead,
  and Nginx forwards to the web VM. Both deployments must use the same path.
```

- Only one deployment runs on the web VM during any measurement. The other is stopped.
- Both deployments use the same MariaDB VM. The Docker deployment does not run its own database.
- k6 runs on its own VM so load generation does not compete with the application for CPU or memory.
- WordPress files, theme, plugins, and data are identical for both deployments.
- The Docker image is pinned to a specific tag. We do not use `latest`.

Exact VM roles, flavors, CPU counts, RAM, disk, and software versions are recorded in `infra/`.

## Repository layout

| Folder | Owner | Contents |
| --- | --- | --- |
| `infra/` | Nathan | VM inventory, SSH access notes, connectivity checks, MariaDB setup |
| `native/` | Nathan | Native WordPress install, dataset creation, restore and start/stop instructions |
| `docker/` | Adrian | Dockerfile or compose file, `.env.example`, start/stop/check instructions |
| `nginx/` | Adrian | Proxy configuration, or a note that the proxy was deferred |
| `load-tests/` | Ahron | k6 scripts, run instructions, run schedule |
| `monitoring/` | Aaron | Scripts that collect CPU and memory at about one-second intervals |
| `analysis/` | Aaron | Scripts that turn results into graphs and tables |
| `results/` | Ahron, Aaron | One folder per run, named by run ID |
| `report/` | Aaron | Report outline, sections from each member, figures, final PDF |

Each folder has its own README with details. If you need to change a file in someone else's folder, tell them first.

## Setup order

1. Create the repository and add everyone as a collaborator (Nathan).
2. Check RAC quotas for instances, vCPUs, and RAM, then confirm which VM hosts the web app, the database, and the load generator (Nathan).
3. Create the Ubuntu 18.04 VMs and arrange SSH access (Nathan).
4. Verify connectivity: load generator to web VM, web VM to database VM, and, if there is a proxy, load generator to proxy and proxy to web VM (Nathan).
5. Install MariaDB, then create the WordPress database and a dedicated user (Nathan).
6. Agree on WordPress, PHP, web server, and database versions (Nathan and Adrian).
7. Install native WordPress and load the test dataset. Save a baseline database backup (Nathan).
8. Install Docker and run WordPress in one container against the same database (Adrian).
9. Test switching between deployments (Nathan and Adrian).
10. Install k6 on the load generator and run a 1 to 2 user smoke test against both deployments (Ahron).
11. Start monitoring scripts on all three VMs (Aaron).
12. Run the pilot experiment (Ahron, with the others).
13. Generate graphs and tables, then assemble the report (Aaron).

Do not create extra RAC instances until we confirm quota and where the machines will live. Separate RAC projects are fine only if we verify the network connectivity we need.

## Pilot experiment

| Setting | Value |
| --- | --- |
| Deployments | Native, single Docker container |
| User levels | 10, 25, 50 (adjust after the smoke test, then keep the same for both) |
| Repetitions | 3 per deployment and user level |
| Warm-up | 2 minutes, excluded from reported statistics |
| Measurement | 5 minutes |
| Think time | 1 to 3 seconds |
| Total runs | 18 |

For every run:

1. Activate the correct deployment and confirm the other is stopped.
2. Restore the baseline dataset.
3. Start monitoring.
4. Warm up, then measure.
5. Save results under a unique run ID.

Deployment order is interleaved or randomized, not all native first. Nobody changes the application while a measurement is running.

### Run IDs

Run IDs follow `<deployment>_<users>users_rep<n>`, for example `native_25users_rep1` or `docker_50users_rep3`. The same ID names the folder in `results/` and appears in monitoring output. Ahron and Aaron may refine the format, but it must be settled before the first run.

For each run, record the deployment, user count, repetition, start and end timestamps, workload version or Git commit, and any issues.

## Rules

- Never commit passwords, private SSH keys, VPN files, or real `.env` files. The `.gitignore` blocks the common cases, but check `git status` before you commit.
- Share database credentials privately, not through this repository. Commit `.env.example` with placeholders only.
- Each person provides their own public SSH key and keeps their private key.
- Do not use an unpinned `latest` Docker image.
- Only the deployment under test runs on the web VM during measurements.
- Record setup instructions, configuration, and results here.
- Everyone writes their own report material and records their actual contributions.
- If something blocks you, post the exact error and what you tried in the group chat right away.

Database dumps and raw k6 output are excluded by `.gitignore` because of size and sensitivity. Keep them on the VMs and write down the path and restore command in `native/` or `infra/`.

## Schedule

| When | Goal |
| --- | --- |
| November 4 | Repository, quota and architecture decisions, access, initial setup, scripts, report outline |
| November 5, morning | Working deployments, dataset, smoke tests, monitoring |
| November 5, afternoon and evening | Pilot runs and graphs |
| November 6, morning | Finish writing and results discussion |
| November 6, afternoon | Group review and submission, with time to spare |

If we run short on time, we reduce the pilot scope and report the limitation instead of rushing inconsistent tests.

## Report requirements

The report must stay within eight pages and cover:

1. Status against the proposal's original milestones.
2. Plan adjustments (listed above).
3. Preliminary results with graphs or tables.
4. Infrastructure details: hosting locations, VM specifications, where k6 and other scripts run, and confirmation that load generation is separate from the web server.
5. Updated milestones.
6. Individual contribution breakdown.

Claims must separate completed work from planned work. We do not claim maximum capacity or a clear winner unless the measurements support it.

## Cloning and contributing

```bash
git clone <repository-url>
cd seng533-wp-benchmark
```

Pull before you push, keep commits small, and write commit messages that say what changed. Before committing, run `git status` and check that no credentials, keys, or `.env` files are staged.

## Team

- Nathan: GitHub, infrastructure, database, native WordPress
- Adrian: Docker WordPress, proxy configuration
- Ahron: k6 workload, experiment execution
- Aaron: monitoring, analysis, report assembly
