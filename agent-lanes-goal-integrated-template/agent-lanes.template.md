# Agent Lanes

本文件记录长期职责泳道。Agent 线程可以替换，但 Lane 的职责、读写范围、日志和工作区应保持稳定。

线程标题和泳道显示名尽量使用中文，不加项目名前缀；项目名、模块名放在任务上下文和文档里。

## 泳道清单

| lane | 中文名 | purpose | current_session | write_scope | read_scope | worklog | workspace | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| orchestrator | 主调度泳道 | 读状态、判断下一步、派发结构化任务、合并 callback、刷新 dashboard、维护全局状态 | codex:TODO | `agent-lanes/`, `docs/` | 全项目只读 | `agent-lanes/lanes/orchestrator/worklog.md` | `agent-lanes/lanes/orchestrator/workspace/` | active |
| planning | 规划泳道 | 产品目标、阶段范围、优先级、验收标准、任务切片、需求变更落档 | codex:TODO | `docs/01-product-spec.md`, `docs/03-dev-plan.md`, `agent-lanes/lanes/planning/` | `docs/`, `agent-lanes/`, `<PRIMARY_MODULE>/` 只读 | `agent-lanes/lanes/planning/worklog.md` | `agent-lanes/lanes/planning/workspace/` | active |
| design | 设计泳道 | 前端页面设计、信息架构、用户路径、交互状态、视觉规范、设计验收标准 | codex:TODO | `docs/02-design-brief.md`, `agent-lanes/lanes/design/` | `docs/`, `agent-lanes/`, `<PRIMARY_MODULE>/` 只读 | `agent-lanes/lanes/design/worklog.md` | `agent-lanes/lanes/design/workspace/` | active |
| development | 开发泳道 | 按已批准目标实现、修复、运行验证、提交变更文件和证据 | codex:TODO | `<PRIMARY_MODULE>/`, `tests/`, `docs/04-goal-log.md`, `agent-lanes/lanes/development/` | `docs/`, `agent-lanes/`, `<PRIMARY_MODULE>/`, `tests/` | `agent-lanes/lanes/development/worklog.md` | `agent-lanes/lanes/development/workspace/` | active |
| guardian | 守门泳道 | 检查权限、隐私、secret、外部 API、AI/付费调用、真实写入、发布和平台风险 | codex:TODO | `docs/capability-status.json`, `docs/capability-provider-contract.md`, `agent-lanes/lanes/guardian/` | `docs/`, `agent-lanes/`, `<PRIMARY_MODULE>/` 只读 | `agent-lanes/lanes/guardian/worklog.md` | `agent-lanes/lanes/guardian/workspace/` | active |
| review | 验收泳道 | 独立验收规划、设计、开发和守门结果，检查目标、标准、风险和新鲜证据 | codex:TODO | `docs/05-review-report.md`, `docs/06-release-record.md`, `agent-lanes/lanes/review/` | 全项目只读 | `agent-lanes/lanes/review/worklog.md` | `agent-lanes/lanes/review/workspace/` | active |
| evolution | 进化泳道 | 沉淀重复失败、调整 Skill 边界、改进模板、同步可复用规则 | codex:TODO | `.agents/`, `.codex/`, `docs/agent-lanes-goal-integrated-template/`, `agent-lanes/lanes/evolution/` | `docs/`, `agent-lanes/`, `.agents/`, `.codex/` | `agent-lanes/lanes/evolution/worklog.md` | `agent-lanes/lanes/evolution/workspace/` | paused |

## 使用规则

- `current_session` 必须对应当前负责该 Lane 的 Codex thread id 或 deep link；线程工具不可用时写 `pending_setup`，不要伪造 thread id。
- `write_scope` 只表示默认可写范围；涉及高风险、secret、真实数据写入、真实付费调用或发布时仍需用户批准。
- 一个 Lane 可以暂时没有线程，但必须标记 `pending_setup`。
- 替换线程时，只更新 `current_session`，不要改变 Lane 名称和职责。
- 每个 Lane 的工作必须写入对应 `worklog`，中间产物放入对应 `workspace`。
- 非主调度泳道完成任务后必须执行 completion callback：先写本泳道 worklog，再生成 callback JSON，并调用 `agent-lanes/scripts/deliver_callback.py` 投递给回报邮局；只有脚本返回 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 时，才把这一条合并原文发给主调度线程。`message-log.jsonl` 只作为审计备份；`send_required=false`、`spooled_waiting`、`spooled` 或 `batched_log` 不算送达。
- 平时优先打开 `agent-lanes/dashboard.md` 看全局状态；刷新命令：`python agent-lanes\scripts\render_dashboard.py`。
- 完整收发记录只生成并优先打开 `agent-lanes/communications-readable.xlsx`；机器审计和 raw 字段追溯使用 `message-log.jsonl`，不再额外导出 CSV。
- 泳道沟通默认中文优先；`status`、`task_type`、`message_id`、`thread_id`、`file path`、命令、API 名和 JSON key 保留英文或原文。

## 默认推进方式

主调度收到用户需求后，优先判断最短产品纵向闭环，而不是机械串行运行所有 GOAL Skill。

- 需求、目标、验收标准不清：派给 `planning`。
- 涉及页面、交互、视觉、信息架构：派给 `design`。
- 涉及实现、修复、本地验证：派给 `development`。
- 涉及权限、外部 API、付费、真实写入、隐私、发布：派给 `guardian`。
- 阶段边界、交付判断、证据冲突或高风险变更：派给 `review`。
- 重复失败、规则膨胀、模板复用、Skill 边界需要调整：派给 `evolution`。

低风险任务可用结构化泳道任务替代正式 GOAL；跨泳道依赖、阶段顺序、联调路线、风险或回滚不清时再使用更重的 GOAL 规划。

## Sketch Plan Loop / 骨架计划循环

主调度泳道要先维护产品全链路骨架，再派发局部开发任务。通用骨架链路是：

```text
用户输入
-> 数据/素材进入
-> 处理/生成
-> 人工审核
-> 组合/编排
-> 输出/渲染
-> 报告/交付
```

当用户说完成度、太慢、整体推进、计划、项目还差什么、骨架、先打通、全链路，或最近 3-5 个 GOAL 都集中在同一局部能力时，主调度先派 `planning` 做 Skeleton Plan Refresh，而不是继续派 `development` 深挖局部 capability。

泳道职责：

- `orchestrator`: 判断本轮是直接执行，还是先 Plan Refresh；若派发任务，必须说明它补哪条骨架环节。
- `planning`: 维护 Skeleton Pass、Real Pass、Quality Pass、Production Pass，并给出 3-6 个最高价值薄纵向切片。
- `development`: 只执行计划中的下一刀；开发前说明补哪条骨架链路，完成后说明下一个非同能力骨架节点。
- `guardian`: 只在真实 provider/API/账号/成本/受监管操作/高风险自动化执行/外部写入等风险处卡边界，不把普通准备壳层变成独立阶段。
- `review`: 阶段边界检查骨架是否更接近端到端可运行，而不只检查文件是否有改动。
- `evolution`: 当系统再次陷入局部深挖或骨架判断缺失时，沉淀规则。

推荐节奏：

```text
Plan Refresh -> Thin Slice Execute -> Focused Verify -> Dashboard/Docs Merge -> 下一刀
```

小切片跑聚焦门禁；阶段边界再做合并审查；高风险才完整审查。

## 连续讨论协同模式

用户持续讨论需求、技术路线、判断、担心、偏好或临时想法时，主调度不能要求用户每次手动指定某条泳道。每条有实质信息的用户消息都先做讨论 intake，并归入四类：

- `capture_only`: 背景、偏好、观察或仍不稳定的想法。写入合适文档或 message-log，不派发执行任务。
- `dispatch_needed`: 已经形成稳定小任务。派给合适泳道；线程工具不可用时写 `pending_dispatch` fallback。
- `confirmation_needed`: 涉及路线锁定、产品取舍、真实外部调用、付费、secret、账号、持久写入、受监管操作/高风险自动化执行、生产声明或重型框架采用。先给用户确认卡，不派发产品化开发。
- `clarify_needed`: 信息不足且合理假设会明显跑偏。只问最小必要问题，并把未决点写入 message-log 或对应文档。

讨论 intake 的最低动作：

- 判断消息新增了什么：新需求、需求修改、技术路线判断、资料线索、风险意见、优先级变化、验收标准变化或机制反馈。
- 决定落档位置：`docs/01-product-spec.md`、`docs/02-design-brief.md`、`docs/03-dev-plan.md`、`docs/09-research-roadmap.md`、`docs/capability-status.json`、provider card、`agent-lanes/message-log.jsonl` 或泳道 worklog。
- 不派发时说明原因；派发时带 `discussion_source` 或 `source_message_id`，让后续 callback 能追溯。
- 最终回复必须明确：本轮是已记录、已派发、需要确认，还是需要澄清。

### 讨论场景 Hook 矩阵

| 讨论场景 | 主调度优先调用的 Skill | 默认派发泳道 | 默认落档位置 | 何时派发 |
| --- | --- | --- | --- | --- |
| 探讨需求、产品想法、功能取舍、目标用户、先做什么不做什么 | `product-spec-builder` | `planning` | `docs/01-product-spec.md`, `docs/03-dev-plan.md` | 形成稳定需求切片、验收标准或产品边界时 |
| 探讨计划、阶段路线、优先级、里程碑、下一轮 GOAL | `dev-planner`; 目标不清时加 `goal-creator` | `planning` 或 `orchestrator` | `docs/03-dev-plan.md`, `docs/04-goal-log.md` | 需要拆任务、定阶段、改优先级或建立 GOAL 时 |
| 探讨技术方案、架构、数据源、开源库、provider/API、模型或能力接入 | `dev-planner`; 涉及真实调用/secret/条款/成本时加 `gate-runner` 或 `code-reviewer` | `planning`, `guardian`; 确认后才到 `development` | `docs/09-research-roadmap.md`, `docs/13-l1-l5-information-source-architecture.md`, `docs/14-market-candidate-classification.md`, `docs/capability-status.json`, provider card | 低风险调研可派规划；真实 provider/API/模型/付费/账号/受监管操作/高风险自动化执行能力必须先进守门 |
| 探讨 UI、页面体验、信息架构、交互状态、面板或原型 | `design-brief-builder`; 需要 demo 时加 `prototype-builder` | `design` | `docs/02-design-brief.md` | 有明确页面、用户路径或状态覆盖要求时 |
| 讨论实现、联调、本地验证、脚本、fixture、端到端样本 | `dev-builder`, `bug-fixer`, `gate-runner` | `development` | `scripts/`, `artifacts/`, `<PRIMARY_MODULE>/`, `docs/03-dev-plan.md`, `docs/capability-status.json` | 需求、边界和风险都清楚时；否则先规划或守门 |
| 讨论验收、完成判断、证据冲突、风险复核、是否可收工 | `review-runner`, `gate-runner`, `code-reviewer` | `review` | `docs/05-review-report.md`, `agent-lanes/dashboard.md` | 已有产物或 callback 需要独立核对时 |
| 讨论机制、模板、hook、skill、泳道协作、重复摩擦或规则进化 | `evolution-runner`, `goal-methodology-guide` | `evolution` | `.codex/hooks/`, `.agents/skills/`, `agent-lanes/agent-lanes.md`, `docs/agent-lanes-goal-integrated-template/` | 用户明确要求优化机制，或多次流程摩擦暴露可复用规则缺口时 |

主调度要把“当前线程调用 Skill”和“其他泳道真正参与”分开处理：调用 Skill 后仍需结构化派发，派发任务必须带 `discussion_source` 或 `source_message_id`；如果线程工具不可用，写入 `pending_dispatch` fallback，并在 dashboard 可见。

## Dispatch Queue / 单泳道任务锁

Codex 线程不是可靠的多消息队列。主调度不能在同一目标泳道仍有未完成任务时继续 `send_message_to_thread` 追加新任务或补充上下文；否则会打断该泳道正在执行的任务，造成回复截断、上下文覆盖和半成品堆积。

规则：

1. 同一泳道同一时间只能有一个 `active_dispatch`。
2. 主调度派发前必须检查 `agent-lanes/message-log.jsonl`：若目标泳道最新 dispatch 尚无匹配 `reply_to` 的 completion callback，则该泳道 busy。
3. busy 时不得继续发线程消息，只能写 `queued_dispatch` 或 `context_patch` 到 `message-log.jsonl`。
4. 目标泳道 callback 后，主调度合并该泳道 queued/context_patch，生成一条完整派发包，再发送下一条任务。
5. 并行派发只允许发生在不同泳道、互不强依赖、且每个目标泳道都不 busy 的情况下。

`queued_dispatch` 至少包含：`message_id`、`target_lane`、`blocked_by_active_dispatch`、`source_message_id` 或 `reply_to`、`summary`、`context_files`、`created_at`、`status: queued_dispatch`。

## Callback Inbox / 主调度收件箱

Codex 线程不是主调度的可靠中断队列。单条泳道 callback 不得把完整回报直接插入主调度线程，避免打断主调度正在进行的合并、派发、计划刷新或用户确认。

规则：

1. 完整 completion callback 的用户可读主通道是回报邮局生成并发送到主调度线程的单条 `thread_prompt`。
2. `agent-lanes/message-log.jsonl` 只作为审计备份和异常查证入口，不是主调度默认收件箱。
3. 非主调度泳道完成后先写 worklog，再调用 `agent-lanes/scripts/deliver_callback.py` 投递完整 callback。
4. 只有脚本返回 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 时，泳道才发送这一条合并后的原文消息；不得发送短 wake，也不得要求主调度去 message-log 自取原文。
5. 如果脚本返回 `send_required=false`、`spooled_waiting`，或只生成 `spooled` / `batched_log` 记录，说明回报尚未真正送达；泳道必须重跑投递或记录阻塞。
6. 主调度收到 `【邮局合并回报】` 后直接处理；只有证据冲突、疑似重复、门禁报错、需要审计或用户要求追溯时，才按 `message_id` 或 `reply_to + from_agent + task_type` 去重查证。

推荐 callback 审计记录使用 `delivery_mode: direct_thread_prompt_ready`；历史 `log_only`、`wake_only`、`direct_legacy` 只能作为迁移期记录。

泳道完成任务时应优先使用统一投递脚本，而不是自己手写轮询逻辑：

```powershell
python agent-lanes\scripts\deliver_callback.py `
  --callback-file agent-lanes\lanes\<lane>\workspace\completion-callback.json `
  --poll-interval-seconds 60
```

脚本先把完整 callback 放进 `agent-lanes/callback-inbox/pending/` 暂存，并在 message-log 追加一条小的 `callback_spooled` 收据；随后立即运行一次邮局合批，生成 `callback_batch_ready`、`thread_prompt`、`target_thread_id` 和 `outbox_path`。只有脚本返回 `send_required=true` 且带完整 `thread_prompt`，本次回报才算可投递；泳道必须把这一条 `thread_prompt` 原样发送给主调度线程。若返回 `send_required=false`、`spooled_waiting`，或只生成 `spooled` / `batched_log`，说明尚未真正送达，必须重跑投递或记录阻塞。

### Post Office Gate / 邮局门禁

模板建议提供轻量检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts\check-agent-lanes-post-office.ps1
```

默认只报告 `PASS` / `WARN` / `FAIL`，不因为历史旧记录阻塞开发。它检查绕过邮局的直接 callback、未被 batch 覆盖的 spooled 记录、pending 过久未投递和邮局状态文件。需要严格模式时设置 `AGENT_LANES_POST_OFFICE_STRICT=1`。

## 邮局合并投递与 Dashboard 可读性

用户纠正的稳定规则：回报邮局不能把同一批 callback 拆成多条 wake 发进主调度线程。每轮投递必须把当前批次的多条泳道回报整合成一条完整消息，直接包含原文摘要、证据、风险和下一步建议。

执行规则：

1. 非主调度泳道完成后统一调用 `agent-lanes/scripts/deliver_callback.py`，只把完整 callback 投递到 `agent-lanes/callback-inbox/pending/`，不得自己拼短 wake 去打断主调度。
2. `agent-lanes/scripts/callback_post_office.py` 不得把 pending callback 移出暂存，除非同一批次已经生成可发送的完整 `thread_prompt`、`target_thread_id` 和 `outbox_path`。
3. `callback_batch_ready` 必须包含 `thread_prompt`、`target_thread_id` 和 `outbox_path`。工具层只能发送这一条合并后的 `thread_prompt`，不得逐条发送“某泳道完成，请去收件箱看”。
4. 合并消息正文必须让主调度不用打开收件箱也能判断：谁完成了、状态是什么、原文摘要是什么、证据在哪里、风险是什么、建议下一步是什么。
5. `agent-lanes/dashboard.md` 是人类主控台，不是机器日志视图。主视图应优先展示忙闲、邮局批次、泳道状态、摘要、风险和建议动作；长 `message_id`、`thread_id`、脚本路径和原始 JSON 只放到“排查入口”或结构化日志中。
6. `agent-lanes/communications-readable.xlsx` 是完整收发记录的唯一用户表格视图，必须保留中文表头、冻结首行、筛选、合理列宽、自动换行和质量状态颜色；raw 审计视图继续使用 `message-log.jsonl`，不要再生成 CSV 副本。

这条规则优先于旧的轻量 wake 规则。旧规则中的“只发 message_id + inbox_path”只适用于没有邮局合并能力的历史兼容场景；当前模板默认使用“邮局合并原文信”。
