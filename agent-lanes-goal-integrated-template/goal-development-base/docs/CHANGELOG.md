# Changelog

## 2026-07-11

- Agent Lanes V2.1：自动推进机器事实收敛到 current-state、Value Slice ledger、Product Value Gate 和 Value Delta Gate；默认连续两切片后用户检查点，外部副作用必须精确解析授权。

## Unreleased

### Added

- Added post-office readable delivery artifacts: merged
  `orchestrator-message.md` and outbox `*-thread-send.json` files must be
  written for stable Windows/PowerShell/Desktop Chinese preview, while JSONL
  remains an append-only audit backup.
- Added post-office retry-state visibility: dashboards must show whether the
  latest merged callback outbox is generated-to-send, pending retry, or already
  sent/handled, including the outbox path, target thread and merged-message
  file for manual retry.
- Added mechanism checks for post-office readable output encoding, retry-state
  fields, retry instructions and dashboard latest-outbox status so future
  template copies do not regress to unreadable or invisible delivery state.
- Added `Anti-Shell Gate`: after a stage reaches `current-stage-good-enough`,
  review returns no `blocking_concerns`, or a chain has completed design ->
  local consume -> focused review, the next step must default to a different
  P1/P2 mainline slice, real sample/quality confidence, or user-perspective
  vertical acceptance. More handoff, readiness, screenshots, evidence-only or
  review-surface work must cite a concrete P1/P2 blocker.
- Added dashboard pending consistency guidance: human-facing dashboards should
  reconcile pending dispatches with `reply_to`, lane callback text, task ids,
  message-log and worklog before showing an item as still waiting.
- Added user-request separation for dashboards: user messages to the
  orchestrator are shown as orchestrator requests, not lane dispatches waiting
  for completion callbacks.
- Added outbox fallback semantics for post-office delivery: if
  `send_message_to_thread` fails with a tool-level error such as
  `no active turn to steer`, the merged `thread_prompt`, `outbox_path` and
  audit rows remain the source of truth and should be retried, not replaced by
  a short wake or duplicate business work.
- Added `Dynamic Boundary Gate`: high-risk capabilities such as provider/live
  API, secrets, scheduler, writeback, production feed, regulated operations,
  `quality_reviewed` and `production_ready` are authorization gates, not
  permanent bans. Once a user grants scoped authorization, lanes should proceed
  with controlled implementation, smoke, evidence, quality review or production
  preparation instead of repeating generic boundary blocks.
- Added `Human-Readable Frontend Gate` for user-facing UI. Main reading layers
  must be Chinese-first and explain state, judgment, evidence, risk and next
  action in user language. Raw enums, JSON keys, internal state names, paths,
  validator fields, commands, ids and debug details must move to audit or
  diagnostic layers.
- Added `Tool-Level IA Gate` for complex workbench/product-map UI. Frontend
  plans and reviews must define user goals, top-level pages, page
  responsibilities, user questions, card responsibilities, field purposes,
  entries, result-review paths and state boundaries before accepting a tool map.
- Added `Internal Simulation Semantics Gate` for generic internal-simulation workflows.
  boundary. Projects must distinguish current local/static/non-production
  samples, product-internal simulated execution state, and high-risk external
  execution that needs guardian/user authorization.
- Added `Open Source Integration Gate` for requests to reuse or adapt existing
  frontend/backend/open-source implementations, requiring license,
  attribution, dependency, local smoke, adapter and guardian boundaries before
  any integration work.
- Added Figma-style frontend design review gates for complex workbench UIs:
  first-screen task focus, action path, visual hierarchy, audit-detail folding,
  status semantics, human-readable labels, narrow-screen readability and visible
  risk prompts.
- Added `Decision-Usefulness Gate` for complex business cards. Card-based UIs
  must state the current judgment, impact on the user's core decision, 2-4
  readable evidence points, veto/risk conditions, next human action and where
  technical audit details are folded.
- Added `docs/capability-provider-contract.md` as the generic provider adapter
  standard. External APIs, cloud providers, local models, CLIs, SDKs and media
  tools now default to internal capability contract -> provider adapter/CLI
  wrapper -> real dependency, with heavyweight runtimes kept outside the app.
- Added real-execution self-closing rules: real path/cwd/input/output wiring
  failures should be fixed and rerun in the same GOAL, while successful real
  runs should automatically save evidence, connect downstream consumption,
  update registry and run focused gates.
- Added mock and media fixture boundaries: mock/stub/monkeypatch tests cannot
  advance provider maturity, audio fixtures cannot imply full video/raw-video/
  scene-split/atom closure, and large media fixtures should be external or
  generated.
- Added `scripts/validate-capability-status.ps1` to validate the generic
  capability registry, including JSON shape, maturity values, required fields,
  evidence records and present/verified evidence paths.
- Added a reusable definition for "user-usable capability": entry point, real or
  fixed fixture input, real output/artifact, failure state, rerun command/gate
  and a visible result location.
- Added capability variants guidance so materially different provider modes
  such as CPU/GPU, sync/async, reference/no-reference, batch/single or
  local/cloud do not get hidden behind one maturity value.
- Added lightweight continuation mode for ordinary `continue/next` requests:
  orchestrators now start from the smallest useful context and escalate only for
  state conflicts, high risk, stage boundaries, release/hand-off or unclear next
  steps.
- Added `docs/capability-status.json` as a generic machine-readable registry for
  model/API/CLI/provider maturity, evidence paths, approval state, budget limits
  and next workflow consumption.
- Added template-wide real-first integration rules for external APIs, cloud
  providers, local models, CLIs, SDKs and media tools. The base workflow now
  asks for bounded live-call approval when needed, runs local real smokes by
  default when safe, saves reusable artifacts and tracks maturity from contract
  through production readiness.

### Changed

- Updated `design-brief-builder`, `frontend-quality-runner` and
  `open-source-research-runner` so tool-level IA, internal-simulation semantics
  and open-source integration boundaries are routed by natural-language hooks
  and checked by the mechanism gate.
- Updated `design-brief-builder` and `frontend-quality-runner` so a frontend can
  no longer pass by being field-complete only; user-readable IA and Figma-style
  review findings must be written back to project docs or review artifacts.
- Updated frontend design and quality Skills so `decision_card`, `evidence_card`,
  `workflow_card` and `audit_card` are explicit card types; non-decision cards
  must say they do not support the core business judgment.
- Updated orchestration, planning, development, gates and review rules so
  lightweight continuation escalates when user feedback conflicts with state
  docs or registry evidence is stale.
- Updated review-debounce rules so accumulated small fixes require a merged
  review after 3-5 fixes or before user/customer/production-ready claims.
- Updated development, gate and review Skills with risk-tiered execution,
  review-debounce and a 2-3 preparatory-slice budget so future projects are
  nudged toward vertical user-capability closure.
- Updated orchestrator, development, gate, review and release Skills so
  fake/check/contract cannot be mistaken for completed real integration.
- Updated hook routing and mechanism checks to preserve real integration rules
  when the template is copied to future projects.

### Fixed

- 

### Verification

- `.\scripts\validate-skills.ps1`
- `.\scripts\check-skill-mechanism.ps1`
- `.\scripts\check-framework.ps1`
