# GOAL 开发基座

把这个文件包复制到新项目根目录，就能给项目装上一套可复用的 AI 开发操作系统。

## 复制方式

把本目录里的内容复制到目标项目根目录：

```text
AGENTS.md
.agents/
.codex/
docs/
scripts/
```

复制后重启 Codex，或在该项目里开启新 session，让本地规则和本地 Skills 生效。

## 推荐第一句话

```text
使用本项目里的 GOAL 开发基座。
先检查 docs/00-project-state.md，然后帮我创建第一份产品需求文档。
```

## 自然语言调用

不需要 slash 调用 Skill。复制本基座后，用户可以直接说：

- “帮我整理需求”
- “下一步”
- “继续”
- “写一个 GOAL”
- “开始开发这个阶段”
- “跑一下门禁”
- “做代码审查”
- “检查有没有闭环缺陷”
- “准备发布记录”
- “把这次失败沉淀成规则”
- “这套机制到底怎么用”
- “什么时候写脚本门禁”
- “什么时候调用自进化”
- “什么时候派子 Agent / 新脑子”

Codex 应根据 `.codex/hooks/skill-hooks.md` 和各 `SKILL.md` 的 description 自动选择对应本地 Skill。

## 方法

```text
人定 GOAL。
Codex 跑循环。
文档保存上下文。
审查门禁保护质量。
失败信号改进未来规则。
```

## 最小工作流

1. 用户只说“下一步/继续”时，用 `project-orchestrator` 读取项目状态并选择下一步。
2. 用 `product-spec-builder` 澄清需求。
3. 如果涉及 UI、UX、内容、架构或产品气质，用 `design-brief-builder`。
4. 如果需要原型、设计稿或可复用原型代码，用 `prototype-builder`。
5. 如果阶段顺序、跨泳道依赖、联调路线、风险或回滚不清，用 `dev-planner` 拆开发阶段。
6. 如果目标、范围、完成标准或验证方式不清，用 `goal-creator` 创建一个可执行 GOAL；低风险结构化泳道派发可跳过正式 GOAL。
7. 用 `dev-builder` 实现，或由主调度结构化派发到对应泳道。
8. 出现真实缺陷时，用 `bug-fixer` 复现、修复和回归。
9. 用 `gate-runner` 运行构建、测试、类型检查、文档、审查和发布门禁。
10. 代码改动完成后，用 `code-reviewer` 做代码级独立审查。
11. 完成前用 `review-runner` 做总体验收审查。
12. 发布、部署或交接时，用 `release-builder`。
13. 不清楚整套机制或调用时机时，用 `goal-methodology-guide`。

启用 Agent Lanes 时，GOAL Skill 不是固定串行流水线。主调度可以并行派发规划、设计、守门等互不阻塞的泳道任务，用 completion callback 和 dashboard 合并结果；低风险任务使用聚焦门禁，阶段边界或中高风险再做完整验收。

## 方法论原文和使用手册

本基座把方法论本身也作为本地 Skill 的参考资料保存，复制整个包时会一起带走：

- `.agents/skills/goal-methodology-guide/SKILL.md`
- `.agents/skills/goal-methodology-guide/references/GOAL-methodology-abstract.md`
- `.agents/skills/goal-methodology-guide/references/usage-playbook.md`

当用户问“这套机制怎么用”“什么时候用哪个 Skill”“门禁脚本什么时候写”“自进化什么时候调用”“什么时候派新脑子”时，优先使用 `goal-methodology-guide`。
