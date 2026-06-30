#!/usr/bin/env python3
"""Render a readable Agent Lanes dashboard."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AGENT_LANES = ROOT / "agent-lanes"


LANE_LABELS = {
    "orchestrator": "主调度泳道",
    "planning": "规划泳道",
    "design": "设计泳道",
    "development": "开发泳道",
    "guardian": "守门泳道",
    "review": "验收泳道",
    "evolution": "进化泳道",
    "callback_post_office": "回报邮局",
}


def now_text() -> str:
    return datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()


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
            row = json.loads(line)
        except json.JSONDecodeError:
            row = {
                "message_id": f"parse-error-line-{line_no}",
                "status": "PARSE_ERROR",
                "summary": line[:160],
                "created_at": "",
            }
        rows.append(row)
    return rows


def rel(path: str | Path) -> str:
    path_obj = Path(path)
    text = path_obj.as_posix()
    if path_obj.is_absolute():
        try:
            text = path_obj.relative_to(ROOT).as_posix()
        except ValueError:
            text = path_obj.as_posix()
    return text


def md_link(label: str, path: str | Path) -> str:
    return f"[{label}]({rel(path)})"


def compact(value: Any, max_len: int = 120) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text if len(text) <= max_len else text[: max_len - 1].rstrip() + "…"


def readable(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def valid_display_callback(msg: dict[str, Any]) -> bool:
    return completion_like(msg) and not message_is_garbled(msg)


def item_link_or_code(item: Any) -> str:
    text = readable(item)
    if not text:
        return "-"
    path = ROOT / text
    if path.exists():
        return md_link(text, text)
    return f"`{text}`" if ("/" in text or "\\" in text or "." in Path(text).name) else text


def append_value_block(lines: list[str], title: str, value: Any) -> None:
    if value in (None, "", []):
        return
    lines.append(f"**{title}**")
    if isinstance(value, list):
        for item in value:
            lines.append(f"- {item_link_or_code(item)}")
    else:
        for paragraph in readable(value).splitlines():
            paragraph = paragraph.strip()
            if paragraph:
                lines.append(paragraph)
    lines.append("")


def csv_value(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, list):
        return "\n".join(csv_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def time_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return text
    return parsed.strftime("%Y-%m-%d %H:%M:%S")


def communication_type(msg: dict[str, Any]) -> str:
    task_type = str(msg.get("task_type") or "")
    if task_type == "callback_batch_ready":
        return "邮局合并批次"
    if task_type == "callback_spooled":
        return "邮局暂存回执"
    if task_type == "orchestrator_state":
        return "主调度忙闲状态"
    if is_dispatch(msg):
        return "主调度派发"
    if completion_like(msg):
        return "泳道完成回报"
    return "普通记录"


def quality_state(msg: dict[str, Any]) -> str:
    if message_is_garbled(msg):
        return "乱码/需重发"
    if completion_like(msg) and not msg.get("delivery_mode") and str(msg.get("to_agent") or "") == "主调度泳道":
        return "可能旧式直投"
    return "正常"


def communication_full_row(msg: dict[str, Any], aliases: dict[str, str]) -> dict[str, str]:
    return {
        "created_at": csv_value(msg.get("created_at")),
        "message_id": csv_value(msg.get("message_id")),
        "reply_to": csv_value(msg.get("reply_to")),
        "from_agent": lane_label(msg.get("from_agent"), aliases),
        "to_agent": lane_label(msg.get("to_agent"), aliases),
        "communication_type": communication_type(msg),
        "task_type": csv_value(msg.get("task_type")),
        "status": csv_value(msg.get("status")),
        "delivery_mode": csv_value(msg.get("delivery_mode")),
        "batch_id": csv_value(msg.get("batch_id")),
        "quality_state": quality_state(msg),
        "summary": csv_value(msg.get("summary")),
        "changed_files": csv_value(msg.get("changed_files")),
        "evidence": csv_value(msg.get("evidence")),
        "concerns": csv_value(msg.get("concerns")),
        "next_recommended_lane": lane_label(msg.get("next_recommended_lane"), aliases),
        "next_recommended_action": csv_value(msg.get("next_recommended_action")),
        "callback_ids": csv_value(msg.get("callback_ids")),
        "outbox_path": csv_value(msg.get("outbox_path")),
        "orchestrator_message_path": csv_value(msg.get("orchestrator_message_path")),
        "thread_prompt": csv_value(msg.get("thread_prompt")),
        "orchestrator_message": csv_value(msg.get("orchestrator_message")),
        "raw_json": json.dumps(msg, ensure_ascii=False, separators=(",", ":")),
    }


def communication_readable_row(index: int, msg: dict[str, Any], aliases: dict[str, str]) -> dict[str, str]:
    return {
        "序号": str(index),
        "时间": time_text(msg.get("created_at")),
        "类型": communication_type(msg),
        "来源": lane_label(msg.get("from_agent"), aliases),
        "去向": lane_label(msg.get("to_agent"), aliases),
        "状态": csv_value(msg.get("status")),
        "质量": quality_state(msg),
        "对应任务": csv_value(msg.get("reply_to")),
        "消息编号": csv_value(msg.get("message_id")),
        "摘要": csv_value(msg.get("summary")),
        "建议动作": csv_value(msg.get("next_recommended_action")),
        "产物/文件": csv_value(msg.get("changed_files")),
        "验证证据": csv_value(msg.get("evidence")),
        "关注点": csv_value(msg.get("concerns")),
        "邮局批次": csv_value(msg.get("batch_id") or msg.get("outbox_path")),
        "主调度收到原文": csv_value(msg.get("thread_prompt") or msg.get("orchestrator_message")),
        "原始JSON": json.dumps(msg, ensure_ascii=False, separators=(",", ":")),
    }


def export_readable_xlsx(rows: list[dict[str, str]], path: Path) -> bool:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    except Exception:
        return False

    headers = list(rows[0].keys()) if rows else [
        "序号",
        "时间",
        "类型",
        "来源",
        "去向",
        "状态",
        "质量",
        "对应任务",
        "消息编号",
        "摘要",
        "建议动作",
        "产物/文件",
        "验证证据",
        "关注点",
        "邮局批次",
        "主调度收到原文",
        "原始JSON",
    ]
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "完整收发账本"
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header, "") for header in headers])

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin", color="D9E2F3")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    good_fill = PatternFill("solid", fgColor="E2F0D9")
    warn_fill = PatternFill("solid", fgColor="FFF2CC")
    bad_fill = PatternFill("solid", fgColor="FCE4D6")
    type_fill = PatternFill("solid", fgColor="DDEBF7")

    widths = {
        "序号": 8,
        "时间": 20,
        "类型": 16,
        "来源": 14,
        "去向": 14,
        "状态": 16,
        "质量": 16,
        "对应任务": 34,
        "消息编号": 38,
        "摘要": 72,
        "建议动作": 72,
        "产物/文件": 48,
        "验证证据": 72,
        "关注点": 60,
        "邮局批次": 34,
        "主调度收到原文": 90,
        "原始JSON": 90,
    }

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border

    header_index = {name: idx + 1 for idx, name in enumerate(headers)}
    for row in sheet.iter_rows(min_row=2):
        quality = str(row[header_index["质量"] - 1].value or "")
        row_fill = good_fill if quality == "正常" else warn_fill
        if "乱码" in quality or "重发" in quality:
            row_fill = bad_fill
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = border
            cell.fill = row_fill
        row[header_index["类型"] - 1].fill = type_fill

    for column_cells in sheet.columns:
        header = str(column_cells[0].value or "")
        sheet.column_dimensions[column_cells[0].column_letter].width = widths.get(header, 20)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    sheet.sheet_view.showGridLines = False
    for row_idx in range(2, sheet.max_row + 1):
        sheet.row_dimensions[row_idx].height = 72
    sheet.row_dimensions[1].height = 28
    workbook.save(path)
    return True


def export_communications_workbook(messages: list[dict[str, Any]], aliases: dict[str, str]) -> dict[str, Path]:
    readable_xlsx_path = AGENT_LANES / "communications-readable.xlsx"
    readable_rows = [communication_readable_row(index, msg, aliases) for index, msg in enumerate(messages, start=1)]
    export_readable_xlsx(readable_rows, readable_xlsx_path)
    return {"readable_xlsx": readable_xlsx_path}


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


def looks_garbled(value: Any) -> bool:
    return any(("???" in text.strip()) or (text.strip() and set(text.strip()) == {"?"}) for text in iter_text_values(value))


def message_is_garbled(msg: dict[str, Any]) -> bool:
    fields = [
        msg.get("from_agent"),
        msg.get("to_agent"),
        msg.get("summary"),
        msg.get("evidence"),
        msg.get("concerns"),
        msg.get("next_recommended_action"),
        msg.get("orchestrator_message"),
        msg.get("thread_prompt"),
    ]
    return any(looks_garbled(field) for field in fields)


def completion_like(msg: dict[str, Any]) -> bool:
    if msg.get("task_type") in {"completion_callback", "completion_callback_protocol_update"}:
        return True
    if msg.get("status") not in {"DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"}:
        return False
    fields = ["summary", "changed_files", "evidence", "concerns", "next_recommended_lane", "next_recommended_action"]
    return sum(1 for field in fields if msg.get(field) not in (None, "", [])) >= 4


def is_dispatch(msg: dict[str, Any]) -> bool:
    task_type = str(msg.get("task_type") or "")
    status = str(msg.get("status") or "")
    return status in {"DISPATCHED", "sent", "active_dispatch"} or "dispatch" in task_type


def is_reply_to(msg: dict[str, Any], dispatch_id: str) -> bool:
    return str(msg.get("reply_to") or "") == dispatch_id and completion_like(msg)


def dispatch_reply_tokens(msg: dict[str, Any]) -> set[str]:
    tokens = {str(msg.get("message_id") or "")}
    for key, value in msg.items():
        if key.endswith("_dispatch_id") and value:
            tokens.add(str(value))
    return {token for token in tokens if token}


def worklog_progress(path_value: Any) -> str:
    if not path_value:
        return "-"
    path = ROOT / str(path_value)
    if not path.exists():
        return "未找到 worklog"
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return "worklog 编码不可读"
    headings = [line.strip("# ").strip() for line in lines if line.startswith("## ")]
    if headings:
        return compact(headings[-1], 80)
    nonempty = [line.strip() for line in lines if line.strip()]
    return compact(nonempty[-1], 80) if nonempty else "暂无进度"


def msg_link(label: str, msg: dict[str, Any]) -> str:
    mid = compact(msg.get("message_id"), 64)
    return f"{label}: `{mid}`" if mid else label


def status_badge(status: str) -> str:
    labels = {
        "active": "运行中",
        "paused": "暂停",
        "archived": "归档",
        "blocked": "阻塞",
    }
    return labels.get(status, status or "-")


def lane_label(value: Any, aliases: dict[str, str] | None = None) -> str:
    text = str(value or "")
    if aliases and text in aliases:
        return aliases[text]
    return LANE_LABELS.get(text, text or "-")


def short_time(value: Any) -> str:
    text = str(value or "")
    if "T" in text:
        return text.split("T", 1)[1][:8]
    return compact(text, 16)


def human_event(msg: dict[str, Any], aliases: dict[str, str]) -> str:
    task_type = str(msg.get("task_type", ""))
    source = lane_label(msg.get("from_agent"), aliases)
    status = str(msg.get("status") or "")
    summary = compact(msg.get("summary"), 120)
    if message_is_garbled(msg):
        return f"需要重发：检测到乱码回报 `{compact(msg.get('message_id'), 72)}`。"
    if task_type == "callback_batch_ready":
        count = len(msg.get("callback_ids") or [])
        return f"邮局把 {count} 条泳道回报合并成 1 条主调度消息。"
    if task_type == "callback_spooled":
        return f"{source} 的回报已进入邮局暂存，等待主调度空闲后合批。"
    if task_type == "orchestrator_state":
        state = "空闲" if msg.get("state") == "idle" else "忙碌"
        return f"主调度状态变为{state}：{compact(msg.get('reason'), 80)}"
    if task_type in {"completion_callback", "completion_callback_protocol_update"}:
        return f"{source} 回报 {status}：{summary}"
    if task_type == "queued_dispatch":
        return f"有任务进入排队：{summary}"
    return summary or compact(task_type, 80)


def latest_post_office_status() -> dict[str, Any]:
    state_path = AGENT_LANES / "callback-inbox" / "post-office-state.json"
    pending_dir = AGENT_LANES / "callback-inbox" / "pending"
    state: dict[str, Any] = {}
    if state_path.exists():
        try:
            state = read_json(state_path)
        except json.JSONDecodeError:
            state = {"status": "unreadable"}
    pending_count = len(list(pending_dir.glob("*.json"))) if pending_dir.exists() else 0
    state["pending_count"] = pending_count
    return state


def first_lines(text: str, max_lines: int = 16) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if len(lines) <= max_lines:
        return lines
    return lines[:max_lines] + [f"……另有 {len(lines) - max_lines} 行，见批次消息文件。"]


def main() -> int:
    registry = read_json(AGENT_LANES / "agent-registry.json")
    messages = read_jsonl(AGENT_LANES / "message-log.jsonl")
    agents = registry.get("agents", [])

    lane_aliases: dict[str, str] = {}
    for agent in agents:
        lane_aliases[str(agent.get("agent_id", ""))] = str(agent.get("display_name", ""))
        lane_aliases[str(agent.get("display_name", ""))] = str(agent.get("display_name", ""))
    lane_aliases.update(LANE_LABELS)
    known_lane_names = {str(agent.get("display_name", "")) for agent in agents if agent.get("display_name")}

    callback_types = {"completion_callback", "completion_callback_protocol_update"}
    callbacks = [m for m in messages if m.get("task_type") in callback_types or completion_like(m)]
    display_callbacks = [m for m in callbacks if valid_display_callback(m)]
    dispatches = [m for m in messages if is_dispatch(m)]
    batches = [m for m in messages if m.get("task_type") == "callback_batch_ready"]
    orchestrator_states = [m for m in messages if m.get("task_type") == "orchestrator_state"]
    latest_batch = batches[-1] if batches else None
    latest_state = orchestrator_states[-1] if orchestrator_states else None
    post_office = latest_post_office_status()
    garbled_messages = [m for m in messages if message_is_garbled(m)]
    current_garbled = [m for m in garbled_messages if str(m.get("created_at") or "") >= "2026-06-24T15:49:29+08:00"]
    communication_exports = export_communications_workbook(messages, lane_aliases)

    latest_callback_by_lane: dict[str, dict[str, Any]] = {}
    for msg in display_callbacks:
        lane_name = lane_label(msg.get("from_agent"), lane_aliases)
        latest_callback_by_lane[lane_name] = msg

    latest_inbox_by_lane: dict[str, dict[str, Any]] = {}
    latest_open_dispatch_by_lane: dict[str, dict[str, Any]] = {}
    for msg in dispatches:
        lane_name = lane_label(msg.get("to_agent"), lane_aliases)
        if lane_name not in known_lane_names:
            continue
        latest_inbox_by_lane[lane_name] = msg
        tokens = dispatch_reply_tokens(msg)
        if tokens and not any(any(is_reply_to(candidate, token) for token in tokens) for candidate in messages):
            latest_open_dispatch_by_lane[lane_name] = msg

    latest_spool_by_reply: dict[str, dict[str, Any]] = {}
    for msg in messages:
        if msg.get("task_type") == "callback_spooled" and msg.get("reply_to"):
            latest_spool_by_reply[str(msg.get("reply_to"))] = msg

    active_non_orchestrator = [
        a for a in agents if a.get("agent_id") != "orchestrator" and a.get("status") == "active"
    ]
    callback_covered = sum(1 for a in active_non_orchestrator if a.get("display_name") in latest_callback_by_lane)

    lines: list[str] = []
    lines.append("# Agent Lanes 总控台")
    lines.append("")
    lines.append(f"更新时间：`{now_text()}`")
    lines.append("")
    lines.append("这是给人看的入口：先看当前状态、邮局批次、泳道回报和下一步建议；长 ID、脚本路径和原始 JSON 放在最后的排查入口。")
    lines.append("")

    lines.append("## 一眼看懂")
    lines.append("")
    lines.append(f"- 活跃泳道：`{sum(1 for a in agents if a.get('status') == 'active')}`")
    lines.append(f"- 完成回报覆盖：`{callback_covered}/{len(active_non_orchestrator)}` 条非主调度活跃泳道已有回报记录")
    open_count = len(latest_open_dispatch_by_lane)
    lines.append(f"- 可能待回派发：`{open_count}` 条最新收信未直接匹配完成回报；旧记录可能因 reply_to 使用任务 id 而无法自动折叠")
    if current_garbled:
        lines.append(f"- 当前质量告警：`{len(current_garbled)}` 条新记录含 `???`，需要对应泳道重发 UTF-8 callback")
    else:
        lines.append("- 当前质量告警：无新乱码回报")
    if latest_state:
        state_label = "空闲" if latest_state.get("state") == "idle" else "忙碌"
        lines.append(f"- 主调度状态：{state_label}（{compact(latest_state.get('reason'), 80)}）")
    else:
        lines.append("- 主调度状态：未看到 `orchestrator_state`，邮局会保持谨慎等待。")
    po_action = compact(post_office.get("last_action") or post_office.get("status") or "unknown", 40)
    lines.append(f"- 回报邮局：{po_action}，暂存待投递 `pending={post_office.get('pending_count', 0)}`")
    if latest_batch:
        lines.append(f"- 最近邮局批次：{len(latest_batch.get('callback_ids') or [])} 条回报已合并为 1 条主调度消息")
    elif callbacks:
        lines.append("- 最近邮局批次：还没有合批记录")
    lines.append(f"- 完整收发账本：{md_link('推荐打开 Excel 版', communication_exports['readable_xlsx'])}")
    lines.append("")

    lines.append("## 泳道收发工作台")
    lines.append("")
    lines.append("| 泳道 | 最近收信 | 当前进度 | 最近回信 | 邮局/质量 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for agent in agents:
        display = str(agent.get("display_name", agent.get("agent_id", "")))
        inbox = latest_inbox_by_lane.get(display)
        open_dispatch = latest_open_dispatch_by_lane.get(display)
        callback = latest_callback_by_lane.get(display)
        inbox_text = "-"
        if inbox:
            state = "可能待回" if open_dispatch and open_dispatch.get("message_id") == inbox.get("message_id") else "已处理/有后续"
            inbox_text = f"{state}<br>{msg_link('收信', inbox)}<br>{compact(inbox.get('summary'), 84)}"
        progress = worklog_progress(agent.get("worklog"))
        reply_text = "-"
        quality_bits: list[str] = []
        if callback:
            reply_text = f"`{short_time(callback.get('created_at'))}` {callback.get('status', '-')}<br>{msg_link('回信', callback)}<br>{compact(callback.get('summary'), 84)}"
            spool = latest_spool_by_reply.get(str(callback.get("message_id") or ""))
            if callback.get("batch_id"):
                quality_bits.append(f"邮局批次 `{compact(callback.get('batch_id'), 34)}`")
            elif spool:
                quality_bits.append("已进邮局暂存")
            elif display != "主调度泳道":
                quality_bits.append("未见邮局批次")
        lane_messages = [m for m in messages if lane_label(m.get("from_agent"), lane_aliases) == display or lane_label(m.get("to_agent"), lane_aliases) == display]
        lane_current_garbled = [m for m in lane_messages if m in current_garbled]
        if lane_current_garbled:
            quality_bits.append(f"乱码告警 {len(lane_current_garbled)}")
        if not quality_bits:
            quality_bits.append("正常")
        lines.append(f"| {display} | {inbox_text} | {progress} | {reply_text} | {'<br>'.join(quality_bits)} |")
    lines.append("")

    if current_garbled:
        lines.append("## 当前质量告警")
        lines.append("")
        lines.append("这些记录是在乱码防线启用后出现的，不能当作有效中文回报；应打回对应泳道重新生成 UTF-8 callback。")
        lines.append("")
        lines.append("| 时间 | 记录 | 来源 | 摘要 |")
        lines.append("| --- | --- | --- | --- |")
        for msg in current_garbled[-12:][::-1]:
            source = lane_label(msg.get("from_agent"), lane_aliases)
            lines.append(f"| `{short_time(msg.get('created_at'))}` | `{compact(msg.get('message_id'), 72)}` | {source} | {compact(msg.get('summary'), 100)} |")
        lines.append("")

    if latest_batch:
        lines.append("## 最近一封邮局合并信")
        lines.append("")
        message_text = str(latest_batch.get("orchestrator_message") or "")
        if message_text:
            for line in first_lines(message_text, 18):
                lines.append(f"> {line}")
        else:
            count = len(latest_batch.get("callback_ids") or [])
            lines.append(f"> 本批共 {count} 条回报，旧记录未包含合并正文。")
        if latest_batch.get("orchestrator_message_path"):
            lines.append("")
            lines.append(f"完整批次消息：{md_link('打开合并信', latest_batch['orchestrator_message_path'])}")
        lines.append("")

    lines.append("## 泳道状态")
    lines.append("")
    lines.append("| 泳道 | 状态 | 最近回报 | 下一步建议 | 详情 |")
    lines.append("| --- | --- | --- | --- | --- |")
    for agent in agents:
        display = str(agent.get("display_name", agent.get("agent_id", "")))
        callback = latest_callback_by_lane.get(display)
        callback_text = "-"
        next_action = "-"
        if callback:
            callback_text = f"{callback.get('status', '-')}: {compact(callback.get('summary'), 72)}"
            next_action = compact(callback.get("next_recommended_action"), 72) or lane_label(
                callback.get("next_recommended_lane"), lane_aliases
            )
        detail = f"{md_link('worklog', agent.get('worklog', ''))} / {md_link('workspace', agent.get('workspace', ''))}"
        lines.append(
            f"| {display} | {status_badge(agent.get('status', ''))} | {callback_text} | {next_action} | {detail} |"
        )
    lines.append("")

    lines.append("## 近期有效产物记录")
    lines.append("")
    lines.append("这里展示给人读的完整记录：只放未乱码的有效 completion callback；历史 `????` 记录放到质量/排查区，不在这里当作正常产物。")
    lines.append("")
    if display_callbacks:
        for msg in display_callbacks[-6:][::-1]:
            source = lane_label(msg.get("from_agent"), lane_aliases)
            message_id = compact(msg.get("message_id"), 96)
            lines.append(f"### `{short_time(msg.get('created_at'))}` {source} · `{msg.get('status', '-')}`")
            lines.append("")
            lines.append(f"- 回报编号：`{message_id}`")
            if msg.get("reply_to"):
                lines.append(f"- 对应任务：`{compact(msg.get('reply_to'), 96)}`")
            lines.append("")
            append_value_block(lines, "完成摘要", msg.get("summary"))
            append_value_block(lines, "产物 / 变更文件", msg.get("changed_files"))
            append_value_block(lines, "验证证据", msg.get("evidence"))
            append_value_block(lines, "关注点", msg.get("concerns"))
            next_action = msg.get("next_recommended_action") or lane_label(msg.get("next_recommended_lane"), lane_aliases)
            append_value_block(lines, "建议动作", next_action)
    else:
        lines.append("暂无有效完成回报。")
        lines.append("")

    historical_garbled_callbacks = [m for m in callbacks if message_is_garbled(m)]
    if historical_garbled_callbacks:
        lines.append("## 历史质量污染记录")
        lines.append("")
        lines.append("这些记录保留为审计事实，但不再作为正常产物展示；如需要真实语义，应让对应泳道重发 UTF-8 callback。")
        lines.append("")
        lines.append("| 时间 | 记录 | 来源 | 处理方式 |")
        lines.append("| --- | --- | --- | --- |")
        for msg in historical_garbled_callbacks[-8:][::-1]:
            source = lane_label(msg.get("from_agent"), lane_aliases)
            lines.append(f"| `{short_time(msg.get('created_at'))}` | `{compact(msg.get('message_id'), 84)}` | {source} | 已从主产物区过滤，仅保留审计 |")
        lines.append("")

    lines.append("## 最近动态")
    lines.append("")
    lines.append("| 时间 | 动态 |")
    lines.append("| --- | --- |")
    for msg in messages[-15:][::-1]:
        lines.append(f"| `{short_time(msg.get('created_at'))}` | {human_event(msg, lane_aliases)} |")
    if not messages:
        lines.append("| - | 暂无消息 |")
    lines.append("")

    smoke_paths = [
        ("规划 smoke 产物", "agent-lanes/lanes/planning/workspace/smoke-test-plan.md"),
        ("设计 smoke 产物", "agent-lanes/lanes/design/workspace/smoke-test-empty-state-design.md"),
        ("验收 smoke 结论", "agent-lanes/lanes/review/workspace/smoke-test-review.md"),
    ]
    existing_smoke = [(label, path) for label, path in smoke_paths if (ROOT / path).exists()]
    if existing_smoke:
        lines.append("## 最近闭环产物")
        lines.append("")
        for label, path in existing_smoke:
            lines.append(f"- {md_link(label, path)}")
        lines.append("")

    lines.append("## 排查入口")
    lines.append("")
    lines.append("- 人看状态：本文件。")
    lines.append("- 机器追溯：`agent-lanes/message-log.jsonl`。")
    lines.append(f"- 推荐阅读账本：{md_link('agent-lanes/communications-readable.xlsx', communication_exports['readable_xlsx'])}。")
    lines.append("- 邮局暂存：`agent-lanes/callback-inbox/pending/`。")
    lines.append("- 邮局已投递批次：`agent-lanes/callback-inbox/delivered/`。")
    lines.append("- 刷新命令：`python agent-lanes/scripts/render_dashboard.py`。")
    lines.append("")

    dashboard = AGENT_LANES / "dashboard.md"
    dashboard.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Rendered {dashboard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
