# 模板使用指南

## 如何使用模板

将 `assets/templates/` 中的文件复制到目标项目，并根据目标项目调整。保留目标项目的真实事实、命令和约束。删除不相关的指导文字。

不要把占位内容当作事实复制。

## 模板地图

- `AGENTS.md`：项目级 Agent 入口规则。
- `vault/index.md`：上下文路由和记忆更新规则。承载 `trellium-policy` 项目策略块（预算与 TASK storage），含任务与授权速查表。
- `vault/project.md`：稳定项目目标和范围。
- `vault/runtime.md`：项目全局当前状态与可选导航 Focus；TASK 状态和清单直接来自任务状态块。
- `vault/governance.md`：任务等级、授权等级、任务生命周期、任务契约和验收门。
- `vault/decisions.md`：长期决策；生命周期四态；超阈值索引化（正文入 `vault/decisions/`）。
- `vault/handoff.md`：仅当真实中断留下非可推导恢复事实时才写入的 transient delta；每条三小节（Why interrupted / Transient context not captured elsewhere / Exact resume point）；实时 Git 事实不写入。
- `vault/parked.md`：用户挂起事项冷索引（P-xxxx 条目）；仅被提及时读取；清理只出提案。
- `vault/collaboration.md`：协作偏好和观察模式。
- `vault/tasks/README.md`：任务生命周期流转、`trellium-task-state` 状态块规则、任务模板和 review 台账模板。
- `skills/trellium-work/SKILL.md`：非琐碎项目任务的可复用工作流。

## 新项目初始化

大多数模板可以直接使用，然后补充项目事实：

1. 在 `vault/project.md` 替换项目名称和目标。
2. 在 `vault/runtime.md` 设置当前阶段、可选 Focus 任务和检查命令；不要把 TASK 状态复制进 runtime。
3. `vault/parked.md` 没有挂起事项时保持模板态，不要预填。
4. 保持 `vault/governance.md` 保守。
5. 只有具体 profile 或用户需求需要时，才添加项目代码和测试。

## 既有项目接入

谨慎合并：

1. 如果已有 `AGENTS.md`，保留既有项目规则，并在不削弱原规则的前提下加入 vault/governance 路由。
2. 如果已有 decisions 或 ADR，不迁移历史，只在 `vault/decisions.md` 中添加指针。
3. 如果已有 docs，避免重写；只有有用且被允许时，添加极短协作说明。
4. 除非用户明确扩大范围，不触碰业务工程文件。
5. 接入时不创建 `vault/decisions/` 与 `vault/tasks/archive/`；两者由首次压缩按需创建。

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
