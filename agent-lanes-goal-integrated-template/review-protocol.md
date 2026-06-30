# Agent Lanes Review Protocol

本协议定义独立验收 Agent 如何检查多泳道产物链。验收对象可以是开发结果，也可以是规划、设计、守门、发布准备或一次需求路由 smoke test 的综合证据。

## 核心原则

提交产物的泳道不能自己做最终完成判断。各泳道可以提交 worklog、artifact 和 completion callback，验收 Agent 负责独立检查证据是否足够支持主调度进入下一步。

沟通默认中文优先；`status`、`decision`、`severity`、`message_id`、`task_type`、路径、命令、API 名和 JSON key 保留英文或原文。

## 审查顺序

1. 规格符合性：是否满足 GOAL、用户目标、范围边界和验收标准。
2. 证据新鲜度：是否有本轮或当前 GOAL 内的新鲜验证证据。
3. 多泳道一致性：规划、设计、开发、守门 callback 是否互相吻合，是否存在重复、缺失或证据冲突。
4. 行为检查：功能是否按要求运行，失败状态是否清楚；文档任务则检查落档位置、边界和可追溯性。
5. 风险检查：是否涉及 secret、权限、数据写入、付费 API、发布或生产可用声明。
6. Dashboard 证据：需求路由、机制 smoke test 或多泳道闭环验收必须刷新并检查 `agent-lanes/dashboard.md`。
7. 文档一致性：状态文档、计划、日志、产物路径是否同步。
8. 后续建议：通过、打回、继续补证据、转守门、转进化或请求用户决策。

## 审查输出格式

```json
{
  "status": "DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED",
  "review_scope": "本次验收覆盖的泳道、GOAL 或功能切片。",
  "findings": [
    {
      "severity": "P1 | P2 | P3 | P4",
      "title": "问题标题",
      "evidence": "文件、命令、产物、dashboard 或行为证据。",
      "required_fix": "必须补齐或修改的内容。"
    }
  ],
  "verified_evidence": [
    "命令结果或产物路径"
  ],
  "decision": "pass | pass_with_concerns | fail | needs_context",
  "next_action": "回派某泳道 / 请求用户 / 进入开发 / 进入发布 / 转进化沉淀规则"
}
```

## 打回条件

- 完成声明缺少证据。
- 验证失败或未运行。
- 验收标准没有覆盖。
- 旧 evidence 未复核。
- 文档和实际行为不一致。
- 高风险改动没有用户批准或独立审查。
- 需要用户产品取舍却继续假推进。

## 审查防抖

- 低风险小切片不强制完整审查。
- 普通中风险可以在同一纵向功能包末尾合并审查。
- 高风险必须立即审查。
- 同一功能包内小修只补跑失败门禁或局部复核，除非出现 P1/P2、风险升级或用户明确要求。
- 低风险 callback 可以由主调度先聚合；只有阶段边界、高风险、证据冲突、用户要求或机制 smoke test 才需要验收泳道完整介入。
- 验收发现重复失败、规则膨胀、callback 去重缺口或模板缺口时，应建议转 `evolution`，但不应把业务修复任务交给进化泳道。
