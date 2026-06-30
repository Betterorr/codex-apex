from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


LANES = [
    ("orchestrator", "主调度泳道"),
    ("planning", "规划泳道"),
    ("design", "设计泳道"),
    ("development", "开发泳道"),
    ("guardian", "守门泳道"),
    ("review", "验收泳道"),
    ("evolution", "进化泳道"),
]


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def copy_if_needed(src: Path, dst: Path, overwrite: bool, report: list[str]) -> None:
    if not src.exists():
        report.append(f"SKIP missing template file: {src}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        report.append(f"KEEP existing: {dst}")
        return
    shutil.copy2(src, dst)
    report.append(f"COPY {src} -> {dst}")


def copy_tree_files_if_needed(src_dir: Path, dst_dir: Path, overwrite: bool, report: list[str]) -> None:
    if not src_dir.exists():
        report.append(f"SKIP missing template dir: {src_dir}")
        return
    for src in src_dir.rglob("*"):
        if not src.is_file():
            continue
        rel = src.relative_to(src_dir)
        copy_if_needed(src, dst_dir / rel, overwrite, report)


def write_if_missing(path: Path, content: str, report: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        report.append(f"KEEP existing: {path}")
        return
    path.write_text(content, encoding="utf-8")
    report.append(f"CREATE {path}")


def load_policy(template_path: Path) -> dict:
    policy = json.loads(template_path.read_text(encoding="utf-8-sig"))
    policy["enabled_at"] = iso_now()
    policy.setdefault("mode", "advisory")
    return policy


def build_registry(project_name: str, primary_module: str, orchestrator_thread_id: str) -> dict:
    agents = []
    for lane_id, display_name in LANES:
        thread_id = orchestrator_thread_id if lane_id == "orchestrator" else "pending_setup"
        agents.append(
            {
                "agent_id": lane_id,
                "display_name": display_name,
                "thread_id": thread_id,
                "status": "active" if lane_id == "orchestrator" else "pending_setup",
                "worklog": f"agent-lanes/lanes/{lane_id}/worklog.md",
                "workspace": f"agent-lanes/lanes/{lane_id}/workspace",
                "read_scope": [
                    "AGENTS.md",
                    "docs/",
                    "agent-lanes/",
                    primary_module,
                ],
                "write_scope": [
                    f"agent-lanes/lanes/{lane_id}/worklog.md",
                    f"agent-lanes/lanes/{lane_id}/workspace/",
                    "agent-lanes/message-log.jsonl",
                ],
            }
        )
    return {
        "project": project_name,
        "version": 1,
        "created_at": iso_now(),
        "agents": agents,
        "communication": {
            "callback_delivery": "post_office_direct_thread_prompt",
            "audit_log": "agent-lanes/message-log.jsonl",
            "message_log_role": "audit_backup_not_default_inbox",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy Agent Lanes template into a target project.")
    parser.add_argument("--target-root", required=True, help="Target project root.")
    parser.add_argument("--template-dir", default=None, help="Template directory. Defaults to parent of this script dir.")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--primary-module", default=".")
    parser.add_argument("--orchestrator-thread-id", default="pending_setup")
    parser.add_argument("--overwrite-runtime", action="store_true", help="Overwrite existing runtime template/script files.")
    args = parser.parse_args()

    target = Path(args.target_root).resolve()
    template = Path(args.template_dir).resolve() if args.template_dir else Path(__file__).resolve().parents[1]
    report: list[str] = []

    agent_lanes = target / "agent-lanes"
    callback_inbox = agent_lanes / "callback-inbox"
    for directory in [
        agent_lanes / "scripts",
        callback_inbox / "pending",
        callback_inbox / "delivered",
        callback_inbox / "outbox",
    ]:
        directory.mkdir(parents=True, exist_ok=True)
        report.append(f"ENSURE DIR {directory}")

    for lane_id, _ in LANES:
        for directory in [
            agent_lanes / "lanes" / lane_id / "workspace",
        ]:
            directory.mkdir(parents=True, exist_ok=True)
            report.append(f"ENSURE DIR {directory}")

    copies = [
        ("agent-lanes.template.md", "agent-lanes/agent-lanes.md"),
        ("completion-callback.template.json", "agent-lanes/completion-callback.template.json"),
        ("scripts/render_dashboard.py", "agent-lanes/scripts/render_dashboard.py"),
        ("scripts/deploy_agent_lanes_template.py", "agent-lanes/scripts/deploy_agent_lanes_template.py"),
        ("scripts/deliver_callback.py", "agent-lanes/scripts/deliver_callback.py"),
        ("scripts/callback_post_office.py", "agent-lanes/scripts/callback_post_office.py"),
        ("scripts/check_callback_post_office.py", "agent-lanes/scripts/check_callback_post_office.py"),
        ("goal-development-base/scripts/check-agent-lanes-post-office.ps1", "scripts/check-agent-lanes-post-office.ps1"),
    ]
    for src_rel, dst_rel in copies:
        copy_if_needed(template / src_rel, target / dst_rel, args.overwrite_runtime, report)

    copy_tree_files_if_needed(
        template / "goal-development-base" / ".agents" / "skills",
        target / ".agents" / "skills",
        args.overwrite_runtime,
        report,
    )
    copy_tree_files_if_needed(
        template / "goal-development-base" / ".codex" / "hooks",
        target / ".codex" / "hooks",
        args.overwrite_runtime,
        report,
    )

    policy_template = template / "callback-inbox" / "post-office-policy.json"
    policy_target = callback_inbox / "post-office-policy.json"
    if policy_template.exists() and (args.overwrite_runtime or not policy_target.exists()):
        policy = load_policy(policy_template)
        policy_target.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report.append(f"CREATE {policy_target}")
    else:
        report.append(f"KEEP existing: {policy_target}")

    registry_path = agent_lanes / "agent-registry.json"
    if not registry_path.exists():
        registry = build_registry(args.project_name, args.primary_module, args.orchestrator_thread_id)
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report.append(f"CREATE {registry_path}")
    else:
        report.append(f"KEEP existing: {registry_path}")

    worklog_template = template / "worklog-template.md"
    base_worklog = worklog_template.read_text(encoding="utf-8-sig") if worklog_template.exists() else "# Worklog\n"
    for lane_id, display_name in LANES:
        worklog = agent_lanes / "lanes" / lane_id / "worklog.md"
        content = (
            f"{base_worklog.rstrip()}\n\n"
            f"## {iso_now()} 初始化\n\n"
            f"- 泳道：`{display_name}` / `{lane_id}`\n"
            f"- thread_id：`{args.orchestrator_thread_id if lane_id == 'orchestrator' else 'pending_setup'}`\n"
            f"- 状态：模板部署初始化。\n"
        )
        write_if_missing(worklog, content, report)

    message_log = agent_lanes / "message-log.jsonl"
    message_log.parent.mkdir(parents=True, exist_ok=True)
    bootstrap_event = {
        "message_id": f"bootstrap-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "task_type": "agent_lanes_bootstrap",
        "from_agent": "template_deploy_script",
        "to_agent": "orchestrator",
        "status": "DONE",
        "summary": "Agent Lanes template deployed with post-office direct thread_prompt callback rules.",
        "template_dir": str(template),
        "orchestrator_thread_id": args.orchestrator_thread_id,
        "created_at": iso_now(),
    }
    with message_log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(bootstrap_event, ensure_ascii=False) + "\n")
    report.append(f"APPEND {message_log}")

    snippet = target / "agent-lanes" / "AGENTS.agent-lanes-snippet.md"
    write_if_missing(
        snippet,
        "# Agent Lanes 规则片段\n\n"
        "- 非主调度泳道完成后调用 `agent-lanes/scripts/deliver_callback.py`。\n"
        "- `message-log.jsonl` 只作为审计备份，不是主调度默认收件箱。\n"
        "- `deliver_callback.py` 输出 `send_required=true` 时，只发送返回的 `thread_prompt` 一次。\n"
        "- `deliver_callback.py` 输出 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log` 记录时，不算完成回报已送达；必须重跑投递或记录阻塞，不能短 wake。\n"
        "- 主调度收到 `【邮局合并回报】` 后直接处理原文。\n",
        report,
    )

    install_report = agent_lanes / "INSTALL-REPORT.md"
    install_report.write_text("# Agent Lanes 安装报告\n\n" + "\n".join(f"- {line}" for line in report) + "\n", encoding="utf-8")
    print(json.dumps({"status": "DONE", "target_root": str(target), "template_dir": str(template), "report": report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
