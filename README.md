# Codex Apex

Codex Apex is an open template system for running long-lived, multi-lane development workflows inside Codex.

It packages two complementary ideas:

- **Agent Lanes**: a coordination protocol for splitting a project across persistent agent lanes such as orchestration, planning, design, development, guardian review, independent review, and evolution.
- **GOAL Development Base**: a local project operating system for clarifying goals, planning work, implementing changes, validating evidence, reviewing risk, releasing, and evolving the workflow.

The current canonical template is:

```text
agent-lanes-goal-integrated-template/
```

## Start A Project With This Template

This repository is meant to be copied into another Codex project. The template folder is not the runtime itself; it is the installer package that tells Codex how to create the runtime files, lane registry, worklogs, callback routing, gates, and GOAL skills inside your own project.

Template folder:

```text
agent-lanes-goal-integrated-template/
```

Recommended location in your target project:

```text
<TARGET_PROJECT_ROOT>/docs/agent-lanes-goal-integrated-template/
```

### 1. Copy The Template Folder

Clone this repository or download it as a ZIP, then copy this folder into your target project:

```text
agent-lanes-goal-integrated-template/
```

For example:

```text
your-project/
  docs/
    agent-lanes-goal-integrated-template/
```

### 2. Paste This Prompt Into Codex

Paste the whole block into Codex while Codex is opened in your target project. If the template is under `docs/agent-lanes-goal-integrated-template/`, there are no required placeholders.

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

If you placed the template somewhere else, tell Codex the path and use the optional `--template-dir` argument.

The full deployment prompt lives in:

```text
agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md
```

Recovery and persistence references:

```text
agent-lanes-goal-integrated-template/PERSISTENT-RUNTIME-FILES.md
agent-lanes-goal-integrated-template/orchestrator-recovery-template.md
agent-lanes-goal-integrated-template/goal-development-base/.agents/skills/lane-recovery-runner/SKILL.md
```

### What Codex Will Create

After deployment, your target project should gain a runtime structure like:

```text
agent-lanes/
  agent-registry.json
  agent-lanes.md
  message-log.jsonl
  dashboard.md
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
docs/
```

## Why This Exists

Codex is strongest when project context, execution boundaries, evidence, and follow-up routing are explicit. Codex Apex turns those practices into a portable template so a project can keep moving without losing track of:

- who owns each type of work,
- where decisions and worklogs live,
- how completion callbacks are delivered,
- which gates must stop for user confirmation,
- how review and evolution feed back into the system,
- how a new orchestrator or lane thread can recover from persistent runtime files when an old thread is too long or fails.

## Quick Start

1. Copy `agent-lanes-goal-integrated-template/` into the target project, preferably under `docs/`.
2. Open `agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md`.
3. Paste the minimal prompt into Codex from the target project root.
4. Review the generated runtime files, especially `agent-lanes/dashboard.md`, `agent-lanes/message-log.jsonl`, and each lane worklog.

For the GOAL-integrated version, start with:

```text
agent-lanes-goal-integrated-template/README-GOAL-INTEGRATED.md
agent-lanes-goal-integrated-template/BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md
```

## Language Versions

The original template content is Chinese-first because it was built for Chinese project operations. This repository uses English as the default public entry point while preserving the Chinese version as the canonical operating text during the first open-source phase.

- English entry: `README.md`
- Chinese entry: `README.zh-CN.md`
- Language and release strategy: `docs/i18n-strategy.zh-CN.md`

## Repository Layout

```text
.
├── README.md
├── README.zh-CN.md
├── docs/
│   ├── i18n-strategy.zh-CN.md
│   └── release-checklist.zh-CN.md
└── agent-lanes-goal-integrated-template/
    ├── README.md
    ├── README-GOAL-INTEGRATED.md
    ├── DEPLOY-PROMPT.md
    ├── TEMPLATE-MANIFEST.md
    ├── scripts/
    └── goal-development-base/
```

## Current Status

This repository is in its first open-source packaging pass. The template is usable today as a Chinese-first canonical operating template with English public entry points and a minimal bootstrap prompt.

Latest template package: `20260703-loop-empty-array-warning-fix`.

- Preserves Next Mainline Slice Selection for automatic follow-up slice routing.
- Fixes Product Loop warnings so empty `blocking_concerns` and `backlog_concerns` arrays mean no concern, not missing fields.
- Adds `frontend-workflow-planner` and `VERSION-HISTORY.md` to the portable template.

## License

MIT
