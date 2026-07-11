#!/usr/bin/env python3
"""Maintain the authoritative Value Slice interaction ledger."""

from __future__ import annotations

import argparse
import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from control_provenance import sha256_json


BUDGET_EVENT_TYPES = {"dispatch_started", "direct_execution_completed"}
CALLBACK_EVENT_TYPE = "callback_accepted"
LOCK_TIMEOUT_SECONDS = 10.0
CONTROL_VERSION = "2.3"
TERMINAL_EVENT_TYPES = {"value_delta_verified", "direct_execution_completed", "dispatch_cancelled"}
DISPATCH_CONTRACT_FIELDS = {
    "control_version",
    "dispatch_hash",
    "value_slice_id",
    "interaction_id",
    "source_message_id",
    "actor",
    "target_lane",
    "target_thread_id",
    "dispatch_mode",
    "callback_budget",
    "auto_iteration_id",
    "authorization_request_hash",
    "authorization_registry_hash",
    "authorization_result_hash",
}


def now_text() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


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
            raise ValueError(f"invalid ledger JSON at line {line_no}: {exc}") from exc
    return rows


def budget_usage(rows: list[dict[str, Any]], value_slice_id: str) -> int:
    interaction_ids: set[str] = set()
    for index, row in enumerate(rows):
        if row.get("value_slice_id") != value_slice_id or row.get("event_type") not in BUDGET_EVENT_TYPES:
            continue
        interaction_ids.add(str(row.get("interaction_id") or row.get("source_message_id") or f"row-{index}"))
    return len(interaction_ids)


def callback_usage(rows: list[dict[str, Any]], value_slice_id: str) -> int:
    return len(
        {
            str(row.get("interaction_id") or row.get("source_message_id"))
            for row in rows
            if row.get("value_slice_id") == value_slice_id
            and row.get("event_type") == CALLBACK_EVENT_TYPE
            and (row.get("interaction_id") or row.get("source_message_id"))
        }
    )


def dispatch_reservation_usage(rows: list[dict[str, Any]], value_slice_id: str) -> int:
    return len(
        {
            str(row.get("interaction_id") or row.get("source_message_id"))
            for row in rows
            if row.get("value_slice_id") == value_slice_id
            and row.get("event_type") == "dispatch_started"
            and (row.get("interaction_id") or row.get("source_message_id"))
        }
    )


def find_dispatch_event(rows: list[dict[str, Any]], dispatch_id: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("event_type") != "dispatch_started":
            continue
        ids = {str(row.get("interaction_id") or ""), str(row.get("source_message_id") or "")}
        if dispatch_id in ids:
            return row
    return None


def dispatch_is_terminal(rows: list[dict[str, Any]], dispatch_id: str) -> bool:
    return any(
        row.get("event_type") in TERMINAL_EVENT_TYPES
        and dispatch_id in {str(row.get("interaction_id") or ""), str(row.get("source_message_id") or "")}
        for row in rows
    )


def active_control_dispatches(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row.get("event_type") == "dispatch_started"
        and row.get("control_version") == CONTROL_VERSION
        and not dispatch_is_terminal(rows, str(row.get("interaction_id") or row.get("source_message_id") or ""))
    ]


def dispatch_contract_diff(existing: dict[str, Any], candidate: dict[str, Any]) -> list[str]:
    return sorted(field for field in DISPATCH_CONTRACT_FIELDS if existing.get(field) != candidate.get(field))


def write_current_state(path: Path, state: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8-sig")
    os.replace(temporary, path)


@contextmanager
def ledger_lock(path: Path, timeout_seconds: float = LOCK_TIMEOUT_SECONDS):
    """Serialize cross-process read/check/append cycles with a sidecar lock."""
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+b")
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    deadline = time.monotonic() + timeout_seconds
    acquired = False
    try:
        while not acquired:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt

                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except (OSError, BlockingIOError):
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out acquiring ledger lock: {lock_path}")
                time.sleep(0.05)
        yield
    finally:
        if acquired:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def append_event(path: Path, event: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    with ledger_lock(path):
        rows = read_jsonl(path)
        identity = (
            event.get("value_slice_id"),
            event.get("event_type"),
            event.get("interaction_id") or event.get("source_message_id"),
        )
        for row in rows:
            row_identity = (
                row.get("value_slice_id"),
                row.get("event_type"),
                row.get("interaction_id") or row.get("source_message_id"),
            )
            if identity == row_identity:
                if event.get("event_type") == "dispatch_started":
                    changed = dispatch_contract_diff(row, event)
                    if changed:
                        raise ValueError(f"dispatch identity was reused with a different contract: {changed}")
                return row, False

        slice_id = str(event.get("value_slice_id") or "")
        event_type = str(event.get("event_type") or "")
        if event_type == "dispatch_started":
            callback_budget = int(event.get("callback_budget") or 0)
            if callback_budget < 1:
                raise ValueError("dispatch_started requires callback_budget >= 1")
            used = dispatch_reservation_usage(rows, slice_id)
            if used >= callback_budget:
                raise ValueError(f"callback dispatch reservation budget exhausted: {used}/{callback_budget}")
        elif event_type == CALLBACK_EVENT_TYPE:
            reply_to = str(event.get("reply_to") or "")
            dispatch = find_dispatch_event(rows, reply_to)
            if not dispatch:
                raise ValueError(f"callback_accepted requires a recorded dispatch_started: {reply_to}")
            if str(dispatch.get("value_slice_id") or "") != slice_id:
                raise ValueError("callback_accepted value_slice_id does not match recorded dispatch")
            if any(
                row.get("event_type") == CALLBACK_EVENT_TYPE and str(row.get("reply_to") or "") == reply_to
                for row in rows
            ):
                raise ValueError(f"recorded dispatch already has an accepted callback: {reply_to}")
            callback_budget = int(dispatch.get("callback_budget") or 0)
            used = callback_usage(rows, slice_id)
            if callback_budget < 1 or used >= callback_budget:
                raise ValueError(f"callback acceptance budget exhausted: {used}/{callback_budget}")

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return event, True


def reserve_dispatch(path: Path, event: dict[str, Any], current_state_path: Path) -> tuple[dict[str, Any], bool]:
    """Atomically reserve one global active dispatch and auto-iteration slot."""
    if event.get("control_version") != CONTROL_VERSION or not event.get("dispatch_hash"):
        raise ValueError("trusted dispatch reservation requires V2.3 control_version and dispatch_hash")
    with ledger_lock(path):
        rows = read_jsonl(path)
        identity = (
            event.get("value_slice_id"),
            event.get("event_type"),
            event.get("interaction_id") or event.get("source_message_id"),
        )
        for row in rows:
            row_identity = (
                row.get("value_slice_id"),
                row.get("event_type"),
                row.get("interaction_id") or row.get("source_message_id"),
            )
            if identity == row_identity:
                changed = dispatch_contract_diff(row, event)
                if changed:
                    raise ValueError(f"dispatch identity was reused with a different contract: {changed}")
                return row, False

        active = active_control_dispatches(rows)
        if active:
            raise ValueError(f"global active dispatch reservation already exists: {active[0].get('interaction_id')}")

        callback_budget = int(event.get("callback_budget") or 0)
        slice_id = str(event.get("value_slice_id") or "")
        if callback_budget < 1 or dispatch_reservation_usage(rows, slice_id) >= callback_budget:
            raise ValueError("callback dispatch reservation budget exhausted")

        state = json.loads(current_state_path.read_text(encoding="utf-8-sig")) if current_state_path.exists() else {}
        if event.get("dispatch_mode") == "auto":
            policy = state.get("automation_policy") or {}
            iteration_id = str(event.get("auto_iteration_id") or "")
            if not iteration_id or iteration_id != str(policy.get("auto_iteration_id") or ""):
                raise ValueError("auto iteration id does not match current-state inside reservation lock")
            active_auto_reservations = sum(
                1
                for row in active_control_dispatches(rows)
                if row.get("dispatch_mode") == "auto" and str(row.get("auto_iteration_id") or "") == iteration_id
            )
            completed = int(policy.get("consecutive_auto_slices") or 0)
            maximum = int(policy.get("max_consecutive_auto_slices") or 0)
            if maximum < 1 or completed + active_auto_reservations >= maximum:
                raise ValueError(f"automatic slice checkpoint required inside reservation lock: {completed}+{active_auto_reservations}/{maximum}")

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        state["active_value_slice"] = {
            "value_slice_id": event.get("value_slice_id"),
            "dispatch_message_id": event.get("interaction_id"),
            "target_lane": event.get("target_lane"),
            "status": "DISPATCHED",
            "started_at": event.get("created_at"),
            "dispatch_hash": event.get("dispatch_hash"),
            "control_version": CONTROL_VERSION,
        }
        state["updated_at"] = now_text()
        if current_state_path.exists():
            write_current_state(current_state_path, state)
        return event, True


def record_terminal_event(path: Path, event: dict[str, Any], current_state_path: Path) -> tuple[dict[str, Any], bool]:
    if event.get("event_type") not in TERMINAL_EVENT_TYPES:
        raise ValueError("record_terminal_event requires a terminal event type")
    with ledger_lock(path):
        rows = read_jsonl(path)
        identity = (
            event.get("value_slice_id"),
            event.get("event_type"),
            event.get("interaction_id") or event.get("source_message_id"),
        )
        for row in rows:
            row_identity = (
                row.get("value_slice_id"),
                row.get("event_type"),
                row.get("interaction_id") or row.get("source_message_id"),
            )
            if identity == row_identity:
                return row, False
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        if current_state_path.exists():
            state = json.loads(current_state_path.read_text(encoding="utf-8-sig"))
            active = state.get("active_value_slice") or {}
            if str(active.get("dispatch_message_id") or "") == str(event.get("interaction_id") or event.get("source_message_id") or ""):
                state["active_value_slice"] = None
                state["updated_at"] = now_text()
                write_current_state(current_state_path, state)
        return event, True


def self_test() -> dict[str, Any]:
    rows = [
        {"value_slice_id": "VS-1", "event_type": "dispatch_started", "interaction_id": "msg-1"},
        {"value_slice_id": "VS-1", "event_type": "value_delta_verified", "interaction_id": "msg-1"},
        {"value_slice_id": "VS-1", "event_type": "direct_execution_completed", "interaction_id": "direct-1"},
    ]
    usage = budget_usage(rows, "VS-1")
    callbacks = callback_usage(rows, "VS-1")
    return {"status": "PASS" if usage == 2 and callbacks == 0 else "FAIL", "budget_usage": usage, "callback_usage": callbacks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read or append the Value Slice ledger.")
    parser.add_argument("--ledger", default="agent-lanes/value-slice-ledger.jsonl")
    parser.add_argument("--action", choices=["usage", "record"])
    parser.add_argument("--slice-id")
    parser.add_argument("--event-type", choices=sorted(BUDGET_EVENT_TYPES | {"callback_accepted", "value_delta_verified", "checkpoint"}))
    parser.add_argument("--interaction-id")
    parser.add_argument("--source-message-id")
    parser.add_argument("--actor", default="orchestrator")
    parser.add_argument("--summary", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if not args.action or not args.slice_id:
        raise SystemExit("--action and --slice-id are required")

    ledger = Path(args.ledger).resolve()
    if args.action == "usage":
        rows = read_jsonl(ledger)
        print(json.dumps({"status": "PASS", "value_slice_id": args.slice_id, "budget_usage": budget_usage(rows, args.slice_id)}, ensure_ascii=False, indent=2))
        return 0
    if not args.event_type or not (args.interaction_id or args.source_message_id):
        raise SystemExit("record requires --event-type and --interaction-id or --source-message-id")

    event = {
        "schema_version": "agent-lanes.value-slice-ledger.v1",
        "event_id": f"ledger-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "event_type": args.event_type,
        "value_slice_id": args.slice_id,
        "interaction_id": args.interaction_id or args.source_message_id,
        "source_message_id": args.source_message_id,
        "actor": args.actor,
        "summary": args.summary,
        "created_at": now_text(),
    }
    stored, appended = append_event(ledger, event)
    print(json.dumps({"status": "PASS", "appended": appended, "event": stored}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
