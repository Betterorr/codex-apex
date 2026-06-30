# 泳道 Skill 与 Hook 设置总表

本文件用于新项目移植时核对：每条泳道默认应该使用哪些 GOAL skill、这些 skill 的自然语言 hook 要写在哪里、命中后应该落到哪些项目文件。

核心原则：

- 真正影响 Codex 自动选择 skill 的位置是每个 `SKILL.md` 的 frontmatter `description`。
- 维护用总表是 `goal-development-base/.codex/hooks/skill-hooks.md`。
- 每个 `SKILL.md` 正文必须保留“自然语言触发词”段，方便人工审查和机制门禁检查。
- 新增、删除或改造 skill 时，必须同时更新这三个位置：`description`、正文触发词、`skill-hooks.md`。

## 总览

| 泳道 | 默认职责 | 默认 skill | 关键 hook / 用户说法 | 默认产物 |
| --- | --- | --- | --- | --- |
| 主调度泳道 `orchestrator` | 读状态、判断下一步、派发泳道、合并 callback、节奏控制 | `project-orchestrator`, `goal-creator`, `goal-methodology-guide` | 下一步、继续、整体推进、完成度、太慢、全链路、需求讨论、技术路线、泳道派发、callback 打断主调度、模板怎么用 | `docs/00-project-state.md`, `docs/04-goal-log.md`, `agent-lanes/message-log.jsonl`, `agent-lanes/dashboard.md` |
| 规划泳道 `planning` | 需求、范围、验收标准、阶段计划、骨架计划 | `product-spec-builder`, `dev-planner`, `goal-creator`, `requirements-traceability-runner` | 需求、PRD、MVP、先做什么、开发计划、阶段路线、需求追踪、traceability matrix、Skeleton Plan Refresh | `docs/01-product-spec.md`, `docs/03-dev-plan.md`, `docs/05-review-report.md`, planning worklog/workspace |
| 设计泳道 `design` | UI/UX、信息架构、页面状态、原型、前端体验标准 | `design-brief-builder`, `prototype-builder`, `frontend-quality-runner` | UI、UX、页面怎么设计、交互、信息架构、原型、Figma、前端质感、页面可读性、浏览器截图验收 | `docs/02-design-brief.md`, `docs/05-review-report.md`, `artifacts/<slice>/`, design worklog/workspace |
| 开发泳道 `development` | 实现、修 bug、联调、局部门禁、真实样本/fixture 接线 | `dev-builder`, `bug-fixer`, `gate-runner`, `systematic-debugging-runner` | 实现、开始开发、改代码、联调、跑起来、bug、报错、测试失败、先查根因、门禁、真实 smoke | 业务代码、`scripts/`, `artifacts/`, `docs/04-goal-log.md`, capability registry 更新 |
| 守门泳道 `guardian` | 权限、secret、外部 API、账号、付费、发布、安全、provider 边界 | `gate-runner`, `code-reviewer`, `goal-methodology-guide`, `open-source-research-runner` | secret、付费 API、账号、外部 provider、真实调用、license、权限、安全、生产声明、交易/远程写入 | `docs/capability-status.json`, `docs/capability-provider-contract.md`, guardian worklog/workspace |
| 验收泳道 `review` | 独立验收、证据核对、代码审查、需求覆盖、阶段边界复核 | `review-runner`, `code-reviewer`, `gate-runner`, `requirements-traceability-runner`, `frontend-quality-runner` | 检查是否完成、验收、证据够不够、代码审查、完成了吗、需求覆盖、前后端是否对齐、UI 截图验收 | `docs/05-review-report.md`, `docs/06-release-record.md`, review worklog/workspace |
| 进化泳道 `evolution` | 沉淀重复失败、改模板、改 hook、改门禁、skill 适配 | `evolution-runner`, `goal-methodology-guide`, `systematic-debugging-runner` | 进化、沉淀规则、模板升级、hook 设置、skill 适配、规则膨胀、callback 机制不对、信息流断了 | 模板目录、`.agents/skills/`, `.codex/hooks/`, `.codex/gates/`, evolution worklog |

## Skill Hook 必须落位的位置

每个 skill 都必须有三处 hook：

1. `goal-development-base/.agents/skills/<skill-name>/SKILL.md`
   - frontmatter `description`：用于 Codex 自动发现和触发。
   - 正文“自然语言触发词”：用于人工维护和审查。
2. `goal-development-base/.codex/hooks/skill-hooks.md`
   - 汇总所有 skill 的触发词。
   - 包含“讨论场景 Hook 矩阵”，用于主调度做 discussion intake。
3. `goal-development-base/.codex/gates/skill-mechanism-check.ps1`
   - 机制门禁必须检查 `frontmatter-name`、`frontmatter-description`、`自然语言触发词`、`完成门禁`、`打回条件`、`项目文档中文优先` 等核心规则。

## 主调度 Hook 分流规则

主调度线程收到用户自然语言时，先由 `project-orchestrator` 做 discussion intake，再决定是否派泳道：

| 用户正在说什么 | 分类 | 默认处理 |
| --- | --- | --- |
| 背景、偏好、观察、暂时想法 | `capture_only` | 写入合适文档或 `message-log` 摘要，不派执行任务 |
| 已形成稳定小任务 | `dispatch_needed` | 派给合适泳道；任务带 `discussion_source` 或 `source_message_id` |
| 涉及路线锁定、付费、secret、账号、真实外部调用、远程写入、生产声明 | `confirmation_needed` | 先给用户确认卡，不直接开发 |
| 信息不足且合理假设会跑偏 | `clarify_needed` | 只问最小必要问题，并记录未决点 |

## 部署后必须检查

新项目部署模板后，至少检查：

- `.agents/skills/*/SKILL.md` 是否存在，数量应为 18 个。
- 每个 `SKILL.md` 是否有 frontmatter `name` 和 `description`。
- 每个 `SKILL.md` 是否有“自然语言触发词”“输出”“完成门禁”“打回条件”。
- `.codex/hooks/skill-hooks.md` 是否存在，并包含 18 个 skill。
- `.codex/hooks/skill-hooks.md` 是否包含“讨论场景 Hook 矩阵”。
- `.codex/gates/skill-mechanism-check.ps1` 是否通过。

推荐命令：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-skills.ps1
powershell -ExecutionPolicy Bypass -File scripts\check-framework.ps1
powershell -ExecutionPolicy Bypass -File scripts\check-skill-mechanism.ps1
```

## 改造外部 Skill 的规则

如果从本机或外部引入新 skill，不能直接原样塞进项目。必须先适配：

- 输出文件必须接入当前 GOAL 文档体系，例如 `docs/01-product-spec.md`、`docs/02-design-brief.md`、`docs/03-dev-plan.md`、`docs/05-review-report.md` 或泳道 workspace。
- 不允许另起一套旁路文档体系，让其他泳道读不到。
- 不允许绕过守门直接引入会触发账号、secret、付费、远程写入、真实 provider、生产发布或交易风险的能力。
- 只提升速度、但不能明显提升质量或降低风险的 skill，不进入默认推荐。
- 改造后必须更新 `SKILL-RECOMMENDATIONS.md`、`skill-hooks.md` 和机制门禁。
