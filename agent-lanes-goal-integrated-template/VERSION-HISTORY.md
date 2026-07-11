# Agent Lanes + GOAL 模板版本升级说明

本文件是模板包对外发布时的版本说明入口。每次重新打包发布前，都要在这里追加一条版本记录，说明本次升级解决了什么问题、包含哪些新材料、迁移到其他项目时需要注意什么。

## 2026-07-11 / 20260711-domain-neutral-real-run-reaudit

### 变更摘要

- 清除模板中的源项目产品链路、页面名、`MD-*` ID、金融领域默认值和示例路径，改为由目标项目定义 `north_star`、`active_user_loop`、验证工作台和内部模拟执行语义。
- 保留 Value Slice、Stage Value Gate、Anti-Shell Gate、最多两刀检查点和动态授权闸门，但不绑定任何行业。
- Product Value Gate 新增人类可读字段乱码检查（包括 `???`），并拒绝把 `product_value_gate`、`dispatch_hash`、`callback_provenance` 回填到 immutable dispatch 合同。
- 首次启用或重大机制升级后，先运行 1-2 个低/中风险真实产品切片；积累完整控制面记录后，由未参与实现的 Agent 独立复审，复审前不得开启长期无人值守。
- 新增发布构建脚本，对项目专属词、`???`/replacement character 乱码、嵌套同名 Skill 副本、必需文件和 zip 内容做 fail-closed 检查。

### 迁移提示

目标项目部署后先填写自己的产品骨架、P1/P2 主线和用户闭环。不要复制源项目的业务页面或 ID。旧模板包保留为历史；新部署优先使用本版本生成的 zip 和 manifest。

## 2026-07-11 / 20260711-trusted-control-transaction-v2-3

### 变更摘要

- 不同 Value Slice 的 dispatch 统一竞争全局 active reservation；auto iteration 已完成刀数和 active reservation 在同一 ledger 锁内核对。
- dispatch event 保存完整合同 hash，identity 重用只有关键字段/hash 完全一致才允许幂等。
- Product Gate 内部调用 authorization resolver；禁止信任 dispatch 自报 `AUTHORIZED`。
- 新增 `control_provenance.py`，为 evidence receipt 和 callback claim 签名；Value Delta/邮局同时检查签名、ledger provenance、thread/lane 和 dispatch hash。
- 历史 V2.1/V2.2 弱 dispatch event 不得支撑新 V2.3 completion。
- integrated 与 working-copy 两套部署路径均复制 V2.3 核心脚本并初始化本地 provenance key。

### 迁移提示

部署后不要复制其它项目的 `.codex/runtime/agent-lanes-control.key`；每个项目独立生成。旧 ledger 保留审计，但新 completion 必须来自新 V2.3 dispatch。该签名边界面向协作式本地自动化，不代表同用户恶意进程隔离。

## 2026-07-11 / 20260711-control-kernel-hardening-v2-2

### 变更摘要

- 强制 dispatch envelope 使用 `dispatch_mode=manual|auto`；正式派发必须 `--record-dispatch`，候选验证显式 `--dry-run`。
- Product Value Gate 拒绝冲突 active slice，并对手动/自动 external effects 统一要求授权解析结果。
- Value Delta Gate 强制 dispatch file、ledger `dispatch_started` 和 `evidence_receipt.py` receipt；陈旧时间、自报 command、非零退出或 artifact hash/mtime 漂移均 fail closed。
- callback 按注册泳道、目标主调度、dispatch target、`reply_to` 和 `value_slice_id` 做语义校验；接受后写入 callback budget。
- Value Slice ledger 增加跨进程锁、原子预算预留及同一 dispatch 单 callback 限制；dashboard 改用精确匹配并显示控制面冲突。

### 迁移提示

旧 append-only 日志无需批量回写；从新派发开始补 `dispatch_mode` 并使用新 Product/Value Delta Gate。部署脚本会复制 `evidence_receipt.py`。迁移后运行五个脚本自测、机制门禁和一次负向集成 smoke；在独立复审前保留人工检查点。

## 2026-07-11 / 20260711-observability-evidence-integrity

### 变更摘要

- 回报邮局新增 callback 身份与回复链 fail-closed 校验，避免“未知泳道”和不可追踪回报。
- dashboard 从 `current-state.active_value_slice` 补齐尚未进入 message-log 的 active dispatch，避免待回计数与当前状态冲突。
- Value Delta Gate 新增带时区 ISO-8601、未来时间、完成/证据时间顺序和 dispatch-to-completion id 校验。
- Product Value Gate 支持 `outbound_message_id`，ledger 记录与真实发出消息保持一致。
- 同步项目 Skill、机制门禁、模板脚本和部署后自测。

### 迁移提示

部署后运行 `deliver_callback.py --self-test`、`product_value_gate.py --self-test`、`value_delta_gate.py --self-test` 和 `render_dashboard.py`。新 callback 必须显式提供 `from_agent`、`to_agent`、`reply_to` 和 `value_slice_id`；历史 append-only 日志无需批量改写。

## 2026-07-11 / 20260711-bounded-autopilot-control-plane

### 变更摘要

- 新增 `value-slice-ledger.jsonl` 和 `value_slice_ledger.py`，把正式泳道交互与主调度直接执行统一计入预算，关闭只查 message-log 的绕过路径。
- 新增完成后的 `Value Delta Gate`：必须证明 before/after、至少两个验收结果和新鲜 evidence，只有 PASS 才能累计自动切片。
- 新增精确 capability/variant 授权解析器；pending、blocked、额度不足或缺授权依据时 fail closed。
- 受控自动推进默认最多连续 2 个 Value Slice，然后进入用户检查点；高风险、路线冲突、成熟度晋级、远程写入和高风险真实执行提前停止。
- dashboard 把早于当前状态且 pending=0 的 READY outbox 标记为历史未确认投递，不再诱导业务重做。

### 迁移提示

同步三个新脚本、完成模板、current-state automation policy 和 ledger；旧项目可把已确认的直接执行补录为 `direct_execution_completed`。启用自动推进前必须由用户给出本次迭代授权，并在 `current-state.json` 写明 `auto_iteration_id`、两切片上限和停止条件。

## 2026-07-11 / 20260711-agent-lanes-v2-value-slice-gate

### 变更摘要

- 用 `Value Slice + Product Value Gate` 替代 callback 建议驱动的微任务自动续航；没有真实用户动作、阻塞解除、可信度增量或风险降低的 consumer/handoff/readiness 默认拒绝。
- callback 预算最多 3 次，下一泳道建议改为 `advisory_only`；低/中风险本地切片在功能包或阶段边界合并审查。
- `message-log.jsonl` 保留业务记录，`transport-log.jsonl` 承载 spooling、batching 和 orchestrator state；`dashboard.md` 改为紧凑当前状态，完整历史输出到 `dashboard-full.md`。
- 新增 `product-feature-status.json` 模板，把用户页面、动作和 workflow 与 provider/system capability 成熟度分开。

### 迁移提示

旧项目不删除历史日志和大文档。部署新模板后创建 `current-state.json`、`transport-log.jsonl` 和 `product-feature-status.json`，运行 `product_value_gate.py --self-test`，再用一个 Value Slice 派发做 smoke。旧 consumer capability 可只读保留并逐步迁移，不再新增同类条目。

## 2026-07-10 / 20260710-post-office-readable-retry-status

### 变更摘要

- 修复回报邮局最后一公里：`orchestrator-message.md` 和 outbox `*-thread-send.json` 作为人类可读投递产物，必须用能被 Windows/PowerShell/桌面预览稳定识别中文的方式写入。
- `deliver_callback.py` 输出保留 `target_thread_id`、`thread_prompt`、`outbox_path` 和待重试语义；如果 `send_message_to_thread` 返回 `no active turn to steer` 或目标线程不可用，不要求泳道重做业务任务，只保留 outbox 等待重试。
- `render_dashboard.py` 顶部新增邮局投递状态摘要，显示最新 outbox 是已生成待发送 / 待重试，还是已发送 / 已处理，并给出合并信和 outbox 链接。
- `skill-mechanism-check.ps1` 增加邮局可读编码、outbox 重试状态、deliver 重试提示和 dashboard 最新 outbox 状态检查，避免模板迁移后回退。
- 同步 GOAL base、本地机制 Skill、hook/gate 和模板脚本；不重写历史乱码审计正文，历史 `message-log.jsonl` 继续作为审计事实保留。

### 迁移提示

已部署旧模板的项目建议同步 `agent-lanes/scripts/callback_post_office.py`、`agent-lanes/scripts/deliver_callback.py`、`agent-lanes/scripts/render_dashboard.py`、`AGENTS.md`、`.agents/skills/project-orchestrator`、`.agents/skills/evolution-runner` 和 `.codex/gates/skill-mechanism-check.ps1`。

迁移后用一个最小 callback dry-run 生成 outbox，直接用 PowerShell `Get-Content` 打开新生成的 `orchestrator-message.md` 和 `*-thread-send.json`，确认中文可读；再运行 `python agent-lanes\scripts\render_dashboard.py`，确认 dashboard 顶部能看到最新邮局投递状态。

## 2026-07-10 / 20260710-dynamic-boundary-gate

### 变更摘要

- 新增 `Dynamic Boundary Gate / 动态边界闸门`：模板不再把 `quality_reviewed`、`production_ready`、provider/live API、secret、scheduler、writeback、production feed、受监管操作、高风险自动化执行或真实外部状态变化写成永久禁区。
- 更新 `AGENTS.md`、`project-orchestrator`、`dev-builder`、`review-runner`、`gate-runner` 和 `evolution-runner`：未授权时不越权、不伪装完成；已有一次性授权或 standing authorization 时，必须记录授权范围并进入受控实现、smoke、样本保存、质量复核或生产准备。
- 更新 hook 路由：当用户说“边界写死了”“授权后还被挡住”“真实接入被机制拦住”时，自动路由到进化/守门/门禁，而不是继续按旧边界停住。
- 更新 `skill-mechanism-check.ps1`：检查模板和项目本地 Skill 是否包含动态边界闸门，防止未来又退回“不要触碰”的死边界表达。
- 更新 Bootstrap 和泳道模板：守门泳道被定义为“把高风险能力转成可授权、可验证、可回滚路径”的泳道，而不是永久阻断真实接入的泳道。

### 迁移提示

已部署旧模板的项目建议同步本版本中的 `AGENTS.md`、`.agents/skills/project-orchestrator`、`.agents/skills/dev-builder`、`.agents/skills/review-runner`、`.agents/skills/gate-runner`、`.agents/skills/evolution-runner`、`.codex/hooks/skill-hooks.md` 和 `.codex/gates/skill-mechanism-check.ps1`。

迁移后，历史 worklog、message-log 和审计记录中保留的“本轮未触碰高风险能力”不需要重写；它们是历史事实。需要改变的是未来派发、验收和 dashboard 文案：必须区分 `本轮未推进`、`待授权`、`已授权待验证`、`已受控验证/可进入下一成熟度`，不能把阶段边界写成最终产品定位。

## 2026-07-06 / 20260706-tool-level-ia-virtual-portfolio-open-source-gates

### 变更摘要

- 新增 `Tool-Level IA Gate / 工具级信息架构门槛`：复杂工具型前端不能只描述已有卡片、字段和审计状态，必须从用户目标出发定义一级页面、页面职责、用户问题、卡片职责、字段用途、入口、结果回看和状态边界。
- 新增 `Internal Simulation Semantics Gate / 内部模拟执行语义门槛`：把“当前阶段的本地样本 / 静态 payload / 非生产边界”和“目标态的产品内模拟执行能力”分开表达，避免把阶段性 readonly 文案误写成最终产品定位。
- 新增 `Open Source Integration Gate / 开源嫁接门槛`：当用户希望复用别人开发好的前端、后端或开源模块时，必须先检查 license、attribution、dependency、local smoke、adapter 边界和 guardian 边界；不能直接复制外部项目代码，也不能绕过高风险守门。
- 强化 `design-brief-builder` 和 `frontend-quality-runner`：涉及跨页面工作台、工具地图、验证实验、内部模拟执行或结果看板时，设计和验收都要先判断整体工具结构，而不是只审卡片主阅读层。
- 强化 `open-source-research-runner`：开源调研输出必须落到项目文档、候选池、路线图或泳道 workspace，并明确“可借鉴 / 可适配 / 暂不引入”的边界。
- 同步更新 hook 路由和 `skill-mechanism-check.ps1`，确保这些规则不只停留在说明文档里。

### 迁移提示

这次升级来自一个复杂工具型前端的真实失败案例，但模板沉淀的是通用机制：任何复杂工具、运营后台、研究台、数据产品或工作台，都需要先定义“用户要完成什么事、一级页面怎么承载、结果在哪里回看、风险和审计信息放在哪一层”。不要把触发案例里的行业对象、业务术语或页面名称照搬到其他项目。

`Internal Simulation Semantics Gate` 是通用的“内部模拟执行 / 沙盒执行 / 非真实外部执行”语义门槛：它要求区分阶段性只读样本、产品内部受控状态变化，以及需要账号/secret/付费/远程写入/受监管操作的高风险真实执行。

如果目标项目要引入开源前后端或第三方示例实现，应先让 `open-source-research-runner` 产出 Open Source Integration Gate 结论，再由 planning / guardian / development 分别处理许可、依赖、adapter 和本地 smoke，不要把外部代码直接复制进业务目录。

## 2026-07-06 / 20260706-decision-usefulness-gate

### 变更摘要

- 新增 `Decision-Usefulness Gate / 决策意义门槛`：复杂业务卡片不能只做到字段齐全、validator 通过和审计可追溯，主阅读层必须让用户看懂当前判断、对核心业务判断的影响、关键证据、否决/风险条件和下一步人工动作。
- `frontend-quality-runner` 增加卡片类型和打回条件：`decision_card`、`evidence_card`、`workflow_card`、`audit_card`。非决策卡片必须在主视图说明它不支持业务判断，只用于证据复核、流程导航或技术审计。
- `design-brief-builder` 增加设计前置要求：涉及研究、候选、复盘、报告、行动等决策辅助卡片时，设计 Brief 必须先定义卡片类型和决策意义，不能从 raw enum、JSON key、source path、target surface 或审计字段反推 UI。
- Hook 路由新增“决策卡片、研究卡片、候选卡片、复盘卡片、报告卡片、行动卡片、核心业务判断、当前判断、决策意义、机器字段卡片”等触发词。
- 机制门禁新增检查项，确保模板迁移后不会退回“机器字段卡片通过、用户仍无法判断下一步”的旧模式。

### 迁移提示

迁移到其他项目时，目标项目应把“核心业务判断”替换为自己的真实判断场景，例如是否进入审批、是否继续处理、是否升级风险、是否联系客户、是否发布、是否进入下一阶段。通用要求是：业务卡片的主层必须支持用户形成下一步判断；技术审计、追溯路径和 validator 状态默认进入折叠层。

## 2026-07-05 / 20260705-figma-frontend-quality-gate

### 变更摘要

- 将 Figma / 专业设计审查视角纳入复杂工具型前端的默认质量门槛。
- `frontend-quality-runner` 不再只检查截图、字段完整性和可读性；必须检查首屏任务、行动路径、主次分层、审计信息折叠、状态语义、人话文案、窄屏可用和风险提示。
- `design-brief-builder` 必须在复杂业务工作台页面中写清用户先看什么、下一步点哪里、完成后回到哪里，以及主层 / 详情层 / 审计层如何分工。
- Hook 路由新增 Figma 审查、设计审查、首屏没有重点、行动路径不清、审计信息太多、像日志罗列等触发词。
- 机制门禁新增前端设计审查检查项，防止模板迁移后退回“字段齐全但用户看不懂”的旧模式。

### 迁移提示

迁移到其他项目时，应把这里的规则理解为通用“业务工作台 / 数据工具 / 运营后台 / 研究台”前端质量门槛，而不是某个具体行业的 UI 规则。Figma 不是产品结构源头，但它的审查视角必须进入开发前和验收前：字段、证据和边界齐全，只能说明机器可验；用户能看懂当前任务、风险和下一步，才说明前端设计合格。

## 2026-07-03 / 20260703-registry-orchestrator-thread-resolution

### 变更摘要

- 修复邮局 / callback 投递脚本的旧主调度线程残留问题：`deliver_callback.py` 和 `callback_post_office.py` 默认不再使用硬编码线程 id，而是优先读取 `agent-lanes/agent-registry.json` 中当前 `orchestrator.thread_id`。
- 当用户通过 lane recovery 替换主调度线程后，后续泳道 completion callback 会自动投递到当前主调度，而不是投到历史归档线程。
- 保留显式 `--orchestrator-thread-id` 覆盖能力；若 registry 缺失，则退到 `AGENT_LANES_ORCHESTRATOR_THREAD_ID`，最后才是 `pending_setup`。

### 迁移提示

已部署旧模板的项目如果发生过主调度线程重建，必须同步本版本的 `deliver_callback.py` 和 `callback_post_office.py`。否则泳道可能已经完成并写入审计日志，但合并回报会投到旧线程，表现为“主调度等待开发回报”。


## 2026-07-03 / 20260703-loop-empty-array-warning-fix

### 变更摘要

- 修复 dashboard / post-office 对 Product Loop 字段的误判：`blocking_concerns: []` 和 `backlog_concerns: []` 表示字段已填写且当前无对应 concern，不再被标记为 `loop_field_warnings`。
- 同步运行态、working-copy 和可移植模板脚本，避免新项目部署后把“无阻塞”误读成“字段缺失”。
- 保留缺字段检查：字段不存在、值为 `null` 或空字符串时仍会提示补齐。

### 迁移提示

已部署 `20260703-next-mainline-slice-selection` 但 dashboard 仍提示空数组字段缺失的项目，应同步本版本的 `render_dashboard.py` 和 `deliver_callback.py`。这不会放宽回报字段要求，只是把空数组视为合法的“无阻塞 / 无待办”。


## 2026-07-03 / 20260703-next-mainline-slice-selection

### 变更摘要

- 新增 `Next Mainline Slice Selection / 主线自动续航`：阶段发布、阶段合并验收、`current-stage-good-enough` 或无阻塞的 `DONE_WITH_CONCERNS` 之后，主调度必须自动选择下一条 P1/P2 主线切片。
- 明确 `DONE_WITH_CONCERNS` 只看 `blocking_concerns`；没有阻塞时继续推进，`backlog_concerns` 只能进入 backlog、roadmap、dashboard 或阶段发布记录，不能让主线停。
- 规定 `stage_release_record` 后必须写入 `next_mainline_slice_selection`，包含来源、阻塞项、待办项、被选中的下一刀、优先级、为什么现在做和派发/规划动作。
- 收紧 `NEEDS_CONTEXT`：只有真实外部调用、付费、secret、账号、受监管操作或高风险自动化执行；重大产品路线取舍；或上下文不足以判断 P1/P2 时，主调度才能停下来问用户。
- 同步运行态、GOAL base、模板内 `project-orchestrator` 和机制门禁，防止对外模板缺少这条续航规则。

### 迁移提示

已部署旧模板的项目建议同步 `AGENTS.md`、`.agents/skills/project-orchestrator/SKILL.md` 和 `.codex/gates/skill-mechanism-check.ps1`。同步后，目标项目应把 P1/P2 定义成自己的核心用户闭环；主调度在每个阶段完成后，不能只报告完成或等待用户，而要自动选择下一条最高价值主线，除非命中三类合法停顿原因。


## 2026-07-02 / 20260702-generic-risk-wording

### 变更摘要

- 继续净化对外模板文案，把守门边界中的原行业化风险词替换为更通用的“受监管操作 / 高风险自动化执行”。
- 保留原本的风险语义：凡涉及真实调用、账号、secret、成本、外部写入、受监管操作或高风险自动化执行，仍必须通过守门/授权路径；从 `20260710-dynamic-boundary-gate` 起，该路径被定义为动态授权闸门，不是永久阻断。
- 本次只改模板和 GOAL base 的可移植说明，不改变源项目自己的业务规则和运行态约束。

### 迁移提示

目标项目部署后，应把“受监管操作 / 高风险自动化执行”映射成该项目自己的高风险动作，例如发布、扣费、账号操作、远程写入、生产数据变更、批量自动化执行、真实外部状态修改等，而不是默认理解为某个特定行业动作。


## 2026-07-02 / 20260702-stage-value-gate-generic-cleanup

### 变更摘要

- 对输出模板包做通用化清理，移除源项目专属的产品链路、行业术语、provider 名称和风险文案，避免迁移到其他项目时把源项目的具体需求带过去。
- 保留 `Stage Value Gate / 阶段价值门槛`、`Product Loop Check`、邮局合并回报、泳道恢复、dashboard / XLSX 可读记录、项目本地 Skill 等通用机制。
- 将示例描述改成中性表达，例如“用户主流程”“业务工作台”“数据源或输入接入”“结果评分、解释或决策辅助”“高风险结论”等。
- 本版本取代 `agent-lanes-goal-integrated-template-20260702-030855.zip`；上一版已经包含阶段价值门槛，但仍残留源项目专属文案，不建议继续对外发布。

### 迁移提示

新项目使用本版本时，应在部署后由目标项目主调度补写自己的 `active_user_loop`、P1/P2/P3/P4/P5 分层、产品骨架链路、外部依赖授权边界和验收标准。不要把模板里的中性示例当成目标项目需求本身。


## 2026-07-02 / 20260702-stage-value-gate

### 变更摘要

- 新增 `Stage Value Gate / 阶段价值门槛`：主调度派发前必须判断当前任务是 `P1`、`P2`、`P3`、`P4` 还是 `P5`。
- 要求派发记录写清 `stage_priority`、`why_now`、`mainline_impact` 和 `deferred_items`，避免把辅助分支包装成主线。
- 明确 P1/P2 主线优先；P3 只有影响主线可信度时插队；P4/P5 默认进入 backlog 或守门/授权队列。
- 更新 `project-orchestrator` 和机制门禁，确保模板部署后主调度会先做阶段价值排序，再做 Product Loop Check。

### 迁移提示

已部署旧模板的项目应在计划文档中定义自己的 P1-P5 主次表，并同步 `project-orchestrator` 与 `skill-mechanism-check.ps1`。如果主调度想派辅助保存、导出、偏好、二级设置或高风险生产化任务，必须先说明它为什么阻塞 P1/P2。

## 2026-07-02 / 20260702-template-domain-neutralization

### 本次升级重点

- 净化对外可移植模板中的原项目专属文案：移除特定行业、特定页面、特定数据源和特定合规边界的默认表达。
- 将前端增强 Skill 改成通用“目标项目 / 业务工作台 / 数据工具 / 交互产品”表达，避免新项目被原项目的产品形态绑死。
- 将开源研究、需求追踪、系统调试、规划和主调度中的金融专属风险词改成通用“受监管操作 / 高风险自动化执行 / 合规承诺 / production feed”。
- 将默认产品骨架路线改成可替换占位链路：用户/对象/任务范围选择 -> 数据源或输入接入 -> 标准化数据 / artifact -> 核心处理 -> 前端入口 -> 评估 / dry-run / 仿真 -> 报告或交付物 -> 生产接入评估。

### 迁移提示

新项目使用本模板时，应在部署后把 `<PROJECT_NAME>`、`<primary-user-entry>`、`<object/detail-view>`、`<core-action-or-analysis>`、`<review-or-approval-flow>` 和 `<report-or-evidence-output>` 替换成目标项目自己的产品闭环。不要把原项目的行业词、数据源、页面名或合规边界复制到无关项目。

## 2026-07-02 / 20260702-product-loop-callback-quality

### 本次升级重点

- 将 Product Loop 字段从“主调度派发要求”升级为“所有非主调度泳道 completion callback 的通用字段要求”。
- `deliver_callback.py` 新增非阻塞 `missing_product_loop_fields` 质量告警：回报仍可投递，但 dashboard / xlsx 会暴露缺字段，方便下次派发纠正。
- `render_dashboard.py` 新增 `loop_field_warnings`、`active_user_loop`、`loop_impact`、`user_loop_progress`、`blocking_concerns`、`backlog_concerns` 和 `recommended_next_type` 展示，并加入 Product Loop 节奏告警。
- 模板内 `project-orchestrator`、`dev-planner`、`design-brief-builder`、`dev-builder`、`gate-runner`、`review-runner`、`evolution-runner` 同步 completion callback 字段契约。
- 机制门禁新增 Product Loop callback 字段检查，防止后续只在运行态修规则、模板包没有跟着进化。

### 迁移提示

已部署旧模板的项目建议同步本版本中的 `AGENTS.md`、上述本地 Skill、`render_dashboard.py`、`deliver_callback.py` 和 `.codex/gates/skill-mechanism-check.ps1`。同步后，旧历史回报可能出现 `loop_field_warnings`，这是迁移期可接受告警；新回报应逐步补齐字段。

## 2026-07-01 / 20260701-235141

### 本次升级重点

- 吸收产品推进节奏复盘：系统不能只证明每个局部零件安全，必须优先持续交付用户可用闭环。
- 将 `Product Loop First / 用户闭环优先调度` 同步到可移植 GOAL base 和模板内 GOAL base。
- `project-orchestrator` 模板副本新增 `Product Loop Check`，派发前必须写清 `active_user_loop`、`loop_impact`、`same_capability_count_last_5`、`concern_policy` 和 `next_non_same_capability_loop`。
- `review-runner` 模板副本新增 `user_loop_progress`、`blocking_concerns`、`backlog_concerns` 和 `recommended_next_type`。
- 机制门禁新增产品闭环字段检查，避免只改当前项目而漏同步模板。

### 迁移提示

已部署旧模板的项目建议同步 `AGENTS.md` 中的 Product Loop First 段、`project-orchestrator`、`review-runner`、`.codex/hooks/skill-hooks.md` 和 `.codex/gates/skill-mechanism-check.ps1`。同步后应在目标项目定义自己的 `active_user_loop`，不要照搬源项目的具体闭环。

## 2026-07-01 / 20260701-192422

### 本次升级重点

- 吸收二次泳道故障经验：新建替换线程后，如果接管提示过重或一次性读取上下文太多，候选线程也可能立刻 `agent loop died unexpectedly`。
- 升级 `lane-recovery-runner`：恢复流程改为“瘦身接管 -> 连续轻量健康检查 -> registry 切换 -> 分批读取上下文”。
- 增加二次故障处理规则：候选新线程如果健康检查失败，应标记为“历史归档-二次故障”，不得登记为 current thread，也不得继续投递长上下文。
- 更新 `orchestrator-recovery-template.md` 和 `PERSISTENT-RUNTIME-FILES.md`，提供短健康检查提示词和分批读取顺序。
- 更新 hook、gate 和部署提示词，让新项目部署后也能检查这套恢复规则。

### 迁移提示

已使用旧模板的项目不需要重装全部运行态。建议只同步 `lane-recovery-runner`、`.codex/hooks/skill-hooks.md`、`.codex/gates/skill-mechanism-check.ps1`、`orchestrator-recovery-template.md` 和 `PERSISTENT-RUNTIME-FILES.md`，然后重新运行 Skill 机制检查。

## 2026-07-01 / 20260701-191828

### 本次升级重点

- 明确把 `lane-recovery-runner` 随模板交付：目标项目在主调度泳道、开发泳道、验收泳道等 Codex 线程崩溃、过长、无法提交消息或需要替换 `thread_id` 时，可以按持久化运行态文件重建新线程接管。
- 明确项目机制 Skill 必须本地化：目标项目最终使用位置是 `.agents/skills/<skill-name>/`，公共 Skill 目录只能作为方法来源或验证器来源，不能作为项目机制 Skill 的最终安装位置。
- 强化恢复所依赖的持久化文件说明：`agent-lanes/agent-registry.json`、`agent-lanes/message-log.jsonl`、`agent-lanes/dashboard.md`、各泳道 `worklog.md`、`workspace/` 和 GOAL docs 是新线程接管旧线程的真实依据。
- 补齐发布包版本说明机制：以后每次模板升级都必须更新本文件，再重新生成 zip 和 manifest。

### 新增/确认包含

- `goal-development-base/.agents/skills/lane-recovery-runner/SKILL.md`
- `goal-development-base/.agents/skills/lane-recovery-runner/agents/openai.yaml`
- `orchestrator-recovery-template.md`
- `PERSISTENT-RUNTIME-FILES.md`
- `LANE-SKILL-HOOK-MATRIX.md`
- `goal-development-base/.codex/hooks/skill-hooks.md`
- `goal-development-base/.codex/gates/skill-mechanism-check.ps1`

### 迁移提示

把模板部署到新项目后，如果某条泳道线程不可用，不要直接丢弃旧线程上下文，也不要手工虚构新 `thread_id`。应先让可工作的 Codex 线程使用 `lane-recovery-runner`，读取持久化文件，生成恢复包，创建或确认新线程，更新 `agent-registry.json`，归档旧线程，并追加 `message-log.jsonl` 审计记录。

## 2026-07-01 / 20260701-121131

### 本次升级重点

- 在模板包中同步项目本地 Skill 规则：机制 Skill 必须落在目标项目 `.agents/skills/`。
- 确认 `lane-recovery-runner` 已进入模板和 GOAL base。
- 更新部署提示词、manifest、hook 和门禁，使新项目部署后能识别泳道恢复场景。

### 兼容说明

该版本可直接覆盖旧模板包作为新项目安装来源。已部署的旧项目不建议整包覆盖运行态目录，应按 `TEMPLATE-MANIFEST.md` 对照迁移缺失的 Skill、hook、gate 和说明文件。

## 2026-07-01 / 20260701-120248

### 本次升级重点

- 新增 `lane-recovery-runner`，固化“坏泳道/主调度线程崩溃后，新建线程接管、替换 registry、归档旧线程、写恢复包和审计记录”的流程。
- 将泳道恢复机制同步到模板包和 `docs/GOAL-Development-Base/`。

## 2026-07-01 / 20260701-114538

### 本次升级重点

- 增加持久化运行态文件说明，解释新线程如何依赖 registry、message-log、dashboard、worklog、workspace 和 GOAL docs 接管项目。
- 增加主调度恢复提示词模板。

## 2026-06-30 / 20260630-162901

### 本次升级重点

- 增加泳道与 Skill / hook 对照说明。
- 补充模板部署后的 Skill 检查入口。

## 2026-06-30 / 20260630-143513

### 本次升级重点

- 形成第一版可移植 Agent Lanes + GOAL 集成模板包。
- 提供基础部署提示词、运行态模板、邮局回报机制、dashboard 刷新脚本和 GOAL base。
# Agent Lanes GOAL Integrated Template Version History

## 2026-07-04 / 20260704-dashboard-utf8-readable-ledger-fix

### 本次升级重点

- 修复模板内 `scripts/render_dashboard.py` 的 UTF-8 中文渲染链路，避免 dashboard 标题、泳道名、状态说明、建议动作和近期产物摘要被写成 mojibake。
- 保留 `communications-readable.xlsx` 作为主要人读账本，中文表头、冻结首行、筛选、列宽、自动换行和质量状态着色保持启用。
- 增强乱码隔离：dashboard 主视图不展示 `????` 或 mojibake 原文；乱码记录只在质量/审计区展示编号、来源和处理方式，并提示需要重发 UTF-8 callback。
- 同步运行态、working-copy 和可移植模板脚本，防止后续打包或迁移新项目时重新带入坏渲染器。

### 迁移提示

已部署旧模板的项目只需要替换 `agent-lanes/scripts/render_dashboard.py`，然后运行：

```powershell
python agent-lanes\scripts\render_dashboard.py
```

如果历史 `message-log.jsonl` 已经包含乱码记录，不建议重写历史审计；让 dashboard 隔离污染即可。只有仍需业务语义的记录，才要求对应泳道重新投递 UTF-8 callback。
