#!/usr/bin/env bash
# Start/stop samplers on web VM, db VM (via ssh) and the local load-generator VM.
# usage: WEB_HOST=user@ip DB_HOST=user@ip monitoring/monitor_ctl.sh start|stop <run_id>
# optional: SSH_OPTS="-i ~/.ssh/key"
# Output (all inside results/<run_id>/): <run_id>_web.csv, _db.csv, _load.csv, and _docker.csv for docker runs.
set -u
cmd=${1:?start|stop}; id=${2:?run_id}
cd "$(dirname "$0")/.."
: "${WEB_HOST:?set WEB_HOST}" "${DB_HOST:?set DB_HOST}"
out=results/$id; rd=/tmp/mon_$id
sshc() { ssh -o BatchMode=yes -o ConnectTimeout=5 ${SSH_OPTS:-} "$@"; }
scpc() { scp -q -o BatchMode=yes -o ConnectTimeout=5 ${SSH_OPTS:-} "$@"; }
declare -A HOSTS=([web]=$WEB_HOST [db]=$DB_HOST)
rc=0
case $cmd in
start)
  mkdir -p "$out"
  for role in web db; do
    sshc "${HOSTS[$role]}" "mkdir -p $rd; cat > $rd/collect.sh; chmod +x $rd/collect.sh; \
      nohup setsid $rd/collect.sh $rd/${id}_$role.csv </dev/null >/dev/null 2>&1 & echo \$! > $rd/$role.pid" \
      < monitoring/collect.sh || { echo "monitor: failed to start on $role" >&2; rc=1; }
  done
  if [[ $id == docker_* ]]; then
    sshc "$WEB_HOST" "cat > $rd/collect_docker.sh; chmod +x $rd/collect_docker.sh; \
      nohup setsid $rd/collect_docker.sh $rd/${id}_docker.csv </dev/null >/dev/null 2>&1 & echo \$! > $rd/docker.pid" \
      < monitoring/collect_docker.sh || { echo "monitor: docker stats not started" >&2; }
  fi
  nohup setsid monitoring/collect.sh "$out/${id}_load.csv" </dev/null >/dev/null 2>&1 &
  echo $! > "$out/.mon_load.pid"
  sleep 2   # let every sampler write a first row before k6 starts
  ;;
stop)
  [ -f "$out/.mon_load.pid" ] && kill "$(cat "$out/.mon_load.pid")" 2>/dev/null; rm -f "$out/.mon_load.pid"
  for role in web db docker; do
    host=${HOSTS[$role]:-$WEB_HOST}
    sshc "$host" "[ -f $rd/$role.pid ] && kill \$(cat $rd/$role.pid)" 2>/dev/null || continue
    sleep 1
    scpc "$host:$rd/${id}_$role.csv" "$out/" || { echo "monitor: could not fetch $role csv" >&2; rc=1; }
  done
  for host in "$WEB_HOST" "$DB_HOST"; do sshc "$host" "rm -rf $rd" 2>/dev/null; done
  ;;
*) echo "usage: $0 start|stop <run_id>"; exit 1;;
esac
exit $rc
