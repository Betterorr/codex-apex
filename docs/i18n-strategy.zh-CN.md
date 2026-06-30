# Codex Apex 国际化发布策略

## 建议结论

采用三层语言策略：

1. **默认公开入口英文**：GitHub 根目录 `README.md`、仓库描述、release notes 和 topic 使用英文。
2. **中文模板保留为 canonical source**：第一阶段不重写 `agent-lanes-goal-integrated-template/` 内的中文协议，避免破坏已有操作语义。
3. **逐步补英文镜像**：按用户路径优先级翻译，而不是一次性翻译所有文件。

## 为什么不直接做“纯英文版”

这个模板不是普通说明文档，它包含调度规则、门禁边界、callback 语义、泳道职责和 Codex 操作约束。直接整包翻译容易出现三类风险：

- 状态词、权限边界、验收语义被翻译弱化。
- 中文项目里已经验证过的操作口径被改散。
- 英文版还没经过真实项目运行，反而变成新的未验证 canonical。

所以第一阶段更适合把英文作为入口和解释层，把中文作为已验证的操作层。

## 推荐文件布局

```text
README.md                         # 英文默认入口
README.zh-CN.md                   # 中文入口
docs/i18n-strategy.zh-CN.md       # 本策略
docs/release-checklist.zh-CN.md   # 发布清单
agent-lanes-goal-integrated-template/
  README.md                       # 中文 canonical
  README-GOAL-INTEGRATED.md       # 中文 canonical
  DEPLOY-PROMPT.md                # 中文 canonical
  docs/en/                        # 后续可补英文镜像
```

## 翻译优先级

第一优先级：

- 根目录 `README.md`
- `README.zh-CN.md`
- GitHub repository description
- `agent-lanes-goal-integrated-template/README-GOAL-INTEGRATED.md` 的英文摘要
- `DEPLOY-PROMPT.md` 的英文快速说明

第二优先级：

- `TEMPLATE-MANIFEST.md`
- `LANE-GOAL-SKILL-MAP.md`
- `LANE-SKILL-HOOK-MATRIX.md`
- `requirements-routing-protocol.md`
- `review-protocol.md`

第三优先级：

- 深层 skill 文档
- 内部模板 worklog
- 运行态占位文档

## 文案约定

- 产品名统一为 `Codex Apex`。
- 方法论名保留 `Agent Lanes` 和 `GOAL Development Base`。
- JSON key、状态枚举、命令、路径、脚本名、API 名保持原文。
- `guardian` 译为守门泳道时，英文仍保留 `guardian lane`。
- `review` 和 `guardian` 不混用：review 负责验收，guardian 负责权限、风险和边界。

## 首版发布建议

首版可以标记为 `v0.1.0`，定位为：

```text
Chinese-first canonical template with English public entry points.
```

也就是说，首版不承诺完整英文操作文档，但承诺外部用户能从英文 README 理解项目用途、结构和部署入口。

