# results

Owners: Ahron (k6 output) and Aaron (monitoring output)

One folder per run, named by run ID, for example `native_25users_rep1`.

Suggested layout, to be confirmed by Ahron and Aaron:

```
results/
  native_25users_rep1/
    metadata.json      deployment, users, repetition, timestamps, workload commit, issues
    k6-summary.json    end-of-test summary from k6
    web-vm.csv         CPU and memory on the web VM
    db-vm.csv          CPU and memory on the database VM
    loadgen-vm.csv     CPU and memory on the load generator
    docker-stats.csv   container statistics, Docker runs only
```

Raw point-by-point k6 output is ignored by Git because of its size. Keep it on the load generator VM or in shared storage, and note where it is.
