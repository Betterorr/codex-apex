# 持久化运行态文件说明

Agent Lanes 不能依赖某个 Codex 线程的临时上下文来保存项目记忆。线程可能过长、崩溃、被归档或需要替换；项目真正的连续记忆必须写入目标项目里的持久化文件。

一句话原则：

```text
线程可以换，运行态不能丢。
新主调度接管时，先读持久化文件，而不是试图继承旧线程的全部思考过程。
```

## 核心文件

| 文件 | 作用 | 谁主要写入 | 谁主要读取 |
| --- | --- | --- | --- |
| `agent-lanes/agent-registry.json` | 当前泳道注册表，记录每条泳道的 `thread_id`、职责、读写范围、worklog 和 workspace。主调度线程替换时必须更新这里。 | 主调度泳道、进化泳道 | 邮局、dashboard、所有泳道 |
| `agent-lanes/agent-lanes.md` | 人类可读的泳道职责、沟通规则、邮局规则、忙闲状态和 dashboard 说明。 | 主调度泳道、进化泳道 | 所有泳道 |
| `agent-lanes/message-log.jsonl` | 全局审计账本，记录派发、callback、邮局批次、线程替换、异常和状态信号。它是审计备份，不是主调度默认收件箱。 | 所有泳道、邮局、主调度 | dashboard、审计、恢复流程 |
| `agent-lanes/dashboard.md` | 给用户看的当前状态主控台，展示泳道进度、近期产物、风险和建议动作。 | `render_dashboard.py` | 用户、主调度 |
| `agent-lanes/communications-readable.xlsx` | 给用户看的完整收发账本，一行一条消息，保留长摘要、证据、关注点、建议动作、邮局正文和 raw JSON。 | `render_dashboard.py` | 用户 |
| `agent-lanes/lanes/<lane>/worklog.md` | 每条泳道自己的连续工作日志。完成任务前必须追加。 | 对应泳道 | 主调度、验收、恢复流程 |
| `agent-lanes/lanes/<lane>/workspace/` | 每条泳道的中间产物、completion callback、恢复包、审查材料和临时证据。 | 对应泳道 | 主调度、验收、恢复流程 |
| `agent-lanes/callback-inbox/` | 回报邮局暂存、合批、outbox 和 delivered 记录。 | `deliver_callback.py` / `callback_post_office.py` | 邮局、主调度、审计 |

## GOAL 文档记忆

| 文件 | 作用 |
| --- | --- |
| `docs/00-project-state.md` | 项目当前状态、最新决策、当前阶段和重要恢复事件。 |
| `docs/01-product-spec.md` | 产品需求、范围、用户价值和明确不做事项。 |
| `docs/02-design-brief.md` | UI/UX、信息架构、页面状态和设计验收标准。 |
| `docs/03-dev-plan.md` | 阶段计划、最高价值下一刀、任务切片和依赖关系。 |
| `docs/04-goal-log.md` | GOAL 推进历史、验证证据和阶段性结论。 |
| `docs/05-review-report.md` | 独立验收、风险复核和完成标准核对。 |
| `docs/06-release-record.md` | 发布或交付记录。 |
| `docs/capability-status.json` | 机器可读能力 registry，记录能力成熟度、证据、授权、预算、复跑命令和下游消费路径。 |
| `docs/capability-provider-contract.md` | 外部 provider/API/model/CLI 的适配边界、授权规则和风险说明。 |

## 主调度接管时必须读取

新主调度线程或恢复后的主调度线程，至少先读：

- `AGENTS.md`
- `agent-lanes/agent-registry.json`
- `agent-lanes/agent-lanes.md`
- `agent-lanes/dashboard.md`
- `agent-lanes/message-log.jsonl` 的最近有效记录
- `docs/00-project-state.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/capability-status.json`
- `agent-lanes/lanes/orchestrator/worklog.md`
- 如存在恢复包：`agent-lanes/lanes/orchestrator/workspace/orchestrator-recovery-*.md`

接管时要分批读取，不要把所有文件一次性塞进新线程。推荐顺序：

1. 先用一句短提示做健康检查，只要求回复“健康检查通过”。
2. 再读 `AGENTS.md`、`agent-registry.json`、`dashboard.md` 和恢复包摘要。
3. 确认新线程稳定后，再读取 `worklog.md`、GOAL docs 和 `message-log.jsonl` 最近有效记录。
4. 只有在证据冲突、疑似重复、门禁报错、恢复接管或用户要求追溯时，才深入读取完整 `message-log.jsonl` 和 `callback-inbox/`。

主调度只在证据冲突、疑似重复、门禁报错、恢复接管或用户要求追溯时，深入读取 `message-log.jsonl` 和 `callback-inbox/`。正常 callback 处理应直接基于邮局发来的完整 `thread_prompt`。

## 线程替换规则

当主调度线程出现以下情况时，可以换线程：

- 提交消息失败，例如 `failed to start turn: internal error; agent loop died unexpectedly`。
- 线程历史过长，恢复/启动下一轮不稳定。
- 长时间无法响应，但本地运行态文件仍完整。
- 用户明确要求换主调度。

替换时必须：

1. 新开主调度候选线程，并先发送瘦身健康检查提示词。
2. 连续轻量健康检查通过后，再让新线程分批读取持久化运行态文件。
3. 健康检查通过前，不要把未处理的邮局合并回报、长恢复包原文或全量 message-log 投递给新线程。
4. 更新 `agent-lanes/agent-registry.json` 中 `orchestrator.thread_id`。
5. 在 `agent-lanes/message-log.jsonl` 追加一条 `task_type=orchestrator_thread_replacement` 的审计记录。
6. 在 `agent-lanes/lanes/orchestrator/worklog.md` 追加接管记录。
7. 刷新 `agent-lanes/dashboard.md` 和 `communications-readable.xlsx`。
8. 旧线程保留作历史审计，不再作为投递目标。
9. 如果候选线程也崩溃，把它标记为二次故障线程并归档，再创建更轻的候选线程；不要反复向坏候选线程投递长上下文。

## 部署后检查

模板部署后至少确认：

- `agent-lanes/agent-registry.json` 可 JSON 解析，且每条泳道有 `thread_id`、`worklog`、`workspace`。
- `agent-lanes/message-log.jsonl` 可逐行 JSON 解析。
- 每条泳道都有 `worklog.md` 和 `workspace/`。
- `python agent-lanes\scripts\render_dashboard.py` 可以生成 `dashboard.md` 和 `communications-readable.xlsx`。
- 邮局脚本能写入 `callback-inbox/` 并生成完整 `thread_prompt`。
- 新主调度或恢复主调度知道：项目记忆以这些文件为准，而不是以旧线程上下文为准。
