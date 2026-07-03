---
name: dev-planner
description: 当用户提到开发计划、实现计划、技术方案、拆阶段、phase、里程碑、任务拆解、先后顺序、依赖、并行工作、构建命令、测试命令、运行命令、风险、回滚、怎么开发、规划一下开发、技术路线、先做哪一步、开发路线图、分阶段交付、风险拆解、验收路径、前端后端计划、前后端联调计划、分层推进、纵向切片、多泳道协作计划、泳道依赖、Sketch Plan Loop、骨架计划循环、Skeleton Plan Refresh、骨架优先、产品骨架路线、完成度、整体推进、项目还差什么时，使用这个 Skill 创建或更新 docs/03-dev-plan.md。
---

# 开发计划器

目标：产出一份可以按阶段执行、按证据验收的开发计划。

## 自然语言触发词

用户提到这些词或表达时，优先使用本 Skill：

- 开发计划、实现计划、技术方案、架构计划、规划一下开发。
- 拆阶段、phase、里程碑、任务拆解、先后顺序、依赖关系。
- 并行工作、构建命令、测试命令、运行命令、验证方式。
- 风险、阻塞、回滚、开发路线、技术路线、开发路线图、分阶段交付、风险拆解、验收路径、怎么做、先做哪一步。
- 前端后端计划、前后端联调计划、分层推进、纵向切片。
- 多泳道协作计划、泳道依赖。
- Sketch Plan Loop、骨架计划循环、Skeleton Plan Refresh、骨架优先、产品骨架路线。
- 完成度、整体推进、项目还差什么、太慢、先打通、全链路。

## 输入

优先读取：

- `docs/00-project-state.md`
- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- 已有原型或原型代码。
- 现有代码结构。
- 现有包管理、构建、测试配置。

## 核心契约

开发计划不是任务清单，而是验收路线图。每个阶段都必须能运行、能看见、能测试或能交付证据。

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、GOAL log、review/release/report 正文或模板说明时，默认写中文。专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文和外部引用标题可以保留英文或原文。

## 多泳道下的按需计划

启用 Agent Lanes 后，`dev-planner` 负责解决跨泳道依赖和阶段路线不清，而不是把每次“继续”都变成重写计划。

- 简单低风险任务可以由主调度直接派发到对应泳道，不必先更新完整 `docs/03-dev-plan.md`。
- 当规划、设计、守门可以并行时，计划应标出并行泳道、合并点、阻塞条件和谁负责最终验收，而不是强制串行阶段。
- 当 callback 已经提供足够上下文时，计划只需要做滚动更新，补下一条最高价值纵向闭环；不要重复展开已完成阶段。
- 只有在前后端/Provider/联调顺序不清、跨泳道依赖冲突、风险/回滚不清或阶段边界到来时，才需要完整计划更新。
- 计划输出应帮助 `project-orchestrator` 少派无效任务：写清哪些工作可以并行，哪些必须等待，哪些低风险任务可以跳过正式 GOAL 创建。

## 骨架计划模式

当主调度触发 Skeleton Plan Refresh 时，`dev-planner` 不只是重写阶段列表，而是维护 目标项目的产品骨架路线：

```text
用户/对象/任务范围选择
-> 数据源或输入接入
-> 标准化数据 artifact
-> 核心处理、规则、模型或业务逻辑融合
-> 结果评分、解释或决策辅助
-> 前端业务工作台
-> 评估 / dry-run / 仿真
-> 报告、复盘或交付物
-> 报告、复盘或交付物
-> 生产接入评估
```

计划必须区分四种 pass：

- `Skeleton Pass`: 先打通能跑的主流程，允许 fixture 或受控样本，但必须有入口、输出、失败状态和复跑命令。
- `Real Pass`: 把关键节点换成真实执行，例如真实 provider、真实样本、真实 adapter、真实本地计算或真实下游消费。
- `Quality Pass`: 做质量、解释性、体验、稳定性、错误处理、性能和审查。
- `Production Pass`: 做批量、回滚、权限、日志、发布、成本、隐私和高风险真实执行/外部写入边界。

规划必须给出一个粗粒度完成度判断，用于主调度自主推进，不作为对外承诺：

- `0-60%`: Skeleton Pass，先补产品骨架空环和可见主流程。
- `60-80%`: Real Pass，把关键 fixture 换成真实只读样本、真实本地计算或真实 provider adapter。
- `80-90%`: Quality Pass，补质量、解释性、错误状态、体验、稳定性和合并审查。
- `90%+`: Production/Paper Pass，只能进入打包、长跑验证、发布准备或生产接入评估；不得跳过受控验证直接进入高风险真实执行。

每次 Skeleton Plan Refresh 至少回答：

- 哪一环是空白。
- 哪一环只有假数据或 fixture。
- 哪一环只有后端没有前端。
- 哪一环只有前端没有真实执行。
- 哪一环已经 current-stage-good-enough，应暂停深挖。
- 哪些 capability 已经连续推进 2-3 个 GOAL，需要 capability exit check。
- 接下来 3-6 个最高价值薄纵向切片是什么，每一刀补哪一环。
- 哪一刀可以由主调度自动派发落实，哪一刀必须先取得用户确认。

计划刷新输出应写入 `docs/03-dev-plan.md`，必要时同步 `docs/00-project-state.md` 的 Current GOAL / Next GOAL。不要把所有 provider、模型、指标一次性规划成串行大工程；优先选择能让骨架更接近端到端可运行的一刀。

## 规划标准

- 每个阶段都有可观察结果。
- 优先薄纵向切片，不堆不可见基础设施。
- 大任务或高风险任务的计划必须写清关键文件、验证命令、预期证据和打回条件；低风险“继续”不要求展开成冗长计划。
- 明确阶段依赖和可并行工作。
- 明确验证命令、浏览器验收或人工验收步骤。
- 明确哪些现有代码、原型代码或设计资产要复用。
- 明确风险、回滚方式和阻塞条件。
- 每个声称用户可用的阶段都必须规划：入口、真实或固定 fixture 输入、真实输出或 artifact、失败状态、复跑命令或自动门禁、可查看结果位置。
- 每个阶段都必须标注属于 `Skeleton Pass`、`Real Pass`、`Quality Pass` 还是 `Production Pass`。
- 每个阶段都必须标注补的是产品骨架哪一环，以及它是否让全链路更接近可运行。
- 对带前端的项目，每个阶段标注主要层次：需求/设计、后端或契约、前端、联调、门禁或发布。
- 优先安排薄纵向切片，让一个用户可见工作流能从数据来源、业务动作、前端状态、失败状态到验证证据闭环。
- 如果先做后端或契约，必须说明哪个前端场景会消费它；如果先做前端，必须说明数据来源是真实 API/CLI/fixture/schema 还是原型占位。
- 联调阶段必须写清楚入口、数据流、权限边界、错误状态、复跑命令和证据路径。
- 涉及模型、Provider、CLI、SDK、媒体工具或外部 API 时，计划必须包含 `docs/capability-status.json` 的能力 id、成熟度目标、证据路径、授权/预算边界和 `scripts/validate-capability-status.ps1` 门禁。
- 若同一 provider 存在普通生成、参考输入、长文本、批量 worker、CUDA/CPU、同步/异步、线上/本地等不同风险或验证方式，应在计划中拆成多个 capability 或 variants。

## 打回条件

- 阶段只描述“搭基础”，没有可验收结果。
- 计划没有验证命令或验收方式。
- 大任务或高风险任务没有关键文件、验证命令、预期证据和打回条件。
- 原型代码存在但没有复用策略。
- 阶段之间依赖不清。
- 风险被口头带过，没有缓解或回滚方式。
- 带前端项目的计划只堆后端或只堆页面，没有说明前后端数据契约和联调阶段。
- 声称用户可用的阶段缺少入口、真实或固定 fixture 输入、真实输出或 artifact、失败状态、复跑命令/门禁、可查看结果位置中的任一项。
- 涉及模型、Provider、CLI、SDK、媒体工具或外部 API，却没有规划 capability registry 和 registry 校验门禁。
- 计划只围绕某个 provider/capability 继续追加 wrapper、readiness、operator decision、readonly surface、handoff proposal 或 apply readiness，却没有说明它仍是产品骨架的直接硬阻塞。
- 计划没有给出接下来 3-6 个最高价值薄纵向切片，或没有说明哪些骨架环节仍为空。

## 输出

更新 `docs/03-dev-plan.md`，至少包含：

- 架构说明。
- 产品骨架路线和当前缺口。
- `Skeleton Pass` / `Real Pass` / `Quality Pass` / `Production Pass` 阶段表。
- 阶段列表。
- 带前端项目的分层推进表，说明前端、后端/契约、联调和门禁如何衔接。
- 常用命令。
- 可并行工作。
- 回滚说明。

同步更新 `docs/00-project-state.md` 的当前阶段和下一个 GOAL。

如果本轮作为 planning 泳道 completion callback 回报，JSON 必须额外包含：

- `active_user_loop`: 本轮规划服务的用户闭环。
- `loop_impact`: `advanced`、`blocked`、`regression_fixed` 或 `neutral`；普通规划任务应说明它如何让下一刀更接近用户闭环。
- `blocking_concerns`: 真正阻塞当前用户闭环的规划/依赖问题。
- `backlog_concerns`: 不阻塞当前闭环、应进入 backlog 或阶段合并审查的事项。
- `recommended_next_type`: `vertical_loop`、`blocker_fix`、`boundary_review`、`backlog_only` 或 `defer_review_until_boundary`。

## 信号记录

当用户纠正规划粒度、原型复用、阶段顺序或验收方式时，在 `.codex/signals/` 记录 signal。

## 完成门禁

只有当 `goal-creator` 可以不猜范围和验证方式、直接把下一阶段写成 GOAL 时，开发计划才算完成。

## 与前端工作流 Skill 的协作

当开发计划涉及前端底座、React/Vite/Next 技术栈、UI 组件库、金融图表组件、AG Grid / TanStack Table、TradingView Lightweight Charts、ECharts、TanStack Query、Zustand、Dock Layout / Split Pane、目录结构、模块边界、Design Token、主题、多语言或 数据 数据合同，先使用 `frontend-workflow-planner`。

开发计划必须把它输出的 `frontend_stack`、`data_contract`、`module_boundaries`、`output_paths` 和 `acceptance_evidence` 转成可验收切片，写入 `docs/03-dev-plan.md`。如果涉及新依赖、复制外部代码、license/source attribution、provider live call、secret、scheduler、真实远程写入、高风险资源或 production feed，计划必须先转 `guardian`，不能直接派 `development`。
