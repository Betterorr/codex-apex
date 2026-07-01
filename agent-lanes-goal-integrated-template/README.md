# Agent Lanes 多智能体协作法

Agent Lanes 是一套通用的 Codex 多 Agent 项目协作方法：把长期项目拆成多个职责泳道，并通过 Agent 注册表、线程消息、工作日志、产物空间、自动门禁和独立验收协同推进。

## 快速部署入口

把本模板复制到其他项目时，优先使用：

- `DEPLOY-PROMPT.md`：复制给目标项目 Codex 的一键部署提示词。
- `TEMPLATE-MANIFEST.md`：模板材料清单和部署验收 checklist。
- `scripts/deploy_agent_lanes_template.py`：保守部署辅助脚本，默认不覆盖已有运行态文件。
- `callback-inbox/post-office-policy.json`：邮局直投策略模板。
- `scripts/deliver_callback.py`、`scripts/callback_post_office.py`、`scripts/check_callback_post_office.py`：完成回报统一投递和门禁脚本。
- `goal-development-base/.agents/skills/`：随包交付的 GOAL 本地 skill，其中已吸收 `requirements-traceability`、`interface-design` + `frontend-design`、`github-research`、系统化调试方法和泳道恢复方法为项目适配版 runner。

机制 skill 必须项目本地化：复制到目标项目 `.agents/skills/` 后使用。公共 skill 目录只能作为方法来源或验证器来源，不作为目标项目机制 skill 的最终安装位置。

邮局回报机制是当前默认通信方式：非主调度泳道完成后不直接发短 wake，而是调用 `deliver_callback.py`。当脚本输出 `send_required=true` 时，泳道只把返回的 `thread_prompt` 发送给主调度线程一次。若脚本输出 `send_required=false`、`spooled_waiting`，或只留下 `spooled`/`batched_log`，说明回报尚未真正送达，必须重跑投递或记录阻塞。`message-log.jsonl` 只作为审计备份；主调度收到 `【邮局合并回报】` 后直接处理原文，不先要求去收件箱读取完整 callback。

`thread_prompt` 应完整展开 completion callback 的主要字段，不用“另有 X 项，见审计日志”代替正文。审计日志只用于追溯，不承担默认阅读入口。

它适合和 GOAL Skills 一起使用：

```text
GOAL Skills = 单个 Agent 内部的项目操作系统
Agent Lanes = 多个长期 Agent 之间的组织结构和通讯协议
```

## 目标

让用户只需要说一次“继续”或启动一次自动心跳，就能由主调度 Agent 自主判断下一步，派发给合适的 Agent Lane，并在完成后读取结果、验收、打回或进入下一阶段。

## 推荐结构

```text
docs/agent-lanes/
  README.md
  DEPLOY-PROMPT.md
  TEMPLATE-MANIFEST.md
  agent-registry.schema.json
  agent-lanes.template.md
  message-template.json
  completion-callback.template.json
  worklog-template.md
  handoff-protocol.md
  review-protocol.md
  LANE-GOAL-SKILL-MAP.md
  LANE-SKILL-HOOK-MATRIX.md
  PERSISTENT-RUNTIME-FILES.md
  orchestrator-recovery-template.md
  SKILL-RECOMMENDATIONS.md
  tooling-notes.md
  goal-development-base/.agents/skills/
  callback-inbox/post-office-policy.json
  scripts/render_dashboard.py
  scripts/deploy_agent_lanes_template.py
  scripts/deliver_callback.py
  scripts/callback_post_office.py
  scripts/check_callback_post_office.py
```

项目真正启用后，建议复制为：

```text
agent-lanes/
  agent-registry.json
  agent-lanes.md
  message-log.jsonl
  completion-callback.template.json
  dashboard.md
  scripts/render_dashboard.py
  scripts/deploy_agent_lanes_template.py
  scripts/deliver_callback.py
  scripts/callback_post_office.py
  scripts/check_callback_post_office.py
  callback-inbox/
    post-office-policy.json
    pending/
    delivered/
    outbox/
  lanes/
    orchestrator/
      worklog.md
      workspace/
    planning/
      worklog.md
      workspace/
    design/
      worklog.md
      workspace/
    development/
      worklog.md
      workspace/
    guardian/
      worklog.md
      workspace/
    review/
      worklog.md
      workspace/
    evolution/
      worklog.md
      workspace/
```

## 最小可用团队

先从 3 个长期 Agent Lane 开始：

| Lane | 角色 | 主要职责 | 不做什么 |
| --- | --- | --- | --- |
| `orchestrator` | 主调度 Agent | 读状态、判风险、派任务、收结果、更新项目状态 | 不长期代替专项 Lane 做所有事 |
| `development` | 开发执行 Agent | 按任务实现、修复、运行验证、提交证据 | 不擅自改产品方向 |
| `review` | 验收审查 Agent | 按目标和验收标准独立检查、打回或通过 | 不替开发辩护，不直接扩大实现 |

项目复杂后再增加：

- `planning`: 产品规划、需求、阶段目标。
- `design`: 设计、原型、交互。
- `guardian`: 权限、隐私、secret、外部 API、付费调用、真实写入和发布风险。
- `release`: 打包、发布、交付。
- `evolution`: 失败信号、规则沉淀、Skill 进化。

如果使用 `agent-lanes-goal-integrated-template/`，推荐直接保留 7 条默认泳道：主调度、规划、设计、开发、守门、验收、进化。极简项目可以只先绑定其中 3 条线程，但不要从模板里删除其他泳道定义。

## 通讯方式

Agent 之间不要随口转述，使用结构化消息：

```text
orchestrator -> 查 agent-registry.json
orchestrator -> 找目标 lane 的 current_session/thread_id
orchestrator -> send_message_to_thread 投递 message-template.json
orchestrator -> 记录 message-log.jsonl
目标 Agent -> 执行并写 worklog/artifact
目标 Agent -> 调用 deliver_callback.py 生成完整 thread_prompt
目标 Agent -> send_message_to_thread 只发送 thread_prompt 一次
orchestrator -> 直接处理【邮局合并回报】原文，必要时才审计 message-log
orchestrator -> 派给 review 或打回 development
```

默认沟通语言是中文优先。任务目标、范围、验收标准、`summary`、`concerns`、`next_recommended_action`、worklog 正文、dashboard 展示文本和线程回复正文尽量用中文；`status`、`task_type`、`message_id`、`thread_id`、路径、命令、API 名、JSON key 和错误原文保留英文或原文。

## 脱手自动推进

最稳的方式是“中心调度型”，不要一开始做完全点对点自治。

```text
用户输入“继续”
  -> orchestrator 读取项目状态、registry、agent-lanes、message-log、各 lane worklog
  -> 判断最短纵向闭环
  -> 选择 lane
  -> 投递结构化任务
  -> 读取结果
  -> 验收或打回
  -> 更新状态
  -> 进入下一轮
```

如果环境支持自动化，可以建立 heartbeat：

```text
每 30-60 分钟唤醒 orchestrator：
  读取所有 Lane 状态
  选择一个安全的下一步
  执行或派发
  遇到 NEEDS_CONTEXT / 高风险 / 费用 / secret / 发布审批时停止并问用户
```

## 标准状态词

每个 Agent 回报必须使用一个状态词：

| 状态 | 含义 | 主调度动作 |
| --- | --- | --- |
| `DONE` | 完成标准满足，有证据 | 进入验收、发布或下一阶段 |
| `DONE_WITH_CONCERNS` | 主闭环完成，但有非阻塞风险 | 记录风险，必要时派审查 |
| `NEEDS_CONTEXT` | 缺少用户决策、输入样本、授权或产品取舍 | 停下来问用户 |
| `BLOCKED` | 已确认存在阻塞，本地无法继续 | 改派修复/规划，或请求用户介入 |

## 可自动推进的任务

- 本地代码实现。
- 文档更新。
- fixture 测试。
- 本地 smoke。
- 只读 evidence。
- 前后端局部联调。
- 独立审查。
- 自进化规则补丁。

## 必须停下来问用户的任务

- 真实付费 API 调用。
- secret、key、账号权限。
- 删除、覆盖或迁移真实数据。
- 发布上线。
- 客户可用或生产可用声明。
- 大范围架构改变。
- 产品方向取舍。

## 与 GOAL Skills 的分工

| 层 | 负责什么 |
| --- | --- |
| GOAL | 当前目标、范围、完成标准、验证证据 |
| Skill | 单个 Agent 内部选择需求、设计、开发、门禁、审查等能力 |
| Agent Lane | 长期职责、上下文隔离、并行协作 |
| Registry | 身份、thread id、lane、权限、状态 |
| Message Log | 交接记录、责任链、可追溯性 |
| Worklog | 每个 Lane 的执行历史和产物入口 |
| Gate / Review | 程序证据和独立验收 |

## 启用步骤

1. 复制本目录到目标项目。
2. 按 `agent-registry.schema.json` 创建 `agent-registry.json`。
3. 按 `agent-lanes.template.md` 创建 `agent-lanes.md`。
4. 创建 `message-log.jsonl`。
5. 为每个 Lane 创建 `worklog.md` 和 `workspace/`。
6. 复制或生成 `completion-callback.template.json` 和 `scripts/render_dashboard.py`。
7. 用 `tooling-notes.md` 检查当前 Codex 环境可用工具。
8. 先跑一个最小闭环：规划 -> 设计或开发 -> 守门或验收 -> 主调度合并。
9. 刷新 `agent-lanes/dashboard.md`，确认 message-log、worklog 和 callback 都能被统一看到。
10. 再考虑 heartbeat 自动推进。

## 一句话原则

```text
用 Registry 管身份，用 Lanes 管职责，用 Message 管交接，用 Worklog 管追溯，用 GOAL 管目标，用 Gate 管证据，用 Review 管验收，用 Evolution 管教训沉淀。
```
## 模板进化同步规则

模板包也跟着进化：当前项目运行态里的邮局、dashboard、门禁、泳道协议、GOAL 基座或 Skill 规则一旦因为真实失败或用户纠正而升级，进化泳道必须同步检查并更新本模板包的同名脚本和说明文件。新项目复制模板时，不应该继承旧通信规则、旧 dashboard 视图或旧门禁缺口。

同步完成后至少要跑脚本编译、模板部署 smoke、邮局门禁、dashboard 刷新和 JSON/JSONL 解析；如果只改了运行态而没有同步模板，完成回报必须标 `DONE_WITH_CONCERNS` 并写明遗漏原因。

Dashboard 是给用户看的主控台：应优先完整展示近期有效产物记录，包括完成摘要、产物 / 变更文件、验证证据、关注点和建议动作。不要把这些内容压缩成只适合机器看的短表格；历史乱码和无效回报应单独进入质量/污染区。
## 完整收发 Excel 账本

Markdown dashboard 负责让用户快速看懂当前状态；完整收发沟通记录只生成 `agent-lanes/communications-readable.xlsx`。xlsx 每条消息一行，保留长摘要、证据、产物、关注点、建议动作、邮局正文和原始 JSON，并带冻结首行、筛选、列宽、自动换行和质量状态颜色，适合用户直接打开阅读。

机器审计仍以 `agent-lanes/message-log.jsonl` 为源；不要再额外导出 CSV，避免用户看到多个表格入口后混淆。
