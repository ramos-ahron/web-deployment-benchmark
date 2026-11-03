#!/usr/bin/env bash
# usage: BASE_URL=http://<WEB_VM_IP> POST_IDS=1,2,3 [WRITES=1] [NOTES="..."] load-tests/run_test.sh <native|docker> <users> <rep>
set -u
[ $# -eq 3 ] || { echo "usage: $0 <native|docker> <users> <rep>"; exit 1; }
dep=$1 users=$2 rep=$3
: "${BASE_URL:?set BASE_URL}" "${POST_IDS:?set POST_IDS}"
cd "$(dirname "$0")/.."
id=${dep}_${users}users_rep${rep}
out=results/$id
[ -e "$out" ] && { echo "$out already exists, not overwriting"; exit 1; }
mkdir -p "$out"
commit=$(git rev-parse --short HEAD)$(git diff --quiet HEAD -- load-tests || echo -dirty)
start=$(date -u +%FT%TZ)
VUS=$users k6 run --summary-export="$out/summary.json" --out json="$out/raw.json.gz" \
  load-tests/wordpress_browse.js 2>&1 | tee "$out/k6.log"
code=${PIPESTATUS[0]}
cat > "$out/metadata.txt" <<META
run_id=$id
deployment=$dep
users=$users
repetition=$rep
workload=$([ "${WRITES:-0}" = 1 ] && echo read-write-90-10 || echo read-only-preliminary)
warmup=${WARMUP:-2m}
duration=${DURATION:-5m}
start_utc=$start
end_utc=$(date -u +%FT%TZ)
git_commit=$commit
base_url=$BASE_URL
k6_exit_code=$code
notes=${NOTES:-}
META
echo "saved $out (k6 exit $code)"
exit $code
