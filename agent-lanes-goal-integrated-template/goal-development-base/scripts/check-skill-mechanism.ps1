$ErrorActionPreference = "Stop"

$Gate = Join-Path (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")) ".codex\gates\skill-mechanism-check.ps1"

if (-not (Test-Path -LiteralPath $Gate)) {
  Write-Host "Gate script not found: $Gate"
  exit 1
}

powershell -ExecutionPolicy Bypass -File $Gate
