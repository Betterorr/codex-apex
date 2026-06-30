$ErrorActionPreference = "Stop"

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$SkillRoot = Join-Path $Root ".agents\skills"
$ValidatorCandidates = @(
  (Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\scripts\quick_validate.py"),
  (Join-Path $env:USERPROFILE ".codex\skills\.system\skill-creator\quick_validate.py"),
  "C:\Users\Administrator\.codex\skills\.system\skill-creator\scripts\quick_validate.py",
  "C:\Users\RAY\.codex\skills\.system\skill-creator\scripts\quick_validate.py"
)
$Validator = $ValidatorCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not (Test-Path -LiteralPath $SkillRoot)) {
  Write-Host "Skill directory not found: $SkillRoot"
  exit 1
}

if (-not $Validator) {
  Write-Host "Validator not found. Checked:"
  $ValidatorCandidates | ForEach-Object { Write-Host "  $_" }
  exit 1
}

$env:PYTHONUTF8 = "1"

Get-ChildItem -LiteralPath $SkillRoot -Directory | ForEach-Object {
  Write-Host "Validating $($_.Name)..."
  python $Validator $_.FullName
}

Write-Host "Local skill validation complete."
