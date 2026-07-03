# Agent Lanes 模板包一键部署提示词

把本模板目录复制到目标项目后，打开目标项目里的 Codex，粘贴下面这段提示词即可。默认不需要填写项目名：Codex 当前工作目录就是目标项目根目录，当前文件夹名就是项目名。

## 默认路径

- 模板目录：`docs/agent-lanes-goal-integrated-template`
- 项目名：从当前项目文件夹名自动推断
- 主要模块目录：默认 `.`
- 主调度线程 id：默认 `pending_setup`

如果你的模板目录不是默认路径，只需要在提示词里告诉 Codex 实际模板目录，并让它给脚本补 `--template-dir`。

## 可复制提示词

```text
你现在在 Codex 里工作。请把 Agent Lanes + GOAL 开发基座模板部署到当前项目。

默认假设：
- 当前 Codex 工作目录就是目标项目根目录。
- 当前项目文件夹名就是项目名。
- 模板目录在 docs/agent-lanes-goal-integrated-template。
- 主要模块目录先使用 .。
- 主调度线程 id 先使用 pending_setup。

请严格按以下步骤执行，不要改业务代码，不要删除文件。

1. 读取模板核心文件：
   - README.md
   - TEMPLATE-MANIFEST.md
   - VERSION-HISTORY.md
   - agent-lanes.template.md
   - agent-registry.schema.json
   - completion-callback.template.json
   - handoff-protocol.md
   - LANE-GOAL-SKILL-MAP.md
   - LANE-SKILL-HOOK-MATRIX.md
   - PERSISTENT-RUNTIME-FILES.md
   - orchestrator-recovery-template.md
   - BOOTSTRAP-PROMPT.md
   - scripts/render_dashboard.py
   - scripts/deploy_agent_lanes_template.py
   - scripts/deliver_callback.py
   - scripts/callback_post_office.py
   - scripts/check_callback_post_office.py
    - callback-inbox/post-office-policy.json
    - goal-development-base/AGENTS.md
    - goal-development-base/FRAMEWORK.md
    - goal-development-base/.agents/skills/
    - goal-development-base/.codex/hooks/skill-hooks.md
    - SKILL-RECOMMENDATIONS.md

2. 优先使用部署辅助脚本做保守初始化：
   `python .\docs\agent-lanes-goal-integrated-template\scripts\deploy_agent_lanes_template.py`
   脚本会默认使用当前工作目录作为目标项目根目录、当前文件夹名作为项目名、`.` 作为主要模块目录、`pending_setup` 作为主调度线程 id，并且默认不覆盖已有运行态文件。运行后读取 `agent-lanes/INSTALL-REPORT.md`，确认没有缺失模板文件。

3. 如果不能运行部署脚本，再手动创建或补齐运行态目录：
   - `agent-lanes/`
   - `agent-lanes/scripts/`
   - `agent-lanes/callback-inbox/pending/`
   - `agent-lanes/callback-inbox/delivered/`
   - `agent-lanes/callback-inbox/outbox/`
   - `agent-lanes/lanes/orchestrator/workspace/`
   - `agent-lanes/lanes/planning/workspace/`
   - `agent-lanes/lanes/design/workspace/`
   - `agent-lanes/lanes/development/workspace/`
   - `agent-lanes/lanes/guardian/workspace/`
   - `agent-lanes/lanes/review/workspace/`
   - `agent-lanes/lanes/evolution/workspace/`

4. 从模板复制这些文件到运行态：
   - `agent-lanes.template.md` -> `agent-lanes/agent-lanes.md`
   - `completion-callback.template.json` -> `agent-lanes/completion-callback.template.json`
   - `scripts/render_dashboard.py` -> `agent-lanes/scripts/render_dashboard.py`
   - `scripts/deploy_agent_lanes_template.py` -> `agent-lanes/scripts/deploy_agent_lanes_template.py`
   - `scripts/deliver_callback.py` -> `agent-lanes/scripts/deliver_callback.py`
   - `scripts/callback_post_office.py` -> `agent-lanes/scripts/callback_post_office.py`
   - `scripts/check_callback_post_office.py` -> `agent-lanes/scripts/check_callback_post_office.py`
   - `callback-inbox/post-office-policy.json` -> `agent-lanes/callback-inbox/post-office-policy.json`
   - `goal-development-base/.agents/skills/` -> `.agents/skills/`（只补缺失 skill，不覆盖目标项目已有定制 skill）
   - 所有维护当前项目 GOAL / Agent Lanes 机制运作的 skill 都必须项目本地化，最终落在目标项目 `.agents/skills/<skill-name>/`；不要安装到 `C:\Users\...\ .codex\skills` 或其他公共 skill 目录。公共 skill、系统 skill、外部 skill 只能作为方法来源，必须改造成目标项目内本地版后才能进入默认流程。
   - `goal-development-base/.codex/hooks/skill-hooks.md` -> `.codex/hooks/skill-hooks.md`（若目标项目已有 hook，合并新增规则，不覆盖旧规则）

   本模板已吸收 5 个本地化增强 skill：`requirements-traceability-runner`、`frontend-quality-runner`、`open-source-research-runner`、`systematic-debugging-runner`、`lane-recovery-runner`。其中前端只默认吸收 `interface-design` 和 `frontend-design` 两个来源，泳道线程恢复默认走 `lane-recovery-runner`。恢复时先用瘦身提示和连续健康检查确认新线程可用，再切换 registry；如果候选线程也出现 `agent loop died unexpectedly`，必须标记为二次故障并重新创建更轻候选线程。部署后优先使用这些目标项目内 `.agents/skills/` 适配版；原始 `requirements-traceability`、`github-research`、`systematic-debugging` 只作为方法来源或临时深挖工具，不能让产物绕开 `docs/*`、泳道 workspace、worklog 和 dashboard。

5. 初始化 `agent-lanes/callback-inbox/post-office-policy.json`：
   - 把 `enabled_at` 从 `<SET_ON_INSTALL_ISO8601>` 改为当前本地 ISO 时间。
   - 保持 `mode=advisory`。
   - 暂时不要开启 strict，除非用户明确要求。

6. 创建或更新 `agent-lanes/agent-registry.json`，至少包含 7 条泳道：
   - orchestrator / 主调度泳道
   - planning / 规划泳道
   - design / 设计泳道
   - development / 开发泳道
   - guardian / 守门泳道
   - review / 验收泳道
   - evolution / 进化泳道
   写入每条泳道的 `agent_id`、`display_name`、`thread_id`、`status`、`worklog`、`workspace`、`write_scope`、`read_scope`。
   如果没有真实线程 id，写 `pending_setup`，不要虚构。

7. 为每条泳道创建 `worklog.md`：
   - 使用模板 `worklog-template.md` 的格式。
   - 记录初始化时间、职责、线程 id 状态和写入范围。

8. 创建或保留 `agent-lanes/message-log.jsonl`：
   - 如果不存在，创建空文件。
   - 追加一条 `agent_lanes_bootstrap` 事件，记录模板来源、安装时间、主调度线程 id 和已复制脚本。

9. 建立邮局直投规则，必须写进 `agent-lanes/agent-lanes.md`：
   - 非主调度泳道完成后调用 `agent-lanes/scripts/deliver_callback.py`。
   - `message-log.jsonl` 只作为审计备份，不是主调度默认阅读入口。
   - `deliver_callback.py` 输出 `send_required=true` 时，泳道必须只调用一次 `send_message_to_thread(target_thread_id, thread_prompt)`。
   - `deliver_callback.py` 输出 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log` 记录时，本次回报尚未真正送到主调度；泳道必须重跑投递或记录阻塞，不得短 wake，也不得让主调度去 message-log 自取原文。
   - 邮局不得把 pending callback 移出暂存，除非同一批次已经生成 `thread_prompt`、`target_thread_id` 和 `outbox_path`。
   - 主调度收到 `【邮局合并回报】` 后直接处理，不要先去 message-log 收件箱读取原文。
   - 只有证据冲突、疑似重复、门禁报错、需要审计或用户要求追溯时，才打开 message-log 查证。
   - 项目记忆必须落到持久化运行态文件：`agent-registry.json`、`message-log.jsonl`、`dashboard.md`、`communications-readable.xlsx`、各泳道 `worklog.md` / `workspace/` 和 GOAL docs；主调度线程可替换，运行态文件不可丢。
   - 如果主调度线程过长、崩溃或出现 `failed to start turn`，按 `orchestrator-recovery-template.md` 新建主调度候选线程；先发瘦身健康检查提示，连续轻量检查通过后再更新 `agent-registry.json`，不要一开始就投递全量历史或长 callback。

10. 复制 GOAL 开发基座：
   - 若目标项目还没有 `AGENTS.md`，从 `goal-development-base/AGENTS.md` 复制。
   - 若已有 `AGENTS.md`，只追加 Agent Lanes 集成、邮局直投、文件安全、中文优先和完成证据规则，不覆盖用户已有规则。
   - 复制或合并 `goal-development-base/FRAMEWORK.md` 到 `docs/GOAL-Development-Base/FRAMEWORK.md` 或目标项目约定位置。
   - 复制 `goal-development-base/scripts/check-agent-lanes-post-office.ps1` 到 `scripts/check-agent-lanes-post-office.ps1`。

11. 刷新 dashboard：
   - 运行 `python agent-lanes\scripts\render_dashboard.py`
   - 确认生成 `agent-lanes/dashboard.md`
   - 同时确认生成 `agent-lanes/communications-readable.xlsx`。
   - `dashboard.md` 是给人快速看状态；完整收发记录只打开 `communications-readable.xlsx`，机器审计或 raw 字段追溯使用 `message-log.jsonl`，不要再额外生成 CSV。

12. 跑部署自检：
   - `python -m py_compile agent-lanes\scripts\render_dashboard.py agent-lanes\scripts\deliver_callback.py agent-lanes\scripts\callback_post_office.py agent-lanes\scripts\check_callback_post_office.py`
   - `powershell -ExecutionPolicy Bypass -File scripts\check-agent-lanes-post-office.ps1`
   - 用 Python 解析 `agent-lanes/agent-registry.json`
   - 用 Python 逐行解析 `agent-lanes/message-log.jsonl`
   - 确认 `communications-readable.xlsx` 存在且包含中文表头、完整摘要、证据、关注点、建议动作、冻结首行、筛选、列宽和自动换行。

13. 做最小邮局 smoke：
   - 在 `agent-lanes/lanes/evolution/workspace/` 写一个测试 callback JSON。
   - 运行：
     `python agent-lanes\scripts\deliver_callback.py --callback-file agent-lanes\lanes\evolution\workspace\<test-callback>.json --no-start`
   - 如果输出 `send_required=true`，确认 stdout 里有 `target_thread_id` 和 `thread_prompt`。
   - 不要发送短 wake。真实发送时只发送 `thread_prompt`。

14. 最终回复必须包含：
   - `status`
   - `created_files`
   - `changed_files`
   - `evidence`
   - `concerns`
   - `next_recommended_action`

重要约束：
- 不要批量删除文件或目录。
- 不要使用 `del /s`、`rd /s`、`rmdir /s`、`Remove-Item -Recurse`、`rm -rf`。
- 不要改业务代码。
- 不要虚构 thread id。
- 不要把短 wake 当成完成回报。
- `message-log.jsonl` 是审计备份；主调度默认直接处理邮局 `thread_prompt`。
```

## 部署后第一条测试任务

初始化完成后，可以让主调度派一个低风险 smoke：

```text
请主调度派规划泳道写一个只改 workspace/worklog 的空状态需求小测试，再由规划泳道通过 deliver_callback.py 走邮局直投 thread_prompt 回报。不要改业务代码。
```
