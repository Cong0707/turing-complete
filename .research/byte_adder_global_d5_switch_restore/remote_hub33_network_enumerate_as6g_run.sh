#!/usr/bin/env bash
set -uo pipefail

ROOT=/root/congProjects/turing-complete-works
WORK="$ROOT/.research/byte_adder_global_d5_switch_restore_hub33net_e0e4c3fd"
RUN_DIR="$WORK/remote-hub33-network-enumerate-as6g"
RESULT="$RUN_DIR/result.json"

mkdir -p "$RUN_DIR"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONHASHSEED=0
export OMP_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

cp "$WORK/remote_hub33_network_enumerate_as6g_run.sh" "$RUN_DIR/run.sh"
cp "$WORK/remote_hub33_network_enumerate_as6g_spec.json" "$RUN_DIR/spec.json"
{
  date --iso-8601=seconds
  hostname
  uname -a
  nproc
  free -b
  sha256sum \
    "$WORK/search_phase_high_global_map.py" \
    "$WORK/search_hub79_global_function_map.py" \
    "$WORK/hub33_high_function_library.py"
} > "$RUN_DIR/environment-before.txt"

date --iso-8601=seconds > "$RUN_DIR/started-at.txt"
set +e
/usr/bin/time -v -o "$RUN_DIR/time.txt" \
  timeout --signal=TERM --kill-after=30s 5400s \
  prlimit --as=6442450944 -- \
  nice -n 5 \
  "$ROOT/.venv/bin/python" \
  "$WORK/search_phase_high_global_map.py" \
  --mode integrated-nc7 \
  --gate 33 \
  --delay 5 \
  --universe-expansion source1-residual \
  --bus-driver-universe base \
  --mixed-bus2-target-profile hub33-network-functions \
  --max-per-coverage 128 \
  --enumerate-only \
  --solver cadical195 \
  --cost-encoding producer-tiered \
  --cardinality-encoding seqcounter \
  --output "$RESULT" \
  > "$RUN_DIR/stdout.txt" \
  2> "$RUN_DIR/stderr.txt"
rc=$?
set -e

printf '%s\n' "$rc" > "$RUN_DIR/exit-code.txt"
date --iso-8601=seconds > "$RUN_DIR/finished-at.txt"
free -b > "$RUN_DIR/memory-after.txt"
if [[ -f "$RESULT" ]]; then
  sha256sum "$RESULT" > "$RUN_DIR/result.sha256"
fi
exit "$rc"
