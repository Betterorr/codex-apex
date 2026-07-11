# Agent Lanes + GOAL 一键部署提示词

把本模板目录复制到目标项目后，打开目标项目里的 Codex，复制下面这段提示词即可。

如果模板目录是 `docs/agent-lanes-goal-integrated-template/`，不需要手填项目名。项目名默认就是当前 Codex 工作目录的文件夹名。

## 可复制提示词

```text
你现在在 Codex 里工作。请把 Agent Lanes + GOAL 开发基座模板部署到当前项目。

默认假设：
- 当前 Codex 工作目录就是目标项目根目录。
- 当前项目文件夹名就是项目名。
- 模板目录在 docs/agent-lanes-goal-integrated-template。
- 主要模块目录先使用 "."。
- 主调度线程 id 先使用 "pending_setup"。

请先读取：
- docs/agent-lanes-goal-integrated-template/TEMPLATE-MANIFEST.md
- docs/agent-lanes-goal-integrated-template/VERSION-HISTORY.md
- docs/agent-lanes-goal-integrated-template/README-GOAL-INTEGRATED.md
- docs/agent-lanes-goal-integrated-template/goal-development-base/AGENTS.md

然后优先运行：
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

## 非默认路径

如果模板不在 `docs/agent-lanes-goal-integrated-template/`，使用：

```text
python "<模板目录>\scripts\deploy_agent_lanes_template.py" --template-dir "<模板目录>"
```

如果你确实要显式指定目标项目、项目名或主模块，也可以使用：

```text
python "<模板目录>\scripts\deploy_agent_lanes_template.py" --target-root "<目标项目根目录>" --template-dir "<模板目录>" --project-name "<项目名>" --primary-module "<主要模块目录>"
```

## 部署后的第一步

从一个低风险、可验收的 Value Slice 开始。先确认 `agent-lanes/dashboard.md`、`agent-lanes/agent-registry.json`、`agent-lanes/value-slice-ledger.jsonl` 和 `docs/product-feature-status.json` 已存在，再由主调度泳道派发规划、设计、开发、guardian、review 或 evolution 任务。
