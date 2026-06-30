# Agent Lanes Handoff Protocol

本协议定义 Agent 之间如何交接任务，避免靠聊天转述造成上下文丢失。

## 交接类型

| Type | From | To | 用途 |
| --- | --- | --- | --- |
| `planning_to_development` | planning | development | 把需求、目标和验收标准交给开发 |
| `development_to_review` | development | review | 把实现结果和证据交给验收 |
| `review_to_development` | review | development | 验收不通过时打回修复 |
| `review_to_orchestrator` | review | orchestrator | 验收结论回到总调度 |
| `orchestrator_to_specialist` | orchestrator | any specialist lane | 派发专项任务 |
| `signal_to_evolution` | any lane | evolution | 把可复发流程问题交给自进化 |

## 交接必须包含

- `message_id`
- 来源 Agent 和目标 Agent
- 当前 GOAL 或任务名
- 背景文件路径
- 目标结果
- 范围边界
- 验收标准
- 风险等级
- 允许写入范围
- 必需证据
- 预期回报状态

## 语言规则

Agent 之间沟通默认使用中文，方便用户直接阅读。

- 任务目标、范围、验收标准、`summary`、`concerns`、`next_recommended_action`、worklog 正文、dashboard 展示文本和线程回复正文：尽量用中文。
- `status`、`task_type`、`message_id`、`reply_to`、`thread_id`、`lane id`、`file path`、命令、代码标识、API 名、JSON key、错误原文：保留英文或原文。
- 不好翻译或翻译后容易失真的技术名词可以保留英文，但要放在中文语境里说明。

## 自动推进流程

```text
orchestrator
  -> read project state
  -> read agent-registry.json
  -> read agent-lanes.md
  -> choose lane
  -> send structured message
  -> append message-log.jsonl
  -> read target result
  -> route by status
```

## 状态路由

| Reply status | Orchestrator action |
| --- | --- |
| `DONE` | 派给 review，或进入下一阶段 |
| `DONE_WITH_CONCERNS` | 记录风险，必要时派 review |
| `NEEDS_CONTEXT` | 停止自动推进，向用户请求决策、样本或授权 |
| `BLOCKED` | 判断是否派 bug-fixer/planning/evolution，或请求用户介入 |

## 完成回报协议

目标 Agent 完成任务时，必须主动回报主调度 Agent。完成任务但不回报，视为交接不完整。

标准结束顺序：

1. 写入本泳道 `worklog.md`。
2. 生成完成回报 JSON。
3. 调用 `agent-lanes/scripts/deliver_callback.py` 把完整 callback 投递到回报邮局；邮局负责追加到 `message-log.jsonl` 作为审计备份，并生成 `thread_prompt`、`target_thread_id` 和 `outbox_path`。
4. 默认不由单泳道提醒主调度。只有 `deliver_callback.py` 返回 `send_required=true` 且带完整 `thread_prompt` 时，泳道才把这一条合并后的原文消息发送给主调度；不得逐条发送“某泳道完成，请去收件箱看”。若返回 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log`，视为未完成投递，必须重跑或记录阻塞。
5. 最终回复中保留 `status`、`evidence`、`next_recommended_lane`。

完成回报必须包含：

- `message_id`
- `reply_to`
- `from_agent`
- `to_agent`
- `status`
- `summary`
- `changed_files`
- `evidence`
- `concerns`
- `next_recommended_lane`
- `next_recommended_action`
- `created_at`

主调度默认直接处理邮局发来的 `thread_prompt` 原文消息，不再先去 `message-log.jsonl` 收件箱读取 callback。`message-log.jsonl` 只作为审计备份；只有证据冲突、疑似重复、门禁报错、需要审计或用户要求追溯时，才按 `message_id` 或 `reply_to + from_agent + task_type` 去重查证。

## 不允许的交接

- 没有验收标准的开发请求。
- 没有证据的完成声明。
- 让开发 Agent 自己做最终验收。
- 高风险、secret、付费 API、发布任务绕过用户批准。
- 多个 Agent 同时写同一文件范围但没有合并者。

## message-log.jsonl 示例

```jsonl
{"message_id":"msg-20260623-001","from_agent":"orchestrator","to_agent":"development","task_type":"implementation_request","related_goal":"p1-login","status":"sent","created_at":"2026-06-23T14:00:00+08:00"}
{"message_id":"msg-20260623-001","from_agent":"development","to_agent":"orchestrator","status":"DONE","evidence":["npm test: passed"],"created_at":"2026-06-23T14:30:00+08:00"}
```

