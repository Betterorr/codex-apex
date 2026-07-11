---
name: frontend-workflow-planner
description: 当用户讨论前端工程工作流、前端立项、前端底座、设计系统、技术栈、UI 组件库、目录结构、模块边界、组件复用、组件登记册、Design Token、多语言、主题、前端数据层级、前端规划与设计如何衔接时，使用这个 Skill 生成或更新目标项目的前端工作流合同，并把结果落到 docs/frontend/、docs/02-design-brief.md、docs/03-dev-plan.md 或泳道 workspace。
---

# 前端工作流规划器

## 核心契约

本 Skill 负责把“想做一个前端页面/工作台/产品界面”的讨论，转成可被规划、设计、开发、验收共同读取的前端工程合同。它不是单页审美建议，也不是直接替开发生成页面代码。

默认产物应写回项目内已有 GOAL 文档体系，不能另起一套旁路文档。目标项目应在使用时把 `<PROJECT_NAME>`、核心用户、产品闭环、前端入口和数据来源替换成本项目自己的定义。

## 自然语言触发词

用户提到这些表达时优先使用本 Skill：

- 前端工作流、前端立项、前端开发流程、前端底座、前端架构、技术栈、UI 组件库。
- 设计系统、Design Token、统一视觉语言、主题、多语言、组件复用。
- 目录结构、模块边界、页面组件怎么放、接口请求怎么放、样式怎么管理。
- 组件标准模块、组件登记册、Component Registry Lifecycle。
- 前端数据层级、数据、页面消费什么数据、后端/脚本/artifact 怎样给前端。
- 规划泳道和设计泳道都能调用、把前端流程变成 Skill。

## 输入

优先读取：

- `docs/00-project-state.md`
- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- `docs/03-dev-plan.md`
- `docs/capability-status.json`
- 已有前端入口、前端源码目录、相关 `artifacts/`、泳道 callback 和 workspace 文件。

如果这些文件不存在，先在输出中说明缺口，并给出最小可建立的文档结构。

## 工作流

每次前端规划至少产出这些决策：

- `product_surface`: 本轮服务的用户工作台、页面或页面区域。
- `active_user_loop`: 本轮前端切片补的是哪条用户闭环，而不是只补局部壳层。
- `design_language`: 面向目标用户的视觉和交互语言，以及明确反参考。
- `frontend_stack`: 框架、构建工具、UI 组件库、图表库、表格库、数据缓存、状态管理和布局策略。
- `module_boundaries`: 页面、组件、data adapter、状态、样式、测试和 artifact 各放哪里。
- `data_contract`: 前端消费哪一层数据；原始脏数据默认由后端、脚本或 artifact 处理，前端只消费受控 schema。
- `component_registry_lifecycle`: 新组件处于 `candidate`、`approved_contract`、`sandbox_poc`、`island_pilot`、`shared_component` 或 `deprecated` 哪个状态。
- `design_tokens`: 颜色、字号、行高、间距、圆角、阴影、边框、密度、状态色和图表色板。
- `i18n_theme_rules`: 文案、主题和语言切换的存放策略。
- `output_paths`: 本轮结果写入哪些 docs、workspace、artifact、prototype 或前端目录。
- `acceptance_evidence`: browser screenshot smoke、static scan、bundle size、数据边界、可访问性、错误态、非生产声明等证据。

## 默认文档结构

长期前端工作流建议在 `docs/frontend/` 下维护这些中间文件：

- `00-frontend-workflow-index.md`: 当前前端路线、阶段、文件索引和下一步。
- `01-information-architecture.md`: 页面、区域、信息层级、用户路径和导航关系。
- `02-surface-specs.md`: 每个 surface 的布局、状态、数据入口、失败状态和验收证据。
- `03-component-inventory.md`: 可复用组件、领域组件、第三方组件和复用阈值。
- `04-data-contract-map.md`: 数据 payload、adapter、字段、来源、边界和质量 blocker。
- `05-design-token-plan.md`: token、密度、字体、颜色、图表 palette、主题和多语言规则。
- `06-figma-bridge.md`: Figma 文件、页面、frame、组件、变量和导出/回写边界。
- `07-iteration-log.md`: 每轮问题、截图反馈、原因归因、修改的中间文件和下一轮计划。
- `08-production-frontend-skeleton.md`: route、目录结构、状态管理、query key、bundle budget、测试门禁和开发边界。
- `10-page-skeleton-blueprint.md`: 页面树、布局区域、主次按钮、状态流转、组件挂载点和数据来源。

## 输出

根据任务落到对应位置：

- 设计路线、信息架构、页面状态、交互和 Design Token：更新 `docs/02-design-brief.md`。
- 技术栈、目录结构、阶段切片、验收命令和风险：更新 `docs/03-dev-plan.md`。
- 组件标准、组件生命周期、实现路径、参考来源、license/source 边界：更新 `docs/frontend/03-component-inventory.md`。
- 泳道临时分析：写入 `agent-lanes/lanes/<lane>/workspace/<slice>.md`。
- 可验证前端 artifact 或 browser smoke：证据放入 `artifacts/<slice>/`。

## 打回条件

遇到这些情况不要直接进入开发：

- 只说“好看、科技感、高级”，没有具体视觉语言、密度、状态、反参考和 Design Token。
- 只选技术栈，没有说明为什么适合目标产品的关键任务。
- 没有目录结构和模块边界，或要求 AI 每个页面自由发挥。
- 新增或吸收组件但没有写入 `docs/frontend/03-component-inventory.md`，或没有标明生命周期状态、实现路径、source/reference、license/boundary 和验收证据。
- 没有前端数据层级，或让页面直接清洗原始脏数据。
- 没有输出路径，导致设计、计划、artifact 和代码产物散落。
- 没有验收证据，尤其是 browser screenshot smoke、静态扫描、数据边界和质量 blocker 可见性。
- 涉及新依赖、license、外部 API、secret、provider live call、scheduler、真实远程写入、高风险资源或 production feed，却没有 guardian / 用户确认。

## 完成门禁

完成前必须说明：

- 本轮覆盖的 `product_surface`、`active_user_loop` 和用户路径。
- 已明确 `design_language`、`frontend_stack`、`data_contract`、`module_boundaries`、`component_registry_lifecycle`、`design_tokens`、`output_paths` 和 `acceptance_evidence`。
- 如果涉及组件新增、吸收或复用，已更新 `docs/frontend/03-component-inventory.md`。
- 如果涉及页面骨架，已明确 `page_tree`、`layout_regions`、`primary_actions`、`secondary_actions`、`state_transitions`、`component_mounts`、`data_sources`、`empty/error/loading states` 和 `acceptance_evidence`。
- 已写入 `docs/02-design-brief.md`、`docs/03-dev-plan.md`、`docs/frontend/` 或泳道 workspace 中至少一个。
- 保持项目文档中文优先；路径、命令、JSON key、status、message_id、库名和 license 保留英文或原文。

## 信号

当用户反馈“前端乱、没有规划、页面层级不清、组件重复、设计稿和实现不一致、Figma 反向主导结构、每次都从零开始”时，在 `.codex/signals/` 记录 signal，或写入 `docs/frontend/07-iteration-log.md`。如果同类问题重复出现 2 次以上，应交给 `evolution-runner` 检查是否需要强化本 Skill、hook 或前端门禁。
