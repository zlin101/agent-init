# 模板使用指南

## 如何使用模板

将 `assets/templates/` 中的文件复制到目标项目，并根据目标项目调整。保留目标项目的真实事实、命令和约束。删除不相关的指导文字。

不要把占位内容当作事实复制。

## 模板地图

- `AGENTS.md`：项目级 Agent 入口规则。
- `vault/index.md`：上下文路由和记忆更新规则。
- `vault/project.md`：稳定项目目标和范围。
- `vault/runtime.md`：当前状态和活跃任务指针。
- `vault/governance.md`：任务等级、授权等级、任务契约和验收门。
- `vault/decisions.md`：长期决策。
- `vault/handoff.md`：近期交接状态。
- `vault/collaboration.md`：协作偏好和观察模式。
- `vault/tasks/README.md`：任务文件状态流转和模板。
- `skills/agent-task/SKILL.md`：非琐碎项目任务的可复用工作流。

## 新项目初始化

大多数模板可以直接使用，然后补充项目事实：

1. 在 `vault/project.md` 替换项目名称和目标。
2. 在 `vault/runtime.md` 设置当前阶段和检查命令。
3. 保持 `vault/governance.md` 保守。
4. 只有具体 profile 或用户需求需要时，才添加项目代码和测试。

## 既有项目接入

谨慎合并：

1. 如果已有 `AGENTS.md`，保留既有项目规则，并在不削弱原规则的前提下加入 vault/governance 路由。
2. 如果已有 decisions 或 ADR，不迁移历史，只在 `vault/decisions.md` 中添加指针。
3. 如果已有 docs，避免重写；只有有用且被允许时，添加极短协作说明。
4. 除非用户明确扩大范围，不触碰业务工程文件。

## 必须定制

始终定制：

- 项目名称
- 项目目标
- 当前阶段
- 必要验证命令
- 技术栈特定约束
- 既有文档或决策位置
- 活跃任务状态

永远不要通过添加密钥、本地绝对路径、私有服务 URL、个人账号细节或默认模型/供应商凭据来“定制”。
