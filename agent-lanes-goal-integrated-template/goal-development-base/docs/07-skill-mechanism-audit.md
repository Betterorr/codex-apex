# Skill 机制审计

本审计用 `D:/1-Projects/TextBrain/GOAL-methodology-abstract.md` 里的 GOAL 方法论检查本模板包的本地 Skills。

## 检查标准

| 标准 | 要求 |
| --- | --- |
| 轻流程 | Skill 不写死每一步实现细节，保留 Agent 自主规划空间。 |
| 厚标准 | 写清什么算合格、什么必须打回、需要什么证据。 |
| 文档驱动 | 每个环节明确读取和更新哪些 `docs/` 文件。 |
| GOAL 驱动 | 目标、完成标准、验证方式和失败循环必须明确。 |
| 独立审查 | 高风险或用户可见改动必须有干净第二视角。 |
| 自动门禁 | 能由程序判断的规则应进入脚本或 `.codex/gates/`。 |
| 信号进化 | 真实失败和用户纠正进入 `.codex/signals/`，再由 evolution-runner 消化。 |
| 子 Agent 纪律 | 子 Agent 只用于独立审查或并行不相交任务，并带完整上下文。 |

## 原始缺口

| 缺口 | 影响 | 修复 |
| --- | --- | --- |
| 缺少原型环节 Skill | 需求和设计到开发之间缺少原型复用决策，容易把高保真代码当普通参考丢掉。 | 新增 `prototype-builder`。 |
| 缺少专门 bug 修复 Skill | 真实缺陷无法形成复现、根因、回归、signal 的闭环。 | 新增 `bug-fixer`。 |
| 缺少方法论命名的代码审查 Skill | 方法论架构中明确列出 `code-reviewer`，模板只有更泛化的 `review-runner`，角色边界不够清晰。 | 新增 `code-reviewer`，专注代码级独立审查。 |
| 多数 Skill 门禁偏薄 | 容易出现“文档写了但不可验收”的假完成。 | 所有 Skill 增加完成门禁和打回条件。 |
| 信号记录不够普遍 | 失败无法稳定进入自进化流程。 | 各关键 Skill 增加 signal 记录规则。 |
| 子 Agent 派发上下文不足 | 审查和并行任务容易断上下文。 | `goal-creator` 和 `dev-builder` 增加子 Agent 上下文要求。 |
| `.codex` 结构不完整 | 方法论中的 subagents/hooks/gates 没有落位。 | 新增 `.codex/subagents/`、`.codex/hooks/`、`.codex/gates/`。 |
| 缺少可执行机制门禁 | 只能靠人工读 Skill，不能自动发现关键机制缺失。 | 新增 `.codex/gates/skill-mechanism-check.ps1` 和 `scripts/check-skill-mechanism.ps1`。 |

## 当前 Skill 覆盖

| Skill | 方法论环节 | 主要产物 |
| --- | --- | --- |
| `product-spec-builder` | 需求澄清 | `docs/01-product-spec.md` |
| `design-brief-builder` | 设计规范 | `docs/02-design-brief.md` |
| `prototype-builder` | 原型/设计图 | 原型复用策略、设计补充、开发输入 |
| `dev-planner` | 开发计划 | `docs/03-dev-plan.md` |
| `goal-creator` | GOAL 机制 | 可执行 GOAL |
| `dev-builder` | 开发执行 | 代码、验证证据、GOAL log |
| `bug-fixer` | 缺陷闭环 | 复现、根因、修复、回归验证 |
| `code-reviewer` | 代码审查 | bug、测试缺口、代码风险、文档漂移 |
| `requirements-traceability-runner` | 需求追踪 | 需求、设计、实现、验证和证据映射 |
| `frontend-quality-runner` | 前端质量 | 信息架构、页面状态、截图验收和可读性检查 |
| `open-source-research-runner` | 开源调研 | 候选库、license、维护度、依赖和守门边界 |
| `systematic-debugging-runner` | 系统化调试 | 复现、数据流追踪、单假设验证和同路径回归 |
| `lane-recovery-runner` | 泳道恢复 | 新线程接管、registry 替换、旧线程归档和审计记录 |
| `review-runner` | 独立审查 | `docs/05-review-report.md` |
| `release-builder` | 发布交付 | `docs/06-release-record.md` |
| `evolution-runner` | 自进化 | 规则/模板/Skill 更新建议 |

## 结论

当前模板包的本地 Skills 已覆盖 GOAL 方法论的主流程、自动门禁、闭环审查、信号进化和项目级门禁落位。

已内置可执行检查：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/check-framework.ps1
powershell -ExecutionPolicy Bypass -File scripts/validate-skills.ps1
powershell -ExecutionPolicy Bypass -File scripts/check-skill-mechanism.ps1
```

其中 `check-skill-mechanism.ps1` 会检查 19 个本地 Skill 是否包含核心契约、输出、完成门禁、打回/判断条件、signal 机制，以及各自环节的关键能力。

具体项目复制本包后，还应根据技术栈继续把 `.codex/gates/` 中的门禁扩展成真实构建、测试、类型检查、浏览器验收或发布检查。

## 2026-07-05 Figma / 前端设计审查补充

触发原因：用户指出复杂工作台页面虽然字段、证据和边界齐全，但首屏没有明确任务焦点，行动路径没有串成线，审计字段和 raw enum 泄露到主阅读层，导致页面像日志罗列。外部 Figma 设计审查视角能更早发现这些严重 IA / UX 问题。

机制补齐：

- `frontend-quality-runner` 必须吸收 Figma 设计审查视角，不再只做截图、可读性和字段检查。
- `design-brief-builder` 在复杂工具型前端设计中必须写清首屏任务、下一步行动、返回路径、主层/详情层/审计层分工。
- `skill-hooks.md` 应把 Figma 审查、首屏没有重点、行动路径不清、审计信息太多、像日志罗列等表达路由到前端质量检查。
- `skill-mechanism-check.ps1` 增加门禁，检查前端质量 Skill 是否覆盖 Figma 审查、首屏任务、行动路径、主次分层、状态语义和窄屏可用。

通用原则：Figma 不是产品结构源头，但它的设计审查视角必须成为复杂前端进入开发/验收前的质量门槛。字段齐全不等于设计合格；用户能看懂当前任务和下一步，才算前端主线可用。

## 2026-07-06 Decision-Usefulness Gate / 决策意义门槛

触发原因：用户指出某复杂工作台的行动卡片虽然已部分中文化，但仍像机器流程和审计字段罗列。卡片没有告诉用户当前结论、对核心业务判断的影响、关键证据、否决条件和下一步人工动作，说明现有 Figma/前端质量门槛仍可能把“机器可验字段齐全”误判为“用户可用信息完整”。

机制补齐：

- `frontend-quality-runner` 增加 Decision-Usefulness Gate。涉及研究、候选、复盘、报告或行动卡片时，必须检查当前判断、核心业务判断影响、关键证据、否决/风险条件、下一步人工动作和技术审计折叠。
- `design-brief-builder` 要求设计 Brief 先声明卡片类型：`decision_card`、`evidence_card`、`workflow_card` 或 `audit_card`。非决策卡片必须说明“不支持核心业务判断，只用于证据复核 / 流程导航 / 技术审计”。
- `skill-hooks.md` 增加决策卡片、研究卡片、候选卡片、复盘卡片、报告卡片、行动卡片、核心业务判断、当前判断、决策意义、机器字段卡片等触发词。
- `skill-mechanism-check.ps1` 增加门禁，检查 `frontend-quality-runner` 和 `design-brief-builder` 是否包含决策意义门槛、卡片类型和关键字段链。

通用原则：业务卡片不是审计日志的漂亮外壳。它必须帮助用户判断下一步是否继续、暂停、复核或排除；raw enum、JSON key、source path、validator status、return anchors 和 rerun command 应默认进入折叠层。

## 2026-07-06 Tool-Level IA / Internal Simulation / Open Source Integration Gates

触发原因：用户进一步指出，复杂前端工具地图不能只解释已有卡片和字段，而要从用户目标出发定义一级页面、页面职责、用户问题、结果回看和状态边界。同时，当前阶段的安全边界不能被误写成最终产品定位；产品内部的模拟执行或沙盒执行，也不能被混同为真实外部执行。另一个需求是“能否嫁接别人开发好的前后端”，这需要先处理 license、attribution、依赖和 adapter 边界，而不是直接复制外部项目。

机制补齐：
- `frontend-quality-runner` 增加 Tool-Level IA Gate。涉及工具地图、跨页面工作台、验证实验、模拟执行、结果看板或复杂后台时，必须检查一级页面、页面职责、用户路径、入口、结果回看、状态边界和字段如何支撑功能。
- `frontend-quality-runner` 和 `design-brief-builder` 增加 Internal Simulation Semantics Gate。模板用通用语义表达为“内部模拟执行 / 沙盒执行 / 非真实外部执行”：要区分当前本地样本或静态 payload、产品内部受控状态变化、以及需要账号、secret、付费、远程写入或受监管操作的高风险真实执行。
- `open-source-research-runner` 增加 Open Source Integration Gate。对外部前端、后端或开源模块的复用，必须先形成 license、attribution、dependency、local smoke、adapter、guardian 边界结论；不得直接复制外部代码进业务目录。
- `skill-hooks.md` 增加工具地图、一级页面、页面职责、用户路径、验证工作台、内部模拟执行、结果曲线、开源前后端嫁接等触发词。
- `skill-mechanism-check.ps1` 增加门禁，检查上述三类机制是否存在于对应 Skill、hook 和项目规则中。

通用原则：工具型前端先做“产品结构”再做“字段呈现”。阶段性只读样本、非生产文案和安全声明是当前约束，不应自动变成目标态。开源嫁接先研究和隔离，再适配和验证，不能让外部实现绕开项目自己的架构、守门和证据体系。

## 2026-07-08 Human-Readable Frontend Gate / 人类可读前端门槛

触发原因：用户指出当前前端仍大量出现偏程序代码、偏审计日志、普通人不易读的信息，同时用户可见前端应默认中文优先。已有 Figma / Decision-Usefulness / Tool-Level IA 规则仍可能允许 raw enum、JSON key、内部状态名、路径、命令、ID 或 validator 字段泄露到主阅读层。

已固化规则：

- `frontend-quality-runner` 必须执行 Human-Readable Frontend Gate。所有用户可见主阅读层默认中文优先，技术字段只允许进入折叠详情、审计抽屉、开发者诊断或报告来源层。
- `design-brief-builder` 必须在设计 Brief 中说明哪些信息用中文人话放在主层，哪些技术信息被折叠；不能让开发直接把字段名当 UI 结构。
- `review-runner` 验收用户可见前端时必须检查中文优先和技术字段外露；若主阅读层像代码、日志或审计表，不能声明前端可用。
- `skill-hooks.md` 增加中文优先、人类可读、程序代码信息、机器字段、技术字段外露等触发词。
- `skill-mechanism-check.ps1` 增加门禁，检查设计、前端质量和验收 Skill 是否覆盖 Human-Readable Frontend Gate。

通用原则：前端不是给 validator 或开发者看的 JSON 浏览器。主层要让用户直接看懂状态、判断、证据、风险和下一步；技术字段保留可追溯，但必须降级到审计/诊断层。

## 2026-06-16 复查记录

复查依据：

- `D:/1-Projects/TextBrain/GOAL-methodology-abstract.md`
- `.agents/skills/*/SKILL.md`
- `scripts/check-framework.ps1`
- `scripts/validate-skills.ps1`
- `scripts/check-skill-mechanism.ps1`

复查结果：

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 模板包必需文件 | 通过 | `check-framework.ps1` 显示 28 个必需文件存在。 |
| Skill 格式合法性 | 历史通过 | 当时 `validate-skills.ps1` 显示 10 个本地 Skill 全部 valid。 |
| GOAL 机制覆盖 | 历史通过 | 当时 `check-skill-mechanism.ps1` 显示 10 个 Skill 全部 PASS。 |

本轮当时未发现新增缺口；二次复查已补充 `code-reviewer`。

## 2026-06-16 二次复查补充

二次复查发现：`GOAL-methodology-abstract.md` 的可复用架构中明确列出 `code-reviewer`，而模板包原本只有泛化的 `review-runner`。两者能力相近，但角色边界不同：

- `code-reviewer`：专注代码级审查，检查 bug、测试缺口、代码风险、范围漂移和文档漂移。
- `review-runner`：负责更高层的 GOAL 闭环、验收证据、发布或流程审查。

已补齐：

- 新增 `.agents/skills/code-reviewer/SKILL.md`
- 更新 `AGENTS.md`
- 更新 `FRAMEWORK.md`
- 更新 `scripts/check-framework.ps1`
- 更新 `.codex/gates/skill-mechanism-check.ps1`

补齐后验证：

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 模板包必需文件 | 通过 | `check-framework.ps1` 显示 29 个必需文件存在。 |
| Skill 格式合法性 | 通过 | `validate-skills.ps1` 显示 11 个本地 Skill 全部 valid。 |
| GOAL 机制覆盖 | 通过 | `check-skill-mechanism.ps1` 显示 11 个 Skill 全部 PASS。 |

## 2026-06-16 子 Agent / 新脑子专项复查

复查重点：

`GOAL-methodology-abstract.md` 明确要求默认由主 Agent 贯穿项目，但以下情况要调用子 Agent / 新脑子：

- 需要干净第二视角，例如代码审查、产品审查、安全审计。
- 多块任务互不依赖，可以并行推进。
- 派发时必须带走完整上下文：当前目标、相关文档、变更范围、验收标准、禁止事项、返回证据格式。
- 主 Agent 保留最终合并和拍板权。

原始缺口：

| 缺口 | 影响 | 修复 |
| --- | --- | --- |
| 顶层规则没有明确哪些步骤必须安排新脑子 | 后续项目可能只把独立审查当建议，而不是门禁。 | 在 `AGENTS.md` 增加“子 Agent / 新脑子规则”。 |
| `goal-creator` 只留了子 Agent 字段，没有写明触发条件 | GOAL 可能不会主动规划代码审查、闭环审查、发布安全审查。 | 增加“子 Agent 安排”，要求写清角色、触发时机、上下文和证据格式。 |
| `dev-builder` 有子 Agent 原则，但没明确代码完成后的强制新脑子步骤 | 开发完成可能跳过独立代码审查或 GOAL 闭环审查。 | 明确自测后进入 `code-reviewer`，GOAL 关闭前进入 `review-runner`。 |
| `code-reviewer` 和 `review-runner` 暗含独立视角，但没有写清派发上下文 | 子 Agent 可能缺文档、GOAL、diff 或验证证据。 | 增加“子 Agent 安排”和必须带走的上下文。 |
| `release-builder` 没有明确发布前安全/隐私/生产风险的独立审查 | 发布记录可能只由实现者自查。 | 增加发布前独立新脑子审查要求。 |
| `evolution-runner` 没有明确新 session 信号消化要独立处理 | 自进化可能被当前实现上下文污染。 | 增加新 session 下作为独立新脑子消化 signals 的要求。 |
| 机制门禁没有检查子 Agent 安排 | 即使 Skill 删除新脑子规则，脚本也不会失败。 | 更新 `.codex/gates/skill-mechanism-check.ps1`，检查关键 Skill 的子 Agent / 新脑子字段。 |

补齐后验证：

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| Skill 格式合法性 | 通过 | `validate-skills.ps1` 显示 11 个本地 Skill 全部 valid。 |
| GOAL 机制覆盖 | 通过 | `check-skill-mechanism.ps1` 显示 11 个 Skill 全部 PASS，并已包含子 Agent / 新脑子检查项。 |

## 2026-06-16 机制意图复盘补充

复盘结论：

整体机制已经基本符合 `GOAL-methodology-abstract.md` 的设计意图：文档驱动、GOAL 驱动、轻流程厚标准、独立审查、失败信号进化都已经落到本地 Skills 中。

本轮发现的缺口：

| 缺口 | 为什么不满足方法论意图 | 修复 |
| --- | --- | --- |
| 自动门禁只有结构和 Skill 机制检查，没有专门 Skill 负责项目级门禁执行 | 方法论第 10 节强调“能用程序判断的规则，不要只写在提示词里”。如果没有门禁执行器，构建、测试、审查、发布检查容易仍停留在口头规则。 | 新增 `gate-runner`，负责运行或创建构建、测试、类型检查、文档、审查和发布门禁。 |
| `goal-creator` 没有把自动门禁写入 GOAL 模板 | GOAL 可能只写验证方式，但没有明确哪些检查要交给门禁卡住。 | 在 GOAL 格式中新增“自动门禁”字段。 |
| `dev-builder` 没有明确先跑项目级门禁再进入审查闭环 | 开发可能直接进入人工式审查，而遗漏构建、测试、类型检查等程序门禁。 | 要求代码改动后先用 `gate-runner` 运行门禁，再进入 `code-reviewer` 和 `review-runner`。 |
| `release-builder` 的发布检查没有接入 `gate-runner` | 发布准备可能只写记录，没有程序化核对启动、日志、回滚、冒烟和配置项。 | 增加发布自动门禁要求。 |

已补齐：

- 新增 `.agents/skills/gate-runner/SKILL.md`
- 更新 `AGENTS.md`
- 更新 `FRAMEWORK.md`
- 更新 `goal-creator`
- 更新 `dev-builder`
- 更新 `release-builder`
- 更新 `scripts/check-framework.ps1`
- 更新 `.codex/gates/skill-mechanism-check.ps1`

补齐后验证：

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 模板包必需文件 | 通过 | `check-framework.ps1` 显示 30 个必需文件存在。 |
| Skill 格式合法性 | 通过 | `validate-skills.ps1` 显示 12 个本地 Skill 全部 valid。 |
| GOAL 机制覆盖 | 通过 | `check-skill-mechanism.ps1` 显示 12 个 Skill 全部 PASS。 |

## 2026-06-16 自然语言 Hook 补充

用户需求：

不希望每次用 slash 手动指定 Skill，而是希望普通说出相关词时，Codex 自动选择对应 Skill。

设计原则：

- 官方 Skill 触发主要依赖 frontmatter `description`，所以触发词必须写进 description。
- 为了可维护性，每个 Skill 正文也要有“自然语言触发词”段。
- `.codex/hooks/skill-hooks.md` 作为总路由表，方便复制基座后维护。
- 机制门禁必须检查每个 Skill 是否包含“自然语言触发词”段。

已补齐：

- 12 个 `SKILL.md` 的 `description` 都加入自然语言触发词。
- 12 个 `SKILL.md` 都新增“自然语言触发词”段。
- 新增 `.codex/hooks/skill-hooks.md`。
- 更新 `AGENTS.md`，说明不需要 slash 调用 Skill。
- 更新 `FRAMEWORK.md`，给出自然语言调用示例。
- 更新 `scripts/check-framework.ps1`，把 hook 路由表纳入必需文件。
- 更新 `.codex/gates/skill-mechanism-check.ps1`，检查每个 Skill 的自然语言 hook 段。

补齐后验证：

| 检查项 | 结果 | 证据 |
| --- | --- | --- |
| 模板包必需文件 | 通过 | `check-framework.ps1` 显示 31 个必需文件存在。 |
| Skill 格式合法性 | 通过 | `validate-skills.ps1` 显示 12 个本地 Skill 全部 valid。 |
| GOAL 机制覆盖 | 通过 | `check-skill-mechanism.ps1` 显示 12 个 Skill 全部 PASS，并已包含自然语言 hook 检查。 |
# 2026-07-10 Dynamic Boundary Gate / 动态边界闸门

## 背景

用户指出：旧机制里大量“本轮没有触碰 provider/live API、secret、scheduler、writeback、生产 feed、真实外部执行、quality_reviewed / production_ready”的边界声明，容易被主调度、开发和验收泳道误读成永久禁止，导致本来可以在授权后快速推进的真实接入、质量复核或生产准备长期被挡住。

## 本次规则

- 边界是闸门，不是墙：高风险能力未授权时不越权、不伪装完成；已授权时必须按授权范围进入受控实现、smoke、样本保存、质量复核或生产准备。
- completion callback、review report 和 dashboard 必须区分 `本轮未推进`、`待授权`、`已授权待验证`、`已受控验证/可进入下一成熟度`。
- 守门泳道负责把风险变成可执行条件，包括授权范围、预算/次数、固定输入、secret 不落盘、允许写入位置、回滚方式和证据路径；不是把能力永久关在门外。
- `skill-mechanism-check.ps1` 已增加动态边界检查，防止 `AGENTS.md`、主调度、开发、验收、门禁和 hook 路由缺失该规则。

## 迁移提示

历史 message-log、worklog 和审计报告里的“本轮未触碰高风险能力”不需要重写。它们是历史事实。需要修正的是未来任务派发和验收语言：不得把阶段限制写成最终产品定位，不得因为 `DONE_WITH_CONCERNS` 中的非阻塞边界声明让主线停住。
