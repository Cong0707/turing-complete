#!/usr/bin/env bash
set -uo pipefail

# Exhaust the remaining topological placements of the two ordinary components
# in the exact g18/o2s8 S5,S6,S7,C8 residual.  Existing audited placements are
# skipped explicitly.  Each job is fail-closed behind an external watchdog;
# timeout or a missing canonical JSON is UNKNOWN, never UNSAT.

ROOT=${ROOT:-/root/congProjects/turing-complete-works}
WORKER=${WORKER:-$ROOT/.research/byte_adder_phase_shortcut_restart/physical_exact.py}
PYTHON=${PYTHON:-$ROOT/.venv/bin/python}
OUT=${OUT:-$ROOT/.research/byte_adder_root/o2s8_position_sweep_20260804}
MAX_JOBS=${MAX_JOBS:-4}
WATCHDOG=${WATCHDOG:-900}
AS_KIB=${AS_KIB:-6291456}
NICE=${NICE:-5}

mkdir -p "$OUT/results" "$OUT/logs" "$OUT/runs"
touch "$OUT/progress.tsv"

declare -A SKIP=(
  [0,1]=1
  [2,3]=1
  [2,4]=1
  [3,4]=1
  [3,5]=1
  [4,5]=1
  [4,6]=1
  [5,6]=1
  [5,7]=1
  [6,7]=1
)

fixed_kinds() {
  local first=$1 second=$2 i token result=""
  for i in $(seq 0 9); do
    token=SWITCH
    if [[ $i -eq $first || $i -eq $second ]]; then
      token='*'
    fi
    if [[ -n $result ]]; then result+=,; fi
    result+=$token
  done
  printf '%s\n' "$result"
}

run_one() {
  local first=$1 second=$2
  local key="p${first}_${second}"
  local result="$OUT/results/${key}.json"
  local log="$OUT/logs/${key}.log"
  local run="$OUT/runs/${key}.run.json"
  local fixed start end rc class status
  fixed=$(fixed_kinds "$first" "$second")
  start=$(date -u +%Y-%m-%dT%H:%M:%SZ)

  set +e
  (
    ulimit -v "$AS_KIB"
    timeout --signal=TERM --kill-after=60s "${WATCHDOG}s" \
      nice -n "$NICE" "$PYTHON" "$WORKER" \
        --domain s34567c8_leaf \
        --outputs S5,S6,S7,C8 \
        --gate-bound 18 --max-delay 5 \
        --components 10 --switches 8 --xors 0 \
        --fixed-kinds "$fixed" \
        --split-slots 1 --shard-count 1 --shard-index 0 \
        --solver cadical195 --timeout 0 \
        --output "$result"
  ) > "$log" 2>&1
  rc=$?
  set -e

  end=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  class=solver_exit
  if [[ $rc -eq 124 || $rc -eq 137 ]]; then class=watchdog_timeout; fi
  status=missing
  if [[ -f $result ]]; then
    status=$(
      "$PYTHON" - "$result" <<'PY'
import json, sys
try:
    value = json.load(open(sys.argv[1], encoding="utf-8")).get("status", "missing")
except Exception:
    value = "invalid_json"
print(value)
PY
    )
  fi
  printf '{"start_utc":"%s","end_utc":"%s","exit_code":%s,"classification":"%s","status":"%s","ordinary_positions":[%s,%s],"fixed_kinds":"%s","watchdog_seconds":%s,"as_limit_kib":%s,"nice":%s}\n' \
    "$start" "$end" "$rc" "$class" "$status" "$first" "$second" \
    "$fixed" "$WATCHDOG" "$AS_KIB" "$NICE" > "$run.tmp"
  mv "$run.tmp" "$run"
  printf '%s\t%s\t%s\t%s\n' "$key" "$status" "$rc" "$class" >> "$OUT/progress.tsv"
  if [[ $status == sat ]]; then
    printf '%s\n' "$key" > "$OUT/SAT_FOUND.tmp"
    mv "$OUT/SAT_FOUND.tmp" "$OUT/SAT_FOUND"
  fi
}

declare -a PAIRS=()
for first in $(seq 0 8); do
  for second in $(seq $((first + 1)) 9); do
    pair="$first,$second"
    if [[ -z ${SKIP[$pair]+x} ]]; then
      PAIRS+=("$first $second")
    fi
  done
done

printf 'ordinary_position_pairs=%s\n' "${#PAIRS[@]}" > "$OUT/sweep.meta"
printf 'max_jobs=%s\nwatchdog=%s\nas_kib=%s\nnice=%s\n' \
  "$MAX_JOBS" "$WATCHDOG" "$AS_KIB" "$NICE" >> "$OUT/sweep.meta"

running=0
for pair in "${PAIRS[@]}"; do
  if [[ -f $OUT/SAT_FOUND ]]; then break; fi
  read -r first second <<< "$pair"
  key="p${first}_${second}"
  if [[ -f $OUT/runs/${key}.run.json ]]; then continue; fi
  run_one "$first" "$second" &
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
import hashlib, json, pathlib, sys

root = pathlib.Path(sys.argv[1])
records = []
for path in sorted((root / "runs").glob("*.run.json")):
    row = json.loads(path.read_text(encoding="utf-8"))
    row["run"] = str(path)
    result = root / "results" / (path.name.removesuffix(".run.json") + ".json")
    log = root / "logs" / (path.name.removesuffix(".run.json") + ".log")
    for label, artifact in (("result", result), ("log", log)):
        row[label] = str(artifact)
        row[label + "_sha256"] = (
            hashlib.sha256(artifact.read_bytes()).hexdigest() if artifact.is_file() else None
        )
    records.append(row)
summary = {
    "schema": "byte-adder-s567c8-g18-o2s8-position-sweep-v1",
    "expected_new_pairs": 35,
    "completed_pairs": len(records),
    "status_counts": {
        status: sum(row.get("status") == status for row in records)
        for status in sorted({str(row.get("status")) for row in records})
    },
    "sat_found": [row["ordinary_positions"] for row in records if row.get("status") == "sat"],
    "records": records,
}
(root / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
)
print(json.dumps({k: summary[k] for k in ("completed_pairs", "status_counts", "sat_found")}))
PY
