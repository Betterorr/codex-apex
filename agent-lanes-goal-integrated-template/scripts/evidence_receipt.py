#!/usr/bin/env python3
"""Create machine-checkable command or artifact receipts for Value Delta Gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import control_provenance
import value_slice_ledger


def now_text() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_receipt(path: Path, payload: dict[str, Any], project_root: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    receipt_hash = control_provenance.sha256_json(payload)
    payload["receipt_hash"] = receipt_hash
    payload["provenance"] = control_provenance.sign_claim(project_root, "evidence_receipt", {key: value for key, value in payload.items() if key != "provenance"})
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ledger_path = project_root / "agent-lanes" / "value-slice-ledger.jsonl"
    rows = value_slice_ledger.read_jsonl(ledger_path)
    dispatch = value_slice_ledger.find_dispatch_event(rows, str(payload.get("dispatch_id") or ""))
    if not dispatch or dispatch.get("control_version") != value_slice_ledger.CONTROL_VERSION:
        raise ValueError("evidence receipt requires a trusted V2.3 dispatch reservation")
    value_slice_ledger.append_event(
        ledger_path,
        {
            "schema_version": "agent-lanes.value-slice-ledger.v1",
            "control_version": value_slice_ledger.CONTROL_VERSION,
            "event_id": f"evidence-{receipt_hash}",
            "event_type": "evidence_receipt_issued",
            "value_slice_id": dispatch.get("value_slice_id"),
            "interaction_id": receipt_hash,
            "source_message_id": payload.get("dispatch_id"),
            "actor": "evidence_receipt",
            "receipt_hash": receipt_hash,
            "receipt_path": str(path),
            "created_at": payload.get("completed_at"),
        },
    )


def command_receipt(args: argparse.Namespace) -> int:
    command = list(args.command_args)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("command mode requires arguments after --")
    started_at = now_text()
    proc = subprocess.run(command, cwd=Path(args.project_root).resolve(), capture_output=True, check=False)
    completed_at = now_text()
    display = subprocess.list2cmdline(command)
    receipt = {
        "schema_version": "agent-lanes.evidence-receipt.v1",
        "receipt_type": "command",
        "dispatch_id": args.dispatch_id,
        "command": display,
        "cwd": str(Path(args.project_root).resolve()),
        "started_at": started_at,
        "completed_at": completed_at,
        "exit_code": proc.returncode,
        "stdout_sha256": sha256_bytes(proc.stdout),
        "stderr_sha256": sha256_bytes(proc.stderr),
        "stdout_bytes": len(proc.stdout),
        "stderr_bytes": len(proc.stderr),
    }
    write_receipt(Path(args.output).resolve(), receipt, Path(args.project_root).resolve())
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return proc.returncode


def artifact_receipt(args: argparse.Namespace) -> int:
    root = Path(args.project_root).resolve()
    source = (root / args.path).resolve()
    if not source.is_file():
        raise SystemExit(f"artifact is not a file: {source}")
    stat = source.stat()
    try:
        display_path = source.relative_to(root).as_posix()
    except ValueError:
        display_path = str(source)
    receipt = {
        "schema_version": "agent-lanes.evidence-receipt.v1",
        "receipt_type": "artifact",
        "dispatch_id": args.dispatch_id,
        "path": display_path,
        "sha256": sha256_file(source),
        "mtime_ns": stat.st_mtime_ns,
        "size_bytes": stat.st_size,
        "completed_at": now_text(),
    }
    write_receipt(Path(args.output).resolve(), receipt, root)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


def self_test(project_root: Path) -> dict[str, Any]:
    target = project_root / "agent-lanes" / "value-slice.template.json"
    stat = target.stat()
    receipt = {
        "schema_version": "agent-lanes.evidence-receipt.v1",
        "receipt_type": "artifact",
        "dispatch_id": "self-test",
        "path": target.relative_to(project_root).as_posix(),
        "sha256": sha256_file(target),
        "mtime_ns": stat.st_mtime_ns,
        "completed_at": now_text(),
    }
    provenance = control_provenance.sign_claim(project_root, "evidence_receipt", receipt)
    ok = len(receipt["sha256"]) == 64 and receipt["mtime_ns"] > 0 and control_provenance.verify_envelope(project_root, provenance, "evidence_receipt")
    return {"status": "PASS" if ok else "FAIL", "receipt": receipt}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Value Delta evidence receipt.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    subparsers = parser.add_subparsers(dest="mode")

    command_parser = subparsers.add_parser("command")
    command_parser.add_argument("--dispatch-id", required=True)
    command_parser.add_argument("--output", required=True)
    command_parser.add_argument("command_args", nargs=argparse.REMAINDER)

    artifact_parser = subparsers.add_parser("artifact")
    artifact_parser.add_argument("--dispatch-id", required=True)
    artifact_parser.add_argument("--output", required=True)
    artifact_parser.add_argument("--path", required=True)

    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if args.self_test:
        result = self_test(root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if args.mode == "command":
        return command_receipt(args)
    if args.mode == "artifact":
        return artifact_receipt(args)
    raise SystemExit("choose command or artifact mode, or use --self-test")


if __name__ == "__main__":
    raise SystemExit(main())
