#!/usr/bin/env python3
"""Check Agent Lanes callback post office protocol health.

Default mode is advisory: findings are printed but exit code remains 0.
Use --strict to fail on errors. This keeps historical legacy callbacks from
blocking current work while still surfacing new protocol drift.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TZ = timezone(timedelta(hours=8))
ORCHESTRATOR_NAMES = {"orchestrator", "主调度泳道", "主调度"}
NON_ORCHESTRATOR = {
    "planning",
    "规划泳道",
    "design",
    "设计泳道",
    "development",
    "开发泳道",
    "guardian",
    "守门泳道",
    "review",
    "验收泳道",
    "evolution",
    "进化泳道",
}
COMPLETION_STATUSES = {"DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"}
DIRECT_OK_MODES = {"direct_thread_prompt_ready"}
STRANDED_DELIVERY_MODES = {"spooled", "batched_log"}


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=TZ)
        return parsed
    except ValueError:
        return None


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def include_since(row: dict[str, Any], since: datetime | None) -> bool:
    if since is None:
        return True
    created = parse_time(row.get("created_at") or row.get("updated_at") or row.get("spooled_at"))
    return created is not None and created >= since


def row_time(row: dict[str, Any]) -> datetime | None:
    return parse_time(row.get("created_at") or row.get("updated_at") or row.get("spooled_at"))


def age_minutes(path: Path) -> float:
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=TZ)
    return (datetime.now(TZ) - modified).total_seconds() / 60


def as_text(value: Any) -> str:
    return str(value or "")


def iter_text_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        texts: list[str] = []
        for item in value.values():
            texts.extend(iter_text_values(item))
        return texts
    if isinstance(value, list):
        texts = []
        for item in value:
            texts.extend(iter_text_values(item))
        return texts
    if isinstance(value, str):
        return [value]
    return []


def looks_garbled(value: str) -> bool:
    text = value.strip()
    if not text:
        return False
    if text and set(text) == {"?"}:
        return True
    return "???" in text


def has_garbled_payload(row: dict[str, Any]) -> bool:
    fields = [
        row.get("from_agent"),
        row.get("to_agent"),
        row.get("summary"),
        row.get("evidence"),
        row.get("concerns"),
        row.get("next_recommended_action"),
        row.get("orchestrator_message"),
        row.get("thread_prompt"),
    ]
    return any(looks_garbled(text) for value in fields for text in iter_text_values(value))


def is_completion_like(row: dict[str, Any]) -> bool:
    if row.get("task_type") in {"completion_callback", "completion_callback_protocol_update"}:
        return True
    if row.get("status") not in COMPLETION_STATUSES:
        return False
    completion_fields = {
        "summary",
        "changed_files",
        "evidence",
        "concerns",
        "next_recommended_lane",
        "next_recommended_action",
    }
    present = sum(1 for field in completion_fields if row.get(field) not in (None, "", []))
    return present >= 4


def batch_has_thread_prompt(row: dict[str, Any]) -> bool:
    return bool(row.get("thread_prompt") and row.get("outbox_path") and row.get("target_thread_id"))


def has_post_office_batch(row: dict[str, Any], batch_ids: set[str]) -> bool:
    message_id = as_text(row.get("message_id"))
    return bool(row.get("batch_id")) or message_id in batch_ids or row.get("delivery_mode") in DIRECT_OK_MODES


def has_completed_thread_prompt_delivery(row: dict[str, Any], thread_ready_callback_ids: set[str]) -> bool:
    message_id = as_text(row.get("message_id"))
    delivery_mode = as_text(row.get("delivery_mode"))
    if delivery_mode == "direct_thread_prompt_ready" and batch_has_thread_prompt(row):
        return True
    return message_id in thread_ready_callback_ids


def main() -> int:
    parser = argparse.ArgumentParser(description="Check callback post office protocol.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--since", help="Only check message-log rows at or after this ISO timestamp.")
    parser.add_argument("--pending-max-age-minutes", type=int, default=30)
    parser.add_argument("--strict", action="store_true", help="Exit 1 if errors are found.")
    parser.add_argument(
        "--strict-direct-bypass",
        action="store_true",
        help="Treat direct completion-like callbacks as errors instead of warnings.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    agent_lanes = project_root / "agent-lanes"
    log_path = agent_lanes / "message-log.jsonl"
    pending_dir = agent_lanes / "callback-inbox" / "pending"
    state_path = agent_lanes / "callback-inbox" / "post-office-state.json"
    policy_path = agent_lanes / "callback-inbox" / "post-office-policy.json"

    since = parse_time(args.since) if args.since else None
    legacy_direct_bypass_ids: set[str] = set()
    legacy_stranded_delivery_ids: set[str] = set()
    legacy_garbled_payload_ids: set[str] = set()
    legacy_garbled_payload_before: datetime | None = None
    if policy_path.exists():
        policy = read_json(policy_path)
        if since is None:
            since = parse_time(policy.get("enabled_at"))
        legacy_items = policy.get("legacy_direct_bypass_message_ids", []) or []
        for item in legacy_items:
            if isinstance(item, str):
                legacy_direct_bypass_ids.add(item)
            elif isinstance(item, dict) and item.get("message_id"):
                legacy_direct_bypass_ids.add(str(item.get("message_id")))
        stranded_items = policy.get("legacy_stranded_delivery_message_ids", []) or []
        for item in stranded_items:
            if isinstance(item, str):
                legacy_stranded_delivery_ids.add(item)
            elif isinstance(item, dict) and item.get("message_id"):
                legacy_stranded_delivery_ids.add(str(item.get("message_id")))
        garbled_items = policy.get("legacy_garbled_payload_message_ids", []) or []
        for item in garbled_items:
            if isinstance(item, str):
                legacy_garbled_payload_ids.add(item)
            elif isinstance(item, dict) and item.get("message_id"):
                legacy_garbled_payload_ids.add(str(item.get("message_id")))
        legacy_garbled_payload_before = parse_time(policy.get("legacy_garbled_payload_before"))

    rows = read_jsonl(log_path)
    scoped_rows = [row for row in rows if include_since(row, since)]

    completion_like_rows = [row for row in scoped_rows if is_completion_like(row)]
    batches = [row for row in rows if row.get("task_type") == "callback_batch_ready"]
    batch_ids: set[str] = set()
    thread_ready_batch_ids: set[str] = set()
    thread_ready_callback_ids: set[str] = set()
    batch_message_paths = 0
    batch_thread_prompts = 0
    for batch in batches:
        if batch.get("orchestrator_message") and batch.get("orchestrator_message_path"):
            batch_message_paths += 1
        if batch_has_thread_prompt(batch):
            batch_thread_prompts += 1
            thread_ready_batch_ids.add(as_text(batch.get("message_id")))
            for callback_id in batch.get("callback_ids", []) or []:
                thread_ready_callback_ids.add(str(callback_id))
        for callback_id in batch.get("callback_ids", []) or []:
            batch_ids.add(str(callback_id))

    errors: list[str] = []
    warnings: list[str] = []
    legacy_direct_bypass: list[str] = []
    legacy_garbled_payload: list[str] = []

    for row in completion_like_rows:
        from_agent = as_text(row.get("from_agent"))
        to_agent = as_text(row.get("to_agent"))
        message_id = as_text(row.get("message_id"))
        if from_agent in ORCHESTRATOR_NAMES:
            continue
        if from_agent not in NON_ORCHESTRATOR:
            continue
        if to_agent not in ORCHESTRATOR_NAMES:
            continue
        if has_completed_thread_prompt_delivery(row, thread_ready_callback_ids):
            continue
        if row.get("delivery_mode") in STRANDED_DELIVERY_MODES or row.get("batch_id") in batch_ids:
            finding = (
                "completion callback reached message-log but has no direct thread_prompt delivery: "
                f"{message_id} from={from_agent} to={to_agent} "
                f"task_type={row.get('task_type') or '-'} delivery_mode={row.get('delivery_mode') or '-'} "
                f"batch_id={row.get('batch_id') or '-'}"
            )
            if message_id in legacy_stranded_delivery_ids or message_id in legacy_direct_bypass_ids:
                legacy_direct_bypass.append(f"legacy migration stranded delivery: {finding}")
            else:
                warnings.append(finding)
            continue
        finding = (
            "direct completion-like callback bypassed post office: "
            f"{message_id} from={from_agent} to={to_agent} "
            f"task_type={row.get('task_type') or '-'} delivery_mode={row.get('delivery_mode') or '-'}"
        )
        if message_id in legacy_direct_bypass_ids:
            legacy_direct_bypass.append(f"legacy migration direct bypass: {finding}")
            continue
        if args.strict_direct_bypass:
            errors.append(finding)
        else:
            warnings.append(finding)

    for batch in [row for row in scoped_rows if row.get("task_type") == "callback_batch_ready"]:
        message_id = as_text(batch.get("message_id"))
        if message_id in thread_ready_batch_ids:
            continue
        callback_ids = {str(item) for item in batch.get("callback_ids", []) or []}
        if callback_ids and callback_ids.issubset(thread_ready_callback_ids):
            continue
        if batch.get("delivery_mode") in STRANDED_DELIVERY_MODES or not batch_has_thread_prompt(batch):
            if message_id in legacy_stranded_delivery_ids:
                legacy_direct_bypass.append(
                    "legacy migration stranded batch: "
                    f"{message_id} delivery_mode={batch.get('delivery_mode') or '-'} status={batch.get('status') or '-'}"
                )
                continue
            warnings.append(
                "callback batch lacks direct thread_prompt/outbox delivery and may strand callbacks: "
                f"{message_id} delivery_mode={batch.get('delivery_mode') or '-'} status={batch.get('status') or '-'}"
            )

    for row in scoped_rows:
        message_id = as_text(row.get("message_id"))
        if not message_id or not has_garbled_payload(row):
            continue
        finding = f"garbled callback/post-office payload contains replacement question marks: {message_id}"
        created = row_time(row)
        if message_id in legacy_garbled_payload_ids or (
            legacy_garbled_payload_before is not None and created is not None and created <= legacy_garbled_payload_before
        ):
            legacy_garbled_payload.append(f"legacy garbled payload: {finding}")
        else:
            warnings.append(finding)

    spooled_rows = [row for row in scoped_rows if row.get("task_type") == "callback_spooled"]
    for row in spooled_rows:
        reply_to = as_text(row.get("reply_to"))
        if reply_to and reply_to not in batch_ids:
            spool_path = row.get("spool_path")
            if spool_path and not (project_root / str(spool_path)).exists():
                warnings.append(f"spooled callback not found in batch and spool file missing: {reply_to}")

    pending_files = sorted(pending_dir.glob("*.json")) if pending_dir.exists() else []
    for pending in pending_files:
        minutes = age_minutes(pending)
        if minutes >= args.pending_max_age_minutes:
            errors.append(f"pending callback older than {args.pending_max_age_minutes} minutes: {pending} ({minutes:.1f}m)")

    if not state_path.exists():
        warnings.append("post office state file missing: agent-lanes/callback-inbox/post-office-state.json")
    else:
        state = read_json(state_path)
        if state.get("status") not in {"running", "stopped"}:
            warnings.append(f"unknown post office state: {state.get('status')}")

    result = {
        "status": "FAIL" if errors else ("WARN" if warnings else "PASS"),
        "checked_rows": len(scoped_rows),
        "completion_like_checked": len(completion_like_rows),
        "batches_seen": len(batches),
        "batches_with_orchestrator_message": batch_message_paths,
        "batches_with_thread_prompt": batch_thread_prompts,
        "pending_count": len(pending_files),
        "legacy_direct_bypass_count": len(legacy_direct_bypass),
        "legacy_direct_bypass": legacy_direct_bypass,
        "legacy_garbled_payload_count": len(legacy_garbled_payload),
        "legacy_garbled_payload": legacy_garbled_payload,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.strict and errors:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
