$ErrorActionPreference = "Stop"

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$Required = @(
  "AGENTS.md",
  ".agents/skills/project-orchestrator/SKILL.md",
  ".agents/skills/product-spec-builder/SKILL.md",
  ".agents/skills/design-brief-builder/SKILL.md",
  ".agents/skills/prototype-builder/SKILL.md",
  ".agents/skills/dev-planner/SKILL.md",
  ".agents/skills/goal-creator/SKILL.md",
  ".agents/skills/dev-builder/SKILL.md",
  ".agents/skills/bug-fixer/SKILL.md",
  ".agents/skills/gate-runner/SKILL.md",
  ".agents/skills/code-reviewer/SKILL.md",
  ".agents/skills/review-runner/SKILL.md",
  ".agents/skills/release-builder/SKILL.md",
  ".agents/skills/requirements-traceability-runner/SKILL.md",
  ".agents/skills/frontend-quality-runner/SKILL.md",
  ".agents/skills/open-source-research-runner/SKILL.md",
  ".agents/skills/systematic-debugging-runner/SKILL.md",
  ".agents/skills/lane-recovery-runner/SKILL.md",
  ".agents/skills/evolution-runner/SKILL.md",
  ".agents/skills/goal-methodology-guide/SKILL.md",
  ".agents/skills/goal-methodology-guide/references/GOAL-methodology-abstract.md",
  ".agents/skills/goal-methodology-guide/references/usage-playbook.md",
  "docs/00-project-state.md",
  "docs/01-product-spec.md",
  "docs/02-design-brief.md",
  "docs/03-dev-plan.md",
  "docs/04-goal-log.md",
  "docs/05-review-report.md",
  "docs/06-release-record.md",
  "docs/capability-status.json",
  ".codex/goals/goal-template.md",
  ".codex/signals/.gitkeep",
  ".codex/subagents/.gitkeep",
  ".codex/hooks/.gitkeep",
  ".codex/hooks/skill-hooks.md",
  ".codex/gates/.gitkeep",
  ".codex/gates/README.md",
  ".codex/gates/skill-mechanism-check.ps1",
  "docs/07-skill-mechanism-audit.md",
  "scripts/validate-skills.ps1",
  "scripts/check-skill-mechanism.ps1",
  "scripts/validate-capability-status.ps1"
)

$Missing = @()
foreach ($item in $Required) {
  $path = Join-Path $Root $item
  if (-not (Test-Path -LiteralPath $path)) {
    $Missing += $item
  }
}

if ($Missing.Count -gt 0) {
  Write-Host "Missing framework files:"
  $Missing | ForEach-Object { Write-Host "  - $_" }
  exit 1
}

Write-Host "GOAL development base check passed: $($Required.Count) required files found."
