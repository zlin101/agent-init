---
name: agent-native-init-zh
description: 用于为新项目或既有软件项目添加持久的 Agent 协作规则、项目记忆、任务治理、交接机制或验收审查门。
---

# Agent Native Init 中文版

## 概览

为项目安装 Agent-native 协作层：简洁的 Agent 入口规则、vault 项目记忆系统、任务契约治理、handoff、可复用工作流和审查验收门。

本 Skill 是自包含包。目标项目不需要存在 `init/` 目录。

## 必读 Reference

编辑目标项目前，先读取本 Skill 自带的 reference：

- `references/protocol-model.md`：核心概念和验收门。
- `references/templates-guide.md`：如何使用模板。

使用 `assets/templates/` 下的文件作为起点。必须根据目标项目替换项目名称、检查命令和真实事实，不要盲目复制占位内容。

## 模式选择

编辑前先选择一种模式：

- **新项目初始化**：目标项目为空、可丢弃，或用户明确要求创建新的 Agent-ready 脚手架。
- **既有项目接入**：目标项目已有源码、依赖、测试、构建文件、部署文件、CI 或项目文档。

不确定时，选择既有项目接入。它更安全，因为默认只新增或合并 Agent 协作层。

## 任务契约

编辑前先说明：

- 目标
- 模式
- 范围和不做范围
- 预计修改的文件
- 授权等级和需要用户确认的事项
- 验收标准
- 验证命令

如果项目已有 `vault/tasks/`，创建或更新任务文件。否则先在工作说明中保留任务契约，等 vault 创建后再写入 `vault/tasks/`。

## 新项目初始化

创建最小可用项目：

1. 添加 Agent 入口文件，例如 `AGENTS.md`；只有有用时才添加工具专属入口文件。
2. 添加必需的 `vault/` 文件。
3. 添加 `skills/agent-task/SKILL.md`。
4. 只有当用户要求具体项目类型时，才添加源码、测试、依赖和 README。
5. 运行最小有意义检查。
6. 在 `vault/runtime.md` 记录当前状态，在 `vault/decisions.md` 记录长期选择。

项目真正需要前，不要添加框架、服务、数据库、CI、部署、LLM SDK 或凭据。

## 既有项目接入

保护既有项目：

1. 先只读扫描：根目录文件、Agent 入口、README/docs、源码结构、依赖文件、测试、构建/部署/CI 文件、既有记忆或决策记录、工作区未提交状态。
2. 先给出接入计划，只列 Agent 协作层修改。
3. 合并既有 Agent 入口规则，不直接覆盖。
4. 创建或合并 `vault/` 文件和 `skills/agent-task/SKILL.md`。
5. 在 `vault/project.md` 记录这是既有项目接入。
6. 在 `vault/runtime.md` 记录接入状态、风险和下一步。

没有用户明确授权时，不要修改业务源码、测试、依赖文件、锁文件、构建文件、部署文件、CI、数据库迁移、环境文件或大段既有文档。

## Review And Reflection

宣布完成前至少跑两轮。

### Round 1 - 协议覆盖审查

检查：

- Agent 入口文件会将非琐碎任务路由到 `vault/index.md`、`vault/runtime.md` 和 `vault/governance.md`。
- 必需 vault 文件存在。
- governance 覆盖任务等级、授权等级、任务契约字段、验收门、升级规则和 handoff。
- `skills/agent-task/SKILL.md` 存在，并聚焦任务执行。
- `vault/runtime.md` 是短当前状态，不是长日志。
- `vault/decisions.md` 记录长期选择。
- 需要协作偏好时，`vault/collaboration.md` 存在。

先修复缺口，再继续。

### Round 2 - 安全和最小化反思

反思：

- 是否有修改超出所选模式？
- 接入模式下是否改动了禁止触碰的工程文件？
- 是否添加了依赖、框架、服务、密钥、本地绝对路径、端口、模型名或凭据？
- 验证命令是否具体且适合项目？
- 剩余风险和需要用户判断的事项是否已记录？

如果发现问题，修复后重复对应轮次。

## 验证

运行任务契约或目标项目 `vault/runtime.md` 指定的验证。

文档级接入优先使用只读检查，例如列出预期文件、搜索关键术语。代码脚手架则运行最小项目测试命令。接入模式下，除非用户授权，不要运行会改变工程状态的命令。

## 完成汇报

汇报：

- 使用的模式。
- 创建或修改的文件。
- 明确未触碰的区域。
- 验证命令和结果。
- review/reflection 结论。
- 剩余风险或需要用户判断的事项。
