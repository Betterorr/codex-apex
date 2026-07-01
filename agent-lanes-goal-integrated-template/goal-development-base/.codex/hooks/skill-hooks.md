# Skill 自然语言 Hook 路由表

目的：让用户不需要 slash 调用 Skill，只要在当前项目对话里提到相关词，Codex 就应优先选择对应本地 Skill。

> 真正影响 Skill 自动触发的是各 `SKILL.md` frontmatter 的 `description`。本文件是当前项目的维护用总表；修改触发词时，要同步更新对应 `SKILL.md` 的 `description` 和“自然语言触发词”段。

| Skill | 常见触发词 |
| --- | --- |
| `project-orchestrator` | 下一步、继续、接着做、往下推进、自动推进、轻量继续、高速产品工程经理、综合调用、总调度、根据当前项目状态决定做什么、继续闭环、推进项目、从当前状态开始、按 GOAL 流程继续、接手继续、你自己判断下一步、自动往后走、别问我先看项目、需求讨论、路线讨论、技术路线、我有个想法、我觉得、我们讨论一下、持续迭代、自动落档、脱手、自主迭代、自动规划、自动落实、callback hook、callback 打断主调度、主调度被打断、主调度收件箱、callback inbox、前端后端怎么推进、前后端联调、前端后端分流、分层推进、多泳道协作、并行泳道、泳道派发、泳道排队、任务排队、任务被覆盖、回复截断、上下文覆盖、泳道被打断、真实接入、外部 API 接入、模型接入、Provider 接入、能力状态 registry、单能力聚焦预算、capability exit check、provider 深挖收敛、Sketch Plan Loop、骨架计划循环、骨架优先、完成度、太慢、整体推进、项目还差什么、全链路扫描、中文文档、文档中文、项目文档中文优先、所有文档用中文 |
| `product-spec-builder` | 需求、产品需求、PRD、需求文档、产品文档、需求澄清、范围、做与不做、用户故事、验收标准、产品想法、MVP、功能边界、帮我想清楚产品、定义第一版、目标用户、核心场景、用户痛点、业务流程、功能清单、非目标、聊聊需求、探讨需求、讨论需求、梳理需求、需求脑暴、产品脑暴、我有个想法、我想做一个、这个产品怎么定义、这个功能要不要做、需求取舍、方案取舍、第一版先做什么、先别开发、先把需求想清楚 |
| `design-brief-builder` | 设计、设计规范、设计 brief、UI、UX、交互、布局、信息架构、视觉方向、界面风格、设计参考、页面状态、空状态、产品气质、视觉规范、响应式、移动端、桌面端、可访问性、文案语气、颜色、字体、圆角、密度、聊聊界面、讨论交互、页面怎么组织、这个界面怎么设计、用户怎么操作 |
| `prototype-builder` | 原型、设计稿、高保真、线框图、可点击原型、Figma、截图转实现、设计代码、原型代码、静态原型、复用原型、页面清单、状态覆盖、按原型开发、不要重写设计、原型验收、交互演示、demo 页面 |
| `dev-planner` | 开发计划、实现计划、技术方案、拆阶段、phase、里程碑、任务拆解、依赖、并行工作、构建命令、测试命令、回滚、技术路线、先做哪一步、怎么实现、开发路线图、分阶段交付、风险拆解、验收路径、前端后端计划、前后端联调计划、分层推进、纵向切片、多泳道协作计划、泳道依赖、Sketch Plan Loop、Skeleton Plan Refresh、骨架计划循环、骨架优先、产品骨架路线、完成度、整体推进、项目还差什么 |
| `goal-creator` | GOAL、目标、写一个目标、变成 GOAL、自动执行、自主执行、闭环、完成标准、验收方式、验证方式、循环规则、下一阶段目标、可执行目标、让 AI 自己跑、不要我一步步盯、一次性跑完、失败后继续修、多泳道派发目标、泳道任务格式 |
| `dev-builder` | 实现、开始开发、执行 GOAL、完成阶段、改代码、做功能、继续开发、按计划开发、跑起来、修到通过、把它做出来、进入开发、按 dev plan 做、完成这个任务、实现 MVP、代码落地、联调、前后端联调、前端接后端、后端接前端、数据契约落地、真实接入、真实调用、模型接入、API 接入、Provider 接入、单能力聚焦预算、capability exit check、provider 深挖收敛、薄纵向切片、骨架计划下一刀、Sketch Plan Loop、Skeleton Plan Refresh |
| `bug-fixer` | bug、报错、异常、失败、坏了、不能用、测试失败、构建失败、回归、修复、fix、debug、复现、根因、定位问题、回归验证、页面点不动、流程断了、线上问题、用户反馈问题、之前好的现在坏了 |
| `gate-runner` | 门禁、自动门禁、检查、跑验证、跑测试、跑构建、typecheck、lint、CI、本地验收、浏览器验收、程序判断、验收脚本、检查脚本、质量门、不能口头通过、证据、冒烟测试、必需文档检查、真实 smoke、真实样本、API 联通、模型联通、Provider 门禁 |
| `code-reviewer` | 代码审查、code review、review 代码、看 diff、检查改动、代码风险、测试缺口、架构偏移、文档漂移、安全风险、认证权限、数据风险、回归风险、发布前代码质量、找问题不要改、独立看代码 |
| `review-runner` | 独立审查、总体验收、闭环审查、流程审计、检查是否完成、完成了吗、验收证据、审查报告、第二视角、新脑子、证据够不够、有没有闭环缺陷、是否可以收工、是否可以发布、GOAL 完成检查、前后端是否对齐、联调是否完成、前端后端一致性、真实接入是否完成、模型/API 是否真的跑通 |
| `release-builder` | 发布、上线、部署、打包、交付、release、deploy、生产就绪、试运行、发布记录、环境变量、启动方式、日志、回滚、冒烟测试、上线前检查、交接、客户交付、部署地址、运行记录、配置项、模型依赖、外部 API 依赖、Provider 依赖、依赖剥离 |
| `evolution-runner` | 进化、自进化、自净化、规则更新、沉淀规则、signals、失败信号、复盘规则、删规则、规则膨胀、问题库、调优框架、优化其他 Skill、让 Skill 更适应项目、自动进化本地 Skills、净化规则、净化 schema、调整 Skill 边界、中文文档规则、文档语言规则、所有 Skill 文档中文 |
| `goal-methodology-guide` | GOAL 方法论、这套机制、开发基座、模板包怎么用、什么时候用哪个 Skill、脚本门禁、自动门禁、自进化、沉淀规则、子 Agent、新脑子、复制出去也能懂 |
| `requirements-traceability-runner` | 需求追踪、traceability matrix、需求到设计/代码/测试映射、验收覆盖、需求漂移、哪个需求有没有实现、发布前需求闭环 |
| `frontend-quality-runner` | 前端体验质量、UI 质感、信息架构、页面可读性、文本溢出、浏览器截图验收、dashboard 好不好用、研究工作台好不好用、移动端适配 |
| `open-source-research-runner` | GitHub 调研、开源库选型、找资源、找实现、github-research、provider 候选、回测框架、图表库、金融数据源、license 评估 |
| `systematic-debugging-runner` | bug、报错、测试失败、构建失败、信息流断了、callback 没送到、门禁异常、数据接线不对、先查根因、root cause、系统化调试 |
| `lane-recovery-runner` | 泳道坏了、主调度坏了、线程崩了、线程死了、旧线程太长、failed to start turn、agent loop died unexpectedly、Error submitting message、新建泳道替换、注册替换、接管旧泳道、恢复接管、替换 thread_id、更新 registry、旧线程归档、新线程沿用原名字、主调度恢复、orchestrator recovery、坏掉的 lane recovery |

## 讨论场景 Hook 矩阵

当用户在主调度线程里自然讨论需求、计划、技术方案或临时想法时，先由 `project-orchestrator` 做 discussion intake，再按下表决定是否调用业务 Skill、是否派发泳道。Skill 调用只代表当前线程开始处理；其他泳道真正参与必须有 `send_message_to_thread` 派发，或在 `agent-lanes/message-log.jsonl` 写入 `pending_dispatch` fallback。

| 用户正在讨论什么 | 优先 Skill | 默认泳道 | 应落到哪里 | 派发条件 |
| --- | --- | --- | --- | --- |
| 探讨需求、产品想法、功能取舍、目标用户、先做什么不做什么 | `project-orchestrator` -> `product-spec-builder` | `planning` | `docs/01-product-spec.md`, `docs/03-dev-plan.md`, `agent-lanes/message-log.jsonl` | 形成稳定需求切片或验收标准时派发；只是背景/偏好时 `capture_only` |
| 探讨计划、阶段路线、优先级、里程碑、下一轮 GOAL | `project-orchestrator` -> `dev-planner`; 目标不清时加 `goal-creator` | `planning` 或 `orchestrator` | `docs/03-dev-plan.md`, `docs/04-goal-log.md`, `agent-lanes/message-log.jsonl` | 需要拆任务、定阶段或改变优先级时派发；路线锁定前用 `confirmation_needed` |
| 探讨技术方案、架构、数据源、开源库、provider/API、模型或能力接入 | `project-orchestrator` -> `dev-planner`; 涉及真实调用/secret/条款/成本时加 `gate-runner` 或 `code-reviewer` | `planning`, `guardian`; 确认后才到 `development` | `docs/09-research-roadmap.md`, `docs/13-l1-l5-information-source-architecture.md`, `docs/14-market-candidate-classification.md`, `docs/capability-status.json`, provider card | 低风险调研可记录和派规划；真实 provider/API/模型/付费/账号/交易能力必须先进 `guardian` |
| 探讨 UI、页面体验、信息架构、交互状态、面板或原型 | `design-brief-builder`; 需要 demo 时加 `prototype-builder` | `design` | `docs/02-design-brief.md`, 原型或 artifact 路径 | 有明确页面、用户操作或状态覆盖要求时派发；未确认产品方向时只写设计影响 |
| 讨论实现、联调、本地验证、脚本、fixture、端到端样本 | `dev-builder`, `bug-fixer`, `gate-runner` | `development` | `scripts/`, `artifacts/`, `moneydigger/`, `docs/03-dev-plan.md`, `docs/capability-status.json` | 需求/边界已清楚且无外部授权风险时派发；否则先 `planning` 或 `guardian` |
| 讨论验收、完成判断、证据冲突、风险复核、是否可收工 | `review-runner`, `gate-runner`, `code-reviewer` | `review` | `docs/05-review-report.md`, `agent-lanes/dashboard.md`, `agent-lanes/message-log.jsonl` | 已有产物或回报需要独立核对时派发 |
| 讨论机制、模板、hook、skill、泳道协作、重复摩擦或规则进化 | `evolution-runner`, `goal-methodology-guide` | `evolution` | `.codex/hooks/`, `.agents/skills/`, `agent-lanes/agent-lanes.md`, `docs/agent-lanes-goal-integrated-template/` | 用户明确要求优化机制，或多次流程摩擦暴露可复用规则缺口时派发 |
| 讨论项目文档语言、文档中文、英文模板看不懂、所有文档尽量中文 | `project-orchestrator` -> `evolution-runner`; 需要解释机制时加 `goal-methodology-guide` | `evolution` | `AGENTS.md`, `.agents/skills/**/SKILL.md`, `.codex/hooks/skill-hooks.md`, `.codex/gates/skill-mechanism-check.ps1`, `docs/04-goal-log.md` | 用户把语言要求明确为长期项目规则时派发；只是一份文档翻译需求时按对应业务 Skill 处理 |
| 讨论需求追踪、验收覆盖、需求是否被设计/实现/测试覆盖 | `requirements-traceability-runner` | `planning` 或 `review` | `docs/05-review-report.md`, `agent-lanes/lanes/<lane>/workspace/traceability-<message_id>.md` | 阶段验收、发布前、需求漂移或用户明确要求追踪矩阵时派发 |
| 讨论前端质感、页面可读性、信息架构或浏览器截图验收 | `frontend-quality-runner` | `design`, `development` 或 `review` | `docs/02-design-brief.md`, `docs/05-review-report.md`, `artifacts/<slice>/` | 用户可见 UI、dashboard、研究工作台或截图证据不足时派发 |
| 讨论开源库、GitHub 资源、provider 候选或外部实现选型 | `open-source-research-runner`; 涉及引入代码/依赖时加 `gate-runner` 或 `guardian` | `planning` 或 `guardian` | `docs/08-open-source-reference-pool.md`, `docs/09-research-roadmap.md`, `docs/capability-status.json`, 泳道 workspace | 需要比较维护度、license、依赖复杂度和集成边界时派发 |
| 讨论 bug、信息流断点、门禁异常、callback 投递异常或需要根因定位 | `systematic-debugging-runner`; 修复代码时再接 `bug-fixer` | `development`, `review` 或 `evolution` | `docs/04-goal-log.md`, 相关泳道 `worklog.md`, `docs/05-review-report.md`, `artifacts/<slice>/` | 需要复现、数据流追踪、单假设验证和同路径回归时派发 |
| 讨论泳道线程崩溃、旧线程过长、主调度无法提交消息、需要新建线程替换和 registry 接管 | `lane-recovery-runner`; 若暴露可复用机制缺口再接 `evolution-runner` | `orchestrator` 或对应故障泳道，必要时 `evolution` | `agent-lanes/agent-registry.json`, `agent-lanes/message-log.jsonl`, 对应泳道 `worklog.md`, `agent-lanes/lanes/<lane>/workspace/lane-recovery-*.md`, `agent-lanes/dashboard.md` | 已确认某条泳道线程不可用、过长、需要归档旧线程或替换 `thread_id` 时执行 |

Hook 结果必须归入四类：

- `capture_only`: 只记录稳定信息，不派发执行任务。
- `dispatch_needed`: 已形成稳定小任务，派发时必须带 `discussion_source` 或 `source_message_id`，目标泳道 callback 必须能追溯到本次讨论。
- `confirmation_needed`: 涉及路线锁定、真实外部调用、付费、secret、账号、券商/交易、持久写入、生产声明或重大架构取舍，先给用户确认卡。
- `clarify_needed`: 信息不足且合理假设会明显跑偏，只问最小必要问题，并记录未决点。

## 路由原则

- 如果一句话同时命中多个 Skill，优先选最接近用户当前动作的 Skill。
- 如果用户只说“下一步”“继续”“接着做”或要求系统根据项目状态综合推进，优先 `project-orchestrator`。
- 如果用户说“完成度”“太慢”“整体推进”“项目还差什么”“骨架”“先打通”“全链路”，或最近多个 GOAL 都在局部 capability 里，优先 `project-orchestrator` 做 Skeleton Plan Refresh 判断。
- 如果主调度收到泳道 completion callback、阶段验收结果或 dashboard 最新事件，默认由 `project-orchestrator` 执行 Autonomous Iteration Check：判断是否自动派规划刷新、继续下一刀、补守门/验收，或停下来问用户。
- 如果用户提到泳道任务排队、回复截断、上下文覆盖、任务覆盖、泳道被打断或后续任务堆积，优先 `project-orchestrator` 触发 dispatch queue 检查；若确认为可复用机制缺口，再派 `evolution-runner` 沉淀规则。
- 如果用户指出单泳道 callback 打断主调度、主调度被插入式回复覆盖、callback 导致主调度任务没做完，优先 `project-orchestrator` 执行 Callback Inbox 检查：完整 callback 走 `message-log.jsonl`，线程只做轻量 wake，主调度批量 drain。
- 如果用户在主调度线程里持续讨论需求、技术路线、个人判断、临时想法或担心，但没有手动指定泳道，也优先 `project-orchestrator` 做 discussion intake：判断记录、派发、确认或澄清。
- 如果用户说“先问清楚”“整理需求”“聊聊需求”“探讨需求”“我有个想法”“先别开发”，优先 `product-spec-builder`，不要直接开发。
- 如果用户说“做出来”“开始开发”“执行 GOAL”，优先 `dev-builder`。
- 如果用户说“检查是否完成”“有没有闭环缺陷”，优先 `review-runner`，不要直接改代码。
- 如果用户说“代码审查”“看 diff”，优先 `code-reviewer`。
- 如果用户说“跑测试”“门禁”“程序判断”，优先 `gate-runner`。
- 如果用户显式要求净化/进化 Skill、优化 hook、处理 signals，或用户纠正暴露出可复用流程缺口，优先 `evolution-runner`；单纯“继续/下一步”不要触发它，除非 signal 或 Skill 不适配已经阻塞当前 GOAL。
- 如果用户问“这套机制怎么用”“什么时候用哪个 Skill”“什么时候写门禁/自进化/派新脑子”，优先 `goal-methodology-guide`。
