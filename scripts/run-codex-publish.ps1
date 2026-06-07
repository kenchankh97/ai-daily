param(
    [string]$Date = "today",
    [int]$MaxAttempts = 6,
    [int]$RetryDelayMinutes = 3,
    [string]$SourceRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$EnvFile = (Join-Path $env:USERPROFILE ".ken-ai-daily\.env.local")
)

$ErrorActionPreference = "Stop"

function Resolve-RunDateId {
    param([string]$RawDate)
    if ($RawDate -eq "today") {
        $Tz = [System.TimeZoneInfo]::FindSystemTimeZoneById("China Standard Time")
        return [System.TimeZoneInfo]::ConvertTime([DateTimeOffset]::UtcNow, $Tz).ToString("yyyyMMdd")
    }
    if ($RawDate -match '^\d{8}$') {
        return $RawDate
    }
    return ([DateTime]::Parse($RawDate)).ToString("yyyyMMdd")
}

$DateId = Resolve-RunDateId -RawDate $Date
$IssueDate = [DateTime]::ParseExact($DateId, "yyyyMMdd", $null).ToString("yyyy-MM-dd")
$Title = "Ken AI Daily $IssueDate"
$BaseDir = if ($env:KEN_AI_DAILY_HOME) { $env:KEN_AI_DAILY_HOME } else { Join-Path $env:USERPROFILE ".ken-ai-daily" }
$LogsDir = Join-Path $BaseDir "logs\codex-publish"
$Checkout = Join-Path $BaseDir "work\codex-publish-$DateId"
$StatePath = Join-Path $SourceRoot ".publish-state.json"

New-Item -ItemType Directory -Force -Path $LogsDir, (Split-Path $Checkout -Parent) | Out-Null

$LastExit = 1
for ($Attempt = 1; $Attempt -le $MaxAttempts; $Attempt++) {
    $Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $LogFile = Join-Path $LogsDir "publish-$DateId-attempt$Attempt-$Stamp.log"
    Write-Host "Starting Codex publish attempt $Attempt/$MaxAttempts for $DateId."

    & python (Join-Path $SourceRoot "scripts\publish_prepared_fresh_clone.py") `
        --date $DateId `
        --source-root $SourceRoot `
        --env-file $EnvFile `
        --title $Title `
        --checkout $Checkout *>&1 |
        Tee-Object -FilePath $LogFile
    $LastExit = $LASTEXITCODE

    if (Test-Path $StatePath) {
        $State = Get-Content $StatePath -Raw | ConvertFrom-Json
        if ($State.status -eq "completed") {
            Write-Host "Codex publish finished with status completed."
            exit 0
        }
        if ($State.linkedin.share_urn) {
            Write-Host "LinkedIn share already exists in state; next attempt will validate without reposting."
        }
    }

    if ($LastExit -eq 0) {
        exit 0
    }
    if ($Attempt -lt $MaxAttempts) {
        Write-Host "Attempt $Attempt failed; retrying in $RetryDelayMinutes minutes."
        Start-Sleep -Seconds ($RetryDelayMinutes * 60)
    }
}

exit $LastExit
