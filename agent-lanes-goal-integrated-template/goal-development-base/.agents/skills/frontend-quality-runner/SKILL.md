---
name: frontend-quality-runner
description: 当用户提到前端体验质量、UI 质感、页面可读性、信息架构、交互状态、前端 polish、视觉审查、Dashboard/业务工作台好不好用、移动端/桌面端适配、文本溢出、按钮/表格/卡片/状态设计、浏览器截图验收时，使用这个 Skill 把 interface-design 和 frontend-design 两个最值得的前端设计方法本地化到 目标项目；输出必须回写 docs/02-design-brief.md、docs/05-review-report.md、artifacts 或对应泳道 workspace，不得只生成孤立设计建议。
---

# 目标项目 前端质量执行器

目标：只吸收 2 个最值得进入 目标项目 默认流程的前端设计方法：`interface-design` 和 `frontend-design`。`interface-design` 负责工具型界面的信息架构、密度、导航、状态和设计系统；`frontend-design` 只吸收“避免通用 AI 模板感、让视觉选择来自产品语境”的 craft 方法。所有规则必须服从 目标项目的业务工作台定位和 GOAL 文档流。

## 吸收边界

- 默认吸收 `interface-design`：目标项目 是业务工作台、dashboard、数据工具和交互产品，不是营销页。
- 有条件吸收 `frontend-design`：只吸收产品语境、视觉差异化、排版/层级/状态 craft；不吸收 landing page、装饰性 hero、过度动效、泛紫色渐变或为“惊艳”牺牲研究效率的倾向。
- 不默认吸收 `frontend-ui-ux-engineer`：它有可用的可访问性、状态和 polish 清单，但与本 Skill 已有规则重叠较高，且示例偏通用组件/电商卡片，暂不进入默认机制。
- 不默认吸收 `app-ui-design`：它偏 iOS/Android 移动端平台指南；目标项目 当前主要是本地 Web 业务工作台，需要时再临时参考。

## 核心契约

- 项目文档中文优先：设计说明、验收问题、截图结论和建议动作写中文；路径、命令、DOM/API 名和错误原文保留原文。
- 前端质量结论必须回写 目标项目 既有文档、artifacts 或泳道 workspace，不产出孤立设计稿体系。
- 如果发现 dashboard、UI 验收或截图规则存在可复用缺口，记录为 signal 或交给进化泳道，不在本 Skill 内顺手扩大机制改造。

## 自然语言触发词

当用户或主调度提到前端体验质量、UI 质感、页面可读性、信息架构、交互状态、前端 polish、视觉审查、Dashboard/业务工作台好不好用、移动端/桌面端适配、文本溢出、按钮/表格/卡片/状态设计、浏览器截图验收时，优先使用本 Skill。

## 固定输入

优先读取：

- `docs/01-product-spec.md`
- `docs/02-design-brief.md`
- `docs/03-dev-plan.md`
- `docs/05-review-report.md`
- `<frontend-entry>/index.html`
- `<frontend-entry>/app.js`
- `<frontend-entry>/styles.css`
- 相关 `moneydigger/data/*.json` / `*.js`
- `agent-lanes/dashboard.md`

## 输出位置

- 设计决策、信息架构、状态规则：写入 `docs/02-design-brief.md`。
- 前端验收、截图结论、问题清单：写入 `docs/05-review-report.md` 或 `agent-lanes/lanes/review/workspace/`。
- 浏览器截图、静态 smoke、可视化证据：写入 `artifacts/<slice>/`。
- 不要创建新的设计体系文档替代 `docs/02-design-brief.md`。

## 目标项目 前端质量标准

- 目标项目 是业务工作台，不是营销 landing page。界面应安静、密集、可扫描、可比较、适合反复研究。
- 每个页面都要回答 `interface-design` 的三件事：这个人是谁、他此刻要完成什么、界面应该让他如何判断下一步。
- 每个重要界面都要有一个来自 目标项目 语境的“签名元素”，例如证据链、provider 状态、fixture/真实数据边界、研究复盘脉络或市场状态，而不是通用卡片堆叠。
- 视觉选择必须能解释原因：为什么这个布局、密度、颜色、字体层级、边框/阴影策略适合金融业务工作台。
- 优先表格、筛选、状态标签、证据面板、解释面板、错误/授权状态，而不是大 hero、装饰性卡片和炫技动效。
- 必须清楚展示数据来源状态：`fixture_only`、`call_count=0`、`no_unverified_claim`、provider blocked、authorization required。
- 任何评分、评估、仿真、关键业务指标或来源状态信息，都不能写成未经验证的生产承诺、合规承诺或效果保证。
- 控件要有稳定尺寸，长文本不能溢出或遮挡；按钮、表格、状态徽标和导航必须在桌面和移动宽度下可读。
- 使用真实浏览器或 Playwright 截图验证用户可见路径；不能只看代码断言。
- 禁止把 `frontend-design` 的营销页倾向带入业务工作台：不要为了“好看”加入大面积 hero、装饰性渐变、低信息密度或无业务含义的动画。

## 工作流

1. 明确本次页面或组件服务哪条产品骨架链路。
2. 对照 `docs/02-design-brief.md` 查是否已有设计约束；没有则先补设计，不直接开改。
3. 检查信息架构：入口、主区域、状态区、证据区、空错态、下一步动作。
4. 检查视觉和交互：可读性、密度、响应式、键盘/鼠标路径、状态反馈、文本溢出。
5. 若需要实现，交给开发泳道；若是验收，给出问题优先级和截图/命令证据。

## 打回条件

- 页面只“好看”但没有解释数据来源、授权状态、风险边界或失败状态。
- 设计产物没有落到 `docs/02-design-brief.md`，开发泳道读不到。
- 浏览器证据缺失，却声称用户可见 UI 已完成。
- 文案暗示高风险结论、高风险真实执行能力、真实 provider maturity 或真实收益证明。
- 大量装饰性视觉牺牲业务工作台的扫描、比较和重复使用效率。

## 完成门禁

完成时至少说明：

- 覆盖的页面/组件和用户路径。
- 更新的设计或验收文件。
- 浏览器/截图/静态 smoke 证据。
- 仍需开发、守门或验收处理的关注点。
