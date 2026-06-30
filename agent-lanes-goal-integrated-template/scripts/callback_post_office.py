#!/usr/bin/env python3
"""Batch lane callbacks and prepare one direct thread message.

The post office keeps ``message-log.jsonl`` as an audit log, but the user-facing
handoff is the generated ``thread_prompt``. A lane that runs the delivery script
must send that one prompt to the orchestrator thread with ``send_message_to_thread``.
The script must not move callbacks out of ``pending`` unless it can also return
or persist a complete ``thread_prompt`` for the same batch.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TZ = timezone(timedelta(hours=8))
DEFAULT_ORCHESTRATOR_THREAD_ID = "pending_setup"


def now_dt() -> datetime:
    return datetime.now(TZ).replace(microsecond=0)


def now_text() -> str:
    return now_dt().isoformat()


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


def safe_name(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return text[:120] or "callback"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_callback(path: Path) -> dict[str, Any]:
    callback = json.loads(path.read_text(encoding="utf-8-sig"))
    if not callback.get("message_id"):
        raise SystemExit(f"Callback file must include message_id: {path}")
    callback.setdefault("task_type", "completion_callback")
    callback.setdefault("delivery_mode", "spooled")
    callback.setdefault("created_at", now_text())
    return callback


def resolve_orchestrator_thread_id(project_root: Path, explicit_value: str | None) -> str:
    if explicit_value and explicit_value != DEFAULT_ORCHESTRATOR_THREAD_ID:
        return explicit_value
    registry_path = project_root / "agent-lanes" / "agent-registry.json"
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8-sig"))
            for agent in registry.get("agents", []):
                if agent.get("agent_id") == "orchestrator" and agent.get("thread_id"):
                    return str(agent["thread_id"])
        except (OSError, json.JSONDecodeError):
            pass
    return os.environ.get("AGENT_LANES_ORCHESTRATOR_THREAD_ID", DEFAULT_ORCHESTRATOR_THREAD_ID)


def latest_orchestrator_state(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    states = [row for row in rows if row.get("task_type") == "orchestrator_state"]
    return states[-1] if states else None


def state_is_idle(state: dict[str, Any] | None) -> tuple[bool, str]:
    if not state:
        return False, "unknown_no_orchestrator_state"
    state_value = str(state.get("state", "")).lower()
    lease_until = parse_time(state.get("lease_until"))
    if state_value == "idle":
        return True, "idle"
    if state_value == "busy" and lease_until and lease_until <= now_dt():
        return True, "busy_lease_expired"
    if state_value == "busy":
        return False, "busy"
    return False, f"unknown_state_{state_value or 'empty'}"


def collect_pending(inbox_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    pending_dir = inbox_root / "pending"
    if not pending_dir.exists():
        return []
    return [(path, read_callback(path)) for path in sorted(pending_dir.glob("*.json"))]


def append_callback_if_missing(log_path: Path, rows: list[dict[str, Any]], callback: dict[str, Any]) -> None:
    if any(row.get("message_id") == callback.get("message_id") for row in rows):
        return
    append_jsonl(log_path, callback)
    rows.append(callback)


def as_list(value: Any) -> list[Any]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    return [value]


def compact(value: Any, max_len: int = 420) -> str:
    text = str(value or "").replace("\r", "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def full_text(value: Any) -> str:
    return str(value or "").replace("\r", "").strip()


def lane_label(value: Any) -> str:
    labels = {
        "planning": "规划泳道",
        "design": "设计泳道",
        "development": "开发泳道",
        "guardian": "守门泳道",
        "review": "验收泳道",
        "evolution": "进化泳道",
        "orchestrator": "主调度泳道",
        "callback_post_office": "回报邮局",
    }
    text = str(value or "")
    return labels.get(text, text or "未知泳道")


def bullet_block(title: str, values: list[Any]) -> list[str]:
    if not values:
        return []
    lines = [f"   {title}："]
    for item in values:
        lines.append(f"   - {full_text(item)}")
    return lines


def build_thread_prompt(batch_id: str, callbacks: list[dict[str, Any]], reason: str) -> str:
    lines: list[str] = []
    lines.append("【邮局合并回报】")
    lines.append(f"本批共 {len(callbacks)} 条泳道回报。请直接按本消息处理，不需要再去 message-log 收件箱读取原文。")
    lines.append("message-log 只作为审计备份；如需查证，再打开对应记录。")
    lines.append("")
    for index, callback in enumerate(callbacks, start=1):
        source = lane_label(callback.get("from_agent"))
        status = callback.get("status", "-")
        summary = full_text(callback.get("summary"))
        next_lane = lane_label(callback.get("next_recommended_lane"))
        next_action = full_text(callback.get("next_recommended_action"))
        reply_to = callback.get("reply_to")

        lines.append(f"{index}. {source} · {status}")
        if reply_to:
            lines.append(f"   对应任务：{reply_to}")
        if summary:
            lines.append(f"   原文摘要：{summary}")
        lines.extend(bullet_block("证据", as_list(callback.get("evidence"))))
        lines.extend(bullet_block("变更文件", as_list(callback.get("changed_files"))))
        concerns = as_list(callback.get("concerns"))
        if concerns:
            lines.extend(bullet_block("风险/关注点", concerns))
        else:
            lines.append("   风险/关注点：无阻塞风险。")
        if callback.get("next_recommended_lane") or next_action:
            lines.append(f"   建议下一泳道：{next_lane or '-'}")
        if next_action:
            lines.append(f"   建议动作：{next_action}")
        lines.append("")

    lines.append("主调度处理要求：")
    lines.append("- 直接基于本合并消息做下一步判断。")
    lines.append("- 不要再回复“我去 message-log 读取完整 callback”。")
    lines.append("- 只有证据冲突、需要审计或疑似重复时，才打开 message-log 查证。")
    lines.append(f"批次编号：{batch_id}")
    lines.append(f"投递原因：{reason}")
    return "\n".join(lines).strip() + "\n"


def drain_pending(
    project_root: Path,
    inbox_root: Path,
    log_path: Path,
    reason: str,
    orchestrator_thread_id: str,
) -> dict[str, Any]:
    pending = collect_pending(inbox_root)
    if not pending:
        return {"status": "nothing_to_drain", "pending_count": 0}

    batch_id = f"callback-batch-{now_dt().strftime('%Y%m%dT%H%M%S%z')}"
    delivered_dir = inbox_root / "delivered" / safe_name(batch_id)
    outbox_dir = inbox_root / "outbox"
    delivered_dir.mkdir(parents=True, exist_ok=True)
    outbox_dir.mkdir(parents=True, exist_ok=True)

    rows = read_jsonl(log_path)
    callback_ids: list[str] = []
    callbacks: list[dict[str, Any]] = []
    summaries: list[dict[str, str]] = []
    for path, callback in pending:
        callback["batch_id"] = batch_id
        callback["delivery_mode"] = "batched_log"
        callback_ids.append(str(callback["message_id"]))
        callbacks.append(callback)
        summaries.append(
            {
                "message_id": str(callback.get("message_id", "")),
                "from_agent": str(callback.get("from_agent", "")),
                "status": str(callback.get("status", "")),
                "summary": compact(callback.get("summary"), 180),
            }
        )
        append_callback_if_missing(log_path, rows, callback)
        shutil.move(str(path), str(delivered_dir / path.name))

    thread_prompt = build_thread_prompt(batch_id, callbacks, reason)
    message_path = delivered_dir / "orchestrator-message.md"
    message_path.write_text(thread_prompt, encoding="utf-8", newline="\n")

    outbox = {
        "message_id": f"{batch_id}-thread-send",
        "batch_id": batch_id,
        "target_thread_id": orchestrator_thread_id,
        "thread_prompt": thread_prompt,
        "status": "READY_TO_SEND",
        "created_at": now_text(),
    }
    outbox_path = outbox_dir / f"{safe_name(batch_id)}-thread-send.json"
    write_json(outbox_path, outbox)

    batch = {
        "message_id": batch_id,
        "from_agent": "callback_post_office",
        "to_agent": "主调度泳道",
        "task_type": "callback_batch_ready",
        "delivery_mode": "direct_thread_prompt_ready",
        "status": "READY_TO_SEND",
        "summary": f"{len(callback_ids)} 条泳道回报已合并为 1 条可直接发送给主调度的原文消息。",
        "callback_ids": callback_ids,
        "callback_summaries": summaries,
        "orchestrator_message": thread_prompt,
        "orchestrator_message_path": message_path.relative_to(project_root).as_posix(),
        "thread_prompt": thread_prompt,
        "target_thread_id": orchestrator_thread_id,
        "outbox_path": outbox_path.relative_to(project_root).as_posix(),
        "delivered_dir": delivered_dir.relative_to(project_root).as_posix(),
        "drain_reason": reason,
        "created_at": now_text(),
    }
    append_jsonl(log_path, batch)
    return {"status": "ready_to_send", "batch": batch}


def write_state(state_path: Path, row: dict[str, Any]) -> None:
    row = dict(row)
    row["updated_at"] = now_text()
    row["pid"] = os.getpid()
    write_json(state_path, row)


def run_once(project_root: Path, poll_interval_seconds: int, orchestrator_thread_id: str) -> dict[str, Any]:
    agent_lanes = project_root / "agent-lanes"
    inbox_root = agent_lanes / "callback-inbox"
    log_path = agent_lanes / "message-log.jsonl"
    state_path = inbox_root / "post-office-state.json"
    pid_path = inbox_root / "post-office.pid"

    inbox_root.mkdir(parents=True, exist_ok=True)
    (inbox_root / "pending").mkdir(parents=True, exist_ok=True)
    (inbox_root / "delivered").mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(os.getpid()), encoding="utf-8")

    rows = read_jsonl(log_path)
    idle, reason = state_is_idle(latest_orchestrator_state(rows))
    pending_count = len(collect_pending(inbox_root))
    if pending_count:
        drain_reason = reason if idle else f"direct_prompt_required_despite_{reason}"
        result = drain_pending(project_root, inbox_root, log_path, drain_reason, orchestrator_thread_id)
        write_state(
            state_path,
            {
                "status": "running",
                "last_action": result.get("status"),
                "last_reason": reason,
                "pending_count": len(collect_pending(inbox_root)),
                "poll_interval_seconds": poll_interval_seconds,
            },
        )
        return result

    result = {"status": "waiting", "pending_count": pending_count, "reason": reason}
    write_state(
        state_path,
        {
            "status": "running",
            "last_action": "waiting",
            "last_reason": reason,
            "pending_count": pending_count,
            "poll_interval_seconds": poll_interval_seconds,
        },
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Agent Lanes callback post office.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--poll-interval-seconds", type=int, default=60)
    parser.add_argument("--once", action="store_true", help="Check once and exit.")
    parser.add_argument(
        "--orchestrator-thread-id",
        default=None,
        help="Defaults to agent-lanes/agent-registry.json orchestrator.thread_id, then AGENT_LANES_ORCHESTRATOR_THREAD_ID, then pending_setup.",
    )
    args = parser.parse_args()

    if args.poll_interval_seconds < 1:
        raise SystemExit("--poll-interval-seconds must be >= 1")

    project_root = Path(args.project_root).resolve()
    orchestrator_thread_id = resolve_orchestrator_thread_id(project_root, args.orchestrator_thread_id)
    inbox_root = project_root / "agent-lanes" / "callback-inbox"
    state_path = inbox_root / "post-office-state.json"
    inbox_root.mkdir(parents=True, exist_ok=True)
    write_state(state_path, {"status": "running", "poll_interval_seconds": args.poll_interval_seconds})

    try:
        while True:
            result = run_once(project_root, args.poll_interval_seconds, orchestrator_thread_id)
            if args.once:
                print(json.dumps(result, ensure_ascii=True, indent=2))
                return 0
            time.sleep(args.poll_interval_seconds)
    finally:
        write_state(state_path, {"status": "stopped", "poll_interval_seconds": args.poll_interval_seconds})


if __name__ == "__main__":
    raise SystemExit(main())
