# Capability Provider Contract

Use this document as the default template for connecting external APIs, local models, CLIs, SDKs, media tools, or platform tasks in any project built on this GOAL base.

## Default Architecture

Every real capability should use this shape:

```text
project workflow
  -> stable internal capability contract
    -> provider adapter or CLI wrapper
      -> local model, external API, SDK, platform task, or media tool
```

Application code and frontend UI should depend on the internal capability contract, not on vendor SDK classes, model directories, API keys, or one-off scripts.

## Required Files

For each provider, keep project-owned files in the repository and keep heavyweight runtime dependencies outside the repository.

- `api/<capability>/<provider>/README.md`: provider purpose, inputs, outputs, limits, install path, safe rerun commands, and known failure modes.
- `api/<capability>/<provider>/manifest.json`: provider id, capability id, runtime type, required env vars, supported variants, output schema, side-effect flags, and maturity.
- `scripts/<capability>-<provider>-cli.*` or `scripts/<capability>-provider-smoke.*`: controlled CLI entrypoint used by backend workflows and gates.
- `artifacts/`, `evidence/`, `frontend/public/bridge/`, or another explicit evidence directory: reusable outputs, task summaries, smoke evidence, and downstream connection evidence.
- `docs/capability-status.json`: machine-readable maturity, approval status, evidence paths, budget limits, rerun command, and next downstream consumer.

External dependencies such as model directories, virtual environments, WSL environments, cloud accounts, large media fixtures, and SDK caches are dependencies, not source code. Document them, but do not embed them into packaged application logic.

## Provider Adapter Rules

- Do not call local model code, vendor SDKs, cloud APIs, or platform task APIs directly from frontend components or high-level business workflows.
- Expose a small stable command or module per capability, such as `tts.generate`, `asr.transcribe`, `digitalHuman.generate`, `media.import`, or `video.render`.
- Put vendor-specific field mapping, auth handling, retry behavior, async polling, and file upload/download logic inside the provider adapter.
- Return project-owned output schemas, not raw vendor responses, unless the raw response is saved separately as evidence.
- Record `provider`, `provider_version_or_path`, `variant`, `input_summary`, `parameter_summary`, `output_path`, `elapsed_ms`, `task_id`, `cost_summary`, `warnings`, `errors`, `side_effects`, and `rerun_command` in evidence.
- Keep secrets in environment variables or local secret stores. Never write API keys into evidence, frontend bridge files, docs, fixtures, or manifests.

## Capability Granularity

Split capabilities or variants when behavior, risk, runtime, or verification differs materially.

Examples:

- `tts.local.cuda.single`
- `tts.local.cuda.batch-worker`
- `tts.cloud.async`
- `asr.local.audio`
- `asr.cloud.live-call`
- `digital-human.cloud.async`

Do not use one maturity value to cover CPU and CUDA, short and long input, reference-input and no-reference generation, local and cloud calls, or sync and async task modes.

## Real Execution Policy

Local providers that are already installed and do not create external cost should default to real smoke or real sample tests. If a real run fails because of path, cwd, env var, input file, encoding, parameter mapping, output directory, or fixture wiring, fix the adapter and rerun the same real path in the same GOAL.

External or paid providers may run real tests only after explicit approval. Approved calls must have a call count or budget limit, fixed test inputs, reusable output artifacts, task/cost/time recording, and secret redaction. If reusable evidence already exists for the same provider, input, and parameter summary, gates should verify the artifact rather than spend credits again.

## Frontend Boundary

The frontend can show capability status, task state, evidence, copied commands, errors, previews, and approved controls. It must not:

- execute arbitrary local shell commands;
- read model directories or secrets directly;
- display API keys;
- bypass backend allowlists;
- pretend a reserved or fixture-only action is a real provider call.

## Completion Claims

Use precise maturity language:

- `contract_defined`: input/output contract exists.
- `dependency_available`: model, CLI, SDK, route, or account is present.
- `real_smoke_passed`: one real minimal call succeeded.
- `real_sample_output_saved`: reusable real output exists.
- `integration_connected`: real output is consumed by the next workflow step.
- `quality_reviewed`: quality, cost, latency, and failure modes have been reviewed.
- `production_ready`: batching, retries, logs, cost controls, rollback, and release boundaries are ready.

Never say a provider is "connected" or "done" unless the maturity level and evidence path make that precise.
