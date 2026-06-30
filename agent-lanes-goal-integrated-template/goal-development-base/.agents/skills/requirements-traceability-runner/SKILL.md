---
name: requirements-traceability-runner
description: 当用户提到需求追踪、需求到设计/代码/测试映射、traceability matrix、需求覆盖、验收覆盖、需求漂移、阶段验收前检查、发布前需求闭环、哪个需求有没有实现或测试时，使用这个 Skill 在当前 GOAL/Agent Lanes 文档体系内建立或审查需求追踪矩阵；输出必须落到 docs/05-review-report.md 或对应泳道 workspace，不得另起独立需求文档体系。
---

# 需求追踪执行器

目标：吸收 `requirements-traceability` 的方法，但适配当前项目固定文档流，确保需求、设计、实现、测试和证据能互相追踪。

## 核心契约

- 项目文档中文优先：需求描述、缺口、建议动作和验收结论写中文；路径、命令、JSON key、状态枚举和错误原文保留原文。
- 只在现有 GOAL/Agent Lanes 文档体系内建立追踪关系，不新建并行需求体系。
- 如果发现可复用的流程缺口，记录为 signal 或交给进化泳道，不在本 Skill 内顺手扩大机制改造。

## 自然语言触发词

当用户或主调度提到需求追踪、需求到设计/代码/测试映射、traceability matrix、需求覆盖、验收覆盖、需求漂移、阶段验收前检查、发布前需求闭环、哪个需求有没有实现或测试时，优先使用本 Skill。

## 固定输入

优先读取：

- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/05-review-report.md`
- `docs/capability-status.json`
- `agent-lanes/dashboard.md`
- 当前任务 callback、变更文件列表、验证命令和证据路径。

如涉及 provider、真实数据、外部 API、模型、账号、secret、付费或生产风险，还要读取：

- `docs/capability-provider-contract.md`
- 相关 provider card 或 capability evidence。

## 输出位置

不要创建新的顶层需求追踪文档。默认写入：

- 阶段验收或发布前：追加到 `docs/05-review-report.md`
- 单泳道中间产物：`agent-lanes/lanes/<lane>/workspace/traceability-<message_id>.md`
- 若需求 ID 本身缺失，只能在 `docs/01-product-spec.md` 提出最小补 ID 建议；未经任务授权不要大规模重写需求文档。

## 追踪矩阵格式

使用中文正文，保留路径、命令、ID、JSON key 原文：

```markdown
## 需求追踪矩阵：<任务/切片>

| Req ID | 需求 | 设计引用 | 实现引用 | 验证/测试 | 证据 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-001 | ... | docs/02-design-brief.md | src/... | 命令/脚本 | artifact/docs 路径 | PASS/缺口/待确认 |

### 阻塞缺口
- ...

### 非阻塞关注
- ...

### 建议动作
- ...
```

## 工作规则

- 不要猜需求。没有明确 ID 时，使用 `INFERRED-001` 临时标记，并写明需要规划泳道确认。
- 每条 in-scope 需求至少要映射到一个设计、实现或验证证据；缺任一关键环节就列为缺口。
- 对用户可见能力，必须确认入口、输入、输出、失败状态、复跑命令和可查看结果位置。
- 对 fixture-only 能力，必须明确不能证明真实 provider、真实生产数据、真实交易、真实执行或生产可用。
- 对外部 API、secret、付费、账号、交易、scheduler 和生产声明，必须转守门泳道确认授权边界。
- 只追踪当前任务或当前阶段范围，不要把全项目所有需求都展开成大表。

## 打回条件

- 需求在 `docs/01-product-spec.md` 中找不到，且 callback 又没有稳定需求描述。
- 实现和设计无法对应，或者证据只证明文件存在、不证明行为。
- 声称完成用户可见闭环，但缺少入口、输入、输出、失败状态、复跑命令或结果位置。
- 用 mock、stub、fixture 证明真实 provider/API/model maturity。
- 新增追踪产物没有写回 `docs/05-review-report.md` 或泳道 workspace，导致主调度和验收读不到。

## 完成门禁

完成时必须给出：

- 追踪范围。
- 需求追踪矩阵。
- 阻塞缺口和非阻塞关注。
- 已核对证据路径和命令。
- 下一步建议泳道。
