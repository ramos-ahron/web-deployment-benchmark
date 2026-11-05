#!/usr/bin/env bash
# Start/stop/check the background samplers ON THE VM YOU ARE LOGGED INTO (no ssh between VMs needed).
# usage: monitoring/sampler.sh start <web|db|load> [docker]   (add "docker" on the web VM during docker runs)
#        monitoring/sampler.sh status <role>
#        monitoring/sampler.sh stop <role>
# Files: ~/mon_data/mon_<role>_<timestamp>.csv (and dock_<timestamp>.csv); survives logout.
set -u
cmd=${1:-}; role=${2:-}
[[ $role =~ ^(web|db|load)$ ]] || { sed -n '2,6p' "$0"; exit 1; }
here=$(cd "$(dirname "$0")" && pwd); dir=$HOME/mon_data; mkdir -p "$dir"
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
case $cmd in
start)
  alive "$dir/$role.pid" && { echo "$role sampler already running (pid $(cat "$dir/$role.pid"))"; exit 1; }
  ts=$(date -u +%Y%m%dT%H%M%S); f=$dir/mon_${role}_$ts.csv
  nohup setsid "$here/collect.sh" "$f" </dev/null >/dev/null 2>&1 &
  echo $! > "$dir/$role.pid"
  if [ "${3:-}" = docker ]; then
    nohup setsid "$here/collect_docker.sh" "$dir/dock_$ts.csv" </dev/null >/dev/null 2>&1 &
    echo $! > "$dir/${role}_docker.pid"
  fi
  sleep 3; echo "started: $f"; tail -n 2 "$f"
  echo "time now (UTC): $(date -u +%FT%TZ)   NTP synced: $(timedatectl show -p NTPSynchronized --value 2>/dev/null || echo unknown)"
  ;;
status)
  alive "$dir/$role.pid" && echo "$role sampler running (pid $(cat "$dir/$role.pid"))" || echo "$role sampler NOT running"
  f=$(ls -t "$dir"/mon_${role}_*.csv 2>/dev/null | head -1); [ -n "$f" ] && { echo "latest: $f ($(wc -l < "$f") lines)"; tail -n 1 "$f"; }
  echo "time now (UTC): $(date -u +%FT%TZ)"
  ;;
stop)
  for p in "$dir/$role.pid" "$dir/${role}_docker.pid"; do
    [ -f "$p" ] && { kill "$(cat "$p")" 2>/dev/null; rm -f "$p"; }
  done
  echo "stopped. files to copy:"; ls -l "$dir"
  ;;
*) sed -n '2,6p' "$0"; exit 1;;
esac
