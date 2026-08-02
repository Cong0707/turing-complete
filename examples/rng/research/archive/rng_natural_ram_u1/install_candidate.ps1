$ErrorActionPreference = 'Stop'

$running = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -ieq 'Turing Complete.exe' -or
    ($_.ExecutablePath -and $_.ExecutablePath -like '*\Turing Complete.exe')
}
if ($running) {
    $details = $running | Select-Object ProcessId, Name, ExecutablePath | Format-Table -AutoSize | Out-String
    throw "Turing Complete is running; refusing to overwrite the save.`n$details"
}

$candidate = 'D:\Develop\Other\turing-complete\.research\rng_natural_ram_u1\candidate\circuit.data'
$destination = 'C:\Users\cong\AppData\Roaming\Turing Complete\schematics\architecture\CODEX-RNG\circuit.data'

Copy-Item -LiteralPath $candidate -Destination $destination -Force

$candidateHash = (Get-FileHash -LiteralPath $candidate -Algorithm SHA256).Hash
$destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash
if ($candidateHash -ne $destinationHash) {
    throw "Post-copy hash mismatch: candidate=$candidateHash destination=$destinationHash"
}

[pscustomobject]@{
    Candidate = $candidate
    Destination = $destination
    SHA256 = $destinationHash
    Length = (Get-Item -LiteralPath $destination).Length
    LastWriteTime = (Get-Item -LiteralPath $destination).LastWriteTime
} | Format-List
