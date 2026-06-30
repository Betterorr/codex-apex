# Changelog

## Unreleased

### Added

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
