#!/usr/bin/env python3
"""Deliver a lane callback through the post office.

The script writes the callback to the local audit queue, asks the post office to
batch pending callbacks once, and prints the single prompt that the lane must
send to the orchestrator thread when it is ready.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import value_slice_ledger
import control_provenance


TZ = timezone(timedelta(hours=8))
DEFAULT_ORCHESTRATOR_THREAD_ID = "pending_setup"




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


def now_text() -> str:
    return datetime.now(TZ).replace(microsecond=0).isoformat()


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
    path.write_text(json.dumps(row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig", newline="\n")


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


def validate_callback_text_quality(callback: dict[str, Any], path: Path) -> None:
    fields = {
        "from_agent": callback.get("from_agent"),
        "to_agent": callback.get("to_agent"),
        "summary": callback.get("summary"),
        "evidence": callback.get("evidence"),
        "concerns": callback.get("concerns"),
        "next_recommended_action": callback.get("next_recommended_action"),
    }
    bad_fields = [name for name, value in fields.items() if any(looks_garbled(text) for text in iter_text_values(value))]
    if bad_fields:
        raise SystemExit(
            "Callback appears to contain mojibake/replacement question marks; "
            "fix the callback file encoding or regenerate the Chinese text before delivery. "
            f"file={path} fields={','.join(bad_fields)}"
        )


def lane_aliases(registry: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for agent in registry.get("agents", []):
        if not isinstance(agent, dict) or not agent.get("agent_id"):
            continue
        agent_id = str(agent["agent_id"])
        for value in (agent_id, agent.get("lane"), agent.get("display_name")):
            if value:
                aliases[str(value)] = agent_id
    return aliases


def validate_callback_semantics(
    callback: dict[str, Any], registry: dict[str, Any], ledger_rows: list[dict[str, Any]], project_root: Path
) -> list[str]:
    errors: list[str] = []
    aliases = lane_aliases(registry)
    from_lane = aliases.get(str(callback.get("from_agent") or ""))
    to_lane = aliases.get(str(callback.get("to_agent") or ""))
    if not from_lane:
        errors.append("from_agent is not a registered lane")
    if to_lane != "orchestrator":
        errors.append("to_agent must resolve to the registered orchestrator lane")
    reply_to = str(callback.get("reply_to") or "")
    dispatch = value_slice_ledger.find_dispatch_event(ledger_rows, reply_to)
    if not dispatch:
        errors.append("reply_to does not match a recorded dispatch_started event")
        return errors
    if str(dispatch.get("value_slice_id") or "") != str(callback.get("value_slice_id") or ""):
        errors.append("callback value_slice_id does not match recorded dispatch")
    target_lane = aliases.get(str(dispatch.get("target_lane") or ""))
    if not target_lane:
        errors.append("recorded dispatch is missing a registered target_lane")
    elif from_lane != target_lane:
        errors.append("callback from_agent does not match recorded dispatch target_lane")
    if dispatch.get("control_version") != value_slice_ledger.CONTROL_VERSION or not dispatch.get("dispatch_hash"):
        errors.append("callback requires a trusted V2.3 dispatch event")
    target_thread_id = str(dispatch.get("target_thread_id") or "")
    if not target_thread_id or str(callback.get("from_thread_id") or "") != target_thread_id:
        errors.append("callback from_thread_id does not match recorded dispatch target thread")
    provenance = callback.get("callback_provenance")
    expected_claim = {
        "dispatch_id": reply_to,
        "value_slice_id": callback.get("value_slice_id"),
        "target_lane": target_lane,
        "target_thread_id": target_thread_id,
        "dispatch_hash": dispatch.get("dispatch_hash"),
    }
    if not isinstance(provenance, dict) or not control_provenance.verify_envelope(project_root, provenance, "lane_callback"):
        errors.append("callback provenance signature is invalid")
    elif provenance.get("claim") != expected_claim:
        errors.append("callback provenance claim does not match dispatch target")
    return errors


def validate_callback_identity(
    callback: dict[str, Any], path: Path, registry: dict[str, Any] | None = None, ledger_rows: list[dict[str, Any]] | None = None, project_root: Path | None = None
) -> None:
    required = ["message_id", "reply_to", "from_agent", "to_agent", "value_slice_id", "status"]
    missing = [field for field in required if callback.get(field) in (None, "", [], {})]
    if missing:
        raise SystemExit(
            "Callback identity is incomplete; delivery is fail-closed until the lane and dispatch chain are explicit. "
            f"file={path} missing={','.join(missing)}"
        )
    if str(callback.get("message_id")) == str(callback.get("reply_to")):
        raise SystemExit(f"Callback message_id must differ from reply_to: file={path}")
    if registry is not None and ledger_rows is not None and project_root is not None:
        semantic_errors = validate_callback_semantics(callback, registry, ledger_rows, project_root)
        if semantic_errors:
            raise SystemExit(
                "Callback identity does not match the registered dispatch chain; delivery is fail-closed. "
                f"file={path} errors={'; '.join(semantic_errors)}"
            )


def callback_loop_field_warnings(callback: dict[str, Any]) -> list[str]:
    if callback.get("task_type") in {"callback_batch_ready", "callback_spooled", "orchestrator_state"}:
        return []
    if str(callback.get("from_agent") or "") in {"review", "验收泳道"}:
        required = ["value_slice_id", "value_delta", "review_policy", "user_loop_progress", "blocking_concerns", "backlog_concerns", "recommended_next_type"]
    else:
        required = ["value_slice_id", "value_delta", "review_policy", "active_user_loop", "loop_impact", "blocking_concerns", "backlog_concerns", "recommended_next_type"]
    return [
        field
        for field in required
        if field not in callback or callback.get(field) is None or callback.get(field) == ""
    ]


def pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def post_office_running(pid_path: Path) -> bool:
    if not pid_path.exists():
        return False
    try:
        return pid_is_running(int(pid_path.read_text(encoding="utf-8").strip()))
    except ValueError:
        return False


def start_post_office(project_root: Path, poll_interval_seconds: int, orchestrator_thread_id: str) -> int:
    script = project_root / "agent-lanes" / "scripts" / "callback_post_office.py"
    log_dir = project_root / "agent-lanes" / "callback-inbox"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / "post-office.stdout.log"
    stderr_path = log_dir / "post-office.stderr.log"
    command = [
        sys.executable,
        str(script),
        "--project-root",
        str(project_root),
        "--poll-interval-seconds",
        str(poll_interval_seconds),
        "--orchestrator-thread-id",
        orchestrator_thread_id,
    ]
    with stdout_path.open("a", encoding="utf-8") as stdout, stderr_path.open("a", encoding="utf-8") as stderr:
        if os.name == "nt":
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
            proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL, creationflags=flags)
        else:
            proc = subprocess.Popen(command, stdout=stdout, stderr=stderr, stdin=subprocess.DEVNULL, start_new_session=True)
    return int(proc.pid)


def read_callback(path: Path, project_root: Path) -> dict[str, Any]:
    callback = json.loads(path.read_text(encoding="utf-8-sig"))
    callback.setdefault("task_type", "completion_callback")
    callback.setdefault("delivery_mode", "spooled")
    callback.setdefault("created_at", now_text())
    registry = json.loads((project_root / "agent-lanes" / "agent-registry.json").read_text(encoding="utf-8-sig"))
    ledger_rows = value_slice_ledger.read_jsonl(project_root / "agent-lanes" / "value-slice-ledger.jsonl")
    validate_callback_identity(callback, path, registry, ledger_rows, project_root)
    validate_callback_text_quality(callback, path)
    return callback


def self_test(project_root: Path) -> dict[str, Any]:
    valid = {
        "message_id": "msg-self-reply",
        "reply_to": "msg-self-dispatch",
        "from_agent": "开发泳道",
        "to_agent": "主调度泳道",
        "value_slice_id": "VS-SELF-1",
        "status": "DONE",
        "from_thread_id": "thread-development",
    }
    registry = {
        "agents": [
            {"agent_id": "orchestrator", "lane": "orchestrator", "display_name": "主调度泳道"},
            {"agent_id": "development", "lane": "development", "display_name": "开发泳道", "thread_id": "thread-development"},
        ]
    }
    ledger_rows = [
        {
            "event_type": "dispatch_started",
            "interaction_id": "msg-self-dispatch",
            "source_message_id": "msg-self-dispatch",
            "value_slice_id": "VS-SELF-1",
            "target_lane": "development",
            "target_thread_id": "thread-development",
            "control_version": value_slice_ledger.CONTROL_VERSION,
            "dispatch_hash": "dispatch-hash-self",
            "callback_budget": 2,
        }
    ]
    valid["callback_provenance"] = control_provenance.sign_claim(
        project_root,
        "lane_callback",
        {
            "dispatch_id": "msg-self-dispatch",
            "value_slice_id": "VS-SELF-1",
            "target_lane": "development",
            "target_thread_id": "thread-development",
            "dispatch_hash": "dispatch-hash-self",
        },
    )
    valid_error = ""
    try:
        validate_callback_identity(valid, Path("self-test-valid.json"), registry, ledger_rows, project_root)
    except SystemExit as exc:
        valid_error = str(exc)
    invalid = dict(valid)
    invalid.pop("from_agent")
    invalid_error = ""
    try:
        validate_callback_identity(invalid, Path("self-test-invalid.json"), registry, ledger_rows, project_root)
    except SystemExit as exc:
        invalid_error = str(exc)
    spoofed = dict(valid)
    spoofed["from_agent"] = "主调度泳道"
    spoof_error = ""
    try:
        validate_callback_identity(spoofed, Path("self-test-spoof.json"), registry, ledger_rows, project_root)
    except SystemExit as exc:
        spoof_error = str(exc)
    passed = not valid_error and "from_agent" in invalid_error and "target_lane" in spoof_error
    return {"status": "PASS" if passed else "FAIL", "valid_error": valid_error, "invalid_error": invalid_error, "semantic_spoof_error": spoof_error}


def record_callback_acceptance(project_root: Path, callback: dict[str, Any]) -> bool:
    ledger_path = project_root / "agent-lanes" / "value-slice-ledger.jsonl"
    _, appended = value_slice_ledger.append_event(
        ledger_path,
        {
            "schema_version": "agent-lanes.value-slice-ledger.v1",
            "event_id": f"callback-{callback.get('message_id')}",
            "event_type": "callback_accepted",
            "value_slice_id": callback.get("value_slice_id"),
            "interaction_id": callback.get("message_id"),
            "source_message_id": callback.get("message_id"),
            "reply_to": callback.get("reply_to"),
            "actor": "deliver_callback",
            "from_agent": callback.get("from_agent"),
            "to_agent": callback.get("to_agent"),
            "summary": callback.get("summary"),
            "created_at": now_text(),
        },
    )
    return appended


def spool_callback(project_root: Path, callback: dict[str, Any]) -> Path:
    inbox_root = project_root / "agent-lanes" / "callback-inbox"
    log_path = project_root / "agent-lanes" / "transport-log.jsonl"
    target = inbox_root / "pending" / f"{safe_name(str(callback['message_id']))}.json"
    if not target.exists():
        callback["spooled_at"] = now_text()
        write_json(target, callback)

    rows = read_jsonl(log_path)
    spool_id = f"{callback['message_id']}-spooled"
    if not any(row.get("message_id") == spool_id for row in rows):
        append_jsonl(
            log_path,
            {
                "message_id": spool_id,
                "reply_to": callback["message_id"],
                "from_agent": callback.get("from_agent", ""),
                "to_agent": "callback_post_office",
                "task_type": "callback_spooled",
                "status": callback.get("status", ""),
                "summary": "callback 已进入邮局暂存；如果主调度空闲，脚本会返回一条可直接发送的合并原文消息。",
                "spool_path": target.relative_to(project_root).as_posix(),
                "created_at": now_text(),
            },
        )
    return target


def run_post_office_once(project_root: Path, poll_interval_seconds: int, orchestrator_thread_id: str) -> dict[str, Any]:
    script = project_root / "agent-lanes" / "scripts" / "callback_post_office.py"
    command = [
        sys.executable,
        str(script),
        "--project-root",
        str(project_root),
        "--poll-interval-seconds",
        str(poll_interval_seconds),
        "--orchestrator-thread-id",
        orchestrator_thread_id,
        "--once",
    ]
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    proc = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8", env=env)
    output = proc.stdout.strip()
    return json.loads(output) if output else {"status": "no_output"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Deliver a lane callback through the post office.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--callback-file")
    parser.add_argument("--poll-interval-seconds", type=int, default=60)
    parser.add_argument("--max-wait-seconds", type=int, default=0)
    parser.add_argument("--no-start", action="store_true", help="Only spool; do not start the background post office.")
    parser.add_argument(
        "--orchestrator-thread-id",
        default=None,
        help="Defaults to agent-lanes/agent-registry.json orchestrator.thread_id, then AGENT_LANES_ORCHESTRATOR_THREAD_ID, then pending_setup.",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        project_root = Path(args.project_root).resolve()
        result = self_test(project_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if not args.callback_file:
        raise SystemExit("--callback-file is required unless --self-test is used")

    if args.poll_interval_seconds < 1:
        raise SystemExit("--poll-interval-seconds must be >= 1")
    if args.max_wait_seconds < 0:
        raise SystemExit("--max-wait-seconds must be >= 0")

    project_root = Path(args.project_root).resolve()
    orchestrator_thread_id = resolve_orchestrator_thread_id(project_root, args.orchestrator_thread_id)
    callback = read_callback(Path(args.callback_file).resolve(), project_root)
    try:
        callback_ledger_recorded = record_callback_acceptance(project_root, callback)
    except (ValueError, TimeoutError) as exc:
        raise SystemExit(f"Callback budget/ledger acceptance failed closed: {exc}") from exc
    loop_field_warnings = callback_loop_field_warnings(callback)
    spool_path = spool_callback(project_root, callback)

    deadline = time.time() + args.max_wait_seconds
    post_office_result: dict[str, Any] = {"status": "not_checked"}
    while True:
        post_office_result = run_post_office_once(project_root, args.poll_interval_seconds, orchestrator_thread_id)
        if post_office_result.get("status") == "ready_to_send":
            break
        if args.max_wait_seconds == 0 or time.time() >= deadline:
            break
        time.sleep(min(args.poll_interval_seconds, max(1, int(deadline - time.time()))))

    inbox_root = project_root / "agent-lanes" / "callback-inbox"
    pid_path = inbox_root / "post-office.pid"
    started_pid: int | None = None
    running = post_office_running(pid_path)
    if post_office_result.get("status") != "ready_to_send" and not running and not args.no_start:
        started_pid = start_post_office(project_root, args.poll_interval_seconds, orchestrator_thread_id)
        running = True

    batch = post_office_result.get("batch") or {}
    thread_prompt = batch.get("thread_prompt") or batch.get("orchestrator_message")
    result = {
        "status": "ready_to_send" if thread_prompt else "spooled_waiting",
        "message_id": callback["message_id"],
        "spool_path": spool_path.relative_to(project_root).as_posix(),
        "post_office_status": post_office_result.get("status"),
        "post_office_running": running,
        "post_office_started_pid": started_pid,
        "target_thread_id": batch.get("target_thread_id", orchestrator_thread_id),
        "outbox_path": batch.get("outbox_path"),
        "orchestrator_message_path": batch.get("orchestrator_message_path"),
        "delivery_state": "ready_to_send_or_retry" if thread_prompt else "spooled_waiting",
        "send_required": bool(thread_prompt),
        "callback_ledger_recorded": callback_ledger_recorded,
        "thread_prompt": thread_prompt,
        "quality_warnings": {
            "missing_product_loop_fields": loop_field_warnings,
            "recommendation": (
                "Add Value Slice identity/value_delta/review_policy plus Product Loop concern fields before the next lane reply."
                if loop_field_warnings
                else ""
            ),
        },
        "instruction": (
            "Call send_message_to_thread once with target_thread_id and thread_prompt. If the tool returns no active turn to steer or the target thread is unavailable, keep outbox_path as pending retry; do not send a short wake or redo the lane task."
            if thread_prompt
            else "Callback has not reached the orchestrator thread. Do not send a short wake; rerun delivery or record a blocked delivery."
        ),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
