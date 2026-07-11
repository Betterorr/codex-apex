---
name: open-source-research-runner
description: 当用户提到 GitHub 调研、开源库选型、找资源、找实现、github-research、opensrc、替换开源库、provider 候选、验证框架、图表库、数据源、指标/规则库、论文代码、嫁接别人开发好的前后端、开源前端、开源后端、Open Source Integration Gate 或需要比较仓库维护度/license/依赖复杂度时，使用这个 Skill 在目标项目文档体系内做开源研究；输出必须落到 docs/08-open-source-reference-pool.md、docs/09-research-roadmap.md、docs/capability-status.json 或泳道 workspace，不得直接复制外部代码进项目。
---

# 开源研究执行器

目标：吸收 `github-research` 和开源分析类 skill 的方法，但把输出固定到目标项目的研究、守门和能力状态文档。

## 核心契约

- 项目文档中文优先：候选比较、license 风险、维护度判断、建议动作写中文；仓库名、URL、license 名、命令、API 名保留原文。
- 开源研究只产出候选、风险和集成建议；不得绕过守门泳道直接复制外部代码或推进 provider maturity。
- 对“可以用别人开发好的前后端嫁接”的需求，必须先走 Open Source Integration Gate：先定义本项目自己的页面职责、字段合同、adapter 边界和安全边界，再评估外部模块；不得直接把外部前后端复制进业务目录或绕过 guardian。
- 如果发现可复用的选型规则、license 风险或 provider 接入缺口，记录为 signal 或交给进化泳道。

## 自然语言触发词

当用户或主调度提到 GitHub 调研、开源库选型、找资源、找实现、github-research、opensrc、替换开源库、provider 候选、验证框架、图表库、数据源、指标/规则库、论文代码、嫁接别人开发好的前后端、开源前端、开源后端、Open Source Integration Gate 或需要比较仓库维护度/license/依赖复杂度时，优先使用本 Skill。

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
- 不要把外部仓库源码直接复制进业务目录、`scripts/` 或应用运行目录。

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
- 与目标项目产品骨架哪一环相关。
- 可复用组件、主要依赖、运行门槛、数据/网络/secret 要求。
- 是否会引入真实 provider、付费、账号、远程写入、受监管操作、高风险自动化执行或生产化承诺风险。
- 与现有 `docs/capability-provider-contract.md` 的适配方式。
- 推荐结论：采用、观望、拒绝、需要守门确认。

## 守门边界

- 引入外部代码前，必须检查 license 和依赖风险。
- 引入真实 provider/API/SDK/CLI 前，必须进入守门泳道。
- 不要把开源 demo 的能力成熟度直接写成目标项目已接入。
- 不要因为仓库 star 多就推荐采用；要看维护度、接口边界、测试和可替换性。

## Open Source Integration Gate / 开源嫁接门槛

当目标是“用别人开发好的前后端嫁接”或引入图表、验证实验、内部模拟执行、数据源、规则库、报告组件时，必须先完成以下检查，不能直接进入开发复制：

- License / attribution：确认 license 类型、商业/修改/分发限制、署名要求、NOTICE/版权保留要求。
- Dependency：列出运行时、构建工具、系统依赖、体积、语言栈、平台限制和维护成本。
- Local smoke：在不接真实 provider、不读 secret、不触碰远程状态的前提下，设计最小本地 smoke 或 fixture 验证方案。
- Adapter 边界：外部模块只能通过受控 adapter、wrapper 或数据合同接入；业务 UI 不直接绑定外部项目目录结构、全局状态或 vendor API。
- Guardian 边界：凡涉及 provider/live API、secret、账号、真实资金、production feed、scheduler、远程写入、高风险自动化执行或受监管操作，必须先转 guardian。
- Source handling：不得把外部前后端整包复制进项目；需要引用代码时必须先有 license 结论、归属说明、最小复制范围和后续维护责任。
- Capability maturity：外部项目 demo 成功不等于目标项目已具备能力；只有本地 adapter smoke、artifact、下游消费和质量审查才能推进本项目 maturity。

## 打回条件

- 只总结 README，没有看 license、维护度、依赖和集成边界。
- 输出没有写入 `docs/08-open-source-reference-pool.md` 或 `docs/09-research-roadmap.md`。
- 直接建议复制代码进项目，没有 license/守门结论。
- 建议嫁接外部前后端，但没有 Open Source Integration Gate：license / attribution / dependency / local smoke / adapter / guardian 边界。
- 把外部仓库能力误写为目标项目已具备能力。

## 完成门禁

完成时必须给出：

- 候选清单和推荐排序。
- 每个候选的采用/拒绝理由。
- license、依赖、权限和 provider 风险。
- Open Source Integration Gate 结论：license / attribution / dependency / local smoke / adapter / guardian 边界是否清楚。
- 建议下一泳道：规划、守门、开发或暂不推进。
