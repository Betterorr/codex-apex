---
name: open-source-research-runner
description: 当用户提到 GitHub 调研、开源库选型、找资源、找实现、github-research、opensrc、替换开源库、provider 候选、回测框架、图表库、金融数据源、指标/因子库、论文代码或需要比较仓库维护度/license/依赖复杂度时，使用这个 Skill 在 MoneyDigger 文档体系内做开源研究；输出必须落到 docs/08-open-source-reference-pool.md、docs/09-research-roadmap.md、docs/capability-status.json 或泳道 workspace，不得直接复制外部代码进项目。
---

# MoneyDigger 开源研究执行器

目标：吸收 `github-research` 和开源分析类 skill 的方法，但把输出固定到 MoneyDigger 的研究/守门/能力状态文档。

## 核心契约

- 项目文档中文优先：候选比较、license 风险、维护度判断、建议动作写中文；仓库名、URL、license 名、命令、API 名保留原文。
- 开源研究只产出候选、风险和集成建议；不得绕过守门泳道直接复制外部代码或推进 provider maturity。
- 如果发现可复用的选型规则、license 风险或 provider 接入缺口，记录为 signal 或交给进化泳道。

## 自然语言触发词

当用户或主调度提到 GitHub 调研、开源库选型、找资源、找实现、github-research、opensrc、替换开源库、provider 候选、回测框架、图表库、金融数据源、指标/因子库、论文代码或需要比较仓库维护度/license/依赖复杂度时，优先使用本 Skill。

## 固定输入

优先读取：

- `docs/03-dev-plan.md`
- `docs/08-open-source-reference-pool.md`
- `docs/09-research-roadmap.md`
- `docs/capability-status.json`
- `docs/capability-provider-contract.md`
- 当前任务的目标、候选能力、禁止事项和授权边界

## 输出位置

- 开源候选池：`docs/08-open-source-reference-pool.md`
- 研究路线、候选比较、下一步调研：`docs/09-research-roadmap.md`
- 涉及 provider/API/CLI/SDK/模型/外部服务能力：更新或建议更新 `docs/capability-status.json`
- 深度仓库分析中间产物：`agent-lanes/lanes/planning/workspace/` 或 `agent-lanes/lanes/guardian/workspace/`
- 不要把外部仓库源码直接复制进 `moneydigger/`、`scripts/` 或业务目录。

## 使用 `github-research` 的条件

只有满足以下条件才启动完整 GitHub 研究：

- 需要比较多个仓库，而不是查一个 README。
- 需要看 license、维护度、依赖复杂度、代码结构和可复用组件。
- 任务允许网络访问、GitHub API 或浅克隆。
- `gh` CLI 已安装并认证；如果没有，记录阻塞或降级为只读网页/本地资料调研。

若只是快速了解一个库，先做轻量调研，不启动完整 6 阶段 deep dive。

## 研究维度

每个候选至少记录：

- 仓库 URL、license、维护状态、最近更新、stars/forks 只作弱信号。
- 与 MoneyDigger 产品骨架哪一环相关。
- 可复用组件、主要依赖、运行门槛、数据/网络/secret 要求。
- 是否会引入真实 provider、付费、账号、远程写入、券商/交易或投资建议风险。
- 与现有 `docs/capability-provider-contract.md` 的适配方式。
- 推荐结论：采用、观望、拒绝、需要守门确认。

## 守门边界

- 引入外部代码前，必须检查 license 和依赖风险。
- 引入真实 provider/API/SDK/CLI 前，必须进入守门泳道。
- 不要把开源 demo 的能力成熟度直接写成 MoneyDigger 已接入。
- 不要因为仓库 star 多就推荐采用；要看维护度、接口边界、测试和可替换性。

## 打回条件

- 只总结 README，没有看 license、维护度、依赖和集成边界。
- 输出没有写入 `docs/08-open-source-reference-pool.md` 或 `docs/09-research-roadmap.md`。
- 直接建议复制代码进项目，没有 license/守门结论。
- 把外部仓库能力误写为 MoneyDigger 已具备能力。

## 完成门禁

完成时必须给出：

- 候选清单和推荐排序。
- 每个候选的采用/拒绝理由。
- license、依赖、权限和 provider 风险。
- 建议下一泳道：规划、守门、开发或暂不推进。
