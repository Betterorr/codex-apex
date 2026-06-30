$ErrorActionPreference = "Stop"

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$RegistryPath = Join-Path $Root "docs\capability-status.json"

if (-not (Test-Path -LiteralPath $RegistryPath)) {
  Write-Host "Missing docs/capability-status.json"
  exit 1
}

try {
  $registry = Get-Content -LiteralPath $RegistryPath -Encoding UTF8 -Raw | ConvertFrom-Json
} catch {
  Write-Host "Invalid JSON in docs/capability-status.json"
  Write-Host $_.Exception.Message
  exit 1
}

$requiredMaturity = @(
  "contract_defined",
  "dependency_available",
  "real_smoke_passed",
  "real_sample_output_saved",
  "integration_connected",
  "quality_reviewed",
  "production_ready"
)

$failures = New-Object System.Collections.Generic.List[string]

function Test-NonEmptyString($value) {
  return ($null -ne $value -and $value -is [string] -and $value.Trim().Length -gt 0)
}

function Test-PlaceholderPath($path) {
  if (-not (Test-NonEmptyString $path)) {
    return $true
  }
  return ($path -match "^replace-with" -or $path -match "<.*>" -or $path -match "^\.\.\.")
}

function Resolve-EvidencePath($root, $path) {
  if ([System.IO.Path]::IsPathRooted($path)) {
    return $path
  }
  return Join-Path $root $path
}

if ($null -eq $registry.schema_version) {
  $failures.Add("schema_version is required")
}

if ($null -eq $registry.maturity_levels) {
  $failures.Add("maturity_levels is required")
} else {
  foreach ($level in $requiredMaturity) {
    if ($registry.maturity_levels -notcontains $level) {
      $failures.Add("maturity_levels missing $level")
    }
  }
}

if ($null -eq $registry.capabilities -or $registry.capabilities.Count -eq 0) {
  $failures.Add("capabilities must contain at least one entry, even if it is a template example")
}

$allowedEvidenceStatuses = @(
  "planned",
  "present",
  "verified",
  "expired",
  "exists",
  "exists_when_generated",
  "present_when_checked",
  "dependency_available"
)

foreach ($capability in @($registry.capabilities)) {
  $id = $capability.id
  if (-not (Test-NonEmptyString $id)) {
    $failures.Add("capability id is required")
    $id = "<missing-id>"
  }

  foreach ($field in @("domain", "provider", "kind", "runtime", "maturity", "rerun_command", "next_step", "expires_when")) {
    if (-not (Test-NonEmptyString $capability.$field)) {
      $failures.Add("$id missing $field")
    }
  }

  if ($requiredMaturity -notcontains $capability.maturity) {
    $failures.Add("$id has invalid maturity: $($capability.maturity)")
  }

  if ($null -eq $capability.approval) {
    $failures.Add("$id missing approval")
  } else {
    if ($null -eq $capability.approval.required) {
      $failures.Add("$id approval.required is required")
    }
    if (-not (Test-NonEmptyString $capability.approval.status)) {
      $failures.Add("$id approval.status is required")
    }
  }

  if ($null -eq $capability.budget) {
    $failures.Add("$id missing budget")
  }

  if ($null -eq $capability.evidence -or $capability.evidence.Count -eq 0) {
    $failures.Add("$id must include at least one evidence entry")
  } else {
    foreach ($evidence in @($capability.evidence)) {
      foreach ($field in @("type", "path", "status", "summary")) {
        if (-not (Test-NonEmptyString $evidence.$field)) {
          $failures.Add("$id evidence missing $field")
        }
      }

      if (Test-NonEmptyString $evidence.status) {
        if ($allowedEvidenceStatuses -notcontains $evidence.status) {
          $failures.Add("$id evidence has unsupported status: $($evidence.status)")
        }
      }

      if ((@("present", "verified", "exists") -contains $evidence.status) -and -not (Test-PlaceholderPath $evidence.path)) {
        $resolvedEvidence = Resolve-EvidencePath $Root $evidence.path
        if (-not (Test-Path -LiteralPath $resolvedEvidence)) {
          $failures.Add("$id evidence path not found: $($evidence.path)")
        }
      }
    }
  }

  if ($null -ne $capability.variants) {
    foreach ($variant in @($capability.variants)) {
      if (-not (Test-NonEmptyString $variant.id)) {
        $failures.Add("$id variant id is required")
      }
      if ((Test-NonEmptyString $variant.maturity) -and ($requiredMaturity -notcontains $variant.maturity)) {
        $failures.Add("$id variant $($variant.id) has invalid maturity: $($variant.maturity)")
      }
    }
  }
}

if ($failures.Count -gt 0) {
  Write-Host "Capability status validation failed:"
  $failures | ForEach-Object { Write-Host "  - $_" }
  exit 1
}

Write-Host "Capability status validation passed: $($registry.capabilities.Count) capabilities checked."
