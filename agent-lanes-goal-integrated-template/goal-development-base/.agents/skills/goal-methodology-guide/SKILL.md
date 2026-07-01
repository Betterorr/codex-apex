---
name: goal-methodology-guide
description: 解释、复盘和维护 GOAL 开发基座的方法论与使用时机。Use when the user asks about GOAL 方法论、这套机制怎么用、什么时候用哪个 Skill、脚本门禁/自动门禁是什么、什么时候写门禁脚本、什么时候调用自进化、如何沉淀规则、什么时候派子 Agent/新脑子、Sketch Plan Loop、骨架计划循环、骨架优先、薄纵向切片、整体推进、完成度、如何复制和使用这个开发基座，或要求把方法论经验写入模板包。
---

# GOAL 方法论使用指南

## 核心契约

把 GOAL 开发基座解释成一套“项目操作系统”，而不是一组孤立提示词。

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、GOAL log、review/release/report 正文或模板说明时，默认写中文。专有名词、品牌、代码、命令、路径、API 名、JSON key、状态枚举、错误原文、许可证原文和外部引用标题可以保留英文或原文。解释机制时也应优先中文，避免让用户通过英文模板理解项目规则。

必须围绕三层机制回答或维护：

1. Skill 负责识别任务类型和产出契约。
2. 脚本门禁负责把可判断的完成标准变成可失败的程序证据。
3. 自进化负责把真实失败和用户纠正沉淀成后续规则。

详细原理见：

- `references/GOAL-methodology-abstract.md`: 原始 GOAL 方法论抽象版。
- `references/usage-playbook.md`: 本模板的具体使用手册、门禁时机、自进化时机和 Skill 路由说明。

## 自然语言触发词

用户提到以下表达时，优先使用本 Skill：

- GOAL 方法论、这套机制、开发基座、模板包怎么用。
- 什么时候用哪个 Skill、Skill 之间怎么配合。
- 自动门禁、脚本门禁、能用脚本判断就不要用提示词判断。
- 什么时候写门禁脚本、哪些检查要程序化。
- 自进化、自净化、沉淀规则、失败信号、signals。
- 子 Agent、新脑子、独立审查、什么时候派发。
- Sketch Plan Loop、骨架计划循环、骨架优先、薄纵向切片、整体推进、完成度、项目还差什么。
- 把方法论写进模板、复制出去也能懂。

## 处理流程

1. 先判断用户是在问“机制解释”还是“模板维护”。
2. 如果是机制解释，读取 `references/usage-playbook.md`，必要时再读取 `references/GOAL-methodology-abstract.md`。
3. 如果是模板维护，检查 `.agents/skills/`、`.codex/hooks/skill-hooks.md`、`.codex/gates/`、`AGENTS.md` 和 `FRAMEWORK.md` 是否同步。
4. 如果新增或修改 Skill，保持 Skill 本体精简，把长说明放入 `references/`，并运行 Skill 校验。
5. 如果发现某条规则可以程序判断，优先补门禁脚本或把它加入 `gate-runner` 的职责说明。
6. 如果规则来自真实失败或用户纠正，记录或引导进入 `.codex/signals/`，再由 `evolution-runner` 消化。

## 输出

回答用户时要给出可执行判断，而不是只讲理念：

- 当前应该使用哪个 Skill。
- 是否需要写脚本门禁。
- 门禁应该现在写、稍后写，还是复用现有命令。
- 是否需要记录 signal 并进入自进化。
- 是否需要派子 Agent/新脑子。
- 应该更新哪些模板文件。

## 完成门禁

完成本 Skill 相关维护前，必须确认：

- 原始方法论文件已在 `references/GOAL-methodology-abstract.md` 中保留。
- 使用手册说明了 Skill、门禁、自进化和子 Agent 的调用时机。
- 自然语言 hook 已在 `.codex/hooks/skill-hooks.md` 和本 Skill description 中体现。
- 如果修改了 Skill，`scripts/validate-skills.ps1` 能通过。
- 如果修改了机制规则，`scripts/check-skill-mechanism.ps1` 能通过。

## 打回条件

出现以下情况不能宣称完成：

- 只把方法论放进普通文档，没有放进可复制的本地 Skill 包。
- 只解释“怎么做”，没有说明“什么时候用什么”。
- 只靠提示词约束可程序判断的规则，没有考虑自动门禁。
- 自进化被写成每次都运行，而不是由真实失败、用户纠正或 signals 触发。
- 子 Agent 被写成默认流水线，而不是用于独立审查或可并行任务。

## 信号

如果用户纠正本方法论的用法，例如“这个时候应该先门禁，不该先开发”，要把它视为可沉淀信号。

信号进入 `.codex/signals/` 后，不要立刻无脑写进规则；由 `evolution-runner` 判断是否满足“真实失败、可复发、能提升后续任务、不会限制模型能力”。
