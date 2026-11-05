#!/usr/bin/env bash
# Per-container stats (supplementary only; each sample takes ~1-2 s, so it is coarser than collect.sh).
# usage: collect_docker.sh <out.csv>
OUT=${1:?out.csv}
echo "ts_epoch,container,cpu_pct,mem_usage" > "$OUT"
trap 'exit 0' TERM INT
while true; do
  ts=$(date +%s.%N)
  docker stats --no-stream --format '{{.Name}},{{.CPUPerc}},"{{.MemUsage}}"' | sed "s/^/$ts,/" >> "$OUT"
done
