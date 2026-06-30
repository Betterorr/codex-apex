# GOAL Log

Use this file to preserve cross-session continuity.

## Entries

### 2026-06-23 - Template Real-First Provider Integration Rules

GOAL:

Upgrade the reusable GOAL development base so future projects with external
APIs, cloud providers, local models, CLIs, SDKs or media tools can move toward
real smoke tests, bounded live calls and workflow integration early instead of
stalling at fake/check/contract.

Scope:

- In:
  - Add generic real integration maturity states.
  - Require local safe dependencies to default toward real smoke/sample tests.
  - Require online or paid live calls to ask the user for explicit bounded
    approval.
  - Preserve reusable artifacts so future gates can reuse test outputs.
  - Update hook routing and mechanism checks.
- Out:
  - No project-specific model, API, product, provider or business rule.
  - No automatic unbounded online calls.
  - No secret values in docs.

Completion standards:

- Project orchestration can choose real integration or approval request as the
  next step when dependencies exist.
- Development, gate, review and release Skills distinguish fake/check/contract
  from real integration.
- Mechanism checks fail if the core real integration clauses are removed.

Verification evidence:

- PASS: `.\scripts\validate-skills.ps1`.
- PASS: `.\scripts\check-skill-mechanism.ps1`.
- PASS: `.\scripts\check-framework.ps1`.

Changed files:

- `AGENTS.md`
- `.agents/skills/project-orchestrator/SKILL.md`
- `.agents/skills/dev-builder/SKILL.md`
- `.agents/skills/gate-runner/SKILL.md`
- `.agents/skills/review-runner/SKILL.md`
- `.agents/skills/release-builder/SKILL.md`
- `.codex/hooks/skill-hooks.md`
- `.codex/gates/skill-mechanism-check.ps1`
- `docs/CHANGELOG.md`
- `docs/04-goal-log.md`

Decisions:

- Safety boundaries should act as execution unlock gates: request approval,
  limit cost/side effects and save evidence, rather than permanently blocking
  real testing.

Residual risks:

- Future projects still need to define their own provider-specific CLI,
  credentials, budget limits and evidence paths.

### YYYY-MM-DD - GOAL title

GOAL:

Scope:

- In:
- Out:

Completion standards:

- 

Verification evidence:

- 

Changed files:

- 

Decisions:

- 

Residual risks:

- 
