#!/usr/bin/env bash
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd -- "$HERE/../.." && pwd)
RESULT_DIR="$HERE/remote-all268-enumerate-k128-as6g"
mkdir -p -- "$RESULT_DIR"

awk '/MemAvailable/{print}' /proc/meminfo >"$RESULT_DIR/meminfo.before.txt"
ps -eo pid,etimes,rss,args >"$RESULT_DIR/processes.before.txt"

if pgrep -af "$HERE/search_phase_high_global_map.py" \
    >"$RESULT_DIR/branch-workers.before.txt"; then
  echo "refusing to start a second branch worker" >&2
  exit 73
fi

available_kib=$(awk '/MemAvailable/{print $2}' /proc/meminfo)
if (( available_kib < 8 * 1024 * 1024 )); then
  echo "MemAvailable below 8 GiB: ${available_kib} KiB" >&2
  exit 74
fi

export PYTHONPATH="$REPO/src"
export PYTHONHASHSEED=0
export MALLOC_ARENA_MAX=2

set +e
(
  ulimit -Sv 6291456
  exec /usr/bin/time -v \
    timeout --signal=TERM --kill-after=60s 14400s \
    nice -n 5 \
    "$REPO/.venv/bin/python" "$HERE/search_phase_high_global_map.py" \
      --mode integrated-nc7 \
      --delay 5 \
      --gate 33 \
      --universe-expansion source1-residual \
      --bus-driver-universe base \
      --mixed-bus2-target-profile all-base-bus-targets \
      --mixed-bus2-driver-profile source1-enable-base-data \
      --mixed-bus2-driver-profile source1-enable-source1-data \
      --mixed-bus2-probe-rows 1024 \
      --mixed-bus2-exact-threshold 8 \
      --max-per-coverage 128 \
      --enumerate-only \
      --progress \
      --solver cadical195 \
      --cost-encoding producer-tiered \
      --cardinality-encoding seqcounter \
      --cnf-storage streaming \
      --output "$RESULT_DIR/result.json"
) >"$RESULT_DIR/stdout.log" 2>"$RESULT_DIR/stderr.log"
status=$?
set -e

printf '%s\n' "$status" >"$RESULT_DIR/exit_code.txt"
awk '/MemAvailable/{print}' /proc/meminfo >"$RESULT_DIR/meminfo.after.txt"
ps -eo pid,etimes,rss,args >"$RESULT_DIR/processes.after.txt"
exit "$status"
