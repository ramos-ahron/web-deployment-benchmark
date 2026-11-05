#!/usr/bin/env bash
# Functionality only, not a benchmark. Run on seng533-load.
set -euo pipefail
url="${1:-http://10.1.3.45/}"
code=$(curl -L -sS -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 30 "$url")
printf 'HTTP status: %s\n' "$code"
[[ "$code" == 200 ]] || { printf 'Smoke check failed.\n' >&2; exit 1; }
