#!/usr/bin/env bash
# Run once before the campaign (and again after). Shows clock offset of web/db VMs relative to this VM.
# usage: WEB_HOST=user@ip DB_HOST=user@ip monitoring/check_clocks.sh
: "${WEB_HOST:?}" "${DB_HOST:?}"
for h in "$WEB_HOST" "$DB_HOST"; do
  a=$(date +%s.%N); r=$(ssh -o BatchMode=yes ${SSH_OPTS:-} "$h" 'date +%s.%N'); b=$(date +%s.%N)
  awk -v a="$a" -v b="$b" -v r="$r" -v h="$h" 'BEGIN{printf "%s offset vs load VM: %+.3f s (round trip %.3f s)\n", h, r-(a+b)/2, b-a}'
done
echo "Want |offset| well under 0.5 s. If not: sudo chronyc makestep (or fix NTP) on the offending VM."
