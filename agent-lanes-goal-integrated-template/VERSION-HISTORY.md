# Agent Lanes + GOAL 模板版本升级说明

本文件是模板包对外发布时的版本说明入口。每次重新打包发布前，都要在这里追加一条版本记录，说明本次升级解决了什么问题、包含哪些新材料、迁移到其他项目时需要注意什么。
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
- 保留原本的风险语义：凡涉及真实调用、账号、secret、成本、外部写入、受监管操作或高风险自动化执行，仍必须先进守门泳道。
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
