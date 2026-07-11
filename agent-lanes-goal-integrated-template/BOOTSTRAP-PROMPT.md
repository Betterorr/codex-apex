# Agent Lanes 初始化提示词

把 `docs/agent-lanes-working-copy/` 这个模板文件夹复制到另一个项目后，可以把下面这段提示词发给 Codex，让它在目标项目里初始化整套 Agent Lanes 机制。

## 使用方式

先替换占位符：

- `<TARGET_PROJECT_ROOT>`: 目标项目根目录，例如 `D:\00-antigravity\NewProject`
- `<TEMPLATE_DIR>`: 复制过去的 Agent Lanes 模板目录，例如 `D:\00-antigravity\NewProject\docs\agent-lanes`
- `<PROJECT_NAME>`: 项目名，例如 `NewProject`
- `<PRIMARY_MODULE>`: 主要代码模块目录，例如 `webapp`、`shoplens`、`src`；如果没有就写 `.`。

然后把完整提示词发给 Codex。

## 可复制提示词

```text
你现在在 Codex 里工作。请在这个项目中初始化一套 Agent Lanes 多泳道协作机制。

目标项目根目录：
<TARGET_PROJECT_ROOT>

模板目录：
<TEMPLATE_DIR>

项目名：
<PROJECT_NAME>

主要模块目录：
<PRIMARY_MODULE>

请按以下要求执行：

1. 先读取模板目录里的所有核心文件：
   - README.md
   - agent-lanes.template.md
   - agent-registry.schema.json
   - message-template.json
   - handoff-protocol.md
   - review-protocol.md
   - tooling-notes.md
   - worklog-template.md
   - completion-callback.template.json（如果存在）
   - scripts/render_dashboard.py（如果存在）
   - BOOTSTRAP-PROMPT.md（如果存在）

2. 在目标项目根目录下创建项目运行态目录 `agent-lanes/`，不要直接把模板目录当运行态使用。

3. 建立以下泳道，线程标题和显示名尽量使用中文，不要加项目名前缀：
   - `orchestrator`: 主调度泳道
   - `planning`: 规划泳道
   - `design`: 设计泳道
   - `development`: 开发泳道
   - `guardian`: 守门泳道
   - `review`: 验收泳道
   - `evolution`: 进化泳道，默认 paused

4. 在 `agent-lanes/` 下创建或补齐：
   - `agent-registry.json`
   - `agent-lanes.md`
   - `message-log.jsonl`
   - `completion-callback.template.json`
   - `dashboard.md`
   - `scripts/render_dashboard.py`
   - `lanes/<lane>/worklog.md`
   - `lanes/<lane>/workspace/`

5. 如果当前 Codex 环境有线程工具，请为这些长期泳道创建或绑定 Codex 线程：
   - 先使用 `list_projects` 找到目标项目。
   - 使用 `create_thread` 创建缺失泳道线程。
   - 使用 `set_thread_title` 把线程改名为中文泳道名。
   - 把返回的 thread id 写入 `agent-lanes/agent-registry.json` 和 `agent-lanes/agent-lanes.md`。
   - 如果线程工具不可用，不要虚构 thread id，把 `thread_id` 写成 `pending_setup`，并在 `message-log.jsonl` 里说明原因。

6. 必须建立完成回报机制：
   - 非主调度泳道完成任务后，必须先写本泳道 `worklog.md`。
   - 必须生成 completion callback JSON。
   - 泳道之间沟通默认中文优先：`summary`、`concerns`、`next_recommended_action`、worklog 正文、dashboard 展示文本和线程回复正文尽量用中文；`status`、`task_type`、`message_id`、`thread_id`、文件路径、命令、API 名、JSON key 和错误原文保留英文或原文。
   - 必须复制或生成 `agent-lanes/scripts/deliver_callback.py`、`agent-lanes/scripts/callback_post_office.py`，让非主调度泳道统一把完整 callback 投递给邮局。
   - 默认不由单泳道直接提醒主调度。泳道只调用 `deliver_callback.py`，由邮局生成完整 `thread_prompt`。
   - 邮局每轮只能生成一条 `callback_batch_ready`，其中必须包含 `thread_prompt`、`target_thread_id` 和 `outbox_path`。如果工具层需要用 `send_message_to_thread` 唤醒主调度，只能发送这一条合并后的原文消息，不得逐条发送“某泳道完成，请去收件箱看”。
   - 只有 `deliver_callback.py` 返回 `send_required=true` 时，本次完成回报才算可投递；如果返回 `send_required=false`、`spooled_waiting`，或只留下 `spooled`/`batched_log`，必须重跑投递或记录阻塞，不能短 wake。
   - 合并消息必须直接写出每条 callback 的原文摘要、证据、风险、变更文件和下一步建议；`agent-lanes/message-log.jsonl` 只作为审计备份，主调度不应为了理解回报再去翻收件箱。
   - 主调度默认直接处理邮局发来的 `thread_prompt`；只有证据冲突、疑似重复、门禁报错、需要审计或用户要求追溯时，才读取 message-log 并按 `message_id` 或 `reply_to + from_agent + task_type` 去重查证。
   - 主调度把缺少 completion callback 的任务视为未完整交接。

7. 必须建立统一查看入口：
   - 生成 `agent-lanes/dashboard.md`。
   - 从模板复制 `scripts/render_dashboard.py` 到 `agent-lanes/scripts/render_dashboard.py`；如果模板缺失，再生成等价脚本。
   - Dashboard 是人看的主控台，主视图优先展示主调度忙闲、邮局批次、泳道摘要、风险和建议动作；长 ID、脚本路径和原始 JSON 只放在排查入口。
   - `render_dashboard.py` 还必须生成完整收发账本：`agent-lanes/communications-readable.xlsx`。
   - 给用户日常查看时只指向 `communications-readable.xlsx`；机器审计或 raw 字段追溯使用 `message-log.jsonl`，不要再额外生成 CSV。
   - 在 `agent-lanes/agent-lanes.md` 写清楚：平时优先看 `agent-lanes/dashboard.md`，需要刷新时运行：
     `python agent-lanes\scripts\render_dashboard.py`

8. 默认泳道职责：
   - 主调度泳道：读状态、判断下一步、派发结构化任务、收集证据、更新泳道状态。
   - 规划泳道：产品目标、阶段范围、优先级、验收标准、任务切片。
   - 设计泳道：前端页面设计、信息架构、用户路径、交互状态、视觉规范、设计验收标准。
   - 开发泳道：实现已批准任务、运行验证、提交变更文件和证据。
   - 守门泳道：检查权限、隐私、secret、外部 API、付费调用、发布和平台风险，并把高风险事项转成可授权、可验证、可回滚的动态边界闸门。
   - 验收泳道：独立验收规划、设计、开发结果，检查目标、标准、风险和新鲜证据。
   - 进化泳道：沉淀重复失败、改进模板；没有明确复发信号前保持 paused。

9. 安全边界：
   - 不要批量删除文件或目录。
   - 不要使用 `del /s`、`rd /s`、`rmdir /s`、`Remove-Item -Recurse`、`rm -rf`。
   - 需要删除文件时，只能一次删除一个明确路径的文件。
   - 遇到 secret、真实付费 API、发布上线、生产可用声明、真实数据迁移或产品方向取舍时，先检查是否已有覆盖本次范围的用户授权；已有授权则记录依据并按守门条件推进，未授权或超出范围时才停下来问用户。

10. 初始化完成后请做校验：
   - `agent-registry.json` 能被 JSON parser 正常解析。
   - 每条泳道都有 worklog 和 workspace。
   - `dashboard.md` 能生成。
   - `communications-readable.xlsx` 能生成，且至少包含中文表头、冻结首行、筛选、合理列宽和自动换行。
   - `message-log.jsonl` 至少记录初始化事件。
   - 最终回复中列出创建的文件、已绑定的线程、未绑定的 pending_setup，以及下一步建议。

如果当前环境已经安装了 `agent-lanes-bootstrap` Skill，请优先使用该 Skill 和它的脚本；如果没有，就按模板文件和以上步骤手动初始化。
```

## 初始化后推荐第一步

初始化完成后，让主调度先跑一个低风险文档闭环测试：

```text
主调度泳道 -> 规划泳道 -> 设计泳道 -> 验收泳道
```

测试任务可以是：为某个页面或功能定义一个“空状态”提示区域，只写各泳道 workspace 和 worklog，不改代码。

验收目标：

- 主调度能派发任务。
- 目标泳道能完成并主动 callback 主调度。
- 主调度能读取 callback 并派发下一泳道。
- dashboard 能显示这次闭环。

