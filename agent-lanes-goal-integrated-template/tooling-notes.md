# Codex Tooling Notes for Agent Lanes

本文件记录 Agent Lanes 可能用到的 Codex 内置工具。不同环境可见工具可能不同，启用前应先探测。

## 长期线程型 Agent 工具

| Tool | 用途 |
| --- | --- |
| `codex_app.list_projects` | 列出本地/远程项目，创建项目内 Agent 前使用 |
| `codex_app.create_thread` | 创建新的长期 Agent 线程 |
| `codex_app.list_threads` | 查找已有 Agent 线程 |
| `codex_app.read_thread` | 读取另一个 Agent 的近期状态、结果或阻塞 |
| `codex_app.send_message_to_thread` | 向目标 Agent 投递结构化任务 |
| `codex_app.set_thread_title` | 设置稳定线程名称 |
| `codex_app.set_thread_pinned` | 置顶长期核心 Agent |
| `codex_app.set_thread_archived` | 归档结束或过期 Agent |

## Fork / Handoff 工具

| Tool | 用途 |
| --- | --- |
| `codex_app.fork_thread` | 从当前或指定线程复制出子线程 |
| `codex_app.handoff_thread` | 在线程、checkout、worktree 或远程主机之间交接 |
| `codex_app.get_handoff_status` | 查询 handoff 状态 |

适合：

- 从规划上下文派生开发线程。
- 从失败现场派生审查线程。
- 将工作隔离到 worktree。
- 在本地和远程主机之间转移任务。

## 自动化 / 心跳工具

| Tool | 用途 |
| --- | --- |
| `codex_app.automation_update` | 创建、更新、查看或删除定时任务、监控、heartbeat |

适合：

- 稍后自动检查长任务。
- 定期读取 Lane 状态。
- 定时继续安全的下一步。
- 监控外部任务结果。

边界：

- 自动化只负责触发检查或继续动作。
- 完成判断仍应由 Gate / Review / 用户最终验收决定。
- 遇到费用、secret、发布、删除数据、产品取舍时，先检查是否已有覆盖本次范围的用户授权；已有授权则记录依据并走守门/开发/验收的受控路径，未授权或超出范围时才停下来问用户。

## 临时并行子 Agent

| Tool | 用途 |
| --- | --- |
| `multi_agent_v1.spawn_agent` | 启动临时 explorer 或 worker 子 Agent |

区别：

| 类型 | 特点 | 适合 |
| --- | --- | --- |
| 长期线程型 Agent | 有稳定 lane、thread id、worklog、workspace | 长期职责、持续维护、跨轮协作 |
| 临时子 Agent | 当前任务内临时生成，完成后回收 | 并行调研、局部实现、一次性审查 |

## 工具发现建议

启动 Agent Lanes 前，先搜索或确认这些工具是否可用：

```text
create_thread
list_threads
read_thread
send_message_to_thread
set_thread_title
set_thread_pinned
set_thread_archived
fork_thread
handoff_thread
get_handoff_status
automation_update
spawn_agent
```

## 降级方案

| 缺失工具 | 降级做法 |
| --- | --- |
| `create_thread` | 人工创建会话，再把 thread id 写入 registry |
| `send_message_to_thread` | 人工复制结构化消息 |
| `read_thread` | 让目标 Agent 主动写 worklog 或 artifact |
| `set_thread_title` | 手动命名线程 |
| `automation_update` | 手动检查或用项目脚本提醒 |
| `spawn_agent` | 用长期 Agent Lane 或手动新线程替代 |

## 推荐安全边界

可以自动推进：

- 本地代码实现。
- 文档更新。
- fixture 测试。
- 本地 smoke。
- 只读 evidence。
- 前后端局部联调。
- 独立审查。
- 自进化规则补丁。

动态授权闸门：

- 真实付费 API 调用。
- secret / key / 账号权限。
- 删除、覆盖或迁移真实数据。
- 发布上线。
- 客户可用或生产可用声明。
- 大范围架构改变。
- 产品方向取舍。

这些事项未授权或超出授权范围时要问用户；已有授权时应按授权范围、预算、输入、证据和回滚要求继续推进。
