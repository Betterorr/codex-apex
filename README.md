# Codex Apex

Codex Apex is a portable Agent Lanes + GOAL template for running long-lived development work inside Codex.

It helps a project keep coordination, evidence, review, and recovery in files instead of leaving everything inside one chat thread.

## Latest Version

Current release: **Agent Lanes GOAL Portable v2.3**

This v2.3 package is a GPT-5.6-assisted upgrade of the previous public template. The main shift is away from getting stuck polishing wrappers, shells, and secondary mechanism details, and toward value-gated product slices:

- `Value Slice` templates for dispatching work around a concrete user-visible slice.
- `Product Value Gate` and `Value Delta Gate` scripts to keep work tied to product movement.
- control provenance, authorization resolution, evidence receipts, and a value-slice ledger.
- `current-state` and `product-feature-status` templates for durable project state.
- zero-required-placeholder bootstrap: the project name defaults to the current Codex project folder.

Release asset SHA-256:

```text
873323E414CAA613A96407E229D339D47FE5C7B9F1DA6B322FC62144C57C5969
```

## One-Click Bootstrap Prompt

Copy `agent-lanes-goal-integrated-template/` into your target project, preferably here:

```text
<your-project>/docs/agent-lanes-goal-integrated-template/
```

Then open Codex in the target project root and paste this prompt:

```text
You are working inside Codex in the target project.

Please deploy the Agent Lanes + GOAL development-base template into the current project.

Default assumptions:
- The current Codex working directory is the target project root.
- The current project folder name is the project name.
- The template directory is docs/agent-lanes-goal-integrated-template.
- The primary module can start as ".".
- The orchestrator thread id can start as "pending_setup".

First read:
- docs/agent-lanes-goal-integrated-template/DEPLOY-PROMPT.md
- docs/agent-lanes-goal-integrated-template/TEMPLATE-MANIFEST.md
- docs/agent-lanes-goal-integrated-template/README-GOAL-INTEGRATED.md
- docs/agent-lanes-goal-integrated-template/goal-development-base/AGENTS.md

Then run:
python ".\docs\agent-lanes-goal-integrated-template\scripts\deploy_agent_lanes_template.py"

Rules:
- Do not delete files.
- Do not overwrite business code.
- If AGENTS.md, docs/, scripts/, .agents/, or .codex/ already exist, merge conservatively and record conflicts in docs/goal-agent-lanes-integration-notes.md.
- After deployment, read agent-lanes/INSTALL-REPORT.md.
- Run the template's validation scripts where available.
- Tell me which files were created, which were skipped, and what needs confirmation.

Use agent-lanes/dashboard.md as the main entry after deployment.
Use agent-lanes/message-log.jsonl, lane worklogs, completion callbacks, evidence receipts, and value-slice-ledger.jsonl as trace records.
```

If you placed the template somewhere else, tell Codex the path and pass `--template-dir`.

## What It Creates

The deployment script creates a local runtime in the target project:

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

## Why This Exists

Codex is strongest when context, execution boundaries, evidence, callbacks, and review gates are explicit. Codex Apex packages those habits into a reusable template so a project can recover from long chats, hand work across lanes, and keep a durable record of what changed and why.

## Repository Layout

```text
.
|-- README.md
|-- README.zh-CN.md
|-- docs/
|-- agent-lanes-goal-integrated-template/
|   |-- DEPLOY-PROMPT.md
|   |-- TEMPLATE-MANIFEST.md
|   |-- VERSION-HISTORY.md
|   |-- scripts/
|   `-- goal-development-base/
```

## License

MIT
