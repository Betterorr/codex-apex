# Skill 机制审计

本审计用模板内 `.agents/skills/goal-methodology-guide/references/GOAL-methodology-abstract.md` 里的 GOAL 方法论检查本模板包的本地 Skills。

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

## 2026-06-16 复查记录

复查依据：

- `.agents/skills/goal-methodology-guide/references/GOAL-methodology-abstract.md`
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

## 2026-06-23 单能力聚焦预算补充

用户纠正：

GOAL Skill 体系在真实执行时可能围绕单个 API、provider 或 capability 连续深挖，追加 wrapper、readiness、operator decision、readonly surface、handoff proposal、apply readiness 等壳层，导致整体产品纵向闭环推进不足。

修复原则：

- 单个 provider/capability 连续推进 2-3 个 GOAL 后，`project-orchestrator` 必须做 Capability Exit Check。
- Exit Check 必须判断成熟度、真实样本或真实 smoke、下游消费、剩余人工决策/授权/预算/真实写入/质量审查，以及是否仍是下一条用户可见流程的直接硬阻塞。
- 如果当前阶段已经够用，停止继续围绕该 capability 加壳，把剩余优化放入 backlog 或显式授权队列。
- 下一步切回前端可操作入口、前后端联调、端到端样本、核心业务流程、报告、打包、发布或另一个关键能力。

已补齐：

- 更新 `AGENTS.md` 的项目级规则。
- 更新 `.agents/skills/project-orchestrator/SKILL.md` 的调度规则和触发词。
- 更新 `.agents/skills/dev-builder/SKILL.md` 的执行规则和打回条件。
- 更新 `.codex/hooks/skill-hooks.md` 的自然语言路由。
- 更新 `.codex/gates/skill-mechanism-check.ps1`，检查 Capability Exit Check 关键规则。

## 2026-06-23 多泳道协作瘦身补充

用户判断：

原 GOAL Skills 为单 Agent 自主运行设计，部分规则偏固定串行：先 GOAL、再计划、再开发、再门禁、再完整审查。启用多泳道后，这些步骤可以由主调度结构化派发、泳道并行产物、completion callback、聚焦门禁和阶段边界合并验收替代，避免效率浪费。

修复原则：

- Skill 是职责契约，不是固定流水线。
- 主调度可以并行派发规划、设计、守门等互不阻塞的泳道任务。
- 结构化泳道任务可替代低风险场景下的正式 `goal-creator`。
- `dev-planner` 只在跨泳道依赖、阶段顺序、联调路线、风险或回滚不清时使用。
- `review-runner` 默认审查主调度聚合后的证据包，不逐条完整审查低风险 callback。
- `gate-runner` 按泳道变更面运行聚焦门禁，不因多泳道存在自动全量门禁。

已补齐：

- 更新 `AGENTS.md` 的“多泳道协作下的 Skill 瘦身”规则。
- 更新 `.agents/skills/project-orchestrator/SKILL.md` 的多泳道协作模式。
- 更新 `.agents/skills/goal-creator/SKILL.md` 和 `.agents/skills/dev-planner/SKILL.md` 的按需使用边界。
- 更新 `.agents/skills/review-runner/SKILL.md` 和 `.agents/skills/gate-runner/SKILL.md` 的聚合/聚焦策略。
- 更新 `.agents/skills/goal-methodology-guide/references/usage-playbook.md`、`.codex/hooks/skill-hooks.md` 和 `.codex/gates/skill-mechanism-check.ps1`。
