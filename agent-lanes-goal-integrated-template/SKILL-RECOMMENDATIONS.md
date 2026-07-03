# Skill 使用建议模板

本文件随 Agent Lanes + GOAL 模板一起复制到新项目，用于指导主调度选择高质量 skill。

原则：优先使用能提高需求清晰度、设计质量、验证质量、审查质量和开源选型质量的 skill；只提高执行速度但不能明显提高质量或降低风险的 skill，不进入默认推荐。

## 推荐类别

| 场景 | 推荐 skill | 使用理由 | 默认泳道 |
| --- | --- | --- | --- |
| 需求拆解、范围取舍、验收标准 | `product-spec-builder`, `spec-gathering`, `specalign` | 把模糊想法变成可开发、可验收、可传递的需求。 | 规划泳道 |
| 需求到设计/代码/测试追踪 | `requirements-traceability-runner` | 已吸收需求追踪方法，固定回写 `docs/05-review-report.md` 或泳道 workspace。 | 规划泳道、验收泳道 |
| UI/UX、信息架构、页面状态 | `design-brief-builder`, `frontend-quality-runner` | 已只吸收 `interface-design` 和 `frontend-design` 两个最值得的前端设计方法；设计写回 `docs/02-design-brief.md`，验收写回 `docs/05-review-report.md`。 | 设计泳道、验收泳道 |
| 无设计稿但需要高质量前端 | `frontend-quality-runner` | 适合把功能页面提升为清晰、可用、有质感的工具型/工作台界面。 | 设计泳道、开发泳道、验收泳道 |
| 复杂阶段计划、骨架刷新、纵向切片 | `dev-planner`, `goal-creator` 按需 | 当下一刀、依赖顺序、风险或完成标准不清时使用。 | 主调度泳道、规划泳道 |
| 真实缺陷、测试失败、异常行为 | `bug-fixer`, `systematic-debugging-runner` | 先复现、追数据流、验证单一假设，再最小修复并同路径回归。 | 开发泳道、验收泳道 |
| 泳道线程崩溃、过长或无法提交消息 | `lane-recovery-runner` | 按持久化运行态文件完成新线程创建、瘦身健康检查、registry 替换、旧线程归档、二次故障归档和审计记录，避免靠聊天记忆接管或用过重提示压垮新线程。 | 主调度泳道、进化泳道 |
| 浏览器可见 UI 验证 | `playwright`, `e2e-testing` | 用真实浏览器检查导航、页面状态、用户路径、截图和关键回归。 | 开发泳道、验收泳道 |
| 门禁、证据、能力状态 registry | `gate-runner`, `implementation-verify` 按需 | 把可程序化判断的完成条件变成命令证据。 | 守门泳道、验收泳道 |
| 代码级独立审查 | `code-reviewer`, `review-runner` | 高风险、跨模块、阶段边界、发布前或用户可见完成声明需要第二视角。 | 验收泳道 |
| 开源库/实现/资源调研 | `open-source-research-runner` | 已吸收 GitHub/开源分析方法，固定写入开源候选池、研究路线或守门 workspace。 | 规划泳道、守门泳道 |
| 指标、仪表盘、可视化质量 | `data-analytics:design-kpis`, `data-analytics:visualize-data`, `data-analytics:build-dashboard` | 适合设计 KPI、评分解释、报告图表和 dashboard。 | 设计泳道、验收泳道 |
| 流程规则、模板、hook 进化 | `evolution-runner`, `skill-finder`, `skill-creator` 按需 | 把真实失败、用户纠正或稳定流程缺口沉淀成模板、skill 或门禁。 | 进化泳道 |

## 外部 skill 引入规则

模板包已内置 5 个本地化增强 skill：`requirements-traceability-runner`、`frontend-quality-runner`、`open-source-research-runner`、`systematic-debugging-runner`、`lane-recovery-runner`。其中 `frontend-quality-runner` 只吸收 `interface-design` 和 `frontend-design` 两个前端设计来源，`lane-recovery-runner` 用于泳道线程恢复接管。新项目默认先用这些落在目标项目 `.agents/skills/` 的本地化版本；原始外部 skill 和公共 skill 只作为方法来源或深挖补充，不能作为项目机制 skill 的最终安装位置。

维护项目机制运作的 skill 创建规则：

- 默认创建到当前项目 `.agents/skills/<skill-name>/`。
- 同步维护 `.codex/hooks/skill-hooks.md`、`.codex/gates/skill-mechanism-check.ps1` 和模板包 `goal-development-base/.agents/skills/`。
- 不要把项目机制 skill 安装到公共目录；公共目录中的 skill 只用于学习方法、读取说明或调用系统验证器。

使用 `skill-finder` 时，先运行：

```powershell
npx -y skills find "<keywords>"
```

外部候选必须先复核文档、安装命令、适用边界和与本项目模板的冲突，再决定是否安装。不要因为安装量高就默认加入主流程。

使用 `open-source-research-runner` 或临时补充 `github-research` 时，适合开源库、论文实现、provider、回测/图表/数据处理库选型。默认要求：

- `gh` CLI 已安装并已认证。
- 允许网络访问和浅克隆仓库。
- 输出 integration blueprint、license 风险和复用边界，并写回模板约定的研究/守门文档。
- 不得直接复制外部代码进项目；必须先走守门泳道或用户确认。

## 暂不默认推荐

- 只提高操作速度但不提升质量的通用自动化 skill。
- 会引入额外平台、账号、远程写入或重型工作流的 skill。
- 与当前项目域无关的 skill，除非用户明确要求进入该场景。
