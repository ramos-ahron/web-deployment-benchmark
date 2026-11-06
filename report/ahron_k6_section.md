## k6 workload and test execution (Ahron)

### Workload

Each virtual user opens the home page, then three posts chosen at random from a fixed list of 25 post IDs (requests of the form /?p=ID). The IDs come from five points across the 10,000-post dataset, so the test does not hit only the newest posts. After every request the user waits a random 1 to 3 seconds. k6 requests the HTML only and does not download images, CSS or scripts. On this site /?p=ID redirects to the post's permalink, so each post view counts as two requests in k6's totals. In the 50-user smoke test, k6 recorded 2,793 requests for 1,596 page views, which is the 1.75 ratio this predicts.

The script has an optional 90/10 read/write mix, but we did not use it. No restore procedure had been tested (infra/backups.md), so writes would have changed the dataset between runs with no way to reset it. Both deployments therefore ran the same read-only workload, which we call a preliminary workload because it leaves out the 90/10 mix from the proposal.

We count two kinds of failure separately. An HTTP failure is a network error or a 4xx or 5xx response. An application-check failure is a response below 400 whose content does not look like a WordPress page.

### Where k6 runs

k6 v2.3.0 runs on seng533-load, a separate RAC VM (m1.small, 2 vCPUs, 2 GB RAM, 20 GB disk, Ubuntu 18.04), apart from the web VM (seng533-web) and the database VM (seng533-db), so load generation does not take CPU or memory from the web server. It sends requests directly to the web VM at 10.1.3.45; there is no Nginx proxy. I connect through the RAC VPN and start each run from an SSH session inside tmux on the load VM. Peak CPU on the load VM during the pilot was [N]% according to Aaron's monitoring.

### Test procedure

Before the pilot I ran 1-user and 2-user smoke tests against both deployments, with no HTTP failures and no failed checks. For each pilot run we started the deployment under test and confirmed the other was stopped. The read-only workload does not change the database, so we did not restore it between runs. Whole-VM CPU and memory samplers ran continuously on all three VMs, and Aaron cut them into per-run files using the start and end times in each run's metadata. k6 ran [10, 25 or 50] users for a 2-minute warm-up followed by a 5-minute measurement with the same number of users in both phases. Warm-up requests are tagged and left out of every reported statistic. Each run is saved under an ID such as native_25users_rep1 with k6's summary, its raw data points, and a metadata file (deployment, users, repetition, UTC start and end, git commit of the workload, notes on problems). Within each repetition the six deployment and user-level combinations were shuffled with a fixed seed (533), so neither deployment always ran first.

### Pilot scope

The pilot has two deployments (native and one Docker container), 10, 25 and 50 users, and three repetitions, which is 18 runs. [N] of them were completed. [List any missing runs and why.] The pilot is meant to compare the two setups under moderate load, not to find maximum capacity.

### Deviations from the proposal

- k6 instead of Locust.
- Ubuntu 18.04 instead of 22.04.
- The two deployments ran one at a time on a single web VM, and there is no separate Nginx proxy VM. The RAC project quota of 8 vCPUs and 8 GB RAM was fully used by the three VMs (infra/vm-inventory.md).
- Fewer load levels and repetitions than the proposal.
- Workload: read-only preliminary, with no 90/10 write mix.
- Dataset: 10,000 posts and 2 comments instead of 10,000 posts and 50,000 comments.
- The Docker container was limited to 2 vCPUs and 3 GB RAM, while native WordPress had the whole 2-vCPU, 4 GB VM (docker/DEPLOYMENT.md).
