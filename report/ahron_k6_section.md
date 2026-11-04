## k6 workload and test execution (Ahron)

### Workload

Each virtual user opens the home page, then three posts chosen at random from a fixed list of [N] post IDs (requests of the form /?p=ID). After every request the user waits a random 1 to 3 seconds. k6 requests the HTML only and does not download images, CSS or scripts.

[Keep one of the next two paragraphs.]

About 10% of iterations post a comment instead of browsing, which gives the 90/10 read/write mix from the proposal. A comment counts as saved only if WordPress replies with a redirect to the new comment. [Describe how we confirmed the database row count went up, and by how much.]

Comment writes were not working on both deployments by [date], so both ran the same read-only workload. We call it preliminary because it leaves out the 90/10 mix from the proposal.

We count two kinds of failure separately. An HTTP failure is a network error or a 4xx or 5xx response. An application-check failure is a response below 400 whose content does not look like a WordPress page [or a comment that was not saved].

### Where k6 runs

k6 v[VERSION] runs on its own RAC VM ([flavor], [N] vCPUs, [N] GB RAM, Ubuntu 18.04), apart from the web VM and the database VM, so load generation does not take CPU or memory from the web server. It reaches the web VM [directly at <path> / through the Nginx proxy]. I connect through the RAC VPN and start runs from an SSH session inside tmux on the load VM. Peak CPU on the load VM during the pilot was [N]% according to Aaron's monitoring.

### Test procedure

For each run we started the deployment under test, confirmed the other was stopped, restored the baseline database, and had monitoring started. k6 then ran [N] users for a 2-minute warm-up followed by a 5-minute measurement with the same number of users. Warm-up requests are tagged and left out of every reported statistic. Each run is saved under an ID such as native_25users_rep1 with k6's summary, the raw data points, and a metadata file (deployment, users, repetition, UTC start and end, git commit of the workload, notes on problems). Within each repetition the six deployment and user-level combinations were shuffled with a fixed seed (533), so neither deployment always ran first.

### Pilot scope

The pilot has two deployments (native and one Docker container), [10, 25 and 50] users, and three repetitions, which is 18 runs. [N] of them were completed. [List any missing runs and why.] The pilot is meant to compare the two setups under moderate load, not to find maximum capacity.

### Deviations from the proposal

- k6 instead of Locust. [Reason, ask the team.]
- Ubuntu 18.04 instead of 22.04. [Reason, ask the team.]
- The two deployments ran one at a time on a single web VM. [What the proposal had.]
- Fewer load levels and repetitions than the proposal. [Proposal values.]
- Workload: [read-only preliminary / 90/10 mix].
- Dataset: [actual posts and comments] instead of 10,000 posts and 50,000 comments.
- [Nginx proxy used / deferred, per Adrian.]
