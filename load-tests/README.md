# load-tests

k6 workload for the WordPress pilot (native install vs one Docker container). Written by Ahron.

## What a run does

Each virtual user loads the home page, then three posts picked at random from POST_IDS (`/?p=ID`), and waits 1 to 3 seconds after every request. A run has two phases back to back with the same number of users: a warm-up (2 minutes by default) and a measurement phase (5 minutes by default). Every data point is tagged `phase=warmup` or `phase=measure`. The thresholds and the numbers to report use `{phase:measure}` only.

Without `WRITES=1` the workload is read-only and tagged `read-only-preliminary`. With `WRITES=1`, about 10% of iterations post a comment instead of browsing (the 90/10 mix). A comment counts as saved when WordPress replies with a redirect to `#comment-<id>`.

k6 requests the HTML only. It does not download images, CSS or scripts. If `/?p=ID` redirects to another URL, k6 follows it and each hop counts as a request.

Two kinds of failure are recorded separately. `http_req_failed` covers network errors and 4xx/5xx responses. `app_check_failed` covers a response below 400 whose content is wrong (no `wp-content` in the page, or a comment that was not saved). A request is never counted in both.

## Settings

| Variable | Default | Meaning |
|---|---|---|
| BASE_URL | none, required | `http://<WEB_VM_IP>`, no trailing slash |
| POST_IDS | none, required | comma-separated post IDs that exist in the dataset |
| VUS | 1 | users (the wrapper sets it from its second argument) |
| WARMUP | 2m | warm-up length |
| DURATION | 5m | measurement length |
| WRITES | off | set to `1` for the 90/10 mix |
| MARKER | wp-content | text a real page must contain |

## Running

Run from the repo root on the load-generator VM. The wrapper takes deployment (`native` or `docker`), users, and repetition.

```
export BASE_URL=http://<WEB_VM_IP> POST_IDS=<POST_IDS>
load-tests/run_test.sh native 10 1
load-tests/run_test.sh docker 25 2
WRITES=1 load-tests/run_test.sh native 50 3
WARMUP=5s DURATION=10s load-tests/run_test.sh native 2 1    # short dry run
```

Plain k6 without the wrapper:

```
VUS=10 BASE_URL=http://<WEB_VM_IP> POST_IDS=<POST_IDS> k6 run load-tests/wordpress_browse.js
```

The wrapper refuses to overwrite an existing run folder. k6 exits with 99 if an error-rate threshold is crossed. The results are still saved and the exit code goes in metadata.txt.

## Output

Each run gets `results/<deployment>_<users>users_rep<n>/`, for example `results/native_25users_rep1/`:

- `summary.json`: k6 summary export, including the `{phase:measure}` entries
- `raw.json.gz`: every data point with its tags (filter `"phase":"measure"`)
- `metadata.txt`: key=value lines with run_id, deployment, users, repetition, workload, warmup, duration, start_utc, end_utc, git_commit, base_url, k6_exit_code, notes
- `k6.log`: what k6 printed

Times are UTC. The measurement phase starts about WARMUP after start_utc. The exact window is the first and last `measure` points in the raw file. A git_commit ending in `-dirty` means load-tests had uncommitted changes.

Folders starting with `smoke-` are test runs and are not committed.

## Run order

`run_matrix.csv` lists the 18 runs. Within each repetition the six deployment/user-level pairs are shuffled with a fixed seed (533), so native and Docker alternate over time and a stopped pilot is still balanced. To regenerate after changing the user levels:

```
python3 - <<'EOF'
import random
r = random.Random(533)
rows = []
for rep in (1, 2, 3):
    block = [(d, u) for d in ("native", "docker") for u in (10, 25, 50)]
    r.shuffle(block)
    rows += [(d, u, rep) for d, u in block]
print("order,run_id,deployment,users,rep")
for i, (d, u, rep) in enumerate(rows, 1):
    print(f"{i},{d}_{u}users_rep{rep},{d},{u},{rep}")
EOF
```
