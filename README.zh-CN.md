# Codex Apex

Codex Apex 是一套用于 Codex 内部自开发体系的开源模板：它把长期项目拆成多个稳定的 Agent 泳道，并用 GOAL 开发基座约束每条泳道内部如何澄清、计划、开发、验证、审查、发布和进化。

当前可发布的核心模板目录是：

```text
agent-lanes-goal-integrated-template/
```

## 一键启动方式

这个仓库最重要的用法是：把 `agent-lanes-goal-integrated-template/` 复制到你自己的项目里，然后把下面这段提示词发给目标项目里的 Codex。Codex 会读取模板目录，自动创建 Agent Lanes 运行态、泳道注册表、工作日志、回报机制、门禁脚本和 GOAL skills。

推荐放置路径：

```text
<TARGET_PROJECT_ROOT>/docs/agent-lanes-goal-integrated-template/
```

### 可复制启动提示词

如果模板放在 `docs/agent-lanes-goal-integrated-template/`，下面这段可以直接复制给 Codex，不需要填写项目名。Codex 当前所在的项目文件夹名就是项目名。

```text
你现在在 Codex 里工作。请把 Agent Lanes + GOAL 开发基座模板部署到当前项目。

默认假设：
- 当前 Codex 工作目录就是目标项目根目录。
- 当前项目文件夹名就是项目名。
- 模板目录在 docs/agent-lanes-goal-integrated-template。
- 主要模块目录先使用 .。
- 主调度线程 id 先使用 pending_setup。

请先读取模板目录里的 DEPLOY-PROMPT.md、TEMPLATE-MANIFEST.md、README-GOAL-INTEGRATED.md 和 goal-development-base/AGENTS.md，理解这个模板会创建什么运行态。

然后优先运行：
python ".\docs\agent-lanes-goal-integrated-template\scripts\deploy_agent_lanes_template.py"

部署要求：
- 不要删除文件。
- 不要覆盖已有业务代码。
- 如果目标项目已有 AGENTS.md、docs/、scripts/、.agents/ 或 .codex/ 内容，只能保守合并或补齐缺失文件，并把冲突写入 docs/goal-agent-lanes-integration-notes.md。
- 部署后读取 agent-lanes/INSTALL-REPORT.md。
- 运行模板自带的可用校验脚本。
- 最后告诉我已经创建了哪些文件、哪些文件被跳过、有哪些冲突或需要我确认的事项。

部署完成后，请把 agent-lanes/dashboard.md 作为主入口，把 agent-lanes/message-log.jsonl、各 lane 的 worklog.md 和 completion callback 作为追溯记录。
```

如果模板没有放在默认路径，只需要告诉 Codex 模板目录，并使用脚本的可选参数 `--template-dir`。

更完整的部署提示词在：

```text
agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md
```

## 这个项目解决什么问题

当一个 Codex 项目从一次性任务变成长期迭代后，最容易丢失的是上下文、职责边界、验收证据和回报路径。Codex Apex 把这些东西模板化：

- 用 Agent Lanes 管多线程、多泳道、多智能体协作。
- 用 GOAL Development Base 管单个泳道内部的目标、计划、执行、验证和复盘。
- 用 message log、worklog、dashboard 和 completion callback 保留可追溯记录。
- 用 guardian/review/evolution 让权限、风险、验收和规则沉淀有固定位置。
- 用持久化运行态文件支持主调度或泳道线程恢复：线程可以换，运行态不能丢。

恢复和持久化说明入口：

```text
agent-lanes-goal-integrated-template/PERSISTENT-RUNTIME-FILES.md
agent-lanes-goal-integrated-template/orchestrator-recovery-template.md
agent-lanes-goal-integrated-template/goal-development-base/.agents/skills/lane-recovery-runner/SKILL.md
```

## 快速使用

1. 把 `agent-lanes-goal-integrated-template/` 复制到目标项目。
2. 打开 `agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md`。
3. 在目标项目根目录的 Codex 里粘贴一键启动提示词。
4. 部署后优先看 `agent-lanes/dashboard.md`、`agent-lanes/message-log.jsonl` 和各泳道 `worklog.md`。

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

当前模板包版本：`20260703-loop-empty-array-warning-fix`。

- 保留 Next Mainline Slice Selection，用于主线自动续航和下一切片选择。
- 修复 Product Loop 字段告警：空的 `blocking_concerns` / `backlog_concerns` 数组表示当前无 concern，不再视为字段缺失。
- 新增 `frontend-workflow-planner` 和 `VERSION-HISTORY.md`。
