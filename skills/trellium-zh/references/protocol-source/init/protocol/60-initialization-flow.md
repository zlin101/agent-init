# 60 - 初始化流程

## 定位

本流程用于新项目初始化。

如果目标是已经存在的项目，并且只想接入 Agent 记忆管理和协作治理，请使用 `70-adoption-flow.md`。

## 步骤

使用 `init/INIT.md` 初始化项目时：

1. 读取 `init/INIT.md`。
2. 按顺序读取协议模块。
3. 如果项目类型明确，显式选择一个或多个 profile 及其目标根目录；不自动猜测。
4. 明确项目名称、项目类型和当前阶段。
5. 询问 owner 选择存储模式（schema v2 `storage_mode`）：`local`（默认）、`tracked`（共享完整 TASK 流水）、`private`（managed 文件不进 Git，terminal 历史可另存本机；语义与接入顺序见 `70-adoption-flow.md`「Private 存储模式」，adopt 前须通过只读 `private_preflight` 探针）。
6. 创建或更新 `AGENTS.md`。
7. 创建 `vault/`。
8. 创建 `vault/index.md`，写入已选 storage；local 模式由 Agent 同时创建只覆盖 TASK/review/archive 的 `vault/tasks/.gitignore`；private 模式不创建 tasks/.gitignore，改为维护 `.git/info/exclude` 的 canonical trellium-private block。
9. 创建 `vault/project.md`。
10. 创建 `vault/runtime.md`。
11. 创建 `vault/governance.md`。
12. 创建 `vault/decisions.md`。
13. 创建 `vault/handoff.md`。
14. 创建 `vault/parked.md`。
15. 创建 `vault/tasks/README.md`。
16. 只在需要时创建 `vault/details/*` 文件。
17. 创建 `skills/`。
18. 创建必要初始 skill。
19. 为每个选定语言生成完整的 `docs/engineering/profiles/<profile>.md`（含声明 roots），并在 `AGENTS.md` 写入一跳条件路由；保留 `docs/engineering/code-comments.md`（Comment/API Documentation Policy），未选语言不生成，已有工程规范不覆盖。完整规则见 `70-adoption-flow.md`「Profile 工程规范」。
20. 仅按选定 profile 的需要初始化源码、测试和依赖文件。
21. 更新 `README.md`。
22. 运行最小检查。
23. 更新 `vault/runtime.md`，记录最终初始化状态。
24. 将长期有效的协议或 profile 决策记录到 `vault/decisions.md`。

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
