# Agent Lanes Working Copy

This folder is the reusable adjustment space for the Agent Lanes template.

## Purpose

Use this copy to test changes before touching the source template under `docs/agent-lanes/`.

## Promotion Flow

1. Keep `docs/agent-lanes-template-snapshots/2026-06-23-original/` unchanged as the baseline.
2. Make proposed improvements in `docs/agent-lanes-working-copy/`.
3. Validate the improved workflow in the project-local runtime under `agent-lanes/`.
4. If the improvement holds up, promote the change into `docs/agent-lanes/`.
5. Record the reason and evidence in `agent-lanes/message-log.jsonl` or the relevant lane worklog.

## Current Direction

- Add thread lifecycle operations to the template.
- Clarify the difference between global Skill, project-local template, and project-local runtime.
- Make template evolution explicit instead of editing the source template first.
- Add a required completion callback: every non-orchestrator lane must notify the orchestrator thread when a task reaches `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, or `BLOCKED`.
- Add `BOOTSTRAP-PROMPT.md`: a copy-paste prompt for initializing this template in another Codex project after the template folder is copied there.

## 2026-06-23: GOAL Integrated Template

Created a new integrated template copy at `docs/agent-lanes-goal-integrated-template/`.

This copy includes:

- Agent Lanes working-copy files.
- Embedded GOAL Development Base under `goal-development-base/`.
- `README-GOAL-INTEGRATED.md`.
- `LANE-GOAL-SKILL-MAP.md`.
- `LANE-SKILL-HOOK-MATRIX.md`.
- `BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md`.

Intent:

- Let another Codex project initialize both local GOAL skills and Agent Lanes runtime from one copied template folder.
- Keep install behavior additive: copy missing files, merge root `AGENTS.md`, record conflicts, avoid destructive cleanup.
- Make the integration prompt responsible for creating threads, binding lane registry, enforcing completion callback, and running a smoke test.

## 2026-06-23: Runtime System Consolidated Back Into Template

The first production-style runtime proved that the template needs to ship more than prose. This template now carries the runtime assets and defaults needed to reproduce the current system in another Codex project.

Added or promoted:

- 7 default lanes: orchestrator, planning, design, development, guardian, review, evolution.
- Chinese-first lane communication, while preserving technical identifiers and JSON keys in English/original form.
- `completion-callback.template.json` as a first-class template file.
- `scripts/render_dashboard.py` as a first-class template file.
- Dashboard-first operating habit: people inspect `agent-lanes/dashboard.md`; machines trace `agent-lanes/message-log.jsonl`.
- Multi-lane GOAL slimming: structured lane dispatch can replace formal GOAL ceremony for low-risk tasks.
- Capability Exit Check: after 2-3 consecutive GOALs on one provider/capability, project-orchestrator must decide whether to stop deepening and return to the highest-value product vertical loop.

Promotion boundary:

- Keep business-specific paths out of the template. Use `<PRIMARY_MODULE>` and target-project docs instead of copying source-project-only module names.
- Do not copy runtime logs or thread ids into the reusable template; only copy templates, scripts, protocols and bootstrap prompts.
- Do not delete or overwrite target project files during bootstrap; merge additively and record conflicts.
- Template evolution sync: when a runtime mechanism evolves, update the template package at the same time. Matching scripts, protocols, deploy prompts, README, manifest and GOAL base files should stay in sync unless there is a documented reason not to.
- Evolution completion reports should call out template sync explicitly. If template sync is skipped, mark the result `DONE_WITH_CONCERNS` and explain what must be copied later.
