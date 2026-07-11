---
name: review-runner
description: 当用户提到独立审查、总体验收、闭环审查、检查是否完成、有没有闭环缺陷、完成了吗、验收证据、审查报告、第二视角、新脑子、发布准备检查、流程审计、证据够不够、是否可以收工、是否可以发布、GOAL 完成检查、用户闭环是否推进、持续交付是否被流程拖慢、前端是否人类可读、前端中文优先、前端技术字段外露、前后端是否对齐、联调是否完成、前端后端一致性、真实接入是否完成、模型/API 是否真的跑通时，使用这个 Skill 对 GOAL 完成状态做独立审查。
---

# 独立审查器

## Agent Lanes V2 审查去抖

只有 `bundle_boundary`、`stage_boundary`、`high_risk`、`user_requested` 或 `blocking_concern` 可以触发独立审查。低/中风险本地 callback 默认延迟到功能包边界；审查结果必须写 `value_slice_id` 与真实 `value_delta`，下一泳道建议只作咨询。

目标：用独立视角找出 bug、回归、测试缺口、闭环缺口和没有证据支撑的完成声明。

## 自然语言触发词

用户提到这些词或表达时，优先使用本 Skill：

- 独立审查、总体验收、闭环审查、流程审计、第二视角、新脑子。
- 检查是否完成、完成了吗、有没有闭环缺陷、验收证据。
- 审查报告、发布准备检查、安全/认证/数据审查。
- 证据够不够、是否可以收工、是否可以发布、GOAL 完成检查。
- 用户闭环是否推进、持续交付是否被流程拖慢、是不是又在证明局部零件。
- 前端是否人类可读、前端中文优先、前端技术字段外露。
- 前后端是否对齐、联调是否完成、前端后端一致性。
- 真实接入是否完成、模型/API 是否真的跑通、Provider 是否已接入。

## 输入

优先读取：

- 当前 GOAL。
- `docs/00-project-state.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/capability-status.json`
- `docs/capability-provider-contract.md`，当审查涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider。
- 当前 diff 或变更文件。
- 测试、构建、浏览器或运行证据。

## 核心契约

审查员必须像没有参与开发的新脑子。不要替实现者辩护，先找风险和证据缺口。

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、GOAL log、review/release/report 正文或模板说明时，默认写中文。专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文和外部引用标题可以保留英文或原文。验收时需要核对新增项目文档是否遵守中文优先；不遵守时至少记录 concern，影响用户理解时应打回。

审查也要按风险分级投入。`review-runner` 不是每个低风险小切片的必经站；它优先用于高风险、完成声明、跨模块、用户可见闭环、真实线上调用、数据写入、发布/交付和连续流程失效。

多泳道协作下，`review-runner` 默认审查主调度聚合后的证据包，而不是对每条低风险泳道 callback 都启动完整审查。只有 callback 互相冲突、缺少新鲜证据、进入阶段边界、准备声明用户可用/客户可用/发布可用，或风险达到中高等级时，才需要完整验收泳道介入。

高风险、大功能或阶段边界审查采用两步视角，但不增加两轮重审：

1. 规格符合性：先判断 GOAL、用户目标、边界、前后端/Provider 接线和完成标准是否真的满足。
2. 工程质量：再检查 bug、测试缺口、数据/权限/安全风险、文档漂移和维护成本。

低风险小切片不因本规则强制进入完整审查；普通中风险可在同一纵向功能包末尾合并审查。

## 子 Agent 安排

当本轮风险等级或阶段边界需要审查时，`review-runner` 必须作为未参与本轮实现的新脑子执行，用来做 GOAL 级闭环审查。低风险小切片不必每次单独调用本 Skill。

派发时必须带上：

- 当前 GOAL 和完成标准。
- 相关项目文档。
- 变更范围。
- 代码审查结果。
- 构建、测试、浏览器、日志或交付物证据。
- 禁止事项和需要返回的证据格式。

审查不通过时，不能靠解释放行；必须回到主 Agent 修复，再重新审查。

## 审查触发强度

- `low_risk`: 文档补充、fixture 更新、只读展示或无行为变化的小修，通常只需要聚焦门禁；若用户没有要求审查，可以合并到后续阶段审查。
- `medium_risk`: 单模块代码、局部用户可见行为、后端 runner、本地真实 smoke、非破坏性输出，可以在同一纵向功能包末尾做一次合并审查。
- `high_risk`: 跨模块合同、线上 API、secret、权限、安全、数据写入、registry/source 变更、发布/交付或客户可用声明，必须立即审查。
- 审查防抖：同一纵向功能包内已经完整审查通过后，后续小修默认只做局部复核或要求补跑失败门禁。只有 P1/P2 阻塞、风险升级到 `high_risk`、触及 secret/权限/数据写入/线上 API/registry/source/发布，或用户明确要求时，才重新打开完整审查。
- 小修累计也要收敛。同一纵向能力包连续累计 3-5 个小修后，或准备声明用户可用、客户可用、生产可用前，必须做一次合并审查。
- 如果已经连续两个以上 GOAL 都是 contract/fixture/schema/handoff/readiness/evidence-only/review-surface，审查要指出流程低效风险，并要求下一步转向真实执行、前端可操作、后端到前端接线或端到端流程。
- 执行 Anti-Shell Gate：当本轮验收对象已经形成用户可见闭环且 `blocking_concerns=[]`，验收建议必须是阶段收束 / `Next Mainline Slice Selection`，不得建议继续同类 handoff、readiness、browser smoke、screenshot、evidence-only、review surface、status panel 或 summary wrapper。只有发现 P1/P2 阻塞时，才允许建议最小同类修复。
- 多泳道低风险 callback 已经被主调度聚合且证据一致时，可以记录为 `review_deferred_until_boundary`；不要为了形式对每条泳道回报生成完整审查报告。

## 用户闭环审查字段

从 2026-07-01 起，完整验收必须额外判断本轮是否推进用户可用闭环，而不是只判断局部能力是否安全。

验收输出应包含：

- `active_user_loop`: 本轮审查对应的用户闭环。
- `user_loop_progress`: `advanced`、`neutral`、`blocked` 或 `regression`。
- `blocking_concerns`: 真的阻塞当前 `active_user_loop` 的问题，才允许成为下一轮自动派发依据。
- `backlog_concerns`: 不阻塞当前用户闭环的质量、性能、体验、bundle、source、真实数据或文档后续项。
- `recommended_next_type`: `vertical_loop`、`blocker_fix`、`boundary_review`、`backlog_only` 或 `defer_review_until_boundary`。

如果本轮作为 review 泳道 completion callback 回报，上述字段必须进入 JSON 原文，供 dashboard / xlsx 展示和主调度节奏判断；不能只写在聊天总结里。

判定规则：

- 如果验收通过但 `user_loop_progress=neutral`，结论可以是 `DONE_WITH_CONCERNS`，但下一步应回到主调度做产品路线选择，不应自动派同一 capability 的下一层 gate。
- 如果 concern 只是 bundle 过大、真实样本质量 blocker 未解除、source 还可更细、截图还可更多，默认归入 `backlog_concerns`，除非它直接让当前入口不可用、误导用户或破坏边界。
- 低风险、本地-only、证据一致的小切片可以记录为 `review_deferred_until_boundary`；不要为了每个 callback 生成完整验收链。
- 审查员不得把 `backlog_concerns` 写成“下一步必须继续开发同类壳层”。推荐动作应优先指向纵向用户闭环、P1/P2 blocker fix 或阶段合并审查。

## 审查重点

- bug 和行为回归。
- 完成标准是否真的有新鲜证据，或复用 evidence 是否已经检查仍有效。
- 测试、构建、浏览器或运行验证是否覆盖目标。
- 文档是否与实际行为一致。
- 安全、隐私、数据、权限和发布风险。
- 带前端项目要检查前端状态、后端/API/CLI/schema/fixture、数据适配、错误状态和门禁证据是否互相一致。
- 用户可见前端必须检查 Human-Readable Frontend Gate：主阅读层是否中文优先，是否用人话说明状态、判断、证据、风险和下一步；raw enum、JSON key、内部状态名、source path、artifact path、validator status、rerun command、thread/message id、DOM/API 名、脚本名或调试字段是否只出现在折叠详情、审计抽屉、开发者诊断或报告来源层。
- 如果 GOAL 声称完成用户可见流程，必须能说明用户在哪里操作、数据从哪里来、失败时看到什么、哪条命令或测试证明它可运行。
- 如果 GOAL 声称用户可用，必须具备一个入口、一个真实或固定 fixture 输入、一个真实输出或可复用 artifact、一个失败状态、一个复跑命令或自动门禁、一个可查看结果的位置。
- 如果 GOAL 只完成后端或只完成前端，审查结论必须明确它是局部完成还是闭环完成，并写出下一层缺口。
- 对本地桥接、浏览器调用本地能力、权限、认证和数据写入类变更，必须检查 allowlist、权限边界、输入限制、失败状态和复跑证据。
- 涉及外部 API、云端 Provider、本地模型、CLI、SDK、媒体处理工具或其他真实运行依赖时，必须审查接入成熟度：`contract_defined`、`dependency_available`、`real_smoke_passed`、`real_sample_output_saved`、`integration_connected`、`quality_reviewed`、`production_ready`。
- 审查模型、Provider、CLI、SDK、媒体工具或外部服务时，必须优先核对 `docs/capability-status.json`：成熟度是否与证据一致、输出是否可复用、授权/预算是否清楚、下一步消费路径是否真实存在。
- registry 审查必须检查能力粒度是否合理；若同一 provider 的普通生成、参考输入、长文本、批量 worker、CUDA/CPU、同步/异步、线上/本地风险不同，不应被一个成熟度笼统覆盖。
- registry 审查必须检查 `scripts/validate-capability-status.ps1` 是否通过；如果项目尚未提供该脚本，应把缺口交给 `gate-runner`。
- mock、stub、pytest monkeypatch 只能证明代码路径和错误处理，不能作为 provider/model/API maturity 提升证据。
- 审查真实执行失败时，要确认是否属于路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线问题；若是，必须在同一 GOAL 内小范围修复并复跑同一真实路径，不能退回 fake/check。
- 审查真实执行通过后，要确认 artifact/evidence 已保存，输出已接入本轮目标里的下游消费路径，`docs/capability-status.json` 已更新，registry 校验和相关聚焦门禁已运行。
- 媒体类能力要按层级审查：audio fixture 只能证明音频路径，不能宣称完整 video/raw-video/scene-split/atom 闭环；video fixture、scene split、transcript evidence、materialization 和 selectable atom 是不同成熟度。
- 小型音频/JSON fixture 可以进入项目仓库；大视频、长音频、模型样本应使用外部路径、生成脚本或 fixture README，避免项目包膨胀。
- 审查外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider 时，必须核对 provider 解耦：业务流程和前端是否只依赖内部能力合同；真实依赖是否位于 adapter/CLI wrapper/受控本地服务后；README/manifest/smoke/evidence 是否足以让后续更换 provider。
- 如果只做到 fake/check/contract，审查必须说明真实执行为什么不可行、缺少哪个依赖或缺少哪项用户授权；不能通过“已接入”结论。
- 对本地已安装、不会产生外部费用或远程副作用的依赖，缺少真实 smoke/样本 evidence 时应列为缺口。
- 对线上 API、付费模型、外部平台或会改变远程状态的能力，必须检查授权语句、次数/预算上限、固定输入、任务 id/响应摘要、输出 artifact、复用策略和 secret 不落盘证据。
- 真实样本输出不等于生产放行；审查要区分能跑通、样本可读、已接入工作流、质量可用和生产可用。
- 审查边界文案时要执行 Dynamic Boundary Gate：`quality_reviewed`、`production_ready`、provider/live API、secret、scheduler、writeback、受监管操作、高风险自动化执行、production feed、真实远程资源或真实外部状态变化不能被写成永久禁区。审查可以接受“本轮未推进”作为范围说明，但如果用户已授权或任务目标就是推进这些能力，必须要求给出受控授权、证据和下一成熟度路径。
- completion callback 或 dashboard 如果只写“没有触碰 provider/live API、secret、scheduler、production feed 或高风险外部执行”而没有说明这是本轮范围、待授权状态还是下一步可推进路径，至少记为 `backlog_concerns`；如果它导致主线停滞或误导目标态，则升级为 `blocking_concerns`。
- 是否有应该记录到 `.codex/signals/` 的流程失败。

## 输出

更新 `docs/05-review-report.md`，包含：

- 审查范围。
- 按严重程度排序的问题。
- 必须修复项。
- 已审查的验证证据。
- 闭环结论。

如果没有阻塞问题，明确说明，并列出剩余风险。

## 打回条件

- 阻塞问题未修复。
- 修复后未重新验证。
- 只检查文件存在，没有检查行为和验收证据。
- 审查没有覆盖 GOAL 的关键完成标准。
- 高风险、大功能或阶段边界审查只看代码质量，没有先判断规格/用户目标是否满足。
- 带前端项目没有检查前端、后端/契约和联调证据是否一致。
- 用户可见前端主阅读层出现大量程序代码式、审计日志式或普通用户难以理解的信息，或者没有中文优先文案，却声明前端可用。
- 模型/API/Provider 接入没有说明真实执行成熟度，或把 fake/check/contract 当成真实接入完成。
- 对低风险小切片无理由要求完整审查，导致主线交付被流程记录拖慢。
- 同一纵向功能包内的小修无 P1/P2、无风险升级、无高风险边界变化，却反复要求完整审查。
- 多泳道低风险 callback 证据一致，却逐条触发完整审查，导致主调度无法合并推进。
- 涉及模型、Provider、CLI、SDK 或外部服务的完成声明没有同步 `docs/capability-status.json`，或 registry 成熟度高于真实证据。
- 用 mock/stub/pytest monkeypatch 的结果推进 provider/model/API maturity。
- 真实执行成功后缺少 evidence、下游消费、registry 更新或聚焦门禁。
- 真实执行接线失败修复后没有复跑同一真实 CLI/API/model 路径。
- 用 audio fixture 跑通结果宣称完整 video/raw-video/scene-split/atom 闭环。
- 声称用户可用，但缺少入口、真实或固定 fixture 输入、真实输出或 artifact、失败状态、复跑命令/门禁、可查看结果位置中的任一项。
- 涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider 时，没有 provider adapter/CLI wrapper 边界，却宣称能力可替换或已可集成。
- 同一 provider 的多个风险不同子能力被一个 maturity 混写，导致审查无法判断真实完成范围。

## 信号记录

如果审查发现的不是单个代码错误，而是可复发的流程问题，例如 GOAL 不可验证、开发未跑门禁、文档没有更新、原型复用被误判、发布证据缺失，在 `.codex/signals/` 写 signal。

## 完成门禁

只有阻塞问题都修复，并且重新验证或明确无需重新验证后，审查才算通过。
