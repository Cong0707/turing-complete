[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^(single_k\d+|multi_d[23]_k\d+)$')]
    [string]$C5Shard,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 3)]
    [int]$T5Drivers,

    [Parameter(Mandatory = $true)]
    [ValidateRange(1, 3)]
    [int]$S5Drivers,

    [string]$RemoteHost = 'root@new.xem8k5.top',
    [int]$PollSeconds = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$GateBound = 16
$Components = 13
$Solver = 'cadical195'
$InternalTimeout = 0
$WatchdogSeconds = 21600
$AsLimitKiB = 4194304
$Nice = 10
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $Here '..\..')).Path
$Python = Join-Path $RepoRoot '.venv\Scripts\python.exe'
$Results = Join-Path $Here 'results'
$RemoteRoot = '/root/congProjects/turing-complete-works/.research/byte_adder_cross_boundary_joint_restart'
$Stem = "g${GateBound}_n${Components}_c5_${C5Shard}_t${T5Drivers}_s${S5Drivers}"
$ArtifactName = "$Stem.json"
$RunName = "$Stem.run.json"
$LauncherName = "$Stem.launcher.log"
$AuditName = "bit35_joint_${Stem}_terminal_audit.json"
$ArtifactPath = Join-Path $Results $ArtifactName
$RunPath = Join-Path $Results $RunName
$LauncherPath = Join-Path $Results $LauncherName
$AuditPath = Join-Path $Here $AuditName

function Invoke-RemoteScript {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Script,

        [Parameter(Mandatory = $true)]
        [string]$Context
    )

    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Script))
    $command = "printf '%s' '$encoded' | base64 -d | bash"
    $output = @(& ssh -o BatchMode=yes -o ConnectTimeout=15 $RemoteHost $command)
    if ($LASTEXITCODE -ne 0) {
        throw "$Context failed with exit ${LASTEXITCODE}: $($output -join ' ')"
    }
    return $output
}

if ($PollSeconds -lt 1) {
    throw 'PollSeconds must be positive'
}
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "project Python is absent: $Python"
}

foreach ($path in @($ArtifactPath, $RunPath, $LauncherPath, $AuditPath)) {
    if (Test-Path -LiteralPath $path) {
        throw "local canonical output already exists: $path"
    }
    if (Test-Path -LiteralPath ($path + '.tmp')) {
        throw "local temporary output already exists: $path.tmp"
    }
}

$launchTemplate = @'
set -eu
cd __REMOTE_ROOT__
stem=__STEM__

check_hash() {
  path=$1
  expected=$2
  actual=$(sha256sum "$path" | awk '{print $1}')
  if [ "$actual" != "$expected" ]; then
    printf 'GUARD_FAIL hash path=%s actual=%s expected=%s\n' "$path" "$actual" "$expected" >&2
    exit 22
  fi
}

check_hash exact_bit35_joint_phase_driver_shard.py a64634e6c160114b8bdb06c893a8e26e4f8c9c6e9eb208ca410fe538313f770d
check_hash bit35_joint_c5_normal_form.py 583036983d44c9f90bb1d8fbd694f34b3de8932e6a722511a2f88b0ff3a63c83
check_hash bit35_joint_phase_driver_classes.py babbf4bb118cbcda9638f2d76cd3082a996a15c7225dd5ef49f12ae8be25a3d9
check_hash exact_bit35_joint_c5_normal_form_shard.py 949b0e922710db86afa3a7f7881da47005319db147bf2be77b0527e0d0c97276
check_hash exact_bit35_joint_sat.py 83e3d79130ce2f8844041ad2d1b55363a8a00297836c81b98eab69e607c75aef
check_hash ../byte_adder_pair_macro_exact/exact_paid_physical_search_core.py 5cfd8d5121620393201f51a3db0f7328229253502cf6831ce32f8ea935b5108a
check_hash ../byte_adder_pair_macro_exact/exact_paid_physical_core.py 9c671db251d1070b647094833c616501f72f6f6b542b6da35f0856b4f0c29dd6
check_hash ../byte_adder_pair_macro_exact/exact_paid_physical_cnf.py a565201bf7e99f6ded6732e70d883cd9a90e5da2e42d72171f11952bb3566ca4

test -x /root/congProjects/turing-complete-works/.venv/bin/python
/root/congProjects/turing-complete-works/.venv/bin/python -c 'import pysat' >/dev/null

for path in \
  "results/${stem}.json" \
  "results/${stem}.json.tmp" \
  "results/${stem}.run.json" \
  "results/${stem}.run.json.tmp" \
  "results/${stem}.launcher.log" \
  "results/${stem}.launcher.log.tmp"
do
  if [ -e "$path" ]; then
    printf 'GUARD_FAIL existing=%s\n' "$path" >&2
    exit 20
  fi
done

worker_count=$(ps -eo comm=,args= | awk '$1 ~ /^python/ && $0 ~ /exact_bit35_joint_phase_driver_shard[.]py/ {n++} END {print n+0}')
if [ "$worker_count" -ne 0 ]; then
  printf 'GUARD_FAIL worker_count=%s\n' "$worker_count" >&2
  exit 21
fi

nohup bash -s >/dev/null 2>&1 <<'WORKER_WRAPPER' &
set +e
cd __REMOTE_ROOT__
stem=__STEM__
start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
pid=$$
ulimit -v __AS_LIMIT__
nice -n __NICE__ timeout --signal=TERM --kill-after=30s __WATCHDOG__s \
  /root/congProjects/turing-complete-works/.venv/bin/python \
  exact_bit35_joint_phase_driver_shard.py \
  --gate-bound __GATE_BOUND__ \
  --components __COMPONENTS__ \
  --c5-shard __C5_SHARD__ \
  --t5-drivers __T5_DRIVERS__ \
  --s5-drivers __S5_DRIVERS__ \
  --solver __SOLVER__ \
  --timeout __INTERNAL_TIMEOUT__ \
  --output "results/${stem}.json" \
  > "results/${stem}.launcher.log" 2>&1
rc=$?
end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
case "$rc" in
  0|2) classification=solver_exit ;;
  124|137) classification=watchdog_timeout ;;
  *) classification=wrapper_error ;;
esac
printf '{"start_utc":"%s","end_utc":"%s","pid":%s,"exit_code":%s,"classification":"%s","watchdog_seconds":__WATCHDOG__,"as_limit_kib":__AS_LIMIT__,"nice":__NICE__}\n' \
  "$start_utc" "$end_utc" "$pid" "$rc" "$classification" \
  > "results/${stem}.run.json.tmp"
mv -f "results/${stem}.run.json.tmp" "results/${stem}.run.json"
WORKER_WRAPPER

printf 'LAUNCHED stem=%s wrapper_pid=%s pre_worker_count=%s\n' "$stem" "$!" "$worker_count"
'@

$replacements = [ordered]@{
    '__REMOTE_ROOT__' = $RemoteRoot
    '__STEM__' = $Stem
    '__AS_LIMIT__' = [string]$AsLimitKiB
    '__NICE__' = [string]$Nice
    '__WATCHDOG__' = [string]$WatchdogSeconds
    '__GATE_BOUND__' = [string]$GateBound
    '__COMPONENTS__' = [string]$Components
    '__C5_SHARD__' = $C5Shard
    '__T5_DRIVERS__' = [string]$T5Drivers
    '__S5_DRIVERS__' = [string]$S5Drivers
    '__SOLVER__' = $Solver
    '__INTERNAL_TIMEOUT__' = [string]$InternalTimeout
}
$remoteLaunch = $launchTemplate
foreach ($entry in $replacements.GetEnumerator()) {
    $remoteLaunch = $remoteLaunch.Replace($entry.Key, $entry.Value)
}
$remoteLaunch += "`n"

$launchOutput = @(Invoke-RemoteScript -Script $remoteLaunch -Context 'remote launch')
if ($launchOutput.Count -ne 1 -or $launchOutput[0] -notmatch "^LAUNCHED stem=$([regex]::Escape($Stem)) ") {
    throw "unexpected remote launch response: $($launchOutput -join ' ')"
}

$pollTemplate = @'
set -eu
cd __REMOTE_ROOT__
stem=__STEM__
if [ -f "results/${stem}.run.json" ]; then
  printf 'terminal\n'
  exit 0
fi
worker_count=$(ps -eo comm=,args= | awk '$1 ~ /^python/ && $0 ~ /exact_bit35_joint_phase_driver_shard[.]py/ {n++} END {print n+0}')
if [ "$worker_count" -gt 1 ]; then
  printf 'invalid_worker_count:%s\n' "$worker_count"
  exit 23
fi
if [ -f "results/${stem}.launcher.log" ]; then
  printf 'running:%s\n' "$worker_count"
else
  printf 'missing:%s\n' "$worker_count"
  exit 24
fi
'@
$remotePoll = $pollTemplate.Replace('__REMOTE_ROOT__', $RemoteRoot).Replace('__STEM__', $Stem) + "`n"

Start-Sleep -Seconds 1
while ($true) {
    $pollOutput = @(Invoke-RemoteScript -Script $remotePoll -Context 'remote poll')
    if ($pollOutput.Count -ne 1) {
        throw "unexpected remote poll response: $($pollOutput -join ' ')"
    }
    if ($pollOutput[0] -eq 'terminal') {
        break
    }
    if ($pollOutput[0] -notmatch '^running:[01]$') {
        throw "invalid remote state: $($pollOutput[0])"
    }
    Start-Sleep -Seconds $PollSeconds
}

$hashTemplate = @'
set -eu
cd __REMOTE_ROOT__
stem=__STEM__
test -f "results/${stem}.run.json"
test -f "results/${stem}.launcher.log"
for path in "results/${stem}.json" "results/${stem}.run.json" "results/${stem}.launcher.log"; do
  if [ -f "$path" ]; then
    sha256sum "$path"
  fi
done
'@
$remoteHash = $hashTemplate.Replace('__REMOTE_ROOT__', $RemoteRoot).Replace('__STEM__', $Stem) + "`n"
$hashOutput = @(Invoke-RemoteScript -Script $remoteHash -Context 'remote terminal hash collection')

$remoteHashes = @{}
foreach ($line in $hashOutput) {
    if ($line -notmatch '^([0-9a-f]{64})\s+(.+)$') {
        throw "invalid remote sha256sum line: $line"
    }
    $name = ($Matches[2] -split '/')[-1]
    $remoteHashes[$name] = $Matches[1]
}
foreach ($required in @($RunName, $LauncherName)) {
    if (-not $remoteHashes.ContainsKey($required)) {
        throw "remote terminal evidence is absent: $required"
    }
}

foreach ($name in @($ArtifactName, $RunName, $LauncherName)) {
    if (-not $remoteHashes.ContainsKey($name)) {
        continue
    }
    & scp -q "${RemoteHost}:${RemoteRoot}/results/$name" $Results
    if ($LASTEXITCODE -ne 0) {
        throw "scp failed for $name with exit $LASTEXITCODE"
    }
    $localPath = Join-Path $Results $name
    $localHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $localPath).Hash.ToLowerInvariant()
    if ($localHash -ne $remoteHashes[$name]) {
        throw "transport hash mismatch for ${name}: local=$localHash remote=$($remoteHashes[$name])"
    }
}

$auditArgs = @(
    (Join-Path $Here 'audit_bit35_joint_phase_driver_result.py'),
    '--artifact', $ArtifactPath,
    '--run-record', $RunPath,
    '--output', $AuditPath,
    '--gate-bound', [string]$GateBound,
    '--components', [string]$Components,
    '--c5-shard', $C5Shard,
    '--t5-drivers', [string]$T5Drivers,
    '--s5-drivers', [string]$S5Drivers,
    '--solver', $Solver,
    '--internal-timeout', [string]$InternalTimeout,
    '--watchdog-seconds', [string]$WatchdogSeconds,
    '--as-limit-kib', [string]$AsLimitKiB,
    '--nice', [string]$Nice
)
& $Python @auditArgs | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "terminal audit failed with exit $LASTEXITCODE; inspect $AuditPath"
}

$audit = Get-Content -Raw -LiteralPath $AuditPath | ConvertFrom-Json
if ($audit.status -ne 'pass' -or @($audit.errors).Count -ne 0) {
    throw "terminal audit did not pass: $AuditPath"
}
$artifactStatus = if (Test-Path -LiteralPath $ArtifactPath) {
    (Get-Content -Raw -LiteralPath $ArtifactPath | ConvertFrom-Json).status
} else {
    $null
}
$solveSeconds = if (Test-Path -LiteralPath $ArtifactPath) {
    (Get-Content -Raw -LiteralPath $ArtifactPath | ConvertFrom-Json).solve_seconds
} else {
    $null
}

[ordered]@{
    stem = $Stem
    artifact_status = $artifactStatus
    terminal_classification = $audit.terminal_classification
    audit_status = $audit.status
    solve_seconds = $solveSeconds
    remote_sha256 = $remoteHashes
    audit_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $AuditPath).Hash.ToLowerInvariant()
} | ConvertTo-Json -Depth 4
