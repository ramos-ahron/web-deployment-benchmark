# Team handoff

## Nathan: completed

Three RAC VMs; SSH/network troubleshooting; remote MariaDB; Apache/PHP native deployment; WordPress validation; 10,000-post seed; private web/database backups; configuration records. This package supplies documentation and repeatable helper commands, not executed Docker or k6 implementations.

## Adrian: container deployment

Use the same web host for sequential native/container trials, the same external database, WordPress 6.9.11, Twenty Twenty-Four 1.2, no active plugins, and matching PHP/Apache processing and OPcache settings. Compare full versions/configurations, not just image labels. Image availability/compatibility with this legacy stack still needs confirmation; a modern default WordPress image will not automatically match this baseline.

The DB permits wordpress from 10.1.3.45. Verify actual container-to-DB source/authentication; do not assume bridging preserves that identity. Configure secrets privately. Coordinate stopping the native service before binding the container to its port. Do not run native and container benchmark workloads concurrently. Preserve the site URL, content, theme, plugin state, and permalink behavior. Do not run another WordPress installer against the populated DB.

## Ahron: k6 and GitHub

Use seng533-load (10.1.3.86), separate from web/database. Confirm k6 is installed there and record its version; only the web VM's k6 version was supplied. Define a closed-workload VU script, think time, URL mix, warm-up, measurement duration, repeated trials, and error checks. Save scripts and exports with run IDs and Git commit. No load-test results are claimed yet.

## Aaron: monitoring/report

VM access was deferred and must be arranged if needed. Collect web, DB, and generator CPU/memory plus swap activity and enough system information to detect bottlenecks. Align timestamps with each k6 run. A maxed-out generator or database can hide web deployment differences.

## Fair-comparison checklist

- Same content snapshot, software/theme/plugins, endpoints and workload.
- Equal total CPU/memory budgets for the configurations being compared; record limits and background processes.
- Same warm-up/cache policy; enabled OPcache is not WordPress full-page caching.
- Record Nginx overhead when a balancer is introduced and define whether it belongs in the resource budget.
- Repeat trials and report variation; one smoke check is not evidence of speedup.
- Label the baseline as native deployment within a VM, not physical bare metal.
- Current web VM has only 2 vCPUs. Four containers each limited to 2 CPUs cannot supply 8 physical/virtual CPU capacity on that host. Larger planned scaling needs more allocation/quota or an explicitly documented revised design.
- Current project uses all 8 GB RAM. The planned 4/8-vCPU VM experiments are not provisioned by this setup.
