#!/usr/bin/env bash
set -uo pipefail

# Search every topological placement of five ordinary gates and six Switches
# in the exact D5 S5/S6/S7/C8 residual.  The five ordinary kinds remain free,
# so the 462 position patterns cover the complete no-XOR g17/o5/s6 class.
# A watchdog or missing result is UNKNOWN and is never promoted to UNSAT.

ROOT=${ROOT:-/root/congProjects/turing-complete-works}
WORKER=${WORKER:-$ROOT/.research/byte_adder_phase_shortcut_restart/physical_exact.py}
PYTHON=${PYTHON:-$ROOT/.venv/bin/python}
OUT=${OUT:-$ROOT/.research/byte_adder_root/g17_o5s6_position_sweep_20260804}
MAX_JOBS=${MAX_JOBS:-12}
WATCHDOG=${WATCHDOG:-180}
AS_KIB=${AS_KIB:-1310720}
NICE=${NICE:-5}

mkdir -p "$OUT/results" "$OUT/logs" "$OUT/runs"
touch "$OUT/progress.tsv"

fixed_kinds() {
  local positions=",$1," i token result=""
  for i in $(seq 0 10); do
    token=SWITCH
    if [[ $positions == *",${i},"* ]]; then
      token='*'
    fi
    if [[ -n $result ]]; then result+=,; fi
    result+=$token
  done
  printf '%s\n' "$result"
}

run_one() {
  local positions=$1
  local key="o${positions//,/_}"
  local result="$OUT/results/${key}.json"
  local log="$OUT/logs/${key}.log"
  local run="$OUT/runs/${key}.run.json"
  local fixed start end rc class status

  if [[ -f $run || -f $OUT/SAT_FOUND ]]; then
    return 0
  fi

  fixed=$(fixed_kinds "$positions")
  start=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  (
    ulimit -v "$AS_KIB"
    timeout --signal=TERM --kill-after=30s "${WATCHDOG}s" \
      nice -n "$NICE" "$PYTHON" "$WORKER" \
        --domain s34567c8_leaf \
        --outputs S5,S6,S7,C8 \
        --gate-bound 17 --max-delay 5 \
        --components 11 --switches 6 --xors 0 \
        --fixed-kinds "$fixed" \
        --split-slots 1 --shard-count 1 --shard-index 0 \
        --solver cadical195 --timeout 0 \
        --output "$result"
  ) > "$log" 2>&1
  rc=$?

  end=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  class=solver_exit
  if [[ $rc -eq 124 || $rc -eq 137 ]]; then class=watchdog_timeout; fi
  status=missing
  if [[ -f $result ]]; then
    status=$(
      "$PYTHON" - "$result" <<'PY'
import json
import sys

try:
    value = json.load(open(sys.argv[1], encoding="utf-8")).get("status", "missing")
except Exception:
    value = "invalid_json"
print(value)
PY
    )
  fi

  printf '{"start_utc":"%s","end_utc":"%s","exit_code":%s,"classification":"%s","status":"%s","ordinary_positions":[%s],"fixed_kinds":"%s","watchdog_seconds":%s,"as_limit_kib":%s,"nice":%s}\n' \
    "$start" "$end" "$rc" "$class" "$status" "$positions" \
    "$fixed" "$WATCHDOG" "$AS_KIB" "$NICE" > "$run.tmp"
  mv "$run.tmp" "$run"
  printf '%s\t%s\t%s\t%s\n' "$key" "$status" "$rc" "$class" >> "$OUT/progress.tsv"

  if [[ $status == sat ]]; then
    printf '%s\n' "$key" > "$OUT/SAT_FOUND.tmp"
    mv "$OUT/SAT_FOUND.tmp" "$OUT/SAT_FOUND"
  fi
}

mapfile -t PATTERNS < <(
  "$PYTHON" - <<'PY'
import hashlib
import itertools


def priority(ordinary: tuple[int, ...]) -> tuple[object, ...]:
    pattern = "".join("O" if index in ordinary else "S" for index in range(11))
    transitions = sum(a != b for a, b in zip(pattern, pattern[1:]))
    bus_then_gate = any(
        pattern[index:index + 2] == "SS" and "O" in pattern[index + 2:]
        for index in range(10)
    )
    gate_then_bus = any(
        pattern[index:index + 2] == "OO" and "S" in pattern[index + 2:]
        for index in range(10)
    )
    early_balance = abs(pattern[:4].count("O") - 2)
    digest = hashlib.sha256(pattern.encode("ascii")).hexdigest()
    return (not (bus_then_gate and gate_then_bus), abs(transitions - 5), early_balance, digest)


patterns = sorted(itertools.combinations(range(11), 5), key=priority)
for positions in patterns:
    print(",".join(map(str, positions)))
PY
)

{
  printf 'schema=g17-o5s6-position-sweep-v1\n'
  printf 'ordinary_position_patterns=%s\n' "${#PATTERNS[@]}"
  printf 'complete_no_xor_topology_class=true\n'
  printf 'gate=17\ndelay=5\ncomponents=11\nordinary=5\nswitches=6\nxors=0\n'
  printf 'max_jobs=%s\nwatchdog=%s\nas_kib=%s\nnice=%s\n' \
    "$MAX_JOBS" "$WATCHDOG" "$AS_KIB" "$NICE"
  printf 'worker_sha256=%s\n' "$(sha256sum "$WORKER" | cut -d' ' -f1)"
  printf 'launcher_sha256=%s\n' "$(sha256sum "$0" | cut -d' ' -f1)"
} > "$OUT/sweep.meta"

running=0
for positions in "${PATTERNS[@]}"; do
  if [[ -f $OUT/SAT_FOUND ]]; then break; fi
  key="o${positions//,/_}"
  if [[ -f $OUT/runs/${key}.run.json ]]; then continue; fi
  run_one "$positions" &
  running=$((running + 1))
  if [[ $running -ge $MAX_JOBS ]]; then
    wait -n || true
    running=$((running - 1))
  fi
done

while [[ $running -gt 0 ]]; do
  wait -n || true
  running=$((running - 1))
done

"$PYTHON" - "$OUT" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
records = []
for path in sorted((root / "runs").glob("*.run.json")):
    row = json.loads(path.read_text(encoding="utf-8"))
    stem = path.name.removesuffix(".run.json")
    result = root / "results" / f"{stem}.json"
    log = root / "logs" / f"{stem}.log"
    row["run"] = str(path)
    for label, artifact in (("result", result), ("log", log)):
        row[label] = str(artifact)
        row[label + "_sha256"] = (
            hashlib.sha256(artifact.read_bytes()).hexdigest()
            if artifact.is_file()
            else None
        )
    records.append(row)

statuses = sorted({str(row.get("status")) for row in records})
summary = {
    "schema": "g17-o5s6-position-sweep-summary-v1",
    "expected_position_patterns": 462,
    "completed_position_patterns": len(records),
    "status_counts": {
        status: sum(row.get("status") == status for row in records)
        for status in statuses
    },
    "sat_found": [
        row["ordinary_positions"] for row in records if row.get("status") == "sat"
    ],
    "unknown_is_not_unsat": True,
    "records": records,
}
(root / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
    newline="\n",
)
print(json.dumps({
    key: summary[key]
    for key in ("completed_position_patterns", "status_counts", "sat_found")
}))
PY
