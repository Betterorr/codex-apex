# Codex Apex

Codex Apex is an open template system for running long-lived, multi-lane development workflows inside Codex.

It packages two complementary ideas:

- **Agent Lanes**: a coordination protocol for splitting a project across persistent agent lanes such as orchestration, planning, design, development, guardian review, independent review, and evolution.
- **GOAL Development Base**: a local project operating system for clarifying goals, planning work, implementing changes, validating evidence, reviewing risk, releasing, and evolving the workflow.

The current canonical template is:

```text
agent-lanes-goal-integrated-template/
```

## Why This Exists

Codex is strongest when project context, execution boundaries, evidence, and follow-up routing are explicit. Codex Apex turns those practices into a portable template so a project can keep moving without losing track of:

- who owns each type of work,
- where decisions and worklogs live,
- how completion callbacks are delivered,
- which gates must stop for user confirmation,
- how review and evolution feed back into the system.

## Quick Start

1. Copy `agent-lanes-goal-integrated-template/` into the target project.
2. Open `agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md`.
3. Replace the placeholders with the target project paths and thread IDs.
4. Paste the prompt into Codex in the target project.
5. Review the generated runtime files, especially `agent-lanes/dashboard.md`, `agent-lanes/message-log.jsonl`, and each lane worklog.

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

This repository is in its first open-source packaging pass. The template is usable, but the public-facing documentation and licensing still need final review before the first GitHub release.

## License

MIT

