# GOAL 开发基座使用手册

本文件说明复制本开发基座之后，后续 Agent 应该怎样理解和使用这套机制。

## 1. 一句话总览

GOAL 开发基座不是一堆分散 Skill，而是一套项目推进机制：

```text
人定目标，AI 跑循环。
Skill 识别任务，文档传递上下文。
脚本门禁卡住底线，自进化吸收真实失败。
```

## 2. 三层机制

### Skill 层

Skill 负责回答“现在是什么任务”。

它不应该把所有步骤写死，而应该规定：

- 什么时候使用。
- 输入应该读哪些文档。
- 输出必须更新哪些文件。
- 什么状态不能放行。
- 哪些失败要记录 signal。

启用多泳道后，Skill 还负责定义职责边界，但不再要求每个请求按单 Agent 流水线完整经过所有阶段。主调度可以用结构化派发、completion callback 和 dashboard 合并来替代部分正式 GOAL、计划和审查步骤。

### 自动门禁层

门禁负责回答“有没有客观证据证明完成”。

凡是可以用程序判断的规则，都不要只写在提示词里。门禁可以是现有命令，也可以是模板或项目里的脚本。

常见门禁包括：

- 构建是否通过。
- 测试是否通过。
- typecheck、lint、格式检查是否通过。
- 必需文档是否存在。
- Skill 是否具备自然语言触发词。
- 发布记录是否包含启动、日志、环境变量、回滚和冒烟测试。
- 审查报告是否存在阻塞问题。
- `docs/capability-status.json` 是否结构正确、成熟度合法、证据字段完整。

门禁的本质是：

```text
规则负责表达标准，程序负责卡住底线。
```

### 自进化层

自进化负责回答“这次失败以后还会不会再犯”。

它不是每一步都运行，也不是不断堆规则。只有出现真实信号时才触发：

- 用户明确纠正了流程。
- 任务失败暴露了规则缺口。
- 审查发现同类风险可能复发。
- 门禁缺失导致问题漏过。
- 用户说“以后记住”“沉淀成规则”“自进化一下”“复盘规则”。
- `.codex/signals/` 中已有待处理信号。

一条规则值得沉淀，必须满足：

- 来自真实失败或真实纠正。
- 删除后问题大概率复发。
- 能提升后续同类任务表现。
- 不会明显限制模型自主能力。

## 3. 什么时候用哪个 Skill

| 用户意图 | 应用 Skill | 产物或动作 |
| --- | --- | --- |
| 想法、需求、范围还不清楚 | `product-spec-builder` | 更新 `docs/01-product-spec.md` |
| 需要 UI、UX、交互、视觉方向 | `design-brief-builder` | 更新 `docs/02-design-brief.md` |
| 需要原型、高保真、设计稿、可复用原型代码 | `prototype-builder` | 形成原型策略并更新设计/计划文档 |
| 需要拆阶段、排计划、定义实现路径 | `dev-planner` | 更新 `docs/03-dev-plan.md` |
| 需要把任务变成可执行目标 | `goal-creator` | 写出含完成标准和验证方式的 GOAL |
| 要开始实现或执行 GOAL | `dev-builder` | 改代码、验证、更新文档 |
| 出现 bug、报错、测试失败、构建失败 | `bug-fixer` | 复现、定位、修复、回归验证 |
| 需要跑测试、构建、typecheck、CI、本地验收 | `gate-runner` | 运行或创建自动门禁 |
| 需要看代码 diff、风险、测试缺口 | `code-reviewer` | 代码级独立审查 |
| 需要判断 GOAL 是否真正闭环 | `review-runner` | 总体验收审查和 `docs/05-review-report.md` |
| 需要发布、部署、回滚、日志、冒烟记录 | `release-builder` | 更新 `docs/06-release-record.md` |
| 需要沉淀规则、处理 signals、复盘流程 | `evolution-runner` | 规则修改建议或删除建议 |
| 需要解释整套机制怎么用 | `goal-methodology-guide` | 说明 Skill、门禁、自进化和子 Agent 时机 |

### 多泳道协作下的降本规则

启用 `agent-lanes/` 后，默认把 GOAL Skills 当成团队协作协议，而不是固定串行工序。

- `project-orchestrator` 可以并行派发规划、设计、守门等互不阻塞的泳道任务。
- 结构化泳道任务已经包含目标、范围、完成标准、验证证据、禁止事项和回报格式时，可以替代单独运行 `goal-creator`。
- `dev-planner` 只在跨泳道依赖、先后顺序、风险、回滚、联调路线不清时使用；不为低风险继续任务重写计划。
- `review-runner` 审查主调度聚合后的证据包；低风险 callback 可以延迟到阶段边界合并验收。
- `gate-runner` 按泳道变更面运行聚焦门禁；只有共享合同、真实联调、权限/数据写入、发布或高风险边界变化时升级完整门禁。
- 自进化批处理真实失败和用户纠正，不因每条 callback 自动触发。

### Sketch Plan Loop / 骨架计划循环

多泳道协作不能只追求“任务被派出去”，还要持续看产品主链路有没有变完整。`project-orchestrator` 应把 Sketch Plan Loop 作为默认调度习惯：

```text
Plan Refresh -> Thin Slice Execute -> Focused Verify -> Docs/Dashboard Merge -> 下一刀
```

当用户说“继续”但最近 3-5 个 GOAL 都在同一能力里，或用户提到完成度、太慢、整体推进、计划、项目还差什么、骨架、先打通、全链路时，主调度不要直接派 `dev-builder` 继续局部深挖，而要先让 `dev-planner` 做一次 Skeleton Plan Refresh。

Skeleton Plan Refresh 至少检查：

- 产品骨架链路哪一环是空白。
- 哪一环只有 fixture、假数据或只读样本。
- 哪一环只有后端没有前端，或只有前端没有真实执行。
- 哪一环已经达到当前阶段够用，应暂停深挖。
- 同一 provider/capability 是否已经连续推进 2-3 个 GOAL，需要 capability exit check。
- 接下来 3-6 个最高价值薄纵向切片分别补哪一环。

通用产品骨架可以先按这条线判断：

```text
用户输入 -> 数据/素材进入 -> 处理/生成 -> 人工审核 -> 组合/编排 -> 输出/渲染 -> 报告/交付
```

计划里要标明当前切片属于哪个 Pass：

- `Skeleton Pass`: 先打通能跑的主流程。
- `Real Pass`: 把关键节点换成真实执行。
- `Quality Pass`: 做质量、体验、稳定性。
- `Production Pass`: 做批量、权限、回滚、发布。

`dev-builder` 只执行最新骨架计划里的下一刀。每个实现 GOAL 都要说明它补的是产品骨架哪一环、是否让全链路更接近可运行、如果只是局部优化为什么现在是硬阻塞、完成后切到哪个非同能力骨架节点。

## 4. 带前端项目怎么分层推进

带前端的项目不要让“继续”长期偏向同一层。`project-orchestrator` 每次都要检查需求/设计、后端或契约、前端、联调、门禁和审查哪一层最缺。

推荐节奏：

1. 需求和交互不清楚时，先用 `product-spec-builder` 或 `design-brief-builder`。
2. 先后关系不清楚时，用 `dev-planner` 写成薄纵向切片，每个阶段标注主要层次。
3. 前端需要的数据和动作没有来源时，先做 API/CLI/schema/fixture/contract。
4. 后端或契约已有证据但用户无法操作时，做前端壳、页面状态和数据适配。
5. 两边都存在但没有真实流动时，做最小安全联调：固定入口、失败状态、权限边界、复跑命令和证据文件。
6. 准备说完成前，用 `review-runner` 检查前端状态、后端/契约、数据适配和验证证据是否一致。

判断口诀：

- 后端完成不等于用户流程完成。
- 静态前端不等于真实能力接入。
- 联调不是大而全，先让一条安全数据流能被验证。
- 连续两个阶段都偏同一层时，下一次调度必须解释为什么继续当前层，或切到缺口层。

## 5. 脚本门禁什么时候写

不要在模板里预写所有项目特定脚本。不同项目的技术栈、测试命令、部署方式不同，模板只预置机制和通用门禁。

模板阶段应该提供：

- `.codex/gates/` 作为门禁脚本目录。
- `gate-runner` 作为门禁发现和补齐 Skill。
- 通用检查脚本，例如框架完整性、Skill 合法性、Skill 机制检查。
- 文档说明哪些情况必须门禁。

具体项目阶段再补：

- React 项目可能补 `npm run build`、`npm run test`、`npm run typecheck`。
- Python 项目可能补 `pytest`、`ruff check`、`mypy`。
- API 项目可能补 smoke test、鉴权测试、契约测试。
- 发布项目可能补环境变量、启动方式、日志、回滚、冒烟脚本。
- 模型/API/CLI/provider 项目应复用或扩展 `scripts/validate-capability-status.ps1`，检查能力 registry、证据路径和成熟度。

应该写脚本门禁的时机：

1. GOAL 的完成标准可以程序判断，但项目还没有对应命令。
2. 同一个人工检查已经重复出现两次以上。
3. 这个检查漏掉会造成用户可见问题、安全问题、发布风险或数据风险。
4. 审查发现“靠 Agent 自觉”不足以稳定保证。
5. 一次真实失败说明缺少这道门禁。

不需要写脚本门禁的情况：

- 判断高度主观，例如“这个视觉是否高级”。
- 一次性探索，不会复用。
- 还没有稳定标准，写脚本会过早锁死方向。

## 5.1 用户可用能力与能力 Registry

声称一项能力“用户可用”时，至少要具备：

- 一个用户或调用方能触达的入口。
- 一个真实或固定 fixture 输入。
- 一个真实输出或可复用 artifact。
- 一个失败状态或错误反馈。
- 一个复跑命令或自动门禁。
- 一个可查看结果的位置。

只完成后端、只完成前端、只完成合同、只保存孤立样本，都只能算局部完成。

模型、Provider、CLI、SDK、媒体工具和外部 API 的状态应写入 `docs/capability-status.json`。registry 是调度依据，不是完成证据本身；创建 registry 不能替代真实 smoke、真实样本、前后端接线或质量审查。

如果同一 provider 有普通生成、参考输入、长文本、批量 worker、CUDA/CPU、同步/异步、线上/本地等不同风险或验证方式，应拆成多个 capability 或 variants，不能用一个成熟度覆盖所有子能力。

真实执行闭环要自收尾：真实调用失败且原因是路径、cwd、环境变量、输入文件、编码、参数映射、输出目录或 fixture 接线时，应在同一 GOAL 内小范围修复并复跑同一真实路径；真实调用通过后，应自动保存 evidence、接入下游消费、更新 registry、运行 registry 校验和聚焦门禁。

mock、stub、pytest monkeypatch 只能证明代码路径，不能推进 provider/model/API maturity。媒体 fixture 也要分层：audio fixture 不能代表完整 video/raw-video/scene-split/atom 闭环；大型媒体应通过外部路径、生成脚本或 fixture README 管理。

普通“继续/下一步”默认使用轻量继续模式；当用户反馈与状态文档不一致、registry 证据过期、阶段边界、高风险、发布/交付或判断不清时，升级完整复盘。

同一纵向能力包内，小修默认只跑聚焦门禁；但累计 3-5 个小修后，或准备声明用户可用、客户可用、生产可用前，必须做一次合并审查。

## 6. 自进化什么时候调用

自进化不是主流程里的固定步骤，而是信号驱动的维护动作。

推荐调用时机：

- 一个 GOAL 完成后，如果过程中出现了失败、返工、用户纠正或门禁缺口。
- 新 session 开始时，如果 `.codex/signals/` 非空。
- 用户明确说要“复盘”“沉淀规则”“以后记住”“自进化”。
- 审查报告指出某类问题可能反复出现。
- 发现某条旧规则已经过时、冲突或只是重复常识。

自进化的输出不应该直接等于改规则。它应该先提出建议：

- 新增什么规则。
- 修改什么 Skill。
- 新增什么门禁。
- 删除什么过时规则。
- 为什么这条规则值得保留。

只有用户确认或任务要求允许时，才写入 Skill、AGENTS、hooks、gates 或文档。

## 7. 子 Agent / 新脑子什么时候派

默认由主 Agent 贯穿任务，不要把所有事情拆成流水线。

适合派子 Agent 的情况只有两类：

1. 需要独立视角：代码审查、闭环审查、安全/隐私审查、发布风险审查。
2. 任务互不依赖：多个模块可以并行调研、并行实现、并行验证。

不适合派子 Agent 的情况：

- 需求还不清楚。
- 主 Agent 还没读完核心文档。
- 子任务之间强依赖，需要连续判断。
- 只是为了显得流程复杂。

派发时必须带走：

- 当前 GOAL。
- 相关文档。
- 变更范围。
- 验收标准。
- 禁止事项。
- 已有验证证据。
- 需要返回的证据格式。

主 Agent 必须保留最终合并和拍板权。

## 8. 一条 GOAL 的标准闭环

单 Agent 或高风险任务使用完整闭环：

```text
创建 GOAL
-> 明确完成标准和验证方式
-> 判断是否需要预置门禁
-> 实现
-> 自测和运行门禁
-> 独立代码审查
-> 修复阻塞问题
-> 闭环审查
-> 更新文档和变更记录
-> 必要时记录 signal
-> 交付证据
```

多泳道低风险任务可以使用轻量闭环：

```text
主调度结构化派发
-> 泳道执行并写 worklog
-> completion callback
-> 聚焦门禁或证据检查
-> 主调度合并 dashboard/message-log
-> 阶段边界再合并审查
```

不能跳过的底线：

- 没有证据，不说完成。
- 门禁失败，不说完成。
- 独立审查有阻塞问题，不说完成。
- 文档与实际不一致，不说完成。
- 发现可复发失败，不悄悄遗忘，要记录 signal。

## 9. 复制到新项目后的第一步

复制整个开发基座后，建议在新项目第一句话说：

```text
使用本项目里的 GOAL 开发基座。
先读取 AGENTS.md、FRAMEWORK.md 和 docs/00-project-state.md。
如果我提出的是模糊想法，先用 product-spec-builder 澄清需求。
```

如果要检查基座是否完整，运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-framework.ps1
powershell -ExecutionPolicy Bypass -File scripts/validate-skills.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-skill-mechanism.ps1
powershell -ExecutionPolicy Bypass -File scripts/validate-capability-status.ps1
```

## 10. 最容易误用的地方

### 误用一：把 Skill 当 slash 命令

正确做法：普通自然语言即可触发。hook 的真正入口是每个 `SKILL.md` 的 `description`，`.codex/hooks/skill-hooks.md` 是维护总表。

### 误用二：把门禁当成后期补充

正确做法：写 GOAL 时就判断哪些完成标准需要门禁。已有命令就复用，没有命令且风险高，就让 `gate-runner` 补脚本。

### 误用三：每次都自进化

正确做法：自进化由失败、纠正、signals 或明确复盘触发。没有真实信号时，不要制造规则。

### 误用四：过早派大量子 Agent

正确做法：主 Agent 负责连续判断。只有独立审查或可并行任务才派子 Agent。

### 误用五：只改代码不改文档

正确做法：产品、设计、实现、验证、发布有变化时，同步更新受影响文档。
