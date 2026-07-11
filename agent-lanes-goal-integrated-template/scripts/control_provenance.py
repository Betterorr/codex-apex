#!/usr/bin/env python3
"""Local control-plane provenance signing for cooperative Agent Lanes automation.

This is a workflow trust boundary, not hostile same-user process isolation.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "agent-lanes.control-provenance.v1"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def key_path(project_root: Path) -> Path:
    return project_root / ".codex" / "runtime" / "agent-lanes-control.key"


def initialize_key(project_root: Path) -> Path:
    path = key_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(os.urandom(32))
    if len(path.read_bytes()) < 32:
        raise ValueError(f"control provenance key is invalid: {path}")
    return path


def load_key(project_root: Path) -> bytes:
    path = key_path(project_root)
    if not path.exists():
        raise ValueError("control provenance key is not initialized")
    key = path.read_bytes()
    if len(key) < 32:
        raise ValueError("control provenance key is invalid")
    return key


def sign_claim(project_root: Path, claim_type: str, claim: dict[str, Any]) -> dict[str, Any]:
    envelope = {"schema_version": SCHEMA_VERSION, "claim_type": claim_type, "claim": claim}
    envelope["signature"] = hmac.new(load_key(project_root), canonical_json(envelope), hashlib.sha256).hexdigest()
    return envelope


def verify_envelope(project_root: Path, envelope: dict[str, Any], claim_type: str) -> bool:
    if envelope.get("schema_version") != SCHEMA_VERSION or envelope.get("claim_type") != claim_type:
        return False
    signature = str(envelope.get("signature") or "")
    unsigned = {key: value for key, value in envelope.items() if key != "signature"}
    expected = hmac.new(load_key(project_root), canonical_json(unsigned), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize or self-test local Agent Lanes provenance.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if args.init:
        path = initialize_key(root)
        print(json.dumps({"status": "PASS", "key_path": str(path), "key_persisted_outside_project_docs": True}, ensure_ascii=False, indent=2))
        return 0
    if args.self_test:
        initialize_key(root)
        envelope = sign_claim(root, "self_test", {"value": 1})
        tampered = json.loads(json.dumps(envelope))
        tampered["claim"]["value"] = 2
        result = {"status": "PASS" if verify_envelope(root, envelope, "self_test") and not verify_envelope(root, tampered, "self_test") else "FAIL"}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    raise SystemExit("use --init or --self-test")


if __name__ == "__main__":
    raise SystemExit(main())
