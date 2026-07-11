#!/usr/bin/env python3
"""Resolve one exact capability/variant authorization request fail-closed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def capability_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("capabilities", "items"):
        rows = registry.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def approval_allowed(status: str) -> bool:
    text = status.lower()
    if any(token in text for token in ("pending", "blocked", "denied", "expired", "superseded", "consumed")):
        return False
    return text.startswith("approved") or "authorized" in text or text.startswith("not_required")


def remaining_calls(budget: dict[str, Any]) -> int:
    if "remaining_live_call_limit" in budget:
        return int(budget.get("remaining_live_call_limit") or 0)
    return max(0, int(budget.get("live_call_limit") or 0) - int(budget.get("call_count") or 0))


def resolve(registry: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    capability_id = str(request.get("capability_id") or "")
    variant_id = str(request.get("variant_id") or "")
    requested_calls = int(request.get("requested_live_calls") or 0)
    external_effects = request.get("requested_external_effects") or []
    scope_reference = str(request.get("authorization_scope_reference") or "")
    matches = [row for row in capability_rows(registry) if str(row.get("id") or "") == capability_id]
    if len(matches) != 1:
        return {"status": "NEEDS_CONTEXT", "authorized": False, "reason": f"exact capability id resolved to {len(matches)} rows", "capability_id": capability_id}
    capability = matches[0]
    approval = capability.get("approval") or {}
    approval_status = str(approval.get("status") or "")
    source = "capability"
    if variant_id:
        variants = [row for row in (capability.get("variants") or []) if isinstance(row, dict) and str(row.get("id") or "") == variant_id]
        if len(variants) != 1:
            return {"status": "NEEDS_CONTEXT", "authorized": False, "reason": f"exact variant id resolved to {len(variants)} rows", "capability_id": capability_id, "variant_id": variant_id}
        approval_status = str(variants[0].get("approval_status") or "")
        source = "variant"

    errors: list[str] = []
    if not approval_allowed(approval_status):
        errors.append(f"{source} approval is not active: {approval_status or 'missing'}")
    remaining = remaining_calls(capability.get("budget") or {})
    if requested_calls > remaining:
        errors.append(f"requested live calls exceed remaining budget: {requested_calls}/{remaining}")
    if (requested_calls > 0 or external_effects) and not scope_reference:
        errors.append("external effects require authorization_scope_reference")
    if request.get("requires_secret") and not request.get("secret_not_persisted"):
        errors.append("secret use requires secret_not_persisted=true")
    return {
        "status": "AUTHORIZED" if not errors else "DENIED",
        "authorized": not errors,
        "capability_id": capability_id,
        "variant_id": variant_id or None,
        "approval_source": source,
        "approval_status": approval_status,
        "requested_live_calls": requested_calls,
        "remaining_live_calls": remaining,
        "requested_external_effects": external_effects,
        "authorization_scope_reference": scope_reference or None,
        "errors": errors,
    }


def self_test() -> dict[str, Any]:
    registry = {"capabilities": [{"id": "cap-1", "approval": {"status": "approved_standing"}, "budget": {"live_call_limit": 2, "call_count": 1}, "variants": [{"id": "blocked", "approval_status": "pending_user_confirmation"}]}]}
    allowed = resolve(registry, {"capability_id": "cap-1", "requested_live_calls": 1, "authorization_scope_reference": "user-msg-1"})
    blocked = resolve(registry, {"capability_id": "cap-1", "variant_id": "blocked"})
    return {"status": "PASS" if allowed["authorized"] and not blocked["authorized"] else "FAIL", "allowed": allowed, "blocked": blocked}


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve exact capability authorization and budget.")
    parser.add_argument("--registry", default="docs/capability-status.json")
    parser.add_argument("--request-file")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if not args.request_file:
        raise SystemExit("--request-file is required unless --self-test is used")
    result = resolve(read_json(Path(args.registry).resolve()), read_json(Path(args.request_file).resolve()))
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["authorized"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
