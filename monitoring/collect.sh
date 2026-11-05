#!/usr/bin/env bash
# Whole-VM CPU + memory sampler, ~1 s interval. Linux only.
# Runs on web, db and load-generator VMs (started by monitor_ctl.sh).
# usage: collect.sh <out.csv> [interval_seconds=1]      stop with kill/SIGTERM
OUT=${1:?out.csv}; INT=${2:-1}
echo "ts_epoch,cpu_pct,mem_used_mb,mem_total_mb,mem_used_pct,load1" > "$OUT"
cpu(){ awk '/^cpu /{t=0; for(i=2;i<=9;i++) t+=$i; print t, $5+$6}' /proc/stat; }   # total, idle+iowait
read -r pt pi < <(cpu)
trap 'exit 0' TERM INT
while true; do
  sleep "$INT"
  read -r t i < <(cpu)
  ts=$(date +%s.%N)
  awk -v ts="$ts" -v dt=$((t-pt)) -v di=$((i-pi)) -v l="$(cut -d' ' -f1 /proc/loadavg)" '
    /^MemTotal/{tot=$2} /^MemAvailable/{av=$2}
    END{printf "%s,%.1f,%.0f,%.0f,%.1f,%s\n", ts, (dt>0?100*(dt-di)/dt:0), (tot-av)/1024, tot/1024, 100*(tot-av)/tot, l}
  ' /proc/meminfo >> "$OUT"
  pt=$t; pi=$i
done