# Agent Lanes + GOAL Integrated Template

这是一份新的集成模板包，用来把两套机制一起带到其他 Codex 项目里：

- Agent Lanes：多线程、多泳道、多智能体协作、派发、回报、总控台。
- GOAL Development Base：单个泳道内部如何澄清、计划、开发、验证、审查、发布和进化。

拿到这份目录的人，可以把整个目录复制到目标项目，然后把 `BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md` 里的提示词发给 Codex，让 Codex 自动装配运行态。

## 包内结构

```text
agent-lanes-goal-integrated-template/
  README-GOAL-INTEGRATED.md
  BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md
  LANE-GOAL-SKILL-MAP.md
  LANE-SKILL-HOOK-MATRIX.md
  PERSISTENT-RUNTIME-FILES.md
  orchestrator-recovery-template.md
  agent-lanes.template.md
  agent-registry.schema.json
  message-template.json
  completion-callback.template.json
  handoff-protocol.md
  review-protocol.md
  tooling-notes.md
  worklog-template.md
  scripts/
    render_dashboard.py
  goal-development-base/
    AGENTS.md
    FRAMEWORK.md
    .agents/skills/
    .codex/hooks/
    .codex/gates/
    docs/
    scripts/
```

## 三层落地

模板目录不是运行态。初始化后，目标项目里应该出现三层：

```text
目标项目/
  AGENTS.md                         # 项目规则，合并 GOAL 和 Agent Lanes 规则
  .agents/skills/                   # GOAL 本地 skills
  .codex/hooks/                     # 自然语言 skill 路由
  .codex/gates/                     # 门禁脚本与说明
  docs/                             # GOAL 项目记忆文档
  agent-lanes/                      # Agent Lanes 运行态
    agent-registry.json
    agent-lanes.md
    message-log.jsonl
    completion-callback.template.json
    dashboard.md
    communications-readable.xlsx
    scripts/render_dashboard.py
    lanes/<lane>/worklog.md
    lanes/<lane>/workspace/
```

## 安全合并原则

初始化时应只新增或补齐，不要粗暴覆盖目标项目已有文件。

- 如果目标项目没有 `AGENTS.md`，可以复制 `goal-development-base/AGENTS.md` 后追加 Agent Lanes 规则。
- 如果目标项目已有 `AGENTS.md`，保留原内容，追加一个 `GOAL + Agent Lanes` 集成段；遇到冲突时采用更严格规则，并记录到 `docs/goal-agent-lanes-integration-notes.md`。
- `.agents/skills/` 只复制缺失的 skill 目录；同名 skill 已存在时不要覆盖，记录冲突。
- `.codex/`、`docs/`、`scripts/` 只补齐缺失文件；同名文件已存在时不要覆盖，记录冲突。
- 不要批量删除文件或目录。

## 推荐使用方式

1. 把本目录复制到目标项目，例如：

```text
<TARGET_PROJECT_ROOT>/docs/agent-lanes-goal-integrated-template/
```

2. 打开 `BOOTSTRAP-PROMPT-GOAL-INTEGRATED.md`。
3. 替换占位符。
4. 把完整提示词发给 Codex。
5. 初始化完成后，优先查看：

```text
agent-lanes/dashboard.md
agent-lanes/communications-readable.xlsx
docs/00-project-state.md
docs/04-goal-log.md
```

`agent-lanes/dashboard.md` 负责快速看状态；完整收发记录只生成并优先打开 `agent-lanes/communications-readable.xlsx`。机器审计和 raw 字段追溯使用 `message-log.jsonl`，不再额外导出 CSV。

## 讨论式协作默认能力

初始化后的主调度不只响应“继续”。当用户在主调度线程里持续讨论需求、技术路线、判断、担心、偏好或临时想法时，主调度必须自动做讨论 intake，而不是要求用户手动调用某条泳道。

- 背景、偏好、观察或未稳定想法：标为 `capture_only`，写入合适文档或 message-log。
- 已形成稳定小任务：标为 `dispatch_needed`，派给合适泳道，或写 `pending_dispatch` fallback。
- 涉及路线锁定、产品取舍、真实外部调用、付费、secret、账号、持久写入、券商/交易、生产声明或重型框架采用：标为 `confirmation_needed`，先给用户确认卡。
- 信息不足且容易跑偏：标为 `clarify_needed`，只问最小必要问题。

派发任务必须带 `discussion_source` 或 `source_message_id`，让 completion callback 能追溯到是哪次讨论触发。

## 一句话原则

用 Agent Lanes 管多线程组织协作，用 GOAL skills 管每条泳道内部执行纪律；用 message-log 和 worklog 留痕，用 dashboard 让人一眼看见系统是否闭环，用 readable xlsx 账本保存完整收发摘要、产物、证据、关注点和建议动作。

## 多泳道下的 GOAL 使用方式

这份模板内置的是多泳道协作版 GOAL Skill：

- 主调度可以用结构化泳道任务替代低风险场景下的正式 `goal-creator`。
- `dev-planner` 只在跨泳道依赖、阶段顺序、联调路线、风险或回滚不清时使用。
- 规划、设计、守门无强依赖时可以并行派发，再由主调度合并 completion callback。
- `review-runner` 和 `gate-runner` 按风险聚合证据与聚焦门禁，不逐条完整审查低风险 callback。
- 同一 capability 连续推进 2-3 个 GOAL 后必须做 Capability Exit Check，够用就切回产品纵向闭环。

## 当前默认泳道

集成模板默认落地 7 条长期泳道：

- `orchestrator`：主调度泳道。
- `planning`：规划泳道。
- `design`：设计泳道。
- `development`：开发泳道。
- `guardian`：守门泳道。
- `review`：验收泳道。
- `evolution`：进化泳道，默认可以 `paused`，有明确复发信号或模板沉淀任务时再启用。

这 7 条泳道是当前推荐完整形态；极简项目仍可先只启用主调度、开发、验收，但模板应保留全部定义，避免后续扩展时重新发明通讯和回报机制。

## 沟通语言

泳道之间默认中文优先，方便用户直接看懂 dashboard、message-log 和 worklog。`summary`、`concerns`、`next_recommended_action`、任务说明和线程回复正文尽量写中文；`status`、`task_type`、`message_id`、`thread_id`、路径、命令、API 名、JSON key 和错误原文保留英文或原文。
