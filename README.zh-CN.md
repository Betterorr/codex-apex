# Codex Apex

Codex Apex 是一套用于 Codex 长期项目协作的 Agent Lanes + GOAL 开源模板。

它的目标不是再加一层漂亮外壳，而是把项目推进过程中真正容易丢失的东西落到文件里：多泳道协作、目标拆解、价值切片、证据、回调、审核、恢复和演进。

## 最新版本

当前版本：**Agent Lanes GOAL Portable v2.3**

这一版是基于 GPT-5.6 重新升级过的版本。相比上一版，它重点解决一个问题：旧版更容易让 Agent 陷入“加壳”“机制细节”“格式推敲”的循环里，而 v2.3 把主线拉回到真实产品价值和可验收切片。

主要升级：

- 新增 `Value Slice` 和 `Value Slice Completion` 模板，用一个明确的价值切片组织派发和验收。
- 新增 `Product Value Gate`、`Value Delta Gate`，让每次推进先回答“对产品有没有实际变化”。
- 新增 `control_provenance`、`resolve_authorization`、`evidence_receipt`、`value_slice_ledger` 等脚本。
- 新增 `current-state` 和 `product-feature-status` 状态模板。
- 保留一键启动体验：不需要手填项目名，项目名默认取当前 Codex 所在项目文件夹名。

发布包 SHA-256：

```text
873323E414CAA613A96407E229D339D47FE5C7B9F1DA6B322FC62144C57C5969
```

## 一键启动方式

把 `agent-lanes-goal-integrated-template/` 复制到你的目标项目，推荐放在：

```text
<你的项目>/docs/agent-lanes-goal-integrated-template/
```

然后在目标项目根目录打开 Codex，把下面这段提示词复制进去：

```text
你现在在 Codex 里工作。请把 Agent Lanes + GOAL 开发基座模板部署到当前项目。

默认假设：
- 当前 Codex 工作目录就是目标项目根目录。
- 当前项目文件夹名就是项目名。
- 模板目录在 docs/agent-lanes-goal-integrated-template。
- 主要模块目录先使用 "."。
- 主调度线程 id 先使用 "pending_setup"。

请先读取：
- docs/agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md
- docs/agent-lanes-goal-integrated-template/TEMPLATE-MANIFEST.md
- docs/agent-lanes-goal-integrated-template/README-GOAL-INTEGRATED.md
- docs/agent-lanes-goal-integrated-template/goal-development-base/AGENTS.md

然后运行：
python ".\docs\agent-lanes-goal-integrated-template\scripts\deploy_agent_lanes_template.py"

部署要求：
- 不要删除文件。
- 不要覆盖已有业务代码。
- 如果目标项目已有 AGENTS.md、docs/、scripts/、.agents/ 或 .codex/ 内容，只能保守合并或补齐缺失文件，并把冲突写入 docs/goal-agent-lanes-integration-notes.md。
- 部署后读取 agent-lanes/INSTALL-REPORT.md。
- 尽量运行模板自带的可用校验脚本。
- 最后告诉我创建了哪些文件、跳过了哪些文件、有哪些冲突或需要我确认的事项。

部署完成后，请把 agent-lanes/dashboard.md 作为主入口，把 agent-lanes/message-log.jsonl、各 lane 的 worklog.md、completion callback、evidence receipt 和 value-slice-ledger.jsonl 作为追踪记录。
```

如果模板没有放在默认路径，只需要告诉 Codex 模板目录，并使用脚本的可选参数 `--template-dir`。

## 它会创建什么

部署脚本会在目标项目里创建本地运行态：

```text
agent-lanes/
  agent-registry.json
  agent-lanes.md
  dashboard.md
  message-log.jsonl
  transport-log.jsonl
  value-slice-ledger.jsonl
  callback-inbox/
  lanes/
    orchestrator/
    planning/
    design/
    development/
    guardian/
    review/
    evolution/

.agents/skills/
.codex/hooks/
.codex/gates/
docs/product-feature-status.json
```

## 这个项目解决什么问题

当一个 Codex 项目从一次性任务变成长期迭代后，最容易丢失的是上下文、职责边界、验收证据、回调路径和主线优先级。Codex Apex 把这些东西模板化，让项目可以换线程、分泳道、可恢复、可追踪，同时尽量让每次推进都绑定到真实价值切片。

## 开源策略

- GitHub 默认入口使用英文，降低外部理解门槛。
- 中文说明保留为第一阶段的主要操作文本。
- 文件名、命令、JSON key、状态枚举、路径和 API 名保持英文或原文，避免实际执行时漂移。

## 许可证

MIT
