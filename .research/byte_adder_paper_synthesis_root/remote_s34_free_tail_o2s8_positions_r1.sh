#!/usr/bin/env bash
set -euo pipefail

ROOT=/root/congProjects/turing-complete-works
cd "$ROOT"

PREVIOUS=.research/byte_adder_paper_synthesis_root/remote-sweeps/s34_free_tail_terminal_priority_20260804_r1
OUT=.research/byte_adder_paper_synthesis_root/remote-sweeps/s34_free_tail_o2s8_positions_20260804_r1
RUNNER=.research/byte_adder_paper_synthesis_root/run_s34_free_tail_o2s8_positions.py

mkdir -p "$OUT"

# Do not add six more workers while the terminal-priority batch still owns its
# six slots.  suffix16 may continue in parallel; its measured footprint plus
# this batch stays below the observed safe memory envelope.
if [[ -f "$PREVIOUS/launcher.pid" ]]; then
    previous_pid=$(cat "$PREVIOUS/launcher.pid")
    if kill -0 "$previous_pid" 2>/dev/null; then
        printf 'waiting for terminal-priority PID %s\n' "$previous_pid"
        tail --pid="$previous_pid" -f /dev/null
    fi
fi

printf 'starting o2/s8 position sweep at %s\n' "$(date --iso-8601=seconds)"
exec .venv/bin/python "$RUNNER" \
    --out "$OUT" \
    --workers 6 \
    --wall-timeout 900 \
    --address-space 1610612736 \
    --nice 10 \
    --solver cadical195
