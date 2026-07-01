# GOAL 开发基座

本项目使用文档驱动的 GOAL 工作流。

## 运行原则

人负责方向决策和最终验收。Codex 负责澄清、规划、实现、验证、审查、更新文档，并记录可复用的失败信号。

## Sketch Plan Loop / 骨架优先推进

本项目默认采用“先打产品骨架，再逐层加深”的推进方式。GOAL Skill 不能只寻找下一件局部能做的事，也不能长期围绕单个 provider、模型、API、指标或页面壳层深挖。

当用户提到“完成度、太慢、整体推进、计划、项目还差什么、骨架、先打通、全链路”，或最近连续 3-5 个 GOAL 都集中在同一局部能力时，主调度应先触发一次轻量 Skeleton Plan Refresh，而不是直接进入开发。

通用产品骨架链路是：

```text
用户输入
-> 数据/素材进入
-> 处理/生成
-> 人工审核
-> 组合/编排
-> 输出/渲染
-> 报告/交付
```

每个开发 GOAL 必须说明它补的是哪一环，是否让全链路更接近可运行。如果只是局部优化，必须说明为什么它仍是当前用户可见闭环的直接硬阻塞；否则应把优化放入 backlog 或授权队列，切回最高价值的产品纵向闭环。

## Agent Lanes 集成

本项目同时使用 `agent-lanes/` 作为多智能体泳道运行态。

- 主调度泳道负责读取项目状态、判断下一步、派发结构化任务、接收完成回报。
- 规划泳道负责需求、范围、验收标准、任务切片。
- 设计泳道负责 UI/UX、信息架构、页面状态、原型和设计验收标准。
- 开发泳道负责按已批准 GOAL 实现、修复、验证和提交证据。
- 守门泳道负责权限、secret、外部 API、provider、隐私、付费调用、发布和平台风险。
- 验收泳道负责独立检查目标、实现、文档、风险和新鲜证据。
- 进化泳道负责把重复失败、用户纠正和稳定流程改进沉淀到模板、skill、hook 或门禁。

非主调度泳道完成主调度派发任务后，必须：

1. 写本泳道 `worklog.md`。
2. 生成 completion callback JSON。
3. 调用 `agent-lanes/scripts/deliver_callback.py` 把完整 callback 投递给回报邮局；邮局再写入 `agent-lanes/message-log.jsonl` 作为审计备份。
4. 默认不由单泳道发送短 wake。邮局将 callback 合并成一条 `thread_prompt`；泳道拿到 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 后，必须只用 `send_message_to_thread` 发送这一条合并原文消息。若返回 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log` 记录，说明回报尚未真正送达；必须重跑投递或记录阻塞，不能要求主调度去 message-log 自取原文。
5. 在最终回复保留 `status`、`evidence`、`next_recommended_lane`。

主调度处理 callback 时默认直接阅读邮局发来的合并原文消息，不再先回复“去 message-log 读取完整 callback”。只有证据冲突、疑似重复、需要审计或用户要求追溯时，才打开 `agent-lanes/message-log.jsonl` 按 `message_id` 或 `reply_to + from_agent + task_type` 去重查证。

泳道沟通默认使用中文。`summary`、`concerns`、`next_recommended_action`、worklog 正文、dashboard 展示文本、线程回复正文尽量写中文；`status`、`task_type`、`message_id`、`thread_id`、`file path`、命令、代码标识、API 名、JSON key、错误原文等保留英文或原文。

## 项目文档中文优先

本模板部署到目标项目后，所有面向项目协作的文档默认使用中文，包括 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard 展示文本、GOAL log、review/release/report 正文、provider card 说明和模板说明。

除非用户明确要求英文，或内容属于专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文、外部引用标题，否则不要把正文写成英文。主调度派发泳道任务时必须把这条作为 `language_rule` 放入上下文；验收和门禁发现新增项目文档大段英文正文时，应打回修改或记录 concern。

平时统一查看入口是 `agent-lanes/dashboard.md`。需要刷新时运行：

```powershell
python agent-lanes\scripts\render_dashboard.py
```

完整收发记录只生成并优先打开 `agent-lanes/communications-readable.xlsx`；机器审计和 raw 字段追溯使用 `agent-lanes/message-log.jsonl`，不再额外导出 CSV。Dashboard 负责快速看状态，xlsx 账本负责保存完整摘要、产物、证据、关注点和建议动作。

## 多泳道协作下的 Skill 瘦身

本项目启用 `agent-lanes/` 后，GOAL Skills 不再按单 Agent 固定流水线机械执行。Skill 负责职责契约和完成标准，泳道负责并行产物，主调度负责合并、补派和切换方向。

- 规划、设计、守门之间没有强依赖时，可以并行派发；主调度等待 completion callback 后合并，而不是固定“需求->设计->守门”串行等待。
- 主调度的一条结构化泳道任务可以替代正式 `goal-creator`，前提是它已经包含目标、范围、完成标准、验证证据、禁止事项和回报格式。
- `dev-planner` 只在跨泳道依赖、阶段顺序、前后端/Provider/联调路线、风险或回滚不清时使用；普通低风险继续任务可以直接派发。
- `review-runner` 默认审查主调度聚合后的证据包。低风险泳道 callback 不逐条完整验收；阶段边界、用户可见完成声明、中高风险、证据冲突或阻塞问题才触发完整验收。
- `gate-runner` 按泳道变更面运行聚焦门禁，再由主调度聚合证据；不要因为多泳道存在就自动全量 CI、全量审查或完整发布门禁。
- 自进化由真实失败、用户纠正或稳定 signal 触发，不因为每轮多泳道 callback 都自动运行。

## 文件安全规则

禁止批量删除文件或目录。

不要使用：

- `del /s`
- `rd /s`
- `rmdir /s`
- `Remove-Item -Recurse`
- `rm -rf`

需要删除文件时，只能一次删除一个明确路径的文件，例如：

```powershell
Remove-Item "C:\path\to\file.txt"
```

如果需要批量删除文件，应停止操作，并让用户手动删除。

使用这个循环：

```text
GOAL -> clarify -> plan -> build -> verify -> independent review -> document -> release record
```

没有证据，不要宣称完成。

默认采用“轻量继续模式”：普通“继续/下一步”只读取当前状态、开发计划、目标日志、能力状态 registry 和当前切片直接相关文件；只有状态冲突、阶段边界、高风险、发布/交付、用户要求复盘、判断不清、用户反馈与状态文档不一致或 registry 证据过期时，才升级为完整复盘。

完成声明必须绑定新鲜证据。主 Agent 只有在本轮或当前 GOAL 内刚运行过验证命令、检查过 artifact/evidence、或确认过可复用证据仍有效时，才能报告完成；如果依赖旧证据，必须说明可能过期和剩余风险。

普通输出使用轻量状态词，减少长篇复盘：

- `DONE`: 完成标准满足，并有新鲜证据。
- `DONE_WITH_CONCERNS`: 主闭环完成，但仍有非阻塞风险或质量待审。
- `NEEDS_CONTEXT`: 缺少用户决策、输入样本、授权或产品取舍。
- `BLOCKED`: 已确认存在阻塞，当前无法靠本地修复继续推进。

## 本地 Skills

任务匹配时，优先使用 `.agents/skills/` 里的本地 Skill：

所有用于维护当前项目 GOAL / Agent Lanes 机制运作的 Skill 都必须项目本地化：默认创建、改造和读取位置是 `.agents/skills/<skill-name>/`。`C:\Users\...\ .codex\skills` 或其他公共 Skill 目录只能作为方法来源、验证器来源或临时参考，不能作为当前项目机制 Skill 的最终安装位置。若从公共 Skill、外部 Skill 或系统 Skill 吸收方法，必须改造成项目内本地版，产物回写当前项目 `docs/`、`agent-lanes/`、`.codex/` 或泳道 workspace，并同步到可移植模板。

- `project-orchestrator`: 用户说“下一步/继续”时，先读项目状态，再综合选择合适的本地 Skill 推进闭环。
- `product-spec-builder`: 把模糊想法逼问成 `docs/01-product-spec.md`。
- `design-brief-builder`: 把产品意图转成 `docs/02-design-brief.md`。
- `prototype-builder`: 基于需求和设计产出原型方案、原型验收标准或可复用原型代码。
- `dev-planner`: 把需求、设计和原型拆成 `docs/03-dev-plan.md` 里的可验收阶段。
- `goal-creator`: 在目标、范围、完成标准或验证方式不清时写出精确 GOAL；多泳道低风险派发可由结构化任务替代。
- `dev-builder`: 执行一个 GOAL 或阶段，验证并更新文档。
- `bug-fixer`: 对真实缺陷进行复现、定位、修复、回归验证和信号沉淀。
- `gate-runner`: 运行或创建项目级自动门禁，把构建、测试、审查、发布检查变成程序化证据。
- `code-reviewer`: 对代码改动做独立代码审查，检查 bug、测试缺口、风险和文档漂移。
- `review-runner`: 做独立审查，并更新 `docs/05-review-report.md`。
- `release-builder`: 准备 `docs/06-release-record.md` 中的发布证据。
- `requirements-traceability-runner`: 吸收需求追踪方法，把需求、设计、实现、验证和证据映射写回 `docs/05-review-report.md` 或泳道 workspace，避免产物旁路分散。
- `frontend-quality-runner`: 只吸收 `interface-design` 和 `frontend-design` 两个前端设计来源，把信息架构、页面状态、截图验收和可读性问题写回 `docs/02-design-brief.md`、`docs/05-review-report.md` 或 `artifacts/`。
- `open-source-research-runner`: 吸收 `github-research` 和开源分析方法，把开源候选、license、维护度、依赖和守门边界写回 `docs/08-open-source-reference-pool.md`、`docs/09-research-roadmap.md` 或泳道 workspace。
- `systematic-debugging-runner`: 吸收系统化调试方法，要求复现、数据流追踪、单假设验证和同路径回归，并把结论写回 `docs/04-goal-log.md`、相关泳道 worklog、`docs/05-review-report.md` 或 artifact。
- `lane-recovery-runner`: 当泳道线程崩溃、过长、无法提交消息或需要新建替换时，基于持久化运行态文件完成新线程创建、registry 更新、旧线程归档、恢复提示词投递和审计记录。
- `evolution-runner`: 在明确边界内把真实失败、用户纠正和稳定项目约束变化转成对本地 Skill、hook、门禁和项目规则的改进。
- `goal-methodology-guide`: 解释和维护 GOAL 方法论、Skill 使用时机、脚本门禁、自进化和子 Agent 规则。

## 自然语言 Hook

用户不需要 slash 调用 Skill。只要普通表达命中相关词，就应自动选择对应本地 Skill。

维护路由表：

- `.codex/hooks/skill-hooks.md`

触发词必须同时写进：

- 对应 `SKILL.md` 的 frontmatter `description`。
- 对应 `SKILL.md` 正文的“自然语言触发词”段。

如果新增或改造 Skill，也必须补充 hook 路由和机制检查。

## 文档上下文

把这些文件当作项目记忆：

- `docs/00-project-state.md`
- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/05-review-report.md`
- `docs/06-release-record.md`
- `docs/capability-status.json`
- `docs/capability-provider-contract.md`
- `docs/CHANGELOG.md`
- `.agents/skills/goal-methodology-guide/references/GOAL-methodology-abstract.md`
- `.agents/skills/goal-methodology-guide/references/usage-playbook.md`

任何产品、设计、实现、验证或发布变化，都要更新受影响文档。

低风险小修不强制全量文档更新。中风险能力包可以在功能包末尾合并更新。高风险、阶段边界、真实执行、用户可见能力变化、发布/交付必须更新相关文档和证据。

## 能力状态 Registry

模型、Provider、CLI、SDK、媒体处理工具或外部服务接入状态必须进入 `docs/capability-status.json`。

默认采用 Provider 解耦。凡是外部 API、云端平台、本地模型、CLI、SDK 或媒体工具，都必须按 `docs/capability-provider-contract.md` 走三层结构：项目内部能力合同 -> provider adapter/CLI wrapper -> 真实依赖。业务流程和前端不能直接绑定某个模型目录、Vendor SDK、API key 或一次性脚本。

每个 provider 至少要有项目内 wrapper/manifest/README/smoke 或等价说明；模型权重、虚拟环境、WSL 环境、云账号、SDK 缓存和大媒体样本保留为外部依赖，不打包进主程序。主程序只打包受控 CLI、adapter、manifest、安装说明、证据读取和复跑命令。

每个能力至少记录：

- 能力 id、类型、provider、运行位置。
- 成熟度：`contract_defined`、`dependency_available`、`real_smoke_passed`、`real_sample_output_saved`、`integration_connected`、`quality_reviewed`、`production_ready`。
- 证据路径、复跑命令、输入摘要、输出路径。
- 授权状态、预算/次数上限、secret 不落盘规则。
- 下一步消费路径和 evidence 过期条件。

registry 是调度依据，不是完成证据本身。创建或更新 registry 不能替代真实 smoke、真实样本、前后端接线或质量审查。

能力粒度要贴近真实调用方式。若同一 provider 同时包含普通生成、参考输入、长文本、批量 worker、CUDA/CPU、同步/异步、线上/本地等明显不同风险或验证方式，应拆成多个 capability 或在 capability 下使用 variants，不能用一个成熟度覆盖所有子能力。

registry 必须通过 `scripts/validate-capability-status.ps1`。该门禁至少检查 JSON 可解析、必需字段存在、成熟度合法、证据字段完整；当证据标记为 present/verified 且路径不是占位符时，还应检查路径是否存在。

真实执行闭环必须自收尾。模型/API/CLI/provider 的真实调用失败时，如果失败属于路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线问题，主 Agent 应在同一 GOAL 内小范围修复并复跑聚焦门禁；只有涉及线上费用、secret、破坏性写入、权限扩大、source/registry 写入或产品取舍时才停下来请求用户确认。

真实调用通过后，主 Agent 不应等待用户提示下一步；应自动保存 artifact/evidence，把输出接到本轮目标里的下游消费路径，更新 `docs/capability-status.json`，运行 registry 校验和相关聚焦门禁，并明确哪些部分仍不是用户可用或生产可用。

mock、stub、pytest monkeypatch 只能证明代码路径和错误处理，不能推进 provider/model/API 的 maturity。maturity 只能由真实 CLI/API/model 输出、真实 artifact、真实下游消费或质量审查推进。

媒体类 fixture 要按层级声明：audio fixture 只能证明音频路径，不能宣称完整 video/raw-video/scene-split/atom 闭环；video fixture、scene split、transcript evidence、materialization 和 selectable atom 是不同成熟度。小型音频/JSON fixture 可以进入项目；大视频、长音频、模型样本应使用外部路径、生成脚本或 fixture README，避免模板或项目包膨胀。

## 单能力聚焦预算 / Capability Exit Check

单个 provider/capability 不能连续占用太多 GOAL。ASR、TTS、OCR、下载器、本地模型、外部 API、生成模型、支付/发布接口等能力都适用本规则。

- `project-orchestrator` 在同一 capability 连续推进 2 个 GOAL 后，下一次调度前必须做 Capability Exit Check；连续 3 个 GOAL 后默认停止继续深挖，除非它仍是当前用户可用闭环的直接硬阻塞。
- Exit Check 至少判断：当前成熟度级别；是否已有真实样本或真实 smoke；是否已经被下游流程消费；剩余工作是否需要人工决策、授权、预算、真实写入或质量审查；它是否仍然是下一条用户可见流程的直接硬阻塞。
- 如果已达到 current-stage-good-enough，停止围绕该 capability 追加 wrapper、readiness、operator decision、readonly surface、handoff proposal、apply readiness 等壳层。
- 剩余优化进入 backlog 或显式授权队列；下一步切回最高价值产品纵向闭环，例如前端可操作入口、前后端联调、端到端样本、核心业务流程、报告、打包、发布或另一个关键能力。
- 只有当该 capability 仍是当前用户可用闭环的直接硬阻塞时，才允许继续深挖；GOAL 必须写清本轮解除哪个具体阻塞，以及完成后切到哪个 non-same-capability loop。
- `dev-builder` 接到同一 capability 深挖 GOAL 时，必须确认调度器已经给出 exit check；没有时先补轻量 exit check，并把结论写入输出或 `docs/04-goal-log.md`。

## 用户可用能力定义

声称某项能力“用户可用”时，至少要具备：

- 一个用户或调用方能触达的入口。
- 一个真实或固定 fixture 输入。
- 一个真实输出或可复用 artifact。
- 一个失败状态或错误反馈。
- 一个复跑命令或自动门禁。
- 一个可查看结果的位置。

只完成后端、只完成前端、只完成合同、只保存孤立样本，都只能算局部完成，不能称为用户可用闭环。

## GOAL 要求

GOAL 必须包含：

- 具体结果。
- 范围边界。
- 完成标准。
- 验证证据。
- 文档更新。
- 验证失败后的循环规则。

如果 GOAL 模糊，先重写，或只追问能让完成状态可验证的问题。

## 审查门禁

对高风险、用户可见、跨模块、安全、认证、数据、发布或关键流程改动，必须使用独立审查。

审查输出必须先列问题。阻塞问题必须修复并重新验证后，才能宣称完成。

审查防抖：同一纵向能力包已经通过完整独立审查后，小修默认只跑失败门禁或聚焦门禁。只有 P1/P2、风险升级、高风险边界变化、secret/权限/数据写入/线上 API/registry/source/发布，或用户明确要求时，才重新触发完整审查。

小修累计也要收敛。同一纵向能力包连续累计 3-5 个小修后，或准备声明用户可用、客户可用、生产可用前，必须做一次合并审查，避免小风险堆积成中风险。

可以吸收外部工程纪律，但不得大幅增加 token 和流程成本。大任务、高风险或阶段边界审查时，先检查“规格/用户目标是否满足”，再检查代码质量；低风险和普通中风险小切片不因此新增强制子 Agent、严格 TDD 或完整审查。

## 自动门禁

能用程序判断的完成条件，不要只写在提示词里。

这些情况必须尽量进入 `gate-runner` 或 `.codex/gates/`：

- 构建失败不能完成。
- 测试失败不能完成。
- 类型检查、lint 或格式检查失败不能完成。
- 审查失败不能完成。
- 必需文档缺失或过期不能进入下一阶段。
- 发布前启动、日志、回滚、冒烟测试、隐私/安全记录缺失不能宣称可发布。
- `docs/capability-status.json` 结构错误、成熟度非法、必需字段缺失或 verified/present 证据路径不存在时，不能宣称相关 provider/model/API/CLI 能力完成。
- 真实执行暴露的接线失败本身就是有效证据，必须记录在 GOAL log、capability registry 或相关 evidence 中；修复后要复跑同一真实路径，而不是退回 fake/check。

如果同一用户能力包已经连续 2-3 个切片都是合同、fixture、schema、readiness、handoff、evidence-only 或 review surface，下一步必须优先转向真实执行、前端可操作入口、后端到前端接线或端到端样本；除非缺少用户授权、依赖不可用或存在 P1/P2 阻塞。

## 外部依赖 / API / 模型真实接入

如果项目包含外部 API、云端 Provider、本地模型、CLI、SDK、媒体处理工具或其他真实运行依赖，Skill 体系不能长期停在 fake、check、contract 或 readiness。

通用接入成熟度：

```text
contract_defined -> dependency_available -> real_smoke_passed -> real_sample_output_saved -> integration_connected -> quality_reviewed -> production_ready
```

运行原则：

- 本地已安装、不会产生外部费用或远程副作用的依赖，默认应主动进入真实 smoke 或最小真实样本测试。
- 线上 API、付费模型、外部平台或会改变远程状态的能力，Agent 应主动向用户请求一次明确授权，说明调用目的、输入样例、次数/预算上限、secret 边界和输出复用策略。
- 用户授权后可以真实调用；调用后必须保存可复用 evidence/artifact，后续门禁默认复用，避免重复消耗。
- 如果用户给出覆盖一组 provider、模型或依赖的站立授权，主调度应把授权范围、默认调用上限、固定输入、费用上限、secret 不落盘和仍然排除事项写入 `docs/capability-status.json` 或 `docs/capability-provider-contract.md`。后续同范围内安装、dry-run、metadata 检查和受控 smoke 不再逐条打回确认卡；超出范围、需要 token/付费预算、券商/交易、scheduler、生产 feed 或投资建议声明时仍必须重新守门。
- 用户暂未授权时，允许推进合同、适配、readiness 和排队计划，但必须把 live call 标成 `pending_user_approval`，不能用 fake/check 冒充已接入。
- 真实 smoke 不等于生产可用；必须继续区分“能跑通”“样本可读”“已接到工作流”“质量通过”“生产可用”。
- 客户端或浏览器不得直接执行任意本地命令、读取 secret 或绕过受控后端/CLI/API 适配层。

## 带前端项目的分层推进

如果项目包含前端、后端/API/CLI、数据契约或本地桥接，`project-orchestrator` 必须在“继续/下一步”时判断当前最缺的是需求/设计、后端或契约、前端、联调、门禁还是审查。

- 后端或契约阶段必须说明哪个前端场景会消费它。
- 前端阶段必须说明数据来源是真实 API/CLI/fixture/schema、适配层还是原型占位。
- 联调阶段必须有固定入口、权限边界、错误状态、复跑命令和证据文件。
- 连续多个阶段偏向同一层时，下一次继续必须检查另一层和联调层是否已经落后。

## 子 Agent / 新脑子规则

默认由主 Agent 贯穿项目，不要过早拆成大量子 Agent。

以下步骤必须安排“新脑子”：

- 代码实现后：用 `code-reviewer` 做未参与实现的代码级独立审查。
- GOAL 完成前：用 `review-runner` 做闭环审查，核对完成标准、证据和文档更新。
- 发布前涉及安全、隐私、权限、数据或生产风险时：用独立审查视角检查发布记录和风险。
- 新 session 发现 `.codex/signals/` 有具体待处理信号，且信号指向 Skill、hook、门禁或流程规则时：用 `evolution-runner` 独立消化信号并在边界内落地规则修改。

只有两类任务适合派子 Agent：

- 需要干净第二视角，例如代码审查、产品审查、安全审计、发布审查。
- 多块任务互不依赖，可以并行推进。

派发子 Agent 时必须带走完整上下文：

- 当前 GOAL。
- 相关文档。
- 变更范围。
- 验收标准。
- 禁止事项。
- 已有验证证据。
- 需要返回的证据格式。

主 Agent 保留最终合并和拍板权。子 Agent 是另一颗脑子，不是另一个文件夹。

## 信号

当真实失败或用户纠正暴露出可复用流程规则时，在 `.codex/signals/` 下写一条简短记录。

只保留能防止真实复发的规则。规则过时或不再有用时，要删除。

