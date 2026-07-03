# 主调度泳道恢复模板

当主调度线程崩溃、过长、无法提交消息或需要替换时，使用本模板创建恢复包。建议保存到：

```text
agent-lanes/lanes/orchestrator/workspace/orchestrator-recovery-<YYYYMMDD>-<reason>.md
```

## 诊断记录

- 旧主调度线程 id：`<OLD_ORCHESTRATOR_THREAD_ID>`
- 新主调度线程 id：`<NEW_ORCHESTRATOR_THREAD_ID_OR_PENDING>`
- 触发时间：`<ISO8601_LOCAL_TIME>`
- 触发错误：`<ERROR_TEXT>`
- 未处理批次或任务：`<PENDING_BATCH_OR_MESSAGE_ID>`
- 关键证据：
  - `<EVIDENCE_1>`
  - `<EVIDENCE_2>`
  - `<EVIDENCE_3>`

判断结论：

```text
<说明是线程运行时问题、消息编码问题、邮局投递问题，还是业务任务问题。>
```

## 新主调度接管提示词

先把下面这段“瘦身健康检查提示词”发给新主调度候选线程。只有候选线程能稳定回复后，才发送后续接管提示词。

```text
你现在是 <PROJECT_NAME> 项目的主调度泳道候选线程。

这是一次恢复健康检查，不要开始调度，不要读取大量历史。

请只确认三件事：
1. 你知道自己将接管主调度泳道。
2. 旧主调度线程 `<OLD_ORCHESTRATOR_THREAD_ID>` 因 `<ERROR_TEXT>` 不再作为投递目标。
3. 下一步你会先读持久化文件，而不是依赖旧线程临时上下文。

只回复：健康检查通过
```

健康检查通过后，再发送下面这段接管提示词。若候选线程在健康检查阶段报 `agent loop died unexpectedly`、`failed to start turn` 或 `Error submitting message`，把它标记为二次故障线程并归档，不要继续投递长提示。

```text
你现在接管 <PROJECT_NAME> 项目的主调度泳道。

这是恢复接管，不是新项目初始化。旧主调度线程 `<OLD_ORCHESTRATOR_THREAD_ID>` 出现 `<ERROR_TEXT>`，已不建议继续作为投递目标。

请先阅读：
- AGENTS.md
- agent-lanes/agent-registry.json
- agent-lanes/agent-lanes.md
- agent-lanes/dashboard.md
- agent-lanes/message-log.jsonl 的最近有效记录，不要全量读取
- docs/00-project-state.md
- docs/03-dev-plan.md
- docs/04-goal-log.md
- docs/capability-status.json
- agent-lanes/lanes/orchestrator/worklog.md
- agent-lanes/lanes/orchestrator/workspace/orchestrator-recovery-<YYYYMMDD>-<reason>.md

如果这些文件较长，请分批读取。先读 registry、dashboard 和恢复包摘要，确认可用后再逐步读取 worklog、GOAL docs 和最近 message-log。

请直接处理这条旧主调度未完成的事项：

<PASTE_PENDING_CALLBACK_BATCH_OR_TASK_HERE>

接管后请执行：

1. 写入 `orchestrator_state=busy` 到 `agent-lanes/message-log.jsonl`，标明正在恢复 `<PENDING_BATCH_OR_MESSAGE_ID>`。
2. 基于持久化文件和上面的待处理事项做判断，不要依赖旧线程临时上下文。
3. 如果待处理事项是 completion callback，直接处理邮局合并原文；只有证据冲突、疑似重复、门禁报错或用户要求追溯时，才打开 message-log 查证。
4. 更新必要的项目状态文件，例如 `docs/00-project-state.md`、`docs/03-dev-plan.md`、`docs/04-goal-log.md`、`docs/capability-status.json`。
5. 更新 `agent-lanes/lanes/orchestrator/worklog.md`。
6. 追加 `agent-lanes/message-log.jsonl` 审计记录。
7. 运行 `python agent-lanes\scripts\render_dashboard.py`。
8. 完成稳定检查点后写入 `orchestrator_state=idle`。

最终回复至少包含：
- status
- changed_files
- evidence
- concerns
- next_recommended_lane
- next_recommended_action
```

## Registry 替换步骤

新线程创建并通过至少两次轻量健康检查后，更新 `agent-lanes/agent-registry.json`：

```json
{
  "agent_id": "orchestrator",
  "thread_id": "<NEW_ORCHESTRATOR_THREAD_ID>",
  "notes": "Replaced old orchestrator thread <OLD_ORCHESTRATOR_THREAD_ID> on <ISO8601_LOCAL_TIME>; old thread kept for historical audit."
}
```

不要删除旧线程记录中的历史信息；旧线程 id 应保留在 `notes`、worklog 或恢复包里。

如果第一次新建的候选线程也失败，应把它写入恢复包和审计记录，标记为“历史归档-二次故障”，然后用更短的健康检查提示词创建下一候选线程。不要把失败候选线程登记为当前投递目标。

## message-log 审计记录模板

```json
{
  "created_at": "<ISO8601_LOCAL_TIME>",
  "message_id": "msg-<YYYYMMDD>-orchestrator-thread-replacement",
  "from_agent": "evolution_lane",
  "to_agent": "orchestrator_lane",
  "task_type": "orchestrator_thread_replacement",
  "status": "DONE",
  "summary": "Created and registered a replacement orchestrator lane thread. The old orchestrator thread is kept for historical audit only.",
  "old_orchestrator_thread_id": "<OLD_ORCHESTRATOR_THREAD_ID>",
  "new_orchestrator_thread_id": "<NEW_ORCHESTRATOR_THREAD_ID>",
  "changed_files": [
    "agent-lanes/agent-registry.json",
    "agent-lanes/message-log.jsonl",
    "agent-lanes/lanes/orchestrator/worklog.md"
  ],
  "evidence": [
    "new thread created",
    "agent-registry.json orchestrator.thread_id updated",
    "recovery prompt sent"
  ],
  "concerns": [
    "Do not keep sending new work to the old orchestrator thread."
  ],
  "next_recommended_lane": "orchestrator",
  "next_recommended_action": "Replacement orchestrator should process the pending batch or task, then resume normal scheduling."
}
```

## 完成检查

- `agent-lanes/agent-registry.json` 指向新主调度线程。
- 新主调度线程已通过至少两次轻量健康检查。
- `agent-lanes/message-log.jsonl` 可解析，替换记录唯一。
- 旧主调度线程不再作为投递目标。
- `agent-lanes/dashboard.md` 已刷新。
- 未处理 callback 或任务已经交给新主调度。
- 如果门禁仍为 `WARN`，必须区分历史迁移 warning 和当前替换问题。
