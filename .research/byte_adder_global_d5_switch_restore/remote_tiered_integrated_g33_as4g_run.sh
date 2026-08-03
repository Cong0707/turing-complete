#!/usr/bin/env bash
set -uo pipefail

ROOT=/root/congProjects/turing-complete-works
RUN_DIR="$ROOT/.research/byte_adder_global_d5_switch_restore/remote-integrated-g33-mixed-tiered-as4g"
RESULT="$RUN_DIR/result.json"

mkdir -p "$RUN_DIR"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export OMP_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

date --iso-8601=seconds > "$RUN_DIR/started-at.txt"
set +e
/usr/bin/time -v -o "$RUN_DIR/time.txt" \
  timeout --signal=TERM --kill-after=30s 1800s \
  prlimit --as=4294967296 -- \
  nice -n 5 \
  "$ROOT/.venv/bin/python" \
  "$ROOT/.research/byte_adder_global_d5_switch_restore/search_phase_high_global_map.py" \
  --mode integrated-nc7 \
  --gate 33 \
  --delay 5 \
  --universe-expansion source1-residual \
  --without-new-bus2 \
  --mixed-bus2-target-profile witness-controls \
  --max-per-coverage 128 \
  --timeout-ms 600000 \
  --solver cadical195 \
  --cost-encoding producer-tiered \
  --output "$RESULT"
rc=$?
set -e

printf '%s\n' "$rc" > "$RUN_DIR/exit-code.txt"
date --iso-8601=seconds > "$RUN_DIR/finished-at.txt"
if [[ -f "$RESULT" ]]; then
  sha256sum "$RESULT" > "$RUN_DIR/result.sha256"
fi
exit "$rc"
