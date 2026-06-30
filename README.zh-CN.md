# Codex Apex

Codex Apex 是一套用于 Codex 内部自开发体系的开源模板：它把长期项目拆成多个稳定的 Agent 泳道，并用 GOAL 开发基座约束每条泳道内部如何澄清、计划、开发、验证、审查、发布和进化。

当前可发布的核心模板目录是：

```text
agent-lanes-goal-integrated-template/
```

## 这个项目解决什么问题

当一个 Codex 项目从一次性任务变成长期迭代后，最容易丢失的是上下文、职责边界、验收证据和回报路径。Codex Apex 把这些东西模板化：

- 用 Agent Lanes 管多线程、多泳道、多智能体协作。
- 用 GOAL Development Base 管单个泳道内部的目标、计划、执行、验证和复盘。
- 用 message log、worklog、dashboard 和 completion callback 保留可追溯记录。
- 用 guardian/review/evolution 让权限、风险、验收和规则沉淀有固定位置。

## 快速使用

1. 把 `agent-lanes-goal-integrated-template/` 复制到目标项目。
2. 打开 `agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md`。
3. 替换目标项目路径、项目名、主调度线程 id 等占位符。
4. 把提示词发给目标项目里的 Codex。
5. 部署后优先看 `agent-lanes/dashboard.md`、`agent-lanes/message-log.jsonl` 和各泳道 `worklog.md`。

如果要使用 GOAL 集成版，优先阅读：

```text
agent-lanes-goal-integrated-template/README-GOAL-INTEGRATED.md
agent-lanes-goal-integrated-template/BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md
```

## 开源语言策略

建议采用“英文默认入口 + 中文 canonical 模板 + 后续逐步英文镜像”的方式。

- GitHub 首页默认英文，降低外部理解门槛。
- 中文文档保留为第一阶段的权威操作版本，避免过早翻译导致语义漂移。
- 关键入门文档先双语，深层协议文档后续按优先级翻译。
- 文件名、命令、JSON key、状态枚举、路径和 API 名保持英文或原文。

详细策略见 [docs/i18n-strategy.zh-CN.md](docs/i18n-strategy.zh-CN.md)。

## 当前状态

项目已经从 MoneyDigger 的模板包 artifacts 中复制出独立工作副本。原始包副本保留在本地 `template-packages/`，通过 `.gitignore` 排除，不作为 GitHub 发布内容。

首版发布采用：

- 仓库名：`codex-apex`
- 开源协议：MIT
- 文档形态：英文入口 + 中文模板主体

