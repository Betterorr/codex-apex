# Agent Lanes + GOAL Integrated Bootstrap Prompt

把 `agent-lanes-goal-integrated-template/` 复制到另一个项目后，打开目标项目里的 Codex，把下面整段提示词发给 Codex。默认不需要填写项目名：Codex 当前工作目录就是目标项目根目录，当前文件夹名就是项目名。

## 默认值

- 模板目录：`docs/agent-lanes-goal-integrated-template`
- 项目名：从当前项目文件夹名自动推断
- 主要代码目录：默认 `.`
- 主调度线程 id：默认 `pending_setup`

## 可复制提示词

```text
你现在在 Codex 里工作。请在当前项目中初始化一套 Agent Lanes + GOAL Development Base 集成机制。

默认假设：
- 当前 Codex 工作目录就是目标项目根目录。
- 当前项目文件夹名就是项目名。
- 集成模板目录在 docs/agent-lanes-goal-integrated-template。
- 主要代码模块先使用 .。
- 主调度线程 id 先使用 pending_setup。

目标：
把模板中的多 Agent 泳道体系和 GOAL 本地 skills 装配到目标项目，让后续 Codex 可以通过自然语言自动选择 GOAL skills，并通过 Agent Lanes 进行多线程协作、派发、完成回报和 dashboard 汇总。

请按以下步骤执行：

1. 先读取模板核心文件：
   - README-GOAL-INTEGRATED.md
   - LANE-GOAL-SKILL-MAP.md
   - LANE-SKILL-HOOK-MATRIX.md
   - PERSISTENT-RUNTIME-FILES.md
   - orchestrator-recovery-template.md
   - agent-lanes.template.md
   - agent-registry.schema.json
   - message-template.json
   - completion-callback.template.json
   - handoff-protocol.md
   - review-protocol.md
   - tooling-notes.md
   - worklog-template.md
   - scripts/render_dashboard.py
   - goal-development-base/FRAMEWORK.md
   - goal-development-base/AGENTS.md
   - goal-development-base/.codex/hooks/skill-hooks.md
   - goal-development-base/docs/00-project-state.md
   - goal-development-base/docs/capability-provider-contract.md

2. 安全安装 GOAL Development Base：
   - 如果目标项目没有 `AGENTS.md`，从 `goal-development-base/AGENTS.md` 创建。
   - 如果目标项目已有 `AGENTS.md`，不要覆盖；在文件末尾追加一个 `GOAL + Agent Lanes` 集成段，保留原规则，冲突时采用更严格规则。
   - 创建或补齐 `.agents/skills/`，只复制缺失的 GOAL skill 目录。
   - 所有维护当前项目 GOAL / Agent Lanes 机制运作的 skill 都必须项目本地化，最终落在目标项目 `.agents/skills/<skill-name>/`；不要安装到 `C:\Users\...\ .codex\skills` 或其他公共 skill 目录。公共 skill、系统 skill、外部 skill 只能作为方法来源，必须改造成目标项目内本地版后才能进入默认流程。
   - 创建或补齐 `.codex/hooks/`、`.codex/gates/`、`.codex/goals/`、`.codex/signals/`、`.codex/subagents/`，只复制缺失文件。
   - 创建或补齐 `docs/00-project-state.md`、`docs/01-product-spec.md`、`docs/02-design-brief.md`、`docs/03-dev-plan.md`、`docs/04-goal-log.md`、`docs/05-review-report.md`、`docs/06-release-record.md`、`docs/capability-status.json`、`docs/capability-provider-contract.md`、`docs/CHANGELOG.md`；已有同名文件不要覆盖。
   - 创建或补齐 `scripts/` 中缺失的 GOAL 辅助脚本；已有同名脚本不要覆盖。
   - 把所有跳过、冲突或合并动作记录到 `docs/goal-agent-lanes-integration-notes.md`。

3. 初始化 Agent Lanes 运行态：
   - 在目标项目根目录创建或补齐 `agent-lanes/`，不要把模板目录直接当运行态。
   - 创建或补齐：
     - `agent-lanes/agent-registry.json`
     - `agent-lanes/agent-lanes.md`
     - `agent-lanes/message-log.jsonl`
   - `agent-lanes/completion-callback.template.json`
   - `agent-lanes/dashboard.md`
   - `agent-lanes/scripts/render_dashboard.py`
     - `agent-lanes/lanes/<lane>/worklog.md`
     - `agent-lanes/lanes/<lane>/workspace/`

4. 建立以下中文泳道，不要在线程标题前加项目名前缀：
   - `orchestrator`: 主调度泳道
   - `planning`: 规划泳道
   - `design`: 设计泳道
   - `development`: 开发泳道
   - `guardian`: 守门泳道
   - `review`: 验收泳道
   - `evolution`: 进化泳道

5. 如果当前 Codex 环境有线程工具：
   - 先用 `list_projects` 找到目标项目。
   - 为缺失泳道创建 Codex 线程。
   - 用 `set_thread_title` 设置中文泳道名。
   - 建议置顶长期核心泳道。
   - 把返回的 thread id 写入 `agent-lanes/agent-registry.json` 和 `agent-lanes/agent-lanes.md`。
   - 如果线程工具不可用，不要伪造 thread id；写 `pending_setup` 并记录原因。

6. 建立 completion-callback-required 机制：
   - 每条非主调度泳道完成主调度任务后，必须先写本泳道 `worklog.md`。
   - 必须生成 completion callback JSON，包含 `status`、`summary`、`changed_files`、`evidence`、`concerns`、`next_recommended_lane`、`next_recommended_action`。
   - 泳道之间沟通默认中文优先：`summary`、`concerns`、`next_recommended_action`、worklog 正文、dashboard 展示文本和线程回复正文尽量用中文；`status`、`task_type`、`message_id`、`thread_id`、文件路径、命令、API 名、JSON key 和错误原文保留英文或原文。
   - 必须调用 `agent-lanes/scripts/deliver_callback.py` 投递完整 callback。
   - 只有 `deliver_callback.py` 返回 `send_required=true`、`target_thread_id` 和完整 `thread_prompt` 时，才用 `send_message_to_thread` 把这一条合并原文发给主调度线程。
   - 如果返回 `send_required=false`、`spooled_waiting`，或只生成 `spooled`/`batched_log` 记录，说明回报尚未真正送达；泳道必须重跑投递或记录阻塞，不得短 wake，也不得让主调度去 message-log 自取原文。
   - `agent-lanes/message-log.jsonl` 只作为审计备份和异常查证入口。
   - `PERSISTENT-RUNTIME-FILES.md` 是线程接管和项目记忆规则：主调度线程可以替换，但 `agent-registry.json`、`message-log.jsonl`、`dashboard.md`、`communications-readable.xlsx`、各泳道 `worklog.md` / `workspace/` 和 GOAL docs 必须保持完整。
   - 当主调度线程崩溃、过长或无法提交消息时，使用 `orchestrator-recovery-template.md` 生成恢复包，新建主调度线程，更新 `agent-registry.json`，旧线程只保留作历史审计。
   - 主调度应把缺少 callback 的任务视为交接未完成。

7. 把 GOAL skills 映射到泳道职责：
   - 主调度泳道主要使用 `project-orchestrator`；目标、范围、完成标准或验证方式不清时再按需使用 `goal-creator`。
   - 主调度泳道线程崩溃、过长、无法提交消息或需要新线程接管时，使用 `lane-recovery-runner`，并按 `PERSISTENT-RUNTIME-FILES.md` 与 `orchestrator-recovery-template.md` 更新 registry、归档旧线程和写审计记录。
   - 规划泳道使用 `product-spec-builder`；跨泳道依赖、阶段顺序、联调路线、风险或验证方式不清时再按需使用 `dev-planner`、`goal-creator`。
   - 设计泳道使用 `design-brief-builder`、`prototype-builder`。
   - 开发泳道使用 `dev-builder`、`bug-fixer`、`gate-runner`。
   - 守门泳道使用 `gate-runner`、`code-reviewer`。
   - 验收泳道使用 `review-runner`、`code-reviewer`、`gate-runner`。
   - 进化泳道使用 `evolution-runner`、`goal-methodology-guide`。
   - 进化泳道在发现泳道恢复流程可复用缺口时，可以配合 `lane-recovery-runner` 把规则同步回模板、hook 和门禁。
   - 低风险任务优先使用结构化泳道派发、completion callback、聚焦门禁和 dashboard 聚合；不要机械串行运行正式 GOAL、完整 dev plan 和完整 review。

8. 建立“连续讨论协同模式”：
   - 用户在主调度线程里讨论需求、技术路线、判断、担心、偏好或临时想法时，主调度必须自动做 discussion intake，不要求用户每次手动指定泳道。
   - 将每条有实质信息的消息归为 `capture_only`、`dispatch_needed`、`confirmation_needed` 或 `clarify_needed`。
   - `capture_only` 写入合适文档或 `agent-lanes/message-log.jsonl`，不派发执行任务。
   - `dispatch_needed` 派给合适泳道；线程工具不可用时写 `pending_dispatch` fallback。
   - `confirmation_needed` 先给用户确认卡，不派发产品化开发。
   - `clarify_needed` 只问最小必要问题，并记录未决点。
   - 初始化 `.codex/hooks/skill-hooks.md` 中的“讨论场景 Hook 矩阵”：探讨需求走 `product-spec-builder`/规划泳道；探讨计划走 `dev-planner` 或 `goal-creator`/规划泳道；探讨技术方案、数据源、provider/API、模型能力时先走 `dev-planner`，涉及真实调用、secret、成本、账号或交易时走守门泳道；探讨 UI 走设计泳道；讨论实现和联调才走开发泳道；讨论验收走验收泳道；讨论机制和模板走进化泳道。
   - 派发任务必须带 `discussion_source` 或 `source_message_id`，让 completion callback 能追溯到触发讨论。

9. 建立 `Sketch Plan Loop / 骨架计划循环`：
   - 当用户说“完成度、太慢、整体推进、计划、项目还差什么、骨架、先打通、全链路”，或最近 3-5 个 GOAL 都集中在同一局部能力时，主调度不得直接进入开发，应先判断是否触发 Skeleton Plan Refresh。
   - 通用产品骨架链路为：用户输入 -> 数据/素材进入 -> 处理/生成 -> 人工审核 -> 组合/编排 -> 输出/渲染 -> 报告/交付；目标项目可在 `docs/03-dev-plan.md` 中替换成项目专属骨架。
   - `dev-planner` 必须维护 `Skeleton Pass`、`Real Pass`、`Quality Pass`、`Production Pass`，并给出接下来 3-6 个最高价值薄纵向切片。
   - `dev-builder` 只执行骨架计划里的下一刀；执行前说明补哪条骨架环节，执行后说明下一个非同能力骨架节点。
   - 小切片跑聚焦门禁，阶段边界做合并审查，高风险才完整审查。

10. 建立统一查看入口：
   - 生成 `agent-lanes/dashboard.md`。
   - 从模板复制 `scripts/render_dashboard.py` 到 `agent-lanes/scripts/render_dashboard.py`；如果模板缺失，再生成等价脚本。
   - 在 `agent-lanes/agent-lanes.md` 写清楚：平时优先打开 `agent-lanes/dashboard.md` 看全局状态。
   - 需要刷新时运行：`python agent-lanes\scripts\render_dashboard.py`
   - `render_dashboard.py` 还必须生成完整收发账本：`agent-lanes/communications-readable.xlsx`。
   - 给用户日常查看时只指向 `communications-readable.xlsx`；机器审计或 raw 字段追溯使用 `message-log.jsonl`，不要再额外生成 CSV。

11. 安全规则：
   - 禁止批量删除文件或目录。
   - 不要使用 `del /s`、`rd /s`、`rmdir /s`、`Remove-Item -Recurse`、`rm -rf`。
   - 需要删除文件时，只能一次删除一个明确路径的文件。
   - 遇到 secret、真实付费 API、真实数据迁移、发布上线、生产可用声明、产品方向取舍时，停止并问用户。

12. 验证：
   - `agent-lanes/agent-registry.json` 能被 JSON parser 解析。
   - `agent-lanes/message-log.jsonl` 每行都能被 JSON parser 解析。
   - 每条泳道都有 worklog 和 workspace。
   - GOAL skill 目录存在于 `.agents/skills/`。
   - `.codex/hooks/skill-hooks.md` 存在。
   - `.codex/hooks/skill-hooks.md` 包含 `lane-recovery-runner` 触发词，`.codex/gates/skill-mechanism-check.ps1` 会检查该 Skill。
   - `agent-lanes/dashboard.md` 能生成。
   - `communications-readable.xlsx` 能生成，且至少包含中文表头、冻结首行、筛选、合理列宽和自动换行。

13. 初始化后跑一个最小闭环烟雾测试：
   - 主调度泳道派发一个低风险文档任务给规划泳道。
   - 如该任务同时涉及 UI 或权限风险，可并行派发给设计泳道或守门泳道。
   - 各泳道完成后 callback 主调度。
   - 主调度合并 callback 和 message-log，确认是否需要补派开发/验收；低风险且证据一致时可记录为阶段边界再合并验收。
   - 刷新 dashboard，确认 message-log 和 worklog 都有记录。

最终回复请列出：
- 已安装或补齐的 GOAL files。
- 已创建或补齐的 Agent Lanes files。
- 已绑定的线程 id。
- 仍是 `pending_setup` 的泳道。
- smoke test 是否完成。
- 需要用户手动处理的冲突或风险。
```
