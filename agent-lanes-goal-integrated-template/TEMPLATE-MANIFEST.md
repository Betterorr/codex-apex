# Agent Lanes + GOAL 模板包材料清单

本文件用于把模板包复制到其他项目时做核对。新项目部署时，优先阅读 `DEPLOY-PROMPT.md`，再按本清单确认材料是否齐全。

## 一键部署入口

- `DEPLOY-PROMPT.md`：复制给目标项目 Codex 的部署提示词。
- `scripts/deploy_agent_lanes_template.py`：可选部署辅助脚本，默认只创建缺失文件，不覆盖已有运行态。
- `README.md`：Agent Lanes 基础说明和启用步骤。
- `README-GOAL-INTEGRATED.md`：Agent Lanes 与 GOAL 开发基座集成说明。
- `BOOTSTRAP-PROMPT.md` / `BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md`：初始化泳道时使用的启动提示词。

## 运行态模板

- `agent-lanes.template.md`：目标项目的 `agent-lanes/agent-lanes.md` 模板。
- `agent-registry.schema.json`：`agent-lanes/agent-registry.json` 的结构校验参考。
- `message-template.json`：主调度派发任务消息模板。
- `completion-callback.template.json`：泳道完成回报模板。
- `worklog-template.md`：每条泳道的 `worklog.md` 初始模板。
- `handoff-protocol.md`：泳道交接协议。
- `review-protocol.md`：验收泳道协议。
- `requirements-routing-protocol.md`：需求路由 smoke test 协议。
- `LANE-GOAL-SKILL-MAP.md`：泳道与 GOAL Skill 的职责映射。
- `LANE-SKILL-HOOK-MATRIX.md`：每条泳道对应的 skill、自然语言 hook 落位和部署后检查总表。
- `EVOLUTION-NOTES.md`：进化泳道可复用规则沉淀入口。
- `SKILL-RECOMMENDATIONS.md`：质量优先 skill 候选池和外部 skill 引入规则。
- `tooling-notes.md`：工具可用性和部署注意事项。
- 已吸收并随包交付的本地化增强 skill：`requirements-traceability-runner`、`frontend-quality-runner`、`open-source-research-runner`、`systematic-debugging-runner`；其中 `frontend-quality-runner` 只吸收 `interface-design` 和 `frontend-design` 两个前端设计来源。新项目默认优先使用这些适配版，不直接把原始外部 skill 作为默认入口。

## 邮局回报机制

- `scripts/deliver_callback.py`：非主调度泳道完成后统一调用的投递入口。
- `scripts/callback_post_office.py`：合并 pending callback，生成给主调度的完整 `thread_prompt`。
- `scripts/check_callback_post_office.py`：检查短 wake、绕过邮局和历史异常。
- `callback-inbox/post-office-policy.json`：目标项目部署时复制到 `agent-lanes/callback-inbox/post-office-policy.json` 的策略模板。

核心规则：

- `message-log.jsonl` 只作为审计备份，不是主调度默认收件箱。
- `deliver_callback.py` 输出 `send_required=true` 时，泳道只发送一次返回的 `thread_prompt`。
- `deliver_callback.py` 输出 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log` 记录时，不算完成回报已送达；泳道必须重跑投递或记录阻塞，不能发送短 wake，也不能要求主调度去 message-log 自取原文。
- 邮局不得把 pending callback 移出暂存，除非同一批次已经生成可发送的完整 `thread_prompt`、`target_thread_id` 和 `outbox_path`。
- 主调度收到 `【邮局合并回报】` 后直接处理原文，不先要求“去 message-log 读取完整 callback”。
- `thread_prompt` 必须完整展开 `summary`、`changed_files`、`evidence`、`concerns`、`next_recommended_action` 等回报字段，不用“另有 X 项，见审计日志”代替正文。
- 只有证据冲突、疑似重复、门禁报错、需要审计或用户要求追溯时，才打开 `message-log.jsonl` 查证。
- `legacy_direct_bypass_message_ids` 和 `legacy_stranded_delivery_message_ids` 只能用于已解释的历史迁移期记录。新项目默认保持空数组；未来新 completion callback 绕过邮局或只停在 `spooled`/`batched_log` 仍必须报警或打回。
- `deliver_callback.py` 会拒绝明显乱码的 callback，例如连续 `???` 或全问号 agent 名；`legacy_garbled_payload_message_ids` 只能记录已发送的历史乱码污染，新项目默认保持空数组。

## Dashboard 与门禁

- `scripts/render_dashboard.py`：刷新 `agent-lanes/dashboard.md`。
- `goal-development-base/scripts/check-agent-lanes-post-office.ps1`：邮局机制门禁。
- `goal-development-base/AGENTS.md`：可合并到目标项目根目录的协作规则。
- `goal-development-base/FRAMEWORK.md`：GOAL 开发基座方法说明。
- `goal-development-base/.agents/skills/`：目标项目可选复制的本地 Skill 基座，包含 GOAL 基础 skill 和本地化增强 skill。
- `goal-development-base/.codex/`：目标项目可选复制的 hook / gate 基座。

## 部署验收

模板部署到新项目后，至少要完成这些检查：

1. 可选运行 `python .\docs\agent-lanes-goal-integrated-template\scripts\deploy_agent_lanes_template.py`。脚本默认使用当前工作目录作为目标项目根目录、当前文件夹名作为项目名、`.` 作为主要模块目录、`pending_setup` 作为主调度线程 id；非默认模板路径才需要补 `--template-dir`。
2. `python agent-lanes\scripts\render_dashboard.py`
3. `python -m py_compile agent-lanes\scripts\render_dashboard.py agent-lanes\scripts\deliver_callback.py agent-lanes\scripts\callback_post_office.py agent-lanes\scripts\check_callback_post_office.py`
4. `powershell -ExecutionPolicy Bypass -File scripts\check-agent-lanes-post-office.ps1`
5. Python 解析 `agent-lanes/agent-registry.json`。
6. Python 逐行解析 `agent-lanes/message-log.jsonl`。
7. 用 `deliver_callback.py --callback-file ... --no-start` 做一次最小邮局 smoke，确认输出含 `send_required`、`target_thread_id` 和 `thread_prompt`。

## 不做事项

- 不要改业务代码。
- 不要删除文件或目录。
- 不要虚构 `thread_id`。
- 不要发送短 wake 代替完整 `thread_prompt`。
- 不要把 `message-log.jsonl` 重新升级成主调度默认收件箱。
- `TEMPLATE-MANIFEST.md` includes the current template material checklist.

## 模板进化同步规则

运行态 `agent-lanes/`、本地 Skill、hook、gate 或 GOAL 基座发生机制进化时，不能只改当前项目。进化泳道必须同步检查并更新本模板包的对应材料，让模板复制到其他项目后继承同一套有效规则。

必须同步的常见位置：

- 邮局、投递、dashboard、门禁脚本：同步到 `scripts/` 下同名文件。
- 泳道职责、回报规则、dashboard 阅读规则：同步到 `agent-lanes.template.md`、`handoff-protocol.md`、`review-protocol.md` 和 `requirements-routing-protocol.md`。
- 一键部署和新项目启动说明：同步到 `DEPLOY-PROMPT.md`、`BOOTSTRAP-PROMPT.md`、`BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md`。
- 模板材料说明：同步到 `README.md`、`README-GOAL-INTEGRATED.md`、`TEMPLATE-MANIFEST.md` 和 `EVOLUTION-NOTES.md`。
- GOAL 基座规则或 Skill 变化：同步到 `goal-development-base/` 下对应文件。

同步后至少验证：脚本 hash 或内容一致性、`py_compile`、模板部署 smoke、邮局门禁、dashboard 刷新，以及 JSON/JSONL 可解析。

## Dashboard 阅读规则

`agent-lanes/dashboard.md` 是给用户看的主控台，不是机器日志压缩表。模板内 `scripts/render_dashboard.py` 必须保留“近期有效产物记录”这类人读区块，完整展示每条有效 completion callback 的完成摘要、产物 / 变更文件、验证证据、关注点和建议动作。

历史乱码、短 wake、绕过邮局或无法信任的记录不应混入正常产物区；它们应进入质量告警或历史污染区，只作为审计事实保留。
## 完整收发 Excel 账本

`agent-lanes/dashboard.md` 负责快速浏览，但 Markdown 预览器可能截断长文本、表格换行或链接展示。模板应同时生成 `agent-lanes/communications-readable.xlsx` 作为完整收发账本。

xlsx 每行对应一条 `message-log.jsonl` 记录，至少保留：时间、message_id、reply_to、from_agent、to_agent、通信类型、task_type、status、质量状态、summary、changed_files、evidence、concerns、next_recommended_action、邮局正文和 raw_json。

用户需要完整追溯时优先打开 xlsx；机器审计仍以 `message-log.jsonl` 为源。

为改善表格可读性，模板应同时生成：

- `agent-lanes/communications-readable.xlsx`：唯一用户表格入口，带冻结首行、筛选、列宽、自动换行和质量状态颜色。
