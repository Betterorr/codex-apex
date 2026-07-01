---
name: dev-builder
description: 当用户提到实现、开始开发、执行 GOAL、完成这个阶段、改代码、做这个功能、继续开发、按计划开发、把它做出来、跑起来、修到通过、实现 phase、开发闭环、进入开发、按 dev plan 做、完成这个任务、实现 MVP、代码落地、联调、前后端联调、前端接后端、后端接前端、数据契约落地、真实接入、真实调用、模型接入、API 接入、Provider 接入、单能力聚焦预算、capability exit check、provider 深挖收敛、薄纵向切片、骨架计划下一刀、Sketch Plan Loop、Skeleton Plan Refresh 时，使用这个 Skill 执行一个 GOAL 或开发阶段。
---

# 开发执行器

目标：实现一个边界清晰的 GOAL，并用证据闭环。

## 自然语言触发词

用户提到这些词或表达时，优先使用本 Skill：

- 实现、开始开发、改代码、做这个功能、把它做出来。
- 执行 GOAL、完成这个阶段、实现 phase、按计划开发、继续开发。
- 跑起来、修到通过、开发闭环、验证后再完成。
- 根据 dev plan 做、进入开发、完成这个任务、实现 MVP、代码落地、联调。
- 前后端联调、前端接后端、后端接前端、数据契约落地。
- 真实接入、真实调用、模型接入、API 接入、Provider 接入。
- 单能力聚焦预算、capability exit check、provider 深挖收敛。
- 薄纵向切片、骨架计划下一刀、Sketch Plan Loop、Skeleton Plan Refresh。

## 输入

优先读取：

- 当前 GOAL。
- `docs/00-project-state.md`
- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- `docs/03-dev-plan.md`
- `docs/capability-status.json`
- `docs/capability-provider-contract.md`，当 GOAL 涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider。
- `.codex/goals/goal-template.md`
- 当前代码和测试配置。

## 核心契约

开发不是写完代码就结束。必须形成与风险匹配的证据闭环：

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、GOAL log、review/release/report 正文或模板说明时，默认写中文。专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文和外部引用标题可以保留英文或原文。

```text
低风险：开发 -> 聚焦自测 -> 直接相关文档/日志 -> 完成
中风险：开发 -> 相关门禁 -> 必要修复 -> 功能包末尾合并审查 -> 完成
高风险：开发 -> 自测 -> 独立审查 -> 修复 -> 复审 -> 文档更新 -> 完成
```

## 执行规则

- 编辑前先理解现有项目模式。
- 改动范围贴合 GOAL，不做无关重构。
- 优先复用既有代码、设计资产和原型代码。
- 执行前先确认当前 GOAL 是否来自最新 Skeleton Plan 或 `docs/03-dev-plan.md` 的骨架计划；如果计划过期、局部过深或没有说明补哪条产品骨架链路，先回到 `project-orchestrator`/`dev-planner` 做 Skeleton Plan Refresh。
- 每个 GOAL 开始前必须回答：它补的是产品骨架哪一环；做完是否让全链路更接近可运行；如果只是局部优化，为什么现在必须做；做完后下一个非同能力骨架节点是什么。
- 默认执行薄纵向切片：优先把入口、数据/fixture、处理、可查看输出、失败状态、复跑命令和证据连起来，而不是把单个点做到很精再离开。
- 如果当前任务只会新增 wrapper、readiness、operator decision、readonly surface、handoff proposal 或 apply readiness，必须先确认它解除的是当前用户可见闭环的直接硬阻塞；否则把它放入 backlog 或授权队列。
- 开始实现前标注本 GOAL 风险等级：`low_risk`、`medium_risk` 或 `high_risk`。风险等级决定验证、审查和文档强度。
- `low_risk` 包括文档补充、fixture 更新、只读前端展示、局部测试补齐、无行为变化的小修。执行聚焦验证并记录证据即可；通常不需要完整独立审查、完整发布记录或全量测试。
- `medium_risk` 包括单模块代码、局部用户可见行为、后端 runner、本地真实 smoke、非破坏性输出。运行相关门禁；独立审查可以合并到同一纵向功能包末尾，不必每个微切片都单独审查。
- `high_risk` 包括跨模块合同、线上 API、secret、权限、安全、数据写入、registry/source 变更、发布/交付或客户可用声明。必须完整门禁和独立审查。
- 优先完成用户可用的纵向功能包。若当前任务只是 contract/fixture/schema/handoff/readiness/evidence-only/review surface，检查最近两个切片；如果已经连续两次类似，先转向真实执行、前端可操作、后端到前端接线或端到端流程。
- 用户可用能力至少具备一个入口、一个真实或固定 fixture 输入、一个真实输出或可复用 artifact、一个失败状态、一个复跑命令或自动门禁、一个可查看结果的位置。只完成后端、只完成前端、只完成合同、只保存孤立样本，都只能算局部完成。
- 带前端项目开发时，先判断当前 GOAL 属于后端/契约、前端、联调还是门禁；输出和文档都要保留这个判断。
- 做后端/API/CLI/schema/fixture 时，必须说明哪个前端流程会消费这些字段、动作、状态或错误；若没有消费方，不能把它当成用户可见闭环。
- 做前端时，必须说明数据来源是真实 API/CLI/fixture/schema、适配层还是原型 mock；未接入能力要标为预留、禁用或演示，不能伪装成真实执行。
- 做联调时，优先选择最小安全纵切，并补齐固定入口、复跑命令、失败状态、证据文件和权限边界。客户端或浏览器不得接受任意本地命令或越权操作；本地桥接应使用 allowlist、静态证据或受控 API。
- 做外部 API、云端 Provider、本地模型、CLI、SDK、媒体处理工具或其他真实运行依赖时，完成标准不能只停在 fake/check/contract。除非缺少依赖、输入或用户明确禁止，至少要跑一个真实 smoke 或最小真实样本。
- 做外部 API、云端 Provider、本地模型、CLI、SDK、媒体处理工具或其他真实运行依赖时，默认先实现 provider adapter/CLI wrapper，而不是把真实依赖直连到业务流程或前端。项目仓库保存 wrapper、manifest、README、受控 smoke/CLI、schema 和 evidence；模型权重、虚拟环境、WSL 环境、云账号、SDK 缓存和大媒体样本作为外部依赖记录，不打包进主程序。
- 涉及模型、Provider、CLI、SDK、媒体处理工具或外部服务时，必须读取并维护 `docs/capability-status.json`：记录能力 id、成熟度、证据路径、授权状态、预算/次数限制、复跑命令、下一步消费路径和过期条件。registry 缺失时可以创建最小条目，但不能把创建 registry 当成真实接入完成。
- 能力粒度要贴近真实调用方式。若同一 provider 同时包含普通生成、参考输入、长文本、批量 worker、CUDA/CPU、同步/异步、线上/本地等明显不同风险或验证方式，应拆成多个 capability 或在 capability 下使用 variants，不能用一个成熟度覆盖所有子能力。
- 真实执行失败时先分类：路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线问题属于同一 GOAL 内应修复的问题。修复后必须复跑同一真实 CLI/API/model 路径和相关聚焦门禁；不要退回 fake/check，也不要等待用户提示下一步。
- 真实执行通过后必须自收尾：保存 artifact/evidence，把输出接到本轮目标里的下游消费路径，更新 `docs/capability-status.json`，运行 registry 校验和相关聚焦门禁，并说明哪些仍不是用户可用、完整媒体闭环或生产可用。
- mock、stub、pytest monkeypatch 只能证明代码路径和错误处理，不能推进 provider/model/API 的 maturity。maturity 只能由真实 CLI/API/model 输出、真实 artifact、真实下游消费或质量审查推进。
- 媒体类 fixture 要按层级声明：audio fixture 只能证明音频路径，不能宣称完整 video/raw-video/scene-split/atom 闭环；video fixture、scene split、transcript evidence、materialization 和 selectable atom 是不同成熟度。
- 小型音频/JSON fixture 可以进入项目仓库；大视频、长音频、模型样本应使用外部路径、生成脚本或 fixture README，避免项目包膨胀。
- 本地已安装、不会产生外部费用或远程副作用的依赖，默认可以真实运行；输出必须保存为可复用 evidence/artifact，并记录 provider、版本/路径、输入摘要、参数摘要、耗时、输出路径、错误/警告和复跑命令。
- 线上 API、付费模型、外部平台或会改变远程状态的能力，必须先向用户请求明确授权；授权请求要包含调用目的、固定输入样例、次数/预算上限、secret 不落盘规则、输出保存位置和复用策略。
- 用户暂未授权 live call 时，只能完成合同、readiness、适配层或待执行队列，并把真实调用状态标成 `pending_user_approval`；不能用 fake/check 冒充已接入。
- 真实输出生成后，应尽量接到下一步工作流、安全适配层、前端证据面板、报告、队列或后续 CLI/API；孤立样本只能算 `real_sample_output_saved`，不能算 `integration_connected`。
- 模型或 Provider 接入完成声明必须写清成熟度：`contract_defined`、`dependency_available`、`real_smoke_passed`、`real_sample_output_saved`、`integration_connected`、`quality_reviewed` 或 `production_ready`。
- 同一用户能力包最多允许 2-3 个准备性切片。若已经连续完成 contract/fixture/schema/readiness/evidence-only 等准备工作，下一步必须优先做真实运行、前端可操作入口、后端到前端接线或端到端样本。
- 单个 provider/capability 不能连续占用太多 GOAL。若当前 GOAL 继续围绕同一 ASR、TTS、OCR、下载器、本地模型、外部 API、生成模型、支付/发布接口等 capability 深挖，并且最近 2-3 个 GOAL 已经属于同一 capability，执行前必须确认 `project-orchestrator` 已做 Capability Exit Check；没有确认时，先在本轮做轻量 exit check 并把结论写入输出。
- Capability Exit Check 必须判断当前成熟度、真实样本或真实 smoke、下游消费路径、剩余人工决策/授权/预算/真实写入/质量审查需求，以及该 capability 是否仍是下一条用户可见闭环的直接硬阻塞。
- 如果该 capability 已达到 current-stage-good-enough，dev-builder 不应继续添加 wrapper、readiness、operator decision、readonly surface、handoff proposal、apply readiness 等壳层；应把剩余优化写入 backlog 或显式授权队列，并把当前 GOAL 改向前端入口、前后端联调、端到端样本、核心业务流程、报告、打包、发布或另一个关键 capability。
- 只有当 capability 仍是直接硬阻塞时才继续实现；输出必须写清本 GOAL 解除的具体阻塞，以及完成后要切换到哪个 non-same-capability loop。
- 验证失败时继续修复，不用解释替代修复。
- 能用 `gate-runner` 执行的检查必须先进入门禁。
- 完成声明必须引用本轮或当前 GOAL 内的新鲜证据：刚运行的命令、刚检查的 artifact/evidence、或刚验证仍有效的可复用 evidence。旧 evidence 未复核时，只能说“未重新验证”或 `DONE_WITH_CONCERNS`。
- 修改 `docs/capability-status.json` 后必须运行 `scripts/validate-capability-status.ps1`，或说明项目尚未提供该门禁并让 `gate-runner` 补齐。
- 高风险、跨模块、secret、权限、数据写入、线上 API、registry/source 修改、发布/客户可用声明必须进入 `review-runner`；普通用户可见小改若是低/中风险，可以先用聚焦门禁闭环，并在功能包末尾合并审查。
- 无法运行的验证要写明原因和剩余风险。

## 子 Agent 规则

默认主 Agent 贯穿实现。只有两种情况派发子 Agent：

- 需要干净第二视角，例如 review。
- 多块任务互不依赖，可以并行。

派发时必须带上：当前 GOAL、相关文档、变更范围、验收标准、禁止事项、需要返回的证据格式。

风险分级的新脑子步骤：

- 低风险小切片：聚焦验证通过、文档证据清楚即可；不强制 `code-reviewer` 或 `review-runner`。
- 中风险切片：相关门禁必须跑；`code-reviewer` 或 `review-runner` 可以在同一纵向功能包末尾合并执行。
- 高风险切片：代码改动完成后，先用 `gate-runner` 运行构建、测试、类型检查、文档和审查相关门禁；再交给 `code-reviewer` 或 `review-runner` 做未参与实现的独立审查。
- GOAL 准备宣称生产可用、客户可用、真实线上调用可用、数据写入可用或发布可用时，必须进入 `review-runner`。
- 同一纵向功能包已经完整审查通过后，后续小修不得自动重新触发完整 `review-runner`；除非出现 P1/P2 阻塞、风险升级到 `high_risk`、触及 secret/权限/数据写入/线上 API/registry/source/发布，或用户明确要求。默认只补跑失败门禁、相关聚焦门禁或局部复核。
- 同一纵向能力包连续累计 3-5 个小修后，或准备声明用户可用、客户可用、生产可用前，必须做一次合并审查，避免小风险堆积成中风险。
- 审查不通过时，主 Agent 修复后重新进入同一审查门禁，直到通过或明确阻塞。

## 输出

更新：

- 相关代码和测试。
- `docs/capability-status.json`，当模型、Provider、CLI、SDK 或外部服务成熟度、证据、授权或下一步消费路径变化时。
- `docs/04-goal-log.md`，记录中高风险、阶段边界、真实执行、失败修复或用户可见能力变化；低风险小修可以只保留命令/产物证据。
- 受影响的产品、设计、开发计划或变更记录；低风险小修不强制全量文档更新。
最终汇报必须包含骨架执行判断：本 GOAL 属于 `Skeleton Pass`、`Real Pass`、`Quality Pass` 或 `Production Pass`；补了哪条产品骨架链路；是否让全链路更接近可运行；下一条建议的非同能力骨架节点是什么。

最终汇报使用轻量状态词：`DONE`、`DONE_WITH_CONCERNS`、`NEEDS_CONTEXT` 或 `BLOCKED`。状态词不能替代证据；也不能因为状态词而对低风险小切片新增完整审查。

## 打回条件

- 构建、测试、类型检查或关键手动验收失败。
- `gate-runner` 有失败门禁。
- 审查有阻塞问题。
- 文档与实际行为不一致。
- 完成声明缺少本轮/当前 GOAL 新鲜证据，或复用旧 evidence 但没有检查有效性。
- 外部 API、Provider、本地模型或真实运行依赖只有 fake/check/contract，却宣称已经接入。
- 用 mock/stub/pytest monkeypatch 的结果推进 provider/model/API maturity。
- 真实执行失败属于路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线问题，却没有在同一 GOAL 内修复并复跑真实路径。
- 真实执行成功后没有保存 evidence、没有接到下游消费路径、没有更新 capability registry 或没有跑相关聚焦门禁。
- 用音频 fixture 跑通结果宣称完整 video/raw-video/scene-split/atom 闭环。
- 将大视频、长音频或模型样本直接放入项目包，而不是使用外部路径、生成脚本或 fixture README。
- 需要线上 live call 但没有用户授权、次数/预算上限、secret 边界或可复用 artifact 策略。
- 带前端项目只完成后端却宣称用户流程完成，或只完成静态前端却宣称真实能力已接入。
- 联调缺少固定入口、复跑命令、失败状态、证据文件或权限边界。
- 连续多个 GOAL 只增加 contract/fixture/schema/handoff/readiness/evidence-only/review surface，却没有推进真实执行、前端可操作、后端到前端接线或端到端用户流程。
- 同一 capability 连续 2-3 个 GOAL 后继续追加 wrapper/readiness/operator decision/readonly surface/handoff proposal/apply readiness 壳层，却没有 Capability Exit Check、直接硬阻塞说明或后续 non-same-capability loop。
- 对低风险小切片无理由运行完整发布/审查流程，导致主线交付被流程记录拖慢。
- 同一纵向功能包内的小修无 P1/P2、无风险升级、无高风险边界变化，却反复触发完整 `review-runner`。
- 声称用户可用，但缺少入口、真实或固定 fixture 输入、真实输出或 artifact、失败状态、复跑命令/门禁、可查看结果位置中的任一项。
- registry 成熟度覆盖了风险明显不同的多个子能力，导致普通生成、参考输入、长文本、批量、CUDA/CPU、同步/异步或线上/本地状态被混在一起。

## 信号记录

当实现中出现可复用失败，例如验证漏跑、原型复用误判、范围漂移、审查遗漏时，在 `.codex/signals/` 记录 signal。

## 完成门禁

所有完成标准都有证据，阻塞审查问题已关闭，相关文档已更新后，才能报告完成。
