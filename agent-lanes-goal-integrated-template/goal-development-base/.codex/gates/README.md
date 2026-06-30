# Gates

这里放项目级自动门禁脚本或配置。

原则：

- 能用程序判断的规则，不只写在提示词里。
- 构建失败、测试失败、审查失败、必需文件缺失、发布记录缺失，都应该尽量变成门禁。
- 门禁脚本可以由具体项目按技术栈补充。

当前内置门禁：

- `skill-mechanism-check.ps1`：检查 `.agents/skills/` 中的本地 Skill 是否符合 GOAL 方法论要求，包括核心契约、输出、完成门禁、打回条件、signal 机制和各环节关键能力。
- `scripts/validate-capability-status.ps1`：检查 `docs/capability-status.json` 是否 JSON 合法、成熟度合法、必需字段完整，并在 evidence 标记为 present/verified/exists 且路径不是占位符时检查路径存在。
