param(
    [ValidateSet("KOSPI", "KOSDAQ")]
    [string]$Market = "KOSPI",
    [int]$Days = 420,
    [double]$Sleep = 0.15,
    [switch]$SkipFundamentals
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendRoot = Join-Path $projectRoot "backend"
$python = Join-Path $backendRoot ".venv\Scripts\python.exe"
$logDirectory = Join-Path $backendRoot "logs"
$lockFile = Join-Path $logDirectory "market-refresh.lock"
$logFile = Join-Path $logDirectory ("market-refresh-{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

if (-not (Test-Path $python)) {
    throw "Python virtual environment not found: $python"
}

New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
if (Test-Path $lockFile) {
    throw "A market refresh is already running. Remove $lockFile only after checking the running task."
}

New-Item -ItemType File -Path $lockFile -Force | Out-Null
try {
    $arguments = @("manage.py", "refresh_market_data", "--market", $Market, "--days", $Days, "--sleep", $Sleep, "--skip-fundamentals")

    "[{0}] Starting market refresh" -f (Get-Date -Format "s") | Tee-Object -FilePath $logFile -Append
    & $python @arguments 2>&1 | Tee-Object -FilePath $logFile -Append
    if ($LASTEXITCODE -ne 0) {
        throw "refresh_market_data failed with exit code $LASTEXITCODE"
    }
    "[{0}] Market refresh completed" -f (Get-Date -Format "s") | Tee-Object -FilePath $logFile -Append
}
finally {
    Remove-Item -LiteralPath $lockFile -Force -ErrorAction SilentlyContinue
}
