---
name: project-orchestrator
description: 当用户提到下一步、继续、接着做、往下推进、自动推进、轻量继续、高速产品工程经理、综合调用、总调度、根据当前项目状态决定做什么、继续闭环、推进项目、从当前状态开始、按 GOAL 流程继续、接手继续、你自己判断下一步、自动往后走、别问我先看项目、需求讨论、路线讨论、技术路线、我有个想法、我觉得、我们讨论一下、持续迭代、自动落档、脱手、自主迭代、自动规划、自动落实、callback hook、callback 打断主调度、主调度被打断、主调度收件箱、callback inbox、前端后端怎么推进、前后端联调、前端后端分流、分层推进、多泳道协作、并行泳道、泳道派发、真实接入、外部 API 接入、模型接入、Provider 接入、能力状态 registry、单能力聚焦预算、capability exit check、provider 深挖收敛、Sketch Plan Loop、骨架计划循环、骨架优先、Product Loop First、用户闭环优先、持续交付可用产品、先打通可用闭环、不要证明每个零件安全、完成度、太慢、整体推进、项目还差什么、全链路扫描、中文文档、文档中文、项目文档中文优先时，使用这个 Skill 读取当前项目状态并选择合适的本地 Skill 工作流推进任务。
---

# 项目总调度器

## 核心契约

把用户的一句“下一步”或“继续”变成一次有证据的项目推进。

先读项目状态，再判断当前最缺的闭环环节，最后按对应本地 Skill 的契约执行。不要跳过需求、设计、计划、GOAL、验证、审查、文档和发布记录之间的必要顺序。

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、GOAL log、review/release/report 正文或模板说明时，默认写中文。专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文和外部引用标题可以保留英文或原文。派发泳道任务时必须带上 `language_rule: 项目文档中文优先`，并要求目标泳道的 summary、concerns、next action 和文档正文尽量中文。

## 自然语言触发词

- 下一步
- 继续
- 接着做
- 往下推进
- 自动推进
- 轻量继续
- 高速产品工程经理
- 综合调用
- 总调度
- 根据当前项目状态决定做什么
- 继续闭环
- 推进项目
- 从当前状态开始
- 按 GOAL 流程继续
- 接手继续
- 你自己判断下一步
- 自动往后走
- 别问我先看项目
- 需求讨论
- 路线讨论
- 技术路线
- 我有个想法
- 我觉得
- 我们讨论一下
- 持续迭代
- 自动落档
- 脱手
- 自主迭代
- 自动规划
- 自动落实
- callback hook
- callback 打断主调度
- 主调度被打断
- 主调度收件箱
- callback inbox
- 前端后端怎么推进
- 前后端联调
- 前端后端分流
- 分层推进
- 多泳道协作
- 并行泳道
- 泳道派发
- 真实接入
- 外部 API 接入
- 模型接入
- Provider 接入
- 能力状态 registry
- 单能力聚焦预算
- capability exit check
- provider 深挖收敛
- Sketch Plan Loop
- 骨架计划循环
- 骨架优先
- Product Loop First
- 用户闭环优先
- 持续交付可用产品
- 先打通可用闭环
- 不要证明每个零件安全
- 完成度、太慢、整体推进、项目还差什么、全链路扫描
- 中文文档、文档中文、项目文档中文优先、所有文档用中文

## 启动检查

默认使用“轻量继续模式”。只有在状态冲突、阶段切换、高风险、发布/交付、用户要求复盘、文档缺失、判断不清、用户反馈与状态文档不一致或 registry 证据过期时，才升级为完整复盘模式。

### V2 执行内核唯一事实源

自动推进的机器事实只来自四处：`agent-lanes/current-state.json`、`agent-lanes/value-slice-ledger.jsonl`、`Product Value Gate` 和 `Value Delta Gate`。`AGENTS.md`、本 Skill、GOAL log、历史 callback 和泳道建议负责解释与审计，不得覆盖这四个运行态结论。出现冲突时 fail closed，并把冲突写入检查点；不要再用文件末尾“高优先级覆盖旧规则”的方式叠加补丁。

轻量继续模式优先读取：

- `agent-lanes/current-state.json`：V2 当前价值切片、阻塞、backlog 和调度策略的最小事实源。
- `agent-lanes/dashboard.md`：只读当前运行状态，不默认展开 `dashboard-full.md`。
- `docs/product-feature-status.json`：判断用户可见产品能力；UI consumer/handoff 不再进入 capability registry。
- `docs/capability-status.json`：仅在当前切片涉及模型、Provider、CLI、执行引擎、授权或外部 API 时读取。
- `docs/capability-provider-contract.md`，若当前切片涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider。
- 与当前 `Current active slice` 或 `Next GOAL` 直接相关的代码、README、fixture、evidence 或测试文件。

`docs/03-dev-plan.md`、`docs/04-goal-log.md`、`docs/05-review-report.md` 和 `agent-lanes/message-log.jsonl` 是历史/审计输入；只有当前状态冲突、阶段边界、证据追溯或完整复盘时才打开，不能再作为每次“继续”的默认大上下文。

完整复盘模式再读取这些文件，缺失时把缺失本身作为当前问题处理：

- `docs/00-project-state.md`
- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/05-review-report.md`
- `docs/06-release-record.md`
- `docs/capability-status.json`
- `.codex/hooks/skill-hooks.md`

检查 `.codex/signals/`，但不要因为存在文件就每次触发 `evolution-runner`。只有满足“自进化触发规则”时才切换到自进化；否则继续按当前项目阶段推进。

## Sketch Plan Loop / 骨架计划循环

默认推进要先维护产品全链路骨架，再逐层加深。主调度不能只因为某个局部 capability 仍有 wrapper、readiness、operator decision、readonly surface 或 handoff proposal 可做，就继续围绕它深挖。

当出现以下情况时，不直接进入 `dev-builder`，先触发 `dev-planner` 做一次 Skeleton Plan Refresh：

- 用户说“完成度、太慢、整体推进、计划、项目还差什么、骨架、先打通、全链路”。
- 用户只说“继续”，但最近已经连续推进 3-5 个 GOAL，且缺少新的全链路判断。
- 同一 provider/capability 已经连续推进 2-3 个 GOAL。
- 当前 Next GOAL 只是局部壳层、evidence、decision、readonly surface、handoff proposal 或 apply readiness。
- `docs/capability-status.json` 很多能力已有 evidence，但没有形成用户可操作流程。
- 当前计划只剩细节，但产品仍不能端到端跑，或文档里的下一步看起来过窄、过旧。

Skeleton Plan Refresh 至少扫描目标项目定义的产品骨架。通用示例：

```text
用户入口 / 对象选择
-> 数据源接入
-> 标准化数据 artifact
-> 核心计算、分析或业务规则
-> 解释、评分、推荐或决策辅助
-> 前端工作台 / 操作入口
-> 验证实验或预演
-> 内部模拟执行 / 结果看板
-> 报告 / 复盘
-> 发布、交付或高风险外部执行评估
```

刷新时必须回答：

- 哪一环是空白。
- 哪一环只有假数据或 fixture。
- 哪一环只有后端没有前端。
- 哪一环只有前端没有真实执行。
- 哪一环已经 current-stage-good-enough，应暂停深挖。
- 接下来 3-6 个最高价值薄纵向切片是什么。

推进节奏：

- 每执行 3 个 GOAL，做一次轻量 Skeleton Plan Refresh。
- 每执行 5-6 个 GOAL，做一次完整骨架扫描。
- 如果当前计划仍新鲜且下一刀明确，继续执行下一刀。
- 如果计划过期、局部过深、用户觉得慢，先计划刷新再执行。
- 门禁仍保留，但用于防止坏东西进入骨架：小切片跑聚焦门禁，阶段边界做合并审查，高风险才完整审查。

### Stage Value Gate / 阶段价值门槛

派发前先做阶段价值判断。不要把“能做的小闭环”误判成“当前最该做的主线”。模板默认优先级：

- `P1`: 目标项目在 `docs/01-product-spec.md` 或 `docs/03-dev-plan.md` 中定义的核心用户闭环。
- `P2`: 页面骨架、导航、面板关系、按钮动作、信息密度、跳转路径。
- `P3`: 数据质量、真实样本、source quality blocker、关键字段可信度。
- `P4`: 备注保存、导出、写回、长期存档等辅助能力，默认 backlog / session_only。
- `P5`: 云同步、远程写入、scheduler、受监管操作、高风险自动执行和生产承诺，默认守门/授权队列。

每次派发前必须写清 `stage_priority`、`why_now`、`mainline_impact` 和 `deferred_items`。P4/P5 只有在阻塞 P1/P2 时才能成为下一刀；否则只记录 backlog，不向用户发确认卡，不派开发泳道。

### Agent Lanes V2 / Value Slice Gate

多泳道的最小调度单位是 `Value Slice`，不是 capability、artifact、consumer、handoff、checkpoint 或页面镜像。新派发必须基于 `agent-lanes/value-slice.template.json`，至少回答：

- `user_outcome`：用户最终获得什么结果。
- `new_user_action`：本轮新增或恢复哪个可观察动作。
- `expected_value_delta`：`new_user_action`、`blocker_removed`、`quality_confidence` 或 `risk_reduction`。
- `primary_surface`：唯一完整承载能力的入口。
- `supporting_surfaces`：其它入口只能是 `link_or_summary`，不得复制完整卡片。
- `review_policy` 与 `callback_budget`：一个 Value Slice 最多 3 次正式泳道回报。
- `completion_gate_required=true`：切片完成必须提交 `agent-lanes.value-slice-completion.v1` 并通过 Value Delta Gate。
- `next_step_policy=advisory_only`：泳道的下一步建议不能直接触发派发。

派发前必须运行：

```powershell
python agent-lanes/scripts/product_value_gate.py --dispatch-file <dispatch.json> --record-dispatch
```

门禁失败时不得调用 `send_message_to_thread`，不得用 callback 建议、旧计划或“主线自动续航”绕过。`consumer/handoff/checkpoint/readiness/review_surface/evidence_only` 没有具体 `blocking_concern_id` 时直接进入 backlog。

dispatch envelope 必须显式写 `dispatch_mode=manual|auto`；候选检查使用 `--dry-run`，不得把 dry-run 当成正式派发。正式派发必须在 ledger 原子预留 callback budget，并拒绝冲突的 `current-state.active_value_slice`。自动模式还必须满足 automation policy；手动/自动模式的 external effects 都必须携带授权解析结果。

本地直接执行也必须记录 `direct_execution_completed`。切片完成前先用 `agent-lanes/scripts/evidence_receipt.py` 生成 command/artifact receipt，再运行：

```powershell
python agent-lanes/scripts/value_delta_gate.py --completion-file <completion.json> --dispatch-file <dispatch.json> --record
```

没有 PASS 不得增加 `consecutive_auto_slices`，不得选择下一条自动切片。

Value Delta Gate 缺 dispatch file、ledger 中没有对应 `dispatch_started`、receipt 早于派发、command 非零退出、artifact hash/mtime 漂移时必须 fail closed。收到 callback 时还要确认邮局已写入 `callback_accepted`；dashboard 只有精确 `reply_to + lane + value_slice_id` 匹配才能关闭待回。

V2.3 的正式派发结果还必须保留 `dispatch_hash` 和 `callback_provenance`，并随结构化任务交给目标泳道。全局 dispatch reservation 在 ledger 锁内重新核对其它 Value Slice 的 active slot 与 auto iteration 剩余额度；不得先在锁外判断后直接发送。external effects 由 Product Gate 内部调用 resolver，dispatch 自带的 `authorization_resolution` 只作审计输入，不能作为授权事实。

控制内核使用 `.codex/runtime/agent-lanes-control.key` 签发本地 provenance。主调度不得把 key 内容写入消息、日志、artifact 或项目文档；普通泳道只消费 Product Gate 返回的 callback claim，并通过 `evidence_receipt.py` 请求实际执行/核对后签发 receipt。该边界防止协作式自动化误报，不等价于敌对同用户进程隔离。

### Product Loop Check / 用户闭环检查

主调度优先维护一个明确的 `active_user_loop`。目标项目必须自行定义，通用示例是：

```text
入口 / 对象选择 -> 详情 / 分析 -> 证据 / 质量 -> 行动或内部预演 -> 复盘 / 报告
```

每次派发前必须写清：

- `stage_priority`: `P1`、`P2`、`P3`、`P4` 或 `P5`。
- `why_now`: 为什么本轮现在做，而不是做更高优先级主线。
- `mainline_impact`: `direct_advance`、`blocks_mainline`、`quality_confidence`、`backlog_only` 或 `risk_boundary`。
- `active_user_loop`: 本轮服务的用户闭环。
- `loop_impact`: `advanced`、`blocked`、`regression_fixed` 或 `neutral`。普通开发任务不应是 `neutral`；若只是证据补齐，必须说明它解除哪项用户可见交付阻塞。
- `same_capability_count_last_5`: 最近 5 个相关 GOAL 中同一 capability 的数量。
- `concern_policy`: 本轮 concern 是 `blocking_concern` 还是 `backlog_concern`。
- `next_non_same_capability_loop`: 完成后要切回的非同类用户闭环。

非主调度泳道 completion callback 字段硬约束：

- 所有 callback 必须带 `value_slice_id`、`value_delta` 和 `review_policy`。
- planning / design / development / guardian / evolution callback 还必须带 `active_user_loop`、`loop_impact`、`blocking_concerns`、`backlog_concerns`、`recommended_next_type`。
- review callback 还必须带 `active_user_loop`、`user_loop_progress`、`blocking_concerns`、`backlog_concerns`、`recommended_next_type`。
- 主调度收到缺字段回报时可以先处理原文，但下一次同泳道派发必须要求补齐；dashboard / xlsx 中的 `loop_field_warnings` 作为质量告警。

调度硬约束：

- 同一 capability 连续最多推进 2 个切片；第 3 个默认停止，除非它是当前 `active_user_loop` 的 P1/P2 直接硬阻塞。
- 连续 3 个任务里至少 1 个必须推进纵向用户闭环，不能全是 schema、readiness、wrapper、evidence-only、review surface、browser smoke 或 screenshot。
- `DONE_WITH_CONCERNS` 不自动生成下一条任务。只有 `blocking_concern` 可以继续派发；`backlog_concern` 进入 backlog、roadmap 或阶段合并审查。
- 低风险、本地-only、证据一致的小切片默认合并验收；不要逐条完整审查拖慢主线。
- 下一刀如果不能让 `active_user_loop` 前进，先做 Skeleton Plan Refresh 或路线取舍卡。
- 执行 Anti-Shell Gate：阶段已经 `current-stage-good-enough`、验收 `blocking_concerns=[]`，或同一链路已完成“设计 -> 本地消费 -> 聚焦验收”后，下一刀默认必须切到非同类 P1/P2 主线、真实样本/质量可信度推进，或用户视角纵向验收；继续派 handoff / readiness / browser smoke / screenshot / evidence-only / review surface / status panel / summary wrapper，必须引用具体 P1/P2 `blocking_concern`。
- Handoff 只能算一次推进：如果本轮 handoff 已经把上一阶段结果接到下一段用户路径，后续不得继续围绕同一 handoff 做 polish / evidence / screenshot / readiness，除非验收明确给出阻塞。
- dashboard 是人看的运行态。若 dashboard 显示“可能待回”但 message-log / worklog 已有对应 completion callback，先刷新或修正 dashboard 匹配，不要重复派同一任务。
- dashboard 的“泳道待回”不能混入用户给主调度的请求。用户请求应单独显示为主调度待处理或历史请求，不按 completion callback 折叠。

### Next Mainline Slice Selection / 主线自动续航

主调度完成一个主线阶段后，要自动找下一段主线，而不是停在 concern 或阶段发布记录上。

触发条件：

- 收到 `stage_release_record`、阶段合并验收或 `current-stage-good-enough`。
- 收到 `DONE`。
- 收到 `DONE_WITH_CONCERNS`，但 `blocking_concerns` 为空或不阻塞当前 P1/P2。

处理规则：

1. 只把 `blocking_concerns` 当成阻塞。`backlog_concerns` 必须写入 backlog、roadmap、dashboard 或阶段发布记录，不得触发同类修复，不得让主线停。
2. 如果没有阻塞，运行 `Next Mainline Slice Selection`，从 `agent-lanes/current-state.json`、`agent-lanes/dashboard.md`、最新 callback 和产品 feature 状态中选择下一条 P1/P2 候选；历史计划和 GOAL log 只在冲突时追溯。
3. 选择结果必须写入 worklog 或派发记录的 `next_mainline_slice_selection`，包含 `source_message_id` 或 `stage_release_record_id`、`blocking_concerns`、`backlog_concerns`、`selected_next_slice`、`stage_priority`、`why_now`、`mainline_impact`、`dispatch_or_plan`。
4. 如果下一条 P1/P2 清楚，先生成一个 Value Slice dispatch artifact 并运行 Product Value Gate；门禁通过后才派最合适的一条泳道。
5. 如果下一条 P1/P2 不清楚，可以由主调度本地完成轻量候选比较；只有跨模块依赖、重大路线或验收边界确实不清楚时才派 planning，不能把每次阶段关闭都变成 planning refresh。
6. 阶段发布后允许进入 `idle_with_recommendation`：已记录候选 Value Slice 但尚未通过门禁时，不得为了“不能停”制造新任务。
7. 如果刚关闭的是 handoff / readiness / evidence / screenshot / review surface 类阶段，`selected_next_slice` 默认必须是非同类 P1/P2 用户闭环；仍选择同类切片时，必须在 `why_now` 引用具体 `blocking_concerns`。

只有三类 `NEEDS_CONTEXT` 合法：

- 真实外部调用、付费、secret、账号、受监管操作、高风险自动化执行、远程写入或生产化承诺。
- 重大产品路线取舍。
- 上下文不足，无法判断当前 P1/P2 主线。

## Autonomous Iteration Loop / 自主迭代推进循环

主调度不能等用户反复说“做全盘计划”“整体推进”。每次收到泳道 completion callback、阶段验收结果或 dashboard 刷新后，都要自动执行 Autonomous Iteration Check。

检查输入：

- `agent-lanes/current-state.json` 的 `automation_policy`、结构化 `candidate_slices`、阻塞和当前用户闭环。
- `agent-lanes/value-slice-ledger.jsonl` 的预算使用和最近检查点。
- 最新邮局合并 callback 的 `status`、`evidence`、`blocking_concerns` 与 Value Delta Gate 证据。
- `agent-lanes/dashboard.md` 的泳道忙闲和紧凑运行态。
- 只有候选涉及 Provider、外部 API、secret、持久写入或成熟度推进时，才读取 `docs/capability-status.json` 并运行 `resolve_authorization.py`；只有状态冲突或阶段复盘时才打开 message-log、GOAL log 和旧计划。

检查问题：

- 当前产品骨架整体完成度处于哪个区间：`0-60%`、`60-80%`、`80-90%`、`90%+`。
- 最近 2-3 个 GOAL 是否围绕同一 capability/provider。
- 是否存在“计划已落实，但没有新计划”的空档。
- 下一刀是否仍能推进用户可见闭环，而不是继续补壳层。
- 下一刀的 `stage_priority` 是 P1/P2/P3/P4/P5 哪一类；如果是 P4/P5，它是否真的阻塞 P1/P2。
- 最近是否把辅助分支、备注、导出、保存、展示 polish 或二级设置误当成主线。
- 是否需要用户授权、预算、账号、secret、真实写入、交易、路线锁定或产品取舍。

自动动作：

- 如果计划过期、下一刀不清楚、阶段完成度跨过阈值、或同一 capability 连续 2-3 次，先在主调度生成候选 Value Slice；只有跨泳道依赖或重大路线仍不清楚时才派 `planning`。
- 如果规划 callback 已给出 3-6 个薄纵向切片，先按 `stage_priority` 和 `mainline_impact` 排序；优先派 P1/P2，P3 只在影响主线可信度时插队，P4/P5 默认进 backlog。
- 如果下一刀低风险、属于 P1/P2 或阻塞 P1/P2 的 P3，仍必须先通过 Product Value Gate，再派对应泳道。
- 开发/设计/守门完成后优先复用本切片门禁证据；只有 Value Slice 到达 bundle/stage boundary、出现 P1/P2 blocker、风险升级为 high_risk 或用户明确要求时才派 `review`。普通低/中风险小修不自动派 review。
- 如果发现风险边界不清，自动派 `guardian`；如果涉及必须用户决策的事项，停止并给用户确认卡。
- 如果当前阶段完成度达到 `80-90%`，自动进入 Quality Pass；达到 `90%+` 后，只能进入打包、长跑验证、发布准备或高风险外部执行评估，不得跳过受控验证直接改变真实外部状态。
- 受控自动推进一次最多连续完成 `automation_policy.max_consecutive_auto_slices` 个 Value Slice，模板默认上限是 2。达到上限、出现两个同等合理的 P1/P2 路线、高风险、授权解析失败、成熟度要推进到 `quality_reviewed/production_ready`、远程写入或高风险真实执行时，必须写检查点并停止自动派发。
- 首次启用或重大机制升级后，先运行 1-2 个低/中风险真实产品切片；积累 dispatch、callback、receipt、Value Delta、ledger 和 dashboard 记录后，再由未参与实现的 Agent 独立复审。复审前不得把受控迭代升级为长期无人值守。
- 外部副作用不能靠自然语言判断授权。派发必须携带 `resolve_authorization.py` 生成的精确 capability/variant `AUTHORIZED` 结果；最具体 variant 优先于 capability，pending/blocked/额度不足一律 fail closed。

完成度阈值用于调度，不是对外承诺：

- `0-60%`: Skeleton Pass，优先可见主流程、本地 artifact、失败状态、复跑命令。
- `60-80%`: Real Pass，替换关键 fixture 为真实只读样本、真实 provider adapter 或真实本地计算。
- `80-90%`: Quality Pass，做质量、解释性、体验、稳定性、错误处理和合并审查。
- `90%+`: Production / Controlled Operation Pass，做打包、长时间验证、发布准备、权限/回滚/日志和高风险外部执行评估。

打回条件：

- 主调度收到 callback 后只转述结果，没有判断下一步 hook。
- 计划已经落实完，却没有自动触发新的计划刷新或下一刀派发。
- 连续多次局部深挖，却没有 capability exit check。
- 需要用户授权或路线取舍，却假装可以自动继续。
- 把 P4/P5 辅助分支当成下一刀，却没有说明它阻塞哪条 P1/P2 主线。

## 调度顺序

按下面顺序选择一个最适合的下一步。只选择当前最能推进闭环的动作，不要一次铺开所有 Skill。

1. 如果产品目的、用户、范围或验收标准不清楚，使用 `product-spec-builder` 的工作流更新 `docs/01-product-spec.md`。
2. 如果需求清楚但 UI、UX、交互、内容结构或产品气质不清楚，使用 `design-brief-builder` 更新 `docs/02-design-brief.md`。
3. 如果需要原型、页面清单、可复用原型代码或截图转实现策略，使用 `prototype-builder`。
4. 如果需求和设计已足够，但没有阶段化实现计划，使用 `dev-planner` 更新 `docs/03-dev-plan.md`。
5. 如果计划存在但当前执行目标不够精确，使用 `goal-creator` 创建可执行 GOAL。
6. 如果当前 GOAL 清楚且没有阻塞，使用 `dev-builder` 实现并自测。
7. 如果出现真实 bug、报错、构建失败、测试失败或用户反馈问题，使用 `bug-fixer`。
8. 如果完成条件可程序判断，或用户要求检查、测试、构建、lint、typecheck、CI、本地验收，使用 `gate-runner`。
9. 如果代码改动属于 `high_risk`，或涉及跨模块、secret、权限、数据写入、线上 API、registry/source 修改、发布/客户可用声明，使用 `code-reviewer` 做未参与实现的代码级独立审查；`low_risk` 和普通 `medium_risk` 可以先用聚焦门禁闭环，并在同一纵向功能包末尾合并审查。
10. 如果准备声明生产可用、客户可用、真实线上调用可用、数据写入可用、发布可用，或同一纵向功能包到达阶段边界，使用 `review-runner` 做闭环审查并更新 `docs/05-review-report.md`；低风险小切片不必每次单独触发。
11. 如果要上线、部署、打包、交付或交接，使用 `release-builder` 更新 `docs/06-release-record.md`。
12. 如果用户问机制、调用时机、门禁、自进化或子 Agent 规则，使用 `goal-methodology-guide`。
13. 如果符合下面的“自进化触发规则”，使用 `evolution-runner`。

## 多泳道协作模式

当项目启用 `agent-lanes/` 时，调度顺序不是固定串行流水线。`project-orchestrator` 应把 Skill 当成职责契约，把泳道当成并行执行单元，用结构化派发和 completion callback 合并结果。

- 用户在主调度线程里提出新需求、修改需求、路线判断、临时想法或对方案的意见时，先执行轻量需求 intake，再决定是否派发泳道。不能只在当前聊天里理解后静默继续。
- 需求 intake 至少判断：这句话属于产品需求、设计影响、守门风险、开发任务、验收问题还是机制进化；稳定事实应写入哪个项目文档；是否需要其它泳道实际处理；是否需要停止向用户要授权或产品取舍。
- 稳定事实优先落档：产品需求写 `docs/01-product-spec.md`，设计影响写 `docs/02-design-brief.md`，阶段/路线写 `docs/03-dev-plan.md`，能力/Provider 边界写 `docs/capability-status.json`，参考资料写 `docs/08-open-source-reference-pool.md`，调度流水写 `agent-lanes/message-log.jsonl`。
- 如果需要其它泳道参与，优先用 `send_message_to_thread` 发送结构化任务；如果线程工具不可用，必须在 `agent-lanes/message-log.jsonl` 记录 `pending_dispatch` 或 fallback 任务，不能声称其它泳道已经处理。
- 派发消息必须包含目标、上下文文件、允许写入范围、完成标准、禁止事项、风险等级、完成回报 JSON 格式和中文优先规则。
- 派发消息还必须内嵌完整 `value_slice`，并附 Product Value Gate 的 PASS 证据；没有门禁证据的 dispatch 只允许记录为 draft，不得发送。
- 主调度只有收到目标泳道 completion callback，或明确记录 fallback/pending 状态后，才能说该需求已经进入多泳道机制。
- 如果规划、设计、守门之间没有强依赖，可以并行派发；例如需求切片、UI/UX 影响和权限/Provider 风险可以同时进入对应泳道。
- 主调度的一条结构化派发可以替代单独运行 `goal-creator`，前提是派发消息已经包含目标、范围、完成标准、验证证据、禁止事项和回报格式。
- `dev-planner` 不是每次“继续”的必经站；只有阶段顺序、跨泳道依赖、前后端/联调路径、风险或回滚不清楚时才使用。轻量继续可以用当前 `docs/03-dev-plan.md`、泳道 worklog 和 dashboard 做滚动判断。
- 多个低风险泳道回报不需要逐条触发完整 `review-runner`。主调度先聚合 callback、dashboard、message-log 和相关文档；只有阶段边界、用户可见完成声明、中高风险、冲突证据或阻塞问题才派验收泳道做完整审查。
- 门禁按变更面选择：规划/设计文档跑文档和机制检查，开发跑聚焦构建/测试/CLI/浏览器门禁，Provider 跑 registry 和真实 smoke 门禁；不要因为多泳道存在就自动全量门禁。
- 主调度保留最终合并权。泳道负责产物和证据，主调度负责判断是否合并、切换泳道、补派缺口或进入验收。
- 如果泳道 callback 之间互相冲突，或者某条泳道产物缺失完成证据，先补派或验收，不要用固定下一阶段掩盖冲突。

## Dispatch Queue / 单泳道任务锁

Codex 线程不是可靠的多消息队列。`project-orchestrator` 不得把同一泳道当成可无限追加消息的队列；同一目标泳道仍有未完成任务时，继续 `send_message_to_thread` 会打断正在执行的上下文，导致回复截断、输入覆盖和半成品堆积。

派发前必须执行 busy check：

1. 读取 `agent-lanes/message-log.jsonl` 和目标泳道 worklog。
2. 找出发给该泳道的最新 `DISPATCHED`、`sent` 或 `active_dispatch` 记录。
3. 检查是否已有匹配该 dispatch `message_id` 的 completion callback，即 callback 的 `reply_to` 指向该 dispatch，且 `from_agent` 是目标泳道。
4. 如果没有匹配 callback，该泳道视为 busy。

busy 时的处理：

- 不得调用 `send_message_to_thread` 给该泳道补发新任务、返工要求或上下文合并。
- 只能追加 `queued_dispatch` 或 `context_patch` 到 `agent-lanes/message-log.jsonl`，并在主调度 worklog 说明它被哪个 active dispatch 阻塞。
- queued 记录至少包含 `message_id`、`target_lane`、`blocked_by_active_dispatch`、`source_message_id` 或 `reply_to`、`summary`、`context_files`、`created_at`、`status: queued_dispatch`。
- 等目标泳道 callback 回来后，主调度先合并该泳道所有 queued/context_patch，去重后生成一条完整新任务，再发送到泳道线程。

并行派发只允许发生在不同泳道、互不强依赖、且每个目标泳道都不 busy 的情况下。自动推进、callback hook 和用户新输入都不能绕过这个单泳道任务锁。

## Callback Inbox / 主调度收件箱

`project-orchestrator` 不能把自己的线程当成可被任意泳道 callback 随时打断的收件箱。主调度正在合并证据、刷新计划、派发任务或向用户确认时，如果其它泳道直接把完整 callback 发进主调度线程，会造成当前判断被插入式信息打断，甚至让多个 callback 覆盖同一个调度循环。

主调度的 callback 处理规则：

- 完成回报的用户可读主通道是邮局生成并发到线程里的单条 `thread_prompt`，不是短 wake，也不是让主调度默认去 `message-log` 自取原文。
- `agent-lanes/message-log.jsonl` 是审计备份和异常查证入口；只有证据冲突、疑似重复、门禁报错、需要审计或用户要求追溯时，主调度才打开它去重查证。
- 主调度开始合并 callback、刷新计划、派发任务、生成用户确认卡或运行较长验证前，必须写 `orchestrator_state` 到 `agent-lanes/transport-log.jsonl`，标记 `state=busy`、`reason`、`active_batch_id` 或 `active_message_id`、`lease_until`。
- 主调度完成本轮稳定检查点后，必须写 `orchestrator_state` 到 `agent-lanes/transport-log.jsonl`，标记 `state=idle`，并记录本轮 `last_drained_callback_ids` 或 `active_batch_id`。
- 主调度收到 `【邮局合并回报】` 后，直接基于消息里的摘要、证据、风险、变更文件和建议动作做下一步判断，不先回复“我去 message-log 读取完整 callback”。
- 非主调度泳道完成后调用 `agent-lanes/scripts/deliver_callback.py`；只有脚本返回 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 时，才算可投递完成。`send_required=false`、`spooled_waiting`、`spooled` 或 `batched_log` 只代表进入审计/暂存，不代表主调度已收到。
- 处理一条邮局合并回报期间不得因为新的线程 callback 改写当前决策；新 callback 留到下一轮稳定检查点处理。
- 如果 `send_message_to_thread` 返回 `no active turn to steer`、线程不可接管或其它工具层失败，只重试同一个 outbox `thread_prompt`；不得要求泳道重做业务任务。
- dashboard 中早于 `current-state.updated_at`、pending=0 且没有发送确认的 READY outbox 标记为 `historical_unacknowledged`，只保留审计，不自动重试或触发业务任务。

主调度输出或 worklog 应标记本轮处理到哪个 callback，例如 `last_drained_callback_id` 或本轮 callback batch 列表，避免下次重复消费同一批结果。

## 连续讨论协同模式

当用户正在开放式讨论需求、技术路线、判断、担心、偏好或临时想法时，主调度不能等待用户显式说“调用某个 skill/泳道”。每条有实质信息的用户消息都要先做一次讨论 intake，并把结果归入以下四类之一：

- 做讨论 intake 时，先查 `.codex/hooks/skill-hooks.md` 的“讨论场景 Hook 矩阵”，再决定本轮优先 Skill、默认泳道、落档位置和是否派发；不要只凭关键词直接跳到开发。
- `capture_only`: 只是背景、偏好、观察或仍不稳定的想法。主调度应写入合适的研究/需求/路线文档或 message-log 摘要，不派发执行任务。
- `dispatch_needed`: 已经形成可由某条泳道处理的稳定小任务。主调度应派发给 planning/design/guardian/development/review/evolution 中最合适的泳道，或在线程工具不可用时写 `pending_dispatch` fallback。
- `confirmation_needed`: 涉及路线锁定、产品取舍、真实外部调用、付费、secret、账号、持久写入、受监管操作、高风险真实执行、生产声明或重型框架采用，且尚未覆盖在当前授权内。主调度先给用户确认卡；如果已有明确授权或 standing authorization，则记录授权依据并进入 guardian/development/review 的受控路径。
- `clarify_needed`: 信息不足且合理假设会带来方向性偏差。主调度只问最小必要问题，并把未决点写入 message-log 或对应文档。

讨论 intake 的最低动作：

- 识别用户这条消息新增了什么：新需求、需求修改、技术路线判断、资料线索、风险意见、优先级变化、验收标准变化或机制反馈。
- 判断应该更新哪里：`docs/01-product-spec.md`、`docs/02-design-brief.md`、`docs/03-dev-plan.md`、`docs/09-research-roadmap.md`、`docs/capability-status.json`、对应 provider card、`agent-lanes/message-log.jsonl` 或泳道 worklog。
- 如果暂时不派发，也要说明原因：尚不稳定、需要用户确认、风险过高、已有泳道正在处理、或只是背景信息。
- 如果派发，任务必须带上 `discussion_source` 或 `source_message_id`，让后续 callback 能追溯到哪次讨论触发。
- 主调度每次最终回复都要给出“我已记录/派发/需要确认/需要澄清”的明确状态，避免用户不知道讨论是否进入机制。

连续讨论不等于连续开发。默认先沉淀和路由；只有当用户已经确认，或任务属于低风险研究/文档/fixture/已批准 bounded smoke，才允许继续进入执行泳道。

## 开放研发项目模式

当项目目标开放、用户也明确表示自己还不知道从哪里入手时，不要把流程误判成“需求已经确认 -> 自动开发”。此类项目应采用探索式研发节奏。

可自主推进的探索任务：

- 阅读、下载、比较开源库、论文、API 文档、示例项目和方法论。
- 整理技术路线图、候选方案对比、研究问题、失败原因和推荐/不推荐理由。
- 运行本地 fixture、确定性样本、只读本地脚本，或已经由 guardian 批准的 bounded read-only smoke。
- 更新 `docs/09-research-roadmap.md`、`docs/04-goal-log.md`、`docs/capability-status.json`、dashboard 和泳道 worklog。

必须先检查授权状态的事项：

- 锁定重大技术路线或采用重型框架作为产品依赖。
- 新增产品化功能开发，而不只是探索 artifact。
- 运行新的真实外部 provider/API、付费调用、secret、账号、受监管操作或持久写入。
- 正式选择核心执行引擎、内部模拟机制、数据源策略、前端工程栈或长期运行架构。

上述事项如果已经被本轮明确授权或站立授权覆盖，主调度不得继续停在确认卡；应把授权范围、预算/次数、固定输入、secret 不落盘、允许写入位置、回滚方式、证据路径和仍然排除事项写入派发记录或 `docs/capability-status.json`，然后派 guardian/development/review 进入受控实现、smoke、样本保存、质量复核或生产准备。未授权或超出授权范围时，确认卡必须包含：要锁定或开发什么、为什么现在做、已有证据、可选方案、推荐理由、风险/禁止事项、验收标准和确认后派给哪条泳道。用户确认前，可以继续低风险研究，但不能派发超出授权范围的产品化开发任务。

## 带前端项目的分层自主分流

如果项目包含前端、后端/API/CLI、数据契约或本地桥接，不能只按“最近在做什么”惯性推进。每次“继续”都要先做一次轻量分层判断：

- 需求层：用户旅程、数据字段、权限边界或验收标准不清楚时，先回到 `product-spec-builder` 或 `design-brief-builder`。
- 计划层：前端、后端、契约、联调和验证的先后关系不清楚时，先用 `dev-planner` 把阶段拆成薄纵向切片。
- 后端/契约层：前端需要的数据、动作、状态或错误模型没有稳定来源时，先做 API/CLI/schema/fixture/contract 或对应门禁，不要让前端发明私有字段。
- 前端层：后端/契约已有可用证据，但用户无法操作、查看或验收时，优先做前端壳、页面状态、数据适配和可见工作流。
- 联调/桥接层：前端和后端分别存在，但真实数据、命令、API、权限或错误状态没有打通时，优先做最小安全联调。联调要有固定入口、失败状态、复跑命令和证据文件；浏览器或客户端不能伪装成已经完成未接入能力。
- 审查层：如果已经连续两个以上阶段偏向同一层，下一次调度必须检查另一层和联调层是否已经落后，并在输出里说明为什么继续当前层或切换层。

通用判断原则：

- 用户可见功能不能只以后端完成声明收口；必须有前端可见状态、文档证据或明确标为预留。
- 前端页面不能只靠静态 mock 宣称完成；必须说明数据来自真实 API/CLI/fixture/schema，或明确是原型/预留。
- 联调 GOAL 优先选择小而安全的纵切，例如读取一份后端导出的 JSON、调用一个 allowlisted CLI/API、刷新一个 fixture、显示一类错误状态。
- 如果做哪一层仍不清楚，先用 `review-runner` 做闭环审查或用 `dev-planner` 重写下一阶段，不要默认继续堆后端或堆前端。

## 效率模式与纵向闭环规则

连续推进时，默认选择能最大增加用户可用能力的最短纵向切片，而不是默认新增一层 contract、fixture、schema、handoff、readiness、evidence-only 或 review surface。

用户可用能力至少具备一个入口、一个真实或固定 fixture 输入、一个真实输出或可复用 artifact、一个失败状态、一个复跑命令或自动门禁、一个可查看结果的位置。只完成后端、只完成前端、只完成合同、只保存孤立样本，都只能算局部完成。

风险分级：

- `low_risk`: 文档补充、fixture 更新、只读前端展示、局部测试、无行为变化的小修。只需要聚焦门禁，通常不需要完整独立审查和发布记录。
- `medium_risk`: 单模块代码、局部用户可见行为、后端 runner、本地真实 smoke、非破坏性输出。需要相关门禁；独立审查可以合并到同一纵向功能包末尾。
- `high_risk`: 跨模块合同、线上 API、secret、权限、安全、数据写入、registry/source 变更、发布/交付或客户可用声明。必须完整门禁、独立审查和必要发布记录。

效率打回条件：

- 最近两个已完成或计划中的切片都属于 contract/fixture/schema/handoff/readiness/evidence-only/review-surface 时，下一步必须优先转向真实执行、前端可操作、后端到前端接线或端到端流程。
- 同一用户能力包最多允许 2-3 个准备性切片。超过后必须转向真实运行、前端可操作入口、后端到前端接线或端到端样本；除非缺少用户授权、依赖不可用或存在 P1/P2 阻塞。
- 同一个用户能力不要拆成过多微型阶段。能在一个 GOAL 内完成“合同最小定义 + runner + 真实/fixture 验证 + 前端/后续消费”的，应合并成一个纵向功能包。
- 审查防抖：同一个纵向功能包内，完整 `review-runner` 只在阶段边界、P1/P2 阻塞、风险升级到 `high_risk`、触及 secret/权限/数据写入/线上 API/registry/source/发布，或用户明确要求时重复触发。普通小修只补跑失败门禁、相关聚焦门禁或局部复核。
- 小修累计也要收敛。同一纵向能力包连续累计 3-5 个小修后，或准备声明用户可用、客户可用、生产可用前，必须做一次合并审查，避免小风险堆积成中风险。

## 单能力聚焦预算 / Capability Exit Check

调度器必须防止单个 provider/capability 连续吞掉项目节奏。ASR、TTS、OCR、下载器、本地模型、外部 API、生成模型、支付/发布接口等都算 capability。

- 轻量继续时，先从 `docs/04-goal-log.md`、`docs/capability-status.json` 和最近任务记录判断最近 2-3 个 GOAL 是否连续围绕同一 capability/provider 推进。
- 同一 capability 连续推进 2 个 GOAL 后，下一次继续前必须做 capability exit check；连续 3 个 GOAL 后默认停止继续深挖，除非它仍是当前用户可用闭环的直接硬阻塞。
- capability exit check 至少回答：当前成熟度是哪一级；是否已有真实样本或真实 smoke；是否已经被下游流程消费；剩余工作是否需要人工决策、授权、预算、真实写入或质量审查；它是否仍然是下一条用户可见流程的直接硬阻塞。
- 如果已经达到 current-stage-good-enough，就停止继续追加 wrapper、readiness、operator decision、readonly surface、handoff proposal、apply readiness 等壳层，把剩余优化放入 backlog 或显式授权队列。
- 下一步必须切回最高价值的产品纵向闭环，例如前端可操作入口、前后端联调、端到端样本、核心业务流程、报告、打包、发布，或另一个关键 capability。
- 只有当该 capability 仍是当前用户可用闭环的直接硬阻塞时，才允许继续深挖；输出必须说明本 GOAL 解除哪个具体阻塞，以及完成后切到哪个 non-same-capability loop。
- exit check 的结论要写入本轮输出；中高风险、阶段边界或真实接入变化还要写入 `docs/04-goal-log.md` 或 `docs/capability-status.json`。

## 外部依赖/API/模型真实接入分流

如果项目包含外部 API、云端 Provider、本地模型、CLI、SDK、媒体处理工具或其他真实运行依赖，不要把安全边界理解成“只能 fake/check/contract”。调度器应主动判断当前处于哪一级成熟度：

1. `contract_defined`: 输入、输出、错误格式和安全边界已定义。
2. `dependency_available`: 本地模型/CLI/SDK、账号、密钥名称、网络路由或平台权限可用。
3. `real_smoke_passed`: 至少一次真实最小调用通过。
4. `real_sample_output_saved`: 真实输出保存成可复用 evidence/artifact。
5. `integration_connected`: 外部 provider、SDK、模型或执行引擎的输出已被真实业务 workflow/adapter 消费；仅增加 UI consumer、报告镜像、队列镜像或 handoff 不推进 capability maturity。
6. `quality_reviewed`: 质量、耗时、成本、失败模式经过人工或独立审查。
7. `production_ready`: 有批量稳定性、重试、日志、成本、回滚、发布和隐私边界。

默认采用 Provider 解耦：业务流程和前端只依赖项目内部能力合同；真实依赖必须藏在 provider adapter、CLI wrapper 或受控本地服务后面。不要让前端组件、核心业务 runner 或高层 workflow 直接绑定模型目录、Vendor SDK、API key、云端任务 API 或一次性脚本。新 provider 至少要有 README/manifest/受控 CLI 或 smoke 入口，并同步 `docs/capability-status.json`。

优先从 `docs/capability-status.json` 读取成熟度、证据路径、授权状态、预算限制和下一步。如果 registry 缺失或过期，当前 GOAL 可以先补最小 registry 条目；但补 registry 不能替代真实 smoke、真实样本或接线。

能力粒度要贴近真实调用方式。若同一 provider 同时包含普通生成、参考输入、长文本、批量 worker、CUDA/CPU、同步/异步、线上/本地等明显不同风险或验证方式，应拆成多个 capability 或在 capability 下使用 variants，不能用一个成熟度覆盖所有子能力。

涉及 registry 的推进应优先运行或补充 `scripts/validate-capability-status.ps1`，确保 JSON 结构、成熟度、必需字段和 verified/present 证据路径可检查。

真实执行失败时，不要立刻回到 readiness 或等待用户下一步。如果失败属于路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线问题，优先让 `dev-builder` 在同一 GOAL 内小范围修复并复跑真实路径。

真实执行通过后，调度器应继续检查是否已经保存 artifact/evidence、是否接入本轮目标里的下游消费路径、是否更新 `docs/capability-status.json`、是否运行 registry 校验和相关聚焦门禁；缺任一项时，下一步仍属于当前能力包收尾，不要切换到新功能。

mock、stub、pytest monkeypatch 只能证明代码路径和错误处理，不能推进 provider/model/API maturity。

媒体类能力要区分 audio fixture、video fixture、raw-video import、scene split、transcript evidence、materialization 和 selectable atom；不能因为音频 ASR 跑通就宣称完整视频导入或原子素材闭环。

调度规则：

- `quality_reviewed`、`production_ready`、provider/live API、secret、scheduler、writeback、broker/trading、production feed、真实订单、真实资金或真实持仓是动态授权能力，不是永久禁止项。主调度可以说“本轮未推进”，但不得把它写成未来不能推进；如果用户已经授权，就要转成受控任务和可验证证据。
- 本地已安装、不会产生外部费用或远程副作用的依赖，下一步应优先创建或执行真实 smoke/真实样本 GOAL，而不是继续扩展 fake/check。
- 线上 API、付费模型、外部平台或会改变远程状态的能力，调度器应主动向用户请求一次明确授权；请求必须说明调用目的、固定输入样例、次数/预算上限、secret 不落盘规则、输出保存位置和复用策略。
- 如果用户给出一次性授权或 standing authorization，下一步可以进入真实 live call、受控写入、质量复核或生产准备，并把授权依据写入派发记录和 registry；如果用户暂未授权，下一步只能做合同、readiness、适配或排队，并把 live call 状态写成 `pending_user_approval`。
- 如果已经有同输入、同 provider、同参数摘要的可复用 artifact，默认复用和验证它，不要反复消耗线上额度。
- 真实 smoke 只证明能跑通；不能自动宣称质量通过或生产可用。
- 客户端或浏览器不能直接执行任意本地命令、读取 secret 或绕过受控后端/CLI/API 适配层。

## 自进化触发规则

`project-orchestrator` 只在这些情况下触发 `evolution-runner`：

- 显式触发：用户直接要求进化、净化、调整 Skill、优化 hook、沉淀规则、处理 signals。
- 强触发：用户刚刚纠正了流程，并且这条纠正会影响以后同类任务。
- 强触发：同一个误路由、漏步骤、漏门禁、漏文档更新或错误完成声明已经出现两次以上，或已经阻塞当前 GOAL。
- 强触发：项目文档新增了稳定约束，例如技术栈、运行命令、验收方式、发布方式，而相关 Skill 还没同步。
- 强触发：`.codex/signals/` 里有非 `.gitkeep` 的未处理 signal，并且 signal 指向本地 Skill、hook、门禁或流程规则。
- 弱触发：继续推进时发现某个 Skill 的触发词或边界略不适配，但不阻塞当前 GOAL。此时先完成当前主任务，再在输出里建议后续自进化，或记录 signal。

不要触发 `evolution-runner` 的情况：

- 用户只是说“继续/下一步”，且项目当前最缺的是需求、设计、计划、开发、验证或审查。
- `.codex/signals/` 只有 `.gitkeep` 或没有具体可处理内容。
- 问题属于一次性业务选择、审美偏好、产品方向讨论，不是可复用流程规则。
- 当前问题应由 `product-spec-builder`、`dev-builder`、`bug-fixer`、`gate-runner` 或 `review-runner` 直接处理。
- 自进化会打断当前可执行 GOAL，且不是完成该 GOAL 的阻塞项。

## 执行方式

- 读取被选中 Skill 的 `SKILL.md`，按它的核心契约执行。
- 如果多个 Skill 都适合，优先选择更早阻塞项目闭环的 Skill。
- 如果用户只说“继续”，不要追问泛泛问题；根据文档里的 `Next GOAL`、开放风险和最近验证证据决定下一步。
- 如果必须追问，只问能让完成状态可验证的最小问题。
- 执行过程中保持一个主线，不要把“调度”变成只列计划。

## 输出

输出必须包含：

- 当前判断：基于哪些文件和证据判断下一步。
- 调用路线：选择哪个本地 Skill，以及为什么。
- 实际动作：本轮已经更新、运行、实现或验证了什么。
- 证据：文件路径、命令结果、测试结果、审查结果或明确的未验证项。
- 下一步：如果仍未闭环，写出下一条可执行 GOAL。
- Value Slice：本轮 `value_slice_id`、实际 `value_delta` 和 callback budget 使用情况；泳道的 `recommended_next_*` 只能标为咨询建议。

轻量继续模式下，输出可以压缩为：当前判断、选定 Skill、实际动作、验证证据、下一步。只有完整复盘、高风险、阶段边界或用户要求时，才展开全部字段。

输出状态使用轻量状态词，避免长篇流程复盘：

- `DONE`: 完成标准满足，并有本轮或当前 GOAL 内的新鲜验证证据。
- `DONE_WITH_CONCERNS`: 主闭环完成，但仍有非阻塞风险、质量待审或后续接线。
- `NEEDS_CONTEXT`: 缺少用户决策、输入样本、授权或产品取舍，无法可靠继续。
- `BLOCKED`: 已确认存在阻塞，当前无法靠本地小范围修复继续推进。

不要为了套用状态词触发额外审查。状态词只压缩汇报，不改变风险分级、审查防抖和轻量继续规则。

## 完成门禁

只有满足以下条件，才能说本轮“继续”完成：

- 已读取当前状态文档，或明确说明缺失并补齐。
- 已选择并执行一个最合适的本地 Skill 工作流。
- 已更新受影响文档，至少包括 `docs/00-project-state.md` 或被选中 Skill 要求的文档。
- 如果本轮是需求/路线讨论，已完成讨论 intake，并明确给出 `capture_only`、`dispatch_needed`、`confirmation_needed` 或 `clarify_needed` 状态。
- 已提供新鲜验证证据；如果只复用旧 evidence，必须检查仍有效并说明过期风险。验证无法运行时，说明原因和风险。
- 如果发现真实失败或用户纠正暴露可复用规则，已在 `.codex/signals/` 记录 signal 或说明为什么不记录。

## 打回条件

遇到以下情况，不要宣称完成：

- 产品目标或 GOAL 模糊到无法验收，却直接进入开发。
- 代码改动没有运行可用验证，也没有说明验证缺口。
- 高风险改动没有独立审查。
- 文档仍停留在模板内容，却声称项目状态清楚。
- 发布、部署或交接没有启动方式、日志、回滚、冒烟测试和风险记录。
