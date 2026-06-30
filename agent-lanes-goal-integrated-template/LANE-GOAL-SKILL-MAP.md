# Lane To GOAL Skill Map

这份映射说明 Agent Lanes 和 GOAL skills 如何配合。

| 泳道 | 常用 GOAL skills | 作用 |
| --- | --- | --- |
| 主调度泳道 | `project-orchestrator`, `goal-creator` 按需, `goal-methodology-guide` | 读取项目状态，判断下一步，结构化派发泳道任务，合并 callback，维护节奏。 |
| 规划泳道 | `product-spec-builder`, `dev-planner` 按需, `goal-creator` 按需 | 澄清需求、范围、验收标准；只有跨泳道依赖、阶段顺序或验证方式不清时才补计划/正式 GOAL。 |
| 设计泳道 | `design-brief-builder`, `prototype-builder`, `review-runner` | 形成 UI/UX、交互、页面状态、原型和设计验收标准。 |
| 开发泳道 | `dev-builder`, `bug-fixer`, `gate-runner` | 执行 GOAL、改代码、修缺陷、跑验证。 |
| 守门泳道 | `gate-runner`, `code-reviewer`, `goal-methodology-guide` | 检查权限、secret、外部 API、provider、发布、安全和证据边界。 |
| 验收泳道 | `review-runner`, `code-reviewer`, `gate-runner` | 独立验收目标、实现、风险、测试、文档和新鲜证据。 |
| 进化泳道 | `evolution-runner`, `goal-methodology-guide` | 把重复失败、用户纠正、稳定流程改进沉淀成模板、skill、hook 或门禁规则。 |

## 默认流转

```text
主调度泳道
  -> 并行派发：规划泳道 / 设计泳道 / 守门泳道（无强依赖时）
  -> 合并 completion callback 和 dashboard
  -> 派发开发泳道或补派缺口泳道
  -> 按风险选择聚焦门禁或验收泳道
  -> 进化泳道 only when reusable process signal exists
```

不是每个任务都需要走全链路。低风险任务可以用结构化泳道派发替代正式 `goal-creator`，并用聚焦门禁和主调度合并证据收口；阶段边界、用户可见完成声明、中高风险、证据冲突、权限/数据写入/外部 API/发布时，再进入完整验收。

## 连续讨论协同

用户不需要在需求和技术路线讨论中手动调用某条泳道。主调度每次收到有实质信息的讨论消息，都先做 discussion intake：

- `capture_only`: 背景、偏好、观察或未稳定想法，写入文档或 message-log。
- `dispatch_needed`: 稳定小任务，派给对应泳道，或写 `pending_dispatch` fallback。
- `confirmation_needed`: 路线锁定、产品取舍、真实外部调用、付费、secret、账号、持久写入、券商/交易、生产声明或重型框架采用，先给用户确认卡。
- `clarify_needed`: 信息不足且容易跑偏，只问最小必要问题。

主调度派发讨论产生的任务时，必须带 `discussion_source` 或 `source_message_id`；目标泳道 callback 必须能说明处理的是哪次讨论产生的事项。

### 讨论场景 Hook 矩阵

| 讨论场景 | 优先 Skill | 默认泳道 |
| --- | --- | --- |
| 探讨需求、产品想法、功能取舍、目标用户、先做什么不做什么 | `project-orchestrator` -> `product-spec-builder` | `planning` |
| 探讨计划、阶段路线、优先级、里程碑、下一轮 GOAL | `project-orchestrator` -> `dev-planner`; 目标不清时加 `goal-creator` | `planning` 或 `orchestrator` |
| 探讨技术方案、架构、数据源、开源库、provider/API、模型或能力接入 | `project-orchestrator` -> `dev-planner`; 开源选型用 `open-source-research-runner`; 涉及真实调用/secret/成本时加 `gate-runner` 或 `code-reviewer` | `planning`, `guardian`; 确认后才到 `development` |
| 探讨 UI、页面体验、信息架构、交互状态、面板或原型 | `design-brief-builder`; 前端质量/截图验收用 `frontend-quality-runner`; 需要 demo 时加 `prototype-builder` | `design` |
| 讨论实现、联调、本地验证、脚本、fixture、端到端样本 | `dev-builder`, `bug-fixer`, `systematic-debugging-runner`, `gate-runner` | `development` |
| 讨论验收、完成判断、证据冲突、风险复核、是否可收工 | `review-runner`, `gate-runner`, `code-reviewer` | `review` |
| 讨论机制、模板、hook、skill、泳道协作、重复摩擦或规则进化 | `evolution-runner`, `goal-methodology-guide` | `evolution` |

如果场景涉及路线锁定、真实 provider/API/模型/付费/secret/账号/券商或交易能力，先进入 `confirmation_needed` 或 `guardian`，不得直接派发 `development`。

## 多泳道协作瘦身规则

- Skill 是职责契约，不是固定流水线。
- 主调度可以并行派发互不阻塞的泳道任务。
- `goal-creator` 和 `dev-planner` 是按需工具，不是每次继续的必经站。
- `review-runner` 默认审查主调度聚合后的证据包，不逐条完整审查低风险 callback。
- `gate-runner` 按泳道变更面运行聚焦门禁，不因多泳道存在自动全量门禁。
- 进化泳道只处理真实失败、用户纠正或稳定 signal。

## 质量优先 Skill 候选池

模板默认推荐优先使用能提高质量、减少返工或降低风险的 skill。候选清单见 `SKILL-RECOMMENDATIONS.md`。

- 需求和范围不清时，优先 `product-spec-builder`；需要验收覆盖或需求追踪矩阵时用 `requirements-traceability-runner`。`spec-gathering`、`specalign` 只作为方法补充，不另建旁路文档体系。
- UI/UX、信息架构、页面状态和前端质感不足时，优先 `design-brief-builder` 和 `frontend-quality-runner`。`frontend-quality-runner` 只吸收 `interface-design` 和 `frontend-design` 两个来源；`frontend-ui-ux-engineer` 暂不进默认机制。
- 真实缺陷、测试失败或行为异常时，优先 `bug-fixer` 和 `systematic-debugging-runner`，先定位根因再修复。
- 用户可见 UI 闭环或浏览器行为需要验证时，优先 `playwright` 或 `e2e-testing`。
- 高风险、跨模块、阶段边界、发布前或用户可见完成声明，优先 `code-reviewer` 和 `review-runner`。
- 开源库、provider、指标库、回测框架、图表库或外部实现选型时，使用 `open-source-research-runner`；原始 `github-research` 或同类开源分析 skill 只作为临时深挖工具。引入代码前必须检查 license、维护度和守门边界。
- 只有现有 skill 不能覆盖明确质量缺口时，才用 `skill-finder` 搜索外部候选；搜索结果必须先复核文档，不因安装量高就直接进入默认流程。

只提升操作速度、但不能明显提升质量或降低风险的 skill，不进入默认推荐。会引入账号、secret、付费、远程写入、真实 provider 或重型框架的 skill，必须先走守门泳道或用户确认。

## Dispatch Queue / 单泳道任务锁

- 同一泳道同一时间只能有一个 active dispatch；未收到匹配 `reply_to` 的 completion callback 前，该泳道视为 busy。
- 主调度不得向 busy 泳道继续 `send_message_to_thread`。新任务、补充上下文和返工要求必须写成 `queued_dispatch` 或 `context_patch`。
- queued 记录必须说明 `target_lane`、`blocked_by_active_dispatch`、`source_message_id`/`reply_to`、`summary`、`context_files` 和 `created_at`。
- active dispatch 完成后，主调度先合并该泳道队列，再发送一条完整的新任务。
- 并行派发只允许发生在不同泳道、互不强依赖、且目标泳道都不 busy 的情况下。

## Callback Inbox / 主调度收件箱

- 完整 completion callback 的用户可读主通道是回报邮局生成的 `thread_prompt`；`agent-lanes/message-log.jsonl` 只作为审计备份。
- 非主调度泳道完成后先写 worklog，再调用 `agent-lanes/scripts/deliver_callback.py` 投递完整 callback。
- 默认不由单泳道发送短 wake。回报邮局必须生成一条完整 `thread_prompt`；脚本输出 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 后，泳道只发送这一条合并后的原文消息，不得逐条发送“某泳道完成，请去收件箱看”。
- 如果脚本返回 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log` 记录，说明回报尚未真正送达；泳道必须重跑投递或记录阻塞，不能让主调度去 message-log 自取原文。
- drain 时按 `message_id` 去重，必要时按 `reply_to + from_agent + task_type` 折叠；同一轮 batch 统一路由，不被新 callback 中途改写。
- 这条规则防止单泳道 callback 打断主调度正在进行的合并、计划刷新、用户确认或下一步派发。

## Sketch Plan Loop / 骨架计划循环

多泳道协作默认使用骨架优先推进：

```text
Plan Refresh -> Thin Slice Execute -> Focused Verify -> Dashboard/Docs Merge -> 下一刀
```

触发条件：

- 用户说完成度、太慢、整体推进、计划、项目还差什么、骨架、先打通、全链路。
- 最近 3-5 个 GOAL 都在同一局部能力里。
- 同一 provider/capability 连续推进 2-3 个 GOAL。
- capability registry 有很多 evidence，但没有形成用户可操作流程。
- 当前 Next GOAL 只是 wrapper、readiness、operator decision、readonly surface、handoff proposal 或 apply readiness。

泳道分工：

- 主调度泳道：判断是否需要 Skeleton Plan Refresh。
- 规划泳道：维护产品骨架路线，输出 Skeleton Pass、Real Pass、Quality Pass、Production Pass 和 3-6 个最高价值薄纵向切片。
- 开发泳道：只执行骨架计划里的下一刀，说明补哪条骨架环节和下一个非同能力节点。
- 守门泳道：卡真实 provider/API/secret/账号/成本/交易/外部写入边界。
- 验收泳道：检查产物是否让骨架更接近端到端可运行。

## GOAL 文档写入归属

泳道的运行态 `write_scope` 必须和 GOAL root docs 归属一致：

- 规划泳道写 `docs/01-product-spec.md` 和 `docs/03-dev-plan.md`。
- 设计泳道写 `docs/02-design-brief.md`。
- 守门泳道写 `docs/capability-status.json` 和 `docs/capability-provider-contract.md`。
- 验收泳道写 `docs/05-review-report.md` 和 `docs/06-release-record.md`。
- 进化泳道写 Agent Lanes / GOAL 模板规则目录，不写业务实现代码。

如果主调度派发的需求路由任务要求目标泳道写这些文件，派发前必须确认 `agent-lanes/agent-registry.json` 和 `agent-lanes/agent-lanes.md` 已覆盖对应路径。

## 完成回报要求

任何非主调度泳道完成主调度派发任务后，都必须：

1. 追加写本泳道 `worklog.md` 末尾，保持时间从旧到新。
2. 生成 completion callback JSON。
3. 调用 `agent-lanes/scripts/deliver_callback.py` 投递给回报邮局；`message-log` 只作为审计备份。
4. 默认不由单泳道提醒主调度。邮局必须合批生成一条 `thread_prompt`；只有脚本输出 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 后，泳道才发送这一条合并后的原文消息。`send_required=false`、`spooled_waiting`、`spooled` 或 `batched_log` 均视为未完成投递。
5. 在最终回复里保留 `status`、`evidence`、`next_recommended_lane`。

没有 completion callback 的任务，主调度应视为交接未完成。

沟通语言默认中文优先：`summary`、`concerns`、`next_recommended_action`、worklog 正文、dashboard 展示文本和线程回复正文尽量用中文；`status`、`task_type`、`message_id`、`thread_id`、文件路径、命令、API 名、JSON key 和错误原文保留英文或原文。

Dashboard、主调度和验收泳道读取 callback 时必须去重：优先按 `message_id`，必要时按 `reply_to + from_agent + task_type` 折叠重复 fallback。需求路由 smoke test 的验收必须刷新并查看 `agent-lanes/dashboard.md`，否则最高只能给 `DONE_WITH_CONCERNS`。

