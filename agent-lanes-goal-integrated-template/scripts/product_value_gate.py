#!/usr/bin/env python3
"""Fail closed when a lane dispatch does not create a defensible value slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import resolve_authorization
from control_provenance import sha256_json, sign_claim
from value_slice_ledger import CONTROL_VERSION, dispatch_reservation_usage, now_text, reserve_dispatch


WRAPPER_TERMS = {
    "consumer",
    "handoff",
    "checkpoint",
    "readiness",
    "review_surface",
    "review-surface",
    "evidence_only",
    "evidence-only",
    "status_panel",
    "summary_wrapper",
    "browser_smoke_only",
    "screenshot_only",
}
ALLOWED_VALUE_DELTAS = {"new_user_action", "blocker_removed", "quality_confidence", "risk_reduction"}
ALLOWED_REVIEW_POLICIES = {"bundle_boundary", "stage_boundary", "high_risk", "user_requested", "blocking_concern"}
REVIEW_LANES = {"review", "验收泳道"}
VALID_STAGE_PRIORITIES = {"P1", "P2", "P3", "P4", "P5"}
VALID_MAINLINE_IMPACTS = {"direct_advance", "blocks_mainline", "quality_confidence", "risk_boundary"}
VALID_DISPATCH_MODES = {"manual", "auto"}
IMMUTABLE_CONTRACT_FORBIDDEN_FIELDS = {"product_value_gate", "dispatch_hash", "callback_provenance"}
GARBLED_MARKERS = ("???", "\ufffd", "锟斤拷", "Ã", "â€")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def text_blob(payload: dict[str, Any]) -> str:
    fields = [
        payload.get("message_id"),
        payload.get("task_type"),
        payload.get("summary"),
        payload.get("related_goal"),
        (payload.get("value_slice") or {}).get("title"),
        (payload.get("value_slice") or {}).get("slice_kind"),
    ]
    return " ".join(str(item or "").lower() for item in fields)


def present(value: Any) -> bool:
    return value not in (None, "", [], {})


def suspicious_text_paths(value: Any, path: str = "$") -> list[str]:
    hits: list[str] = []
    if isinstance(value, str):
        if any(marker in value for marker in GARBLED_MARKERS):
            hits.append(path)
    elif isinstance(value, dict):
        for key, item in value.items():
            hits.extend(suspicious_text_paths(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hits.extend(suspicious_text_paths(item, f"{path}[{index}]"))
    return hits


def outbound_message_id(payload: dict[str, Any]) -> str:
    return str(payload.get("outbound_message_id") or payload.get("message_id") or "")


def target_agent(registry: dict[str, Any], target: str) -> dict[str, Any] | None:
    for agent in registry.get("agents", []):
        if not isinstance(agent, dict):
            continue
        if target in {str(agent.get("agent_id") or ""), str(agent.get("lane") or ""), str(agent.get("display_name") or "")}:
            return agent
    return None


def resolve_dispatch_authorization(root: Path, payload: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str], str | None, str | None]:
    automation = payload.get("automation") or {}
    external_effects = payload.get("external_effects") or automation.get("external_effects") or []
    if not external_effects:
        return None, [], None, None
    request = payload.get("authorization_request") or automation.get("authorization_request")
    if not isinstance(request, dict):
        return None, ["external effects require authorization_request resolved inside Product Value Gate"], None, None
    requested_effects = sorted(str(item) for item in (request.get("requested_external_effects") or []))
    if requested_effects != sorted(str(item) for item in external_effects):
        return None, ["authorization_request external effects do not match dispatch external_effects"], None, None
    registry_path = root / "docs" / "capability-status.json"
    registry = read_json(registry_path)
    result = resolve_authorization.resolve(registry, request)
    errors = [] if result.get("authorized") is True and result.get("status") == "AUTHORIZED" else [
        f"authorization resolver denied external effects: {result.get('errors') or result.get('reason')}"
    ]
    return result, errors, sha256_json(request), sha256_json(registry)


def validate_dispatch(
    payload: dict[str, Any],
    history: list[dict[str, Any]],
    ledger: list[dict[str, Any]] | None = None,
    current_state: dict[str, Any] | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    value_slice = payload.get("value_slice")
    if not isinstance(value_slice, dict):
        return ["missing value_slice object"], warnings

    polluted_contract_fields = sorted(IMMUTABLE_CONTRACT_FORBIDDEN_FIELDS.intersection(payload))
    if polluted_contract_fields:
        errors.append(
            "dispatch contract must remain immutable; gate/provenance results belong in a sidecar: "
            + ", ".join(polluted_contract_fields)
        )
    garbled_paths = suspicious_text_paths(payload)
    if garbled_paths:
        errors.append("garbled human-readable dispatch text detected: " + ", ".join(garbled_paths[:12]))

    required = [
        "value_slice_id",
        "user_outcome",
        "new_user_action",
        "expected_value_delta",
        "active_user_loop",
        "stage_priority",
        "mainline_impact",
        "risk_level",
        "slice_kind",
        "primary_surface",
        "acceptance_criteria",
        "review_policy",
        "callback_budget",
        "next_step_policy",
    ]
    errors.extend(f"missing value_slice.{field}" for field in required if not present(value_slice.get(field)))
    if not present(payload.get("message_id")):
        errors.append("missing message_id")
    if "outbound_message_id" in payload and not present(payload.get("outbound_message_id")):
        errors.append("outbound_message_id must be non-empty when provided")
    if not present(payload.get("task_type")):
        errors.append("missing task_type")
    if not present(payload.get("to_agent") or payload.get("target_lane")):
        errors.append("missing to_agent/target_lane")
    dispatch_mode = str(payload.get("dispatch_mode") or "")
    if dispatch_mode not in VALID_DISPATCH_MODES:
        errors.append("dispatch_mode must be explicitly manual or auto")

    if value_slice.get("expected_value_delta") not in ALLOWED_VALUE_DELTAS:
        errors.append("expected_value_delta must describe a real user/blocker/quality/risk change")
    if value_slice.get("stage_priority") not in VALID_STAGE_PRIORITIES:
        errors.append("stage_priority must be P1-P5")
    if value_slice.get("mainline_impact") not in VALID_MAINLINE_IMPACTS:
        errors.append("mainline_impact must directly advance, unblock, improve confidence, or reduce risk")
    if value_slice.get("next_step_policy") != "advisory_only":
        errors.append("next_step_policy must be advisory_only")
    if value_slice.get("completion_gate_required") is not True:
        errors.append("value_slice.completion_gate_required must be true")

    blocker_id = value_slice.get("blocking_concern_id")
    blob = text_blob(payload)
    wrapper_hits = sorted(term for term in WRAPPER_TERMS if term in blob)
    if wrapper_hits and not present(blocker_id):
        errors.append(f"wrapper-like dispatch requires blocking_concern_id: {', '.join(wrapper_hits)}")

    supporting = value_slice.get("supporting_surfaces") or []
    if not isinstance(supporting, list):
        errors.append("supporting_surfaces must be a list")
        supporting = []
    non_summary = [item for item in supporting if not isinstance(item, dict) or item.get("mode") != "link_or_summary"]
    if non_summary and not value_slice.get("tool_level_ia_change"):
        errors.append("supporting surfaces may only use link_or_summary unless this is a Tool-Level IA change")

    criteria = value_slice.get("acceptance_criteria") or []
    if not isinstance(criteria, list) or len(criteria) < 2:
        errors.append("acceptance_criteria must contain at least two verifiable outcomes")

    try:
        callback_budget = int(value_slice.get("callback_budget", 0))
    except (TypeError, ValueError):
        callback_budget = 0
    if callback_budget < 1 or callback_budget > 3:
        errors.append("callback_budget must be between 1 and 3")

    target_lane = str(payload.get("to_agent") or payload.get("target_lane") or "")
    review_policy = str(value_slice.get("review_policy") or "")
    risk_level = str(value_slice.get("risk_level") or "")
    if target_lane in REVIEW_LANES:
        if review_policy not in ALLOWED_REVIEW_POLICIES:
            errors.append("review dispatch requires an allowed review_policy")
        if risk_level in {"low_risk", "medium_risk"} and review_policy not in {
            "bundle_boundary",
            "stage_boundary",
            "user_requested",
            "blocking_concern",
        }:
            errors.append("low/medium risk review is allowed only at a bundle/stage boundary or explicit blocker/request")

    if value_slice.get("capability_registry_change"):
        registry_target = str(value_slice.get("registry_target") or "")
        if wrapper_hits and registry_target.endswith("capability-status.json"):
            errors.append("UI consumer/handoff/readiness must update product-feature-status.json, not capability-status.json")

    slice_id = str(value_slice.get("value_slice_id") or "")
    previous_dispatches = [
        row
        for row in history
        if row.get("value_slice_id") == slice_id
        or isinstance(row.get("value_slice"), dict)
        and row["value_slice"].get("value_slice_id") == slice_id
    ]
    ledger_usage = dispatch_reservation_usage(ledger or [], slice_id)
    historical_usage = len(previous_dispatches)
    used_budget = ledger_usage if ledger_usage > 0 else historical_usage
    if callback_budget and used_budget >= callback_budget:
        errors.append(f"value slice interaction budget exhausted: {used_budget}/{callback_budget}")

    active = (current_state or {}).get("active_value_slice")
    if isinstance(active, dict):
        active_status = str(active.get("status") or "").upper()
        active_slice_id = str(active.get("value_slice_id") or "")
        if active_status not in {"DONE", "DONE_WITH_CONCERNS", "BLOCKED", "CANCELLED", "COMPLETE"} and active_slice_id and active_slice_id != slice_id:
            errors.append(f"another active value slice is already in progress: {active_slice_id}")

    automation = payload.get("automation") or {}
    if dispatch_mode == "auto":
        if automation.get("auto_dispatch") is not True:
            errors.append("auto dispatch requires automation.auto_dispatch=true")
        policy = (current_state or {}).get("automation_policy") or {}
        if policy.get("status") not in {"authorized_ready", "running"}:
            errors.append("bounded autopilot is not authorized_ready or running")
        if risk_level not in set(policy.get("allowed_risk_levels") or []):
            errors.append(f"risk level is outside bounded autopilot: {risk_level}")
        consecutive = int(policy.get("consecutive_auto_slices") or 0)
        maximum = int(policy.get("max_consecutive_auto_slices") or 0)
        if maximum < 1 or consecutive >= maximum:
            errors.append(f"automatic slice checkpoint required: {consecutive}/{maximum}")
        if automation.get("auto_iteration_id") != policy.get("auto_iteration_id"):
            errors.append("automation.auto_iteration_id does not match current-state policy")
    elif automation.get("auto_dispatch") is True:
        errors.append("manual dispatch cannot set automation.auto_dispatch=true")

    external_effects = payload.get("external_effects") or automation.get("external_effects") or []
    if external_effects:
        request = payload.get("authorization_request") or automation.get("authorization_request")
        if not isinstance(request, dict):
            errors.append("external effects require authorization_request for internal resolver execution")

    if len(supporting) > 4:
        warnings.append("more than four supporting links may still indicate IA sprawl")
    if value_slice.get("stage_priority") in {"P4", "P5"} and not present(blocker_id):
        errors.append("P4/P5 work requires a P1/P2 blocking_concern_id")
    return errors, warnings


def self_test() -> dict[str, Any]:
    valid = {
        "message_id": "self-test-valid",
        "dispatch_mode": "manual",
        "task_type": "development_vertical_slice",
        "to_agent": "development",
        "value_slice": {
            "value_slice_id": "VS-SELF-1",
            "user_outcome": "用户可以完成一次端到端复盘",
            "new_user_action": "提交一次模拟动作并回看结果",
            "expected_value_delta": "new_user_action",
            "active_user_loop": "发现 -> 复盘",
            "stage_priority": "P1",
            "mainline_impact": "direct_advance",
            "risk_level": "medium_risk",
            "slice_kind": "vertical_product_slice",
            "primary_surface": "Primary Workbench",
            "supporting_surfaces": [{"surface": "Object List", "mode": "link_or_summary"}],
            "acceptance_criteria": ["动作可执行", "结果可回看"],
            "review_policy": "bundle_boundary",
            "callback_budget": 3,
            "next_step_policy": "advisory_only",
            "completion_gate_required": True,
        },
    }
    invalid = json.loads(json.dumps(valid, ensure_ascii=False))
    invalid["message_id"] = "self-test-invalid"
    invalid["task_type"] = "development_consumer_handoff"
    invalid["value_slice"]["new_user_action"] = "新增 consumer"
    valid_errors, _ = validate_dispatch(valid, [], [], {})
    invalid_errors, _ = validate_dispatch(invalid, [], [], {})
    missing_mode = json.loads(json.dumps(valid, ensure_ascii=False))
    missing_mode.pop("dispatch_mode")
    missing_mode_errors, _ = validate_dispatch(missing_mode, [], [], {})
    conflicting_state = {"active_value_slice": {"value_slice_id": "VS-OTHER", "status": "DISPATCHED"}}
    conflict_errors, _ = validate_dispatch(valid, [], [], conflicting_state)
    auto_omitted = json.loads(json.dumps(valid, ensure_ascii=False))
    auto_omitted["dispatch_mode"] = "auto"
    auto_state = {
        "automation_policy": {
            "status": "running",
            "allowed_risk_levels": ["medium_risk"],
            "consecutive_auto_slices": 0,
            "max_consecutive_auto_slices": 2,
            "auto_iteration_id": "AUTO-SELF",
        }
    }
    auto_omitted["automation"] = {"auto_iteration_id": "AUTO-SELF"}
    auto_omitted_errors, _ = validate_dispatch(auto_omitted, [], [], auto_state)
    manual_effect = json.loads(json.dumps(valid, ensure_ascii=False))
    manual_effect["external_effects"] = ["remote_write"]
    manual_effect_errors, _ = validate_dispatch(manual_effect, [], [], {})
    garbled = json.loads(json.dumps(valid, ensure_ascii=False))
    garbled["value_slice"]["user_outcome"] = "???"
    garbled_errors, _ = validate_dispatch(garbled, [], [], {})
    polluted = json.loads(json.dumps(valid, ensure_ascii=False))
    polluted["dispatch_hash"] = "should-live-in-sidecar"
    polluted_errors, _ = validate_dispatch(polluted, [], [], {})
    passed = (
        not valid_errors
        and any("blocking_concern_id" in item for item in invalid_errors)
        and any("dispatch_mode" in item for item in missing_mode_errors)
        and any("another active value slice" in item for item in conflict_errors)
        and any("automation.auto_dispatch" in item for item in auto_omitted_errors)
        and any("authorization_request" in item for item in manual_effect_errors)
        and any("garbled human-readable" in item for item in garbled_errors)
        and any("dispatch contract must remain immutable" in item for item in polluted_errors)
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "valid_errors": valid_errors,
        "invalid_errors": invalid_errors,
        "missing_mode_errors": missing_mode_errors,
        "active_slice_conflict_errors": conflict_errors,
        "auto_mode_omission_errors": auto_omitted_errors,
        "manual_external_effect_errors": manual_effect_errors,
        "garbled_text_errors": garbled_errors,
        "polluted_contract_errors": polluted_errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one Agent Lanes V2 value-slice dispatch.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--dispatch-file")
    parser.add_argument("--ledger", default="agent-lanes/value-slice-ledger.jsonl")
    parser.add_argument("--record-dispatch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        result = self_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "PASS" else 1
    if not args.dispatch_file:
        raise SystemExit("--dispatch-file is required unless --self-test is used")
    if args.record_dispatch == args.dry_run:
        raise SystemExit("choose exactly one of --record-dispatch or --dry-run")

    root = Path(args.project_root).resolve()
    payload = read_json(Path(args.dispatch_file).resolve())
    history = read_jsonl(root / "agent-lanes" / "message-log.jsonl")
    ledger_path = (root / args.ledger).resolve()
    ledger = read_jsonl(ledger_path)
    current_state_path = root / "agent-lanes" / "current-state.json"
    current_state = read_json(current_state_path) if current_state_path.exists() else {}
    errors, warnings = validate_dispatch(payload, history, ledger, current_state)
    authorization_resolution, authorization_errors, authorization_request_hash, authorization_registry_hash = resolve_dispatch_authorization(root, payload)
    authorization_result_hash = sha256_json(authorization_resolution) if authorization_resolution is not None else None
    errors.extend(authorization_errors)
    registry = read_json(root / "agent-lanes" / "agent-registry.json")
    target = str(payload.get("to_agent") or payload.get("target_lane") or "")
    agent = target_agent(registry, target)
    if not agent:
        errors.append("target lane is not registered")
    target_thread_id = str((agent or {}).get("thread_id") or "")
    if not target_thread_id:
        errors.append("target lane is missing thread_id")
    dispatch_hash = sha256_json(payload)
    callback_claim = {
        "dispatch_id": outbound_message_id(payload),
        "value_slice_id": (payload.get("value_slice") or {}).get("value_slice_id"),
        "target_lane": (agent or {}).get("agent_id"),
        "target_thread_id": target_thread_id,
        "dispatch_hash": dispatch_hash,
    }
    callback_provenance = sign_claim(root, "lane_callback", callback_claim) if not errors else None
    recorded = False
    if not errors and args.record_dispatch:
        value_slice = payload.get("value_slice") or {}
        interaction_id = outbound_message_id(payload)
        try:
            _, recorded = reserve_dispatch(
                ledger_path,
                {
                    "schema_version": "agent-lanes.value-slice-ledger.v1",
                    "control_version": CONTROL_VERSION,
                    "event_id": f"dispatch-{interaction_id}",
                    "event_type": "dispatch_started",
                    "value_slice_id": value_slice.get("value_slice_id"),
                    "interaction_id": interaction_id,
                    "source_message_id": interaction_id,
                    "actor": "product_value_gate",
                    "dispatch_hash": dispatch_hash,
                    "summary": payload.get("summary") or value_slice.get("title"),
                    "task_type": payload.get("task_type"),
                    "target_lane": payload.get("to_agent") or payload.get("target_lane"),
                    "target_thread_id": target_thread_id,
                    "dispatch_mode": payload.get("dispatch_mode"),
                    "callback_budget": int(value_slice.get("callback_budget") or 0),
                    "auto_iteration_id": (payload.get("automation") or {}).get("auto_iteration_id"),
                    "authorization_request_hash": authorization_request_hash,
                    "authorization_registry_hash": authorization_registry_hash,
                    "authorization_result_hash": authorization_result_hash,
                    "created_at": now_text(),
                },
                current_state_path,
            )
        except (ValueError, TimeoutError) as exc:
            errors.append(str(exc))
    latest_ledger = read_jsonl(ledger_path)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "dispatch_file": str(Path(args.dispatch_file)),
        "dispatch_message_id": outbound_message_id(payload),
        "value_slice_id": (payload.get("value_slice") or {}).get("value_slice_id"),
        "interaction_budget_used": dispatch_reservation_usage(latest_ledger, str((payload.get("value_slice") or {}).get("value_slice_id") or "")) or len(
                [
                    row
                    for row in history
                    if row.get("value_slice_id") == (payload.get("value_slice") or {}).get("value_slice_id")
                    or isinstance(row.get("value_slice"), dict)
                    and row["value_slice"].get("value_slice_id") == (payload.get("value_slice") or {}).get("value_slice_id")
                ]
            ),
        "dispatch_recorded": recorded,
        "dispatch_hash": dispatch_hash,
        "callback_provenance": callback_provenance,
        "authorization_resolution": authorization_resolution,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
