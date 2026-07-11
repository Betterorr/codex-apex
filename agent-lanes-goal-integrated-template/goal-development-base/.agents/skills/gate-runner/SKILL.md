---
name: gate-runner
description: 当用户提到门禁、自动门禁、检查、跑验证、跑测试、跑构建、typecheck、lint、格式检查、CI、本地验收、浏览器验收、证据、不能口头通过、程序判断、发布检查、必需文档检查、验收脚本、检查脚本、质量门、冒烟测试、真实 smoke、真实样本、API 联通、模型联通、Provider 门禁时，使用这个 Skill 运行、整理或创建项目级自动门禁。
---

# 门禁执行器

## Product Value Gate

派发前运行 `python agent-lanes/scripts/product_value_gate.py --dispatch-file <dispatch.json>`。低风险聚焦证据写入 Value Slice workspace，避免每个 callback 都追加巨型 GOAL/review 文档。

目标：把可程序判断的完成条件变成真实门禁，而不是只写在提示词里。

## 自然语言触发词

用户提到这些词或表达时，优先使用本 Skill：

- 门禁、自动门禁、检查、跑验证、跑测试、跑构建。
- typecheck、lint、格式检查、CI、本地验收、浏览器验收。
- 证据、不能口头通过、程序判断、卡住底线、验收脚本、检查脚本、质量门。
- 发布检查、必需文档检查、审查门禁、冒烟测试。
- 真实 smoke、真实样本、API 联通、模型联通、Provider 门禁。

## 输入

优先读取：

- 当前 GOAL 和完成标准。
- `docs/00-project-state.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/05-review-report.md`
- `docs/06-release-record.md`
- `docs/capability-status.json`
- `docs/capability-provider-contract.md`，当门禁涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider。
- `.codex/gates/`
- 项目的构建、测试、lint、类型检查、运行和发布脚本。

## 核心契约

门禁负责卡住底线。构建失败、测试失败、审查失败、必需文档缺失、发布记录缺失时，不能靠解释放行。

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、GOAL log、review/release/report 正文或模板说明时，默认写中文。专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文和外部引用标题可以保留英文或原文。文档语言门禁应检查新增项目文档是否出现大段英文正文；发现时打回修改或记录 concern。

门禁也负责控制流程成本。不要把所有切片都升级成全量 CI、全量审查和完整发布检查；按风险等级选择最小足够门禁。

多泳道协作下，门禁按泳道变更面选择并由主调度聚合。规划/设计泳道通常跑文档、JSON/JSONL、机制或一致性检查；开发泳道跑代码、构建、测试、CLI 或浏览器门禁；守门泳道跑权限、Provider、registry 和授权边界检查；验收泳道只在阶段边界、中高风险或证据冲突时要求完整审查门禁。

风险分级：

- `low_risk`: 文档、fixture、只读展示、局部测试、无行为变化的小修。运行相关文件/局部命令即可。
- `medium_risk`: 单模块代码、局部 UI、后端 runner、本地真实 smoke、非破坏性输出。运行相关单元/CLI/前端 build 或桥接验证。
- `high_risk`: 跨模块合同、线上 API、secret、权限、安全、数据写入、registry/source 变更、发布/交付。运行完整相关门禁和独立审查门禁。

## 门禁类型

按项目实际情况组织这些门禁：

- 构建门禁：build、compile、package。
- 测试门禁：unit、integration、e2e、regression。
- 静态门禁：lint、typecheck、format check。
- 文档门禁：必需 docs 是否存在，相关文档是否更新。
- 契约门禁：API/CLI/schema/fixture 是否可验证，前端适配层是否消费同一份数据合同。
- 前端门禁：构建、类型检查、浏览器冒烟、关键页面状态和失败状态是否可见。
- 联调门禁：最小端到端路径、受控入口、权限边界、错误状态、复跑命令和证据文件是否存在。
- 真实执行门禁：外部 API、云端 Provider、本地模型、CLI、SDK、媒体处理工具或其他真实运行依赖，是否已经按条件跑过真实 smoke/样本，并保存可复用 artifact。
- 授权门禁：线上 API、付费模型、外部平台或会改变远程状态的能力，是否有用户授权、次数/预算上限、固定输入、secret 不落盘规则和复用策略。
- 接线门禁：真实输出是否已被下一步工作流、安全适配层、前端证据面板、报告、队列或后续 CLI/API 消费。
- 能力状态门禁：涉及模型、Provider、CLI、SDK 或外部服务时，检查 `docs/capability-status.json` 是否记录成熟度、证据路径、授权/预算、复跑命令、下一步消费路径和过期条件。
- Registry 结构门禁：运行 `scripts/validate-capability-status.ps1`，检查 JSON 可解析、必需字段存在、成熟度合法、证据字段完整，并在证据标记为 present/verified 且路径不是占位符时检查路径存在。
- Provider 解耦门禁：涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider 时，检查是否存在项目内 adapter/CLI wrapper、README/manifest 或等价说明；业务流程和前端不得直接依赖模型目录、Vendor SDK、API key 或一次性脚本。
- 用户可用门禁：声明用户可用时，检查是否存在入口、真实或固定 fixture 输入、真实输出或可复用 artifact、失败状态、复跑命令或自动门禁、可查看结果位置。
- 真实执行自收尾门禁：真实 CLI/API/model 跑通后，检查 artifact/evidence、下游消费、capability registry、registry 校验和相关聚焦门禁是否完成。
- mock 边界门禁：mock、stub、pytest monkeypatch 只能证明代码路径，不能作为 provider/model/API maturity 提升证据。
- 媒体 fixture 门禁：audio fixture、video fixture、scene split、transcript evidence、materialization 和 selectable atom 必须分层判断，不能用音频样本冒充完整视频或 atom 闭环。
- 审查门禁：`code-reviewer` 和 `review-runner` 是否通过。
- 发布门禁：启动、日志、回滚、冒烟测试、配置项、隐私和安全记录。
- 运行门禁：本地服务、浏览器流程、CLI 输出、下载物或交付物存在。

## 真实执行门禁策略

- `fake`、`fixture`、`check` 只能证明合同、映射或依赖边界，不能证明真实接入完成。
- mock、stub、pytest monkeypatch 只能证明代码路径和错误处理，不能推进 maturity。
- 本地已安装、不会产生外部费用或远程副作用的依赖，门禁应优先升级为 `real_smoke` 或 `real_sample`。
- 线上 live call 只有在用户授权、次数/预算上限和 secret 边界存在时运行；否则门禁应输出 `pending_user_approval`，而不是通过。
- Dynamic Boundary Gate：`quality_reviewed`、`production_ready`、provider/live API、secret、scheduler、writeback、受监管操作、高风险自动化执行、production feed、真实远程资源或真实外部状态变化不是永久禁止项。门禁输出要区分 `needs_auth`、`authorized_ready`、`authorized_verified`、`scope_not_advanced_this_round` 和 `out_of_scope`；已有授权时不得继续用“未触碰”作为阻塞理由。
- 如果已有同输入、同 provider、同参数摘要的 evidence，默认验证并复用该 artifact；只有用户批准或 evidence 过期/不适用时才重复 live call。
- 如果 `docs/capability-status.json` 显示已有可复用 evidence，门禁默认验证 artifact 是否存在、结构是否可读、参数摘要是否匹配，而不是重复生成。
- 门禁输出要区分 `runtime_verified`、`sample_output_verified`、`integration_connected`、`quality_reviewed` 和 `production_ready`。
- 真实执行写文件时必须使用临时目录、outputs、artifacts、evidence 或隔离目录，不能覆盖源文件或生产数据。
- 真实执行失败如果属于路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线问题，修复后必须复跑同一真实路径；只跑 mock 或合同门禁不能替代复跑。

## 聚焦门禁策略

- 优先运行最接近变更面的门禁：改前端先跑前端 build/bridge，改 CLI 先跑对应 CLI fixture/focused tests，改 Skill 先跑 Skill/机制门禁。
- 全量测试或完整发布门禁只在高风险、跨模块、发布/交付或聚焦门禁无法覆盖风险时运行。
- 如果某个 evidence 已经存在且输入/provider/参数摘要未变，默认做 artifact 存在性和结构验证，不重复生成。
- 门禁报告要区分“本轮新运行验证”和“复用旧 evidence 后验证结构/存在性”。旧 evidence 未检查时不能作为完成证据。
- 门禁输出要写明本次选择的是聚焦门禁还是完整门禁，以及为什么足够。
- 同一纵向功能包内，完整审查门禁已经通过后，小修默认只要求补跑失败门禁或相关聚焦门禁；只有 P1/P2、风险升级、高风险边界变化或用户明确要求，才重新要求完整审查门禁。
- 同一纵向能力包连续累计 3-5 个小修后，或准备声明用户可用、客户可用、生产可用前，要求一次合并审查门禁。
- 多泳道并行任务先运行各自聚焦门禁，再由主调度合并证据；只有共享合同、真实联调、发布、权限或数据写入边界变化时，才升级为跨泳道完整门禁。

## 输出

更新或补充：

- `docs/04-goal-log.md`：记录本次门禁运行结果。
- `docs/05-review-report.md`：记录审查门禁结果。
- `docs/06-release-record.md`：记录发布门禁结果。
- `docs/capability-status.json`：记录真实执行能力的门禁状态、证据或过期条件变化。
- `.codex/gates/`：必要时补充项目级门禁脚本或说明。

如果本轮作为 guardian / gate 泳道 completion callback 回报，JSON 必须额外包含：

- `active_user_loop`: 本轮门禁保护的用户闭环。
- `loop_impact`: `advanced`、`blocked`、`regression_fixed` 或 `neutral`；若只是证据补齐，要说明解除哪个用户可见交付阻塞。
- `blocking_concerns`: 真正阻塞当前用户闭环或必须用户授权的风险。
- `backlog_concerns`: 不阻塞当前闭环、应进入 backlog 或阶段合并审查的风险。
- `recommended_next_type`: `vertical_loop`、`blocker_fix`、`boundary_review`、`backlog_only` 或 `defer_review_until_boundary`。

## 打回条件

- 存在失败门禁。
- 只声明“应该通过”，没有本轮命令、日志、截图、产物证据，或没有对复用 evidence 做有效性检查。
- 审查报告仍有阻塞问题。
- 必需文档缺失或明显过期。
- 涉及模型、Provider、CLI、SDK 或外部服务时，`docs/capability-status.json` 缺少对应条目或证据路径，却宣称能力已接入。
- `scripts/validate-capability-status.ps1` 失败，却宣称相关 provider/model/API/CLI 能力完成。
- 涉及外部 API、本地模型、CLI、SDK、媒体工具或云端 Provider 时，业务流程或前端绕过 provider adapter/CLI wrapper 直接绑定真实依赖。
- 用 mock/stub/pytest monkeypatch 作为 provider/model/API maturity 提升证据。
- 真实执行成功后缺少 artifact/evidence、下游消费、registry 更新或相关聚焦门禁。
- 真实执行接线失败修复后没有复跑同一真实 CLI/API/model 路径。
- 用 audio fixture 结果宣称完整 video/raw-video/scene-split/atom 闭环。
- 外部 API、Provider、本地模型或真实运行依赖只有 fake/check/contract，却宣称已经真实接入。
- 线上 live call 缺少授权、次数/预算上限、secret 边界或可复用 artifact 策略。
- 带前端项目缺少必要的契约、前端构建或联调证据，却宣称用户流程完成。
- 发布相关 GOAL 缺少启动、日志、回滚或冒烟证据。
- 低风险切片无理由要求完整发布/审查门禁，导致流程成本明显高于风险。
- 同一纵向功能包内的小修无 P1/P2、无风险升级、无高风险边界变化，却反复要求完整审查门禁。
- 多泳道低风险任务已经有各自聚焦门禁，却无理由要求所有泳道重复全量门禁。
- 声称用户可用，但缺少入口、真实或固定 fixture 输入、真实输出或 artifact、失败状态、复跑命令/门禁、可查看结果位置中的任一项。

## 信号记录

如果门禁失败暴露出可复发流程问题，例如某类测试长期缺失、GOAL 没写验证方式、发布记录总是漏日志或回滚，在 `.codex/signals/` 写 signal。

## 完成门禁

只有相关门禁全部通过，或明确标为不适用并说明原因，`gate-runner` 才算通过。
