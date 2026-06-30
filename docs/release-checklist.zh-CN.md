# Codex Apex 开源发布清单

## 已完成

- 已把 `D:\00-antigravity\MoneyDigger\artifacts\template-packages` 原样复制到当前项目的 `template-packages/`。
- 已从最新版 `agent-lanes-goal-integrated-template-20260630-162901.zip` 展开出可迭代源码目录。
- 已添加根目录英文 `README.md`。
- 已添加根目录中文 `README.zh-CN.md`。
- 已添加 `.gitignore`，排除原始包副本、Python 缓存和本地环境文件。
- 已添加国际化策略文档。

## 发布配置

- GitHub 仓库名：`codex-apex`
- 开源协议：`MIT`
- 首版形态：英文入口 + 中文 canonical 模板

## 发布前检查

- 运行敏感信息扫描。
- 确认 `.pyc`、`__pycache__`、zip 包和本地 artifacts 不进入 git。
- 运行模板自带校验脚本。
- 初始化 git 仓库并检查 `git status`。
- 创建 GitHub public repository。
- 推送 `main` 分支。
- 创建 `v0.1.0` tag 或 GitHub release。

## 推荐首版描述

```text
Codex Apex is an open template system for running long-lived, multi-lane development workflows inside Codex. It combines Agent Lanes for multi-agent coordination with a GOAL Development Base for disciplined project execution.
```
