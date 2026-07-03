---
name: lane-recovery-runner
description: 当用户提到泳道坏了、主调度坏了、线程崩了、agent loop died、failed to start turn、Error submitting message、旧泳道过长、需要新建泳道替换、注册替换、归档旧线程、恢复接管、替换 thread_id、重建主调度或其他 Agent Lane 线程恢复时，使用此 Skill 按持久化运行态文件完成新线程创建、registry 更新、旧线程归档、恢复提示词投递和审计记录。
---

# 泳道恢复执行器

目标：当某条 Agent Lane 线程不可用、过长、崩溃或无法提交消息时，用新线程接管这条泳道，并让项目运行态继续保持可追溯、可恢复、可审计。

## 自然语言触发词

用户提到这些词或表达时，优先使用本 Skill：

- 泳道坏了、主调度坏了、线程崩了、线程死了、旧线程太长。
- `failed to start turn`、`agent loop died unexpectedly`、`Error submitting message`。
- 新建一个泳道替换、注册替换、接管旧泳道、恢复接管。
- 替换 `thread_id`、更新 registry、旧线程归档、新线程沿用原名字。
- 主调度恢复、orchestrator recovery、坏掉的 lane recovery。

## 输入

先读取：

- `AGENTS.md`
- `agent-lanes/agent-registry.json`
- `agent-lanes/agent-lanes.md`
- `agent-lanes/dashboard.md`
- `agent-lanes/message-log.jsonl` 最近记录
- `agent-lanes/lanes/<lane>/worklog.md`
- `agent-lanes/lanes/<lane>/workspace/`
- `docs/00-project-state.md`
- `docs/03-dev-plan.md`
- `docs/04-goal-log.md`
- `docs/capability-status.json`
- 如存在：`docs/agent-lanes-goal-integrated-template/PERSISTENT-RUNTIME-FILES.md`
- 如存在：`docs/agent-lanes-goal-integrated-template/orchestrator-recovery-template.md`

## 核心契约

## 项目文档中文优先

更新 `docs/*.md`、`agent-lanes/**/*.md`、泳道 worklog、dashboard、恢复包、审计说明和模板说明时，默认写中文。`status`、`task_type`、`message_id`、`thread_id`、路径、命令、API 名、JSON key 和错误原文保留英文或原文。

- 线程可以换，运行态不能丢。
- 新线程接管的是持久化运行态和未完成任务，不是旧线程的全部临时思考。
- `agent-lanes/agent-registry.json` 是当前投递目标的来源；替换线程必须更新这里。
- `agent-lanes/message-log.jsonl` 是审计账本；替换动作必须追加记录。
- 旧线程保留作历史审计，不删除。
- 不要因为线程坏了就重做业务产物；先恢复调度，再决定下一步。
- 恢复接管必须先瘦身再加上下文：新线程第一条提示只做身份、故障、少量必读文件和一条短健康检查，不要一次性塞入全部历史、长 dashboard、长 message-log 或大段待处理批次。
- 新线程创建成功不等于恢复完成；至少要完成连续轻量健康检查，确认它能接收短消息、读取最小持久化文件并稳定回复后，才能把 registry 正式切到新线程。
- 如果新线程在健康检查或后台投递中再次出现 `agent loop died unexpectedly` / `failed to start turn` / `Error submitting message`，应把它标记为二次故障线程并归档，再创建更轻的候选线程；不要反复给同一个坏线程补发长提示。
- 如果这次恢复暴露出可复用流程缺口，记录 signal 或派 `evolution-runner` 沉淀规则；不要在恢复流程里顺手改业务代码。

## 恢复流程

1. 确认故障对象：
   - 明确坏掉的是哪条泳道：`orchestrator`、`planning`、`design`、`development`、`guardian`、`review` 或 `evolution`。
   - 记录旧 `thread_id`、错误文本、未完成的 `message_id` / `batch_id` / 用户请求。

2. 生成恢复包：
   - 写入 `agent-lanes/lanes/<lane>/workspace/lane-recovery-<YYYYMMDD>-<message-or-reason>.md`。
   - 如果是主调度泳道，可使用 `orchestrator-recovery-template.md` 的结构。
   - 恢复包必须包含：旧线程 id、新线程 id 或 pending、错误、未完成事项、接管提示词、下一步检查。

3. 新建或确认新线程：
   - 如果用户要求你代建线程，使用线程工具新建项目本地线程。
   - 新线程初始提示词必须采用瘦身接管：说明它接管哪条泳道、旧线程为何不可用、只要求先读 `AGENTS.md`、`agent-registry.json`、`dashboard.md` 和恢复包摘要；不要在第一条提示中粘贴完整 message-log、完整 worklog、完整 dashboard 或多个大段 callback。
   - 第一条提示应要求新线程只回复一句健康检查，例如“健康检查通过”，不要立刻执行复杂调度。
   - 如果线程工具不可用，不要虚构 id；把新线程标为 `pending_setup` 并说明阻塞。

4. 健康检查与二次故障判定：
   - 对新线程做至少两次轻量健康检查：一次确认能启动并短回复，一次确认能读取最小持久化文件或恢复包摘要。
   - 健康检查通过前，不要把复杂待处理批次、长 callback、全量 message-log 或大段项目历史投递给新线程。
   - 如果新线程健康检查失败，记录错误原文、后台投递结果和失败时间，把该线程改为“历史归档-二次故障”或等价审计状态。
   - 二次故障后重新创建候选线程时，进一步缩短接管提示，只保留项目名、泳道名、旧线程 id、恢复包路径和“先回复可用”的测试指令。

5. 更新 registry：
   - 修改 `agent-lanes/agent-registry.json` 中对应泳道的 `thread_id`。
   - 更新 `last_seen_at`。
   - 在 `notes` 保留旧线程 id、替换时间和原因。
   - 保持 `display_name` / 泳道名可读；如果新线程沿用原名，旧线程应改成历史归档名。
   - 只有健康检查通过后，才把该线程登记为当前投递目标；健康检查失败的候选线程只进入 notes、worklog 或恢复包审计，不作为 current thread。

6. 线程标题和归档：
   - 如果可用，给新线程设置原泳道名，例如 `主调度泳道`。
   - 给旧线程加历史标记，例如 `主调度泳道（历史归档-YYYYMMDD）`。
   - 如果可用，归档旧线程。
   - 归档失败不是恢复阻塞，但必须记录 concern。

7. 追加审计：
   - 在 `agent-lanes/message-log.jsonl` 追加 `task_type=lane_thread_replacement` 或 `orchestrator_thread_replacement`。
   - 审计记录正文可使用英文 agent key，避免 PowerShell 编码把中文写成 `目标项目`。
   - 记录 `old_thread_id`、`new_thread_id`、`changed_files`、`evidence`、`concerns` 和 `next_recommended_action`。

8. 更新 worklog 和 dashboard：
   - 在对应泳道 `worklog.md` 追加替换记录。
   - 运行 `python agent-lanes\scripts\render_dashboard.py`。
   - 如项目有 `communications-readable.xlsx`，确认刷新命令已生成。

9. 验证：
   - JSON parse `agent-lanes/agent-registry.json`。
   - JSONL parse `agent-lanes/message-log.jsonl`。
   - 确认对应泳道 `thread_id` 是新线程。
   - 确认替换审计记录唯一。
   - 运行 `powershell -ExecutionPolicy Bypass -File scripts\check-agent-lanes-post-office.ps1`，如存在。

## 输出

最终回复必须包含：

- `status`
- 旧线程 id 和新线程 id。
- `changed_files`
- `evidence`
- `concerns`
- `next_recommended_lane`
- `next_recommended_action`

## 完成门禁

完成前必须满足：

- 新线程已创建或明确阻塞为 `pending_setup`。
- 新线程已通过至少两次轻量健康检查，或健康检查失败已记录为二次故障并未切换为 current thread。
- `agent-lanes/agent-registry.json` 指向新线程，或阻塞原因已记录。
- 旧线程不再作为投递目标。
- 恢复包已写入对应泳道 workspace。
- `agent-lanes/message-log.jsonl` 已追加可解析审计记录，且没有新增 `数据` 乱码污染。
- 对应泳道 worklog 已追加记录。
- dashboard 已刷新，或说明无法刷新原因。

## 打回条件

出现以下情况时不要宣称恢复完成：

- 新线程 id 未创建，却把 registry 改成虚构 id。
- 只改了线程标题，没有更新 `agent-registry.json`。
- 只在聊天里说明，没有写恢复包、worklog 或 message-log 审计。
- 把旧线程删除，导致历史不可追溯。
- `message-log.jsonl` 新增记录不可 JSON 解析，或出现新 `数据` 乱码污染。
- 未处理 pending callback / 未完成任务，也没有把它交给新线程。
- 新线程尚未通过健康检查，却已把 registry 切到该线程并宣称恢复完成。
- 新线程已经出现二次 `agent loop died unexpectedly`，仍继续向它投递长上下文或真实任务。
