$ErrorActionPreference = "Stop"

$Root = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")
$SkillRoot = Join-Path $Root ".agents\skills"

$RequiredSkills = @(
  "project-orchestrator",
  "product-spec-builder",
  "design-brief-builder",
  "prototype-builder",
  "dev-planner",
  "goal-creator",
  "dev-builder",
  "bug-fixer",
  "gate-runner",
  "code-reviewer",
  "review-runner",
  "release-builder",
  "requirements-traceability-runner",
  "frontend-quality-runner",
  "frontend-workflow-planner",
  "open-source-research-runner",
  "systematic-debugging-runner",
  "lane-recovery-runner",
  "evolution-runner",
  "goal-methodology-guide"
)

# Keep this script ASCII-only so Windows PowerShell can parse it without UTF-8 BOM.
# Regex patterns use .NET \uXXXX escapes to match Chinese section names and concepts.
$CommonChecks = @(
  @{ Name = "frontmatter-name"; Pattern = "(?m)^name:\s*[-a-z0-9]+\r?$" },
  @{ Name = "frontmatter-description"; Pattern = "(?m)^description:\s*.+\r?$" },
  @{ Name = "core-contract"; Pattern = "\u6838\u5fc3\u5951\u7ea6" },
  @{ Name = "output"; Pattern = "\u8f93\u51fa" },
  @{ Name = "completion-gate"; Pattern = "\u5b8c\u6210\u95e8\u7981" },
  @{ Name = "reject-or-judge"; Pattern = "\u6253\u56de\u6761\u4ef6|\u5fc5\u987b\u6f84\u6e05|\u53d1\u5e03\u8bb0\u5f55\u5fc5\u987b\u5305\u542b|\u4fdd\u7559\u89c4\u5219\u7684\u6807\u51c6|\u5fc5\u987b\u8f93\u51fa\u7684\u8bc1\u636e" },
  @{ Name = "signal-loop"; Pattern = "\u4fe1\u53f7|signal|signals" },
  @{ Name = "natural-language-hooks"; Pattern = "\u81ea\u7136\u8bed\u8a00\u89e6\u53d1\u8bcd" },
  @{ Name = "documentation-language"; Pattern = "\u9879\u76ee\u6587\u6863\u4e2d\u6587\u4f18\u5148" }
)

$SpecificChecks = @{
  "project-orchestrator" = @(
    @{ Name = "state-doc"; Pattern = "docs/00-project-state.md" },
    @{ Name = "capability-registry"; Pattern = "docs/capability-status.json" },
    @{ Name = "provider-contract"; Pattern = "capability-provider-contract.md" },
    @{ Name = "light-continue"; Pattern = "\u8f7b\u91cf\u7ee7\u7eed|\u9ed8\u8ba4\u4f7f\u7528" },
    @{ Name = "light-escalation"; Pattern = "\u7528\u6237\u53cd\u9988.*\u72b6\u6001\u6587\u6863|\u8bc1\u636e\u8fc7\u671f" },
    @{ Name = "hook-table"; Pattern = "\.codex/hooks/skill-hooks.md" },
    @{ Name = "dispatch-order"; Pattern = "\u8c03\u5ea6\u987a\u5e8f" },
    @{ Name = "layer-routing"; Pattern = "\u524d\u7aef.*\u540e\u7aef.*\u8054\u8c03|\u5206\u5c42\u81ea\u4e3b\u5206\u6d41" },
    @{ Name = "real-provider-routing"; Pattern = "\u771f\u5b9e\u63a5\u5165|real_smoke|Provider|API" },
    @{ Name = "throughput-mode"; Pattern = "\u6548\u7387\u6a21\u5f0f|\u7eb5\u5411\u95ed\u73af|\u4ea4\u4ed8\u6548\u7387" },
    @{ Name = "review-debounce"; Pattern = "\u5ba1\u67e5\u9632\u6296|P1/P2|review-runner" },
    @{ Name = "slice-budget"; Pattern = "2-3|\u51c6\u5907\u6027\u5207\u7247" },
    @{ Name = "user-usable-definition"; Pattern = "\u7528\u6237\u53ef\u7528.*\u5165\u53e3.*fixture.*artifact" },
    @{ Name = "registry-validator"; Pattern = "validate-capability-status.ps1" },
    @{ Name = "real-execution-self-close"; Pattern = "\u771f\u5b9e\u6267\u884c\u5931\u8d25.*cwd|\u771f\u5b9e\u6267\u884c\u901a\u8fc7.*artifact" },
    @{ Name = "mock-boundary"; Pattern = "mock|stub|monkeypatch" },
    @{ Name = "media-fixture-scope"; Pattern = "audio fixture|video/raw-video|scene-split|atom" },
    @{ Name = "capability-exit-check"; Pattern = "Capability Exit Check|capability exit check" },
    @{ Name = "capability-focus-budget"; Pattern = "current-stage-good-enough|non-same-capability loop" },
    @{ Name = "sketch-plan-loop"; Pattern = "Sketch Plan Loop|\u9aa8\u67b6\u8ba1\u5212\u5faa\u73af|Skeleton Plan Refresh" },
    @{ Name = "autonomous-iteration-loop"; Pattern = "Autonomous Iteration Check|Autonomous Iteration Loop|\u81ea\u4e3b\u8fed\u4ee3" },
    @{ Name = "skeleton-refresh-triggers"; Pattern = "\u5b8c\u6210\u5ea6|\u592a\u6162|\u6574\u4f53\u63a8\u8fdb|\u9879\u76ee\u8fd8\u5dee\u4ec0\u4e48" },
    @{ Name = "multi-lane-collaboration"; Pattern = "\u591a\u6cf3\u9053|Agent Lanes|completion callback" },
    @{ Name = "discussion-intake"; Pattern = "discussion intake|\u8fde\u7eed\u8ba8\u8bba|capture_only|dispatch_needed" },
    @{ Name = "discussion-hook-matrix"; Pattern = "\u8ba8\u8bba\u573a\u666f Hook \u77e9\u9635|\u4f18\u5148 Skill|\u9ed8\u8ba4\u6cf3\u9053" },
    @{ Name = "structured-dispatch"; Pattern = "\u7ed3\u6784\u5316\u6d3e\u53d1|structured" },
    @{ Name = "product-loop-check"; Pattern = "Product Loop Check|active_user_loop|loop_impact" },
    @{ Name = "stage-value-gate"; Pattern = "Stage Value Gate|stage_priority|why_now|mainline_impact" },
    @{ Name = "next-mainline-slice-selection"; Pattern = "Next Mainline Slice Selection|next_mainline_slice_selection|stage_release_record" },
    @{ Name = "mainline-concern-policy"; Pattern = "blocking_concerns[\s\S]*backlog_concerns[\s\S]*P1/P2|backlog_concerns[\s\S]*backlog" },
    @{ Name = "needs-context-only-three"; Pattern = "NEEDS_CONTEXT|secret|account|regulated operation|high-risk automation|\u771f\u5b9e\u5916\u90e8\u8c03\u7528|\u4ed8\u8d39|\u53d7\u76d1\u7ba1\u64cd\u4f5c|\u9ad8\u98ce\u9669\u81ea\u52a8\u5316\u6267\u884c|\u91cd\u5927\u4ea7\u54c1\u8def\u7ebf|\u4e0a\u4e0b\u6587\u4e0d\u8db3" },
    @{ Name = "backlog-concern-policy"; Pattern = "blocking_concern|backlog_concern" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" },
    @{ Name = "next-continue"; Pattern = "\u4e0b\u4e00\u6b65|\u7ee7\u7eed" },
    @{ Name = "local-skills"; Pattern = "product-spec-builder|dev-builder|review-runner" }
  )
  "product-spec-builder" = @(
    @{ Name = "product-doc"; Pattern = "docs/01-product-spec.md" },
    @{ Name = "acceptance"; Pattern = "\u9a8c\u6536" },
    @{ Name = "scope"; Pattern = "\u8303\u56f4|\u505a\u4e0e\u4e0d\u505a" }
  )
  "design-brief-builder" = @(
    @{ Name = "design-doc"; Pattern = "docs/02-design-brief.md" },
    @{ Name = "interaction"; Pattern = "\u4ea4\u4e92" },
    @{ Name = "prototype-boundary"; Pattern = "\u539f\u578b|\u590d\u7528" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" }
  )
  "prototype-builder" = @(
    @{ Name = "prototype"; Pattern = "\u539f\u578b" },
    @{ Name = "reuse-policy"; Pattern = "\u590d\u7528|\u5e9f\u5f03|\u53c2\u8003" },
    @{ Name = "dev-plan-input"; Pattern = "docs/03-dev-plan.md" }
  )
  "dev-planner" = @(
    @{ Name = "dev-plan-doc"; Pattern = "docs/03-dev-plan.md" },
    @{ Name = "phase"; Pattern = "\u9636\u6bb5" },
    @{ Name = "verification"; Pattern = "\u9a8c\u8bc1" },
    @{ Name = "frontend-backend-slicing"; Pattern = "\u524d\u7aef.*\u540e\u7aef|\u7eb5\u5411\u5207\u7247|\u8054\u8c03" },
    @{ Name = "user-usable-definition"; Pattern = "\u7528\u6237\u53ef\u7528.*\u5165\u53e3.*fixture.*artifact" },
    @{ Name = "capability-registry"; Pattern = "docs/capability-status.json|validate-capability-status.ps1" },
    @{ Name = "multi-lane-optional-plan"; Pattern = "\u591a\u6cf3\u9053|\u6cf3\u9053\u4f9d\u8d56|\u5e76\u884c\u6cf3\u9053" },
    @{ Name = "skeleton-plan-mode"; Pattern = "Skeleton Plan Refresh|Skeleton Pass|Real Pass|Quality Pass|Production Pass" },
    @{ Name = "skeleton-gap-questions"; Pattern = "\u54ea\u4e00\u73af\u662f\u7a7a\u767d|3-6|\u8584\u7eb5\u5411\u5207\u7247" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" }
  )
  "goal-creator" = @(
    @{ Name = "completion-standards"; Pattern = "\u5b8c\u6210\u6807\u51c6" },
    @{ Name = "verification-method"; Pattern = "\u9a8c\u8bc1\u65b9\u5f0f" },
    @{ Name = "loop-rule"; Pattern = "\u5faa\u73af\u89c4\u5219" },
    @{ Name = "subagent-plan"; Pattern = "\u5b50 Agent|\u65b0\u8111\u5b50" },
    @{ Name = "auto-gate"; Pattern = "\u81ea\u52a8\u95e8\u7981|gate-runner" },
    @{ Name = "multi-lane-optional-goal"; Pattern = "\u591a\u6cf3\u9053|\u7ed3\u6784\u5316\u6cf3\u9053\u4efb\u52a1" }
  )
  "dev-builder" = @(
    @{ Name = "self-test"; Pattern = "\u81ea\u6d4b|\u9a8c\u8bc1" },
    @{ Name = "independent-review"; Pattern = "\u72ec\u7acb\u5ba1\u67e5" },
    @{ Name = "document-update"; Pattern = "\u6587\u6863\u66f4\u65b0|\u66f4\u65b0\u53d7\u5f71\u54cd\u6587\u6863" },
    @{ Name = "new-brain-gate"; Pattern = "\u65b0\u8111\u5b50|code-reviewer|review-runner" },
    @{ Name = "gate-runner"; Pattern = "gate-runner|\u95e8\u7981" },
    @{ Name = "frontend-backend-contract"; Pattern = "\u524d\u7aef.*\u540e\u7aef|\u6570\u636e\u5951\u7ea6|\u8054\u8c03" },
    @{ Name = "real-provider-execution"; Pattern = "\u771f\u5b9e\u8c03\u7528|real_smoke|pending_user_approval|Provider" },
    @{ Name = "risk-tiered-flow"; Pattern = "low_risk|medium_risk|high_risk" },
    @{ Name = "capability-registry"; Pattern = "docs/capability-status.json" },
    @{ Name = "provider-contract"; Pattern = "capability-provider-contract.md" },
    @{ Name = "review-debounce"; Pattern = "\u540c\u4e00\u7eb5\u5411\u529f\u80fd\u5305|P1/P2|review-runner" },
    @{ Name = "slice-budget"; Pattern = "2-3|\u51c6\u5907\u6027\u5207\u7247" },
    @{ Name = "user-usable-definition"; Pattern = "\u7528\u6237\u53ef\u7528.*\u5165\u53e3.*fixture.*artifact" },
    @{ Name = "capability-variants"; Pattern = "variants|\u666e\u901a\u751f\u6210|\u53c2\u8003\u8f93\u5165|CUDA/CPU" },
    @{ Name = "registry-validator"; Pattern = "validate-capability-status.ps1" },
    @{ Name = "real-execution-self-close"; Pattern = "\u771f\u5b9e\u6267\u884c\u5931\u8d25.*cwd|\u771f\u5b9e\u6267\u884c\u901a\u8fc7.*artifact" },
    @{ Name = "mock-boundary"; Pattern = "mock|stub|monkeypatch" },
    @{ Name = "media-fixture-scope"; Pattern = "audio fixture|video/raw-video|scene-split|atom" },
    @{ Name = "capability-exit-check"; Pattern = "Capability Exit Check|capability exit check" },
    @{ Name = "capability-focus-budget"; Pattern = "current-stage-good-enough|non-same-capability loop" },
    @{ Name = "skeleton-thin-slice"; Pattern = "\u8584\u7eb5\u5411\u5207\u7247|\u9aa8\u67b6\u8ba1\u5212\u4e0b\u4e00\u5200|Skeleton Plan" },
    @{ Name = "skeleton-output-judgment"; Pattern = "Skeleton Pass|Real Pass|Quality Pass|Production Pass|\u4ea7\u54c1\u9aa8\u67b6" },
    @{ Name = "cumulative-review"; Pattern = "3-5|\u5c0f\u4fee.*\u5408\u5e76\u5ba1\u67e5" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" }
  )
  "bug-fixer" = @(
    @{ Name = "reproduce"; Pattern = "\u590d\u73b0" },
    @{ Name = "root-cause"; Pattern = "\u6839\u56e0" },
    @{ Name = "regression"; Pattern = "\u56de\u5f52\u9a8c\u8bc1" }
  )
  "gate-runner" = @(
    @{ Name = "auto-gate"; Pattern = "\u81ea\u52a8\u95e8\u7981|\u95e8\u7981" },
    @{ Name = "build-test"; Pattern = "\u6784\u5efa|\u6d4b\u8bd5|typecheck|lint" },
    @{ Name = "review-gate"; Pattern = "\u5ba1\u67e5\u95e8\u7981|code-reviewer|review-runner" },
    @{ Name = "integration-gate"; Pattern = "\u5951\u7ea6\u95e8\u7981|\u8054\u8c03\u95e8\u7981|\u524d\u7aef\u95e8\u7981" },
    @{ Name = "real-execution-gate"; Pattern = "\u771f\u5b9e\u6267\u884c\u95e8\u7981|real_smoke|pending_user_approval|Provider" },
    @{ Name = "focused-gates"; Pattern = "\u805a\u7126\u95e8\u7981|low_risk|medium_risk|high_risk" },
    @{ Name = "multi-lane-focused-gates"; Pattern = "\u591a\u6cf3\u9053|\u6309\u6cf3\u9053\u53d8\u66f4\u9762|\u805a\u7126\u95e8\u7981" },
    @{ Name = "capability-registry"; Pattern = "docs/capability-status.json" },
    @{ Name = "provider-contract"; Pattern = "capability-provider-contract.md" },
    @{ Name = "review-debounce"; Pattern = "\u540c\u4e00\u7eb5\u5411\u529f\u80fd\u5305|P1/P2|\u5b8c\u6574\u5ba1\u67e5\u95e8\u7981" },
    @{ Name = "user-usable-gate"; Pattern = "\u7528\u6237\u53ef\u7528\u95e8\u7981|\u7528\u6237\u53ef\u7528.*\u5165\u53e3" },
    @{ Name = "registry-validator"; Pattern = "validate-capability-status.ps1" },
    @{ Name = "real-execution-self-close"; Pattern = "\u771f\u5b9e\u6267\u884c\u81ea\u6536\u5c3e|\u4fee\u590d\u540e\u5fc5\u987b\u590d\u8dd1" },
    @{ Name = "mock-boundary"; Pattern = "mock|stub|monkeypatch" },
    @{ Name = "media-fixture-scope"; Pattern = "audio fixture|video fixture|selectable atom" },
    @{ Name = "cumulative-review"; Pattern = "3-5|\u5c0f\u4fee.*\u5408\u5e76\u5ba1\u67e5" },
    @{ Name = "release-gate"; Pattern = "\u53d1\u5e03\u95e8\u7981|\u5192\u70df|\u56de\u6eda" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" }
  )
  "code-reviewer" = @(
    @{ Name = "code-review"; Pattern = "\u4ee3\u7801\u5ba1\u67e5|\u4ee3\u7801\u7ea7\u5ba1\u67e5" },
    @{ Name = "bugs"; Pattern = "bug|\u56de\u5f52" },
    @{ Name = "tests"; Pattern = "\u6d4b\u8bd5|\u9a8c\u8bc1" },
    @{ Name = "blocking"; Pattern = "\u963b\u585e" },
    @{ Name = "new-brain"; Pattern = "\u65b0\u8111\u5b50|\u672a\u53c2\u4e0e\u5b9e\u73b0" }
  )
  "review-runner" = @(
    @{ Name = "independent-view"; Pattern = "\u72ec\u7acb\u89c6\u89d2|\u65b0\u8111\u5b50" },
    @{ Name = "blocking-finding"; Pattern = "\u963b\u585e" },
    @{ Name = "evidence"; Pattern = "\u8bc1\u636e" },
    @{ Name = "subagent-context"; Pattern = "\u5b50 Agent|\u6d3e\u53d1" },
    @{ Name = "frontend-backend-alignment"; Pattern = "\u524d\u7aef.*\u540e\u7aef|\u8054\u8c03|\u6570\u636e\u9002\u914d" },
    @{ Name = "provider-maturity-review"; Pattern = "contract_defined|real_smoke_passed|integration_connected|production_ready" },
    @{ Name = "risk-tiered-review"; Pattern = "\u5ba1\u67e5\u89e6\u53d1\u5f3a\u5ea6|low_risk|medium_risk|high_risk" },
    @{ Name = "capability-registry"; Pattern = "docs/capability-status.json" },
    @{ Name = "provider-contract"; Pattern = "capability-provider-contract.md" },
    @{ Name = "review-debounce"; Pattern = "\u5ba1\u67e5\u9632\u6296|\u540c\u4e00\u7eb5\u5411\u529f\u80fd\u5305|P1/P2" },
    @{ Name = "multi-lane-review-aggregation"; Pattern = "\u591a\u6cf3\u9053|callback|review_deferred_until_boundary" },
    @{ Name = "user-usable-review"; Pattern = "\u7528\u6237\u53ef\u7528.*\u5165\u53e3.*fixture.*artifact" },
    @{ Name = "capability-variants"; Pattern = "variants|\u666e\u901a\u751f\u6210|\u53c2\u8003\u8f93\u5165|CUDA/CPU" },
    @{ Name = "registry-validator"; Pattern = "validate-capability-status.ps1" },
    @{ Name = "real-execution-self-close"; Pattern = "\u771f\u5b9e\u6267\u884c\u5931\u8d25.*cwd|\u771f\u5b9e\u6267\u884c\u901a\u8fc7.*artifact" },
    @{ Name = "mock-boundary"; Pattern = "mock|stub|monkeypatch" },
    @{ Name = "media-fixture-scope"; Pattern = "audio fixture|video/raw-video|scene-split|atom" },
    @{ Name = "user-loop-progress"; Pattern = "user_loop_progress|blocking_concerns|backlog_concerns" },
    @{ Name = "recommended-next-type"; Pattern = "recommended_next_type|vertical_loop|backlog_only" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*user_loop_progress[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" },
    @{ Name = "cumulative-review"; Pattern = "3-5|\u5c0f\u4fee.*\u5408\u5e76\u5ba1\u67e5" }
  )
  "release-builder" = @(
    @{ Name = "startup"; Pattern = "\u542f\u52a8" },
    @{ Name = "logs"; Pattern = "\u65e5\u5fd7" },
    @{ Name = "rollback"; Pattern = "\u56de\u6eda" },
    @{ Name = "smoke"; Pattern = "\u5192\u70df" },
    @{ Name = "release-review"; Pattern = "\u65b0\u8111\u5b50|code-reviewer|review-runner" },
    @{ Name = "gate-runner"; Pattern = "gate-runner|\u81ea\u52a8\u95e8\u7981" },
    @{ Name = "external-dependency-package"; Pattern = "\u6a21\u578b\u4f9d\u8d56|\u5916\u90e8 API \u4f9d\u8d56|Provider \u4f9d\u8d56|\u4f9d\u8d56\u525d\u79bb" }
  )
  "requirements-traceability-runner" = @(
    @{ Name = "review-report-output"; Pattern = "docs/05-review-report.md" },
    @{ Name = "lane-workspace-output"; Pattern = "agent-lanes/lanes/<lane>/workspace|workspace/traceability" },
    @{ Name = "traceability-matrix"; Pattern = "traceability matrix|Req ID|INFERRED-001" },
    @{ Name = "no-parallel-doc-system"; Pattern = "\u4e0d\u65b0\u5efa\u5e76\u884c\u9700\u6c42\u4f53\u7cfb|\u4e0d\u8981\u521b\u5efa\u65b0\u7684\u9876\u5c42\u9700\u6c42\u8ffd\u8e2a\u6587\u6863" },
    @{ Name = "user-usable-check"; Pattern = "\u7528\u6237\u53ef\u89c1\u80fd\u529b|\u5165\u53e3.*\u8f93\u5165.*\u8f93\u51fa" }
  )
  "frontend-quality-runner" = @(
    @{ Name = "design-doc-output"; Pattern = "docs/02-design-brief.md" },
    @{ Name = "review-report-output"; Pattern = "docs/05-review-report.md" },
    @{ Name = "artifact-output"; Pattern = "artifacts/<slice>" },
    @{ Name = "browser-evidence"; Pattern = "Playwright|\u6d4f\u89c8\u5668\u622a\u56fe|\u771f\u5b9e\u6d4f\u89c8\u5668" },
    @{ Name = "research-workbench"; Pattern = "\u7814\u7a76\u5de5\u4f5c\u53f0|landing page" }
  )
  "frontend-workflow-planner" = @(
    @{ Name = "frontend-doc-output"; Pattern = "docs/frontend/" },
    @{ Name = "ia-artifact"; Pattern = "01-information-architecture.md" },
    @{ Name = "surface-artifact"; Pattern = "02-surface-specs.md" },
    @{ Name = "component-inventory"; Pattern = "03-component-inventory.md" },
    @{ Name = "data-contract-map"; Pattern = "04-data-contract-map.md|data_contract" },
    @{ Name = "design-token-plan"; Pattern = "05-design-token-plan.md|Design Token" },
    @{ Name = "figma-bridge"; Pattern = "06-figma-bridge.md|Figma" },
    @{ Name = "iteration-log"; Pattern = "07-iteration-log.md|iteration-log" },
    @{ Name = "external-skill-boundary"; Pattern = "interface-design|frontend-design|figma-use|figma-generate-design|Figma" },
    @{ Name = "guardian-boundary"; Pattern = "guardian|provider live call|secret|scheduler|production feed|high-risk|regulated" }
  )
  "open-source-research-runner" = @(
    @{ Name = "reference-pool-output"; Pattern = "docs/08-open-source-reference-pool.md" },
    @{ Name = "research-roadmap-output"; Pattern = "docs/09-research-roadmap.md" },
    @{ Name = "capability-status"; Pattern = "docs/capability-status.json" },
    @{ Name = "license-risk"; Pattern = "license" },
    @{ Name = "guardian-boundary"; Pattern = "\u5b88\u95e8\u6cf3\u9053|\u4e0d\u5f97\u76f4\u63a5\u590d\u5236\u5916\u90e8\u4ee3\u7801" }
  )
  "systematic-debugging-runner" = @(
    @{ Name = "goal-log-output"; Pattern = "docs/04-goal-log.md" },
    @{ Name = "review-report-output"; Pattern = "docs/05-review-report.md" },
    @{ Name = "root-cause"; Pattern = "root cause|\u6839\u56e0" },
    @{ Name = "same-path-regression"; Pattern = "\u540c\u8def\u5f84\u56de\u5f52|\u590d\u8dd1\u540c\u4e00\u5931\u8d25\u8def\u5f84" },
    @{ Name = "agent-lanes-flow"; Pattern = "message_id|post office|callback|message-log" }
  )
  "lane-recovery-runner" = @(
    @{ Name = "registry-update"; Pattern = "agent-lanes/agent-registry.json" },
    @{ Name = "message-log-audit"; Pattern = "agent-lanes/message-log.jsonl" },
    @{ Name = "worklog-update"; Pattern = "worklog.md" },
    @{ Name = "workspace-recovery"; Pattern = "workspace/lane-recovery|orchestrator-recovery-template" },
    @{ Name = "thread-replacement"; Pattern = "thread_id|\u65e7\u7ebf\u7a0b|\u65b0\u7ebf\u7a0b" },
    @{ Name = "archive-old-thread"; Pattern = "\u5f52\u6863\u65e7\u7ebf\u7a0b|\u5386\u53f2\u5ba1\u8ba1" },
    @{ Name = "slim-recovery-prompt"; Pattern = "\u7626\u8eab\u63a5\u7ba1|\u77ed\u5065\u5eb7\u68c0\u67e5|\u4e0d\u8981\u4e00\u6b21\u6027\u585e\u5165" },
    @{ Name = "health-check-before-cutover"; Pattern = "\u5065\u5eb7\u68c0\u67e5\u901a\u8fc7\u524d|\u81f3\u5c11\u4e24\u6b21\u8f7b\u91cf\u5065\u5eb7\u68c0\u67e5|current thread" },
    @{ Name = "second-failure-archive"; Pattern = "\u4e8c\u6b21\u6545\u969c|agent loop died unexpectedly|failed to start turn" },
    @{ Name = "dashboard-refresh"; Pattern = "render_dashboard.py|dashboard.md" }
  )
  "evolution-runner" = @(
    @{ Name = "signals-dir"; Pattern = "\.codex/signals/" },
    @{ Name = "auto-landing-boundary"; Pattern = "\u81ea\u52a8\u843d\u5730\u6743\u9650|\u5fc5\u987b\u5148\u505c\u4e0b\u6765\u8bf7\u6c42\u7528\u6237\u786e\u8ba4" },
    @{ Name = "prune-rules"; Pattern = "\u5220\u9664\u89c4\u5219|\u957f\u671f\u4e0d\u7528|\u8fc7\u65f6" },
    @{ Name = "evolve-other-skills"; Pattern = "\u8fdb\u5316\u5176\u4ed6 Skill|\u88ab\u8fdb\u5316\u7684 Skill|\u672c\u5730 Skills" },
    @{ Name = "callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" }
  )
  "goal-methodology-guide" = @(
    @{ Name = "methodology-reference"; Pattern = "GOAL-methodology-abstract.md" },
    @{ Name = "usage-playbook"; Pattern = "usage-playbook.md" },
    @{ Name = "gate-timing"; Pattern = "\u95e8\u7981|\u811a\u672c" },
    @{ Name = "evolution-timing"; Pattern = "\u81ea\u8fdb\u5316|signals|signal" },
    @{ Name = "subagent-timing"; Pattern = "\u5b50 Agent|\u65b0\u8111\u5b50" },
    @{ Name = "sketch-plan-loop"; Pattern = "Sketch Plan Loop|\u9aa8\u67b6\u8ba1\u5212\u5faa\u73af|Skeleton Plan Refresh" }
  )
}

if (-not (Test-Path -LiteralPath $SkillRoot)) {
  Write-Host "Skill directory not found: $SkillRoot"
  exit 1
}

$Failures = @()
$Rows = @()

foreach ($skill in $RequiredSkills) {
  $skillPath = Join-Path $SkillRoot $skill
  $skillFile = Join-Path $skillPath "SKILL.md"

  if (-not (Test-Path -LiteralPath $skillFile)) {
    $Failures += "$skill missing SKILL.md"
    $Rows += [PSCustomObject]@{ Skill = $skill; Result = "FAIL"; Missing = "SKILL.md" }
    continue
  }

  $content = Get-Content -LiteralPath $skillFile -Encoding UTF8 -Raw
  $missing = @()

  foreach ($check in $CommonChecks) {
    if ($content -notmatch $check.Pattern) {
      $missing += $check.Name
    }
  }

  foreach ($check in $SpecificChecks[$skill]) {
    if ($content -notmatch $check.Pattern) {
      $missing += $check.Name
    }
  }

  if ($missing.Count -gt 0) {
    $Failures += "$skill missing: $($missing -join ', ')"
    $Rows += [PSCustomObject]@{ Skill = $skill; Result = "FAIL"; Missing = ($missing -join ", ") }
  } else {
    $Rows += [PSCustomObject]@{ Skill = $skill; Result = "PASS"; Missing = "" }
  }
}

$RequiredProjectText = @(
  @{ Path = "AGENTS.md"; Name = "agents-capability-exit-check"; Pattern = "Capability Exit Check" },
  @{ Path = "AGENTS.md"; Name = "agents-current-stage-good-enough"; Pattern = "current-stage-good-enough" },
  @{ Path = "AGENTS.md"; Name = "agents-multi-lane-slimming"; Pattern = "\u591a\u6cf3\u9053\u534f\u4f5c\u4e0b\u7684 Skill \u7626\u8eab" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-capability-exit-check"; Pattern = "capability exit check" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-multi-lane"; Pattern = "\u591a\u6cf3\u9053\u534f\u4f5c" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-discussion-intake"; Pattern = "discussion intake|\u8def\u7ebf\u8ba8\u8bba|\u6301\u7eed\u8fed\u4ee3" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-scenario-matrix"; Pattern = "\u8ba8\u8bba\u573a\u666f Hook \u77e9\u9635" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-need-plan-tech"; Pattern = "\u63a2\u8ba8\u9700\u6c42|\u63a2\u8ba8\u8ba1\u5212|\u63a2\u8ba8\u6280\u672f\u65b9\u6848" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-lane-dispatch-trace"; Pattern = "discussion_source|source_message_id|pending_dispatch" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-sketch-plan-loop"; Pattern = "Sketch Plan Loop|\u9aa8\u67b6\u8ba1\u5212\u5faa\u73af|Skeleton Plan Refresh" },
  @{ Path = "AGENTS.md"; Name = "agents-sketch-plan-loop"; Pattern = "Sketch Plan Loop|\u9aa8\u67b6\u4f18\u5148\u63a8\u8fdb|\u4ea7\u54c1\u9aa8\u67b6" },
  @{ Path = "AGENTS.md"; Name = "agents-product-loop-first"; Pattern = "Product Loop First|active_user_loop|loop_impact" },
  @{ Path = "AGENTS.md"; Name = "agents-stage-value-gate"; Pattern = "Stage Value Gate|stage_priority|why_now|mainline_impact" },
  @{ Path = "AGENTS.md"; Name = "agents-next-mainline-slice-selection"; Pattern = "Next Mainline Slice Selection|next_mainline_slice_selection|stage_release_record" },
  @{ Path = "AGENTS.md"; Name = "agents-mainline-concern-policy"; Pattern = "blocking_concerns[\s\S]*backlog_concerns[\s\S]*P1/P2|backlog_concerns[\s\S]*backlog" },
  @{ Path = "AGENTS.md"; Name = "agents-callback-loop-fields"; Pattern = "active_user_loop[\s\S]*blocking_concerns[\s\S]*backlog_concerns[\s\S]*recommended_next_type" },
  @{ Path = "agent-lanes\scripts\render_dashboard.py"; Name = "dashboard-loop-warnings"; Pattern = "loop_field_warnings|recent_loop_warnings|Product Loop"; Optional = $true },
  @{ Path = "agent-lanes\scripts\deliver_callback.py"; Name = "post-office-loop-warnings"; Pattern = "callback_loop_field_warnings|missing_product_loop_fields"; Optional = $true },
  @{ Path = "AGENTS.md"; Name = "agents-documentation-language"; Pattern = "\u9879\u76ee\u6587\u6863\u4e2d\u6587\u4f18\u5148|language_rule" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-documentation-language"; Pattern = "\u4e2d\u6587\u6587\u6863|\u6587\u6863\u4e2d\u6587|\u6240\u6709\u6587\u6863\u7528\u4e2d\u6587" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-localized-enhancement-skills"; Pattern = "requirements-traceability-runner|frontend-quality-runner|open-source-research-runner|systematic-debugging-runner|lane-recovery-runner" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-frontend-workflow-planner"; Pattern = "frontend-workflow-planner|data_contract|Design Token" },
  @{ Path = "AGENTS.md"; Name = "agents-localized-enhancement-skills"; Pattern = "requirements-traceability-runner|frontend-quality-runner|open-source-research-runner|systematic-debugging-runner|lane-recovery-runner" },
  @{ Path = "AGENTS.md"; Name = "agents-project-local-skills"; Pattern = "\.agents/skills|\u516c\u5171 Skill|\u9879\u76ee\u672c\u5730\u5316" },
  @{ Path = ".codex\hooks\skill-hooks.md"; Name = "hooks-lane-recovery-health-check"; Pattern = "\u7626\u8eab\u63a5\u7ba1|\u5065\u5eb7\u68c0\u67e5|\u4e8c\u6b21\u6545\u969c" },
  @{ Path = ".agents/skills/evolution-runner/SKILL.md"; Name = "evolution-project-local-skills"; Pattern = "\.agents/skills|\u9879\u76ee\u673a\u5236 Skill|\u516c\u5171 Skill" }
)

foreach ($check in $RequiredProjectText) {
  $target = Join-Path $Root $check.Path
  if (-not (Test-Path -LiteralPath $target)) {
    if ($check.Optional) {
      continue
    }
    $Failures += "$($check.Path) missing for $($check.Name)"
    continue
  }

  $content = Get-Content -LiteralPath $target -Encoding UTF8 -Raw
  if ($content -notmatch $check.Pattern) {
    $Failures += "$($check.Path) missing: $($check.Name)"
  }
}

$Rows | Format-Table -AutoSize

if ($Failures.Count -gt 0) {
  Write-Host "GOAL skill mechanism check failed:"
  $Failures | ForEach-Object { Write-Host "  - $_" }
  exit 1
}

Write-Host "GOAL skill mechanism check passed: $($RequiredSkills.Count) skills satisfy required mechanism checks."
