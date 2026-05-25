# 60 - 初始化流程

## 定位

本流程用于新项目初始化。

如果目标是已经存在的项目，并且只想接入 Agent 记忆管理和协作治理，请使用 `70-adoption-flow.md`。

## 步骤

使用 `init/INIT.md` 初始化项目时：

1. 读取 `init/INIT.md`。
2. 按顺序读取协议模块。
3. 如果项目类型明确，读取选定 profile。
4. 明确项目名称、项目类型和当前阶段。
5. 创建或更新 `AGENTS.md`。
6. 如需要，创建或同步 `CLAUDE.md`。
7. 创建 `vault/`。
8. 创建 `vault/index.md`。
9. 创建 `vault/project.md`。
10. 创建 `vault/runtime.md`。
11. 创建 `vault/governance.md`。
12. 创建 `vault/decisions.md`。
13. 创建 `vault/handoff.md`。
14. 创建 `vault/tasks/README.md` 和 `vault/tasks/.gitkeep`。
15. 只在需要时创建 `vault/details/*` 文件。
16. 创建 `skills/`。
17. 创建必要初始 skill。
18. 仅按选定 profile 的需要初始化源码、测试和依赖文件。
19. 更新 `README.md`。
20. 运行最小检查。
21. 更新 `vault/runtime.md`，记录最终初始化状态。
22. 将长期有效的协议或 profile 决策记录到 `vault/decisions.md`。

## 验收

初始化只有在满足以下条件时才算通过：

- 入口文件会路由 Agent 到 vault 和 governance 上下文；
- 必需 vault 文件存在；
- governance 规则存在；
- 任务追踪规则存在；
- 必要 skill 存在；
- 适用 profile 的产物存在；
- 必要检查通过，或失败被明确记录；
- `vault/runtime.md` 反映当前状态。

## 约束

初始化阶段不要引入复杂框架、基础设施或无关能力。
