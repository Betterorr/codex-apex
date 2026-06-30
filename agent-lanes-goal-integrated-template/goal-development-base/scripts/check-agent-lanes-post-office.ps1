$ErrorActionPreference = "Stop"

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$Script = Join-Path $Root "agent-lanes\scripts\check_callback_post_office.py"

if (-not (Test-Path -LiteralPath $Script)) {
  Write-Host "Missing callback post office checker: $Script"
  exit 1
}

$ArgsList = @("--project-root", $Root)

if ($env:AGENT_LANES_POST_OFFICE_SINCE) {
  $ArgsList += @("--since", $env:AGENT_LANES_POST_OFFICE_SINCE)
}

if ($env:AGENT_LANES_PENDING_MAX_AGE_MINUTES) {
  $ArgsList += @("--pending-max-age-minutes", $env:AGENT_LANES_PENDING_MAX_AGE_MINUTES)
}

if ($env:AGENT_LANES_POST_OFFICE_STRICT -eq "1") {
  $ArgsList += "--strict"
}

if ($env:AGENT_LANES_POST_OFFICE_STRICT_DIRECT_BYPASS -eq "1") {
  $ArgsList += "--strict-direct-bypass"
}

python $Script @ArgsList
