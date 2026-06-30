# Requirements Routing Protocol

本协议定义用户在对话里提出初始需求、修改需求、临时想法和判断意见时，Agent Lanes + GOAL skills 应如何路由、落文件和回报。

## 目标

把自然语言需求变成可追踪的项目文件、泳道 worklog、message-log 和 dashboard 事件。

## 输入分类

| 输入类型 | 典型表达 | 首选泳道 | 首选 GOAL skill | 默认落地文件 |
| --- | --- | --- | --- | --- |
| 初始需求 | 我想做一个、我们需要、第一版要有 | 规划泳道 | `product-spec-builder` | `docs/01-product-spec.md` |
| 需求修改 | 改一下、先不要、增加一个、范围变了 | 规划泳道 | `product-spec-builder`, `dev-planner` | `docs/01-product-spec.md`, `docs/03-dev-plan.md` |
| UI/UX 想法 | 页面怎么设计、交互、视觉、空状态 | 设计泳道 | `design-brief-builder`, `prototype-builder` | `docs/02-design-brief.md` |
| 临时想法 | 有个想法、以后也许、先记一下 | 规划泳道 | `product-spec-builder` | `docs/01-product-spec.md` 的候选想法区或 planning worklog |
| 用户判断 | 我决定、我认为、不要这样、应该 | 主调度泳道判断后转派 | 取决于影响面 | 对应文档的决策区 |
| 实现请求 | 做出来、开始开发、改代码 | 开发泳道 | `dev-builder` | `docs/04-goal-log.md` 与代码证据 |
| 风险/权限/API/发布 | 权限、secret、付费、上线、API、provider | 守门泳道 | `gate-runner` | `docs/capability-status.json`, risk notes |
| 完成检查 | 是否完成、检查闭环、验收 | 验收泳道 | `review-runner` | `docs/05-review-report.md` |
| 流程纠正 | 这个机制不对、下次应该、沉淀规则 | 进化泳道 | `evolution-runner` | 模板、skill、hook、门禁或 evolution worklog |

## 路由规则

1. 用户提出初始需求时，主调度先派规划泳道，不直接开发。
2. 规划泳道先澄清目标、用户、范围、验收标准和非目标。
3. 如果需求包含 UI/UX、页面状态、交互、视觉或信息架构，规划完成后派设计泳道。
4. 如果需求影响代码实现，规划或设计完成后派开发泳道。
5. 如果涉及 secret、真实付费 API、权限、外部 provider、真实数据、发布上线或生产可用声明，必须派守门泳道。
6. 任何可交付结果进入下一阶段前，必要时派验收泳道做独立检查。
7. 如果用户只是临时想法，不自动进入开发；先写入候选区或 planning worklog。
8. 如果用户修改需求，先判断影响范围，再更新对应文档，最后派受影响泳道重新检查。
9. 如果用户纠正流程本身，派进化泳道，不要混在产品需求里。

## 文件归属

| 文件 | 主要责任泳道 |
| --- | --- |
| `docs/00-project-state.md` | 主调度泳道 |
| `docs/01-product-spec.md` | 规划泳道 |
| `docs/02-design-brief.md` | 设计泳道 |
| `docs/03-dev-plan.md` | 规划泳道、开发泳道 |
| `docs/04-goal-log.md` | 主调度泳道、开发泳道 |
| `docs/05-review-report.md` | 验收泳道 |
| `docs/06-release-record.md` | 验收泳道、发布相关泳道 |
| `docs/capability-status.json` | 守门泳道 |
| `docs/capability-provider-contract.md` | 守门泳道 |
| `agent-lanes/message-log.jsonl` | 主调度泳道维护，所有泳道追加 callback |

## Registry 写入范围对齐

初始化或维护运行态 `agent-lanes/agent-registry.json` 与 `agent-lanes/agent-lanes.md` 时，必须让泳道 `write_scope` 覆盖上表的 GOAL root docs 归属。最低要求：

- 规划泳道：`docs/01-product-spec.md`、`docs/03-dev-plan.md`、`agent-lanes/lanes/planning/`
- 设计泳道：`docs/02-design-brief.md`、`agent-lanes/lanes/design/`
- 守门泳道：`docs/capability-status.json`、`docs/capability-provider-contract.md`、`agent-lanes/lanes/guardian/`
- 验收泳道：`docs/05-review-report.md`、`docs/06-release-record.md`、`agent-lanes/lanes/review/`
- 进化泳道：`docs/agent-lanes-goal-integrated-template/`、`docs/agent-lanes-working-copy/`、`docs/agent-lanes/`、`docs/GOAL-Development-Base/`、`agent-lanes/lanes/evolution/`

如果需求路由任务需要写入上表文件，而 registry/泳道表未覆盖该路径，主调度应先派进化泳道修正规则或在任务中显式授权，不应让目标泳道用隐含权限写入。

## 完成回报

任何泳道完成需求相关任务后，必须回报：

```json
{
  "status": "DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED",
  "summary": "完成内容",
  "changed_files": [],
  "evidence": [],
  "concerns": [],
  "next_recommended_lane": "orchestrator | planning | design | development | guardian | review | evolution | none",
  "next_recommended_action": "建议下一步"
}
```

### Callback 去重

`agent-lanes/message-log.jsonl` 允许线程回调和 fallback 同时存在，但 dashboard、主调度和验收泳道读取时必须去重：

1. 优先按 `message_id` 去重。
2. 当同一任务出现补写 fallback、尾部补记或重复发送时，按 `reply_to + from_agent + task_type` 视为同一完成回报。
3. 去重后保留证据更完整的一条；证据同等时保留 `created_at` 最新的一条。
4. 验收报告应指出重复来源，但不得因为存在可去重 fallback 就否定已经完成的链路。

### Worklog 追加顺序

所有泳道都必须把新执行记录追加到本泳道 `worklog.md` 末尾，并使用当前时间戳从旧到新排列。不得把新任务插入到历史记录前面。验收泳道发现 worklog 不是追加顺序时，应给 `DONE_WITH_CONCERNS`，并建议进化泳道沉淀规则。

## Smoke Test

建议用两句话测试：

```text
我想做一个产品收藏功能，用户在浏览商品时可以收藏，并在侧边栏查看收藏列表。
```

然后修改：

```text
先不要做云同步，只做本地收藏；但是以后要能导出 CSV。
```

通过标准：

- `docs/01-product-spec.md` 记录初始需求和修改后的范围。
- 如涉及界面，`docs/02-design-brief.md` 记录设计影响。
- 如涉及本地存储或导出，守门泳道记录风险边界。
- 每个参与泳道写 worklog。
- 每个参与泳道写 completion callback。
- `agent-lanes/dashboard.md` 显示这次链路。

验收泳道做需求路由 smoke test 时，必须刷新并查看 dashboard：

```powershell
python agent-lanes\scripts\render_dashboard.py
```

通过标准还必须包含：

- `agent-lanes/dashboard.md` 已展示本次链路的最新完成回报。
- dashboard 中的 concerns、next lane 和关键产物入口与 `message-log.jsonl` 一致。
- 如果 dashboard 没刷新、没查看或未作为证据记录，smoke test 最高只能判为 `DONE_WITH_CONCERNS`。
