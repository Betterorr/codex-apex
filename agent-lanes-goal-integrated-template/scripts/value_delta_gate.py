#!/usr/bin/env python3
"""Fail closed unless a completed Value Slice proves a fresh value delta."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import control_provenance
from value_slice_ledger import CONTROL_VERSION, find_dispatch_event, now_text, read_jsonl, record_terminal_event


ALLOWED_DELTAS = {"new_user_action", "blocker_removed", "quality_confidence", "risk_reduction"}
PASS_STATUSES = {"PASS", "VERIFIED", "PRESENT"}
FUTURE_SKEW = timedelta(seconds=60)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def present(value: Any) -> bool:
    return value not in (None, "", [], {})


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not present(value):
        return None
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} must be a valid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label} must include a timezone offset")
        return None
    return parsed


def dispatch_message_ids(dispatch: dict[str, Any]) -> set[str]:
    return {
        str(value)
        for value in (dispatch.get("message_id"), dispatch.get("outbound_message_id"))
        if present(value)
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_completion(
    payload: dict[str, Any],
    root: Path,
    dispatch: dict[str, Any] | None = None,
    dispatch_event: dict[str, Any] | None = None,
    ledger_rows: list[dict[str, Any]] | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if payload.get("schema_version") != "agent-lanes.value-slice-completion.v1":
        errors.append("unsupported or missing completion schema_version")
    for field in ["value_slice_id", "source_message_id", "status", "expected_value_delta", "actual_value_delta", "acceptance_results", "evidence", "completed_at"]:
        if not present(payload.get(field)):
            errors.append(f"missing completion.{field}")
    if payload.get("status") not in {"DONE", "DONE_WITH_CONCERNS"}:
        errors.append("completion status must be DONE or DONE_WITH_CONCERNS")

    now = datetime.now(timezone.utc)
    completed_at = parse_timestamp(payload.get("completed_at"), "completion.completed_at", errors)
    if completed_at and completed_at.astimezone(timezone.utc) > now + FUTURE_SKEW:
        errors.append("completion.completed_at cannot be in the future")

    actual = payload.get("actual_value_delta")
    if not isinstance(actual, dict):
        errors.append("actual_value_delta must be an object")
        actual = {}
    for field in ["type", "summary", "before", "after"]:
        if not present(actual.get(field)):
            errors.append(f"missing actual_value_delta.{field}")
    if actual.get("type") not in ALLOWED_DELTAS:
        errors.append("actual_value_delta.type is invalid")
    if payload.get("expected_value_delta") != actual.get("type"):
        errors.append("actual value delta type does not match expected_value_delta")
    if actual.get("before") == actual.get("after") and present(actual.get("before")):
        errors.append("before and after states are identical")

    criteria = payload.get("acceptance_results")
    if not isinstance(criteria, list) or len(criteria) < 2:
        errors.append("at least two acceptance_results are required")
        criteria = []
    acceptance_evidence_ids: set[str] = set()
    for index, item in enumerate(criteria):
        if not isinstance(item, dict) or not present(item.get("criterion")):
            errors.append(f"acceptance_results[{index}] is missing criterion")
            continue
        if str(item.get("status") or "").upper() != "PASS":
            errors.append(f"acceptance_results[{index}] did not PASS")
        if not present(item.get("evidence")):
            errors.append(f"acceptance_results[{index}] is missing evidence")
        elif isinstance(item.get("evidence"), list):
            acceptance_evidence_ids.update(str(value) for value in item.get("evidence") if present(value))
        else:
            errors.append(f"acceptance_results[{index}].evidence must be a list of evidence_id values")

    if payload.get("blocking_concerns"):
        errors.append("blocking_concerns must be empty before Value Delta Gate can pass")

    evidence = payload.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("at least one evidence item is required")
        evidence = []
    dispatch_created_at = parse_timestamp(
        (dispatch_event or {}).get("created_at"), "ledger.dispatch_started.created_at", errors
    )
    evidence_ids: set[str] = set()
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            errors.append(f"evidence[{index}] must be an object")
            continue
        if str(item.get("status") or "").upper() not in PASS_STATUSES:
            errors.append(f"evidence[{index}] is not verified")
        evidence_id = str(item.get("evidence_id") or "")
        if not evidence_id:
            errors.append(f"evidence[{index}] is missing evidence_id")
        elif evidence_id in evidence_ids:
            errors.append(f"duplicate evidence_id: {evidence_id}")
        evidence_ids.add(evidence_id)
        if not present(item.get("fresh_at")):
            errors.append(f"evidence[{index}] is missing fresh_at")
        fresh_at = parse_timestamp(item.get("fresh_at"), f"evidence[{index}].fresh_at", errors)
        if fresh_at and fresh_at.astimezone(timezone.utc) > now + FUTURE_SKEW:
            errors.append(f"evidence[{index}].fresh_at cannot be in the future")
        if fresh_at and completed_at and fresh_at > completed_at + FUTURE_SKEW:
            errors.append(f"evidence[{index}].fresh_at cannot be later than completion.completed_at")
        if fresh_at and dispatch_created_at and fresh_at + FUTURE_SKEW < dispatch_created_at:
            errors.append(f"evidence[{index}].fresh_at predates the recorded dispatch")
        evidence_path = item.get("path")
        if evidence_path and not (root / str(evidence_path)).exists():
            errors.append(f"evidence path does not exist: {evidence_path}")
        if not evidence_path and not present(item.get("command")):
            errors.append(f"evidence[{index}] requires path or command")

        receipt_path_value = item.get("receipt_path")
        if not present(receipt_path_value):
            errors.append(f"evidence[{index}] requires receipt_path")
            continue
        receipt_path = root / str(receipt_path_value)
        if not receipt_path.exists():
            errors.append(f"evidence receipt does not exist: {receipt_path_value}")
            continue
        try:
            receipt = read_json(receipt_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"evidence receipt is invalid: {receipt_path_value}: {exc}")
            continue
        if receipt.get("schema_version") != "agent-lanes.evidence-receipt.v1":
            errors.append(f"evidence[{index}] receipt schema is invalid")
        provenance = receipt.get("provenance")
        unsigned_receipt = {key: value for key, value in receipt.items() if key != "provenance"}
        if not isinstance(provenance, dict) or not control_provenance.verify_envelope(root, provenance, "evidence_receipt"):
            errors.append(f"evidence[{index}] receipt provenance signature is invalid")
        elif provenance.get("claim") != unsigned_receipt:
            errors.append(f"evidence[{index}] receipt provenance claim does not match receipt")
        receipt_hash = str(receipt.get("receipt_hash") or "")
        hash_payload = {key: value for key, value in receipt.items() if key not in {"receipt_hash", "provenance"}}
        if receipt_hash != control_provenance.sha256_json(hash_payload):
            errors.append(f"evidence[{index}] receipt_hash is invalid")
        if not any(
            row.get("event_type") == "evidence_receipt_issued"
            and row.get("actor") == "evidence_receipt"
            and row.get("receipt_hash") == receipt_hash
            and str(row.get("source_message_id") or "") in dispatch_message_ids(dispatch or {})
            for row in (ledger_rows or [])
        ):
            errors.append(f"evidence[{index}] receipt is not recorded by the trusted evidence runner")
        if str(receipt.get("dispatch_id") or "") not in dispatch_message_ids(dispatch or {}):
            errors.append(f"evidence[{index}] receipt dispatch_id does not match dispatch")
        receipt_at = parse_timestamp(receipt.get("completed_at"), f"evidence[{index}].receipt.completed_at", errors)
        if receipt_at and dispatch_created_at and receipt_at + FUTURE_SKEW < dispatch_created_at:
            errors.append(f"evidence[{index}] receipt predates the recorded dispatch")
        if fresh_at and receipt_at and abs((fresh_at - receipt_at).total_seconds()) > FUTURE_SKEW.total_seconds():
            errors.append(f"evidence[{index}].fresh_at does not match receipt completion time")
        receipt_type = str(receipt.get("receipt_type") or "")
        if present(item.get("command")):
            if receipt_type != "command" or receipt.get("command") != item.get("command"):
                errors.append(f"evidence[{index}] command does not match receipt")
            if receipt.get("exit_code") != 0 or not present(receipt.get("stdout_sha256")):
                errors.append(f"evidence[{index}] command receipt is not a successful captured execution")
        elif evidence_path:
            resolved_evidence_path = (root / str(evidence_path)).resolve()
            if receipt_type != "artifact" or str(receipt.get("path") or "") != str(evidence_path):
                errors.append(f"evidence[{index}] artifact does not match receipt")
            if resolved_evidence_path.exists():
                stat = resolved_evidence_path.stat()
                if receipt.get("sha256") != sha256_file(resolved_evidence_path):
                    errors.append(f"evidence[{index}] artifact sha256 does not match receipt")
                if int(receipt.get("mtime_ns") or -1) != stat.st_mtime_ns:
                    errors.append(f"evidence[{index}] artifact mtime does not match receipt")

    unknown_acceptance_evidence = sorted(acceptance_evidence_ids - evidence_ids)
    if unknown_acceptance_evidence:
        errors.append(f"acceptance_results reference unknown evidence_id values: {unknown_acceptance_evidence}")

    if dispatch:
        value_slice = dispatch.get("value_slice") or {}
        if value_slice.get("value_slice_id") != payload.get("value_slice_id"):
            errors.append("completion value_slice_id does not match dispatch")
        if value_slice.get("expected_value_delta") != payload.get("expected_value_delta"):
            errors.append("completion expected_value_delta does not match dispatch")
        expected_source_ids = dispatch_message_ids(dispatch)
        if expected_source_ids and str(payload.get("source_message_id") or "") not in expected_source_ids:
            errors.append("completion source_message_id does not match dispatch message_id/outbound_message_id")
        dispatched_criteria = value_slice.get("acceptance_criteria") or []
        completed_criteria = [item.get("criterion") for item in criteria if isinstance(item, dict)]
        missing = [criterion for criterion in dispatched_criteria if criterion not in completed_criteria]
        if missing:
            errors.append(f"completion omitted dispatched acceptance criteria: {missing}")
    else:
        errors.append("dispatch file is required for completion validation")
    if not dispatch_event:
        errors.append("ledger does not contain the corresponding dispatch_started event")
    elif dispatch:
        value_slice = dispatch.get("value_slice") or {}
        required_dispatch_metadata = {
            "control_version": CONTROL_VERSION,
            "actor": "product_value_gate",
            "target_lane": dispatch.get("to_agent") or dispatch.get("target_lane"),
            "dispatch_mode": dispatch.get("dispatch_mode"),
            "callback_budget": int(value_slice.get("callback_budget") or 0),
            "dispatch_hash": control_provenance.sha256_json(dispatch),
        }
        mismatched = [key for key, expected in required_dispatch_metadata.items() if dispatch_event.get(key) != expected]
        if mismatched:
            errors.append(f"recorded dispatch metadata/hash is not trusted V2.3: {mismatched}")
    return errors, warnings


def self_test(root: Path) -> dict[str, Any]:
    artifact_handle = tempfile.NamedTemporaryFile(mode="wb", delete=False, dir=root, prefix="value-delta-self-test-", suffix=".txt")
    artifact_path = Path(artifact_handle.name)
    artifact_handle.write(b"fresh evidence")
    artifact_handle.close()
    receipt_path = artifact_path.with_suffix(".receipt.json")
    dispatch_time = now_text()
    receipt = {
        "schema_version": "agent-lanes.evidence-receipt.v1",
        "receipt_type": "artifact",
        "dispatch_id": "msg-self-1",
        "path": str(artifact_path),
        "sha256": sha256_file(artifact_path),
        "mtime_ns": artifact_path.stat().st_mtime_ns,
        "completed_at": dispatch_time,
    }
    dispatch = {
        "message_id": "msg-self-1",
        "dispatch_mode": "manual",
        "to_agent": "development",
        "value_slice": {
            "value_slice_id": "VS-SELF-1",
            "expected_value_delta": "risk_reduction",
            "acceptance_criteria": ["账本可解析", "门禁可执行"],
            "callback_budget": 2,
        },
    }
    receipt["receipt_hash"] = control_provenance.sha256_json(receipt)
    receipt["provenance"] = control_provenance.sign_claim(root, "evidence_receipt", {key: value for key, value in receipt.items() if key != "provenance"})
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
    dispatch_event = {
        "control_version": CONTROL_VERSION,
        "event_type": "dispatch_started",
        "value_slice_id": "VS-SELF-1",
        "interaction_id": "msg-self-1",
        "actor": "product_value_gate",
        "target_lane": "development",
        "dispatch_mode": "manual",
        "callback_budget": 2,
        "dispatch_hash": control_provenance.sha256_json(dispatch),
        "created_at": dispatch_time,
    }
    receipt_event = {
        "control_version": CONTROL_VERSION,
        "event_type": "evidence_receipt_issued",
        "value_slice_id": "VS-SELF-1",
        "interaction_id": receipt["receipt_hash"],
        "source_message_id": "msg-self-1",
        "actor": "evidence_receipt",
        "receipt_hash": receipt["receipt_hash"],
    }
    ledger_rows = [dispatch_event, receipt_event]
    payload = {
        "schema_version": "agent-lanes.value-slice-completion.v1",
        "value_slice_id": "VS-SELF-1",
        "source_message_id": "msg-self-1",
        "status": "DONE",
        "expected_value_delta": "risk_reduction",
        "actual_value_delta": {"type": "risk_reduction", "summary": "风险减少", "before": "无门禁", "after": "有门禁"},
        "acceptance_results": [
            {"criterion": "账本可解析", "status": "PASS", "evidence": ["ev-artifact"]},
            {"criterion": "门禁可执行", "status": "PASS", "evidence": ["ev-artifact"]},
        ],
        "evidence": [{"evidence_id": "ev-artifact", "type": "artifact", "path": str(artifact_path), "receipt_path": str(receipt_path), "status": "verified", "fresh_at": dispatch_time}],
        "blocking_concerns": [],
        "backlog_concerns": [],
        "completed_at": dispatch_time,
    }
    try:
        errors, warnings = validate_completion(payload, root, dispatch, dispatch_event, ledger_rows)
        future_payload = json.loads(json.dumps(payload))
        future_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
        future_payload["completed_at"] = future_time
        future_payload["evidence"][0]["fresh_at"] = future_time
        future_errors, _ = validate_completion(future_payload, root, dispatch, dispatch_event, ledger_rows)
        missing_dispatch_errors, _ = validate_completion(payload, root, None, None)
        stale_payload = json.loads(json.dumps(payload))
        stale_payload["evidence"][0]["fresh_at"] = "2000-01-01T00:00:00+00:00"
        stale_errors, _ = validate_completion(stale_payload, root, dispatch, dispatch_event, ledger_rows)
        passed = (
            not errors
            and any("cannot be in the future" in item for item in future_errors)
            and any("dispatch file is required" in item for item in missing_dispatch_errors)
            and any("predates the recorded dispatch" in item for item in stale_errors)
        )
        return {
            "status": "PASS" if passed else "FAIL",
            "errors": errors,
            "warnings": warnings,
            "future_timestamp_errors": future_errors,
            "missing_dispatch_errors": missing_dispatch_errors,
            "stale_evidence_errors": stale_errors,
        }
    finally:
        if receipt_path.exists():
            receipt_path.unlink()
        if artifact_path.exists():
            artifact_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a completed Value Slice value delta.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--completion-file")
    parser.add_argument("--dispatch-file")
    parser.add_argument("--ledger", default="agent-lanes/value-slice-ledger.jsonl")
    parser.add_argument("--record", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if args.self_test:
        result = self_test(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if not args.completion_file:
        raise SystemExit("--completion-file is required unless --self-test is used")

    completion_path = Path(args.completion_file).resolve()
    payload = read_json(completion_path)
    dispatch = read_json(Path(args.dispatch_file).resolve()) if args.dispatch_file else None
    ledger_path = (root / args.ledger).resolve()
    ledger_rows = read_jsonl(ledger_path)
    dispatch_ids = dispatch_message_ids(dispatch or {})
    dispatch_event = next((find_dispatch_event(ledger_rows, item) for item in dispatch_ids if find_dispatch_event(ledger_rows, item)), None)
    errors, warnings = validate_completion(payload, root, dispatch, dispatch_event, ledger_rows)
    recorded = False
    if not errors and args.record:
        source_id = str(payload.get("source_message_id"))
        _, recorded = record_terminal_event(
            ledger_path,
            {
                "schema_version": "agent-lanes.value-slice-ledger.v1",
                "control_version": CONTROL_VERSION,
                "event_id": f"value-delta-{payload.get('value_slice_id')}-{source_id}",
                "event_type": "value_delta_verified",
                "value_slice_id": payload.get("value_slice_id"),
                "interaction_id": source_id,
                "source_message_id": source_id,
                "actor": "value_delta_gate",
                "summary": (payload.get("actual_value_delta") or {}).get("summary"),
                "created_at": now_text(),
            },
            root / "agent-lanes" / "current-state.json",
        )
    result = {
        "status": "PASS" if not errors else "FAIL",
        "completion_file": str(completion_path),
        "value_slice_id": payload.get("value_slice_id"),
        "recorded": recorded,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
