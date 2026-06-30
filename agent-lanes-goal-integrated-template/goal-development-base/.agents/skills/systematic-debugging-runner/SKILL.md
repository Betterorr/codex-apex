---
name: systematic-debugging-runner
description: 当用户提到 bug、报错、测试失败、构建失败、UI 行为异常、信息流断了、callback 没送到、门禁异常、数据接线不对、修了还坏、不要猜、先查根因、root cause、系统化调试时，使用这个 Skill 在当前 GOAL/Agent Lanes 体系内执行根因优先的调试流程；输出必须回写 docs/04-goal-log.md、相关泳道 worklog、docs/05-review-report.md 或 artifacts，不得只给口头猜测。
---

# 系统化调试执行器

目标：吸收 `systematic-debugging` 的根因优先方法，适配 GOAL、Agent Lanes、post office、dashboard 和 capability registry。

## 核心契约

- 项目文档中文优先：复现过程、根因、排除假设、修复说明和回归结论写中文；命令、路径、错误原文、JSON key、message_id 保留原文。
- 调试必须先复现和追数据流，再最小修复；不能靠猜测叠补丁。
- 如果根因是流程、模板或门禁缺口，记录为 signal 或交给进化泳道，不在本 Skill 内顺手做大范围机制改造。

## 自然语言触发词

当用户或主调度提到 bug、报错、测试失败、构建失败、UI 行为异常、信息流断了、callback 没送到、门禁异常、数据接线不对、修了还坏、不要猜、先查根因、root cause、系统化调试时，优先使用本 Skill。

## 固定输入

根据问题类型读取：

- `docs/00-project-state.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/05-review-report.md`
- `docs/capability-status.json`
- `agent-lanes/message-log.jsonl`
- `agent-lanes/dashboard.md`
- 相关泳道 `worklog.md`
- 报错命令、日志、测试输出、artifact、浏览器截图或复现步骤。

## 输出位置

- 调试过程和结论：`docs/04-goal-log.md` 或当前泳道 `worklog.md`
- 验收/风险结论：`docs/05-review-report.md`
- 复现脚本、最小样本、截图、trace：`artifacts/<slice>/` 或泳道 workspace
- 如果发现流程性问题，再交给进化泳道沉淀规则；不要在调试 skill 里顺手大改模板。

## 调试四步

1. 复现和读错误：记录命令、输入、实际输出、期望输出、是否稳定复现。
2. 数据流追踪：从失败点向上追踪调用、文件、message_id、artifact、状态字段或 DOM 状态，找出坏值从哪里来。
3. 单一假设验证：一次只验证一个根因假设，使用最小命令或最小改动。
4. 修复和回归：只修根因，不顺手重构；修后复跑同一失败路径和必要聚焦门禁。

## 特别规则

- Agent Lanes 信息流问题优先按 `message_id`、`reply_to`、`batch_id`、`thread_prompt`、`send_required`、`outbox_path` 追踪，不要只看文件尾。
- post office 问题必须区分 `message-log` 审计备份和真实 `thread_prompt` 投递。
- capability 问题必须核对 `docs/capability-status.json`，不能用 fixture 或 mock 推进真实 provider maturity。
- 前端问题要用真实浏览器、截图或 DOM 状态证明，不只看 JS 语法。
- 外部 API、secret、账号、付费、交易、远程写入或 scheduler 问题先停到守门边界，不擅自真实调用。

## 打回条件

- 未复现就提出修复方案。
- 同时改多个可能根因，无法判断哪个生效。
- 修复后没有复跑同一失败路径。
- 只解释“应该好了”，没有命令、截图、日志或 artifact。
- 把一次性业务判断沉淀成长流程规则，或把流程性问题留在口头总结里。

## 完成门禁

完成时必须给出：

- 复现方式和失败证据。
- 根因结论和排除过的假设。
- 修复文件或无需修复的理由。
- 回归验证命令和结果。
- 是否需要进化泳道沉淀规则。
